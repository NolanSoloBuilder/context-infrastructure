import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const outDir = path.resolve("adhoc_jobs/code_s_plan_ppt_test");
const previewDir = path.join(outDir, "preview");
const pptxPath = path.join(outDir, "forgepane_mcp_plan_input.pptx");

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addTitle(slide, title, kicker = "FORGEPANE MCP") {
  const kickerBox = slide.shapes.add({
    geometry: "textbox",
    position: { left: 72, top: 56, width: 420, height: 28 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  kickerBox.text = kicker;
  kickerBox.text.style = { fontSize: 13, bold: true, color: "slate-500" };

  const titleBox = slide.shapes.add({
    geometry: "textbox",
    position: { left: 72, top: 100, width: 840, height: 72 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  titleBox.text = title;
  titleBox.text.style = { fontSize: 38, bold: true, color: "slate-950" };
}

function addBullets(slide, bullets, left = 96, top = 210, width = 950) {
  bullets.forEach((text, index) => {
    const y = top + index * 82;
    const dot = slide.shapes.add({
      geometry: "ellipse",
      position: { left, top: y + 10, width: 16, height: 16 },
      fill: index === 0 ? "#0f766e" : "#475569",
      line: { style: "solid", fill: "none", width: 0 },
    });
    const box = slide.shapes.add({
      geometry: "textbox",
      position: { left: left + 34, top: y, width, height: 56 },
      fill: "none",
      line: { style: "solid", fill: "none", width: 0 },
    });
    box.text = text;
    box.text.style = { fontSize: 22, color: "slate-700" };
  });
}

function addFooter(slide, text = "Source: ForgePane local MCP rollout notes, 2026-06-19") {
  const footer = slide.shapes.add({
    geometry: "textbox",
    position: { left: 72, top: 668, width: 900, height: 24 },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  footer.text = text;
  footer.text.style = { fontSize: 11, color: "slate-400" };
}

async function main() {
  await fs.mkdir(previewDir, { recursive: true });

  const presentation = Presentation.create({
    slideSize: { width: 1280, height: 720 },
  });

  const slides = [
    {
      title: "Test Goal",
      bullets: [
        "Verify whether a delegated agent can turn a PPT into a plan-style execution brief.",
        "Use a tiny ForgePane MCP rollout deck as the source of truth.",
        "Require concrete phases, risks, validation steps, and open questions.",
      ],
    },
    {
      title: "Implementation Phases",
      bullets: [
        "Phase 1: keep the public smoke endpoint minimal and non-sensitive.",
        "Phase 2: use DevSpace Read for search and fetch only, with OAuth owner approval.",
        "Phase 3: keep shell-capable DevSpace behind strong authentication and limited roots.",
      ],
    },
    {
      title: "Risk Controls",
      bullets: [
        "Do not expose write, edit, or bash tools without an explicit private access layer.",
        "Prefer server logs and visible ChatGPT tool-call rows over app chip status text.",
        "Record every public hostname, LaunchAgent, and verification command in repo docs.",
      ],
    },
    {
      title: "Acceptance Criteria",
      bullets: [
        "The smoke tool returns ok=true, service=forgepane-mcp-smoke, domain=forgepane.com.",
        "The plan lists ordered steps, owners, verification checks, and rollback notes.",
        "The final answer must mention any assumptions and avoid claiming unverified work.",
      ],
    },
  ];

  for (const item of slides) {
    const slide = presentation.slides.add();
    slide.background.fill = "#f8fafc";
    slide.shapes.add({
      geometry: "rect",
      position: { left: 0, top: 0, width: 24, height: 720 },
      fill: "#0f766e",
      line: { style: "solid", fill: "none", width: 0 },
    });
    addTitle(slide, item.title);
    addBullets(slide, item.bullets);
    addFooter(slide);
  }

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(previewDir, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(path.join(previewDir, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }

  await writeBlob(path.join(previewDir, "montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));
  await (await PresentationFile.exportPptx(presentation)).save(pptxPath);
  console.log(pptxPath);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
