# OMMA · Motion design

Video de presentación de marca (Reels / Historias, 1080 × 1920, 30 fps, 33 s), construido con el manual de marca de OMMA: paleta café, Cormorant Garamond + Jost + Pinyon Script, íconos de línea de trazo 5 y texturas del sistema.

- `src/omma-lanzamiento.html` — la animación. Todo su estado depende del tiempo `t`, así cada cuadro es exacto. Ábrela con `?play` para verla en tiempo real o con `?t=12.5` para congelar un instante.
- `render.cjs` — la renderiza cuadro a cuadro con Playwright y la codifica con ffmpeg.
- `fonts/` — tipografías de la marca (Google Fonts, licencia OFL).
- `out/omma-lanzamiento-9x16.mp4` — el video.

```bash
NODE_PATH=$(npm root -g) node render.cjs                    # video completo
NODE_PATH=$(npm root -g) node render.cjs --stills 3,12,30  # fotogramas de revisión
```

## Guion

| Tiempo | Capítulo | Fondo | Qué pasa |
|---|---|---|---|
| 0–5 s | 01 · El origen | Crema con líneas | Una aguja cose un hilo punteado caramelo a través del cuadro. «Cada pieza empieza *con un hilo.*» |
| 5–10 s | 02 · El oficio | Espresso (cortina hacia arriba) | Se dibuja el ícono *hecho a mano*. «Cortado y cosido *a mano.*» · PIEZA POR PIEZA |
| 10–15 s | 03 · El diseño | Crema (corte lateral) | Un molde de patronaje: línea de corte punteada, vestido, hilo de la tela y cota de cintura. «Con alma de alta *costura.*» |
| 15–20 s | 04 · El proceso | Cortes secos crema → vainilla → almendra → espresso | Diseño. Corte. Costura. Detalle. · NADA EN SERIE |
| 20–25 s | 05 · Para ti | Vainilla con grano | Script «Hecho para ti» escrito de izquierda a derecha. «Desde Montería, a toda Colombia.» |
| 25–33 s | Firma | Espresso (iris circular: la «O») | Se traza la O, el logotipo OMMA entra cerrando su espaciado hasta 0,14em, filete y VISTE TU ESENCIA. @omma_oficial |

## Reglas de movimiento usadas

El manual solo regula el movimiento web («nada de rebotes»). Para video se aplicó lo mismo con más amplitud:

- Curvas suaves (cúbica de entrada y salida, salida quíntica en textos). Ningún rebote, ningún elástico.
- Textos que suben desde detrás de una línea (máscara), nunca que aparecen de golpe.
- Acercamiento lento y continuo de cámara (5 % por escena).
- Transiciones con forma de oficio: cortina de tela, corte de tijera, la «O» del monograma como iris.
- Script una sola vez en todo el video; un único texto por pantalla; mucho aire.
- Grano de película suave y viñeta cálida, sin negros ni grises.
- Todo el contenido importante entre 300 y 1500 px de alto, lejos de la interfaz de Instagram.

El video no lleva audio: se recomienda añadir en Instagram o en el editor una pieza instrumental lenta (piano o cuerdas, 70–90 BPM). Los cortes de 15–20 s caen cada 1,1 s para acompañar el pulso.
