#!/usr/bin/env python3
"""
VideoProvider - 视频生成提供者抽象基类

定义所有视频生成提供者的统一接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class VideoProvider(ABC):
    """
    视频生成提供者抽象基类
    
    所有视频生成提供者（可灵、Seedance、LTX等）都需要实现此接口。
    
    使用示例：
        class KlingProvider(VideoProvider):
            def generate_video(self, image_start, image_end, ...):
                # 实现可灵视频生成逻辑
                pass
            
            def get_provider_name(self):
                return "Kling AI"
    """
    
    @abstractmethod
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
        生成视频
        
        Args:
            image_start: 起始帧图片路径
            image_end: 结束帧图片路径（可选，用于首尾帧视频）
            prompt: 视频生成提示词
            output_path: 输出视频路径
            duration: 视频时长（秒）
            **kwargs: 提供者特定的额外参数
            
        Returns:
            Dict 包含以下字段：
                - success: bool - 是否成功
                - video_path: str - 视频文件路径
                - metadata: dict - 元数据（时长、分辨率、文件大小等）
                - error: str - 错误信息（失败时）
                
        Raises:
            VideoProviderError: 视频生成失败
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        获取提供者名称
        
        Returns:
            提供者名称字符串，例如 "Kling AI"
        """
        pass
    
    def validate_images(
        self,
        image_start: str,
        image_end: Optional[str] = None,
    ) -> bool:
        """
        验证图片路径是否有效
        
        Args:
            image_start: 起始帧图片路径
            image_end: 结束帧图片路径（可选）
            
        Returns:
            验证是否通过
            
        Raises:
            FileNotFoundError: 图片文件不存在
        """
        import os
        
        if not os.path.exists(image_start):
            raise FileNotFoundError(f"起始帧图片不存在: {image_start}")
        
        if image_end and not os.path.exists(image_end):
            raise FileNotFoundError(f"结束帧图片不存在: {image_end}")
        
        return True
    
    def get_default_quality_settings(self) -> Dict[str, Any]:
        """
        获取默认质量设置
        
        Returns:
            Dict 包含默认分辨率、帧率等设置
        """
        return {
            "resolution": "1920x1080",
            "fps": 24,
            "format": "mp4",
        }