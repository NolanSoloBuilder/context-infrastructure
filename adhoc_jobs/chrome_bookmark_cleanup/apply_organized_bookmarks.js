#!/usr/bin/env node

const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { execFileSync } = require('child_process');
const { backupsDir, outputDir } = require('./private_paths');

process.umask(0o077);

const chromeBookmarksPath = path.join(
  os.homedir(),
  'Library/Application Support/Google/Chrome/Default/Bookmarks',
);
const organizedPath = path.join(outputDir, 'Bookmarks.organized.json');

function checksumBookmarks(bookmarks) {
  const md5 = crypto.createHash('md5');

  function checksumNode(node) {
    md5.update(String(node.id || ''), 'utf8');
    md5.update(Buffer.from(String(node.name || ''), 'utf16le'));
    if (node.type === 'url') {
      md5.update('url', 'utf8');
      md5.update(String(node.url || ''), 'utf8');
    } else {
      md5.update('folder', 'utf8');
      for (const child of node.children || []) checksumNode(child);
    }
  }

  for (const root of ['bookmark_bar', 'other', 'synced']) checksumNode(bookmarks.roots[root]);
  return md5.digest('hex');
}

function chromeIsRunning() {
  try {
    const output = execFileSync('pgrep', ['-x', 'Google Chrome'], { encoding: 'utf8' });
    return output.trim().length > 0;
  } catch (_error) {
    return false;
  }
}

function timestamp() {
  const d = new Date();
  const pad = (value) => String(value).padStart(2, '0');
  return [
    d.getFullYear(),
    pad(d.getMonth() + 1),
    pad(d.getDate()),
    '_',
    pad(d.getHours()),
    pad(d.getMinutes()),
    pad(d.getSeconds()),
  ].join('');
}

function validateBookmarkFile(filePath) {
  const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const computed = checksumBookmarks(data);
  if (data.checksum !== computed) {
    throw new Error(`Checksum mismatch for ${filePath}: stored=${data.checksum} computed=${computed}`);
  }
  return data;
}

function main() {
  if (chromeIsRunning()) {
    console.error('Google Chrome is running. Quit Chrome first, then run this script again.');
    process.exit(2);
  }

  fs.mkdirSync(backupsDir, { recursive: true });
  validateBookmarkFile(chromeBookmarksPath);
  validateBookmarkFile(organizedPath);

  const backupPath = path.join(backupsDir, `Bookmarks.pre_apply_${timestamp()}.json`);
  fs.copyFileSync(chromeBookmarksPath, backupPath);
  fs.copyFileSync(organizedPath, chromeBookmarksPath);
  validateBookmarkFile(chromeBookmarksPath);

  console.log(JSON.stringify({
    applied: true,
    target: chromeBookmarksPath,
    backup: backupPath,
    source: organizedPath,
  }, null, 2));
}

main();
