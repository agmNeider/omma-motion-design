"""Recorta los bocetos originales de OMMA y los pasa a duotono de marca.

El grafito queda en espresso (#4C2B08) y el papel en crema exacta (#EFE6D8),
para que los bocetos se fundan con el fondo del video. El cartón kraft que
asoma por los bordes de la foto se vuelve transparente.

    python3 tools/bocetos.py <foto-abrigos.jpg> <foto-corse.jpg> assets/bocetos
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ESPRESSO = np.array([0x4C, 0x2B, 0x08], float)
CREMA = np.array([0xEF, 0xE6, 0xD8], float)

# (foto, caja) — caja en píxeles de la foto original
CROPS = {
    'abrigo-a': (0, (0, 140, 355, 1095)),
    'abrigo-b': (0, (355, 180, 780, 1110)),
    'traje':    (1, (25, 280, 345, 1235)),
    'petalos':  (1, (300, 280, 690, 1235)),
    'corse':    (1, (140, 370, 320, 690)),
    'falda':    (1, (310, 700, 720, 1180)),
    'hombro':   (0, (80, 180, 330, 520)),
    'cuello':   (0, (460, 180, 660, 420)),
}
# zonas a limpiar (coordenadas del recorte): restos de bocetos vecinos
ERASE = {'petalos': [(0, 0, 62, 345), (0, 0, 400, 28)], 'traje': [(0, 0, 330, 28)]}
SCALE = 3  # se amplían para que se vean nítidos a 1080 × 1920


def kraft_mask(rgb):
    """Píxeles de cartón kraft conectados al borde del recorte."""
    a = rgb.astype(float)
    lum = a @ [0.299, 0.587, 0.114]
    mx, mn = a.max(2), a.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    paper = np.percentile(lum, 85)
    kraft = (lum < paper * 0.82) & (sat > 0.16) & (a[..., 0] >= a[..., 1]) & (a[..., 1] >= a[..., 2])
    img = Image.fromarray((kraft * 255).astype(np.uint8))
    h, w = kraft.shape
    seeds = [(x, 0) for x in range(0, w, 4)] + [(x, h - 1) for x in range(0, w, 4)] + \
            [(0, y) for y in range(0, h, 4)] + [(w - 1, y) for y in range(0, h, 4)]
    for s in seeds:
        if img.getpixel(s) == 255:
            ImageDraw.floodfill(img, s, 128)
    return np.array(img) == 128


def duotone(rgb):
    lum = rgb.astype(float) @ [0.299, 0.587, 0.114]
    # corrige la luz desigual de la foto: divide por el brillo local del papel
    paper = Image.fromarray(lum.astype(np.uint8)).filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(30))
    n = lum / np.maximum(np.array(paper, float), 1)
    lo = np.percentile(n, 1.5)
    t = np.clip((n - lo) / (0.9 - lo), 0, 1) ** 1.6
    return ESPRESSO + (CREMA - ESPRESSO) * t[..., None]


def main(src_a, src_b, out_dir):
    photos = [Image.open(src_a).convert('RGB'), Image.open(src_b).convert('RGB')]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, (i, box) in CROPS.items():
        rgb = np.array(photos[i].crop(box))
        col = duotone(rgb)
        for x0, y0, x1, y1 in ERASE.get(name, []):
            col[y0:y1, x0:x1] = CREMA
        alpha = np.where(kraft_mask(rgb), 0, 255).astype(np.uint8)
        # borde suave: se desvanece hacia los lados del recorte
        h, w = alpha.shape
        edge = np.minimum.reduce([np.arange(w)[None, :].repeat(h, 0), (w - 1 - np.arange(w))[None, :].repeat(h, 0),
                                  np.arange(h)[:, None].repeat(w, 1), (h - 1 - np.arange(h))[:, None].repeat(w, 1)])
        fade = np.clip((edge - 6) / 40, 0, 1) ** 1.5
        a = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(3))
        alpha = (np.array(a) * fade).astype(np.uint8)
        im = Image.fromarray(np.dstack([col.astype(np.uint8), alpha]), 'RGBA')
        im = im.resize((w * SCALE, h * SCALE), Image.LANCZOS)
        im.save(out / f'{name}.png', optimize=True)
        print(name, im.size)


if __name__ == '__main__':
    main(*sys.argv[1:4])
