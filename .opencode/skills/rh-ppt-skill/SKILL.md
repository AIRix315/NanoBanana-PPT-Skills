---
name: rh-ppt-skill
description: Generate high-quality PPT images and dynamic video presentations using RunningHub API. Use when user requests PPT generation, slide creation, or presentation videos. Invoke for keywords like PPT, 幻灯片, 演示文稿, presentation, slides.
license: MIT
allowed-tools:
  - read
  - write
  - bash
  - rhmcp_rh_upload_media
  - rhmcp_rh_execute_app
  - rhmcp_rh_query_task
metadata:
  version: "2.2.0"
  author: "AIRix315"
  platform: "RunningHub"
  triggers: PPT, 幻灯片, 演示文稿, presentation, slides, 生成PPT, generate slides
  output-format: images, videos
---

# RH-PPT-Skill - RunningHub PPT 动态视频生成技能

基于 RunningHub API 自动生成高质量 PPT 图片和动态视频演示。

## 📋 Skill 概述

| 属性 | 值 |
|------|------|
| 名称 | rh-ppt-skill |
| 版本 | 2.2.0 |
| 平台 | RunningHub |
| 功能 | PPT 图片生成 + 动态视频演示 |

---

## ⚡ 推荐配置（Agent 默认行为）

> 🚨 **Agent 必读**：以下为默认配置，Agent 执行时优先使用，不得自主切换高价模型

### 图片生成配置

| 配置项 | 推荐值 | 其他可选 | Agent 行为 |
|--------|--------|----------|------------|
| **分辨率** | **4K**（推荐） | 2K、1K | ✅ 默认使用 4K，用户要求才切换 |

### 视频生成配置

| 配置项 | 推荐值 | 价格 | Agent 行为 |
|--------|--------|------|------------|
| **视频模型** | **v3.1-fast**（推荐） | ~￥0.5/段 | ✅ 默认选择 |
| 高质量备选 | v3.1-pro | ~￥1.4/段 | 用户明确要求"高质量" |
| 专业级 | kling/seedance | ￥2+/段 | 用户明确指定模型名 |

### Agent 规则（强制遵守）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Agent 模型选择规则                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ✅ 允许：默认使用 v3.1-fast + 4K                                   │
│  ✅ 允许：用户明确要求"高质量"时使用 v3.1-pro                        │
│  ✅ 允许：用户明确指定模型名时使用对应模型                           │
│                                                                      │
│  ❌ 禁止：Agent 自主选择高价模型                                     │
│  ❌ 禁止：Agent 推荐"更好的模型"                                     │
│  ❌ 禁止：Agent 询问"是否使用更好的模型"                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 成本预估（5页 PPT）

| 配置 | 图片 | 视频 | 总计 |
|------|------|------|------|
| **推荐配置** (v3.1-fast + 4K) | ￥1.5 | ￥2.0 | **￥3.5** |
| 高质量配置 (v3.1-pro + 4K) | ￥1.5 | ￥5.6 | ￥7.1 |
| 仅图片（不生成视频） | ￥1.5 | - | ￥1.5 |

---

## 🚀 快速开始（Agent 执行指南）

### 前置条件检查

**必须确认：**
1. `.env` 文件存在且包含 `RH_API_KEY`
2. Python 环境已安装依赖：`pip install requests pillow python-dotenv`
3. FFmpeg 已安装（视频功能需要）

**检查命令：**
```bash
# 检查 Key 配置
grep RH_API_KEY .env

# 检查 FFmpeg
ffmpeg -version
```

---

## 🛠️ 可用工具与调用时机

### 工具清单

| 工具脚本 | 功能 | 调用时机 | 预估时间 | API成本 |
|----------|------|----------|----------|---------|
| `generate_ppt.py` | 生成PPT图片 | 总是第一步 | ~30秒/页 | 图片模型计费 |
| `generate_ppt_video.py` | 生成转场视频+合成完整视频 | 用户需要视频时 | ~90-120秒/段 | 视频模型计费 |

### 调用流程图

