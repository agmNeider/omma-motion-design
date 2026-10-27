# OMMA · Motion design

Videos de presentación de marca para Reels e Historias (1080 × 1920, 30 fps, 40 s), construidos con el manual de marca de OMMA: paleta café, Cormorant Garamond + Jost, mucho aire y los bocetos originales de la marca.

| Video | Composición | Concepto |
|---|---|---|
| `out/omma-reel-9x16.mp4` | `src/omma-reel.html` sobre `out/reel-base.mp4` | **Reel del taller** (19 s): videos propios de la marca, cortes al pulso, textos breves y cierre de marca. |
| `out/omma-serie-9x16.mp4` | `src/omma-serie.html` | Serie fotográfica: un libro de fotos que se hojea despacio. |
| `out/omma-lanzamiento-9x16.mp4` | `src/omma-lanzamiento.html` | Primera versión: motion gráfico con hilo, molde y cortes de palabras. |

## Archivos

- `src/*.html` — las animaciones. Todo su estado depende del tiempo `t`, así cada cuadro es exacto. Ábrelas con `?play` para verlas en tiempo real o con `?t=12.5` para congelar un instante.
- `render.cjs` — las renderiza cuadro a cuadro con Playwright y las codifica con ffmpeg, mezclando la música normalizada a -14 LUFS.
- `assets/videos/` — videos originales del taller de OMMA (máquina, hilo, botones, carretes).
- `tools/reel_base.sh` — corta y revela los videos del taller y arma `out/reel-base.mp4`.
- `assets/fotos/originales/` — fotos CC0 de StockSnap; autores y licencia en `assets/fotos/CREDITOS.md`.
- `assets/fotos/*.jpg` — las mismas fotos reveladas y recortadas para la serie (`tools/fotos.py`).
- `assets/originales/` — fotos de los bocetos de la marca; `assets/bocetos/` sus recortes en duotono (`tools/bocetos.py`).
- `tools/buscar_fotos.py` — busca fotos CC0 en Openverse y arma hojas de contacto para elegir.
- `tools/sintesis.py` — instrumentos sintetizados (piano, colchón, bajo, aires) compartidos por las bandas sonoras.
- `tools/musica.py`, `tools/musica_reel.py` — bandas sonoras originales de la serie y del reel, sin licencias de terceros.
- `fonts/` — tipografías de la marca (Google Fonts, licencia OFL).

```bash
# reel del taller
bash tools/reel_base.sh out/reel-base.mp4
python3 tools/musica_reel.py out/musica-reel.wav
NODE_PATH=$(npm root -g) node render.cjs --src src/omma-reel.html --base out/reel-base.mp4 --audio out/musica-reel.wav --out out/omma-reel-9x16.mp4
# serie fotográfica
python3 tools/fotos.py assets/fotos/originales assets/originales assets/fotos
python3 tools/musica.py out/musica-serie.wav
NODE_PATH=$(npm root -g) node render.cjs                    # out/omma-serie-9x16.mp4
NODE_PATH=$(npm root -g) node render.cjs --stills 3,12,30  # fotogramas de revisión
# primera versión:
NODE_PATH=$(npm root -g) node render.cjs --src src/omma-lanzamiento.html --out out/omma-lanzamiento-9x16.mp4 --audio out/musica.wav
```

## Reel del taller

Hecho con los videos propios de la marca, sin imágenes de stock. 100 BPM: cada corte cae en un tiempo de la música.

| Tiempo | Plano | Texto |
|---|---|---|
| 0–3 s | Máquina cosiendo lino a rayas, las manos guían la tela | *Puntada a puntada.* |
| 3–5,4 s | Cono de hilo blanco, el hilo corre hacia la máquina | *Hilo por hilo.* |
| 5,4–7,8 s | Botones que caen sobre la tela (cámara lenta a partir de 60 fps) | *Cada detalle,* |
| 7,8–10,8 s | Carretes que llegan uno a uno (stop motion) | *pensado para ti.* |
| 10,8–13,8 s | La máquina otra vez, de cerca | *Con alma de alta costura.* |
| 13,8–19,2 s | Cierre en crema | OMMA · VISTE TU ESENCIA · @omma_boutique · HECHO A MANO · ENVÍOS A TODA COLOMBIA |

