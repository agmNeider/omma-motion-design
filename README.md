# OMMA · Motion design

Video de presentación de marca (Reels / Historias, 1080 × 1920, 30 fps, 40 s), construido con el manual de marca de OMMA: paleta café, Cormorant Garamond + Jost + Pinyon Script, íconos de línea de trazo 5, texturas del sistema y los bocetos originales de la marca.

- `src/omma-lanzamiento.html` — la animación. Todo su estado depende del tiempo `t`, así cada cuadro es exacto. Ábrela con `?play` para verla en tiempo real o con `?t=12.5` para congelar un instante.
- `render.cjs` — la renderiza cuadro a cuadro con Playwright y la codifica con ffmpeg.
- `assets/originales/` — fotos de los bocetos de la marca.
- `assets/bocetos/` — recortes de esos bocetos en duotono de marca (grafito → espresso, papel → crema), generados con `tools/bocetos.py`.
- `tools/musica.py` — banda sonora original, sintetizada en código (genera `out/musica.wav`, que `render.cjs` mezcla en el video).
- `fonts/` — tipografías de la marca (Google Fonts, licencia OFL).
- `out/omma-lanzamiento-9x16.mp4` — el video.

```bash
python3 tools/bocetos.py assets/originales/boceto-abrigos.jpg assets/originales/boceto-corse.jpg assets/bocetos
python3 tools/musica.py out/musica.wav                       # música (antes del render)
NODE_PATH=$(npm root -g) node render.cjs                    # video completo
NODE_PATH=$(npm root -g) node render.cjs --stills 3,12,30  # fotogramas de revisión
```

## Guion

| Tiempo | Capítulo | Fondo | Qué pasa |
|---|---|---|---|
| 0–5 s | El origen | Crema con líneas | Una aguja cose un hilo punteado caramelo a través del cuadro. «Cada pieza empieza *con un hilo.*» |
| 5–12 s | El boceto | Crema (corte lateral) | El boceto del corsé con falda de pétalos se dibuja de arriba abajo: «Todo nace *a lápiz.*» Luego los dos abrigos de hombros estructurados y el traje con corsé: «*Diseño propio.*» · BOCETOS ORIGINALES |
| 12–17 s | El oficio | Espresso (cortina hacia arriba) | Se dibuja el ícono *hecho a mano*. «Cortado y cosido *a mano.*» · PIEZA POR PIEZA |
| 17–22 s | El diseño | Crema (corte lateral) | El corsé y la falda de pétalos pasan a molde: línea de corte punteada, costuras del corsé, cota de cintura y piquetes. «Con alma de alta *costura.*» |
| 22–27 s | El proceso | Cortes secos crema → vainilla → almendra → espresso | Cada palabra con un detalle de los bocetos: Diseño (cuello y rostro) · Corte (hombro estructurado) · Costura (corsé) · Detalle (pétalos) · NADA EN SERIE |
| 27–32 s | Para ti | Vainilla con grano | Script «Hecho para ti» escrito de izquierda a derecha. «Envíos a toda Colombia.» |
| 32–40 s | Firma | Espresso (iris circular: la «O») | Se traza la O, el logotipo OMMA entra cerrando su espaciado hasta 0,14em, filete y VISTE TU ESENCIA. @omma_boutique |

## Reglas de movimiento usadas

El manual solo regula el movimiento web («nada de rebotes»). Para video se aplicó lo mismo con más amplitud:

- Curvas suaves (cúbica de entrada y salida, salida quíntica en textos). Ningún rebote, ningún elástico.
- Textos que suben desde detrás de una línea (máscara), nunca que aparecen de golpe.
- Bocetos que se revelan como si se estuvieran dibujando y suben despacio.
- Acercamiento lento y continuo de cámara (5 % por escena).
- Transiciones con forma de oficio: cortina de tela, corte de tijera, la «O» del monograma como iris.
- Script una sola vez en todo el video; un único texto por pantalla; mucho aire; sin numeración.
- Los bocetos van en duotono de la paleta para que el amarillo y el rojo del abrigo no salgan de los colores de marca.
- Grano de película suave y viñeta cálida, sin negros ni grises.
- Todo el contenido importante entre 300 y 1500 px de alto, lejos de la interfaz de Instagram.

## Música

Pieza original para piano y colchón de cuerdas en re mayor, sintetizada con `tools/musica.py` (sin muestras ni licencias de terceros). Pulso de 1,1 s (54,5 BPM), el mismo de los cortes de palabras.

| Tiempo | Música |
|---|---|
| 0–5 s | Colchón que se abre y notas sueltas de piano mientras la aguja cose. |
| 5–22 s | Arpegio de piano en corcheas: Re maj9 → Si m11 → Sol maj7 → La sus, un acorde cada 4,4 s (cuatro tiempos). |
| 22–27 s | Un golpe grave en cada corte de palabra y una subida de aire que acumula tensión. |
| 27–32 s | Respiro en Si m9: solo colchón y notas largas para «Hecho para ti». |
| 32–40 s | Resolución en Re mayor con golpe grave al abrirse la «O», destello agudo cuando el logotipo se asienta y desvanecido final. |

Cada transición de escena lleva un aire suave. Mezcla normalizada a -14 LUFS, pico de -1,5 dBTP (el estándar de Instagram).