```
用户请求 PPT
     │
     ▼
┌─────────────────┐
│ 1. 检查 .env    │ ← 必须有 RH_API_KEY
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 收集用户输入 │ ← 主题/文档/风格/页数
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 规划内容     │ ← 生成 slides_plan.json
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 生成图片     │ ← 调用 generate_ppt.py
│    (必需步骤)   │   时间: ~30秒 × 页数
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│ 5a. 返回图片   │    │ 5b. 生成视频     │
│    (可选结束)   │    │    (用户需要)    │
└─────────────────┘    └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ 6. 返回完整结果 │
                       └─────────────────┘
```

---

## 📝 Agent 执行流程（详细）

### 阶段 1: 环境检查

**必须检查：**

```bash
# Step 1: 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "错误: 请创建 .env 文件并配置 RH_API_KEY"
    exit 1
fi

# Step 2: 验证 Key 配置
grep -q "RH_API_KEY=" .env || {
    echo "错误: .env 中缺少 RH_API_KEY"
    exit 1
}

# Step 3: 检查 FFmpeg（视频功能需要）
command -v ffmpeg >/dev/null 2>&1 || {
    echo "警告: FFmpeg 未安装，视频功能将不可用"
    echo "安装: brew install ffmpeg (macOS) 或 sudo apt install ffmpeg (Linux)"
}
```

**Agent 行动：**
- 如果 Key 未配置 → 告诉用户："请先配置 RH_API_KEY，获取地址：https://www.runninghub.cn"
- 如果 FFmpeg 未安装 → 提示用户视频功能需要安装 FFmpeg

---

### 阶段 2: 收集用户输入

**收集信息清单：**

| 信息 | 必需 | 获取方式 | 默认值 |
|------|------|----------|--------|
| 文档/主题内容 | ✅ | 用户直接提供或读取文件 | - |
| 风格 | ❌ | 列出 `assets/styles/` 目录文件 | 渐变毛玻璃 |
| 页数 | ❌ | 询问 | 5页 |
| 分辨率 | ❌ | 询问 | **4K**（推荐） |
| 是否生成视频 | ❌ | 询问 | 否（仅图片） |

**风格文件位置：**
```
assets/styles/
├── gradient-glass.md      # 渐变毛玻璃（科技/商务）
└── vector-illustration.md # 矢量插画（教育/培训）
```

**Agent 代码示例：**

```python
# 扫描可用风格
styles_dir = "assets/styles/"
available_styles = [f.stem for f in Path(styles_dir).glob("*.md")]

# 如果有多个风格，询问用户
if len(available_styles) > 1:
    # 使用 question 工具让用户选择
    ...
else:
    style = available_styles[0]
```

---

### 阶段 3: 内容规划

**根据页数推荐结构：**

| 页数 | 推荐结构 |
|------|----------|
| 5页 | 封面 → 要点1 → 要点2 → 要点3 → 总结 |
| 5-10页 | 封面 → 引言(1-2) → 核心(4-5) → 案例(1-2) → 总结 |
| 10-15页 | 封面 → 目录 → 章节(每章3页) → 数据 → 总结 |
| 20-25页 | 封面 → 目录 → 引言 → 章节(每章4页) → 案例研究 → 数据 → 总结 |

**生成规划文件：**

```json
{
  "title": "PPT标题",
  "total_slides": 5,
  "style": "渐变毛玻璃卡片风格",
  "resolution": "2K",
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "标题：...\n副标题：..."
    },
    ...
  ]
}
```

**保存位置：** `test_slides.json` 或用户指定路径

---

### 阶段 4: 生成 PPT 图片

**调用命令：**

```bash
python scripts/generate_ppt.py \
  --plan test_slides.json \
  --style assets/styles/vector-illustration.md \
  --resolution 4K
```

**参数说明：**

| 参数 | 必需 | 说明 |
|------|------|------|
| `--plan` | ✅ | JSON 规划文件路径 |
| `--style` | ✅ | 风格文件路径 |
| `--resolution` | ❌ | 1K / 2K / **4K**，默认 **4K**（推荐） |
| `--output` | ❌ | 输出目录，默认 `outputs/YYYYMMDD_HHMMSS/` |
| `--draft` | ❌ | 草稿模式（快速生成） |

**时间预估：**
- 4K 分辨率：~60 秒/页（推荐）
- 2K 分辨率：~30 秒/页
- 5 页 PPT (4K)：约 5 分钟

