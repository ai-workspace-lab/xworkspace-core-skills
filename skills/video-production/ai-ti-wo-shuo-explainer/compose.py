#!/usr/bin/env python3
"""用法: compose.sh <episode_dir>   依赖 v2/.venv (edge-tts, numpy, pillow) + ffmpeg
步骤: TTS 分句配音 -> 按配音时长定镜头时长 -> Grok 片段(或静帧推拉兜底)统一到 1080x1920 ->
拼接 -> 叠加顶部标题/字幕/底部真实头像徽章(随音量脉动) -> 混入轻音乐 -> 导出 mp4 + voice.mp3 + cover.png"""
import json, sys, os, subprocess, asyncio, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.abspath(sys.argv[1]); cfg = json.load(open(f"{D}/shots.json"))
B = f"{D}/build"; os.makedirs(B, exist_ok=True)
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
def sh(*a): subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(f): return float(subprocess.check_output(["ffprobe","-v","0","-show_entries","format=duration","-of","csv=p=0",f]))
shots = cfg["shots"]
# 1. TTS
async def tts():
    import edge_tts
    for s in shots:
        await edge_tts.Communicate(s["vo"], cfg.get("voice","zh-CN-YunxiNeural"), rate=cfg.get("rate","+0%")).save(f"{B}/vo{s['id']:02d}.mp3")
asyncio.run(tts())
LEAD, GAP = 0.15, 0.2
# 去掉 TTS 首尾静音，节奏更紧
for s in shots:
    p=f"{B}/vo{s['id']:02d}.mp3"; sh("ffmpeg","-y","-i",p,"-af","silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",p.replace(".mp3",".t.wav")); os.replace(p.replace(".mp3",".t.wav"),p.replace(".mp3",".wav"))
t = 0.0
for s in shots:
    s["vo_len"] = dur(f"{B}/vo{s['id']:02d}.wav")
    s["len"] = round(max(s["duration"], s["vo_len"] + LEAD + GAP), 2); s["t0"] = t; t += s["len"]
TOTAL = t + 0.6  # 结尾留白
# 2. 每个镜头 -> 1080x1920 片段
for s in shots:
    o = f"{B}/s{s['id']:02d}.mp4"; L = s["len"]
    clip = f"{D}/{s.get('clip','')}"
    if s.get("use") == "anim":  # 动画科普模式: 本期目录 scenes.py 里的 scene 函数逐帧绘制
        import importlib.util; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import anim
        spec = importlib.util.spec_from_file_location("scenes", f"{D}/scenes.py"); sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
        os.makedirs(f"{D}/refs", exist_ok=True); s["ref"] = f"{D}/refs/shot-{s['id']:02d}.png"
        anim.render(getattr(sc, s["scene"]), L, o, still=s["ref"])
    elif s.get("use") == "grok" and os.path.exists(clip):
        cl = dur(clip); k = min(max(L / cl, 1.0), 1.5)  # 最多放慢 1.5x，再不够就定格末帧
        vf = f"setpts={k}*PTS,fps={FPS},scale={W}:{H}:flags=lanczos,tpad=stop_mode=clone:stop_duration={L}"
        sh("ffmpeg","-y","-i",clip,"-vf",vf,"-t",str(L),"-an","-c:v","libx264","-pix_fmt","yuv420p","-crf","18",o)
    else:  # 兜底: Ken Burns 静帧缓推
        n = int(L * FPS)
        vf = f"scale=2160:3840,zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS}"
        sh("ffmpeg","-y","-loop","1","-i",s["ref"],"-vf",vf,"-frames:v",str(n),"-c:v","libx264","-pix_fmt","yuv420p","-crf","18",o)
        s["use"] = "fallback"
open(f"{B}/list.txt","w").write("".join(f"file 's{s['id']:02d}.mp4'\n" for s in shots))
sh("ffmpeg","-y","-f","concat","-safe","0","-i",f"{B}/list.txt","-vf",f"tpad=stop_mode=clone:stop_duration=1","-t",str(TOTAL),"-c:v","libx264","-pix_fmt","yuv420p","-crf","18",f"{B}/base.mp4")
# 3. 配音轨 voice.mp3
inp, flt = [], []
for i, s in enumerate(shots):
    inp += ["-i", f"{B}/vo{s['id']:02d}.wav"]; ms = int((s["t0"] + LEAD) * 1000)
    flt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{i}]")
flt.append("".join(f"[a{i}]" for i in range(len(shots))) + f"amix=inputs={len(shots)}:normalize=0,apad=whole_dur={TOTAL}[v]")
sh("ffmpeg","-y",*inp,"-filter_complex",";".join(flt),"-map","[v]","-t",str(TOTAL),f"{B}/voice.wav")
sh("ffmpeg","-y","-i",f"{B}/voice.wav","-b:a","192k",f"{D}/voice.mp3")
# 4. 轻音乐: 柔和和弦铺底 (C-E-G-B)，淡入淡出
mdb = cfg.get("music_db", -30)
if cfg.get("music", "pad") != "none":
    ch = "+".join(f"0.25*sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.25*t))" for f in (130.81,164.81,196.0,246.94))
    sh("ffmpeg","-y","-f","lavfi","-i",f"aevalsrc='{ch}':s=48000:d={TOTAL}","-af",f"afade=in:d=1.5,afade=out:st={TOTAL-2}:d=2,volume={mdb}dB,aformat=channel_layouts=stereo",f"{B}/music.wav")
