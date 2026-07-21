#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const workspaceRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const manifestPath = join(workspaceRoot, "rules/skills/global_skill_snapshots.json");
const manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
const packages = [];

for (const skill of manifest.skills ?? []) {
  for (const relativePackage of skill.dependencyPackages ?? []) {
    const packageRoot = join(workspaceRoot, ".agents/skills", skill.name, relativePackage);
    if (!existsSync(join(packageRoot, "package-lock.json"))) {
      console.error(`ERROR 缺少 package-lock.json：${packageRoot}`);
      process.exit(1);
    }
    packages.push({ skill: skill.name, packageRoot });
  }
}

for (const { skill, packageRoot } of packages) {
  console.log(`INSTALL ${skill} dependencies`);
  const result = spawnSync("npm", ["ci", "--no-audit", "--no-fund"], {
    cwd: packageRoot,
    stdio: "inherit",
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

for (const [script, args] of [
  ["tools/vendor_global_codex_skills.mjs", ["verify"]],
  ["tools/external_skills_registry.mjs", ["verify"]],
]) {
  const result = spawnSync("node", [join(workspaceRoot, script), ...args], {
    cwd: workspaceRoot,
    stdio: "inherit",
  });
  if (result.status !== 0) process.exit(result.status ?? 1);
}

console.log(`OK 项目 Skill 已就绪；安装了 ${packages.length} 组 npm 依赖`);
