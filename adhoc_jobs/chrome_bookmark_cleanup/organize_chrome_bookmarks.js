#!/usr/bin/env node

const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { outputDir } = require('./private_paths');

process.umask(0o077);

const chromeBookmarksPath = path.join(
  os.homedir(),
  'Library/Application Support/Google/Chrome/Default/Bookmarks',
);
const auditItemsPath = path.join(outputDir, 'audit_items.csv');

const GROUPS = [
  {
    name: '00_常用入口',
    topLevelFolders: [],
  },
  {
    name: '01_小红书工作',
    topLevelFolders: ['小红书系统链接', '行为分析'],
  },
  {
    name: '02_AI与个人项目',
    topLevelFolders: ['AI', '国外的新玩具'],
  },
  {
    name: '03_研发与效率工具',
    topLevelFolders: ['TOOLS', '小工具', '框架工具'],
  },
  {
    name: '04_学习与资料',
    topLevelFolders: ['消息获取', '查找书籍', '英语相关', '博客', '商业分析', '学习平台'],
  },
  {
    name: '05_个人生活',
    topLevelFolders: ['4K 影视资源', '游戏相关', '股票交易', 'PERSON', '专利相关'],
  },
  {
    name: '99_待整理',
    topLevelFolders: [],
  },
];

const DIRECT_URL_RULES = [
  {
    name: 'Google 翻译',
    match: (node) => node.url?.includes('translate.google.com'),
    group: '00_常用入口',
  },
  {
    name: 'Bing 国际版',
    match: (node) => node.url?.includes('cn.bing.com'),
    group: '00_常用入口',
  },
  {
    name: 'Switch 下载入口',
    match: (node) => /switch|游戏/i.test(`${node.name} ${node.url}`),
    group: '05_个人生活',
    nestedPath: ['游戏相关', 'NS'],
  },
];

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') quoted = true;
    else if (char === ',') {
      row.push(field);
      field = '';
    } else if (char === '\n') {
      row.push(field);
      if (row.some((item) => item.length > 0)) rows.push(row);
      row = [];
      field = '';
    } else {
      field += char;
    }
  }

  if (field.length || row.length) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function loadNoHistoryUrlSet() {
  if (!fs.existsSync(auditItemsPath)) return new Set();
  const rows = parseCsv(fs.readFileSync(auditItemsPath, 'utf8'));
  const headers = rows.shift() || [];
  const urlIndex = headers.indexOf('url');
  const categoriesIndex = headers.indexOf('categories');
  if (urlIndex === -1 || categoriesIndex === -1) return new Set();

  return new Set(
    rows
      .filter((row) => (row[categoriesIndex] || '').split('|').includes('no_recent_visit_evidence'))
      .map((row) => row[urlIndex])
      .filter(Boolean),
  );
}

function chromeInternalNow() {
  return String((BigInt(Date.now()) + 11644473600000n) * 1000n);
}

function createFolder(name, id, children = []) {
  const now = chromeInternalNow();
  return {
    children,
    date_added: now,
    date_modified: now,
    guid: crypto.randomUUID(),
    id: String(id),
    name,
    type: 'folder',
  };
}

function walk(node, visit, trail = []) {
  visit(node, trail);
  if (node.type === 'folder') {
    for (const child of node.children || []) {
      walk(child, visit, [...trail, node.name]);
    }
  }
}

function countStats(bookmarks) {
  const stats = {
    urls: 0,
    folders: 0,
    emptyFolders: 0,
    domains: new Map(),
  };

  for (const rootName of ['bookmark_bar', 'other', 'synced']) {
    walk(bookmarks.roots[rootName], (node) => {
      if (node.type === 'folder') {
        stats.folders += 1;
        if ((node.children || []).length === 0) stats.emptyFolders += 1;
      } else if (node.type === 'url') {
        stats.urls += 1;
        let host = '(invalid)';
        try {
          host = new URL(node.url).hostname.replace(/^www\./, '').toLowerCase();
        } catch (_error) {
          // Keep invalid URLs visible in the report.
        }
        stats.domains.set(host, (stats.domains.get(host) || 0) + 1);
      }
    });
  }

  stats.topDomains = [...stats.domains.entries()].sort((a, b) => b[1] - a[1]).slice(0, 20);
  delete stats.domains;
  return stats;
}

function maxId(bookmarks) {
  let max = 0;
  for (const rootName of ['bookmark_bar', 'other', 'synced']) {
    walk(bookmarks.roots[rootName], (node) => {
      const id = Number(node.id);
      if (Number.isFinite(id)) max = Math.max(max, id);
    });
  }
  return max;
}

function removeExactDuplicates(folder, seen = new Map(), removed = []) {
  if (folder.type !== 'folder') return removed;

  const nextChildren = [];
  for (const child of folder.children || []) {
    if (child.type === 'url') {
      if (seen.has(child.url)) {
        removed.push({
          name: child.name,
          url: child.url,
          keptAt: seen.get(child.url),
        });
        continue;
      }
      seen.set(child.url, child.name);
      nextChildren.push(child);
    } else {
      removeExactDuplicates(child, seen, removed);
      nextChildren.push(child);
    }
  }
  folder.children = nextChildren;
  return removed;
}

