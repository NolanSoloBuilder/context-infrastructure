import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright';

const root = new URL('..', import.meta.url);
const baseUrl = 'http://127.0.0.1:4399';

async function waitForServer() {
  for (let index = 0; index < 80; index += 1) {
    try {
      const response = await fetch(baseUrl);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error('Vite server did not start');
}

await mkdir(new URL('../public/covers/', import.meta.url), { recursive: true });
await mkdir(new URL('../public/share_cards/', import.meta.url), { recursive: true });

const server = spawn('npm', ['run', 'dev', '--', '--port', '4399', '--strictPort'], {
  cwd: root,
  stdio: ['ignore', 'pipe', 'pipe'],
  detached: true,
});

try {
  await waitForServer();
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1200, height: 1600 }, deviceScaleFactor: 1 });
  await page.goto(`${baseUrl}/?studio=1`, { waitUntil: 'networkidle' });

  const covers = await page.locator('[data-cover]').all();
  if (covers.length !== 10) throw new Error(`Expected 10 covers, found ${covers.length}`);
  for (const cover of covers) {
    const id = await cover.getAttribute('data-cover');
    await cover.screenshot({ path: new URL(`../public/covers/post-${id}.png`, import.meta.url).pathname });
  }

  const cards = await page.locator('[data-share-card]').all();
  if (cards.length !== 8) throw new Error(`Expected 8 share cards, found ${cards.length}`);
  for (const card of cards) {
    const id = await card.getAttribute('data-share-card');
    await card.screenshot({ path: new URL(`../public/share_cards/${id}.png`, import.meta.url).pathname });
  }

  await browser.close();
  console.log(`rendered ${covers.length} covers and ${cards.length} share cards`);
} finally {
  process.kill(-server.pid, 'SIGTERM');
}