# 5. 叠加层: 每帧 PNG 不现实，改为: 字幕/标题静态 PNG + 头像脉动帧序列
with wave.open(f"{B}/voice.wav") as w:
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1) / 32768; sr = w.getframerate()
hop = sr // FPS; env = np.array([np.sqrt(np.mean(a[i:i+hop]**2)) for i in range(0, len(a), hop)])
env = np.convolve(env / (env.max() + 1e-9), np.ones(3)/3, "same")
F = lambda sz: ImageFont.truetype(FONT, sz)
def wrap(txt, font, maxw):
    # 英文单词不拆开；句读不放行首
    import re
    toks = re.findall(r"[A-Za-z0-9.+\-]+|\s|.", txt); lines, cur = [], ""
    for tk in toks:
        if cur and font.getlength(cur + tk) > maxw:
            if tk in "，。、；：？！,.;:?!）」" : cur += tk; continue
            lines.append(cur.rstrip()); cur = tk.lstrip()
        else: cur += tk
    return lines + [cur] if cur else lines
av = Image.open(cfg["avatar"]).convert("RGBA").resize((220, 220), Image.LANCZOS)
mk = Image.new("L", (220, 220), 0); ImageDraw.Draw(mk).ellipse((0, 0, 219, 219), fill=255); av.putalpha(mk)
fdir = f"{B}/ovl"; os.makedirs(fdir, exist_ok=True)
title = cfg["title"]; ft, fs = F(54), F(50)
nfr = int(TOTAL * FPS)
def static_layer(sub):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    tw = ft.getlength(title); d.rounded_rectangle(((W-tw)/2-36, 110, (W+tw)/2+36, 200), 45, fill=(17, 24, 39, 235))
    d.text((W/2, 155), title, font=ft, fill="white", anchor="mm")
    if sub:
        f, lh = fs, 72; ls = wrap(sub, f, 900); y0 = 1390
        if len(ls) > 2: f, lh = F(40), 58; ls = wrap(sub, f, 920)  # 长字幕缩字号，保证不压到头像
        box_h = len(ls) * lh + 30; d.rounded_rectangle((60, y0, W-60, y0+box_h), 26, fill=(255, 255, 255, 235), outline=(37, 99, 235, 255), width=3)
        for j, l in enumerate(ls): d.text((W/2, y0 + 15 + lh//2 + j*lh), l, font=f, fill=(17, 24, 39), anchor="mm")
    return im
cache = {}
for i in range(nfr):
    tt = i / FPS; cur = next((s for s in shots if s["t0"] <= tt < s["t0"] + s["len"]), None)
    sub = cur["vo"] if cur and cur["t0"] + LEAD - 0.1 <= tt <= cur["t0"] + LEAD + cur["vo_len"] + 0.2 else ""
    if sub not in cache: cache[sub] = static_layer(sub)
    im = cache[sub].copy(); e = float(env[min(i, len(env)-1)])
    cx, cy = W//2, 1700; r = 118 + int(22 * e)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    g.ellipse((cx-r-10, cy-r-10, cx+r+10, cy+r+10), fill=(37, 99, 235, int(70 + 120*e)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)) if e > 0.02 else glow)
    ImageDraw.Draw(im).ellipse((cx-118, cy-118, cx+118, cy+118), fill="white")
    im.alpha_composite(av, (cx-110, cy-110))
    im.save(f"{fdir}/{i:05d}.png", compress_level=1)
# 6. 合成
OUT = f"{D}/{cfg.get('output', 'AI替我说-' + cfg.get('slug','ep') + '.mp4')}"
ain = ["-i", f"{B}/voice.wav"] + (["-i", f"{B}/music.wav"] if os.path.exists(f"{B}/music.wav") else [])
amix = "[2:a][3:a]amix=inputs=2:normalize=0[a]" if len(ain) == 4 else "[2:a]anull[a]"
sh("ffmpeg","-y","-i",f"{B}/base.mp4","-framerate",str(FPS),"-i",f"{fdir}/%05d.png",*ain,
   "-filter_complex",f"[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p[v];{amix}",
   "-map","[v]","-map","[a]","-c:v","libx264","-crf","19","-preset","medium","-c:a","aac","-b:a","192k","-t",str(TOTAL),"-movflags","+faststart",OUT)
# 7. 封面 = 第 1 镜 ref + 叠加层(带标题，无字幕)
cv = Image.open(f"{D}/{cfg['cover_ref']}" if cfg.get("cover_ref") else shots[0]["ref"]).convert("RGBA"); lay = static_layer("")
d = ImageDraw.Draw(lay); cx, cy = W//2, 1700
d.ellipse((cx-128, cy-128, cx+128, cy+128), fill=(37, 99, 235, 200)); d.ellipse((cx-118, cy-118, cx+118, cy+118), fill="white")
lay.alpha_composite(av, (cx-110, cy-110)); cv.alpha_composite(lay)
d = ImageDraw.Draw(cv)
if cfg.get("cover_headline"):  # 可选：封面大标题/副标题，放在标题条与截图之间
    d.text((W/2, 300), cfg["cover_headline"], font=F(96), fill=(17, 24, 39), anchor="mm")
    if cfg.get("cover_subline"): d.text((W/2, 410), cfg["cover_subline"], font=F(56), fill=(37, 99, 235), anchor="mm")
d.text((W/2, 1450), "  ".join(cfg.get("tags", [])), font=F(44), fill=(37, 99, 235), anchor="mm")
cv.convert("RGB").save(f"{D}/cover.png")
json.dump({"total": round(TOTAL, 2), "shots": [{k: s[k] for k in ("id","t0","len","vo_len","use")} for s in shots]}, open(f"{B}/timeline.json","w"), ensure_ascii=False, indent=2)
print("OK", OUT, round(TOTAL, 2))
