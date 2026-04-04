#!/usr/bin/env python3
"""
Seedance Provider - Seedance 2.0 视频生成提供者 (RunningHub)

字节跳动 Seedance 2.0 视频生成模型，通过 RunningHub 中转。
支持首帧图生视频和首尾帧图生视频两种模式。
"""

import os
import time
from typing import Any, Dict, List, Optional
from pathlib import Path
import tempfile

import requests

from .base import VideoProvider

# 导入 RunningHub 异常
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from rh_api import RunningHubError


class SeedanceProvider(VideoProvider):
    """
    Seedance 2.0 视频生成提供者

    通过 RunningHub API 调用字节跳动 Seedance 2.0 模型。
    支持首帧图生视频和首尾帧图生视频两种模式。

    使用示例：
        provider = SeedanceProvider(api_key='...')

        # 首帧图生视频
        result = provider.generate_video(
            image_start='slide-01.png',
            prompt='流畅的镜头推拉动画',
            output_path='video.mp4'
        )

        # 首尾帧图生视频（转场）
        result = provider.generate_video(
            image_start='slide-01.png',
            image_end='slide-02.png',
            prompt='平滑过渡转场动画',
            output_path='transition.mp4'
        )
    """

    # RunningHub Seedance 2.0 端点
    ENDPOINT_STANDARD = "/rhart-video/sparkvideo-2.0/image-to-video"
    ENDPOINT_FAST = "/rhart-video/sparkvideo-2.0-fast/image-to-video"

    # 默认配置
    DEFAULT_RESOLUTION = "720p"
    DEFAULT_DURATION = 5
    DEFAULT_RATIO = "16:9"
    DEFAULT_GENERATE_AUDIO = True
    DEFAULT_TIMEOUT = 600  # 10分钟
    POLL_INTERVAL = 5  # 轮询间隔

    # 支持的参数范围
    SUPPORTED_RESOLUTIONS = ["480p", "720p", "1080p", "2k", "4k"]
    SUPPORTED_DURATIONS = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    SUPPORTED_RATIOS = ["adaptive", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        fast_mode: bool = False,
    ):
        """
        初始化 Seedance 提供者

        Args:
            api_key: RunningHub API 密钥
            fast_mode: 是否使用快速模式（Seedance 2.0 Fast）
        """
        self.api_key = api_key or os.environ.get("RH_API_KEY")

        if not self.api_key:
            raise RunningHubError(
                "RunningHub API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'"
            )

        self.fast_mode = fast_mode
        self.base_url = "https://www.runninghub.cn/openapi/v2"
        self.endpoint = self.ENDPOINT_FAST if fast_mode else self.ENDPOINT_STANDARD

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        mode_str = "Fast" if fast_mode else "标准"
        print(f"Seedance 2.0 {mode_str} 提供者已初始化")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"  端点: {self.endpoint}")

    def get_provider_name(self) -> str:
        """返回提供者名称"""
        mode = "Fast" if self.fast_mode else "标准"
        return f"Seedance 2.0 {mode} (字节跳动)"

    def generate_video(
        self,
        image_start: str = "",
        image_end: Optional[str] = None,
        prompt: str = "",
        output_path: str = "",
        duration: int = 5,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        生成视频（实现 VideoProvider 接口）

        Args:
            image_start: 起始帧图片路径（必需）
            image_end: 结束帧图片路径（可选，用于首尾帧转场）
            prompt: 视频生成提示词
            output_path: 输出路径
            duration: 视频时长（秒），范围 4-15
            **kwargs: 额外参数
                - resolution: 分辨率 (480p/720p/1080p/2k/4k)
                - ratio: 宽高比 (adaptive/16:9/4:3/1:1/3:4/9:16/21:9)
                - generate_audio: 是否生成音频 (True/False)

        Returns:
            {
                "success": True/False,
                "video_path": "path/to/video.mp4",
                "metadata": {...},
                "error": "error message"  # 失败时
            }
        """
        # 验证必需参数：必须有首帧图片
        if not image_start:
            return {
                "success": False,
                "error": "Seedance 2.0 图生视频需要提供 image_start（首帧图片）",
                "video_path": "",
                "metadata": {},
            }

        # 验证图片文件存在
        if not os.path.exists(image_start):
            return {
                "success": False,
                "error": f"首帧图片不存在: {image_start}",
                "video_path": "",
                "metadata": {},
            }

        if image_end and not os.path.exists(image_end):
            return {
                "success": False,
                "error": f"尾帧图片不存在: {image_end}",
                "video_path": "",
                "metadata": {},
            }

        # 解析参数
        resolution = kwargs.get("resolution", self.DEFAULT_RESOLUTION)
        ratio = kwargs.get("ratio", self.DEFAULT_RATIO)
        generate_audio = kwargs.get("generate_audio", self.DEFAULT_GENERATE_AUDIO)

        # 验证参数范围
        if resolution not in self.SUPPORTED_RESOLUTIONS:
            resolution = self.DEFAULT_RESOLUTION
        if duration not in self.SUPPORTED_DURATIONS:
            duration = self.DEFAULT_DURATION
        if ratio not in self.SUPPORTED_RATIOS:
            ratio = self.DEFAULT_RATIO

        # 准备输出路径
        if not output_path:
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"seedance_video_{timestamp}.mp4")

        try:
            print(f"🎬 提交视频生成任务...")
            print(f"  模型: Seedance 2.0 {'Fast' if self.fast_mode else '标准'}")
            print(f"  提示词: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
            print(f"  时长: {duration}秒")
            print(f"  分辨率: {resolution}")
            print(f"  宽高比: {ratio}")
            print(f"  生成音频: {'是' if generate_audio else '否'}")
            print(f"  模式: {'首尾帧' if image_end else '首帧图生视频'}")

            # 提交任务
            task_id = self._submit_task(
                image_start=image_start,
                image_end=image_end,
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                ratio=ratio,
                generate_audio=generate_audio,
            )

            # 等待完成
            result = self._poll_task(task_id)

            # 下载视频
            video_url = result["results"][0]["url"]
            video_path = self._download_video(video_url, output_path)

            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

            print(f"✅ 视频生成成功!")
            print(f"  文件: {video_path}")
            print(f"  大小: {file_size_mb:.2f} MB")

            return {
                "success": True,
                "video_path": video_path,
                "metadata": {
                    "duration": duration,
                    "resolution": resolution,
                    "ratio": ratio,
                    "generate_audio": generate_audio,
                    "file_size_mb": file_size_mb,
                    "model": f"Seedance 2.0 {'Fast' if self.fast_mode else '标准'}",
                    "provider": self.get_provider_name(),
                    "task_id": task_id,
                    "mode": "首尾帧" if image_end else "首帧图生视频",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "video_path": "",
                "metadata": {},
            }

    def _submit_task(
        self,
        image_start: str,
        image_end: Optional[str],
        prompt: str,
        duration: int,
        resolution: str,
        ratio: str,
        generate_audio: bool,
    ) -> str:
        """提交视频生成任务"""

        # 上传图片
        print(f"📤 上传图片...")
        first_frame_url = self._upload_image(image_start)

        last_frame_url = None
        if image_end:
            last_frame_url = self._upload_image(image_end)

        url = f"{self.base_url}{self.endpoint}"

        request_body = {
            "prompt": prompt,
            "resolution": resolution,
            "duration": str(duration),
            "firstFrameUrl": first_frame_url,
            "generateAudio": generate_audio,
            "ratio": ratio,
        }

        # 添加尾帧（可选）
        if last_frame_url:
            request_body["lastFrameUrl"] = last_frame_url

        response = self.session.post(url, json=request_body, timeout=30)

        if response.status_code != 200:
            raise RunningHubError(f"提交任务失败: {response.text}")

        data = response.json()

        # 检查错误
        if "errorCode" in data and data["errorCode"]:
            error_msg = data.get("errorMessage", "未知错误")
            raise RunningHubError(f"提交任务失败 [{data['errorCode']}]: {error_msg}")

        task_id = data.get("taskId")
        if not task_id:
            raise RunningHubError(f"未返回任务ID: {data}")

        print(f"✅ 任务已提交: {task_id}")
        return task_id

    def _upload_image(self, image_path: str) -> str:
        """上传图片到 RunningHub"""
        print(f"  上传: {Path(image_path).name}")

        upload_url = f"{self.base_url}/media/upload/binary"

        with open(image_path, "rb") as f:
            image_data = f.read()

        files = {"file": (Path(image_path).name, image_data, "image/png")}
        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.post(upload_url, files=files, headers=headers, timeout=60)

        if response.status_code != 200:
            raise RunningHubError(f"上传图片失败: {response.text}")

        data = response.json()

        # 尝试不同的响应格式
        image_url = (
            data.get("data", {}).get("download_url")
            or data.get("download_url")
            or data.get("url")
            or data.get("data", {}).get("url")
        )

        if not image_url:
            raise RunningHubError(f"未返回图片URL: {data}")

        print(f"  完成: {image_url[:60]}...")
        return image_url

    def _poll_task(self, task_id: str) -> Dict[str, Any]:
        """轮询任务状态（POST /query）"""
        print(f"⏳ 等待视频生成完成...")

        start_time = time.time()
        poll_url = f"{self.base_url}/query"

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > self.DEFAULT_TIMEOUT:
                raise TimeoutError(f"任务超时（{elapsed}秒）")

            # 使用 POST 请求轮询
            response = self.session.post(poll_url, json={"taskId": task_id}, timeout=10)

            if response.status_code != 200:
                raise RunningHubError(f"查询任务失败: {response.text}")

            data = response.json()
            status = data.get("status", "UNKNOWN")

            if status == "SUCCESS":
                print(f"✅ 视频生成完成（耗时 {elapsed} 秒）")
                return data

            elif status == "FAILED":
                error_msg = data.get("errorMessage", "未知错误")
                raise RunningHubError(f"任务失败: {error_msg}")

            elif status in ("SUBMITTED", "PROCESSING", "RUNNING", "QUEUED"):
                print(f"  [{elapsed}s] 状态: {status}，继续等待...")
                time.sleep(self.POLL_INTERVAL)

            else:
                raise RunningHubError(f"未知状态: {status}")

    def _download_video(self, video_url: str, save_path: str) -> str:
        """下载视频"""
        print(f"📥 下载视频...")

        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(video_url, stream=True, timeout=120)

        if response.status_code != 200:
            raise RunningHubError(f"下载失败，状态码: {response.status_code}")

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path
