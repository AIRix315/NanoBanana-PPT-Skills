#!/usr/bin/env python3
"""
Enterprise Video Provider - 企业级视频生成提供者 (RunningHub)

支持 RunningHub 企业级视频生成API：
- 全能视频V3.1-fast-首尾帧生视频-低价渠道版（推荐，~￥0.5/段）
- 全能视频V3.1-pro-首尾帧生视频-官方稳定版（高质量，~￥1.4/段）
- 全能视频X-图生视频-低价渠道版（支持多图参考，最多7张）
- 全能视频X-图生视频-官方稳定版

这些API使用企业级Key (RH_API_KEY)，适合批量生产。

⚡ 推荐配置：
- 默认使用 v3.1-fast（低价渠道版，适合调试和测试）
- 用户明确要求高质量时使用 v3.1-pro
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


class EnterpriseVideoProvider(VideoProvider):
    """
    企业级视频生成提供者

    通过 RunningHub API 调用企业级视频生成模型。
    支持全能视频X（低价/官方）和全能视频V3.1-pro三个模型。

    使用示例：
        provider = EnterpriseVideoProvider(api_key='...')

        # 首帧图生视频（全能视频X低价版）
        result = provider.generate_video(
            image_start='slide-01.png',
            prompt='流畅的镜头推拉动画',
            output_path='video.mp4',
            model='x-low'
        )

        # 多图参考生成（全能视频X低价版，最多7张图）
        result = provider.generate_video(
            image_start='slide-01.png',
            image_end='slide-02.png',  # 会自动加入imageUrls数组
            prompt='从第一张图过渡到第二张图，平滑转场动画',
            output_path='transition.mp4',
            model='x-low'
        )

        # 首尾帧图生视频（全能视频V3.1-pro）
        result = provider.generate_video(
            image_start='slide-01.png',
            image_end='slide-02.png',
            prompt='平滑过渡转场动画',
            output_path='transition.mp4',
            model='v3.1-pro'
        )
    """

    # RunningHub 企业级视频端点
    ENDPOINTS = {
        "v3.1-fast": "/rhart-video-v3.1-fast/start-end-to-video",  # 全能视频V3.1-fast首尾帧（推荐）
        "v3.1-pro": "/rhart-video-v3.1-pro-official/reference-to-video",  # 全能视频V3.1-pro官方稳定版
        "x-low": "/rhart-video-g/image-to-video",  # 全能视频X低价渠道版（支持多图）
        "x": "/rhart-video-g-official/image-to-video",  # 全能视频X官方稳定版
    }

    # 模型显示名称
    MODEL_NAMES = {
        "v3.1-fast": "全能视频V3.1-fast-首尾帧-低价渠道版（推荐，~￥0.5/段）",
        "v3.1-pro": "全能视频V3.1-pro-官方稳定版（高质量，~￥1.4/段）",
        "x-low": "全能视频X-低价渠道版（多图参考）",
        "x": "全能视频X-官方稳定版",
    }

    # 默认配置
    DEFAULT_MODEL = "v3.1-fast"  # 默认使用低价渠道版（推荐）
    DEFAULT_RESOLUTION = "1080p"  # 默认1080p，兼顾质量和成本
    DEFAULT_DURATION = 8
    DEFAULT_ASPECT_RATIO = "16:9"
    DEFAULT_GENERATE_AUDIO = False
    DEFAULT_TIMEOUT = 600  # 10分钟
    POLL_INTERVAL = 5  # 轮询间隔

    # 支持的参数范围
    SUPPORTED_MODELS = ["v3.1-fast", "v3.1-pro", "x-low", "x"]
    SUPPORTED_RESOLUTIONS = {
        "v3.1-fast": ["720p", "1080p", "4k"],
        "v3.1-pro": ["720p", "1080p", "4k"],
        "x-low": ["480p", "720p"],
        "x": ["480p", "720p"],
    }
    SUPPORTED_DURATIONS = {
        "v3.1-fast": [8],  # 固定8秒
        "v3.1-pro": [8],  # 固定8秒
        "x-low": list(range(6, 31)),  # 6-30秒
        "x": [6, 10],
    }
    SUPPORTED_ASPECT_RATIOS = {
        "v3.1-fast": ["16:9", "9:16"],
        "v3.1-pro": ["16:9", "9:16"],
        "x-low": ["2:3", "3:2", "1:1", "16:9", "9:16"],
        "x": ["16:9", "9:16"],
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "v3.1-fast",
    ):
        """
        初始化企业级视频提供者

        Args:
            api_key: RunningHub 企业级 API 密钥
            model: 模型类型
                - "v3.1-fast": 全能视频V3.1-fast首尾帧低价渠道版（默认推荐，~￥0.5/段）
                - "v3.1-pro": 全能视频V3.1-pro官方稳定版（高质量，~￥1.4/段）
                - "x-low": 全能视频X低价渠道版（支持多图）
                - "x": 全能视频X官方稳定版
        """
        # 使用企业级Key（RH_API_KEY或RH_ENTERPRISE_KEY）
        self.api_key = (
            api_key
            or os.environ.get("RH_ENTERPRISE_KEY")
            or os.environ.get("RH_API_KEY")
        )

        if not self.api_key:
            raise RunningHubError(
                "企业级 API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'\n"
                "或\n"
                "  export RH_ENTERPRISE_KEY='your-enterprise-key'"
            )

        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"不支持的模型: {model}，支持的模型: {self.SUPPORTED_MODELS}"
            )

        self.model = model
        self.base_url = "https://www.runninghub.cn/openapi/v2"
        self.endpoint = self.ENDPOINTS[model]

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        print(f"企业级视频提供者已初始化")
        print(f"  模型: {self.MODEL_NAMES[model]}")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")
        print(f"  端点: {self.endpoint}")

    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return f"{self.MODEL_NAMES[self.model]} (企业级)"

    def generate_video(
        self,
        image_start: str = "",
        image_end: Optional[str] = None,
        prompt: str = "",
        output_path: str = "",
        duration: int = 6,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        生成视频（实现 VideoProvider 接口）

        Args:
            image_start: 起始帧图片路径（必需）
            image_end: 结束帧图片路径（可选）
                - 对于 v3.1-fast/v3.1-pro 模型：作为尾帧使用（首尾帧视频）
                - 对于 x-low 模型：会添加到 imageUrls 数组实现多图过渡
                - 对于 x 模型：不支持，会被忽略
            prompt: 视频生成提示词
            output_path: 输出路径
            duration: 视频时长（秒）
                - 全能视频V3.1-fast/pro: 固定8秒
                - 全能视频X低价版: 6-30秒
                - 全能视频X官方版: 6或10秒
            **kwargs: 额外参数
                - resolution: 分辨率 (720p/1080p/4k)
                - aspect_ratio: 宽高比 (16:9/9:16)，取决于模型
                - generate_audio: 是否生成音频 (True/False)，仅V3.1-pro支持
                - extra_images: 额外图片路径列表（仅x-low支持，最多5张额外图片）

        Returns:
            {
                "success": True/False,
                "video_path": "path/to/video.mp4",
                "metadata": {...},
                "error": "error message"  # 失败时
            }
        """
        # 验证必需参数
        if not image_start:
            return {
                "success": False,
                "error": "需要提供 image_start（首帧图片）",
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
        aspect_ratio = kwargs.get("aspect_ratio", self.DEFAULT_ASPECT_RATIO)
        generate_audio = kwargs.get("generate_audio", self.DEFAULT_GENERATE_AUDIO)
        extra_images = kwargs.get("extra_images", [])  # 额外图片（仅x-low支持）

        # 验证参数范围
        if resolution not in self.SUPPORTED_RESOLUTIONS[self.model]:
            print(f"⚠️  分辨率 {resolution} 不支持，使用默认 {self.DEFAULT_RESOLUTION}")
            resolution = self.DEFAULT_RESOLUTION

        if duration not in self.SUPPORTED_DURATIONS[self.model]:
            print(f"⚠️  时长 {duration} 不支持，使用默认 {self.DEFAULT_DURATION}")
            duration = self.DEFAULT_DURATION

        if aspect_ratio not in self.SUPPORTED_ASPECT_RATIOS[self.model]:
            print(
                f"⚠️  宽高比 {aspect_ratio} 不支持，使用默认 {self.DEFAULT_ASPECT_RATIO}"
            )
            aspect_ratio = self.DEFAULT_ASPECT_RATIO

        # 准备输出路径
        if not output_path:
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"enterprise_video_{timestamp}.mp4")

        try:
            print(f"🎬 提交视频生成任务...")
            print(f"  模型: {self.MODEL_NAMES[self.model]}")
            print(f"  提示词: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
            print(f"  时长: {duration}秒")
            print(f"  分辨率: {resolution}")

            # 根据模型类型处理
            if self.model == "x-low":
                # 全能视频X低价版：支持多图参考
                print(
                    f"  模式: {'多图参考' if (image_end or extra_images) else '首帧图生视频'}"
                )
            elif self.model == "v3.1-fast":
                # V3.1-fast：首尾帧视频（推荐）
                print(f"  模式: {'首尾帧视频' if image_end else '首帧图生视频'}")
            elif self.model == "v3.1-pro":
                # V3.1-pro：参考生视频（高质量）
                print(f"  模式: {'首尾帧视频' if image_end else '首帧图生视频'}")
            else:
                # 全能视频X官方版：仅首帧
                if image_end:
                    print(f"  ⚠️  全能视频X官方版不支持尾帧，将忽略 image_end")
                print(f"  模式: 首帧图生视频")

            # 提交任务
            task_id = self._submit_task(
                image_start=image_start,
                image_end=image_end,
                prompt=prompt,
                duration=duration,
                resolution=resolution,
                aspect_ratio=aspect_ratio,
                generate_audio=generate_audio,
                extra_images=extra_images,
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
                    "aspect_ratio": aspect_ratio,
                    "generate_audio": generate_audio,
                    "file_size_mb": file_size_mb,
                    "model": self.MODEL_NAMES[self.model],
                    "provider": self.get_provider_name(),
                    "task_id": task_id,
                    "mode": "多图参考"
                    if (self.model == "x-low" and (image_end or extra_images))
                    else ("首尾帧" if image_end else "首帧图生视频"),
                    "key_type": "enterprise",
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
        aspect_ratio: str,
        generate_audio: bool,
        extra_images: List[str] = [],
    ) -> str:
        """提交视频生成任务"""

        # 上传首帧图片
        print(f"📤 上传图片...")
        image_url = self._upload_image(image_start)

        # 构建请求体（根据模型类型）
        if self.model == "x-low":
            # 全能视频X低价版：支持多图参考
            image_urls = [image_url]

            # 添加尾帧到图片数组
            if image_end:
                last_image_url = self._upload_image(image_end)
                image_urls.append(last_image_url)

            # 添加额外图片
            for img_path in extra_images:
                if os.path.exists(img_path):
                    extra_url = self._upload_image(img_path)
                    image_urls.append(extra_url)

            print(f"  共 {len(image_urls)} 张参考图")

            request_body = {
                "prompt": prompt,
                "aspectRatio": aspect_ratio,
                "imageUrls": image_urls,
                "resolution": resolution,
                "duration": duration,
            }

        elif self.model == "x":
            # 全能视频X官方版：仅首帧
            request_body = {
                "prompt": prompt,
                "imageUrl": image_url,
                "resolution": resolution,
                "duration": str(duration),
            }
            # 忽略尾帧

        elif self.model == "v3.1-fast":
            # 全能视频V3.1-fast：支持首尾帧（低价渠道版）
            if not image_end:
                print(f"  ⚠️  v3.1-fast 需要尾帧，仅使用首帧模式")

            request_body = {
                "prompt": prompt,
                "firstFrameUrl": image_url,
                "aspectRatio": aspect_ratio,
                "resolution": resolution,
                "duration": str(duration),
            }

            # 添加尾帧
            if image_end:
                last_image_url = self._upload_image(image_end)
                request_body["lastFrameUrl"] = last_image_url

        else:  # v3.1-pro
            # 全能视频V3.1-pro：参考生视频（官方稳定版）
            request_body = {
                "prompt": prompt,
                "imageUrls": [image_url],
                "resolution": resolution,
                "generateAudio": generate_audio,
            }

            # 添加尾帧作为参考图
            if image_end:
                last_image_url = self._upload_image(image_end)
                request_body["imageUrls"].append(last_image_url)

        url = f"{self.base_url}{self.endpoint}"
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
