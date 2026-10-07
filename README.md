

https://github.com/user-attachments/assets/6dbf87c3-9d69-47bf-afa9-c723a9cae439





# The stages of a calling

A one-minute animated video based on David Brooks's essay "A Surprising Route to the Best Life Possible" (The New York Times, 27 March 2025). The finished video is [`out/calling.mp4`](out/calling.mp4).

One figure follows one light from a night at the ballpark to a dawn on a mountain, through the essay's five stages: enchantment, curiosity, the gap, mastery and endurance. The narration is a paraphrase of the essay, not its text.

## Made with Claude Code

This video was made entirely with [Claude Code](https://claude.com/claude-code), Anthropic's coding agent. I gave it the essay and directed the format, the style and the revisions. Claude Code wrote the narration script, generated the voice, wrote the animation and music code, rendered the frames, mixed the audio and checked the result. No video editor was used.

Everything is generated locally on a Mac, with no paid APIs for voice, music or visuals.

## How it is made

| Part | Tool | File |
|---|---|---|
| Narration | Kokoro text-to-speech | `src/tts.py`, reading `src/script.txt` |
| Word timings and captions | Whisper (`mlx-whisper`) | `audio/words.json` |
| Animation | HTML canvas, drawn one frame at a time | `src/index.html` |
| On-screen type | GSAP timeline | `src/index.html` |
| Frame capture | Playwright (headless Chromium) | `src/render.mjs` |
| Music | Synthesised with NumPy | `src/music.py` |
| Mixing and encoding | ffmpeg | `build.sh` |

`src/index.v1-footage.html` is an earlier version built on stock footage, kept for comparison. It needs clips that are not in this repo.

## Rebuilding

Requires macOS on Apple Silicon, `ffmpeg`, `espeak-ng`, Node and [uv](https://docs.astral.sh/uv/).

```sh
uv venv --seed --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
npm install && npx playwright install chromium

./build.sh          # render all 1,800 frames, then mix and encode
./build.sh frames   # visuals only
./build.sh mix      # music, audio mix and final encode only
```

To change the narration, edit `src/script.txt`, run `.venv/bin/python src/tts.py af_heart 0.94`, and regenerate `audio/words.json` with Whisper. The cue times in `src/index.html` are written as narration seconds and will need updating to match.

## Credits

Essay by David Brooks, The New York Times. Voice: Kokoro (`af_heart`). Video made with Claude Code.
