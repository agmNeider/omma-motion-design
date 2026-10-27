// Renderiza una composición de src/ cuadro a cuadro y la codifica con ffmpeg.
//   node render.cjs                                  → out/omma-serie-9x16.mp4
//   node render.cjs --src src/omma-reel.html --base out/reel-base.mp4 --audio out/musica-reel.wav --out out/omma-reel-9x16.mp4
//     (--base: la composición es una capa transparente que se superpone a ese video)
//   node render.cjs --src src/omma-lanzamiento.html --out out/omma-lanzamiento-9x16.mp4 --audio out/musica.wav
//   node render.cjs --stills 1,6,12                  → out/stills/t-<seg>.png (revisión)
const { chromium } = require('playwright');
const { spawn, spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const opt = (name, def) => args.includes(name) ? args[args.indexOf(name) + 1] : def;
const SRC = 'file://' + path.resolve(__dirname, opt('--src', 'src/omma-serie.html'));
const stillsArg = opt('--stills', null);
const base = opt('--base', null);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(SRC);
  await page.evaluate(() => window.ready);
  const stage = await page.$('#stage');

  if (stillsArg) {
    fs.mkdirSync(path.join(__dirname, 'out', 'stills'), { recursive: true });
    for (const t of stillsArg.split(',').map(Number)) {
      await page.evaluate(t => render(t), t);
      const file = path.join(__dirname, 'out', 'stills', `t-${t}.png`);
      await stage.screenshot({ path: file, omitBackground: !!base });
      if (base) {  // revisión con el video debajo
        spawnSync('ffmpeg', ['-loglevel', 'error', '-y', '-ss', String(t), '-i', path.resolve(__dirname, base), '-i', file,
          '-filter_complex', '[0:v][1:v]overlay=0:0', '-frames:v', '1', file + '.tmp.png']);
        fs.renameSync(file + '.tmp.png', file);
      }
    }
    await browser.close();
    return;
  }

  const { DURATION, FPS } = await page.evaluate(() => ({ DURATION: window.DURATION, FPS: window.FPS }));
  const total = Math.round(DURATION * FPS);
  const outFile = path.resolve(__dirname, opt('--out', 'out/omma-serie-9x16.mp4'));
  // la música (tools/musica.py) se mezcla si existe, normalizada a -14 LUFS
  const music = path.resolve(__dirname, opt('--audio', 'out/musica-serie.wav'));
  // entradas: [video base], cuadros por tubería, [música]
  const inputs = [], maps = [];
  if (base) inputs.push('-i', path.resolve(__dirname, base));
  inputs.push('-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-');
  const nAudio = base ? 2 : 1;
  if (base) maps.push('-filter_complex', '[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]', '-map', '[v]');
  else maps.push('-map', '0:v');
  if (fs.existsSync(music)) {
    inputs.push('-i', music);
    maps.push('-map', `${nAudio}:a`, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest');
  }
  const ff = spawn('ffmpeg', ['-y', ...inputs, ...maps,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-tune', 'grain', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outFile],
    { stdio: ['pipe', 'ignore', 'inherit'] });

  for (let i = 0; i < total; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await stage.screenshot({ type: 'png', omitBackground: !!base });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`cuadro ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('listo:', outFile);
})();
