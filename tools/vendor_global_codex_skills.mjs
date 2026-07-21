#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  readlinkSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const workspaceRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const projectSkillsRoot = join(workspaceRoot, ".agents/skills");
const claudeSkillsRoot = join(workspaceRoot, ".claude/skills");
const projectLockPath = join(workspaceRoot, "skills-lock.json");
const snapshotPath = join(workspaceRoot, "rules/skills/global_skill_snapshots.json");
const selectionPath = join(workspaceRoot, "rules/skills/project_global_skill_selection.json");
const globalLockPath = join(process.env.HOME ?? "", ".agents/.skill-lock.json");
const excludedNames = new Set([".git", "node_modules", ".DS_Store", "__pycache__"]);
const captureDate = new Date().toISOString().slice(0, 10);

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function globalCodexSkills() {
  const output = execFileSync("npx", ["-y", "skills", "list", "-g", "--json"], {
    cwd: workspaceRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "inherit"],
  });
  return JSON.parse(output)
    .filter((entry) => entry.agents?.includes("Codex"))
    .sort((left, right) => left.name.localeCompare(right.name));
}

function assertSafeName(name) {
  if (!/^[a-z0-9][a-z0-9._-]*$/i.test(name)) throw new Error(`不安全的 Skill 名称：${name}`);
}

function isExcluded(source) {
  return source.split(sep).some((part) => excludedNames.has(part));
}

function walkFiles(root, current = root, exclusions = excludedNames) {
  const files = [];
  for (const entry of readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if (exclusions.has(entry.name)) continue;
    const absolute = join(current, entry.name);
    if (entry.isDirectory()) files.push(...walkFiles(root, absolute, exclusions));
    else if (entry.isFile()) files.push(absolute);
  }
  return files;
}

function directoryHash(root, exclusions = excludedNames) {
  const hash = createHash("sha256");
  for (const file of walkFiles(root, root, exclusions)) {
    const stat = lstatSync(file);
    hash.update(relative(root, file));
    hash.update("\0");
    hash.update(String(stat.mode & 0o777));
    hash.update("\0");
    hash.update(readFileSync(file));
    hash.update("\0");
  }
  return hash.digest("hex");
}

function matchesRecordedHash(root, recordedHash) {
  if (directoryHash(root) === recordedHash) return true;
  const legacyExclusions = new Set([".git", "node_modules", ".DS_Store"]);
  return directoryHash(root, legacyExclusions) === recordedHash;
}

function dependencyPackages(root) {
  return walkFiles(root)
    .filter((file) => file.endsWith(`${sep}package-lock.json`))
    .map((file) => relative(root, dirname(file)) || ".")
    .sort();
}

function displayPath(path) {
  const home = process.env.HOME;
  return home && path.startsWith(`${home}${sep}`) ? `~/${relative(home, path)}` : path;
}

