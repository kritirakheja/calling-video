#!/bin/zsh
# Usage: ./build.sh [frames|mix|all]   (default: all)
set -e
cd "$(dirname "$0")"
step=${1:-all}

if [[ $step == frames || $step == all ]]; then
  rm -rf frames && mkdir frames
  node src/render.mjs
fi

if [[ $step == mix || $step == all ]]; then
  .venv/bin/python src/music.py
  # voice: level it, delay by the 1.2s lead-in, pad to the full minute
  ffmpeg -v error -y -i audio/narration.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,adelay=1200:all=1,apad=whole_dur=60" -ac 2 -ar 48000 audio/voice.wav
  # music: a little room echo, then set well under the voice
  ffmpeg -v error -y -i audio/voice.wav -i audio/music.wav -filter_complex "
    [1:a]aresample=48000,aecho=0.8:0.6:110|230:0.22|0.14,loudnorm=I=-29:TP=-6:LRA=20,aresample=48000,afade=t=in:d=1.2,afade=t=out:st=57.2:d=2.8[m];
    [0:a][m]amix=inputs=2:normalize=0:duration=first[a]" -map "[a]" -t 60 audio/mix.wav
  # two-pass encode at a fixed bitrate so the file stays under 10 MB (1100k video + 128k audio over 60s is about 9.2 MB)
  X264="-c:v libx264 -preset slow -b:v 1100k -pix_fmt yuv420p -x264-params aq-mode=3"
  ffmpeg -v error -y -framerate 30 -i frames/f_%05d.png -t 60 ${=X264} -pass 1 -passlogfile out/x264 -an -f null /dev/null
  ffmpeg -v error -y -framerate 30 -i frames/f_%05d.png -i audio/mix.wav -map 0:v -map 1:a -t 60 \
    ${=X264} -pass 2 -passlogfile out/x264 -c:a aac -b:a 128k -movflags +faststart out/calling.mp4
  rm -f out/x264*
  echo "out/calling.mp4 done"
fi
