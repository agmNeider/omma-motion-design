"""Banda sonora de la serie fotográfica de OMMA (src/omma-serie.html).

Piano solo y colchón suave en re mayor. Un acorde por página de la serie de
fotos, a 66,7 BPM, con un roce de papel al pasar cada página.

    python3 tools/musica.py out/musica-serie.wav

(La música de la primera versión del video está en el historial de git.)
"""
import sys

from sintesis import Mezcla, bass, pad, piano, whoosh

DURATION = 40.0
mx = Mezcla(DURATION)

# ---- Partitura: un acorde por página de la serie ----------------------------------
# Piano solo y lento, con colchón muy suave. Las páginas cambian en estos tiempos:
PAGES = [0.0, 3.0, 6.6, 10.2, 13.8, 17.4, 21.0, 24.6, 28.2, 31.8]
BEAT = 0.9   # 66,7 BPM: cuatro tiempos por página
#            acorde (graves → agudos)          melodía (tiempo dentro de la página, nota)
SCORE = [
    ([50, 57, 64, 66, 69],                    [(0.9, 76), (2.0, 74)]),              # Re maj9 · portada
    ([47, 54, 62, 66, 69],                    [(0.9, 78), (2.7, 76)]),              # Si m11 · encaje
    ([43, 50, 59, 62, 66],                    [(0.9, 74), (2.7, 71)]),              # Sol maj7 · mano
    ([45, 52, 59, 61, 64],                    [(0.9, 73), (1.8, 76), (2.7, 71)]),   # La add9 · taller
    ([42, 50, 57, 61, 64],                    [(0.9, 69), (2.7, 73)]),              # Re/Fa# · boceto
    ([40, 47, 55, 59, 62, 66],                [(1.8, 78)]),                         # Mi m9 · vestido (respiro)
    ([43, 50, 59, 61, 66],                    [(0.9, 74), (2.7, 76)]),              # Sol maj7(#11) · alta costura
    ([45, 52, 57, 62, 64],                    [(0.9, 71), (2.7, 73)]),              # La sus · pieza por pieza
    ([47, 54, 61, 62, 66],                    [(0.9, 73), (2.7, 69)]),              # Si m9 · hecho para ti
    ([38, 50, 57, 61, 64, 69],                [(1.2, 78), (2.4, 81), (3.6, 85)]),   # Re maj9 · OMMA
]


def paper(gain=1.0):
    """Roce de papel al pasar la página: ruido suave, apenas audible."""
    return whoosh(0.45, peak=.35, fmax=3500, gain=0.28 * gain)


for i, (chord, melody) in enumerate(SCORE):
    t0 = PAGES[i]
    dur = (PAGES[i + 1] if i + 1 < len(PAGES) else DURATION) - t0
    last = i == len(SCORE) - 1
    # acorde arpegiado muy despacio, como tocado a mano
    for j, m in enumerate(chord):
        v = (0.42 if j == 0 else 0.30) * (1.15 if last else 1)
        mx.add(piano(m, v, dur=7.0 if last else 5.0), t0 + 0.06 * j, pan=(m - 57) / 40)
    for dt, m in melody:
        mx.add(piano(m, 0.33 if not last else 0.28), t0 + dt, pan=0.15)
    mx.add(pad(chord[1:], dur, attack=1.6, release=2.8, cutoff=1100), t0, gain=0.55)
    mx.add(bass(chord[0] - 12, dur), t0, dry=True, gain=0.55)
    if i > 0:
        mx.add(paper(), t0 - 0.15, pan=-0.2)

mx.guardar(sys.argv[1] if len(sys.argv) > 1 else 'out/musica-serie.wav', fade_out=37.0)
