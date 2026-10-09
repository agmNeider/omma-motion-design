"""Busca fotos CC0 (dominio público) en Openverse, fuente StockSnap, y arma hojas
de contacto numeradas para elegir.

    python3 tools/buscar_fotos.py <carpeta-salida> "fabric" "linen" ...

Guarda <carpeta>/candidatas.json con id, autor, enlace y licencia de cada foto.
"""
import json
import sys
import urllib.parse
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

API = 'https://api.openverse.org/v1/images/'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'omma-motion-design/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main(out, queries):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    found, seen = [], set()
    for q in queries:
        params = urllib.parse.urlencode({'q': q, 'license': 'cc0', 'source': 'stocksnap', 'page_size': 20})
        for r in json.loads(get(f'{API}?{params}'))['results']:
            if r['id'] in seen:
                continue
            seen.add(r['id'])
            found.append({'n': len(found), 'q': q, 'id': r['id'], 'url': r['url'], 'thumb': r['thumbnail'],
                          'w': r.get('width'), 'h': r.get('height'), 'creator': r.get('creator'),
                          'landing': r.get('foreign_landing_url'), 'license': r['license']})
    (out / 'candidatas.json').write_text(json.dumps(found, indent=1, ensure_ascii=False))

    # hojas de contacto de 8 × 5 miniaturas
    T = 180
    for s in range(0, len(found), 40):
        sheet = Image.new('RGB', (8 * T, 5 * T), 'white')
        d = ImageDraw.Draw(sheet)
        for k, f in enumerate(found[s:s + 40]):
            try:
                im = Image.open(BytesIO(get(f['thumb']))).convert('RGB')
            except Exception:
                continue
            im.thumbnail((T - 4, T - 4))
            x, y = (k % 8) * T, (k // 8) * T
            sheet.paste(im, (x + 2, y + 2))
            d.rectangle((x + 2, y + 2, x + 34, y + 20), fill='black')
            d.text((x + 5, y + 5), str(f['n']), fill='white')
        sheet.save(out / f'hoja-{s // 40}.jpg', quality=85)
    print(len(found), 'candidatas')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
