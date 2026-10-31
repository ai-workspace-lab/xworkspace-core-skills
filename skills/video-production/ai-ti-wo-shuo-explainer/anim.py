"""动画科普模式：手绘图解原语 + 场景渲染。所有画面在 1080x1920 白底上逐帧绘制。
内容安全区: y 260–1330（上方标题条，下方字幕从 1390 起、头像徽章 1580+）。
原语都接受 0..1 的进度 p，自动缓动；颜色按 alpha 与白底混合，避免逐层 RGBA 合成。"""
import math, subprocess
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"; REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
INK, GRAY, BLUE, LBLUE, LINE, GREEN, RED, CARD = (17,24,39), (107,114,128), (22,104,227), (232,240,254), (203,213,225), (22,163,74), (220,38,38), (248,250,252)
_fc = {}
def F(sz, bold=True):
    k = (sz, bold)
    if k not in _fc: _fc[k] = ImageFont.truetype(BOLD if bold else REG, sz)
    return _fc[k]
def clamp(x): return max(0.0, min(1.0, x))
def ease(p): p = clamp(p); return p * p * (3 - 2 * p)
def seg(t, a, b): """时间 t 在 [a,b] 内的进度 0..1""" ; return clamp((t - a) / max(b - a, 1e-6))
def mix(c, a): a = clamp(a); return tuple(int(255 + (v - 255) * a) for v in c)
def lerp(p0, p1, p): return (p0[0] + (p1[0] - p0[0]) * p, p0[1] + (p1[1] - p0[1]) * p)

def text(d, xy, s, sz=48, col=INK, a=1, bold=True, anchor="mm"):
    if a > 0.01: d.text(xy, s, font=F(sz, bold), fill=mix(col, a), anchor=anchor)
def box(d, cx, cy, w, h, label=None, p=1, sz=48, sub=None, fill=CARD, outline=LINE, col=INK, r=28, width=4):
    """从中心弹出的圆角卡片(reveal: 缩放 0.85→1 + 淡入)"""
    e = ease(p)
    if e <= 0.01: return
    s = 0.85 + 0.15 * e; w2, h2 = w * s / 2, h * s / 2
    d.rounded_rectangle((cx - w2, cy - h2, cx + w2, cy + h2), r, fill=mix(fill, e), outline=mix(outline, e), width=width)
    if label: text(d, (cx, cy - (22 if sub else 0)), label, sz, col, e)
    if sub: text(d, (cx, cy + sz * 0.75), sub, int(sz * 0.62), GRAY, e, bold=False)
def arrow(d, p0, p1, p=1, col=BLUE, width=8, head=26):
    """从 p0 向 p1 生长的箭头"""
    e = ease(p)
    if e <= 0.01: return
    q = lerp(p0, p1, e); d.line([p0, q], fill=col, width=width)
    ang = math.atan2(q[1] - p0[1], q[0] - p0[0])
    pts = [q, (q[0] - head * math.cos(ang - 0.45), q[1] - head * math.sin(ang - 0.45)), (q[0] - head * math.cos(ang + 0.45), q[1] - head * math.sin(ang + 0.45))]
    d.polygon(pts, fill=col)
def path_point(pts, u):
    L = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(L); u = (u % 1) * tot
    for i, l in enumerate(L):
        if u <= l: return lerp(pts[i], pts[i + 1], u / max(l, 1e-6))
        u -= l
    return pts[-1]
def flow(d, pts, t, n=4, speed=0.6, col=BLUE, r=12, a=1, track=True):
    """沿折线流动的小圆点(数据/任务在流动)"""
    if a <= 0.01: return
    if track: d.line(pts, fill=mix(LINE, a), width=4)
    for k in range(n):
        x, y = path_point(pts, t * speed + k / n); d.ellipse((x - r, y - r, x + r, y + r), fill=mix(col, a))
