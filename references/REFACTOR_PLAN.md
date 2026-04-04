# RH-PPT-Skill 重构规划文档

> **项目重构目标**：将 NanoBanana-PPT-Skills 迁移为 RH-PPT-Skill，使用 RunningHub 国内中转平台替代 Gemini 直连 API，并扩展多模型支持。

---

## 一、项目重命名

### 1.1 Git 配置 ✅ 已完成

| 配置项 | 原值 | 新值 |
|--------|------|------|
| origin | `op7418/NanoBanana-PPT-Skills` | `AIRix315/NanoBanana-PPT-Skills` |
| upstream | - | `op7418/NanoBanana-PPT-Skills` |

### 1.2 需要重命名的项

| 类型 | 原名称 | 新名称 | 文件位置 |
|------|--------|--------|----------|
| 项目名 | NanoBanana PPT Skills | RH-PPT-Skill | README.md, SKILL.md |
| 仓库名 | NanoBanana-PPT-Skills | RH-PPT-Skills | 文档中所有引用 |
| Skill ID | ppt-generator-pro | rh-ppt-skill | SKILL.md 元数据 |
| 安装路径 | ppt-generator | rh-ppt-skill | SKILL.md, README.md |

---

## 二、API 迁移：GEMINI_API_KEY → RH_API_KEY

### 2.1 环境变量变更

| 原变量 | 新变量 | 说明 |
|--------|--------|------|
| `GEMINI_API_KEY` | `RH_API_KEY` | RunningHub API 密钥 |
| `KLING_ACCESS_KEY` | `KLING_ACCESS_KEY` | 保持不变 |
| `KLING_SECRET_KEY` | `KLING_SECRET_KEY` | 保持不变 |

### 2.2 受影响的文件

#### 🔴 必须修改

| 文件 | 修改内容 |
|------|---------|
| `generate_ppt.py` | API 客户端初始化、调用逻辑 |
| `.env.example` | 环境变量说明 |
| `API_MANAGEMENT.md` | API 配置文档 |
| `ENV_SETUP.md` | 环境变量设置指南 |
| `SECURITY.md` | 安全说明 |

#### 🟡 需要更新

| 文件 | 修改内容 |
|------|---------|
| `README.md` | 安装说明、快速开始 |
| `SKILL.md` | Skill 文档 |
| `QUICKSTART.md` | 快速开始指南 |
| `ARCHITECTURE.md` | 架构文档 |

### 2.3 API 调用模式对比

| 维度 | Gemini 直连 | RunningHub 中转 |
|------|-------------|-----------------|
| **认证方式** | `genai.Client(api_key=...)` | `Authorization: Bearer {api_key}` |
| **调用模式** | 同步调用 | 异步提交 + 轮询 |
| **端点格式** | `model="gemini-3-pro-image-preview"` | `POST /openapi/v2/rhart-image-{model}/text-to-image` |
| **返回方式** | `response.parts[].as_image()` | `results[0].url` (需下载) |
| **等待机制** | 阻塞等待 | 轮询 `taskId` 直到 `status="SUCCESS"` |

---

## 三、图像模型支持扩展

### 3.1 RunningHub 支持的图像模型

| 模型 ID | RunningHub 名称 | 特点 | 用途 |
|---------|-----------------|------|------|
| `rhart-image-v2` | 全能图片V2 | Gemini 3.1 Flash，快速、便宜 | 草稿预览 |
| `rhart-image-n-pro` | 全能图片PRO | Gemini 3 Pro，高质量、4K | 最终输出 |

### 3.2 API 参数映射

#### Gemini → RunningHub 参数对照表

| Gemini 参数 | RunningHub 参数 | 说明 |
|-------------|-----------------|------|
| `aspect_ratio="16:9"` | `aspectRatio="16:9"` | 参数名不同，值相同 |
| `image_size="2K"` | `resolution="2K"` | 参数名不同，值相同 |
| `model="..."` | 端点路径 | 模型通过端点选择 |

