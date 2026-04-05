# 更新日志

所有重要的变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/)。

---

## [2.2.0] - 2026-04-05

### 新增

- 新增 v3.1-fast 视频模型支持（低价渠道版，~￥0.5/段）
- 确立推荐配置：v3.1-fast 视频模型 + 4K 图片分辨率
- 添加 Agent 默认行为约束，防止自主选择高价模型
- SKILL.md 添加显眼的推荐配置表格

### 变更

- 删除独立 Kling API (`kling_api.py`)，统一使用 RunningHub API
- 删除 `KLING_ACCESS_KEY` / `KLING_SECRET_KEY` 配置项
- 移除 PyJWT 依赖
- 默认视频模型从 `x-low` 改为 `v3.1-fast`
- 精简 README.md，移除冗余内容
- 修正 SKILL.md 版本号不一致问题

### 移除

- `scripts/kling_api.py` - 独立 Kling API 封装
- `tests/test_kling_transition.py` - 测试文件
- `references/REFACTOR_PLAN.md` - 内部重构文档
- `references/ANTIGRAVITY_WORKFLOW.md` - 内部工作流文档
- `references/installation.md` - 与 README 重复

---

## [2.1.0] - 2026-04-03

### 新增

- 平台迁移：从 Gemini/可灵 迁移到 RunningHub
- 支持多种视频模型选择
- 重构 SKILL.md 针对 Agent 执行优化

### 变更

- 使用 RunningHub API 统一调用

---

## [2.0.0] - 2026-03-xx

### 新增

- 视频功能：智能转场视频生成
- FFmpeg 合成完整视频
- 交互式播放器

---

## [1.0.0] - 2026-02-xx

### 新增

- 初始版本
- PPT 图片生成功能
- 多风格支持