**成功输出：**
```
outputs/YYYYMMDD_HHMMSS/
├── images/
│   ├── slide-01.png
│   ├── slide-02.png
│   ├── slide-03.png
│   ├── slide-04.png
│   └── slide-05.png
├── index.html          # 图片播放器
└── prompts.json        # 提示词记录（调试用）
```

**注意：** 输出目录自动使用时间戳命名，每次生成独立保存，不会覆盖之前的结果。

**错误处理：**

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `RH_API_KEY 未配置` | .env 缺少 Key | 告诉用户配置 Key |
| `API 余额不足` | 账户余额为0 | 告诉用户充值 |
| `生成超时` | 网络或API问题 | 稍后重试 |
| `模型不可用` | 模型维护中 | 更换模型参数 |

---

### 阶段 5: 生成转场视频（可选）

**判断是否需要：**
- 用户明确要求视频
- 用户问答中选择"生成视频"

**前提条件：**
- ✅ PPT 图片已生成
- ✅ FFmpeg 已安装
- ✅ RH_API_KEY 有余额（视频生成需要更多费用）

**工作流程：**

#### 5.1 分析图片生成转场提示词

**Agent 任务：**
1. 读取所有生成的 PPT 图片
2. 分析每对相邻图片的视觉差异
3. 为每个转场生成精准的视频提示词

**提示词模板（保存在 `transition_prompts.json`）：**

```json
{
  "preview": {
    "prompt": "首页循环预览动画：[描述封面页的动态效果]"
  },
  "transitions": [
    {
      "from_slide": 1,
      "to_slide": 2,
      "prompt": "从封面过渡到内容页：[描述转场动画]"
    },
    ...
  ]
}
```

**转场提示词写作要点：**
- 描述起始帧到结束帧的**动态过渡**
- 保持风格一致（渐变毛玻璃 / 矢量插画）
- 控制在 50-100 字
- 避免提到文字（视频模型可能模糊文字）

#### 5.2 调用视频生成命令

```bash
python scripts/generate_ppt_video.py \
  --slides-dir outputs/YYYYMMDD_HHMMSS/images/ \
  --output-dir outputs/YYYYMMDD_HHMMSS_video/ \
  --prompts-file outputs/YYYYMMDD_HHMMSS/transition_prompts.json \
  --video-provider enterprise-video \
  --enterprise-model v3.1-fast
```

**视频模型选择（Agent 必读）：**

```
┌─────────────────────────────────────────────────────────────────────┐
│              视频模型推荐配置（按价格从低到高）                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ╔═══════════════════════════════════════════════════════════════╗  │
│  ║   【默认推荐】v3.1-fast                                        ║  │
│  ╠═══════════════════════════════════════════════════════════════╣  │
│  ║   端点: /rhart-video-v3.1-fast/start-end-to-video            ║  │
│  ║   特点: 首尾帧视频、8秒固定时长                               ║  │
│  ║   分辨率: 720p / 1080p / 4k                                   ║  │
│  ║   价格: ~￥0.5/段                                              ║  │
│  ║   适用: 调试、测试、日常使用                                   ║  │
│  ╚═══════════════════════════════════════════════════════════════╝  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │   【高质量】v3.1-pro（用户明确要求"高质量"）                │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │   端点: /rhart-video-v3.1-pro-official/reference-to-video   │    │
│  │   特点: 高画质输出、支持自动音频                              │    │
│  │   分辨率: 720p / 1080p / 4k                                  │    │
│  │   价格: ~￥1.4/段                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │   【专业级】其他模型（用户明确指定模型名）                   │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │   kling: ~￥2.1-5.6/段                                       │    │
│  │   seedance: 创作级 Key，4-15秒                                │    │
│  │   x-low: 多图参考，6-30秒                                     │    │
│  │                                                              │    │
│  │   ⚠️  Agent 不得自主选择这些高价模型                         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Agent 选择规则：**

1. **首次执行**：使用 `v3.1-fast`（~￥0.5/段）
2. **用户要求"高质量"**：使用 `v3.1-pro`（~￥1.4/段）
3. **用户指定模型名**：使用指定模型
4. **禁止**：Agent 自主切换到高价模型

**时间预估：**
- 每段转场视频：~90-120 秒
- 5 页 PPT（4 段转场）：~6-8 分钟
- 视频合成：~10 秒

**成功输出：**
```
outputs/YYYYMMDD_HHMMSS_video/
├── videos/
│   ├── preview.mp4              # 首页预览
│   ├── transition_01_to_02.mp4  # 转场视频
│   ├── transition_02_to_03.mp4
│   ├── transition_03_to_04.mp4
│   └── transition_04_to_05.mp4
├── video_index.html             # 交互播放器
└── full_ppt_video.mp4           # 完整视频
```

---

### 阶段 6: 返回结果

**仅图片模式：**

```
✅ PPT 图片生成完成！