### 3.3 新增命令行参数

```python
# generate_ppt.py 新增参数
parser.add_argument(
    "--model",
    choices=["v2", "pro"],
    default="pro",
    help="图像生成模型: v2(草稿/快速) 或 pro(高质量/最终)"
)

parser.add_argument(
    "--draft",
    action="store_true",
    help="草稿模式快捷方式: 使用 v2 + 1K 快速生成"
)
```

### 3.4 使用示例

```bash
# 草稿模式（快速、便宜）
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --draft

# 最终模式（高质量）
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model pro --resolution 4K

# 指定模型
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model v2 --resolution 2K
```

---

## 四、视频模型支持扩展

### 4.1 当前视频模型

| 模型 | API 文件 | 说明 |
|------|---------|------|
| 可灵 AI | `kling_api.py` | 当前唯一支持 |

### 4.2 RunningHub 支持的视频模型

| 模型 ID | RunningHub 名称 | 特点 | 状态 |
|---------|-----------------|------|------|
| `kling-v2-6` | Kling 可灵 | 原有支持 | ✅ 已有 |
| `seedance-v2` | Seedance 2.0 | 字节跳动，文/图生视频 | 🆕 新增 |
| `ltx-2-3` | LTX-2.3 | 文生视频 | 🆕 新增 |

### 4.3 视频模型抽象层设计

```python
# 新建 video_providers/base.py
class VideoProvider(ABC):
    @abstractmethod
    def generate_video(
        self,
        image_start: str,
        image_end: Optional[str],
        prompt: str,
        output_path: str,
        **kwargs
    ) -> str:
        """Generate video and return path."""
        pass

# 新建 video_providers/kling.py
class KlingProvider(VideoProvider):
    """可灵 AI 视频提供者（原有）"""
    ...

# 新建 video_providers/seedance.py
class SeedanceProvider(VideoProvider):
    """Seedance 2.0 视频提供者（新增）"""
    ...

# 新建 video_providers/ltx.py
class LTXProvider(VideoProvider):
    """LTX-2.3 视频提供者（新增）"""
    ...

# 新建 video_providers/factory.py
def create_video_provider(provider: str, api_key: str) -> VideoProvider:
    providers = {
        "kling": KlingProvider,
        "seedance": SeedanceProvider,
        "ltx": LTXProvider,
    }
    return providers[provider](api_key)
```

### 4.4 视频提供者选择参数

```python
# generate_ppt_video.py 新增参数
parser.add_argument(
    "--video-provider",
    choices=["kling", "seedance", "ltx"],
    default="kling",
    help="视频生成提供者 (default: kling)"
)
```

---

## 五、文件结构变更

### 5.1 新增文件

```
RH-PPT-Skills/
├── rh_api.py                    # 新增：RunningHub API 客户端
├── video_providers/              # 新增：视频提供者模块
│   ├── __init__.py
│   ├── base.py                   # 抽象基类
│   ├── factory.py                # 提供者工厂
│   ├── kling.py                  # 可灵（原有逻辑迁移）
│   ├── seedance.py               # Seedance 2.0
│   └── ltx.py                    # LTX-2.3
└── provider_config.py            # 新增：提供者配置管理
```

### 5.2 修改文件

```
generate_ppt.py          # 重构：API 调用逻辑
generate_ppt_video.py   # 扩展：视频提供者选择
kling_api.py            # 可能：迁移到 video_providers/kling.py
.env.example            # 更新：环境变量
README.md               # 重写：项目说明
SKILL.md                # 重写：Skill 文档
```

### 5.3 删除/弃用文件

```
无删除，保持向后兼容
```

---

## 六、代码重构详情

### 6.1 `generate_ppt.py` 重构

#### 原代码结构

```python
def get_gemini_client():
    from google import genai
    api_key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def generate_slide(prompt, slide_number, output_dir, resolution):
    client = get_gemini_client()
    response = client.models.generate_content(...)
    image = part.as_image()
    image.save(image_path)
```

