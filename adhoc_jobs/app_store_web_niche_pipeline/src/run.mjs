import { spawn } from "node:child_process";
import { parseArgs } from "./lib.mjs";

const args = parseArgs();
const forwarded = Object.entries(args).flatMap(([key, value]) => (value === true ? [`--${key}`] : [`--${key}`, String(value)]));

async function run(script) {
  await new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [new URL(script, import.meta.url).pathname, ...forwarded], { stdio: "inherit" });
    child.on("error", reject);
    child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`${script} exited with ${code}`))));
  });
}

for (const script of ["./collect.mjs", "./enrich.mjs", "./analyze.mjs", "./report.mjs"]) await run(script);

