#!/usr/bin/env python3
"""
Kling Provider - 可灵 AI 视频生成提供者

基于原有 kling_api.py 实现，适配 VideoProvider 接口。
"""

import base64
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import jwt
import requests

from .base import VideoProvider


class KlingProvider(VideoProvider):
    """
    可灵 AI 视频生成提供者
    
    支持图生视频（单帧动画）和首尾帧视频生成。
    
    使用示例：
        provider = KlingProvider(access_key='...', secret_key='...')
        result = provider.generate_video(
            image_start='slide-01.png',
            image_end='slide-02.png',
            prompt='流畅的转场动画',
            output_path='transition.mp4'
        )
    """
    
    API_BASE_URL = "https://api-beijing.klingai.com"
    API_CREATE_TASK = "/v1/videos/image2video"
    API_QUERY_TASK = "/v1/videos/image2video/{task_id}"
    
    DEFAULT_MODEL = "kling-v2-6"
    DEFAULT_DURATION = "5"
    DEFAULT_MODE = "std"
    DEFAULT_CFG_SCALE = 0.5
    DEFAULT_TIMEOUT = 300
    DEFAULT_POLL_INTERVAL = 5
    DEFAULT_TOKEN_EXPIRE = 1800
    
    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ):
        """
        初始化可灵 AI 客户端
        
        Args:
            access_key: API access key
            secret_key: API secret key
            
        Raises:
            RuntimeError: 如果密钥未配置
        """
        self.access_key = access_key or os.environ.get("KLING_ACCESS_KEY")
        self.secret_key = secret_key or os.environ.get("KLING_SECRET_KEY")
        
        if not self.access_key or not self.secret_key:
            raise RuntimeError(
                "可灵 AI API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export KLING_ACCESS_KEY='your-access-key'\n"
                "  export KLING_SECRET_KEY='your-secret-key'"
            )
        
        self.session = requests.Session()
        
        print(f"可灵 AI 客户端已初始化")
        print(f"  Access Key: {self.access_key[:8]}...{self.access_key[-4:]}")
    
    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return "Kling AI (可灵)"
    
    def generate_video(
        self,
        image_start: str,
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
            image_end: 结束帧图片路径（可选）
            prompt: 视频生成提示词
            output_path: 输出路径
            duration: 视频时长（秒）
            **kwargs: 额外参数
                - model_name: 模型名称（默认 kling-v2-6）
                - mode: 生成模式（std 或 pro）
                - negative_prompt: 负面提示词
                
        Returns:
            {
                "success": True/False,
                "video_path": "path/to/video.mp4",
                "metadata": {...},
                "error": "error message"  # 失败时
            }
        """
        # 验证图片路径
        self.validate_images(image_start, image_end)
        
        # 获取参数
        model_name = kwargs.get("model_name", self.DEFAULT_MODEL)
        mode = kwargs.get("mode", self.DEFAULT_MODE)
        negative_prompt = kwargs.get("negative_prompt", "")
        
        # 准备输出路径
        if not output_path:
            import tempfile
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"kling_video_{timestamp}.mp4")
        
        try:
            # 创建任务
            task_data = self._create_video_task(
                image_start=image_start,
                image_end=image_end,
                prompt=prompt,
                model_name=model_name,
                duration=str(duration),
                mode=mode,
                negative_prompt=negative_prompt,
            )
            
            task_id = task_data["task_id"]
            
            # 等待完成
            result_data = self._wait_for_completion(task_id)
            
            # 获取视频 URL
            videos = result_data.get("task_result", {}).get("videos", [])
            if not videos:
                return {
                    "success": False,
                    "error": "任务完成但未返回视频",
                    "video_path": "",
                    "metadata": {},
                }
            
            video_url = videos[0]["url"]
            
            # 下载视频
            video_path = self._download_video(video_url, output_path)
            
            # 获取文件大小
            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                "success": True,
                "video_path": video_path,
                "metadata": {
                    "duration": duration,
                    "model": model_name,
                    "mode": mode,
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
    
    def _create_video_task(
        self,
        image_start: str,
        image_end: Optional[str],
        prompt: str,
        model_name: str,
        duration: str,
        mode: str,
        negative_prompt: str,
    ) -> Dict[str, Any]:
        """创建视频生成任务"""
        # 准备图片
        request_body = {
            "model_name": model_name,
            "image": self._prepare_image(image_start),
            "duration": duration,
            "mode": mode,
        }
        
        if image_end:
            request_body["image_tail"] = self._prepare_image(image_end)
        
        if prompt:
            request_body["prompt"] = prompt
        
        if negative_prompt:
            request_body["negative_prompt"] = negative_prompt
        
        # 发送请求
        url = f"{self.API_BASE_URL}{self.API_CREATE_TASK}"
        response = self.session.post(
            url,
            json=request_body,
            headers=self._get_auth_headers(),
            timeout=30,
        )
        
        self._check_response(response, "创建任务")
        
        result = response.json()
        task_data = result["data"]
        
        print(f"✅ 任务已提交: {task_data['task_id']}")
        return task_data
    
    def _wait_for_completion(self, task_id: str) -> Dict[str, Any]:
        """等待任务完成"""
        print(f"⏳ 等待视频生成完成...")
        
        start_time = time.time()
        
        while True:
            elapsed = int(time.time() - start_time)
            
            if elapsed > self.DEFAULT_TIMEOUT:
                raise TimeoutError(f"任务超时（{elapsed}秒），任务 ID: {task_id}")
            
            task_data = self._query_task_status(task_id)
            status = task_data["task_status"]
            
            if status == "succeed":
                print(f"✅ 视频生成完成（耗时 {elapsed} 秒）")
                return task_data
            
            if status == "failed":
                error_msg = task_data.get("task_status_msg", "未知错误")
                raise RuntimeError(f"任务失败: {error_msg}")
            
            if status in ("submitted", "processing"):
                print(f"  [{elapsed}s] 状态: {status}，继续等待...")
                time.sleep(self.DEFAULT_POLL_INTERVAL)
            else:
                raise RuntimeError(f"未知的任务状态: {status}")
    
    def _query_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        url = self.API_BASE_URL + self.API_QUERY_TASK.format(task_id=task_id)
        response = self.session.get(url, headers=self._get_auth_headers(), timeout=10)
        self._check_response(response, "查询任务状态")
        return response.json()["data"]
    
    def _download_video(self, video_url: str, save_path: str) -> str:
        """下载视频"""
        print(f"📥 下载视频...")
        print(f"  URL: {video_url[:60]}...")
        print(f"  保存到: {save_path}")
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        response = requests.get(video_url, stream=True, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"下载失败，状态码: {response.status_code}")
        
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"✅ 下载完成")
        return save_path
    
    def _prepare_image(self, image: str) -> str:
        """准备图片（转为 base64）"""
        if os.path.exists(image):
            print(f"  转换图片: {Path(image).name}")
            with open(image, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        return image
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        token = self._generate_jwt_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    
    def _generate_jwt_token(self, expire_seconds: int = DEFAULT_TOKEN_EXPIRE) -> str:
        """生成 JWT token"""
        current_time = int(time.time())
        
        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": current_time + expire_seconds,
            "nbf": current_time - 5,
        }
        
        return jwt.encode(payload, self.secret_key, headers=headers)
    
    def _check_response(self, response: requests.Response, action: str) -> None:
        """检查响应"""
        if response.status_code != 200:
            raise RuntimeError(
                f"{action}失败:\n"
                f"  状态码: {response.status_code}\n"
                f"  响应: {response.text}"
            )
        
        result = response.json()
        if result.get("code") != 0:
            raise RuntimeError(
                f"{action}失败:\n"
                f"  错误码: {result.get('code')}\n"
                f"  消息: {result.get('message')}"
            )