function gitMetadata(path) {
  if (!existsSync(join(path, ".git"))) return {};
  try {
    const repositoryUrl = execFileSync("git", ["-C", path, "remote", "get-url", "origin"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const revision = execFileSync("git", ["-C", path, "rev-parse", "HEAD"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    return { repositoryUrl, revision };
  } catch {
    return {};
  }
}

function ensureClaudeLink(name, destination) {
  mkdirSync(claudeSkillsRoot, { recursive: true });
  const link = join(claudeSkillsRoot, name);
  const target = relative(dirname(link), destination);
  if (existsSync(link) || lstatSafe(link)) {
    const stat = lstatSync(link);
    if (!stat.isSymbolicLink()) throw new Error(`Claude Skill 路径不是软链接，拒绝覆盖：${link}`);
    if (readlinkSync(link) === target) return;
    rmSync(link);
  }
  symlinkSync(target, link);
}

function lstatSafe(path) {
  try {
    return lstatSync(path);
  } catch {
    return null;
  }
}

function loadGlobalLock() {
  return existsSync(globalLockPath) ? readJson(globalLockPath).skills ?? {} : {};
}

function capture() {
  const projectLock = readJson(projectLockPath);
  const managedNames = new Set(Object.keys(projectLock.skills ?? {}));
  const globalLock = loadGlobalLock();
  const availableEntries = new Map(globalCodexSkills().map((entry) => [entry.name, entry]));
  const selection = readJson(selectionPath);
  const previousManifest = existsSync(snapshotPath) ? readJson(snapshotPath) : { skills: [] };
  const previousSnapshots = new Map((previousManifest.skills ?? []).map((skill) => [skill.name, skill]));
  const selectedNames = new Set();
  const entries = selection.skills.map((selected) => {
    if (selectedNames.has(selected.name)) throw new Error(`白名单中存在重复 Skill：${selected.name}`);
    selectedNames.add(selected.name);
    const entry = availableEntries.get(selected.name);
    if (!entry) throw new Error(`白名单 Skill 当前不在全局 Codex 列表中：${selected.name}`);
    return { ...entry, category: selected.category, reason: selected.reason };
  });
  const snapshots = [];

  mkdirSync(projectSkillsRoot, { recursive: true });
  for (const previous of previousSnapshots.values()) {
    if (selectedNames.has(previous.name)) continue;
    assertSafeName(previous.name);
    if (managedNames.has(previous.name)) throw new Error(`拒绝清理 lock-managed Skill：${previous.name}`);
    const destination = join(projectSkillsRoot, previous.name);
    if (existsSync(destination)) {
      if (!matchesRecordedHash(destination, previous.contentHash)) {
        throw new Error(`快照 ${previous.name} 存在未登记修改，拒绝自动清理`);
      }
      rmSync(destination, { recursive: true, force: true });
    }
    const link = join(claudeSkillsRoot, previous.name);
    const linkStat = lstatSafe(link);
    if (linkStat) {
      const expectedTarget = relative(dirname(link), destination);
      if (!linkStat.isSymbolicLink() || readlinkSync(link) !== expectedTarget) {
        throw new Error(`快照 ${previous.name} 的 Claude 路径不受 manifest 管理，拒绝清理`);
      }
      rmSync(link);
    }
  }

  for (const entry of entries) {
    assertSafeName(entry.name);
    if (managedNames.has(entry.name)) throw new Error(`全局 Skill 与项目 lock-managed Skill 重名：${entry.name}`);
    if (!existsSync(join(entry.path, "SKILL.md"))) throw new Error(`全局 Skill 缺少 SKILL.md：${entry.path}`);

    const destination = join(projectSkillsRoot, entry.name);
    const expectedPrefix = `${projectSkillsRoot}${sep}`;
    if (!destination.startsWith(expectedPrefix)) throw new Error(`拒绝写入项目 Skill 目录之外：${destination}`);
    if (existsSync(destination)) {
      const previous = previousSnapshots.get(entry.name);
      if (!previous) throw new Error(`项目 Skill 已存在但不在上一版快照中，拒绝覆盖：${entry.name}`);
      if (!matchesRecordedHash(destination, previous.contentHash)) {
        throw new Error(`快照 ${entry.name} 存在未登记修改，拒绝覆盖`);
      }
      rmSync(destination, { recursive: true, force: true });
    }
    cpSync(entry.path, destination, {
      recursive: true,
      dereference: true,
      preserveTimestamps: true,
      filter: (source) => !isExcluded(relative(entry.path, source)),
    });
    ensureClaudeLink(entry.name, destination);

    const provenance = globalLock[entry.name] ?? {};
    snapshots.push({
      name: entry.name,
      category: entry.category,
      reason: entry.reason,
      originalPath: displayPath(entry.path),
      capturedAt: captureDate,
      contentHash: directoryHash(destination),
      dependencyPackages: dependencyPackages(destination),
      source: provenance.source ?? null,
      sourceType: provenance.sourceType ?? (gitMetadata(entry.path).repositoryUrl ? "git-snapshot" : "local-snapshot"),
      sourceUrl: provenance.sourceUrl ?? gitMetadata(entry.path).repositoryUrl ?? null,
      sourceRevision: gitMetadata(entry.path).revision ?? null,
      sourceSkillPath: provenance.skillPath ?? null,
      globalInstalledAt: provenance.installedAt ?? null,
      globalUpdatedAt: provenance.updatedAt ?? null,
    });
  }

  writeFileSync(
    snapshotPath,
    `${JSON.stringify({
      schemaVersion: 1,
      capturedAt: captureDate,
      selection: "Explicit project allowlist from rules/skills/project_global_skill_selection.json",
      selectionPolicy: selection.policy,
      explicitExclusions: selection.explicitExclusions,
      exclusions: [...excludedNames],
      skills: snapshots,
    }, null, 2)}\n`,
  );
  console.log(`WROTE ${snapshots.length} 个全局 Codex Skill 快照`);
}

function verify() {
  const manifest = readJson(snapshotPath);
  const errors = [];
  for (const skill of manifest.skills ?? []) {
    const destination = join(projectSkillsRoot, skill.name);
    if (!existsSync(join(destination, "SKILL.md"))) {
      errors.push(`${skill.name} 缺少项目 SKILL.md`);
      continue;
    }
    const actualHash = directoryHash(destination);
    if (actualHash !== skill.contentHash) errors.push(`${skill.name} 内容哈希不一致`);
    const link = join(claudeSkillsRoot, skill.name);
    if (!lstatSafe(link)?.isSymbolicLink()) errors.push(`${skill.name} 缺少 Claude 项目软链接`);
  }
  if (errors.length > 0) {
    for (const error of errors) console.error(`ERROR ${error}`);
    process.exitCode = 1;
  } else {
    console.log(`OK ${manifest.skills.length} 个全局 Codex Skill 快照一致`);
  }
}

const command = process.argv[2] ?? "verify";
if (command === "sync") capture();
else if (command === "verify") verify();
else {
  console.error("Usage: node tools/vendor_global_codex_skills.mjs [sync|verify]");
  process.exitCode = 1;
}