#### 新代码结构

```python
# rh_api.py
class RunningHubClient:
    BASE_URL = "https://www.runninghub.cn/openapi/v2"
    
    ENDPOINTS = {
        "v2": "/rhart-image-v2/text-to-image",
        "pro": "/rhart-image-n-pro/text-to-image",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
    
    def submit_task(self, model: str, prompt: str, 
                    aspect_ratio: str, resolution: str) -> str:
        """Submit generation task, return taskId."""
        endpoint = self.ENDPOINTS[model]
        response = self.session.post(
            f"{self.BASE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "prompt": prompt,
                "aspectRatio": aspect_ratio,
                "resolution": resolution,
            }
        )
        return response.json()["taskId"]
    
    def poll_task(self, task_id: str, timeout: int = 300) -> dict:
        """Poll until success, return results."""
        start = time.time()
        while time.time() - start < timeout:
            response = self.session.get(
                f"{self.BASE_URL}/task/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            data = response.json()
            if data["status"] == "SUCCESS":
                return data["results"][0]
            elif data["status"] == "FAILED":
                raise Exception(data.get("errorMessage", "Task failed"))
            time.sleep(3)
        raise TimeoutError(f"Task {task_id} timeout")
    
    def download_image(self, url: str, save_path: str) -> str:
        """Download image from URL."""
        response = self.session.get(url)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path

# generate_ppt.py
def get_rh_client():
    api_key = os.environ.get("RH_API_KEY")
    if not api_key:
        raise ValueError("RH_API_KEY not set")
    return RunningHubClient(api_key)

def generate_slide(prompt, slide_number, output_dir, resolution, model="pro"):
    client = get_rh_client()
    
    # Submit task
    task_id = client.submit_task(
        model=model,
        prompt=prompt,
        aspect_ratio="16:9",
        resolution=resolution,
    )
    
    # Poll for completion
    result = client.poll_task(task_id)
    
    # Download image
    image_path = os.path.join(output_dir, "images", f"slide-{slide_number:02d}.png")
    client.download_image(result["url"], image_path)
    
    return image_path
```

### 6.2 `video_providers/` 模块设计

```python
# base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class VideoProvider(ABC):
    """Abstract base class for video generation providers."""
    
    @abstractmethod
    def generate_video(
        self,
        image_start: str,
        image_end: Optional[str] = None,
        prompt: str = "",
        output_path: str = "",
        duration: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from images.
        
        Args:
            image_start: Path to start frame image
            image_end: Path to end frame image (optional)
            prompt: Video generation prompt
            output_path: Where to save the video
            duration: Video duration in seconds
            **kwargs: Provider-specific options
        
        Returns:
            Dict with 'success', 'video_path', 'metadata'
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for logging."""
        pass

# kling.py
class KlingProvider(VideoProvider):
    """Kling AI video provider (existing implementation)."""
    
    def __init__(self, access_key: str, secret_key: str):
        self.client = KlingVideoGenerator(access_key, secret_key)
    
    def generate_video(self, image_start, image_end, prompt, output_path, duration=5, **kwargs):
        # ...existing logic from kling_api.py
        pass
    
    def get_provider_name(self) -> str:
        return "Kling AI"

# seedance.py
class SeedanceProvider(VideoProvider):
    """Seedance 2.0 video provider via RunningHub."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.runninghub.cn/openapi/v2"
    
    def generate_video(self, image_start, image_end, prompt, output_path, duration=5, **kwargs):
        # Submit to RunningHub Seedance endpoint
        # Poll for completion
        # Download video
        pass
    
    def get_provider_name(self) -> str:
        return "Seedance 2.0"

# factory.py
def create_video_provider(provider_type: str = "kling") -> VideoProvider:
    """Create video provider based on configuration."""
    
    if provider_type == "kling":
        access_key = os.environ.get("KLING_ACCESS_KEY")
        secret_key = os.environ.get("KLING_SECRET_KEY")
        return KlingProvider(access_key, secret_key)
    
    elif provider_type == "seedance":
        api_key = os.environ.get("RH_API_KEY")
        return SeedanceProvider(api_key)
    
    elif provider_type == "ltx":
        api_key = os.environ.get("RH_API_KEY")
        return LTXProvider(api_key)
    
    else:
        raise ValueError(f"Unknown video provider: {provider_type}")
```

