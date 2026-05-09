---
name: sound-fx-for-video
description: "用于视频制作中的音效方案：搜索下载免费音效、Web Audio API 合成音效、以及在 HyperFrames/Remotion/HTML5 视频中的音频集成。触发词包括：音效、SFX、配乐、BGM、whoosh、click、transition、impact、typing 等。"
---

# 视频音效制作 Skill

视频需要声音。这份 Skill 覆盖两条主路径：
1. **搜索并下载** 免费音效素材
2. **合成生成** 自定义音效（Web Audio API，无需外部文件）

按需求选择路径，实际项目通常会混合使用。

---

## 路径一：搜索并下载免费音效

### 推荐来源

| Source | URL | License | API | Best For |
|--------|-----|---------|-----|----------|
| Freesound | freesound.org | CC licenses (check per-file) | REST API (key required) | Huge library, specific sounds |
| Mixkit | mixkit.co/free-sound-effects | Free, no attribution | No | Quick grabs, curated quality |
| Pixabay | pixabay.com/sound-effects | Free, no attribution | No | Clean UI, good variety |
| BBC SFX | bbcsfx.acropolis.org.uk | Free for personal/educational | No | Premium BBC quality |
| ZapSplat | zapsplat.com | Free with attribution | No | Game/comedy/cartoon sounds |
| SoundBible | soundbible.com | Mixed (check per-file) | No | Quick one-off downloads |

### 搜索策略

1. **关键词要具体。**  
   差：`click sound`  
   好：`mouse click sharp UI feedback`  
   差：`whoosh`  
   好：`fast whoosh air sweep transition`

2. **组合关键词搜索：**
   - Object + action: "glass shatter", "paper crumple"
   - Mood + type: "cinematic impact bass", "playful pop notification"
   - Context: "UI button click feedback", "slide transition whoosh"

3. **常见音效分类与搜索词：**

   | Category | Search Terms |
   |----------|-------------|
   | Transitions | whoosh, sweep, swoosh, riser, dive |
   | UI feedback | click, tap, pop, blip, notification, ding |
   | Impacts | boom, hit, slam, thud, punch, bass drop |
   | Typing | keyboard, typing, keystroke, mechanical |
   | Reveals | shimmer, sparkle, magic, chime, glow |
   | Movement | slide, swoop, flutter, bounce, elastic |
   | Atmosphere | ambient, drone, hum, tension, pulse |

### 程序化下载

**Freesound API** (best for automation):

```bash
# 1. Get API key from https://freesound.org/apiv2/apply/
# 2. Search
curl "https://freesound.org/apiv2/search/text/?query=whoosh+transition&fields=id,name,previews,duration,license&token=YOUR_API_KEY"

# 3. Download preview (mp3, no auth needed)
curl -o whoosh.mp3 "https://freesound.org/data/previews/ID_ID_preview.mp3"

# 4. Download full quality (OAuth2 needed)
```

**Simple curl download** (sources with direct links):

```bash
# Pixabay (find the download URL from browser network tab)
curl -L -o click.mp3 "https://cdn.pixabay.com/audio/..."

# Mixkit
curl -L -o transition.wav "https://assets.mixkit.co/active_storage/sfx/..."
```

**Python helper** (for batch downloads):

```python
import urllib.request
import json

FREESOUND_TOKEN = "YOUR_TOKEN"

def search_sfx(query, max_results=5):
    url = f"https://freesound.org/apiv2/search/text/?query={query}&fields=id,name,previews,duration,license&token={FREESOUND_TOKEN}"
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())["results"][:max_results]

def download_preview(sound_id, filename):
    url = f"https://freesound.org/data/previews/{sound_id//1000}/{sound_id}_{sound_id}_preview.mp3"
    urllib.request.urlretrieve(url, filename)
```

### 版权检查

发布前必须检查授权协议：
- **CC0**: Use freely, no attribution
- **CC-BY**: Use with attribution (add to video description)
- **CC-BY-NC**: Non-commercial only — do NOT use for monetized videos
- **CC-BY-SA**: Derivatives must share same license

---

## 路径二：使用 Web Audio API 合成音效

无需音频文件，直接在浏览器中实时合成，适合代码驱动视频流程（HyperFrames、Remotion、HTML5）。

### 快速参考：常见视频音效模式

#### UI Click / Tap
```javascript
function playClick(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
  osc.start(); osc.stop(audioCtx.currentTime + 0.08);
}
```

#### Notification Pop / Ding
```javascript
function playPop(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'sine';
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(880, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.05);
  gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2);
  osc.start(); osc.stop(audioCtx.currentTime + 0.2);
}
```

#### Whoosh / Transition Sweep
```javascript
function playWhoosh(audioCtx) {
  const bufferSize = audioCtx.sampleRate * 0.4;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 2);
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'bandpass'; filter.Q.value = 5;
  filter.frequency.setValueAtTime(200, audioCtx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(4000, audioCtx.currentTime + 0.2);
  filter.frequency.exponentialRampToValueAtTime(200, audioCtx.currentTime + 0.4);
  const gain = audioCtx.createGain();
  gain.gain.setValueAtTime(0, audioCtx.currentTime);
  gain.gain.linearRampToValueAtTime(0.5, audioCtx.currentTime + 0.1);
  gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.4);
  source.connect(filter).connect(gain).connect(audioCtx.destination);
  source.start();
}
```

