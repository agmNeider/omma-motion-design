"""Revela y recorta las fotos de la serie con un mismo tratamiento cálido de película.

Desatura un poco, tiñe hacia la paleta de OMMA (sombras espresso, luces marfil)
y levanta los negros, para que fotos de autores distintos parezcan una sola serie.

    python3 tools/fotos.py assets/fotos/originales assets/originales assets/fotos
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ESPRESSO = np.array([0x4C, 0x2B, 0x08], float) / 255
MARFIL = np.array([0xF6, 0xF0, 0xE4], float) / 255

# nombre de salida: (carpeta, archivo, caja de recorte o None)
SHOTS = {
    'titulo':     ('fotos', 'textura-arena.jpg', None),
    'encaje':     ('fotos', 'encaje-espalda.jpg', None),
    'mano':       ('fotos', 'mano-tul.jpg', (430, 0, 942, 640)),            # 4:5, la mano y el tul
    'ganchos':    ('fotos', 'ganchos.jpg', None),
    'tijeras':    ('fotos', 'tijeras-hilo.jpg', None),
    'boceto':     ('bocetos', 'boceto-corse.jpg', (40, 270, 735, 1236)),    # boceto original de OMMA
    'vestido':    ('fotos', 'vestido-blanco.jpg', None),
    'gala':       ('fotos', 'encaje-vestido.jpg', None),
    'alfileres':  ('fotos', 'boceto-alfileres.jpg', None),
    'strapless':  ('fotos', 'vestido-strapless.jpg', None),
    'falda':      ('fotos', 'falda-tul.jpg', (190, 0, 702, 640)),           # 4:5, el vuelo de la falda
}


def grade(img):
    x = np.asarray(img.convert('RGB'), float) / 255
    lum = (x @ [0.299, 0.587, 0.114])[..., None]
    x = lum + (x - lum) * 0.68                       # desatura
    duo = ESPRESSO + (MARFIL - ESPRESSO) * lum       # tono de marca
    x = x * 0.7 + duo * 0.3
    x = 0.5 + (x - 0.5) * 0.93                       # menos contraste
    x = 0.04 + x * 0.94                              # negros levantados, como película
    return Image.fromarray((np.clip(x, 0, 1) * 255).astype(np.uint8))


def main(fotos_dir, bocetos_dir, out_dir):
    src = {'fotos': Path(fotos_dir), 'bocetos': Path(bocetos_dir)}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (folder, file, box) in SHOTS.items():
        im = Image.open(src[folder] / file)
        if box:
            im = im.crop(box)
        grade(im).save(out / f'{name}.jpg', quality=92)
        print(name, im.size)


if __name__ == '__main__':
    main(*sys.argv[1:4])
