// One-time transformation for the exact Vite snapshot described in README.md.
// Requires the global TypeScript CLI package. No app build or dependencies.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const cp = require("node:child_process");
const ts = require(process.env.TYPESCRIPT_LIB || path.join(cp.execFileSync("npm", ["root", "-g"], {encoding: "utf8"}).trim(), "typescript"));
const dir = path.resolve(process.argv[2] ?? "public", "assets");
const removedRoute = /^\/(?:manual|rename|contact)(?:\/|$)|^\/offline\/pay$/;

function edit(file, callback) {
  const filename = path.join(dir, file);
  const source = fs.readFileSync(filename, "utf8");
  const tree = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const patches = [];
  const cut = (start, end, replacement = "") => patches.push([start, end, replacement]);
  const match = (regex, expected, replacement = "") => {
    const matches = [...source.matchAll(regex)];
    assert.equal(matches.length, expected, `${file}: ${regex}`);
    for (const m of matches) cut(m.index, m.index + m[0].length, replacement);
  };
  const pick = (predicate, expected) => {
    const found = [];
    function visit(node) {
      if (predicate(node, node.getText(tree))) { found.push(node); return; }
      ts.forEachChild(node, visit);
    }
    visit(tree);
    assert.equal(found.length, expected, file + ": unexpected AST match count");
    return found;
  };
  const entries = (predicate, expected) => {
    for (const node of pick((n,t) => n.parent && ts.isArrayLiteralExpression(n.parent) && n.parent.elements.includes(n) && predicate(n,t), expected)) {
      const after = source.slice(node.end).match(/^\s*,/);
      cut(node.getStart(tree), node.end + (after?.[0].length ?? 0));
    }
  };
  callback({match, entries, pick, cut});
  let result = source;
  let boundary = source.length;
  for (const [start, end, value] of patches.sort((a,b)=>b[0]-a[0])) {
    assert.ok(end <= boundary, file + ": overlapping edits");
    result = result.slice(0,start)+value+result.slice(end);
    boundary = start;
  }
  const output = ts.createSourceFile(file,result,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS);
  assert.equal(output.parseDiagnostics.length,0,file + ": invalid patched JS");
  fs.writeFileSync(filename,result);
}
const call = (n) => ts.isCallExpression(n);
const object = (n) => ts.isObjectLiteralExpression(n);

edit("index-GEgtjqXc.js", ({entries}) => {
  entries((n,t) => object(n) && /^\{(?:name:"manual",)?path:"([^"]+)"/.test(t) &&
    removedRoute.test(t.match(/^\{(?:name:"manual",)?path:"([^"]+)"/)[1]), 12);
});
edit("index-CXCZACLn.js", ({entries,match}) => {
  entries((n,t) => call(n) && /^t\("div",\{class:"service-card service-card--(?:manual|rename)"/.test(t),2);
  match(/y\(async\(\)=>\{try\{const r=await w\.get\("\/v1\/packages\/list\?type=manual_rename".*?catch\{\}\}\),/gs,1);
});
edit("index-9P-HFXQs.js", ({entries}) => {
  entries((n,t) => call(n) && t.startsWith('s("div",{class:"list-item",onClick:S}'),1);
});
edit("RelatedServices-DHD8Q25L.js", ({entries}) => {
  entries((n,t) => call(n) && /^e\("div",\{class:"service-btn",onClick:s\[2\]/.test(t),1);
});
edit("UnlockPopup-d_DqVA32.js", ({entries,match}) => {
  entries((n,t) => object(n) && /^\{action:"[^"]+",tag:"(?:大师|人工)起名"/.test(t),2);
  entries((n,t) => call(n) && t.startsWith('t("div",{class:"manual-entry"'),1);
  match(/a==="Y"&&i\("客服优先支持"\),/g,1);
});
edit("index-C4AZAKwy.js", ({entries,match}) => {
  entries((n,t) => object(n) && /^\{question:"(?:如何联系客服|如何开具发票)？"/.test(t),2);
  entries((n,t) => call(n) && t.startsWith('s("div",h,[') && t.includes('没有找到答案'),1);
  match(/\n3\. 联系客服处理|\n\n如因技术问题导致无法正常使用，请联系客服，我们会妥善处理。/g,2);
});
edit("report-C9DHJUc4.js", ({entries}) => {
  entries((n,t) => call(n) && t.startsWith('s("button",{class:"guide-btn outline",onClick:E}'),1);
});
edit("score-yzmNdTRt.js", ({entries}) => {
  entries((n,t) => call(n) && t.length<500 && t.includes('i.$router.push("/manual")'),1);
});
for (const file of ["index-CfRyCSCA.js","index-Czs_4oTz.js","index-DkawjCaP.js","test-BXw1rXOe.js"]) {
  edit(file, ({match}) => match(/<div class="service-card"[^>]*><div class="service-icon"[^>]*>👨‍🏫<\/div><div class="service-info"[^>]*>.*?<\/div><div class="service-tag hot"[^>]*>热门<\/div><\/div>/gs,1));
}
edit("character-library-BwaAqeWc.js", ({match}) => match(/解锁失败，请联系客服/g,1,"解锁失败，请重试"));
edit("report-download-DNPuYz9L.js", ({match}) => match(/请联系客服或重新生成/g,1,"请重新生成"));
// The lazy-loaded result pages import M. Keep the ESM interface with no DOM
// or session storage side effects, preserving their unrelated result logic.
fs.writeFileSync(path.join(dir,"ManualPromoBar-XC0uN0UD.js"),"export const M = { render: () => null };\n");
// Only former route chunks. Keep shared entries and the indexed Vite table.
for (const asset of [
  "index-CUmWDN2N.js","master-detail-5AdJKQx-.js","form-D97oQDsv.js",
  "pay-0Hm2nvyn.js","success-CXDxQLaT.js","index-CTe8ztG9.js",
  "form-DME1fkb4.js","success-K6CSVblH.js","index-DjQo6DUN.js","pay-gNaMR-Yd.js"
]) fs.unlinkSync(path.join(dir,asset));
