#!/usr/bin/env python3
"""用法: python make_refs.py <episode_dir>
读取 shots.json: 先在整图上遮盖 masks，再按 crop 裁图，居中放到 9:16 白底(1080x1920)，
输出 refs/shot-XX.png (GenerateVideo 的 image_path) 和 refs/masked-source.png，并写入 grok_call 参数。"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFilter
d = sys.argv[1]; cfg = json.load(open(f"{d}/shots.json"))
src = Image.open(f"{d}/{cfg['source']}").convert("RGB")
for m in cfg["masks"]:
    b = tuple(m["box"])
    if m.get("mode") == "blur":
        src.paste(src.crop(b).filter(ImageFilter.GaussianBlur(12)), b[:2])
    else:  # cover: 用框左侧像素色填充，看起来像空白
        ImageDraw.Draw(src).rectangle(b, fill=src.getpixel((max(b[0]-3, 0), b[1]+2)))
os.makedirs(f"{d}/refs", exist_ok=True); src.save(f"{d}/refs/masked-source.png")
W, H = 1080, 1920; g = cfg["grok_defaults"]
for s in cfg["shots"]:
    # 安全区: 顶部标题条 110-200，字幕从 1390 起 → 内容放在 y 280-1320、左右各留 60px
    MAXW, MAXH, CY = cfg.get("content_maxw", 960), cfg.get("content_maxh", 1000), cfg.get("content_cy", 800)
    if s.get("ref_from"):  # 预先设计好的画面(卡片/流程/徽章)，直接用
        boxes = []; parts = [Image.open(f"{d}/{s['ref_from']}").convert("RGB")]
    else:
        boxes = s["crop"] if isinstance(s["crop"][0], list) else [s["crop"]]  # 支持多块纵向堆叠
        parts = [src.crop(tuple(b)) for b in boxes]
    n = len(parts); fit = []
    for c in parts:
        cw = MAXW; ch = int(c.height * cw / c.width)
        if ch > MAXH // n: ch = MAXH // n; cw = int(c.width * ch / c.height)
        fit.append(c.resize((cw, ch), Image.LANCZOS))
    tot = sum(x.height for x in fit) + 40 * (n - 1)
    can = Image.new("RGB", (W, H), "white"); y = CY - tot // 2
    for x in fit: can.paste(x, ((W - x.width) // 2, y)); y += x.height + 40
    if s.get("caption"):  # 例如“图中数值为演示数据”
        from PIL import ImageFont
        ImageDraw.Draw(can).text((W // 2, y + 10), s["caption"], font=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 34), fill=(107, 114, 128), anchor="mt")
    p = f"{d}/refs/shot-{s['id']:02d}.png"; can.save(p)
    s["ref"] = os.path.abspath(p)
    if "grok_prompt" in s: s["grok_call"] = {"image_path": os.path.abspath(p), "prompt": s["grok_prompt"] + " " + g["prompt_suffix"],
                      "duration": max(s["duration"], 3), "aspect_ratio": g["aspect_ratio"],
                      "resolution": g["resolution"], "filename": f"{cfg.get('slug','ep')}-shot-{s['id']:02d}.mp4"}
json.dump(cfg, open(f"{d}/shots.json", "w"), ensure_ascii=False, indent=2)
print("refs ok:", len(cfg["shots"]))