📁 输出目录: outputs/YYYYMMDD_HHMMSS/
🖼️ PPT 图片: outputs/YYYYMMDD_HHMMSS/images/slide-*.png
🎬 播放网页: outputs/YYYYMMDD_HHMMSS/index.html

打开播放器:
  open outputs/YYYYMMDD_HHMMSS/index.html

播放器快捷键:
  ← → : 切换页面
  ESC : 全屏切换
  空格 : 自动播放
```

**视频模式：**

```
✅ PPT 动态视频生成完成！

📁 输出目录: outputs/YYYYMMDD_HHMMSS_video/
🖼️ PPT 图片: outputs/YYYYMMDD_HHMMSS/images/
🎬 转场视频: outputs/YYYYMMDD_HHMMSS_video/videos/
🎮 交互播放器: outputs/YYYYMMDD_HHMMSS_video/video_index.html
🎥 完整视频: outputs/YYYYMMDD_HHMMSS_video/full_ppt_video.mp4

打开播放器:
  open outputs/YYYYMMDD_HHMMSS_video/video_index.html

打开完整视频:
  open outputs/YYYYMMDD_HHMMSS_video/full_ppt_video.mp4

视频结构:
  首页预览 → 转场1→2 → 静态页2(3秒) → 转场2→3 → ...
```

---

## 💰 成本与时间预估

### RunningHub 计费说明

**账户状态检查：**
- 注册即获得普通会员 Key
- 企业共享 Key 需充值余额
- 按生成次数计费

**成本预估（仅供参考）：**

| 操作 | 模型 | 预估成本 | 时间 |
|------|------|----------|------|
| PPT 图片生成（4K） | 全能图片PRO | ~￥0.3/页 | 60秒/页 |
| PPT 图片生成（2K） | 全能图片PRO | ~￥0.2/页 | 30秒/页 |
| 转场视频（推荐） | v3.1-fast | ~￥0.5/段 | 90秒/段 |
| 转场视频（高质量） | v3.1-pro | ~￥1.4/段 | 90秒/段 |

**Agent 提示用户：**
- "5 页 PPT（仅图片，4K）：约 ￥1.5，5 分钟"
- "5 页 PPT（推荐配置 v3.1-fast + 4K）：约 ￥3.5，8 分钟"
- "5 页 PPT（高质量配置 v3.1-pro + 4K）：约 ￥7.1，8 分钟"

---

## ⚠️ 错误处理指南

### 常见错误及 Agent 应对

| 错误信息 | Agent 行动 |
|----------|-----------|
| `RH_API_KEY 未配置` | 告诉用户："请先配置 RH_API_KEY，获取地址：https://www.runninghub.cn" |
| `API 余额不足` | 告诉用户："账户余额不足，请充值后重试" |
| `生成超时` | 重试 1 次，若仍失败请用户稍后再试 |
| `图片内容违规` | 告诉用户："内容可能触发审核，请修改后重试" |
| `FFmpeg 未安装` | 仅图片模式可用，视频功能需安装 FFmpeg |
| `视频生成失败` | 检查 Key 余额，提示用户可能需要充值 |

### 错误处理代码示例

```python
try:
    result = subprocess.run(cmd, capture_output=True, timeout=300)
    if result.returncode != 0:
        error_msg = result.stderr.decode()
        
        if "余额不足" in error_msg or "INSUFFICIENT_FUNDS" in error_msg:
            print("❌ RunningHub 账户余额不足")
            print("请充值后重试：https://www.runninghub.cn")
            return None
            
        elif "API_KEY" in error_msg:
            print("❌ RH_API_KEY 未配置或无效")
            print("请检查 .env 文件中的 RH_API_KEY")
            return None
            
        else:
            print(f"❌ 生成失败: {error_msg}")
            return None
            
