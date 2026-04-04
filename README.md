# RH-PPT-Skills

> 从文档到动态视频演示，一站式 PPT 生成工具 | RunningHub API

<div align="center">

![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

**一个 Key，完成所有功能** | [快速开始](#-快速开始) | [详细文档](./QUICKSTART.md)

</div>

---

## 🚀 快速开始

### 第一步：获取 Key

访问 https://www.runninghub.cn 注册并获取 API Key

### 第二步：配置

```bash
# 克隆项目
git clone https://github.com/AIRix315/RH-PPT-Skills.git
cd RH-PPT-Skills

# 配置 Key
cp .env.example .env
# 编辑 .env，填入：RH_API_KEY=your-api-key

# 安装依赖
pip install requests pillow python-dotenv

# 视频功能需要 FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Linux
```

### 第三步：使用

**在 OpenCode/OpenClaw 中直接说：**

> "帮我生成一个关于《AI产品设计原则》的 5 页 PPT，使用渐变毛玻璃风格，需要动态视频"

**或命令行：**

```bash
# 生成 PPT 图片（默认 4K 分辨率）
python scripts/generate_ppt.py --plan slides.json --style assets/styles/gradient-glass.md

# 生成动态视频（可选）
python scripts/generate_ppt_video.py \
  --slides-dir outputs/YYYYMMDD_HHMMSS/images \
  --output-dir outputs/YYYYMMDD_HHMMSS_video \
  --prompts-file outputs/YYYYMMDD_HHMMSS/transition_prompts.json \
  --video-provider enterprise-video \
  --enterprise-model x-low
```

---

## 💰 成本预估

| 内容 | 成本 | 时间 |
|------|------|------|
| 5页 PPT（仅图片） | ~¥0.5 | ~2分钟 |
| 5页 PPT（含视频） | ~¥1.5 | ~8分钟 |
| 10页 PPT（含视频） | ~¥3 | ~15分钟 |

**使用全能视频X低价版最实惠！**

---

## 🎬 视频提供者选择

| 提供者 | 命令参数 | 成本 | 推荐 |
|--------|----------|------|------|
| 全能视频X低价版 | `--enterprise-model x-low` | 💰 | ✅ 默认推荐 |
| 全能视频V3.1-pro | `--enterprise-model v3.1-pro` | 💰💰 | 高质量需求 |

---

## 📖 详细文档

### 核心文档

| 文档 | 说明 | 受众 |
|------|------|------|
| [SKILL.md](./SKILL.md) | Agent 执行指南 | 🤖 Agent |
| [references/QUICKSTART.md](./references/QUICKSTART.md) | 5 分钟快速开始 | 👤 用户 |
| [references/API_MANAGEMENT.md](./references/API_MANAGEMENT.md) | API 密钥配置 | 👤 用户 |
| [references/ARCHITECTURE.md](./references/ARCHITECTURE.md) | 技术架构 | 👤 开发者 |
| [references/SECURITY.md](./references/SECURITY.md) | 安全最佳实践 | 👤 开发者 |

---

## 📁 项目结构

```
RH-PPT-Skills/
├── SKILL.md                    # Agent 执行指南（核心文件）
├── README.md                   # 项目说明
├── .env.example                # 环境变量模板
├── requirements.txt            # Python 依赖
│
├── scripts/                    # 核心脚本
│   ├── generate_ppt.py         # PPT 图片生成
│   ├── generate_ppt_video.py   # 视频生成
│   ├── rh_api.py               # RunningHub API
│   ├── video_composer.py       # FFmpeg 合成
│   └── ...                     # 其他脚本
│
├── assets/                     # 资源文件
│   ├── styles/                 # 视觉风格
│   ├── templates/              # HTML 模板
│   └── prompts/                # 提示词模板
│
├── references/                 # 参考文档
│   ├── QUICKSTART.md          # 快速开始
│   ├── ARCHITECTURE.md        # 架构说明
│   └── ...                    # 其他文档
│
├── tests/                      # 测试文件
│
├── OpenCode/                   # OpenCode 平台适配
│   └── skills/rh-ppt-skill/
│
└── OpenClaw/                   # OpenClaw 平台适配
    └── skills/rh-ppt-skill/
```

## 🎯 平台选择

本项目已适配多个平台，请根据您的使用场景选择：

### 开发调试平台

**[OpenCode](./OpenCode/README.md)** - 适合开发和测试
- 🛠️ Skills 开发和调试
- 🧪 本地测试验证
- 📝 快速迭代开发

**安装路径**: `.opencode/skills/` 或 `.claude/skills/`

### 生产调度平台

**[OpenClaw](./OpenClaw/README.md)** - 适合生产部署
- 🚀 定时任务调度
- 📊 批量生成处理
- ⚙️ 生产环境运行

**安装路径**: `skills/` 或 `.agents/skills/`

### 快速开始

选择您的平台后，按照对应平台的 README.md 进行配置即可。

---

## 🎬 效果演示

<div align="center">

https://github.com/user-attachments/assets/b394de21-2848-489a-8d33-a8e262e60f60

*AI 自动生成 PPT 并添加流畅转场动画 - 从文档分析到视频合成一键完成*

</div>

---

## 📖 简介

NanoBanana PPT Skills 是一个强大的 AI 驱动的 PPT 生成工具，能够：

- 📄 **智能分析文档**，自动提取核心要点并规划 PPT 结构
- 🎨 **生成高质量图片**，使用 RunningHub API（支持多模型切换）
- 🎬 **自动生成转场视频**，使用可灵 AI 创建流畅的页面过渡动画
- 🎮 **交互式视频播放器**，支持键盘控制、循环预览、智能转场
- 🎥 **完整视频导出**，一键合成包含所有转场的完整 PPT 视频

### 🎨 视觉风格

**渐变毛玻璃卡片风格**
- 高端科技感，Apple Keynote 极简主义
- 3D 玻璃物体 + 霓虹渐变
- 电影级光照效果
- 适合：科技产品、商务演示、数据报告

**矢量插画风格**
- 温暖扁平化设计，复古配色
- 黑色轮廓线 + 几何化处理
- 玩具模型般的可爱感
- 适合：教育培训、创意提案、品牌故事

---

## ✨ 功能特性

### 🎯 核心能力

- 🤖 **智能文档分析** - 自动提取核心要点，规划 PPT 内容结构
- 🎨 **多风格支持** - 内置 2 种专业风格，可无限扩展
- 🖼️ **高质量图片** - 16:9 比例，2K/4K 分辨率可选
- 🎬 **AI 转场视频** - 可灵 AI 生成流畅的页面过渡动画
- 🎮 **交互式播放器** - 视频+图片混合播放，支持键盘导航
- 🎥 **完整视频导出** - FFmpeg 合成包含转场的完整 PPT 视频
- 📊 **智能布局** - 封面页、内容页、数据页自动识别
- ⚡ **快速生成** - 2K 约 30 秒/页

### 🆕 视频功能（v2.0）

- 🎬 **首页循环预览** - 自动生成吸引眼球的循环动画
- 🎞️ **智能转场** - 自动生成页面间的过渡视频
- 🎮 **交互式播放** - 按键翻页时播放转场视频，结束后显示静态图片
- 🎥 **完整视频导出** - 合成包含所有转场和静态页的完整视频
- 🔧 **参数统一** - 自动统一所有视频分辨率和帧率，确保流畅播放

### 🛠️ 技术亮点

- ✅ RunningHub API 集成（支持 V2 和 PRO 模型切换）
- ✅ 可灵 AI API 集成（视频生成、数字人、主体库）
- ✅ FFmpeg 视频合成与参数统一
- ✅ 完整的提示词工程和风格管理系统
- ✅ 安全的 .env 环境变量管理
- ✅ 模块化设计，易于扩展
- ✅ 多平台适配（OpenCode、OpenClaw）

---

## 🚀 一键安装

### 快速安装（推荐）

根据您的平台选择对应的安装方式：

#### OpenCode 平台

```bash
# 1. 克隆项目
git clone https://github.com/AIRix315/RH-PPT-Skills.git
cd RH-PPT-Skills

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install requests pillow python-dotenv

# 4. 配置 API 密钥
cp .env.example .env
# 编辑 .env 文件，填入 RH_API_KEY

# 5. 验证安装
python generate_ppt.py --help
```

#### OpenClaw 平台

详见 [OpenClaw/README.md](./OpenClaw/README.md)

### 详细安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/AIRix315/RH-PPT-Skills.git
cd RH-PPT-Skills
```

#### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install requests pillow python-dotenv
```

如果需要视频功能，还需要安装 FFmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 下载 FFmpeg 并添加到系统 PATH
```

#### 4. 配置 API 密钥

**推荐方式：.env 文件**

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中填入你的 API 密钥：

```bash
# RunningHub API 密钥（必需）
RH_API_KEY=your_runninghub_api_key_here

# 可灵 AI API 密钥（可选，用于视频转场功能）
KLING_ACCESS_KEY=your_kling_access_key_here
KLING_SECRET_KEY=your_kling_secret_key_here
```

**替代方式：系统环境变量**

```bash
# zsh 用户 (macOS 默认)
echo 'export RH_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# bash 用户
echo 'export RH_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 5. 验证安装

```bash
python generate_ppt.py --help
```

应该显示帮助信息，表示安装成功。

---

## 🎯 平台适配

本项目已为不同平台提供专门的适配文件：

### OpenCode 适配

**位置**: `OpenCode/skills/rh-ppt-skill/SKILL.md`

**特点**:
- 开发调试
- 快速测试验证
- 本地迭代开发

详见 [OpenCode/README.md](./OpenCode/README.md)

### OpenClaw 适配

**位置**: `OpenClaw/skills/rh-ppt-skill/SKILL.md`

**特点**:
- 生产环境部署
- 定时任务调度
- 批量生成处理

详见 [OpenClaw/README.md](./OpenClaw/README.md)

---

## 💡 使用指南

### 基础使用：生成 PPT 图片

#### 1. 准备内容规划文件

创建 `my_slides_plan.json`：

```json
{
  "title": "AI 产品设计指南",
  "total_slides": 5,
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "标题：AI 产品设计指南\n副标题：构建以用户为中心的智能体验"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "核心原则\n- 简单直观\n- 快速响应\n- 透明可控"
    },
    {
      "slide_number": 3,
      "page_type": "content",
      "content": "设计流程\n1. 用户研究\n2. 原型设计\n3. 测试迭代"
    },
    {
      "slide_number": 4,
      "page_type": "data",
      "content": "用户满意度\n使用前：65%\n使用后：92%\n提升：+27%"
    },
    {
      "slide_number": 5,
      "page_type": "content",
      "content": "总结\n- 以用户为中心\n- 持续优化迭代\n- 数据驱动决策"
    }
  ]
}
```

#### 2. 生成 PPT 图片

```bash
python3 generate_ppt.py \
  --plan my_slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

#### 3. 查看结果

```bash
# 在浏览器中打开图片播放器
open outputs/TIMESTAMP/index.html
```

### 高级使用：生成带转场视频的 PPT

#### 1. 生成 PPT 图片

```bash
python3 generate_ppt.py \
  --plan my_slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

#### 2. 使用 Claude Code 生成转场提示词（必需）

在 Claude Code 中执行：

```
我刚生成了 5 页 PPT 图片在 outputs/TIMESTAMP/images 目录下。
请帮我分析这些图片，为每个页面转场生成视频提示词，
保存为 outputs/TIMESTAMP/transition_prompts.json
```

Claude Code 会：
1. 读取所有 PPT 图片
2. 分析每两页之间的视觉差异
3. 生成精准的转场描述
4. 保存为 JSON 文件

#### 3. 生成转场视频

```bash
python3 generate_ppt_video.py \
  --slides-dir outputs/TIMESTAMP/images \
  --output-dir outputs/TIMESTAMP_video \
  --prompts-file outputs/TIMESTAMP/transition_prompts.json
```

这会生成：
- 首页循环预览视频
- 每个页面间的转场视频
- 交互式视频播放器 HTML
- 完整视频 (full_ppt_video.mp4)

#### 4. 播放交互式视频 PPT

```bash
open outputs/TIMESTAMP_video/video_index.html
```

**播放逻辑**：
1. 首页：播放循环预览视频
2. 按右键：播放转场视频 → 显示目标页图片（停留 2 秒）
3. 再按右键：播放下一个转场视频 → 显示下一页图片
4. 依此类推...

#### 4. 导出完整视频（可选）

交互式播放器会自动生成完整视频：

```bash
# 视频文件
outputs/TIMESTAMP_video/full_ppt_video.mp4
```

完整视频包含：
- 首页预览（如果有）
- 转场视频 01→02
- 第 2 页静态（2 秒）
- 转场视频 02→03
- 第 3 页静态（2 秒）
- ...

---

## 🎬 视频功能

### 转场视频生成

使用可灵 AI 自动生成页面间的转场视频：

```bash
python3 generate_ppt_video.py \
  --slides-dir outputs/20260111_160221/images \
  --output-dir outputs/20260111_video \
  --mode professional \
  --duration 5
```

**参数说明**：
- `--slides-dir`: PPT 图片目录
- `--output-dir`: 输出目录
- `--mode`: 转场模式（`professional` 或 `creative`）
- `--duration`: 转场视频时长（秒，默认 5）

### 交互式播放器

生成的 `video_index.html` 支持：

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 下一页 | `→` `↓` | 播放转场视频，然后显示下一页 |
| 上一页 | `←` `↑` | 返回上一页（直接显示） |
| 首页 | `Home` | 返回首页预览 |
| 末页 | `End` | 跳到最后一页 |
| 播放/暂停 | `空格` | 暂停/继续当前视频 |
| 全屏 | `ESC` | 切换全屏模式 |
| 隐藏控件 | `H` | 隐藏/显示控制提示 |

### 完整视频合成

使用 FFmpeg 自动合成完整视频：

```python
from video_composer import VideoComposer

composer = VideoComposer()
composer.compose_full_ppt_video(
    slides_paths=[...],
    transitions_dict={...},
    output_path='output.mp4',
    slide_duration=2,  # 每页停留 2 秒
    include_preview=True,
    preview_video_path='preview.mp4',
    resolution='1920x1080',
    fps=24
)
```

**特性**：
- 自动统一所有视频的分辨率和帧率
- 保持宽高比，添加黑边
- 支持预览视频循环
- 高质量 H.264 编码

---

## 🎨 风格库

### 已内置风格

#### 1. 渐变毛玻璃卡片风格 (`gradient-glass.md`)

**视觉特点**：
- Apple Keynote 极简主义
- 玻璃拟态效果
- 霓虹紫/电光蓝/珊瑚橙渐变
- 3D 玻璃物体 + 电影级光照

**适用场景**：
- 🚀 科技产品发布
- 💼 商务演示
- 📊 数据报告
- 🏢 企业品牌展示

#### 2. 矢量插画风格 (`vector-illustration.md`)

**视觉特点**：
- 扁平化矢量设计
- 统一黑色轮廓线
- 复古柔和配色
- 几何化简化

**适用场景**：
- 📚 教育培训
- 🎨 创意提案
- 👶 儿童相关
- 💖 温暖品牌故事

### 添加自定义风格

1. 在 `styles/` 目录创建新的 `.md` 文件
2. 按照模板编写风格定义（参考现有风格）
3. 直接使用新风格生成 PPT

---

## 📚 项目结构

```
ppt-generator/
├── README.md                      # 本文件
├── API_MANAGEMENT.md              # API 密钥管理指南
├── ENV_SETUP.md                   # 环境变量配置指南
├── SECURITY.md                    # 安全最佳实践
├── .env.example                   # 环境变量模板
├── .env                          # 实际环境变量（不提交到 Git）
├── .gitignore                    # Git 忽略规则
│
├── generate_ppt.py               # PPT 图片生成脚本
├── generate_ppt_video.py         # 视频生成主脚本
├── kling_api.py                  # 可灵 AI API 封装
├── video_composer.py             # FFmpeg 视频合成
├── video_materials.py            # 视频素材管理
├── transition_prompt_generator.py # 转场提示词生成器
│
├── styles/                       # 风格库
│   ├── gradient-glass.md         # 渐变毛玻璃卡片风格
│   └── vector-illustration.md    # 矢量插画风格
│
├── templates/                    # HTML 模板
│   ├── viewer.html              # 图片播放器
│   └── video_viewer.html        # 视频播放器
│
├── prompts/                      # 提示词模板
│   └── transition_base.md       # 转场提示词基础模板
│
└── outputs/                      # 生成结果（自动创建）
    ├── TIMESTAMP/               # 图片版本
    │   ├── images/             # PPT 图片
    │   ├── index.html          # 图片播放器
    │   └── prompts.json        # 生成提示词记录
    └── TIMESTAMP_video/         # 视频版本
        ├── videos/             # 转场视频
        ├── video_index.html    # 视频播放器
        └── full_ppt_video.mp4  # 完整视频
```

---

## 🔧 配置选项

### 分辨率选择

| 分辨率 | 尺寸 | 文件大小 | 生成速度 | 推荐场景 |
|--------|------|----------|----------|----------|
| 2K | 2752x1536 | ~2.5MB/页 | ~30秒/页 | 日常演示、在线分享 ✅ |
| 4K | 5504x3072 | ~8MB/页 | ~60秒/页 | 打印输出、大屏展示 |

### 视频参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 分辨率 | 1920x1080 | 统一为 1080p，兼容可灵视频 |
| 帧率 | 24fps | 统一帧率，确保流畅拼接 |
| 静态图片时长 | 2秒 | 每页停留时间 |
| 转场视频时长 | 5秒 | 可灵生成的转场时长 |

### 页数建议

| 页数范围 | 演讲时长 | 适用场景 |
|----------|----------|----------|
| 5 页 | 5 分钟 | 电梯演讲、快速介绍 |
| 5-10 页 | 10-15 分钟 | 标准演示、产品介绍 |
| 10-15 页 | 20-30 分钟 | 深入讲解、培训课程 |
| 20-25 页 | 45-60 分钟 | 完整培训、研讨会 |

---

## ❓ 常见问题

### Q: 如何获取 API 密钥？

**A**:
- **RunningHub API**: 访问 RunningHub 平台获取 API 密钥（用于生成 PPT 图片）
- **可灵 AI API**: 访问 [可灵 AI 开放平台](https://klingai.com)，注册并创建应用获取密钥（可选，用于视频转场）

### Q: 是否必须配置可灵 AI 密钥？

**A**: 不是必须的。
- **只生成 PPT 图片**：只需要 RH_API_KEY
- **生成转场视频**：需要 KLING_ACCESS_KEY 和 KLING_SECRET_KEY

### Q: 视频合成失败怎么办？

**A**: 检查以下几点：
1. FFmpeg 是否已安装（`ffmpeg -version`）
2. 视频文件是否存在且完整
3. 磁盘空间是否充足
4. 查看详细错误信息

### Q: 如何修改静态图片展示时间？

**A**: 在 `video_composer.py` 中修改 `slide_duration` 参数（默认 2 秒）

### Q: 转场视频生成很慢怎么办？

**A**: 可灵 AI 生成视频需要一定时间（通常 30-60 秒/段）。可以：
- 减少转场数量
- 使用较短的转场时长
- 分批生成

### Q: 可以导出为 PDF 吗？

**A**: 可以。
1. 在浏览器中打开 `index.html`
2. 按 `Cmd+P` (Mac) 或 `Ctrl+P` (Windows)
3. 选择"另存为 PDF"

### Q: 生成的内容可以商用吗？

**A**: 请查阅相关服务条款：
- RunningHub 使用条款
- [可灵 AI 使用条款](https://klingai.com/terms)

一般情况下，你拥有生成内容的使用权。

---

## 🛡️ 安全说明

### API 密钥安全

本项目采用 `.env` 文件管理 API 密钥，确保安全：

- ✅ `.env` 文件已在 `.gitignore` 中，不会提交到 Git
- ✅ 代码中无硬编码密钥
- ✅ 支持系统环境变量作为备用方案
- ✅ `.env.example` 提供配置模板

**最佳实践**：

```bash
# ✅ 正确：使用 .env 文件
cp .env.example .env
# 编辑 .env 填入真实密钥

# ❌ 错误：直接在代码中写密钥
RH_API_KEY = "your-api-key" # 永远不要这样做！
```

### 提交前检查

```bash
# 验证没有密钥泄露
grep -r "RH_API_KEY\|KLING_" --exclude-dir=.git --exclude-dir=venv .
# 应该无输出（除了 .env.example）

# 检查 .env 文件是否被排除
git status
# 确认 .env 不在待提交列表中
```

详细说明请查看：
- **API_MANAGEMENT.md** - API 密钥管理完整指南
- **ENV_SETUP.md** - 环境变量配置指南
- **SECURITY.md** - 安全最佳实践

---

## 📝 更新日志

### v2.1.0 (2026-04-03)

- 🔄 **API 迁移**
  - 从 Gemini 直连迁移到 RunningHub API
  - 支持 V2（快速）和 PRO（高质量）模型切换
  - 添加 `--model` 和 `--draft` 参数
- 🎬 **视频提供者扩展**
  - 新增 video_providers 模块
  - 支持 Seedance 2.0
  - 支持 LTX-2.3（占位）
- 🎯 **平台适配**
  - OpenCode 平台适配文件
  - OpenClaw 平台适配文件
  - 更新 README.md 添加平台选择引导
- 📚 **文档更新**
  - 更新 API 密钥配置说明
  - 添加平台使用说明
  - 移除过时的 Gemini 相关内容

### v2.0.0 (2026-01-11)

- 🎬 **新增视频功能**
  - 可灵 AI 转场视频生成
  - 交互式视频播放器（视频+图片混合）
  - FFmpeg 完整视频合成
  - 首页循环预览视频
- 🔧 **优化视频合成**
  - 自动统一分辨率和帧率
  - 修复视频拼接兼容性问题
  - 静态图片展示时间改为 2 秒
- 🐛 **Bug 修复**
  - 修复预览模式状态管理问题
  - 修复 FFmpeg 滤镜参数格式错误
- 📚 **文档更新**
  - 全面改写 README
  - 新增视频功能使用指南
  - 更新 API 密钥配置说明

### v1.0.0 (2026-01-09)

- ✨ 首次发布
- 🎨 内置 2 种专业风格
- 🖼️ 支持 2K/4K 分辨率
- 🎬 HTML5 图片播放器
- 📊 智能文档分析
- 🔐 安全的环境变量管理

---

## 🤝 贡献指南

欢迎贡献！你可以：

### 添加新风格

1. Fork 本项目
2. 在 `styles/` 创建新风格文件
3. 参考现有风格编写提示词
4. 测试生成效果
5. 提交 Pull Request

### 报告问题

在 [GitHub Issues](https://github.com/op7418/NanoBanana-PPT-Skills/issues) 提交问题，请包含：
- 错误信息
- 操作步骤
- 系统环境
- 日志文件（如有）

---

## 📄 许可证

MIT License

Copyright (c) 2026 歸藏

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 致谢

- **RunningHub 平台** - 提供稳定的 API 中转服务
- **可灵 AI 团队** - 提供高质量的视频生成服务
- **FFmpeg 项目** - 提供强大的视频处理工具
- **开源社区** - 提供的各种工具和灵感
- **原作者 歸藏** - 提供原始项目基础

---

## 📞 联系方式

- **原作者**: 歸藏 ([@op7418](https://github.com/op7418))
- **重构维护**: AIRix315
- **Issues**: [GitHub Issues](https://github.com/AIRix315/RH-PPT-Skills/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Powered by RunningHub API & 可灵 AI & FFmpeg

</div>
