// Renders src/index.html to transparent PNG frames.
//   node src/render.mjs            -> every frame into frames/
//   node src/render.mjs 3,12.5,40  -> only those seconds, into out/stills/
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const FPS = 30, DUR = 60, WORKERS = 6;
const words = JSON.parse(fs.readFileSync(path.join(ROOT, 'audio/words.json'), 'utf8'));
const stills = process.argv[2] ? process.argv[2].split(',').map(Number) : null;

const jobs = stills
  ? stills.map(t => ({ t, file: path.join(ROOT, 'out/stills', `t_${t.toFixed(2).padStart(5, '0')}.png`) }))
  : Array.from({ length: FPS * DUR }, (_, i) => ({ t: i / FPS, file: path.join(ROOT, 'frames', `f_${String(i).padStart(5, '0')}.png`) }));
fs.mkdirSync(path.dirname(jobs[0].file), { recursive: true });

const browser = await chromium.launch();
let next = 0;
async function worker() {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exitCode = 1; });
  await page.addInitScript(w => { window.WORDS = w; }, words);
  await page.goto('file://' + path.join(ROOT, 'src/index.html'));
  await page.waitForFunction('window.ready === true');
  await page.evaluate(() => document.fonts.ready);
  while (next < jobs.length) {
    const job = jobs[next++];
    await page.evaluate(t => window.seek(t), job.t);
    await page.screenshot({ path: job.file });
  }
  await page.close();
}
await Promise.all(Array.from({ length: Math.min(WORKERS, jobs.length) }, worker));
await browser.close();
console.log(`rendered ${jobs.length} frames`);