function removeEmptyFolders(folder, removed = []) {
  if (folder.type !== 'folder') return false;

  folder.children = (folder.children || []).filter((child) => {
    if (child.type !== 'folder') return true;
    const shouldRemove = removeEmptyFolders(child, removed);
    if (shouldRemove) {
      removed.push(child.name);
      return false;
    }
    return true;
  });

  return folder.children.length === 0;
}

function findFolder(folder, names) {
  let current = folder;
  for (const name of names) {
    current = (current.children || []).find((child) => child.type === 'folder' && child.name === name);
    if (!current) return null;
  }
  return current;
}

function ensureFolderByPath(rootFolder, names, nextIdRef) {
  let current = rootFolder;
  for (const name of names) {
    let next = (current.children || []).find((child) => child.type === 'folder' && child.name === name);
    if (!next) {
      next = createFolder(name, nextIdRef.value++);
      current.children = current.children || [];
      current.children.push(next);
    }
    current = next;
  }
  return current;
}

function extractArchivedUrls(folder, urlSet, archiveRoot, nextIdRef, trail = []) {
  if (folder.type !== 'folder') return 0;

  let archived = 0;
  const nextChildren = [];
  for (const child of folder.children || []) {
    if (child.type === 'url') {
      if (urlSet.has(child.url)) {
        const archiveFolder = ensureFolderByPath(archiveRoot, trail, nextIdRef);
        archiveFolder.children.push(child);
        archived += 1;
      } else {
        nextChildren.push(child);
      }
      continue;
    }

    const nestedArchived = extractArchivedUrls(child, urlSet, archiveRoot, nextIdRef, [...trail, child.name]);
    archived += nestedArchived;
    if ((child.children || []).length > 0) nextChildren.push(child);
  }
  folder.children = nextChildren;
  return archived;
}

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

  for (const root of ['bookmark_bar', 'other', 'synced']) {
    checksumNode(bookmarks.roots[root]);
  }
  return md5.digest('hex');
}

function treeLines(folder, depth = 0, maxDepth = 3) {
  const lines = [];
  if (folder.type !== 'folder') return lines;
  const urlCount = countUrls(folder);
  lines.push(`${'  '.repeat(depth)}- ${folder.name} (${urlCount})`);
  if (depth >= maxDepth) return lines;
  for (const child of folder.children || []) {
    if (child.type === 'folder') {
      lines.push(...treeLines(child, depth + 1, maxDepth));
    }
  }
  const direct = (folder.children || []).filter((child) => child.type === 'url').length;
  if (direct) lines.push(`${'  '.repeat(depth + 1)}- 直接书签 ${direct}`);
  return lines;
}

function countUrls(node) {
  if (node.type === 'url') return 1;
  return (node.children || []).reduce((sum, child) => sum + countUrls(child), 0);
}

function buildExtensionPlan(bookmarks) {
  const folders = [];
  const urls = [];

  function visit(folder, parentPath) {
    for (const child of folder.children || []) {
      if (child.type === 'url') {
        urls.push({
          parentPath,
          title: child.name,
          url: child.url,
        });
        continue;
      }

      const childPath = [...parentPath, child.name];
      folders.push({ path: childPath });
      visit(child, childPath);
    }
  }

  visit(bookmarks.roots.bookmark_bar, []);
  return { folders, urls };
}

