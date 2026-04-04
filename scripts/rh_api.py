#!/usr/bin/env python3
"""
RunningHub API Client - 国内中转平台 API 客户端

提供图像生成（全能图片PRO/V2）和视频生成（Seedance/LTX）的统一接口。
采用异步提交+轮询模式，封装为同步调用接口。

支持双 Key 配置：
- 企业级 Key (RH_ENTERPRISE_KEY): 用于图像生成，高并发
- 创作级 Key (RH_CREATOR_KEY): 用于视频生成，消耗RH币
"""

import os
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import requests


# =============================================================================
# Constants
# =============================================================================

RUNNINGHUB_BASE_URL = "https://www.runninghub.cn/openapi/v2"

# 图像生成端点
# 注意: v2端点可能不可用，pro端点已验证可用
IMAGE_ENDPOINTS = {
    "v2": "/rhart-image-n-pro/text-to-image",  # 改用pro端点，v2可能不可用
    "pro": "/rhart-image-n-pro/text-to-image",  # 已验证可用
}

# 图像生成模型名称（用于日志）
IMAGE_MODEL_NAMES = {
    "v2": "全能图片V2 (Gemini 3.1 Flash)",
    "pro": "全能图片PRO (Gemini 3 Pro)",
}

# 视频生成端点
VIDEO_ENDPOINTS = {
    "seedance": "/rh-seedance-v2/text-to-video",
    "ltx": "/rh-ltx-2-3/text-to-video",
}

# 默认超时和轮询间隔
DEFAULT_TIMEOUT = 300  # 5分钟
DEFAULT_POLL_INTERVAL = 3  # 3秒
DEFAULT_IMAGE_TIMEOUT = 120  # 图像生成超时（2分钟）
DEFAULT_VIDEO_TIMEOUT = 600  # 视频生成超时（10分钟）


# =============================================================================
# API Key 管理
# =============================================================================


def get_enterprise_key() -> Optional[str]:
    """
    获取企业级 API Key

    优先级：
    1. RH_ENTERPRISE_KEY 环境变量
    2. RH_API_KEY 环境变量（兼容模式）

    Returns:
        企业级 API Key，如果未配置则返回 None
    """
    return os.environ.get("RH_ENTERPRISE_KEY") or os.environ.get("RH_API_KEY")


def get_creator_key() -> Optional[str]:
    """
    获取创作级 API Key

    优先级：
    1. RH_CREATOR_KEY 环境变量
    2. RH_API_KEY 环境变量（兼容模式）

    Returns:
        创作级 API Key，如果未配置则返回 None
    """
    return os.environ.get("RH_CREATOR_KEY") or os.environ.get("RH_API_KEY")


def get_image_api_key() -> str:
    """
    获取图像生成所需的 API Key

    Returns:
        API Key 字符串

    Raises:
        RunningHubAuthError: 如果未配置任何 Key
    """
    key = get_enterprise_key()
    if key:
        print(f"使用企业级 API Key: {key[:8]}...{key[-4:]}")
        return key

    raise RunningHubAuthError(
        "图像生成 API 密钥未配置。\n"
        "请设置以下环境变量之一：\n"
        "  export RH_ENTERPRISE_KEY='your-enterprise-key'  # 推荐\n"
        "  export RH_API_KEY='your-api-key'                # 兼容模式\n\n"
        "获取地址：https://www.runninghub.cn/enterprise-api/sharedApi"
    )


def get_video_api_key() -> str:
    """
    获取视频生成所需的 API Key

    Returns:
        API Key 字符串

    Raises:
        RunningHubAuthError: 如果未配置任何 Key
    """
    key = get_creator_key()
    if key:
        print(f"使用创作级 API Key: {key[:8]}...{key[-4:]}")
        return key

    raise RunningHubAuthError(
        "视频生成 API 密钥未配置。\n"
        "请设置以下环境变量之一：\n"
        "  export RH_CREATOR_KEY='your-creator-key'  # 推荐\n"
        "  export RH_API_KEY='your-api-key'          # 兼容模式\n\n"
        "获取地址：https://www.runninghub.cn/enterprise-api/consumerApi"
    )


# =============================================================================
# Exceptions
# =============================================================================


class RunningHubError(Exception):
    """RunningHub API 基础异常"""

    pass


class RunningHubAuthError(RunningHubError):
    """认证失败异常"""

    pass


