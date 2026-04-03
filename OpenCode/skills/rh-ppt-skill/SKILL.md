---
name: rh-ppt-skill
description: PPT 图片生成技能 - 支持 RunningHub API 和多模型切换
---

# RH-PPT-Skill

## 功能

生成高质量 PPT 图片，支持：
- V2（草稿快速）和 PRO（高质量）双模式
- 多种视频提供者（可灵、Seedance、LTX）
- 自定义风格模板

## 环境要求

- Python 3.8+
- RH_API_KEY（RunningHub API 密钥）
- 可选：KLING_ACCESS_KEY, KLING_SECRET_KEY

## 使用方法

### 基本用法

```bash
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md
```

### 草稿模式

```bash
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --draft
```

### 选择模型

```bash
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model pro
python generate_ppt.py --plan slides.json --style styles/gradient-glass.md --model v2
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --plan | PPT 计划文件（JSON） | 必需 |
| --style | 风格模板文件 | 必需 |
| --draft | 草稿模式（快速生成） | False |
| --model | 模型选择（v2, pro） | v2 |
| --output | 输出目录 | output/ |

## 故障排查

### API 错误

检查 RH_API_KEY 是否正确配置：
```bash
export RH_API_KEY="your-api-key"
```

### 图片生成失败

检查模型是否支持：
- v2：快速生成，适合草稿
- pro：高质量生成，适合最终版本

## 更多信息

详见项目根目录 README.md