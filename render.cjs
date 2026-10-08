// Renderiza src/omma-lanzamiento.html cuadro a cuadro y lo codifica con ffmpeg.
//   node render.cjs                 → out/omma-lanzamiento-9x16.mp4
//   node render.cjs --stills 1,6,12 → out/stills/t-<seg>.png (revisión)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const SRC = 'file://' + path.join(__dirname, 'src', 'omma-lanzamiento.html');
const args = process.argv.slice(2);
const stillsArg = args.includes('--stills') ? args[args.indexOf('--stills') + 1] : null;

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
      await stage.screenshot({ path: path.join(__dirname, 'out', 'stills', `t-${t}.png`) });
    }
    await browser.close();
    return;
  }

  const { DURATION, FPS } = await page.evaluate(() => ({ DURATION: window.DURATION, FPS: window.FPS }));
  const total = Math.round(DURATION * FPS);
  const outFile = path.join(__dirname, 'out', 'omma-lanzamiento-9x16.mp4');
  // la música (tools/musica.py → out/musica.wav) se mezcla si existe, normalizada a -14 LUFS
  const music = path.join(__dirname, 'out', 'musica.wav');
  const audio = fs.existsSync(music)
    ? ['-i', music, '-map', '0:v', '-map', '1:a', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    : [];
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-', ...audio,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-tune', 'grain', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', outFile],
    { stdio: ['pipe', 'ignore', 'inherit'] });

  for (let i = 0; i < total; i++) {
    await page.evaluate(t => render(t), i / FPS);
    const buf = await stage.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`cuadro ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('listo:', outFile);
})();
