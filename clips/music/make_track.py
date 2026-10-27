"""Original high-energy electronic track for the Shorts edit (numpy only).

Usage: make_track.py OUT.wav BPM BARS CUE_BAR,CUE_BAR,...
Cue bars get a riser before them and a crash on them, so cuts land on hits.
"""
import sys
import wave

import numpy as np

SR = 44100
BPM = float(sys.argv[2])
BEAT = 60 / BPM
BAR = BEAT * 4
BARS = int(sys.argv[3])
CUES = {int(c) for c in sys.argv[4].split(",")}
N = int(SR * BAR * BARS) + SR
rng = np.random.default_rng(7)


def t(sec):
    return np.arange(int(SR * sec)) / SR


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def kick():
    x = t(0.35)
    f = 50 + 120 * np.exp(-x * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 8)


def clap():
    x = t(0.25)
    return rng.standard_normal(len(x)) * np.exp(-x * 22)


def hat():
    x = t(0.06)
    n = rng.standard_normal(len(x))
    n = np.diff(n, prepend=0)  # crude high-pass
    return n * np.exp(-x * 70)


def saw(freq, sec, detune=(0.0,)):
    x = t(sec)
    out = np.zeros_like(x)
    for d in detune:
        out += 2 * ((x * freq * (1 + d)) % 1) - 1
    return out / len(detune)


def lowpass(sig, alpha):
    out = np.empty_like(sig)
    acc = 0.0
    for k, v in enumerate(sig):
        acc += alpha * (v - acc)
        out[k] = acc
    return out


def note(m):
    return 440 * 2 ** ((m - 69) / 12)


# Am - F - C - G
PROG = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
ROOTS = [45, 41, 48, 43]

drums = np.zeros(N)
bass = np.zeros(N)
chords = np.zeros(N)
lead = np.zeros(N)
fx = np.zeros(N)

K, C, H = kick(), clap(), hat()


def open_hat():
    x = t(0.18)
    n = np.diff(rng.standard_normal(len(x)), prepend=0)
    return n * np.exp(-x * 18)


def crash():
    x = t(1.6)
    n = np.diff(rng.standard_normal(len(x)), prepend=0)
    return n * np.exp(-x * 2.5)


OH, CR = open_hat(), crash()
stab_cache = {}

for bar in range(BARS):
    b0 = bar * BAR
    chord = PROG[bar % 4]
    root = ROOTS[bar % 4]
    intro = bar < 2
    pre_cue = (bar + 1) in CUES and bar > 1
    for beat in range(4):
        s = b0 + beat * BEAT
        if not intro:
            add(drums, s, K, 0.9)
            if beat in (1, 3):
                add(drums, s, C, 0.35)
        add(drums, s + BEAT / 2, OH, 0.22)
        if not intro:
            for q in (0, 0.25, 0.75):
                add(drums, s + q * BEAT, H, 0.12)
        if pre_cue and beat >= 2:
            for q in (0, 0.25, 0.5, 0.75):  # snare roll into the cut
                add(drums, s + q * BEAT, C, 0.18 + 0.1 * q)
        if not intro:
            # offbeat sub bass
            bx = t(BEAT / 2)
            env = np.minimum(1, bx * 200) * np.exp(-bx * 4)
            add(bass, s + BEAT / 2, np.sin(2 * np.pi * note(root - 12) * bx) * env, 0.55)
    # chord stabs on an off-beat rhythm
    for pos in (0, 0.75, 1.5, 2.5, 3.25):
        dur = BEAT * 0.6
        key = (chord, dur)
        if key not in stab_cache:
            sig = sum(saw(note(m), dur, (-0.006, 0.0, 0.006)) for m in chord) / 3
            sig = lowpass(sig, 0.18)
            x = t(dur)
            stab_cache[key] = sig * np.exp(-x * 5)
        g = 0.12 if intro else 0.22
        add(chords, b0 + pos * BEAT, stab_cache[key], g)
    # simple lead hook in the second half of each 8-bar phrase
    if not intro:
        arp = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
        for k in range(16):
            m = arp[k % 4] + (12 if k % 8 >= 6 else 0)
            dur = BEAT / 4
            x = t(dur)
            sig = lowpass(saw(note(m), dur, (-0.004, 0.004)), 0.35)
            add(lead, b0 + k * BEAT / 4, sig * np.exp(-x * 14), 0.11)
    if bar in CUES:
        add(drums, b0, CR, 0.3)
    # noise riser into every 8-bar phrase
    if (bar + 1) in CUES:
        x = t(BAR)
        add(fx, b0, rng.standard_normal(len(x)) * (x / BAR) ** 2, 0.12)

# sidechain-style pump on everything but drums
pump = np.ones(N)
for beat in range(BARS * 4):
    i = int(beat * BEAT * SR)
    x = np.arange(int(BEAT * SR)) / SR
    seg = 1 - 0.6 * np.exp(-x * 14)
    pump[i:i + len(seg)] = seg[: len(pump[i:i + len(seg)])]

mix = drums + (bass + chords + lead + fx) * pump
mix = np.tanh(mix * 1.2)
mix /= np.max(np.abs(mix)) * 1.05

# tiny stereo widening via delayed copy
d = int(0.012 * SR)
left = mix
right = np.concatenate([np.zeros(d), mix[:-d]]) * 0.9 + mix * 0.1
stereo = np.stack([left, right], axis=1)
pcm = (stereo * 32767).astype(np.int16)

with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
