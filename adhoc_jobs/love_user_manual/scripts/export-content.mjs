import { writeFile } from 'node:fs/promises';
import { posts } from '../src/data/posts.js';
import { axes, questions } from '../src/data/questions.js';
import { resultTypes } from '../src/data/results.js';

const sections = posts.map((post) => {
  const slides = post.slides.map((slide, index) => `### 第 ${index + 1} 页\n\n${slide.join('  \n')}`).join('\n\n');
  return `## ${post.id}｜${post.title}

- 封面：${post.cover.join('｜')}
- 标题公式：${post.formula}
- 话题：${post.tags.map((tag) => `#${tag}`).join(' ')}
${post.preflight ? `- 发布前确认：${post.preflight}` : ''}

${slides}

### 正文

${post.body}`;
}).join('\n\n---\n\n');

const document = `# 「关系说明书」小红书 10 篇发布稿 v0.2

生成日期：2026-07-22  
单一内容源：\`src/data/posts.js\`

发布前约束：

- 第 5 篇的第一人称经历必须由实际出镜者改成自己的真实经历。
- 第 2 篇只有在网页、免费结果和保存分享卡均可使用后发布。
- 所有稿件发布当天再检查平台规则和 AI 内容标识要求。

${sections}
`;

await writeFile(new URL('../content/xhs_posts_v02.md', import.meta.url), document, 'utf8');

const questionnaire = `# 关系说明书题库 v0.2

生成日期：2026-07-22  
单一内容源：\`src/data/questions.js\`

四个观察方向：

${Object.values(axes).map((axis) => `- ${axis.name}：${axis.left} — ${axis.right}`).join('\n')}

${questions.map((question, index) => `## ${String(index + 1).padStart(2, '0')}｜${question.scene}

**${question.prompt}**

${question.options.map((option) => `- ${option.label}`).join('\n')}`).join('\n\n')}

计分说明：每题五个选项从左端到右端依次记为 0、25、50、75、100；每个方向取六题平均值。分数只表示本问卷选项中的相对位置，不是常模分数。
`;

const resultLibrary = `# 关系说明书结果库 v0.2

生成日期：2026-07-22  
单一内容源：\`src/data/results.js\`

结果名取四个方向中离中点最远的一端。结果名只是阅读入口，完整报告仍展示四个连续分数。

${Object.values(resultTypes).map((result) => `## ${result.name}

${result.lead}

- 已有能力：${result.strength}
- 容易卡住：${result.friction}
- 对你有用：${result.helpful}
- 可以直接说：“${result.request}”
- 本周练习：${result.practice}`).join('\n\n')}
`;

await Promise.all([
  writeFile(new URL('../content/questionnaire_v02.md', import.meta.url), questionnaire, 'utf8'),
  writeFile(new URL('../content/result_library_v02.md', import.meta.url), resultLibrary, 'utf8'),
]);

console.log(`exported ${posts.length} posts, ${questions.length} questions and ${Object.keys(resultTypes).length} results`);
