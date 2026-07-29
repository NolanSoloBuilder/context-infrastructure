export const profile = {
  name: "Nalon",
  englishName: "Nalon",
  publicName: "Nalon · Builder",
  location: "Beijing, China",
  role: "Engineer · Product Builder",
  headline: "Terminal Dev · Vibe Full-stack · Solo Founder",
  bio: "I build useful products at the intersection of engineering, product, and design. My current work centers on AI agents, full-stack systems, and the context infrastructure that helps people and models collaborate over time.",
  github: "https://github.com/NolanSoloBuilder",
  githubLabel: "NolanSoloBuilder",
  linkedin: "https://www.linkedin.com/in/web-xuhao/",
  x: "https://x.com/NolanBuilder01",
  xiaohongshu: "https://www.xiaohongshu.com/user/profile/676aae57000000001801c80d",
};

export const focusAreas = [
  {
    title: "AI / LLM / Agent",
    detail: "Agent workflows, memory, context, evaluation, and practical product boundaries.",
  },
  {
    title: "Web / Full-stack",
    detail: "From interface behavior and data contracts to services, deployment, and live acceptance.",
  },
  {
    title: "Product / Design",
    detail: "Treating product judgment, interaction quality, and implementation as one continuous system.",
  },
];

export const notes = [
  {
    slug: "first-note",
    date: "Coming soon",
    title: "The first note is taking shape",
    excerpt: "A reserved space for product decisions, engineering lessons, and the systems behind the work.",
    paragraphs: [
      "This is a deliberate placeholder for the first public note.",
      "Future writing will live here: product judgments, engineering lessons, build logs, and the reasoning behind finished systems.",
      "The structure is ready. The actual note will replace this placeholder when it is worth publishing.",
    ],
  },
];

// Only publish projects that the site owner has explicitly approved for this site.
export const projects = [
  {
    title: "CHINA METRO TYPING",
    tag: "Typing game",
    description: "A typing game across real metro lines in 41 Chinese cities, supporting Simplified Chinese and tone-free Pinyin.",
    status: "Live",
    url: "https://metro.forgepane.com/",
    mark: "/assets/projects/china-metro-typing-mark.webp",
    images: ["/assets/projects/china-metro-typing-route.webp"],
    highlights: ["41 cities", "Real metro lines", "Chinese + Pinyin"],
  },
  {
    title: "Cited Alpha",
    tag: "AI research workspace",
    description: "A source-backed AI workspace for financial research that keeps questions, evidence, agent work, and cited outputs together.",
    status: "Live",
    url: "https://cited-alpha.forgepane.com/",
    mark: "/assets/projects/cited-alpha-mark.webp",
    images: [
      "/assets/projects/cited-alpha-landing.webp",
      "/assets/projects/cited-alpha-cited-report.webp",
    ],
    highlights: ["Source-backed", "Agent research", "Cited outputs"],
  },
];