#### Impact / Bass Hit
```javascript
function playImpact(audioCtx) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = 'sine';
  osc.connect(gain).connect(audioCtx.destination);
  osc.frequency.setValueAtTime(150, audioCtx.currentTime);
  osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.3);
  gain.gain.setValueAtTime(1, audioCtx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
  osc.start(); osc.stop(audioCtx.currentTime + 0.4);
  // Add noise burst layer
  const bufferSize = audioCtx.sampleRate * 0.1;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) data[i] = (Math.random() * 2 - 1);
  const noise = audioCtx.createBufferSource();
  noise.buffer = buffer;
  const noiseGain = audioCtx.createGain();
  noiseGain.gain.setValueAtTime(0.5, audioCtx.currentTime);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.15);
  noise.connect(noiseGain).connect(audioCtx.destination);
  noise.start();
}
```

#### Typing / Keystroke
```javascript
function playKey(audioCtx) {
  const bufferSize = audioCtx.sampleRate * 0.03;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / bufferSize, 4);
  }
  const source = audioCtx.createBufferSource();
  source.buffer = buffer;
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'highpass'; filter.frequency.value = 2000;
  const gain = audioCtx.createGain();
  gain.gain.value = 0.15;
  source.connect(filter).connect(gain).connect(audioCtx.destination);
  source.start();
}
```

#### Rise / Tension Builder
```javascript
function playRise(audioCtx, duration = 1.5) {
  const osc = audioCtx.createOscillator();
  osc.type = 'sawtooth';
  const filter = audioCtx.createBiquadFilter();
  filter.type = 'lowpass'; filter.Q.value = 8;
  const gain = audioCtx.createGain();
  osc.connect(filter).connect(gain).connect(audioCtx.destination);
  filter.frequency.setValueAtTime(100, audioCtx.currentTime);
  filter.frequency.exponentialRampToValueAtTime(3000, audioCtx.currentTime + duration);
  gain.gain.setValueAtTime(0.01, audioCtx.currentTime);
  gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + duration);
  osc.start(); osc.stop(audioCtx.currentTime + duration);
}
```

#### Sparkle / Shimmer
```javascript
function playSparkle(audioCtx) {
  const notes = [261.63, 329.63, 392.00, 523.25, 659.25]; // C5 E5 G5 C6 E6
  notes.forEach((freq, i) => {
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    const gain = audioCtx.createGain();
    osc.connect(gain).connect(audioCtx.destination);
    const start = audioCtx.currentTime + i * 0.06;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(0.2, start + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, start + 0.4);
    osc.start(start); osc.stop(start + 0.4);
  });
}
```

### 模式速查表

| Sound | Core Technique | Key Parameters |
|-------|---------------|----------------|
| Click/Tap | Short sine + fast decay | freq 800-1500Hz, dur < 100ms |
| Pop/Bubble | Sine + freq ramp up | freq sweep up, short |
| Whoosh | Filtered noise + bandpass sweep | bandpass sweep 200→4k→200 |
| Impact | Low sine + noise burst | freq 150→30Hz, noise < 150ms |
| Typing | Highpass filtered noise | HPF 2kHz+, dur < 50ms |
| Rise/Tension | Sawtooth + filter sweep | LPF 100→3kHz over duration |
| Sparkle | Arpeggiated sine cluster | C-E-G-C-E, staggered 60ms |
| Boom/Rumble | Very low sine + slow decay | freq 40-80Hz, dur 0.5-2s |
| Slide/Move | Sine with pitch bend | freq ramp up or down |
| Error/Buzz | Square wave buzz | low freq square, short burst |

---

## 路径三：HyperFrames / Remotion 集成

### HyperFrames 音频集成

在 HyperFrames 中，音频常见有两种方式：

**方式 A：Web Audio API（实时合成）**

```javascript
// In your HyperFrames component
const audioCtx = new AudioContext();

function MyAnimation() {
  const handleClick = () => playClick(audioCtx);

  return (
    <div onClick={handleClick}>
      <h1>Click Me</h1>
    </div>
  );
}
```

**方式 B：预加载音频文件**

```javascript
// 1. Import audio file
import whooshSfx from "./sfx/whoosh.mp3";

// 2. Play on animation event
const audio = new Audio(whooshSfx);
audio.play();
```

**方式 C：Remotion `<Audio>` 组件**（使用 Remotion 时）

```jsx
import { Audio, useCurrentFrame } from "remotion";

export const MyComp = () => {
  const frame = useCurrentFrame();
  return (
    <>
      <Audio src={staticFile("whoosh.mp3")} startFrom={30} volume={0.5} />
    </>
  );
};
```

### 视听同步建议

1. **Trigger sounds at animation keyframes**, not at random times
2. **Keep sounds short** (50-300ms for UI, 300-800ms for transitions)
3. **Layer sounds** — a whoosh + impact combo feels better than either alone
4. **Volume hierarchy**: BGM (0.1-0.2) < Transition SFX (0.2-0.3) < Key SFX (0.3-0.5) < Voiceover (1.0)
5. **Always test with audio on** — silent playback hides timing issues

---

## 选择流程

```
Need a sound effect?
├── Is it a simple UI/click/pop? → Synthesize with Web Audio API (instant, no files)
├── Is it a complex/natural sound (footsteps, crowd, rain)? → Download from Freesound/Pixabay
├── Need precise control over timing? → Web Audio API synthesis
├── Need realism? → Download real recordings
└── Both? → Mix: download base layer + synthesize accents on top
```
