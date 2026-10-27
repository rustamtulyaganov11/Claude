#!/usr/bin/env bash
# Builds the vertical Shorts edit: beat-aligned segments + original track.
set -euo pipefail
cd "$(dirname "$0")"
F=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
BPM=140
BAR=$(python3 -c "print(240/$BPM)")  # one bar

seg() { # out src_start bars title subtitle
  local dur
  dur=$(python3 -c "print($3*$BAR)")
  # textfile= avoids drawtext's ':' escaping rules (scores like 0:1)
  printf '%s' "$4" > "seg/$1.title.txt"
  printf '%s' "$5" > "seg/$1.sub.txt"
  ffmpeg -loglevel error -y -ss "$2" -t "$dur" -i src/source.mp4 -filter_complex "\
[0:v]fps=30,scale=1080:-2,pad=1080:1920:0:(oh-ih)/2:black,\
drawtext=fontfile=$F:textfile=seg/$1.title.txt:fontsize=130:fontcolor=white:x=(w-tw)/2:y=330:borderw=7:bordercolor=black@0.6:alpha='min(1,t*5)',\
drawtext=fontfile=$F:textfile=seg/$1.sub.txt:fontsize=62:fontcolor=0xFFD54A:x=(w-tw)/2:y=490:borderw=4:bordercolor=black@0.6:alpha='min(1,max(0,(t-0.15)*5))',\
fade=t=in:st=0:d=0.25:color=white[v]" \
    -map "[v]" -an -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p "seg/$1.mp4"
}

seg 1 70.0  2 'EL CLÁSICO' 'HIGHLIGHTS'
seg 2 91.0  9 'GOAL!' 'Mbappé · 0:1'
seg 3 110.0 9 'GOAL!' 'Raphinha · 1:1'
seg 4 143.5 3 'WHAT A SAVE!' 'Last line of defence'
seg 5 167.0 9 'GOAL!' 'Mbappé · 1:2'
seg 6 189.4 2 'FULL TIME' 'Barcelona 1:2 Real Madrid'

# segment start bars double as music cues: 0 2 11 20 23 32, total 34 bars
python3 music/make_track.py music/track.wav "$BPM" 35 2,11,20,23,32

printf "file '%s.mp4'\n" {1..6} > seg/list.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i seg/list.txt -i music/track.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -af "afade=t=out:st=$(python3 -c "print(34*$BAR-2)"):d=2" -shortest -movflags +faststart out/short-el-clasico.mp4
