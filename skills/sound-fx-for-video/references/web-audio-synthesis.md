# Web Audio API SFX Synthesis Reference

Detailed parameter tuning guide for custom sound effects.

## AudioContext Setup

```javascript
// Always create one AudioContext and reuse it
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

// Resume if suspended (browser autoplay policy)
if (audioCtx.state === 'suspended') audioCtx.resume();
```

## Oscillator Types & Character

| Type | Character | Best For |
|------|-----------|----------|
| `sine` | Clean, pure, smooth | Dings, pops, sparkles, bass |
| `square` | Buzzing, retro, harsh | Errors, 8-bit, alerts |
| `sawtooth` | Bright, rich, buzzy | Rises, tension, synth pads |
| `triangle` | Soft, mellow, warm | Soft UI feedback, ambient |

## Envelope Shapes (Gain Automation)

### Short percussive (clicks, pops)
```
Gain: 0 → 0.3 (instant) → 0.001 (80ms, exponential)
```

### Medium decay (notifications, reveals)
```
Gain: 0 → 0.4 (5ms) → 0.001 (200ms, exponential)
```

### Long fade (whooshes, ambience)
```
Gain: 0 → 0.5 (100ms, linear) → 0 (400ms, linear)
```

### Rise & fall (tension builders)
```
Gain: 0.01 → 0.3 (1.5s, linear) → stop immediately
```

## Frequency Ranges & Perception

| Range | Perception | Use For |
|-------|-----------|---------|
| 20-60 Hz | Deep rumble | Impacts, bass drops |
| 60-200 Hz | Body/thump | Booms, thuds |
| 200-800 Hz | Warmth/mid | UI feedback, soft clicks |
| 800-2000 Hz | Presence | Notification dings, alerts |
| 2000-5000 Hz | Sharp/bright | Crisp clicks, typing, snaps |
| 5000-12000 Hz | Air/sizzle | Shimmer, sparkle, sizzle |

## Noise Types

```javascript
// White noise (equal energy across spectrum)
for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;

// Pink noise (more bass, natural sounding)
let b0=0,b1=0,b2=0,b3=0,b4=0,b5=0,b6=0;
for (let i = 0; i < len; i++) {
  const w = Math.random() * 2 - 1;
  b0 = 0.99886*b0 + w*0.0555179;
  b1 = 0.99332*b1 + w*0.0750759;
  b2 = 0.96900*b2 + w*0.1538520;
  b3 = 0.86650*b3 + w*0.3104856;
  b4 = 0.55000*b4 + w*0.5329522;
  b5 = -0.7616*b5 - w*0.0168980;
  data[i] = (b0+b1+b2+b3+b4+b5+b6+w*0.5362) * 0.11;
  b6 = w * 0.115926;
}

// Brown noise (deep rumble)
let last = 0;
for (let i = 0; i < len; i++) {
  const w = Math.random() * 2 - 1;
  data[i] = (last + 0.02 * w) / 1.02;
  last = data[i];
  data[i] *= 3.5;
}
```

## Layering Patterns

### Impact + Debris
- Layer 1: Low sine sweep (150→30Hz, 300ms)
- Layer 2: Noise burst (100ms, highpass 1kHz)
- Layer 3: Sub hit (40Hz sine, 500ms)

### Whoosh + Pass-by
- Layer 1: Bandpass noise sweep (200→4k→200Hz)
- Layer 2: Subtle pitch-shifted sine doppler effect

### Success / Achievement
- Layer 1: Rising chime arpeggio (C-E-G-C)
- Layer 2: Soft sparkle noise (highpass 8kHz, low volume)
- Layer 3: Warm bass pad underneath (sine 130Hz, slow attack)

## Rendering Web Audio to File (for video export)

When HyperFrames/Remotion renders to MP4, browser AudioContext won't be captured. Pre-render sounds:

```javascript
// Offline render: generate WAV file from Web Audio API
async function renderSoundToFile(renderFunction, duration, filename) {
  const sampleRate = 44100;
  const offlineCtx = new OfflineAudioContext(1, sampleRate * duration, sampleRate);
  renderFunction(offlineCtx);
  const rendered = await offlineCtx.startRendering();
  const wav = audioBufferToWav(rendered);
  const blob = new Blob([wav], { type: 'audio/wav' });
  // Save or use in video
  return URL.createObjectURL(blob);
}

function audioBufferToWav(buffer) {
  const numCh = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const format = 1; // PCM
  const bitDepth = 16;
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numCh * bytesPerSample;
  const data = buffer.getChannelData(0);
  const dataLength = data.length * bytesPerSample;
  const headerLength = 44;
  const totalLength = headerLength + dataLength;
  const arrayBuffer = new ArrayBuffer(totalLength);
  const view = new DataView(arrayBuffer);
  // WAV header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, totalLength - 8, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numCh, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  writeString(view, 36, 'data');
  view.setUint32(40, dataLength, true);
  // PCM data
  let offset = 44;
  for (let i = 0; i < data.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, data[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
  return arrayBuffer;
}

function writeString(view, offset, string) {
  for (let i = 0; i < string.length; i++)
    view.setUint8(offset + i, string.charCodeAt(i));
}
```

## Common Tuning Tips

- **Too harsh?** Add lowpass filter (cutoff 3-5kHz)
- **Too quiet?** Check gain staging; exponential ramp to 0.001, not 0 (Web Audio throws error on 0)
- **Timing off?** Use `audioCtx.currentTime + offset` for precise scheduling
- **Want variation?** Add slight random delay (±30ms) and pitch shift (±5%) for repeated sounds
- **Need stereo?** Use `StereoPannerNode` — `pan.value` from -1 (left) to 1 (right)
