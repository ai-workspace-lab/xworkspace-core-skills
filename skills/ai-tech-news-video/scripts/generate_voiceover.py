#!/usr/bin/env python3
"""Generate all voiceover audio for AI Tech News Flash video using edge-tts."""

import asyncio
import subprocess
import sys
import os

VOICE = "zh-CN-YunxiNeural"
RATE = "+30%"  # Fast pace for news flash style
OUTPUT_DIR = "assets/audio"

# Script template - edit these for each episode
# Rule: NO "第X条", NO time filler words, just content directly
SCRIPTS = {
    "intro": "AI快报，{date}，最热资讯。",
    "card1": "{headline1}。{desc1}",
    "card2": "{headline2}。{desc2}",
    "card3": "{headline3}。{desc3}",
    "card4": "{headline4}。{desc4}",
    "card5": "{headline5}。{desc5}",
    "outro": "以上就是本期 AI 快报。关注拓扑同学，下期见。",
}

async def generate_audio(text, output_path, voice=VOICE, rate=RATE):
    """Generate a single audio file with edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)
    print(f"  Generated: {output_path}")

def get_duration(filepath):
    """Get audio duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", filepath],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # TODO: Replace with actual episode content
    date = "2026年5月7日"
    headlines = {
        "1": ("Anthropic 让 Claude 学会了做梦", "Claude 可在会话间隙回顾历史记录，发现自身错误模式并自我改进"),
        "2": ("xAI 并入 SpaceX 改名 SpaceXAI", "Elon Musk 宣布 xAI 不再独立，同时与 Anthropic 达成算力合作"),
        "3": ("OpenAI 联合 AMD 和 NVIDIA 发布 MRC 协议", "提升大规模 AI 训练集群的 GPU 网络性能与弹性"),
        "4": ("Musk 诉 Altman 庭审关键证人阶段", "Zilis 出庭作证，邮件曝光 Musk 曾计划将 OpenAI 纳入 Tesla"),
        "5": ("43% 美国人认为数据中心推高了电费", "Pew Research 调查显示数据中心能耗已成两党共识议题"),
    }

    # Generate all audio files
    tasks = []

    intro_text = SCRIPTS["intro"].format(date=date)
    tasks.append(generate_audio(intro_text, f"{OUTPUT_DIR}/intro.mp3"))

    for i, (headline, desc) in headlines.items():
        card_text = SCRIPTS[f"card{i}"].format(**{f"headline{i}": headline, f"desc{i}": desc})
        tasks.append(generate_audio(card_text, f"{OUTPUT_DIR}/card{i}.mp3"))

    tasks.append(generate_audio(SCRIPTS["outro"], f"{OUTPUT_DIR}/outro.mp3"))

    await asyncio.gather(*tasks)

    # Print durations for timing reference
    print("\n📊 Audio durations (for HyperFrames timing):")
    total = 0
    for name in ["intro", "card1", "card2", "card3", "card4", "card5", "outro"]:
        path = f"{OUTPUT_DIR}/{name}.mp3"
        if os.path.exists(path):
            dur = get_duration(path)
            total += dur
            print(f"  {name}: {dur:.1f}s")
    print(f"  TOTAL: {total:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