def badge(d, cx, cy, n, p=1, r=34):
    """步骤计数徽章 ①②③"""
    e = ease(p)
    if e <= 0.01: return
    rr = r * (0.6 + 0.4 * e); d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=mix(BLUE, e)); text(d, (cx, cy + 1), str(n), int(rr * 1.1), (255, 255, 255), 1)
def pulse(d, cx, cy, r, t, col=BLUE, a=1):
    """向外扩散的圆环(在线/提示)"""
    for k in range(2):
        q = (t * 0.8 + k / 2) % 1; rr = r * (1 + q * 1.2)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=mix(col, a * (1 - q) * 0.8), width=5)
    d.ellipse((cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5), fill=mix(col, a))
def cloud(d, cx, cy, s=1, p=1, col=LBLUE, outline=BLUE):
    e = ease(p)
    if e <= 0.01: return
    s *= 0.85 + 0.15 * e
    for dx, dy, r in [(-150, 30, 110), (0, -40, 150), (150, 30, 110), (-70, 70, 100), (70, 70, 100)]:
        d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), fill=mix(outline, e))
    for dx, dy, r in [(-150, 30, 102), (0, -40, 142), (150, 30, 102), (-70, 70, 92), (70, 70, 92)]:
        d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s, cx + (dx + r) * s, cy + (dy + r) * s), fill=mix(col, e))
def monitor(d, cx, cy, w, h, p=1, label=None):
    """一台电脑(显示器+底座)"""
    e = ease(p)
    if e <= 0.01: return
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 22, fill=mix((38, 38, 42), e))
    d.rectangle((cx - 30, cy + h / 2, cx + 30, cy + h / 2 + 40), fill=mix((120, 120, 128), e)); d.rounded_rectangle((cx - 100, cy + h / 2 + 36, cx + 100, cy + h / 2 + 52), 8, fill=mix((120, 120, 128), e))
    if label: text(d, (cx, cy + h / 2 + 95), label, 46, INK, e)
def chat(d, cx, cy, w, h, lines, p=1, col=BLUE):
    """对话气泡"""
    e = ease(p)
    if e <= 0.01: return
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 36, fill=mix(col, e))
    d.polygon([(cx - w / 2 + 50, cy + h / 2 - 2), (cx - w / 2 + 110, cy + h / 2 - 2), (cx - w / 2 + 40, cy + h / 2 + 50)], fill=mix(col, e))
    for i, s in enumerate(lines): text(d, (cx, cy - (len(lines) - 1) * 33 + i * 66), s, 50, (255, 255, 255), e)
def typing(d, x, y, lines, p, sz=36, col=(134, 239, 172)):
    """终端逐字打出的命令行"""
    total = sum(len(s) for s in lines); n = int(total * clamp(p))
    for i, s in enumerate(lines):
        k = min(len(s), max(0, n)); n -= len(s)
        if k: d.text((x, y + i * (sz + 14)), s[:k], font=F(sz, False), fill=col)
def paste(im, img, cx, cy, w, p=1):
    """把真实素材(截图/图标)淡入贴上，作为点缀锚点"""
    e = ease(p)
    if e <= 0.01: return
    h = int(img.height * w / img.width); t = img.resize((int(w), h), Image.LANCZOS).convert("RGB")
    if e < 0.99: t = Image.blend(Image.new("RGB", t.size, "white"), t, e)
    im.paste(t, (int(cx - w / 2), int(cy - h / 2)))

def render(scene, L, out, still=None):
    """scene(im, d, t, L) 逐帧绘制 → out.mp4；still: 另存末帧 PNG(封面/ref 用)"""
    n = int(round(L * FPS))
    pr = subprocess.Popen(["ffmpeg", "-y", "-v", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out], stdin=subprocess.PIPE)
    last = None
    for i in range(n):
        im = Image.new("RGB", (W, H), "white"); scene(im, ImageDraw.Draw(im), i / FPS, L); pr.stdin.write(im.tobytes()); last = im
    pr.stdin.close(); pr.wait()
    if still and last: last.save(still)
