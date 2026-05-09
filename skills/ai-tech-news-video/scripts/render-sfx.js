#!/usr/bin/env node
/**
 * Render Web Audio API synthesized sound effects to WAV files.
 * These WAV files can then be used in HyperFrames via <audio> tags.
 *
 * Usage: node render-sfx.js [output-dir]
 * Output: output-dir/whoosh.wav, impact.wav, pop.wav, sparkle.wav, click.wav, rise.wav
 */

const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = process.argv[2] || 'assets/audio/sfx';

// ── Sound synthesis functions (deterministic, no Math.random) ──

function mulberry32(seed) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

async function renderSound(name, duration, renderFn) {
  const sampleRate = 44100;
  const frameCount = Math.ceil(sampleRate * duration);
  const offlineCtx = new OfflineAudioContext(1, frameCount, sampleRate);

  await renderFn(offlineCtx, duration);

  const buffer = await offlineCtx.startRendering();
  const wav = audioBufferToWav(buffer);
  const outPath = path.join(OUTPUT_DIR, `${name}.wav`);
  fs.writeFileSync(outPath, Buffer.from(wav));
  console.log(`  ✅ ${name}.wav (${(duration * 1000).toFixed(0)}ms, ${(wav.byteLength / 1024).toFixed(1)}KB)`);
  return outPath;
}

// ── Sound: Whoosh (transition sweep) ──
async function synthWhoosh(ctx, dur) {
  const bufSize = ctx.sampleRate * 0.35;
  const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
  const d = buf.getChannelData(0);
  let rng = mulberry32(42);
  for (let i = 0; i < bufSize; i++) d[i] = (rng() * 2 - 1) * Math.pow(1 - i / bufSize, 2);

  const src = ctx.createBufferSource(); src.buffer = buf;
  const flt = ctx.createBiquadFilter(); flt.type = 'bandpass'; flt.Q.value = 5;
  flt.frequency.setValueAtTime(200, 0);
  flt.frequency.exponentialRampToValueAtTime(3500, 0.15);
  flt.frequency.exponentialRampToValueAtTime(200, 0.35);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, 0);
  g.gain.linearRampToValueAtTime(0.35, 0.08);
  g.gain.linearRampToValueAtTime(0, 0.35);
  src.connect(flt).connect(g).connect(ctx.destination);
  src.start(0);
}

// ── Sound: Impact (bass hit) ──
async function synthImpact(ctx, dur) {
  const osc = ctx.createOscillator(); osc.type = 'sine';
  const g = ctx.createGain();
  osc.frequency.setValueAtTime(120, 0);
  osc.frequency.exponentialRampToValueAtTime(30, 0.25);
  g.gain.setValueAtTime(0.6, 0);
  g.gain.exponentialRampToValueAtTime(0.001, 0.3);
  osc.connect(g).connect(ctx.destination);
  osc.start(0); osc.stop(0.3);

  // Noise burst
  const bufSize = ctx.sampleRate * 0.1;
  const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
  const d = buf.getChannelData(0);
  let rng = mulberry32(99);
  for (let i = 0; i < bufSize; i++) d[i] = (rng() * 2 - 1);
  const noise = ctx.createBufferSource(); noise.buffer = buf;
  const ng = ctx.createGain();
  ng.gain.setValueAtTime(0.4, 0);
  ng.gain.exponentialRampToValueAtTime(0.001, 0.12);
  noise.connect(ng).connect(ctx.destination);
  noise.start(0);
}

// ── Sound: Pop (notification) ──
async function synthPop(ctx, dur) {
  const osc = ctx.createOscillator(); osc.type = 'sine';
  const g = ctx.createGain();
  osc.frequency.setValueAtTime(880, 0);
  osc.frequency.exponentialRampToValueAtTime(1400, 0.04);
  g.gain.setValueAtTime(0.3, 0);
  g.gain.exponentialRampToValueAtTime(0.001, 0.12);
  osc.connect(g).connect(ctx.destination);
  osc.start(0); osc.stop(0.12);
}

// ── Sound: Click (UI feedback) ──
async function synthClick(ctx, dur) {
  const osc = ctx.createOscillator(); osc.type = 'sine';
  const g = ctx.createGain();
  osc.frequency.setValueAtTime(1200, 0);
  osc.frequency.exponentialRampToValueAtTime(600, 0.05);
  g.gain.setValueAtTime(0.25, 0);
  g.gain.exponentialRampToValueAtTime(0.001, 0.08);
  osc.connect(g).connect(ctx.destination);
  osc.start(0); osc.stop(0.08);
}

// ── Sound: Sparkle (reveal/achievement) ──
async function synthSparkle(ctx, dur) {
  const notes = [523.25, 659.25, 783.99, 1046.5, 1318.5];
  notes.forEach((freq, i) => {
    const osc = ctx.createOscillator(); osc.type = 'sine';
    const g = ctx.createGain();
    osc.connect(g).connect(ctx.destination);
    const s = i * 0.07;
    osc.frequency.value = freq;
    g.gain.setValueAtTime(0, s);
    g.gain.linearRampToValueAtTime(0.15, s + 0.02);
    g.gain.exponentialRampToValueAtTime(0.001, s + 0.4);
    osc.start(s); osc.stop(s + 0.4);
  });
}

// ── Sound: Rise (tension builder) ──
async function synthRise(ctx, dur) {
  const osc = ctx.createOscillator(); osc.type = 'sawtooth';
  const flt = ctx.createBiquadFilter(); flt.type = 'lowpass'; flt.Q.value = 8;
  const g = ctx.createGain();
  osc.connect(flt).connect(g).connect(ctx.destination);
  flt.frequency.setValueAtTime(100, 0);
  flt.frequency.exponentialRampToValueAtTime(3000, 1.0);
  g.gain.setValueAtTime(0.01, 0);
  g.gain.linearRampToValueAtTime(0.25, 1.0);
  osc.start(0); osc.stop(1.0);
}

// ── WAV encoder ──
function audioBufferToWav(buffer) {
  const numCh = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const bitDepth = 16;
  const bytesPerSample = bitDepth / 8;
  const data = buffer.getChannelData(0);
  const dataLength = data.length * bytesPerSample;
  const headerLength = 44;
  const totalLength = headerLength + dataLength;
  const ab = new ArrayBuffer(totalLength);
  const view = new DataView(ab);

  writeStr(view, 0, 'RIFF');
  view.setUint32(4, totalLength - 8, true);
  writeStr(view, 8, 'WAVE');
  writeStr(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, numCh, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * numCh * bytesPerSample, true);
  view.setUint16(32, numCh * bytesPerSample, true);
  view.setUint16(34, bitDepth, true);
  writeStr(view, 36, 'data');
  view.setUint32(40, dataLength, true);

  let offset = 44;
  for (let i = 0; i < data.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, data[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }
  return ab;
}

function writeStr(view, offset, str) {
  for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
}

// ── Main ──
async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  console.log(`🔊 Rendering SFX to ${OUTPUT_DIR}/\n`);

  await renderSound('whoosh', 0.4, synthWhoosh);
  await renderSound('impact', 0.4, synthImpact);
  await renderSound('pop', 0.15, synthPop);
  await renderSound('click', 0.1, synthClick);
  await renderSound('sparkle', 0.6, synthSparkle);
  await renderSound('rise', 1.1, synthRise);

  console.log('\n✨ Done! Use these WAV files in HyperFrames <audio> tags.');
}

main().catch(console.error);
