"""Banda sonora del reel del taller de OMMA (src/omma-reel.html sobre out/reel-base.mp4).

Piano en corcheas y colchón suave en re mayor, 100 BPM (un tiempo = 0,6 s). Cada
corte del video cae en un tiempo y lleva un acento grave muy suave; en la
tarjeta de cierre la pieza resuelve y se apaga.

    python3 tools/musica_reel.py out/musica-reel.wav
"""
import sys

from sintesis import Mezcla, bass, pad, piano, thump

DURATION = 19.2
BEAT = 0.6
mx = Mezcla(DURATION)

# (inicio del plano, tiempos que dura, acorde graves → agudos)
SECTIONS = [
    (0.0, 5, [50, 57, 62, 64, 66, 69]),    # Re maj9 · puntada a puntada
    (3.0, 4, [47, 54, 59, 62, 66, 69]),    # Si m11 · hilo por hilo
    (5.4, 4, [43, 50, 55, 59, 62, 66]),    # Sol maj7 · cada detalle
    (7.8, 5, [45, 52, 57, 61, 64, 69]),    # La · pensado para ti
    (10.8, 5, [47, 54, 57, 62, 64, 66]),   # Si m11 · alta costura
]
PATTERN = [1, 3, 5, 4, 2, 5, 4, 3]         # orden del ostinato en corcheas (índices del acorde)

for k, (t0, beats, chord) in enumerate(SECTIONS):
    dur = beats * BEAT
    mx.add(thump(0.35, f0=80, f1=42, decay=6.0), t0, dry=True)          # acento suave en el corte
    mx.add(bass(chord[0] - 12, dur), t0, dry=True, gain=0.6)
    mx.add(pad(chord[1:5], dur, attack=0.5, release=1.2, cutoff=1300), t0, gain=0.5)
    for i in range(beats * 2):
        m = chord[PATTERN[i % 8]]
        v = 0.36 if i % 2 == 0 else 0.27
        mx.add(piano(m, v, dur=2.5), t0 + i * BEAT / 2, pan=(m - 60) / 30)
    # nota aguda al entrar cada plano: la «firma» del corte
    mx.add(piano(chord[-1] + 12, 0.24), t0 + 0.02, pan=0.3)

# Cierre (13,8 s): resolución en re mayor, sin pulso
END = 13.8
mx.add(thump(0.5, f0=70, f1=34, decay=2.0), END, dry=True)
for j, m in enumerate([38, 50, 57, 61, 64, 69]):
    mx.add(piano(m, 0.5 if j == 0 else 0.38, dur=6.0), END + 0.05 * j, pan=(m - 55) / 40)
mx.add(pad([50, 57, 61, 64, 69], 4.4, attack=0.8, release=1.5), END, gain=0.7)
mx.add(bass(38, 5.0), END, dry=True, gain=0.7)
for t, m in [(15.4, 81), (15.7, 85), (16.2, 88)]:                         # destellos con «Viste tu esencia» y la cuenta
    mx.add(piano(m, 0.28), t, pan=0.35)

mx.guardar(sys.argv[1] if len(sys.argv) > 1 else 'out/musica-reel.wav', fade_out=17.2)
