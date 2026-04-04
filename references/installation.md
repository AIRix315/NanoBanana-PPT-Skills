# RH-PPT-Skills 安装指南

## 快速开始

### 1. Conda 环境已创建 ✅

环境名称: `rh-ppt-skills`
Python 版本: 3.10

### 2. 激活环境

**Windows (PowerShell):**
```powershell
conda activate rh-ppt-skills
```

**Windows (CMD):**
```cmd
conda activate rh-ppt-skills
```

**Linux/Mac:**
```bash
conda activate rh-ppt-skills
```

### 3. 配置环境变量

编辑项目根目录的 `.env` 文件：

```bash
# 填入您的 RunningHub API 密钥
RH_API_KEY=your-runninghub-api-key-here

# 可选：可灵 AI 密钥（用于视频功能）
KLING_ACCESS_KEY=your-kling-access-key-here
KLING_SECRET_KEY=your-kling-secret-key-here
```

### 4. 验证安装

```bash
# 激活环境后运行
python test_environment.py
```

### 5. 测试技能

```bash
# 快速测试（草稿模式）
python scripts/generate_ppt.py --help

# 完整测试（需要 API 密钥）
python scripts/generate_ppt.py --plan test/slides.json --style assets/styles/gradient-glass.md --draft
```

## 文件清单

| 文件 | 说明 |
|------|------|
| `environment.yml` | Conda 环境配置（已创建） |
| `requirements.txt` | Pip 依赖列表（已创建） |
| `.env` | 环境变量（需配置） |
| `test_environment.py` | 环境验证脚本（已创建） |

## 目录结构

```
RH-PPT-Skills/
├── .opencode → OpenCode/        # OpenCode 技能软链接 ✅
├── OpenCode/
│   ├── README.md                # OpenCode 安装指南
│   └── skills/
│       └── rh-ppt-skill/
│           └── SKILL.md         # 技能定义 ✅
├── environment.yml              # Conda 配置 ✅
├── requirements.txt             # Pip 依赖 ✅
├── .env                         # 环境变量（需配置）
└── test_environment.py          # 验证脚本 ✅
```

## OpenCode 使用方法

### 方法 1: 自动识别

启动 OpenCode 后，技能会自动识别：

```
> 有哪些可用的技能？
```

### 方法 2: 显式调用

```
> 使用 rh-ppt-skill 生成一个 5 页的 PPT
```

## 常见问题

### Q: Conda 环境激活失败？

```bash
# 初始化 conda（首次使用）
conda init bash  # Linux/Mac
conda init powershell  # Windows PowerShell
conda init cmd.exe  # Windows CMD

# 重启终端后激活
conda activate rh-ppt-skills
```

### Q: .env 文件在哪里？

```
项目根目录: E:\Projects\RH-PPT-Skills\.env
```

### Q: 如何确认技能已加载？

运行验证脚本：
```bash
python test_environment.py
```

## 下一步

1. ✅ Conda 环境已创建
2. ✅ 依赖已安装
3. ⏳ 配置 `.env` 文件中的 `RH_API_KEY`
4. ⏳ 激活环境: `conda activate rh-ppt-skills`
5. ⏳ 运行验证: `python test_environment.py`