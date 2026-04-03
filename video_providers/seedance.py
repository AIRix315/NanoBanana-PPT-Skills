#!/usr/bin/env python3
"""
Seedance Provider - Seedance 2.0 视频生成提供者 (RunningHub)

字节跳动 Seedance 2.0 视频生成模型，通过 RunningHub 中转。
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
from rh_api import RunningHubClient, RunningHubError


class SeedanceProvider(VideoProvider):
    """
    Seedance 2.0 视频生成提供者
    
    通过 RunningHub API 调用字节跳动 Seedance 2.0 模型。
    
    使用示例：
        provider = SeedanceProvider(api_key='...')
        result = provider.generate_video(
            prompt='科技感转场动画',
            output_path='transition.mp4'
        )
    """
    
    MODEL_NAME = "rh-seedance-v2"
    DEFAULT_TIMEOUT = 600  # 10分钟
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Seedance 提供者
        
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
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        
        self.base_url = "https://www.runninghub.cn/openapi/v2"
        self.endpoint = f"/{self.MODEL_NAME}/text-to-video"
        
        print(f"Seedance 2.0 提供者已初始化")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")
    
    def get_provider_name(self) -> str:
        """返回提供者名称"""
        return "Seedance 2.0 (字节跳动)"
    
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
            output_path = os.path.join(temp_dir, f"seedance_video_{timestamp}.mp4")
        
        try:
            print(f"🎬 提交视频生成任务...")
            print(f"  模型: {self.MODEL_NAME}")
            print(f"  提示词: {prompt[:50]}...")
            
            # 提交任务
            task_id = self._submit_task(
                prompt=prompt,
                duration=duration,
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
    
    def _submit_task(self, prompt: str, duration: int, **kwargs) -> str:
        """提交视频生成任务"""
        url = f"{self.base_url}{self.endpoint}"
        
        request_body = {
            "prompt": prompt,
            "duration": str(duration),
        }
        
        response = self.session.post(url, json=request_body, timeout=30)
        
        if response.status_code != 200:
            raise RunningHubError(f"提交任务失败: {response.text}")
        
        data = response.json()
        
        if "code" in data and data["code"] != 0:
            raise RunningHubError(f"提交任务失败: {data.get('message', '未知错误')}")
        
        task_id = data["data"]["taskId"]
        
        print(f"✅ 任务已提交: {task_id}")
        return task_id
    
    def _poll_task(self, task_id: str) -> Dict[str, Any]:
        """轮询任务状态"""
        print(f"⏳ 等待视频生成完成...")
        
        start_time = time.time()
        poll_url = f"{self.base_url}/task/{task_id}"
        
        while True:
            elapsed = int(time.time() - start_time)
            
            if elapsed > self.DEFAULT_TIMEOUT:
                raise TimeoutError(f"任务超时（{elapsed}秒）")
            
            response = self.session.get(poll_url, timeout=10)
            
            if response.status_code != 200:
                raise RunningHubError(f"查询任务失败: {response.text}")
            
            data = response.json()
            
            if "code" in data and data["code"] != 0:
                raise RunningHubError(f"查询任务失败: {data.get('message', '未知错误')}")
            
            status = data["data"]["status"]
            
            if status == "SUCCESS":
                print(f"✅ 视频生成完成（耗时 {elapsed} 秒）")
                return data["data"]
            
            elif status == "FAILED":
                error_msg = data["data"].get("errorMessage", "未知错误")
                raise RunningHubError(f"任务失败: {error_msg}")
            
            elif status in ("SUBMITTED", "PROCESSING"):
                print(f"  [{elapsed}s] 状态: {status}，继续等待...")
                time.sleep(3)
            
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