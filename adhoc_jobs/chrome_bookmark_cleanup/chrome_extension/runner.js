const TARGET_TOP_LEVEL = [
  '00_常用入口',
  '01_小红书工作',
  '02_AI与个人项目',
  '03_研发与效率工具',
  '04_学习与资料',
  '05_个人生活',
  '99_归档',
];

const FALLBACK_PATH = ['99_待整理', '同步新增'];

function setStatus(message) {
  const el = document.getElementById('status');
  if (el) el.textContent = typeof message === 'string' ? message : JSON.stringify(message, null, 2);
}

function api(method, ...args) {
  return new Promise((resolve, reject) => {
    chrome.bookmarks[method](...args, (result) => {
      const error = chrome.runtime.lastError;
      if (error) reject(new Error(error.message));
      else resolve(result);
    });
  });
}

async function loadPlan() {
  const input = document.getElementById('plan-file');
  const file = input?.files?.[0];
  if (!file) throw new Error('Select bookmark_plan.json before running.');

  const plan = JSON.parse(await file.text());
  if (!Array.isArray(plan.folders) || !Array.isArray(plan.urls)) {
    throw new Error('Invalid bookmark plan: folders and urls must be arrays.');
  }
  return plan;
}

async function getBookmarkBar() {
  const tree = await api('getTree');
  const root = tree[0];
  const byId = (root.children || []).find((node) => node.id === '1');
  if (byId) return byId;
  const firstFolder = (root.children || []).find((node) => node.children);
  if (!firstFolder) throw new Error('Bookmark bar folder not found');
  return firstFolder;
}

function pathKey(path) {
  return path.join('\u0000');
}

async function childrenOf(folderId) {
  return api('getChildren', folderId);
}

async function ensureFolder(parentId, title) {
  const children = await childrenOf(parentId);
  const existing = children.find((node) => !node.url && node.title === title);
  if (existing) return existing;
  return api('create', { parentId, title });
}

async function ensurePath(bookmarkBarId, path) {
  let parentId = bookmarkBarId;
  let current = null;
  for (const title of path) {
    current = await ensureFolder(parentId, title);
    parentId = current.id;
  }
  return current || { id: bookmarkBarId };
}

function walk(node, visit, ancestors = []) {
  visit(node, ancestors);
  for (const child of node.children || []) {
    walk(child, visit, [...ancestors, node]);
  }
}

async function collectBookmarkBarNodes(bookmarkBarId) {
  const [bar] = await api('getSubTree', bookmarkBarId);
  const byUrl = new Map();
  const folders = [];
  const urls = [];
  walk(bar, (node) => {
    if (node.id === bar.id) return;
    if (node.url) {
      urls.push(node);
      const bucket = byUrl.get(node.url) || [];
      bucket.push(node);
      byUrl.set(node.url, bucket);
    } else {
      folders.push(node);
    }
  });
  return { bar, byUrl, folders, urls };
}

async function moveUrlToPlanTarget(node, target, parentId, index) {
  if (node.parentId !== parentId || node.index !== index) {
    await api('move', node.id, { parentId, index });
  }
  if (node.title !== target.title) {
    await api('update', node.id, { title: target.title });
  }
}

async function removeEmptyFolders(bookmarkBarId, desiredFolderKeys) {
  let removed = 0;
  let changed = true;
  while (changed) {
    changed = false;
    const { folders } = await collectBookmarkBarNodes(bookmarkBarId);
    const sorted = folders.sort((a, b) => (b.parentId === a.id ? -1 : 0));
    for (const folder of sorted) {
      const children = await childrenOf(folder.id);
      if (children.length > 0) continue;
      const path = await folderPath(folder.id, bookmarkBarId);
      if (desiredFolderKeys.has(pathKey(path))) continue;
      await api('removeTree', folder.id);
      removed += 1;
      changed = true;
    }
  }
  return removed;
}

async function folderPath(folderId, bookmarkBarId) {
  const path = [];
  let [node] = await api('get', folderId);
  while (node && node.id !== bookmarkBarId) {
    path.unshift(node.title);
    if (!node.parentId) break;
    [node] = await api('get', node.parentId);
  }
  return path;
}

