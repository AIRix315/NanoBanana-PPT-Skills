# RH-PPT-Skills

> 从文档到动态视频演示，一站式 PPT 生成工具 | RunningHub API

<div align="center">

![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

**一个 Key，完成所有功能** | [快速开始](#-快速开始) | [详细文档](./references/QUICKSTART.md)

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
brew install ffmpeg  # macOS | sudo apt install ffmpeg  # Linux
```

### 第三步：使用

**在 OpenCode/OpenClaw 中直接说：**

> "帮我生成一个关于《AI产品设计原则》的 5 页 PPT，使用渐变毛玻璃风格，需要动态视频"

**或命令行：**

```bash
# 生成 PPT 图片（默认 4K）
python scripts/generate_ppt.py --plan slides.json --style assets/styles/gradient-glass.md

# 生成动态视频（可选）
python scripts/generate_ppt_video.py \
  --slides-dir outputs/YYYYMMDD_HHMMSS/images \
  --output-dir outputs/YYYYMMDD_HHMMSS_video \
  --prompts-file outputs/YYYYMMDD_HHMMSS/transition_prompts.json
```

---

## 💰 成本预估

| 配置 | 5页 PPT | 10页 PPT |
|------|---------|----------|
| **推荐配置** (v3.1-fast + 4K) | ~¥3.5 | ~¥6 |
| 高质量配置 (v3.1-pro + 4K) | ~¥7 | ~¥12 |
| 仅图片（不生成视频） | ~¥1.5 | ~¥3 |

> 默认使用 v3.1-fast（~¥0.5/段），Agent 不会自主选择高价模型

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](./SKILL.md) | Agent 执行指南 |
| [快速开始](./references/QUICKSTART.md) | 详细使用教程 |
| [架构说明](./references/ARCHITECTURE.md) | 技术架构 |
| [API 管理](./references/API_MANAGEMENT.md) | API 配置 |

---

## 📂 项目结构

```
RH-PPT-Skills/
├── SKILL.md              # Agent 执行指南
├── scripts/              # 核心脚本
│   ├── generate_ppt.py       # PPT 图片生成
│   └── generate_ppt_video.py # 视频生成
├── assets/
│   ├── styles/           # 视觉风格
│   └── templates/        # HTML 播放器模板
└── references/           # 详细文档
```

---

## 📝 更新日志

见 [CHANGELOG.md](./CHANGELOG.md)

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)