function reorganize(bookmarks) {
  const result = clone(bookmarks);
  const before = countStats(result);
  const removedDuplicates = [];
  const removedEmptyFolders = [];
  const noHistoryUrlSet = loadNoHistoryUrlSet();

  for (const rootName of ['bookmark_bar', 'other', 'synced']) {
    removeExactDuplicates(result.roots[rootName], undefined, removedDuplicates);
    if (rootName !== 'other') {
      removeEmptyFolders(result.roots[rootName], removedEmptyFolders);
    }
  }

  let nextId = maxId(result) + 1;
  const nextIdRef = { value: nextId };
  const archiveRoot = createFolder('历史无访问记录', nextIdRef.value++);
  const archivedNoHistory = extractArchivedUrls(
    result.roots.bookmark_bar,
    noHistoryUrlSet,
    archiveRoot,
    nextIdRef,
  );
  removeEmptyFolders(result.roots.bookmark_bar, removedEmptyFolders);
  nextId = nextIdRef.value;
  const oldTop = result.roots.bookmark_bar.children || [];
  const oldFolders = new Map();
  const directUrls = [];
  for (const child of oldTop) {
    if (child.type === 'folder') oldFolders.set(child.name, child);
    else directUrls.push(child);
  }

  const groupNodes = new Map();
  const newTop = GROUPS.map((group) => {
    const folder = createFolder(group.name, nextId++);
    groupNodes.set(group.name, folder);
    return folder;
  });

  for (const group of GROUPS) {
    const groupFolder = groupNodes.get(group.name);
    for (const folderName of group.topLevelFolders) {
      const folder = oldFolders.get(folderName);
      if (folder) {
        groupFolder.children.push(folder);
        oldFolders.delete(folderName);
      }
    }
  }

  const unmatched = groupNodes.get('99_待整理');
  for (const folder of oldFolders.values()) {
    unmatched.children.push(folder);
  }

  for (const urlNode of directUrls) {
    const rule = DIRECT_URL_RULES.find((item) => item.match(urlNode));
    const targetGroup = groupNodes.get(rule?.group || '99_待整理');
    if (rule?.nestedPath) {
      const nested = findFolder(targetGroup, rule.nestedPath);
      if (nested) {
        nested.children.push(urlNode);
        continue;
      }
    }
    targetGroup.children.push(urlNode);
  }

  if ((archiveRoot.children || []).length > 0) {
    const archiveGroup = createFolder('99_归档', nextId++);
    archiveGroup.children.push(archiveRoot);
    newTop.push(archiveGroup);
  }

  result.roots.bookmark_bar.children = newTop.filter((folder) => (folder.children || []).length > 0);
  result.roots.bookmark_bar.date_modified = chromeInternalNow();
  result.checksum = checksumBookmarks(result);

  return {
    bookmarks: result,
    before,
    after: countStats(result),
    removedDuplicates,
    removedEmptyFolders,
    archivedNoHistory,
  };
}

function writeReport({ before, after, removedDuplicates, removedEmptyFolders, archivedNoHistory, outputPath }) {
  const lines = [];
  lines.push('# Chrome Bookmark Cleanup Report');
  lines.push('');
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push(`- URLs: ${before.urls} -> ${after.urls}`);
  lines.push(`- Folders: ${before.folders} -> ${after.folders}`);
  lines.push(`- Empty folders: ${before.emptyFolders} -> ${after.emptyFolders}`);
  lines.push(`- Exact duplicate URL entries removed: ${removedDuplicates.length}`);
  lines.push(`- Moved to archive/no-history: ${archivedNoHistory}`);
  lines.push(`- Organized preview: ${outputPath}`);
  lines.push('');
  lines.push('## New Bookmark Bar Tree');
  lines.push('');
  lines.push('```text');
  const preview = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
  lines.push(...treeLines(preview.roots.bookmark_bar, 0, 4));
  lines.push('```');
  lines.push('');
  lines.push('## Removed Duplicates');
  lines.push('');
  if (removedDuplicates.length === 0) {
    lines.push('None.');
  } else {
    for (const item of removedDuplicates) {
      lines.push(`- ${item.name}: ${item.url}`);
    }
  }
  lines.push('');
  lines.push('## Removed Empty Folders');
  lines.push('');
  if (removedEmptyFolders.length === 0) {
    lines.push('None.');
  } else {
    for (const name of removedEmptyFolders) lines.push(`- ${name}`);
  }
  lines.push('');
  lines.push('## Top Domains After Cleanup');
  lines.push('');
  for (const [host, count] of after.topDomains) {
    lines.push(`- ${host}: ${count}`);
  }
  fs.writeFileSync(path.join(outputDir, 'report.md'), `${lines.join('\n')}\n`);
}

function main() {
  fs.mkdirSync(outputDir, { recursive: true });
  const source = JSON.parse(fs.readFileSync(chromeBookmarksPath, 'utf8'));
  const currentChecksum = checksumBookmarks(source);
  if (source.checksum !== currentChecksum) {
    throw new Error(`Current bookmark checksum mismatch: stored=${source.checksum} computed=${currentChecksum}`);
  }

  const organized = reorganize(source);
  const outputPath = path.join(outputDir, 'Bookmarks.organized.json');
  fs.writeFileSync(outputPath, `${JSON.stringify(organized.bookmarks, null, 3)}\n`);
  const planPath = path.join(outputDir, 'bookmark_plan.json');
  fs.writeFileSync(planPath, `${JSON.stringify(buildExtensionPlan(organized.bookmarks), null, 2)}\n`);

  const verify = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
  const outputChecksum = checksumBookmarks(verify);
  if (verify.checksum !== outputChecksum) {
    throw new Error(`Organized bookmark checksum mismatch: stored=${verify.checksum} computed=${outputChecksum}`);
  }

  writeReport({ ...organized, outputPath });
  console.log(JSON.stringify({
    source: chromeBookmarksPath,
    output: outputPath,
    plan: planPath,
    report: path.join(outputDir, 'report.md'),
    before: organized.before,
    after: organized.after,
    removedDuplicates: organized.removedDuplicates.length,
    removedEmptyFolders: organized.removedEmptyFolders.length,
    checksum: verify.checksum,
  }, null, 2));
}

main();
