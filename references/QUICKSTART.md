# RH-PPT-Skills 快速上手

## 🚀 5分钟开始

### 第一步：获取 RunningHub API Key

1. 访问 https://www.runninghub.cn
2. 注册并登录
3. 获取 API Key

### 第二步：配置环境

```bash
# 克隆项目
git clone https://github.com/AIRix315/RH-PPT-Skills.git
cd RH-PPT-Skills

# 创建 .env 文件
cp .env.example .env

# 编辑 .env，填入你的 Key
# RH_API_KEY=your-api-key-here
```

### 第三步：在 OpenCode/OpenClaw 中使用

直接对 Agent 说：

> "帮我生成一个关于《AI产品设计原则》的 5 页 PPT，使用渐变毛玻璃风格，需要生成动态视频"

Agent 会自动：
1. 规划内容
2. 生成图片
3. 生成转场视频
4. 合成完整演示视频

### 第四步：查看结果

```bash
# 打开图片播放器（替换时间戳）
open outputs/YYYYMMDD_HHMMSS/index.html

# 打开视频播放器（如果生成了视频）
open outputs/YYYYMMDD_HHMMSS_video/video_index.html
```

**注意：** 输出目录自动使用时间戳命名，如 `outputs/20260404_221500/`

---

## 💰 成本预估

| 内容 | 成本 | 时间 |
|------|------|------|
| 5页 PPT（仅图片） | ~¥0.5 | ~2分钟 |
| 5页 PPT（含视频） | ~¥1.5 | ~8分钟 |
| 10页 PPT（含视频） | ~¥3 | ~15分钟 |

---

## 🎨 可用风格

| 风格 | 文件 | 适用场景 |
|------|------|----------|
| 渐变毛玻璃 | `assets/styles/gradient-glass.md` | 科技、商务、数据报告 |
| 矢量插画 | `assets/styles/vector-illustration.md` | 教育、培训、品牌故事 |

---

## ⚠️ 常见问题

### Q: 提示 "RH_API_KEY 未配置"？

A: 确保创建 `.env` 文件并填入 Key：
```bash
RH_API_KEY=your-api-key-here
```

### Q: 视频生成失败？

A: 检查：
1. FFmpeg 是否安装（`ffmpeg -version`）
2. 账户余额是否充足（登录 RunningHub 查看余额）
3. API Key 是否有效

### Q: 如何安装 FFmpeg？

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# 下载 https://ffmpeg.org/download.html 并添加到 PATH
```

### Q: 生成时间太长？

A: 正常情况下：
- 图片：30秒/页
- 视频：90秒/段转场

如果超过 2 倍时间，检查网络和 API 状态。

---

## 📞 获取帮助

- 详细文档：`SKILL.md`
- API 说明：`API_MANAGEMENT.md`
- 架构说明：`ARCHITECTURE.md`

---

**就这么简单！一个 Key，完成所有功能。** 🎉