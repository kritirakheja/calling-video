"""Score for the video, synthesised from scratch: a soft pad under plucked notes.

The chords follow the story: home (D) for the night and the spark, away to B minor for the gap,
a climb through G and A for the long hours and the storm, and back home to D at dawn.
"""
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SR, DUR = 44100, 60.0
N = int(SR * DUR)
t = np.arange(N) / SR
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)

D, DADD9, G, BM, A_ = [38, 45, 50, 54, 57], [38, 45, 52, 54, 57, 64], [43, 50, 55, 59, 62], [35, 42, 47, 50, 54], [45, 52, 57, 61, 64]
# start, end, chord (MIDI notes), loudness, seconds between plucked notes
SECTIONS = [
    (0.0, 12.5, D, 0.55, 2.0), (12.5, 19.5, DADD9, 0.7, 1.5), (19.5, 25.5, G, 0.8, 1.0), (25.5, 33.0, BM, 0.8, 1.0),
    (33.0, 37.5, G, 0.9, 0.75), (37.5, 42.0, A_, 1.0, 0.75), (42.0, 46.0, BM, 1.05, 0.5), (46.0, 49.6, A_, 1.1, 0.5),
    (49.6, 60.0, [38, 45, 50, 54, 57, 62, 66], 1.0, 1.0),
]

pad = np.zeros(N)
for start, end, chord, loud, _ in SECTIONS:
    env = np.clip((t - (start - 1.0)) / 2.0, 0, 1) * np.clip(((end + 1.0) - t) / 2.0, 0, 1)
    voice = np.zeros(N)
    for i, m in enumerate(chord):
        for detune in (-0.1, 0.1):  # two voices a hair apart give a slow shimmer
            voice += np.sin(2 * np.pi * (hz(m) + detune * (i + 1)) * t + i) / (1 + 0.4 * i)
    pad += voice / len(chord) * env * loud


def pluck(freq, length=4.0):
    n = int(SR * length)
    x = np.arange(n) / SR
    wave = sum(np.sin(2 * np.pi * freq * h * x) / h ** 2 * np.exp(-x / (1.5 / h ** 0.6)) for h in range(1, 6))
    return wave * np.clip(x / 0.008, 0, 1)


left, right = np.zeros(N), np.zeros(N)
count = 0
for start, end, chord, loud, step in SECTIONS:
    tones = [m + 12 for m in chord[2:]]  # the upper notes of the chord, an octave up
    order = tones + tones[-2:0:-1]       # walk up, then back down
    when, k = max(start, 1.2), 0
    while when < min(end, 56.5):
        note = pluck(hz(order[k % len(order)])) * 0.2 * loud
        i0 = int(when * SR)
        seg = note[: N - i0]
        pan = 0.35 if count % 2 else 0.65
        left[i0:i0 + len(seg)] += seg * (1 - pan)
        right[i0:i0 + len(seg)] += seg * pan
        when += step
        k += 1
        count += 1

mixed = np.stack([pad * 0.5 + left, np.roll(pad, 260) * 0.5 + right], axis=1)
mixed = mixed / np.abs(mixed).max() * 0.7
sf.write(ROOT / "audio/music.wav", mixed, SR)
print(f"audio/music.wav written, {count} notes")