---

## 七、配置文件变更

### 7.1 `.env.example`

```bash
# ===========================================
# RH-PPT-Skill 环境变量配置
# ===========================================

# RunningHub API 密钥（必需）
# 用于：全线图像/视频模型国内中转访问
# 获取地址：https://www.runninghub.cn/enterprise-api/sharedApi
RH_API_KEY=your-runninghub-api-key-here

# 可灵 AI API 密钥（可选，用于视频生成）
# 获取地址：https://klingai.com
KLING_ACCESS_KEY=your-kling-access-key-here
KLING_SECRET_KEY=your-kling-secret-key-here

# ===========================================
# 模型选择（可选）
# ===========================================

# 默认图像模型：v2（草稿）或 pro（高质量）
# RH_IMAGE_MODEL=pro

# 默认视频提供者：kling、seedance、ltx
# RH_VIDEO_PROVIDER=kling
```

### 7.2 `provider_config.py` (新增)

```python
"""Provider configuration management."""

import os
from dataclasses import dataclass
from typing import Literal

@dataclass
class ImageProviderConfig:
    """Image generation provider configuration."""
    provider: Literal["rh"] = "rh"
    model: Literal["v2", "pro"] = "pro"
    api_key: str = ""
    
    @classmethod
    def from_env(cls) -> "ImageProviderConfig":
        return cls(
            provider="rh",
            model=os.environ.get("RH_IMAGE_MODEL", "pro"),
            api_key=os.environ.get("RH_API_KEY", ""),
        )

@dataclass
class VideoProviderConfig:
    """Video generation provider configuration."""
    provider: Literal["kling", "seedance", "ltx"] = "kling"
    api_key: str = ""
    access_key: str = ""
    secret_key: str = ""
    
    @classmethod
    def from_env(cls) -> "VideoProviderConfig":
        return cls(
            provider=os.environ.get("RH_VIDEO_PROVIDER", "kling"),
            api_key=os.environ.get("RH_API_KEY", ""),
            access_key=os.environ.get("KLING_ACCESS_KEY", ""),
            secret_key=os.environ.get("KLING_SECRET_KEY", ""),
        )
```

---

## 八、文档更新清单

### 8.1 README.md 更新大纲

```markdown
# RH-PPT-Skill

> 基于 RunningHub 国内中转平台的 AI PPT 生成工具，支持多模型切换

## 功能特性
- 🖼️ 多图像模型：全能图片PRO（高质量）、全能图片V2（草稿快速）
- 🎬 多视频模型：可灵、Seedance 2.0、LTX-2.3
- 🇨🇳 国内直连：无需翻墙，RunningHub 中转

## 快速开始
### 安装
### 配置 API Key
### 生成 PPT

## 模型选择
| 模式 | 命令 | 特点 | 适用场景 |
|------|------|------|---------|
| 草稿 | --draft | 全能图片V2 + 1K | 快速预览 |
| 最终 | --model pro --resolution 4K | 全能图片PRO + 4K | 高质量输出 |
```

### 8.2 SKILL.md 更新大纲

```markdown
# RH-PPT-Skill - Claude Code Skill

## 元数据
- **Skill 名称**: rh-ppt-skill
- **版本**: 3.0.0
- **描述**: 基于 RunningHub 的 AI PPT 生成工具

## 环境变量
- `RH_API_KEY`（必需）
- `KLING_ACCESS_KEY` / `KLING_SECRET_KEY`（可选）

## 模型配置
### 图像模型
### 视频模型
```

