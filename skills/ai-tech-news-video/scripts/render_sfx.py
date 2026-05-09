#!/usr/bin/env python3
"""
Synthesize sound effects as WAV files using numpy.
These WAV files can be used in HyperFrames via <audio> tags.

Usage: python3 render_sfx.py [output-dir]
Output: whoosh.wav, impact.wav, pop.wav, click.wav, sparkle.wav, rise.wav
"""

import struct
import math
import os
import sys

OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "assets/audio/sfx"
SAMPLE_RATE = 44100

def mulberry32(seed):
    """Seeded PRNG for deterministic output."""
    state = [seed]
    def rand():
        state[0] = (state[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = state[0]
        t = ((t ^ (t >> 15)) * (1 | t)) & 0xFFFFFFFF
        t = (t + (((t ^ (t >> 7)) * (61 | t)) ^ t)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) >> 0) / 4294967296
    return rand

def write_wav(filename, samples):
    """Write 16-bit mono WAV file."""
    num_samples = len(samples)
    data_size = num_samples * 2
    with open(filename, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write(struct.pack('<IHHIIHH', 16, 1, 1, SAMPLE_RATE, SAMPLE_RATE * 2, 2, 16))
        f.write(b'data')
        f.write(struct.pack('<I', data_size))
        for s in samples:
            s = max(-1.0, min(1.0, s))
            f.write(struct.pack('<h', int(s * 32767)))

def synth_whoosh():
    """Whoosh / transition sweep (350ms)."""
    duration = 0.35
    n = int(SAMPLE_RATE * duration)
    rng = mulberry32(42)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Noise with envelope
        noise = (rng() * 2 - 1) * (1 - i/n) ** 2
        # Frequency sweep: bandpass center 200→3500→200
        progress = i / n
        if progress < 0.43:
            center = 200 * (3500/200) ** (progress / 0.43)
        else:
            center = 3500 * (200/3500) ** ((progress - 0.43) / 0.57)
        # Simple bandpass approximation: modulate noise with sweep
        mod = math.sin(2 * math.pi * center * t)
        # Gain envelope
        if t < 0.08:
            gain = t / 0.08
        else:
            gain = 1 - (t - 0.08) / (duration - 0.08)
        samples.append(noise * 0.35 * max(0, gain))
    return samples

def synth_impact():
    """Impact / bass hit (400ms)."""
    duration = 0.4
    n = int(SAMPLE_RATE * duration)
    rng = mulberry32(99)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # Low sine sweep 120→30Hz
        freq = 120 * (30/120) ** (min(t, 0.25) / 0.25) if t < 0.25 else 30
        sine = math.sin(2 * math.pi * freq * t)
        gain_s = max(0.001, math.exp(-t * 10)) * 0.6
        # Noise burst (first 120ms)
        if t < 0.12:
            noise = (rng() * 2 - 1) * max(0.001, math.exp(-t * 25)) * 0.4
        else:
            noise = 0
        samples.append(sine * gain_s + noise)
    return samples

def synth_pop():
    """Pop / notification (150ms)."""
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 880 * (1400/880) ** (min(t, 0.04) / 0.04) if t < 0.04 else 1400
        phase += 2 * math.pi * freq / SAMPLE_RATE
        sine = math.sin(phase)
        gain = max(0.001, math.exp(-t * 30)) * 0.3
        samples.append(sine * gain)
    return samples

def synth_click():
    """Click / UI feedback (100ms)."""
    duration = 0.1
    n = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 1200 * (600/1200) ** (min(t, 0.05) / 0.05) if t < 0.05 else 600
        phase += 2 * math.pi * freq / SAMPLE_RATE
        sine = math.sin(phase)
        gain = max(0.001, math.exp(-t * 40)) * 0.25
        samples.append(sine * gain)
    return samples

def synth_sparkle():
    """Sparkle / reveal (600ms)."""
    duration = 0.6
    n = int(SAMPLE_RATE * duration)
    notes = [523.25, 659.25, 783.99, 1046.5, 1318.5]
    samples = [0.0] * n
    for note_i, freq in enumerate(notes):
        start = note_i * 0.07
        phase = 0
        for i in range(n):
            t = i / SAMPLE_RATE
            if t < start:
                continue
            local_t = t - start
            if local_t > 0.4:
                break
            phase += 2 * math.pi * freq / SAMPLE_RATE
            sine = math.sin(phase)
            # Envelope: quick attack, exponential decay
            if local_t < 0.02:
                gain = (local_t / 0.02) * 0.15
            else:
                gain = max(0.001, math.exp(-(local_t - 0.02) * 10)) * 0.15
            samples[i] += sine * gain
    return samples

def synth_rise():
    """Rise / tension builder (1s)."""
    duration = 1.0
    n = int(SAMPLE_RATE * duration)
    samples = []
    phase = 0
    for i in range(n):
        t = i / SAMPLE_RATE
        # Sawtooth: sum of harmonics
        val = 0
        for h in range(1, 8):
            val += (1/h) * math.sin(2 * math.pi * 100 * h * t)
        # Lowpass approximation: reduce higher harmonics over time
        cutoff_ratio = t / duration
        val *= cutoff_ratio ** 2
        # Gain: slow rise
        gain = 0.01 + 0.24 * (t / duration)
        samples.append(val * gain)
    return samples

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"🔊 Rendering SFX to {OUTPUT_DIR}/\n")

    sounds = {
        'whoosh': synth_whoosh,
        'impact': synth_impact,
        'pop': synth_pop,
        'click': synth_click,
        'sparkle': synth_sparkle,
        'rise': synth_rise,
    }

    for name, synth_fn in sounds.items():
        samples = synth_fn()
        path = os.path.join(OUTPUT_DIR, f"{name}.wav")
        write_wav(path, samples)
        dur = len(samples) / SAMPLE_RATE
        size = os.path.getsize(path)
        print(f"  ✅ {name}.wav ({dur*1000:.0f}ms, {size/1024:.1f}KB)")

    print("\n✨ Done! Add these to HyperFrames with <audio> tags.")

if __name__ == "__main__":
    main()
