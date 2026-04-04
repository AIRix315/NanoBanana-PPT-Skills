# RH-PPT-Skill for OpenClaw

## 平台说明

OpenClaw 是一个生产调度平台，用于 Skills 的生产部署和使用。

## Skills 加载路径

OpenClaw 的 Skills 搜索优先级：
1. `skills/`
2. `.agents/skills/`
3. `~/.openclaw/skills/`

本项目使用软链接：
```
skills → OpenClaw/skills/
```

因此 OpenClaw 会自动发现 `OpenClaw/skills/` 下的技能。

## 生产使用流程

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

### 3. 定时任务配置

建议使用 cron 或调度系统定期生成 PPT：

```bash
# crontab 示例
0 9 * * * cd /path/to/RH-PPT-Skills && python scripts/generate_ppt.py --plan daily/slides.json --style assets/styles/gradient-glass.md --model pro
```

## 生产部署配置

### 环境变量

```bash
# .env 文件
RH_API_KEY=your-runninghub-api-key
KLING_ACCESS_KEY=your-kling-access-key
KLING_SECRET_KEY=your-kling-secret-key
```

### 模型选择

| 模型 | 用途 | 特点 |
|------|------|------|
| v2 | 快速生成 | 适合草稿、预览 |
| pro | 高质量 | 适合最终版本 |

### 风格模板

内置风格模板：
- `assets/styles/gradient-glass.md` - 渐变毛玻璃风格
- `assets/styles/vector-illustration.md` - 矢量插画风格

自定义风格模板：参考现有模板格式，创建新的 `.md` 文件。

## 监控与日志

### 日志文件

- 位置：`output/generation.log`
- 内容：API 调用记录、错误信息

### 监控建议

1. 定期检查 API 配额使用情况
2. 监控图片生成成功率
3. 日志轮转避免磁盘占用

## 性能优化

### 批量生成

使用脚本批量生成多个 PPT：
```bash
for plan in plans/*.json; do
  python scripts/generate_ppt.py --plan "$plan" --style assets/styles/gradient-glass.md --model pro
done
```

### 并发生成

使用 GNU Parallel 或 xargs 并发生成：
```bash
find plans/*.json | parallel -j 4 python scripts/generate_ppt.py --plan {} --style assets/styles/gradient-glass.md --model pro
```

## 常见问题

### Q: Skills 未被 OpenClaw 发现？

A: 检查软链接是否正确创建：
```bash
# Windows
dir skills

# Linux/Mac
ls -la skills
```

如果软链接不存在，手动创建：
```bash
# Windows
mklink /D skills OpenClaw\skills

# Linux/Mac
ln -s OpenClaw/skills skills
```

### Q: API 配额耗尽？

A: 监控 API 使用情况，优化模型选择：
- 草稿阶段使用 v2 模型
- 最终版本使用 pro 模型

### Q: 生成速度慢？

A: 考虑并发生成或升级 API 套餐。

## 更多信息

详见项目根目录 [README.md](../README.md)