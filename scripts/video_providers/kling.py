#!/usr/bin/env python3
"""
Kling Provider - 可灵 AI 视频生成提供者 (RunningHub)

通过 RunningHub API 调用可灵 AI 视频生成服务。

支持的模型:
- kling-video-o1: 标准版 (std: 5秒≈￥2.1, 10秒≈￥4.2)
- kling-video-o3-pro: 增强版 (pro: 5秒≈￥2.8, 10秒≈￥5.6)
"""

import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
import tempfile

import requests

from .base import VideoProvider

# 导入 RunningHub 客户端和异常
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from rh_api import RunningHubError


class KlingProvider(VideoProvider):
    """
    可灵 AI 视频生成提供者 (RunningHub)

    通过 RunningHub API 调用可灵 AI 视频生成。
    支持首尾帧控制，适合 PPT 转场视频生成。

    使用示例：
        provider = KlingProvider(api_key='...')
        result = provider.generate_video(
            image_start='slide-01.png',
            image_end='slide-02.png',
            prompt='流畅的转场动画',
            output_path='transition.mp4',
            mode='std',  # std 或 pro
            duration=5
        )
    """

    # RunningHub Kling 端点
    ENDPOINT = "/kling-video-o1/start-to-end"

    # 默认配置
    DEFAULT_DURATION = "5"
    DEFAULT_MODE = "std"  # std 或 pro
    DEFAULT_ASPECT_RATIO = "16:9"
    DEFAULT_TIMEOUT = 300  # 5分钟
    POLL_INTERVAL = 5  # 轮询间隔

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化可灵 AI 提供者

        Args:
            api_key: RunningHub API 密钥
        """
        self.api_key = api_key or os.environ.get("RH_API_KEY")

        if not self.api_key:
            raise RunningHubError(
                "RunningHub API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'"
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        self.base_url = "https://www.runninghub.cn/openapi/v2"

        print(f"可灵 AI 提供者已初始化 (RunningHub)")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")

    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return "Kling AI (RunningHub)"

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
            image_start: 起始帧图片路径
            image_end: 结束帧图片路径（可选，首尾帧必须同时提供或都不提供）
            prompt: 视频生成提示词
            output_path: 输出路径
            duration: 视频时长（秒）
            **kwargs: 额外参数
                - mode: std 或 pro（默认 std）
                - aspect_ratio: 1:1, 9:16, 16:9（默认 16:9）

        Returns:
            {
                "success": True/False,
                "video_path": "path/to/video.mp4",
                "metadata": {...},
                "error": "error message"  # 失败时
            }
        """
        # 验证参数：首尾帧必须同时提供
        if not image_start or not image_end:
            return {
                "success": False,
                "error": "可灵 AI 首尾帧视频生成需要同时提供 image_start 和 image_end",
                "video_path": "",
                "metadata": {},
            }

        # 获取参数
        mode = kwargs.get("mode", self.DEFAULT_MODE)
        aspect_ratio = kwargs.get("aspect_ratio", self.DEFAULT_ASPECT_RATIO)

        # 准备输出路径
        if not output_path:
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"kling_video_{timestamp}.mp4")

        try:
            print(f"🎬 提交视频生成任务...")
            print(f"  模型: kling-video-o1 ({mode})")
            print(
                f"  提示词: {prompt[:50]}..."
                if len(prompt) > 50
                else f"  提示词: {prompt}"
            )
            print(f"  时长: {duration}秒")
            print(f"  比例: {aspect_ratio}")

            # 提交任务
            task_id = self._submit_task(
                image_start=image_start,
                image_end=image_end,
                prompt=prompt,
                duration=str(duration),
                mode=mode,
                aspect_ratio=aspect_ratio,
            )

            # 等待完成
            result = self._poll_task(task_id)

            # 下载视频
            video_url = result["results"][0]["url"]
            video_path = self._download_video(video_url, output_path)

            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

            # 计算费用
            cost = self._calculate_cost(duration, mode)

            print(f"✅ 视频生成成功!")
            print(f"  文件: {video_path}")
            print(f"  大小: {file_size_mb:.2f} MB")
            print(f"  预估费用: ￥{cost:.1f}")

            return {
                "success": True,
                "video_path": video_path,
                "metadata": {
                    "duration": duration,
                    "mode": mode,
                    "aspect_ratio": aspect_ratio,
                    "file_size_mb": file_size_mb,
                    "cost_yuan": cost,
                    "provider": self.get_provider_name(),
                    "task_id": task_id,
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
        image_end: str,
        prompt: str,
        duration: str,
        mode: str,
        aspect_ratio: str,
    ) -> str:
        """提交视频生成任务"""

        # 上传图片
        print(f"📤 上传图片...")
        first_image_url = self._upload_image(image_start)
        last_image_url = self._upload_image(image_end)

        url = f"{self.base_url}{self.ENDPOINT}"

        request_body = {
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "duration": duration,
            "firstImageUrl": first_image_url,
            "lastImageUrl": last_image_url,
            "mode": mode,
        }

        response = self.session.post(url, json=request_body, timeout=30)

        if response.status_code != 200:
            raise RunningHubError(f"提交任务失败: {response.text}")

        data = response.json()

        error_code = data.get("errorCode")
        if error_code:
            error_msg = data.get("errorMessage", "未知错误")
            raise RunningHubError(f"提交任务失败 [{error_code}]: {error_msg}")

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
        """轮询任务状态"""
        print(f"⏳ 等待视频生成完成...")

        start_time = time.time()
        poll_url = f"{self.base_url}/query"

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > self.DEFAULT_TIMEOUT:
                raise TimeoutError(f"任务超时（{elapsed}秒）")

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

        response = requests.get(video_url, stream=True, timeout=60)

        if response.status_code != 200:
            raise RunningHubError(f"下载失败，状态码: {response.status_code}")

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path

    def _calculate_cost(self, duration: int, mode: str) -> float:
        """
        计算预估费用

        std: 5秒≈￥2.1, 10秒≈￥4.2
        pro: 5秒≈￥2.8, 10秒≈￥5.6
        """
        if mode == "pro":
            return 2.8 if duration <= 5 else 5.6
        else:  # std
            return 2.1 if duration <= 5 else 4.2