async function moveTopLevelFolders(bookmarkBarId) {
  let index = 0;
  for (const title of TARGET_TOP_LEVEL) {
    const children = await childrenOf(bookmarkBarId);
    const folder = children.find((node) => !node.url && node.title === title);
    if (folder) {
      await api('move', folder.id, { parentId: bookmarkBarId, index });
      index += 1;
    }
  }
  const children = await childrenOf(bookmarkBarId);
  const fallback = children.find((node) => !node.url && node.title === FALLBACK_PATH[0]);
  if (fallback) await api('move', fallback.id, { parentId: bookmarkBarId, index });
}

async function run() {
  setStatus('Loading plan...');
  const startedAt = new Date().toISOString();
  const plan = await loadPlan();
  const bookmarkBar = await getBookmarkBar();
  const bookmarkBarId = bookmarkBar.id;

  setStatus(`Preparing folders for ${plan.urls.length} planned bookmarks...`);
  const desiredFolderKeys = new Set(plan.folders.map((folder) => pathKey(folder.path)));
  for (const folder of plan.folders) {
    await ensurePath(bookmarkBarId, folder.path);
  }

  const targetParentIds = new Map();
  for (const item of plan.urls) {
    const key = pathKey(item.parentPath);
    if (!targetParentIds.has(key)) {
      const folder = await ensurePath(bookmarkBarId, item.parentPath);
      targetParentIds.set(key, folder.id);
    }
  }

  let { byUrl, urls: originalUrls } = await collectBookmarkBarNodes(bookmarkBarId);
  const usedNodeIds = new Set();
  const plannedUrlSet = new Set(plan.urls.map((item) => item.url));
  let moved = 0;
  let updated = 0;
  let missing = 0;

  setStatus('Moving bookmarks through chrome.bookmarks API...');
  const parentCounters = new Map();
  for (const target of plan.urls) {
    const parentId = targetParentIds.get(pathKey(target.parentPath));
    const index = parentCounters.get(parentId) || 0;
    parentCounters.set(parentId, index + 1);

    const candidates = byUrl.get(target.url) || [];
    const node = candidates.find((candidate) => !usedNodeIds.has(candidate.id));
    if (!node) {
      missing += 1;
      continue;
    }
    const oldParent = node.parentId;
    const oldTitle = node.title;
    await moveUrlToPlanTarget(node, target, parentId, index);
    usedNodeIds.add(node.id);
    if (oldParent !== parentId) moved += 1;
    if (oldTitle !== target.title) updated += 1;
  }

  setStatus('Removing duplicates and moving unknown synced bookmarks...');
  let removedDuplicates = 0;
  let movedUnknown = 0;
  const fallbackFolder = await ensurePath(bookmarkBarId, FALLBACK_PATH);
  const latest = await collectBookmarkBarNodes(bookmarkBarId);
  for (const node of latest.urls) {
    if (usedNodeIds.has(node.id)) continue;
    if (plannedUrlSet.has(node.url)) {
      await api('remove', node.id);
      removedDuplicates += 1;
    } else {
      await api('move', node.id, { parentId: fallbackFolder.id });
      movedUnknown += 1;
    }
  }

  setStatus('Cleaning empty folders and ordering top-level folders...');
  const removedEmptyFolders = await removeEmptyFolders(bookmarkBarId, desiredFolderKeys);
  await moveTopLevelFolders(bookmarkBarId);

  const finalTree = await collectBookmarkBarNodes(bookmarkBarId);
  const result = {
    startedAt,
    finishedAt: new Date().toISOString(),
    plannedUrls: plan.urls.length,
    originalUrls: originalUrls.length,
    finalUrls: finalTree.urls.length,
    moved,
    updated,
    missing,
    removedDuplicates,
    movedUnknown,
    removedEmptyFolders,
    topLevel: (await childrenOf(bookmarkBarId)).map((node) => ({
      title: node.title,
      type: node.url ? 'url' : 'folder',
    })),
  };
  await chrome.storage.local.set({ lastResult: result });
  setStatus(result);
  console.info('Codex Bookmark Organizer result', result);
}

document.getElementById('run')?.addEventListener('click', () => {
  run().catch(async (error) => {
    const result = {
      failedAt: new Date().toISOString(),
      error: error && error.stack ? error.stack : String(error),
    };
    await chrome.storage.local.set({ lastResult: result });
    setStatus(result);
    console.error('Codex Bookmark Organizer failed', error);
  });
});
