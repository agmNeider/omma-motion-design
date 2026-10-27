#!/usr/bin/env bash
# Arma la base del reel: corta los clips del taller al pulso de la música
# (0,6 s = 100 BPM), los revela con un mismo tono cálido y suave y termina en crema.
#   bash tools/reel_base.sh out/reel-base.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=${1:-out/reel-base.mp4}
V=assets/videos

# revelado común: menos saturación, tono cálido, negros levantados
G="eq=saturation=0.74:contrast=0.95,colorbalance=rs=0.05:gs=0.01:bs=-0.06:rm=0.04:bm=-0.05,curves=all='0/0.035 0.5/0.52 1/0.97'"
F="scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p"

ffmpeg -loglevel error -y \
  -i $V/maquina-costura.mov -i $V/hilo-cono.mov -i $V/botones.mov -i $V/carretes.mov \
  -f lavfi -i "color=c=0xefe6d8:s=1080x1920:r=30:d=5.4" \
  -filter_complex "
    [0:v]trim=4.6:7.6,setpts=PTS-STARTPTS,$G,$F[a];
    [1:v]trim=2.0:4.4,setpts=PTS-STARTPTS,$G,$F[b];
    [2:v]setpts=2.4*(PTS-STARTPTS),$G,$F,trim=0:2.4[c];
    [3:v]trim=2.7:5.7,setpts=PTS-STARTPTS,eq=saturation=0.62,$G,$F[d];
    [0:v]trim=0.1:3.1,setpts=PTS-STARTPTS,$G,$F[e];
    [4:v]format=yuv420p[z];
    [a][b][c][d][e][z]concat=n=6:v=1:a=0[out]" \
  -map "[out]" -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