class RunningHubTimeoutError(RunningHubError):
    """任务超时异常"""

    pass


class RunningHubTaskError(RunningHubError):
    """任务失败异常"""

    pass


# =============================================================================
# RunningHub Client
# =============================================================================


class RunningHubClient:
    """
    RunningHub API 客户端

    支持图像生成（全能图片PRO/V2）和视频生成。

    使用示例：
        client = RunningHubClient(api_key="your-api-key")

        # 图像生成
        image_path = client.generate_image(
            prompt="生成一张渐变毛玻璃风格的封面",
            model="pro",
            aspect_ratio="16:9",
            resolution="2K"
        )

        # 视频生成
        video_path = client.generate_video(
            prompt="生成一个科技感的转场视频",
            model="seedance"
        )
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 RunningHub 客户端

        Args:
            api_key: RunningHub API 密钥，如果未提供则从环境变量 RH_API_KEY 读取

        Raises:
            RunningHubAuthError: 如果 API 密钥未配置
        """
        self.api_key = api_key or os.environ.get("RH_API_KEY")

        if not self.api_key:
            raise RunningHubAuthError(
                "RunningHub API 密钥未配置。\n"
                "请设置环境变量:\n"
                "  export RH_API_KEY='your-api-key'\n"
                "或在代码中:\n"
                "  client = RunningHubClient(api_key='your-api-key')"
            )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        print(f"RunningHub API 客户端已初始化")
        print(f"  API 密钥: {self.api_key[:8]}...{self.api_key[-4:]}")

    # -------------------------------------------------------------------------
    # 图像生成
    # -------------------------------------------------------------------------

    def generate_image(
        self,
        prompt: str,
        model: str = "pro",
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        output_path: Optional[str] = None,
        timeout: int = DEFAULT_IMAGE_TIMEOUT,
    ) -> str:
        """
        生成图像（同步接口）

        Args:
            prompt: 图像生成提示词
            model: 模型类型，"v2"（快速/草稿）或 "pro"（高质量/最终）
            aspect_ratio: 图片比例，默认 "16:9"
            resolution: 分辨率，"1K" / "2K" / "4K"
            output_path: 输出路径，如果未提供则使用临时文件
            timeout: 超时时间（秒）

        Returns:
            生成的图像文件路径

        Raises:
            RunningHubTaskError: 任务提交失败
            RunningHubTimeoutError: 任务超时
        """
        # 验证模型
        if model not in IMAGE_ENDPOINTS:
            raise ValueError(
                f"不支持的模型: {model}，支持的模型: {list(IMAGE_ENDPOINTS.keys())}"
            )

        # 提交任务
        print(f"\n🎨 提交图像生成任务...")
        print(f"  模型: {IMAGE_MODEL_NAMES[model]}")
        print(f"  比例: {aspect_ratio}")
        print(f"  分辨率: {resolution}")

        task_id = self._submit_image_task(
            prompt=prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
        )

        # 轮询等待
        result = self._poll_task(
            task_id=task_id,
            timeout=timeout,
            task_type="图像生成",
        )

        # 下载图像
        image_url = result["results"][0]["url"]
        image_path = self._download_image(image_url, output_path)

        print(f"✅ 图像生成成功: {image_path}")
        return image_path

    def _submit_image_task(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        resolution: str,
    ) -> str:
        """
        提交图像生成任务

        Args:
            prompt: 提示词
            model: 模型类型
            aspect_ratio: 比例
            resolution: 分辨率

        Returns:
            任务 ID

        Raises:
            RunningHubTaskError: 提交失败
        """
        endpoint = IMAGE_ENDPOINTS[model]
        url = f"{RUNNINGHUB_BASE_URL}{endpoint}"

        request_body = {
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "resolution": resolution,
        }

        try:
            response = self.session.post(url, json=request_body, timeout=30)

            self._check_response(response, "提交图像生成任务")

            data = response.json()

            # 标准模型API返回格式: {"taskId": "xxx", "status": "RUNNING", ...}
            # 不是 {"data": {"taskId": "xxx"}}
            task_id = data.get("taskId") or data.get("data", {}).get("taskId")

            if not task_id:
                error_code = data.get("errorCode", "UNKNOWN")
                error_msg = data.get("errorMessage", str(data))
                raise RunningHubTaskError(f"提交任务失败 [{error_code}]: {error_msg}")

            print(f"✅ 任务已提交: {task_id}")
            return task_id

        except requests.exceptions.RequestException as e:
            raise RunningHubTaskError(f"提交任务失败: {e}")

    # -------------------------------------------------------------------------
    # 视频生成
    # -------------------------------------------------------------------------

    def generate_video(
        self,
        prompt: str,
        model: str = "seedance",
        output_path: Optional[str] = None,
        timeout: int = DEFAULT_VIDEO_TIMEOUT,
        **kwargs,
    ) -> str:
        """
        生成视频（同步接口）

        Args:
            prompt: 视频生成提示词
            model: 模型类型，"seedance" 或 "ltx"
            output_path: 输出路径
            timeout: 超时时间
            **kwargs: 额外参数

        Returns:
            生成的视频文件路径
        """
        # TODO: 实现视频生成逻辑
        raise NotImplementedError("视频生成功能将在 video_providers 模块中实现")

    # -------------------------------------------------------------------------
    # 任务轮询
    # -------------------------------------------------------------------------

    def _poll_task(
        self,
        task_id: str,
        timeout: int,
        task_type: str = "任务",
    ) -> Dict[str, Any]:
        """
        轮询任务状态直到完成

        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            task_type: 任务类型（用于日志）

        Returns:
            任务结果数据

        Raises:
            RunningHubTimeoutError: 任务超时
            RunningHubTaskError: 任务失败
        """
        print(f"⏳ 等待{task_type}完成（超时: {timeout}秒）...")

        start_time = time.time()
        # 标准模型API轮询端点
        poll_url = f"{RUNNINGHUB_BASE_URL}/query"

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > timeout:
                raise RunningHubTimeoutError(
                    f"{task_type}超时（{elapsed}秒），任务 ID: {task_id}"
                )

            try:
                # POST请求查询任务状态
                response = self.session.post(
                    poll_url, json={"taskId": task_id}, timeout=10
                )
                self._check_response(response, "查询任务状态")

                data = response.json()

                # 标准模型API返回格式: {"status": "SUCCESS", "results": [...], ...}
                status = data.get("status", "UNKNOWN")

                if status == "SUCCESS":
                    print(f"✅ {task_type}完成（耗时 {elapsed} 秒）")
                    return data

                elif status == "FAILED":
                    error_msg = data.get("errorMessage", "未知错误")
                    raise RunningHubTaskError(f"{task_type}失败: {error_msg}")

                elif status in ("SUBMITTED", "PROCESSING", "RUNNING", "QUEUED"):
                    print(f"  [{elapsed}s] 状态: {status}，继续等待...")
                    time.sleep(DEFAULT_POLL_INTERVAL)

                else:
                    # 尝试旧格式兼容
                    if "data" in data:
                        status = data["data"].get("status", "UNKNOWN")
                        if status == "SUCCESS":
                            print(f"✅ {task_type}完成（耗时 {elapsed} 秒）")
                            return data["data"]
                    raise RunningHubTaskError(f"未知的任务状态: {status}")

            except requests.exceptions.RequestException as e:
                print(f"  [{elapsed}s] 查询失败: {e}，重试...")
                time.sleep(DEFAULT_POLL_INTERVAL)

    # -------------------------------------------------------------------------
    # 文件下载
    # -------------------------------------------------------------------------

    def _download_image(
        self,
        image_url: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        下载图像文件

        Args:
            image_url: 图像 URL
            output_path: 输出路径，如果未提供则使用临时文件

        Returns:
            下载的文件路径

        Raises:
            RunningHubError: 下载失败
        """
        # 如果未指定输出路径，使用临时文件
        if not output_path:
            import tempfile

            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            output_path = os.path.join(temp_dir, f"rh_image_{timestamp}.png")

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"📥 下载图像...")
        print(f"  URL: {image_url[:60]}...")
        print(f"  保存到: {output_path}")

        try:
            response = requests.get(image_url, stream=True, timeout=60)

            if response.status_code != 200:
                raise RunningHubError(f"下载图像失败，状态码: {response.status_code}")

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
            print(f"  文件大小: {file_size:.2f} MB")

            return output_path

        except requests.exceptions.RequestException as e:
            raise RunningHubError(f"下载图像失败: {e}")

    # -------------------------------------------------------------------------
    # 响应检查
    # -------------------------------------------------------------------------

    def _check_response(self, response: requests.Response, action: str) -> None:
        """
        检查 API 响应是否成功

        Args:
            response: HTTP 响应对象
            action: 操作描述（用于错误信息）

        Raises:
            RunningHubError: 如果响应表示失败
        """
        if response.status_code != 200:
            raise RunningHubError(
                f"{action}失败:\n"
                f"  状态码: {response.status_code}\n"
                f"  响应: {response.text}"
            )

        data = response.json()

        # RunningHub API 返回格式: {"code": 0, "data": {...}}
        if "code" in data and data["code"] != 0:
            raise RunningHubError(
                f"{action}失败:\n"
                f"  错误码: {data['code']}\n"
                f"  消息: {data.get('message', '未知错误')}"
            )


# =============================================================================
# 工厂函数
# =============================================================================


def get_rh_client(key_type: str = "auto") -> RunningHubClient:
    """
    创建并返回 RunningHub 客户端实例

    Args:
        key_type: Key 类型
            - "auto": 自动选择（默认）
            - "enterprise": 使用企业级 Key（图像生成）
            - "creator": 使用创作级 Key（视频生成）

    Returns:
        配置好的 RunningHubClient 实例

    Raises:
        RunningHubAuthError: 如果 API 密钥未配置
    """
    if key_type == "enterprise":
        api_key = get_image_api_key()
    elif key_type == "creator":
        api_key = get_video_api_key()
    else:
        # 兼容模式：使用 RH_API_KEY 或自动检测
        api_key = (
            os.environ.get("RH_API_KEY") or get_enterprise_key() or get_creator_key()
        )
        if not api_key:
            raise RunningHubAuthError(
                "RunningHub API 密钥未配置。\n"
                "请设置以下环境变量之一：\n"
                "  export RH_API_KEY='your-api-key'              # 通用密钥\n"
                "  export RH_ENTERPRISE_KEY='your-enterprise-key' # 企业级密钥\n"
                "  export RH_CREATOR_KEY='your-creator-key'        # 创作级密钥"
            )

    return RunningHubClient(api_key=api_key)


def get_image_client() -> RunningHubClient:
    """
    创建用于图像生成的客户端（使用企业级 Key）

    Returns:
        配置好的 RunningHubClient 实例
    """
    return RunningHubClient(api_key=get_image_api_key())


def get_video_client() -> RunningHubClient:
    """
    创建用于视频生成的客户端（使用创作级 Key）

    Returns:
        配置好的 RunningHubClient 实例
    """
    return RunningHubClient(api_key=get_video_api_key())


# =============================================================================
# 命令行测试
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RunningHub API 测试")
    parser.add_argument("--test", action="store_true", help="运行连接测试")
    parser.add_argument(
        "--model", choices=["v2", "pro"], default="pro", help="图像模型"
    )
    parser.add_argument("--prompt", type=str, help="测试提示词")

    args = parser.parse_args()

    if args.test:
        print("=" * 60)
        print("RunningHub API 连接测试")
        print("=" * 60)

        try:
            # 检查环境变量
            api_key = os.environ.get("RH_API_KEY")
            if api_key:
                print(f"✅ RH_API_KEY 已设置: {api_key[:8]}...{api_key[-4:]}")
            else:
                print("❌ RH_API_KEY 未设置")
                print("请设置环境变量: export RH_API_KEY='your-api-key'")
                exit(1)

            # 创建客户端
            client = RunningHubClient()

            # 如果提供了提示词，运行生成测试
            if args.prompt:
                print("\n" + "=" * 60)
                print("图像生成测试")
                print("=" * 60)

                test_prompt = args.prompt
                output_dir = "test_outputs"
                os.makedirs(output_dir, exist_ok=True)

                image_path = client.generate_image(
                    prompt=test_prompt,
                    model=args.model,
                    resolution="1K",  # 使用低分辨率测试
                    output_path=os.path.join(output_dir, "test_image.png"),
                )

                print(f"\n✅ 测试成功！")
                print(f"生成的图像: {image_path}")
            else:
                print("\n✅ 客户端初始化成功！")
                print("使用 --prompt 'your prompt' 运行生成测试")

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback

            traceback.print_exc()
            exit(1)
    else:
        parser.print_help()
