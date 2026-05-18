#!/usr/bin/env python3
import math
import os
import struct
import wave


SAMPLE_RATE = 44100


def write_wav(path, samples, volume=1.0):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "w") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for value in samples:
            clipped = max(-1.0, min(1.0, value * volume))
            frame = struct.pack("<hh", int(clipped * 32767), int(clipped * 32767))
            wav.writeframes(frame)


def tone(freq, t):
    return math.sin(2 * math.pi * freq * t)


def envelope(t, duration, attack=0.02, release=0.08):
    if t < attack:
        return t / attack
    if t > duration - release:
        return max(0.0, (duration - t) / release)
    return 1.0


def make_sfx(path, duration, freqs, volume):
    total = int(duration * SAMPLE_RATE)
    samples = []
    for i in range(total):
        t = i / SAMPLE_RATE
        env = envelope(t, duration)
        value = sum(tone(freq, t) for freq in freqs) / len(freqs)
        samples.append(value * env)
    write_wav(path, samples, volume)


def make_bgm(path, duration):
    total = int(duration * SAMPLE_RATE)
    chord = [55.0, 82.41, 110.0, 164.81]
    samples = []
    for i in range(total):
        t = i / SAMPLE_RATE
        pulse = 0.55 + 0.45 * math.sin(2 * math.pi * 1.8 * t)
        pad = sum(tone(freq, t) for freq in chord) / len(chord)
        shimmer = 0.18 * tone(659.25, t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t))
        click = 0.08 * tone(220.0, t) if int(t * 2) % 2 == 0 else 0
        fade = min(1.0, t / 2.0, (duration - t) / 2.0)
        samples.append((0.65 * pad * pulse + shimmer + click) * fade)
    write_wav(path, samples, 0.25)


if __name__ == "__main__":
    make_bgm("assets/audio/bgm.wav", 82.0)
    make_sfx("assets/audio/sfx/whoosh.wav", 0.45, [180, 240, 360], 0.35)
    make_sfx("assets/audio/sfx/impact.wav", 0.32, [70, 110, 180], 0.45)
    make_sfx("assets/audio/sfx/ping.wav", 0.22, [880, 1320], 0.28)