---

## 九、迁移风险评估

### 9.1 技术风险

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| API 调用模式不同 | 🟡 中 | 异步轮询封装为同步接口 |
| 图片下载额外步骤 | 🟢 低 | 封装为统一接口 |
| 依赖变更 | 🟢 低 | 移除 google-genai，添加 requests |
| 向后兼容 | 🟢 低 | 保留原有接口签名 |

### 9.2 业务风险

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| RunningHub 稳定性 | 🟡 中 | 低价渠道版可能不稳定，建议用户测试 |
| 费用变化 | 🟢 低 | 提供成本对比说明 |
| 数据隐私 | 🟢 低 | RunningHub 国内合规 |

---

## 十、实施计划

### 阶段一：核心 API 迁移（优先级：高）

| 任务 | 文件 | 预计时间 |
|------|------|---------|
| 创建 `rh_api.py` | rh_api.py | 2h |
| 重构 `generate_ppt.py` | generate_ppt.py | 3h |
| 更新 `.env.example` | .env.example | 0.5h |
| 单元测试 | tests/ | 1h |

### 阶段二：模型支持扩展（优先级：高）

| 任务 | 文件 | 预计时间 |
|------|------|---------|
| 添加 `--model` 参数 | generate_ppt.py | 0.5h |
| 添加 `--draft` 模式 | generate_ppt.py | 0.5h |
| 测试 V2/PRO 切换 | tests/ | 0.5h |

### 阶段三：视频提供者抽象（优先级：中）

| 任务 | 文件 | 预计时间 |
|------|------|---------|
| 创建 `video_providers/` 模块 | video_providers/ | 2h |
| 迁移可灵逻辑 | video_providers/kling.py | 1h |
| 添加 Seedance 提供者 | video_providers/seedance.py | 2h |
| 添加 LTX 提供者 | video_providers/ltx.py | 1h |
| 更新 `generate_ppt_video.py` | generate_ppt_video.py | 1h |

### 阶段四：文档更新（优先级：中）

| 任务 | 文件 | 预计时间 |
|------|------|---------|
| 重写 README.md | README.md | 1h |
| 重写 SKILL.md | SKILL.md | 1h |
| 更新其他文档 | *.md | 1h |

### 阶段五：测试与发布（优先级：高）

| 任务 | 内容 | 预计时间 |
|------|------|---------|
| 集成测试 | 全流程测试 | 2h |
| 文档审核 | 检查所有说明 | 0.5h |
| Git 提交 | commit + push | 0.5h |

---

## 十一、验收标准

### 功能验收

- [ ] 草稿模式 (`--draft`) 正常工作
- [ ] 最终模式 (`--model pro`) 正常工作
- [ ] V2 模型 (`--model v2`) 正常工作
- [ ] 视频模型切换 (`--video-provider`) 正常工作
- [ ] 环境变量配置正确
- [ ] 错误处理完善

### 文档验收

- [ ] README.md 完整准确
- [ ] SKILL.md 更新
- [ ] .env.example 示例正确
- [ ] API_MANAGEMENT.md 更新
- [ ] ENV_SETUP.md 更新

### 兼容性验收

- [ ] 原有 PPT 生成流程正常
- [ ] 视频生成流程正常
- [ ] 命令行参数兼容
- [ ] 输出格式不变

---

## 十二、后续优化建议

1. **成本优化提示**：在生成前显示预估成本
2. **模型推荐**：根据 PPT 页数自动推荐模型
3. **批量模式**：支持批量生成多个 PPT
4. **缓存机制**：缓存生成的图片，避免重复生成
5. **回退机制**：支持 API 失败时自动切换备用模型

---

**文档版本**: 1.0  
**创建日期**: 2026-04-03  
**作者**: AI Assistant  
**状态**: 规划中（未执行）