except subprocess.TimeoutExpired:
    print("⏳ 生成超时，正在重试...")
    # 重试逻辑
```

---

## 📁 输出文件说明

**注意：** 所有输出使用时间戳目录命名，每次生成独立保存，不会覆盖之前结果。

### 图片模式输出

```
outputs/YYYYMMDD_HHMMSS/
├── images/
│   ├── slide-01.png          # 第1页图片
│   ├── slide-02.png          # 第2页图片
│   └── ...
├── index.html                # 图片播放器
└── prompts.json              # 提示词记录（调试用）
```

### 视频模式输出

```
outputs/YYYYMMDD_HHMMSS_video/
├── videos/                   # 视频素材
│   ├── preview.mp4           # 首页预览（可选）
│   ├── transition_01_to_02.mp4
│   ├── transition_02_to_03.mp4
│   └── ...
├── video_index.html          # 交互播放器
└── full_ppt_video.mp4        # 完整视频
```

### 目录命名规则

- **图片输出**: `outputs/YYYYMMDD_HHMMSS/` (如 `outputs/20260404_221500/`)
- **视频输出**: `outputs/YYYYMMDD_HHMMSS_video/` (如 `outputs/20260404_221500_video/`)
- 时间戳格式：年月日_时分秒
- 原始图片保存在 `_video` 版本的 `images/` 子目录中

### ⚠️ 产出物存储提醒（重要！）

**生成完成后，Agent 应立即提醒用户保存产出物：**

```
✅ 项目完成！

⚠️ 重要提醒：
产出物已保存在 outputs/YYYYMMDD_HHMMSS/ 目录
- 图片总大小：~30-50MB（5页 4K）
- 视频总大小：~10-20MB（4段转场 + 合成）

请尽快将产出物保存到：
- 云盘（Google Drive / 百度网盘 / OneDrive）
- 本地永久存储
- 或下载到用户设备

服务器存储空间有限，定期清理可避免空间堵塞。
```

**清理命令（用户确认后执行）：**
```bash
# 清理指定时间戳目录
rm -rf outputs/YYYYMMDD_HHMMSS*
```

---

## 🎯 最佳实践（Agent 注意事项）

### 时间管理

| 内容量 | 页数 | 仅图片 | 含视频 |
|--------|------|--------|--------|
| 少量 | 5页 | ~2分钟 | ~8分钟 |
| 中等 | 10页 | ~4分钟 | ~15分钟 |
| 大量 | 20页 | ~8分钟 | ~30分钟 |

**Agent 提示：**
- 超过 10 页 → 提示用户"内容较多，可能需要等待较长时间"
- 需要视频 → 提示用户"视频生成需要额外等待"

### 成本控制

- 默认使用低价模型（全能视频X低价版）
- 用户要求高质量时推荐 V3.1-pro
- 明确告知预估成本

### 质量控制

- 内容规划时检查每页字数（建议 50-150 字）
- 避免单页内容过多
- 封面页保持简洁

### 存储空间管理

**关键提醒：**
- 服务器存储空间有限
- 每次 PPT+视频生成约 50-100MB
- **项目完成后必须提醒用户保存并清理**
- 建议用户将产出物转移至云盘或本地永久存储

---

## 🔄 版本历史

### v2.1.0 (当前)

- 🔄 **平台迁移**：从 Gemini/可灵 迁移到 RunningHub
- 💰 **成本优化**：使用全能视频X低价版
- 🎬 **视频提供者**：支持多种视频模型选择
- 📝 **SKILL 重构**：针对 Agent 执行优化

### v2.0.0

- 🎬 新增视频功能
- 🎞️ 智能转场
- 🔧 参数统一

---

## 📞 技术支持

- API 文档：`API_MANAGEMENT.md`
- 环境配置：`ENV_SETUP.md`
- 架构说明：`ARCHITECTURE.md`
- 快速开始：`QUICKSTART.md`

---

**Agent 执行原则：**
1. ✅ 先检查环境，再执行
2. ✅ 明确告知用户时间和成本
3. ✅ 错误时提供具体解决方案
4. ✅ 返回结果时包含打开方式
5. ✅ 视频功能需要确认 FFmpeg 和余额