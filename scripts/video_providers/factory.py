#!/usr/bin/env python3
"""
Video Provider Factory - 视频生成提供者工厂

根据配置创建对应的视频生成提供者实例。
支持双 Key 配置：
- 创作级 Key (RH_CREATOR_KEY): 用于视频生成
- 通用 Key (RH_API_KEY): 兼容模式

⚡ 推荐配置：
- 默认使用 enterprise-video + v3.1-fast（低价渠道版，~￥0.5/段）
- 用户明确要求高质量时使用 v3.1-pro（~￥1.4/段）
"""

import os
from typing import Optional

from .base import VideoProvider


def _get_video_api_key(key_type: str = "auto") -> str:
    """
    获取视频生成所需的 API Key

    Args:
        key_type: Key 类型
            - "auto": 自动选择（默认）
            - "enterprise": 企业级Key（用于全能视频X/V3.1）
            - "creator": 创作级Key（用于Seedance/LTX）

    Returns:
        API Key 字符串

    Raises:
        RuntimeError: 如果未配置任何 Key
    """
    if key_type == "enterprise":
        # 企业级 Key（全能视频X、全能视频V3.1使用）
        key = os.environ.get("RH_ENTERPRISE_KEY") or os.environ.get("RH_API_KEY")
        if key:
            print(f"[视频提供者] 使用企业级 API Key: {key[:8]}...{key[-4:]}")
            return key
    elif key_type == "creator":
        # 创作级 Key（Seedance、LTX使用）
        key = os.environ.get("RH_CREATOR_KEY") or os.environ.get("RH_API_KEY")
        if key:
            print(f"[视频提供者] 使用创作级 API Key: {key[:8]}...{key[-4:]}")
            return key
    else:
        # 自动模式：优先企业级，回退通用
        key = (
            os.environ.get("RH_API_KEY")
            or os.environ.get("RH_ENTERPRISE_KEY")
            or os.environ.get("RH_CREATOR_KEY")
        )
        if key:
            print(f"[视频提供者] 使用 API Key: {key[:8]}...{key[-4:]}")
            return key

    raise RuntimeError(
        "视频生成 API 密钥未配置。\n\n"
        "请设置以下环境变量之一：\n"
        "  export RH_API_KEY='your-api-key'           # 通用（推荐）\n"
        "  export RH_ENTERPRISE_KEY='...'\t           # 企业级\n"
        "  export RH_CREATOR_KEY='...'\t               # 创作级\n\n"
        "或在代码中：\n"
        "  create_video_provider('enterprise-video', api_key='...')"
    )


def create_video_provider(
    provider_type: str = "enterprise-video",
    api_key: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    fast_mode: bool = False,
    model: str = "v3.1-fast",
) -> VideoProvider:
    """
    创建视频生成提供者实例

    Args:
        provider_type: 提供者类型
            - "enterprise-video": 企业级视频（默认推荐）
            - "kling": 可灵AI（需要创作级Key）
            - "seedance": Seedance 2.0（需要创作级Key）
            - "ltx": LTX-2.3（需要创作级Key）
        api_key: RunningHub API 密钥（可选，如未提供则从环境变量读取）
        access_key: (已弃用) 可灵 Access Key
        secret_key: (已弃用) 可灵 Secret Key
        fast_mode: 是否使用快速模式（仅适用于 Seedance）
        model: 企业级视频模型类型（仅适用于 enterprise-video）
            - "v3.1-fast": 全能视频V3.1-fast首尾帧低价渠道版（默认推荐，~￥0.5/段）
            - "v3.1-pro": 全能视频V3.1-pro官方稳定版（高质量，~￥1.4/段）
            - "x-low": 全能视频X低价版（支持多图）
            - "x": 全能视频X官方稳定版

    Returns:
        对应的视频生成提供者实例

    Raises:
        ValueError: 不支持的提供者类型
        RuntimeError: 缺少必要的 API 密钥
    """
    provider_type = provider_type.lower()

    # 企业级视频提供者（使用企业Key）
    if provider_type == "enterprise-video":
        from .enterprise_video import EnterpriseVideoProvider

        if not api_key:
            api_key = _get_video_api_key(key_type="enterprise")

        return EnterpriseVideoProvider(api_key=api_key, model=model)

    # 创作级视频提供者（使用创作Key）
    if not api_key:
        api_key = _get_video_api_key(key_type="creator")

    if provider_type == "kling":
        from .kling import KlingProvider

        return KlingProvider(api_key=api_key)

    elif provider_type == "seedance":
        from .seedance import SeedanceProvider

        return SeedanceProvider(api_key=api_key, fast_mode=fast_mode)

    elif provider_type == "ltx":
        from .ltx import LTXProvider

        return LTXProvider(api_key=api_key)

    else:
        raise ValueError(
            f"不支持的提供者类型: {provider_type}\n"
            f"支持的类型: enterprise-video（推荐）, kling, seedance, ltx"
        )


def list_video_providers() -> dict:
    """
    列出所有支持的视频提供者

    Returns:
        提供者信息字典
    """
    return {
        "enterprise-video": {
            "name": "企业级视频 (全能视频V3.1/X)",
            "endpoint": "/rhart-video-v3.1-fast/start-end-to-video",
            "capabilities": [
                "首尾帧视频(v3.1-fast/pro)",
                "多图参考(X低价)",
                "支持4K分辨率",
                "音频生成",
            ],
            "duration_range": "8秒",
            "key_type": "enterprise",
            "models": {
                "v3.1-fast": {
                    "name": "全能视频V3.1-fast-首尾帧-低价渠道版（推荐）",
                    "duration": "8秒",
                    "resolutions": ["720p", "1080p", "4k"],
                    "estimated_price": "~￥0.5/段",
                    "supports_first_last_frame": True,
                },
                "v3.1-pro": {
                    "name": "全能视频V3.1-pro-官方稳定版（高质量）",
                    "duration": "8秒",
                    "resolutions": ["720p", "1080p", "4k"],
                    "estimated_price": "~￥1.4/段",
                    "supports_first_last_frame": True,
                },
                "x-low": {
                    "name": "全能视频X-低价渠道版 (支持多图参考)",
                    "duration_range": "6-30秒",
                    "resolutions": ["480p", "720p"],
                    "max_images": 7,
                    "supports_transition": True,  # 通过多图实现过渡
                },
                "x": {
                    "name": "全能视频X-官方稳定版 (仅首帧)",
                    "duration_range": "6-10秒",
                    "resolutions": ["480p", "720p"],
                    "supports_transition": False,
                },
            },
        },
        "kling": {
            "name": "可灵 AI (O1) - 通过 RunningHub",
            "endpoint": "/kling-video-o1/start-to-end",
            "capabilities": ["首尾帧视频", "首帧图生视频"],
            "duration_range": "5-10秒",
            "key_type": "creator",
            "estimated_price": "~￥2.1-5.6/段",
        },
        "seedance": {
            "name": "Seedance 2.0 (字节跳动)",
            "endpoint": "/rhart-video/sparkvideo-2.0/image-to-video",
            "capabilities": ["首尾帧视频", "首帧图生视频", "音频生成"],
            "duration_range": "4-15秒",
            "key_type": "creator",
            "estimated_price": "创作级Key计费",
        },
        "ltx": {
            "name": "LTX-2.3 (Lightricks)",
            "endpoint": "/rhart-video/ltx-2.3/image-to-video",
            "capabilities": ["首帧图生视频", "音频生成"],
            "duration_range": "5-20秒",
            "key_type": "creator",
            "estimated_price": "创作级Key计费",
        },
    }
