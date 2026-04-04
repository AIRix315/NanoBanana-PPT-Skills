# RH-PPT-Skill for OpenCode

## 平台说明

OpenCode 是一个开发调试平台，用于 Skills 的开发和测试。

## Skills 加载路径

OpenCode 的 Skills 搜索优先级：
1. `.opencode/skills/`
2. `.claude/skills/`
3. `.agents/skills/`

本项目使用软链接：
```
.opencode → OpenCode/
```

因此 OpenCode 会自动发现 `OpenCode/skills/` 下的技能。

## 开发调试流程

### 1. 环境配置

```bash
# 克隆仓库
git clone https://github.com/AIRix315/RH-PPT-Skills.git
cd RH-PPT-Skills

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 RH_API_KEY
```

### 2. 安装依赖

```bash
pip install requests pillow python-dotenv
```

### 3. 测试运行

```bash
# 基本测试
python scripts/generate_ppt.py --plan test/slides.json --style assets/styles/gradient-glass.md --draft

# 完整测试
python scripts/generate_ppt.py --plan test/slides.json --style assets/styles/gradient-glass.md --model pro
```

### 4. 验证输出

检查 `output/` 目录：
- 图片文件：slide-01.png, slide-02.png, ...
- 日志文件：generation.log

## 测试验证

### 快速验证

```bash
# 使用草稿模式快速验证
python scripts/generate_ppt.py --plan test/slides.json --style assets/styles/gradient-glass.md --draft --model v2
```

### 完整验证

```bash
# 使用 PRO 模型完整验证
python scripts/generate_ppt.py --plan test/slides.json --style assets/styles/gradient-glass.md --model pro
```

## 常见问题

### Q: Skills 未被 OpenCode 发现？

A: 检查软链接是否正确创建：
```bash
# Windows
dir .opencode

# Linux/Mac
ls -la .opencode
```

如果软链接不存在，手动创建：
```bash
# Windows
mklink /D .opencode OpenCode

# Linux/Mac
ln -s OpenCode .opencode
```

### Q: API 调用失败？

A: 检查 .env 文件中的 RH_API_KEY 是否正确配置。

### Q: 图片生成失败？

A: 检查网络连接和 API 配额。

## 更多信息

详见项目根目录 [README.md](../README.md)