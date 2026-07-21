#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { existsSync, lstatSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const workspaceRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const registryPath = join(workspaceRoot, "rules/skills/external_skills_registry.json");
const indexPath = join(workspaceRoot, "rules/skills/EXTERNAL_SKILLS.md");

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function loadState() {
  const registry = readJson(registryPath);
  const lockPath = join(workspaceRoot, registry.lockFile);
  const lock = readJson(lockPath);
  const snapshots = readJson(join(workspaceRoot, registry.snapshotsFile));
  const sourceMetadata = new Map(registry.sources.map((source) => [source.source, source]));
  const skillsBySource = new Map();

  for (const [name, skill] of Object.entries(lock.skills ?? {})) {
    const skills = skillsBySource.get(skill.source) ?? [];
    skills.push({ name, ...skill });
    skillsBySource.set(skill.source, skills);
  }

  for (const skills of skillsBySource.values()) {
    skills.sort((left, right) => left.name.localeCompare(right.name));
  }

  return { registry, lock, snapshots, sourceMetadata, skillsBySource };
}

function snapshotFiles(root, current = root) {
  const files = [];
  for (const entry of readdirSync(current, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
    if ([".git", "node_modules", ".DS_Store", "__pycache__"].includes(entry.name)) continue;
    const absolute = join(current, entry.name);
    if (entry.isDirectory()) files.push(...snapshotFiles(root, absolute));
    else if (entry.isFile()) files.push(absolute);
  }
  return files;
}

function snapshotHash(root) {
  const hash = createHash("sha256");
  for (const file of snapshotFiles(root)) {
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

function validate(state) {
  const errors = [];
  const { registry, lock, snapshots, sourceMetadata, skillsBySource } = state;

  if (registry.schemaVersion !== 1) errors.push("不支持的 registry schemaVersion");
  if (lock.version !== 1) errors.push("不支持的 skills-lock.json version");
  if (snapshots.schemaVersion !== 1) errors.push("不支持的 global_skill_snapshots.json schemaVersion");
  if (sourceMetadata.size !== registry.sources.length) errors.push("registry 中存在重复 source");

  for (const source of skillsBySource.keys()) {
    if (!sourceMetadata.has(source)) errors.push(`lock 中的来源未登记：${source}`);
  }
  for (const source of sourceMetadata.keys()) {
    if (!skillsBySource.has(source)) errors.push(`registry 中的来源没有已安装 Skill：${source}`);
  }

  for (const [name, skill] of Object.entries(lock.skills ?? {})) {
    if (skill.sourceType !== "github") errors.push(`${name} 的 sourceType 不是 github`);
    if (!/^[a-f0-9]{64}$/.test(skill.computedHash ?? "")) errors.push(`${name} 缺少有效 computedHash`);
    const localSkill = join(workspaceRoot, registry.installedRoot, name, "SKILL.md");
    if (!existsSync(localSkill)) errors.push(`${name} 的本地 SKILL.md 不存在：${localSkill}`);
  }

  const lockNames = new Set(Object.keys(lock.skills ?? {}));
  const snapshotNames = new Set();
  for (const skill of snapshots.skills ?? []) {
    if (snapshotNames.has(skill.name)) errors.push(`全局快照中存在重复 Skill：${skill.name}`);
    snapshotNames.add(skill.name);
    if (lockNames.has(skill.name)) errors.push(`全局快照与 lock-managed Skill 重名：${skill.name}`);
    if (!/^[a-f0-9]{64}$/.test(skill.contentHash ?? "")) errors.push(`${skill.name} 缺少有效快照哈希`);
    const localRoot = join(workspaceRoot, registry.installedRoot, skill.name);
    if (!existsSync(join(localRoot, "SKILL.md"))) {
      errors.push(`${skill.name} 的项目快照不存在`);
    } else if (snapshotHash(localRoot) !== skill.contentHash) {
      errors.push(`${skill.name} 的项目快照内容哈希不一致`);
    }
  }

  for (const source of registry.sources) {
    if (!/^[a-f0-9]{40}$/.test(source.recordedRevision ?? "")) {
      errors.push(`${source.source} 缺少有效 recordedRevision`);
    }
  }

  return errors;
}

function escapeTable(value) {
  return String(value ?? "—").replaceAll("|", "\\|");
}

function renderIndex(state) {
  const { registry, lock, snapshots, skillsBySource } = state;
  const managedSkillCount = Object.keys(lock.skills ?? {}).length;
  const snapshotSkillCount = snapshots.skills?.length ?? 0;
  const totalSkills = managedSkillCount + snapshotSkillCount;
  const lines = [
    "# 外部 Skills 注册表",
    "",
    "> 本文件由 `tools/external_skills_registry.mjs sync` 生成。GitHub 安装来源维护在 `external_skills_registry.json` 与 `skills-lock.json`；从用户全局目录精选到项目的快照维护在 `global_skill_snapshots.json`。",
    "",
    `当前项目登记 **${managedSkillCount} 个上游安装 Skill、${snapshotSkillCount} 个精选全局快照，共 ${totalSkills} 个项目级 Skill**。最近对账日期：\`${registry.lastReconciledAt}\`。`,
    "",
    "## 上游来源",
    "",
    "| 来源 | Skill 数 | 版本 | 许可证 | 记录 revision | 最近更新 | 安全记录 |",
    "| --- | ---: | --- | --- | --- | --- | --- |",
  ];

  for (const source of registry.sources) {
    const count = skillsBySource.get(source.source)?.length ?? 0;
    lines.push(
      `| [${source.source}](${source.repositoryUrl}) | ${count} | ${escapeTable(source.version)} | ${escapeTable(source.license)} | \`${source.recordedRevision.slice(0, 12)}\` | ${source.lastUpdatedAt} | ${escapeTable(source.securitySummary)} |`,
    );
  }

  lines.push("", "## 精选全局 Skill 快照", "");
  lines.push("这些 Skill 已复制到仓库内 `.agents/skills/`，迁移后直接以项目级 Skill 生效，不会写回任何全局目录。", "");
  lines.push("| Skill | 分类 | 原全局路径 | 来源 | 快照哈希 | 选择原因 |", "| --- | --- | --- | --- | --- | --- |");
  for (const skill of snapshots.skills ?? []) {
    const source = skill.sourceUrl ? `[${skill.source ?? skill.sourceType}](${skill.sourceUrl})` : skill.sourceType;
    lines.push(`| \`${skill.name}\` | ${skill.category} | \`${skill.originalPath}\` | ${source} | \`${skill.contentHash.slice(0, 12)}\` | ${escapeTable(skill.reason)} |`);
  }
  lines.push("", "明确排除：", "");
  for (const exclusion of snapshots.explicitExclusions ?? []) lines.push(`- ${exclusion}`);

  lines.push("", "## 已安装 Skill", "");
  for (const source of registry.sources) {
    const skills = skillsBySource.get(source.source) ?? [];
    lines.push(`### ${source.source}`, "");
    lines.push(`- 仓库：${source.repositoryUrl}`);
    lines.push(`- 安装日期：\`${source.installedAt}\`；最近更新：\`${source.lastUpdatedAt}\``);
    lines.push(`- 许可证证据：${source.licenseEvidence}`);
    lines.push(`- Skills（${skills.length}）：${skills.map((skill) => `\`${skill.name}\``).join("、")}`);
    for (const note of source.notes ?? []) lines.push(`- 备注：${note}`);
    lines.push("");
  }

  lines.push(
    "## 对账与更新",
    "",
    "只读检查本地注册表、安装目录、锁文件和生成索引是否一致：",
    "",
    "```bash",
    "node tools/external_skills_registry.mjs verify",
    "```",
    "",
    "只读比较 GitHub 当前 revision，发现哪些上游有更新：",
    "",
    "```bash",
    "node tools/external_skills_registry.mjs check-updates",
    "```",
    "",
    "确认需要升级后，显式更新当前项目：",
    "",
    "```bash",
    "npx -y skills update --project -y",
    "```",
    "",
    "更新完成后，审查文件变化与安全提示，再修改 `external_skills_registry.json` 中对应来源的 `recordedRevision`、`version`、`lastUpdatedAt` 和风险备注，最后执行：",
    "",
    "```bash",
    "node tools/external_skills_registry.mjs sync",
    "node tools/external_skills_registry.mjs verify",
    "```",
    "",
    "> 当前 CLI 没有只读的 `skills check`。不要把 `npx skills check` 当作 dry-run；2026-07-21 的实测会直接刷新全部项目 Skill。",
    "",
    "精选全局快照只在需要吸收本机新版时执行增量同步：",
    "",
    "```bash",
    "node tools/vendor_global_codex_skills.mjs sync",
    "node tools/external_skills_registry.mjs sync",
    "node tools/external_skills_registry.mjs verify",
    "```",
    "",
    "新电脑克隆仓库后，Skill 文件已经位于项目目录；如清单中存在 npm 依赖，再执行 `node tools/bootstrap_project_skills.mjs`。该命令不会安装全局 Skill。",
    "",
    "## 新增外部 Skill 的登记要求",
    "",
    "1. 使用项目级安装，不带 `-g`，并确认 `skills-lock.json` 写入来源、路径和哈希。",
    "2. 在 `external_skills_registry.json` 登记上游仓库、默认分支、revision、版本、许可证证据、安装日期和安全备注。",
    "3. 执行 `sync` 生成本索引，再执行 `verify`，确保每个外部 Skill 都能追溯到上游来源。",
    "4. 许可证缺失、自动扫描高风险或包含可执行脚本时，必须在登记记录中明确写出，不能只保留安装成功状态。",
  );

  return `${lines.join("\n")}\n`;
}

function verify(state) {
  const errors = validate(state);
  const expectedIndex = renderIndex(state);
  if (!existsSync(indexPath)) {
    errors.push("缺少生成索引 rules/skills/EXTERNAL_SKILLS.md");
  } else if (readFileSync(indexPath, "utf8") !== expectedIndex) {
    errors.push("EXTERNAL_SKILLS.md 与 registry/lock 不一致；执行 sync 重新生成");
  }

  if (errors.length > 0) {
    for (const error of errors) console.error(`ERROR ${error}`);
    process.exitCode = 1;
    return false;
  }

  const managedCount = Object.keys(state.lock.skills ?? {}).length;
  const snapshotCount = state.snapshots.skills?.length ?? 0;
  console.log(`OK ${managedCount} 个上游安装 Skill，${snapshotCount} 个精选全局快照，共 ${managedCount + snapshotCount} 个项目级 Skill`);
  return true;
}

function checkUpdates(state) {
  if (!verify(state)) return;
  let updates = 0;

  for (const source of state.registry.sources) {
    let remoteRevision;
    try {
      remoteRevision = execFileSync(
        "gh",
        ["api", `repos/${source.source}/commits/${source.defaultBranch}`, "--jq", ".sha"],
        { cwd: workspaceRoot, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] },
      ).trim();
    } catch (error) {
      const detail = error.stderr?.toString().trim() || error.message;
      console.error(`ERROR 无法读取 ${source.source}：${detail}`);
      process.exitCode = 1;
      continue;
    }

    if (remoteRevision === source.recordedRevision) {
      console.log(`CURRENT ${source.source} ${remoteRevision.slice(0, 12)}`);
    } else {
      updates += 1;
      console.log(`UPDATE ${source.source} ${source.recordedRevision.slice(0, 12)} -> ${remoteRevision.slice(0, 12)}`);
    }
  }

  console.log(updates === 0 ? "OK 所有上游 revision 均为当前记录版本" : `INFO ${updates} 个上游存在新 revision`);
}

const command = process.argv[2] ?? "verify";
const state = loadState();

if (command === "sync") {
  const errors = validate(state);
  if (errors.length > 0) {
    for (const error of errors) console.error(`ERROR ${error}`);
    process.exitCode = 1;
  } else {
    writeFileSync(indexPath, renderIndex(state));
    console.log(`WROTE ${indexPath}`);
  }
} else if (command === "verify") {
  verify(state);
} else if (command === "check-updates") {
  checkUpdates(state);
} else {
  console.error("Usage: node tools/external_skills_registry.mjs [verify|check-updates|sync]");
  process.exitCode = 1;
}