- Revelado común (`tools/reel_base.sh`): menos saturación, tono cálido y negros levantados; los carretes neón llevan una desaturación extra para que no salgan de la paleta.
- Los textos van arriba, sobre un velo crema degradado, dentro de la zona segura de Instagram y sin tapar el prensatelas.
- Música (`tools/musica_reel.py`): piano en corcheas y colchón suave en re mayor, un acento grave muy leve en cada corte y resolución en el cierre.

## Serie fotográfica

Cada página es una copia impresa con borde marfil sobre papel crema, con la sombra única de la marca. La foto se acerca muy despacio dentro de su marco, las páginas se funden con una breve pausa en crema entre una y otra, y los textos son pies de foto.

| Tiempo | Página | Pie de foto |
|---|---|---|
| 0–3 s | Portada sobre textura arena difuminada | OMMA · MODA FEMENINA HECHA A MANO |
| 3–6,6 s | Espalda de encaje | ENCAJE |
| 6,6–10 s | Mano sobre tul | *Cada detalle, a mano.* |
| 10–14 s | Díptico: ganchos de madera y tijeras con carrete | EL TALLER |
| 14–17 s | Boceto original de OMMA (corsé y falda de pétalos) | BOCETO ORIGINAL · *Todo nace a lápiz.* |
| 17–21 s | Vestido blanco a toda página (sin textos) | — |
| 21–24,6 s | Detalle de encajes de gala | *Con alma de alta costura.* |
| 24,6–28 s | Díptico: boceto con alfileres y vestido strapless | PIEZA POR PIEZA |
| 28–31,8 s | Vuelo de una falda de tul | *Algo hecho para ti.* |
| 31,8–40 s | Cierre | OMMA · VISTE TU ESENCIA · @omma_boutique · HECHO A MANO · ENVÍOS A TODA COLOMBIA |

Todas las fotos llevan el mismo revelado (`tools/fotos.py`): algo desaturadas, teñidas hacia la paleta (sombras espresso, luces marfil), con negros levantados y grano suave, para que parezcan una sola sesión.

**Música:** piano solo y colchón suave en re mayor, 66,7 BPM, un acorde por página (Re maj9 → Si m11 → Sol maj7 → La add9 → Re/Fa# → Mi m9 → Sol maj7 → La sus → Si m9 → Re maj9), con un roce de papel casi inaudible al pasar cada página.

### Por qué así: tendencias consultadas

- **Lujo silencioso:** ritmo pausado, cada toma con tiempo para respirar, paletas marfil, piedra, topo y café, luz suave y composiciones limpias.
- **Formato lookbook / libro de fotos:** secuencias de fotos fijas presentadas como una edición, más cercanas al carrusel (que en 2026 rinde mejor que el video en guardados y compartidos) que al reel de cortes rápidos.
- **Campañas más cortas y centradas en el detalle:** dejar que la tela, el movimiento y los acabados se lean en pantalla de celular.
- **Contracorriente deliberada:** la tendencia general de Reels son 8–15 cortes rápidos en 30 s; aquí se hace lo contrario a propósito, porque la calma es lo que comunica una marca premium.

## Primera versión (motion gráfico)

`src/omma-lanzamiento.html`: un hilo que cose el cuadro, los bocetos que se dibujan, el molde del corsé con falda de pétalos, cortes de palabras (Diseño · Corte · Costura · Detalle) y la firma con la «O» como iris. Su música (piano, cuerdas y golpes graves a 54,5 BPM) está en el historial de git de `tools/musica.py`.
