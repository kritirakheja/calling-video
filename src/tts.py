"""Narrate src/script.txt with Kokoro. One paragraph per beat, joined with a short pause."""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
PAUSE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.45

paragraphs = [p.strip() for p in (ROOT / "src/script.txt").read_text().split("\n\n") if p.strip()]
pipeline = KPipeline(lang_code="a")

chunks = []
for i, para in enumerate(paragraphs):
    parts = [np.asarray(audio) for _, _, audio in pipeline(para, voice=VOICE, speed=SPEED)]
    chunks.append(np.concatenate(parts))
    if i < len(paragraphs) - 1:
        chunks.append(np.zeros(int(SR * PAUSE), dtype=np.float32))

audio = np.concatenate(chunks)
out = ROOT / "audio/narration.wav"
sf.write(out, audio, SR)
print(f"{out} {len(audio) / SR:.2f}s voice={VOICE} speed={SPEED}")
