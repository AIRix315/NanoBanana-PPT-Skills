#!/usr/bin/env python3
"""
LTX Provider - LTX-2.3 视频生成提供者 (RunningHub)

Lightricks LTX-2.3 文生视频模型，通过 RunningHub 中转。
"""

import os
import time
from typing import Any, Dict, Optional
from pathlib import Path
import tempfile

import requests

from .base import VideoProvider

# 导入 RunningHub 客户端和异常
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from rh_api import RunningHubError


class LTXProvider(VideoProvider):
    """
    LTX-2.3 视频生成提供者

    通过 RunningHub API 调用 Lightricks LTX-2.3 模型。

    端点: /openapi/v2/rhart-video/ltx-2.3/image-to-video

    使用示例：
        provider = LTXProvider(api_key='...')
        result = provider.generate_video(
            image_start='path/to/image.png',
            prompt='自然风景视频',
            output_path='nature.mp4',
            duration=5,
            resolution='720p',
            aspect_ratio='16:9'
        )
    """

    MODEL_NAME = "ltx-2.3"
    ENDPOINT = "/rhart-video/ltx-2.3/image-to-video"  # 不包含 /openapi/v2 前缀
    DEFAULT_TIMEOUT = 600  # 10分钟
    POLL_INTERVAL = 5  # 轮询间隔(秒)
    MAX_POLL_TIME = 300  # 最大等待时间(秒)

    # 宽高比映射
    ASPECT_RATIO_MAP = {
        "9:16": "1",  # 竖屏
        "16:9": "2",  # 横屏
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 LTX 提供者

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

        print(f"LTX-2.3 提供者已初始化")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")

    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return "LTX-2.3 (Lightricks)"

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
            image_start: 起始帧图片路径（可选，文生视频时可为空）
            image_end: 结束帧图片路径（可选）
            prompt: 视频生成提示词
            output_path: 输出路径
            duration: 视频时长（秒）
            **kwargs: 额外参数

        Returns:
            {
                "success": True/False,
                "video_path": "path/to/video.mp4",
                "metadata": {...},
                "error": "error message"  # 失败时
            }
        """
        # 准备输出路径
        if not output_path:
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"ltx_video_{timestamp}.mp4")

        try:
            print(f"🎬 提交视频生成任务...")
            print(f"  模型: {self.MODEL_NAME}")
            print(f"  提示词: {prompt[:50]}...")
            if image_start:
                print(f"  起始图片: {image_start}")

            # 提交任务
            task_id = self._submit_task(
                prompt=prompt,
                duration=duration,
                image_start=image_start,
                **kwargs,
            )

            # 等待完成
            result = self._poll_task(task_id)

            # 下载视频
            video_url = result["results"][0]["url"]
            video_path = self._download_video(video_url, output_path)

            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

            print(f"✅ 视频生成成功: {video_path}")

            return {
                "success": True,
                "video_path": video_path,
                "metadata": {
                    "duration": duration,
                    "model": self.MODEL_NAME,
                    "file_size_mb": file_size_mb,
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
        prompt: str,
        duration: int,
        image_start: str = "",
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        **kwargs,
    ) -> str:
        """提交视频生成任务

        Args:
            prompt: 视频描述
            duration: 时长（5-20秒）
            image_start: 起始图片（本地路径或URL）
            resolution: 分辨率 ("480p", "720p", "1080p")
            aspect_ratio: 宽高比 ("9:16" 或 "16:9")
        """

        # LTX-2.3 只有图生视频
        if not image_start:
            raise RunningHubError(
                "LTX-2.3 只支持图生视频 (image-to-video)，请提供 image_start 参数"
            )

        # 处理图片上传
        if image_start.startswith("http"):
            image_url = image_start
        else:
            image_url = self._upload_image(image_start)

        # 使用标准字段名（不是文档中的数字##格式）
        request_body = {
            "imageUrl": image_url,
            "prompt": prompt,
            "resolution": resolution,  # "480p", "720p", "1080p"
            "aspectRatio": aspect_ratio,  # "9:16", "16:9"
            "duration": duration,
        }

        url = f"{self.base_url}{self.ENDPOINT}"

        response = self.session.post(url, json=request_body, timeout=30)

        if response.status_code != 200:
            raise RunningHubError(f"提交任务失败: {response.text}")

        data = response.json()

        # 检查错误
        error_code = data.get("errorCode")
        if error_code:
            error_msg = data.get("errorMessage", "未知错误")
            raise RunningHubError(f"提交任务失败 [{error_code}]: {error_msg}")

        # 获取taskId
        task_id = data.get("taskId")

        if not task_id:
            raise RunningHubError(f"未返回任务ID: {data}")

        print(f"✅ 任务已提交: {task_id}")
        return task_id

    def _upload_image(self, image_path: str) -> str:
        """上传图片到 RunningHub，返回 URL"""
        print(f"📤 上传图片: {image_path}")

        upload_url = f"{self.base_url}/media/upload/binary"

        # 读取图片文件
        with open(image_path, "rb") as f:
            image_data = f.read()

        # 使用 multipart/form-data 上传
        files = {"file": (Path(image_path).name, image_data, "image/png")}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        response = requests.post(upload_url, files=files, headers=headers, timeout=60)

        if response.status_code != 200:
            raise RunningHubError(f"上传图片失败: {response.text}")

        data = response.json()

        # 获取上传后的 URL
        error_code = data.get("errorCode")
        if error_code:
            error_msg = data.get("errorMessage", "未知错误")
            raise RunningHubError(f"上传失败 [{error_code}]: {error_msg}")

        # 尝试不同的响应格式
        # 格式1: {"url": "..."}
        # 格式2: {"data": {"url": "..."}}
        # 格式3: {"data": {"download_url": "..."}}
        image_url = (
            data.get("url")
            or data.get("download_url")
            or data.get("data", {}).get("url")
            or data.get("data", {}).get("download_url")
        )

        if not image_url:
            raise RunningHubError(f"未返回图片URL: {data}")

        print(f"✅ 图片已上传: {image_url[:60]}...")
        return image_url

    def _poll_task(self, task_id: str) -> Dict[str, Any]:
        """轮询任务状态"""
        print(f"⏳ 等待视频生成完成...")

        start_time = time.time()
        poll_url = f"{self.base_url}/query"

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > self.MAX_POLL_TIME:
                raise TimeoutError(f"任务超时（{elapsed}秒）")

            # POST请求查询任务状态
            response = self.session.post(poll_url, json={"taskId": task_id}, timeout=10)

            if response.status_code != 200:
                raise RunningHubError(f"查询任务失败: {response.text}")

            data = response.json()

            # 标准模型API返回格式
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
                # 尝试旧格式兼容
                if "data" in data:
                    status = data["data"].get("status", "UNKNOWN")
                    if status == "SUCCESS":
                        print(f"✅ 视频生成完成（耗时 {elapsed} 秒）")
                        return data["data"]
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
