---
name: ai-ti-wo-shuo-explainer
description: Use when making a 30s+ 9:16 white-background「AI替我说」knowledge-animation explainer (technical mechanism / popular-science principle) from a product page screenshot or pure drawn animation, with TTS narration, subtitles and an avatar badge.
---
# AI替我说 · 动画科普短视频

核心：「看看知识怎么变成动画」——讲技术机制和科普原理，不做产品页展示。

## 规则
- 30s 以上，9:16，白底；组件用对应软件 logo；讲解人用底部头像徽章（无 AI 仿脸）。有自录口型视频时放进旁白槽位，否则头像随配音轻微脉动。
- 画面不放 URL、二维码、价格；不发布，除非用户明确要求。
- 平台敏感词避开（如 出海、专线、加速、VPN、具体地域）。

## 步骤
1. 写 30–40s 脚本（4–6 个镜头），每镜头一句旁白。
2. 写 shots.json：每个镜头 `"use":"anim"`（anim.py 绘制）或 Grok 图生视频（make_refs.py 生成 9:16 参考图与 GenerateVideo 参数；密集 UI 用静图慢推兜底）。
3. 动画镜头用 anim.py 原语（ease/seg/box/arrow/flow/badge/pulse/cloud/monitor/chat bubble/typing/render）在 scenes.py 里实现。
4. compose.sh：edge-tts（YunxiNeural，rate +20–32%）配音 + 字幕 + 头像徽章 + 轻音乐合成成片，可用 cover_ref 指定封面。
5. 抽帧自检后交付；另写 XHS 文案 300–500 字。

详见 README.md。
