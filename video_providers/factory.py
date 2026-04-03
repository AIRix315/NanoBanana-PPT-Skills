#!/usr/bin/env python3
"""
Video Provider Factory - 视频生成提供者工厂

根据配置创建对应的视频生成提供者实例。
"""

import os
from typing import Optional

from .base import VideoProvider


def create_video_provider(
    provider_type: str = "kling",
    api_key: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
) -> VideoProvider:
    """
    创建视频生成提供者实例
    
    Args:
        provider_type: 提供者类型 - "kling", "seedance", "ltx"
        api_key: RunningHub API 密钥（用于 Seedance/LTX）
        access_key: 可灵 Access Key
        secret_key: 可灵 Secret Key
        
    Returns:
        对应的视频生成提供者实例
        
    Raises:
        ValueError: 不支持的提供者类型
        RuntimeError: 缺少必要的 API 密钥
    """
    if provider_type == "kling":
        from .kling import KlingProvider
        
        # 从环境变量获取密钥（如果未提供）
        access_key = access_key or os.environ.get("KLING_ACCESS_KEY")
        secret_key = secret_key or os.environ.get("KLING_SECRET_KEY")
        
        if not access_key or not secret_key:
            raise RuntimeError(
                "可灵 AI API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export KLING_ACCESS_KEY='your-access-key'\n"
                "  export KLING_SECRET_KEY='your-secret-key'\n"
                "或在代码中:\n"
                "  create_video_provider('kling', access_key='...', secret_key='...')"
            )
        
        return KlingProvider(access_key=access_key, secret_key=secret_key)
    
    elif provider_type == "seedance":
        from .seedance import SeedanceProvider
        
        # 从环境变量获取密钥（如果未提供）
        api_key = api_key or os.environ.get("RH_API_KEY")
        
        if not api_key:
            raise RuntimeError(
                "RunningHub API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'\n"
                "或在代码中:\n"
                "  create_video_provider('seedance', api_key='...')"
            )
        
        return SeedanceProvider(api_key=api_key)
    
    elif provider_type == "ltx":
        from .ltx import LTXProvider
        
        # 从环境变量获取密钥（如果未提供）
        api_key = api_key or os.environ.get("RH_API_KEY")
        
        if not api_key:
            raise RuntimeError(
                "RunningHub API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'\n"
                "或在代码中:\n"
                "  create_video_provider('ltx', api_key='...')"
            )
        
        return LTXProvider(api_key=api_key)
    
    else:
        raise ValueError(
            f"不支持的提供者类型: {provider_type}\n"
            f"支持的类型: kling, seedance, ltx"
        )