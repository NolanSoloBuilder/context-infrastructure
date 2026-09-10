export const CITIES = [
  {
    name: "雅安",
    pinyin: "yaan",
    syllables: ["ya", "an"],
    coordinates: [103.0133, 29.9805],
  },
  {
    name: "乐山",
    pinyin: "leshan",
    syllables: ["le", "shan"],
    coordinates: [103.7656, 29.5521],
  },
  {
    name: "宜宾",
    pinyin: "yibin",
    syllables: ["yi", "bin"],
    coordinates: [104.6432, 28.7513],
  },
];

export const ROUTE_POINTS = [
  { name: "成都", coordinates: [104.0665, 30.5728] },
  ...CITIES,
];

export const ROUTE_DATA_URL = "/data/chengdu-yibin-route.geojson";

export const SCENES = [
  {
    city: "雅安",
    title: "碧峰峡路上",
    segmentLabel: "成都至雅安沿途实景",
    src: "/assets/yaan-bifengxia-road.jpg",
    alt: "雅安碧峰峡道路穿过林木和陡峭岩壁，远处有车辆行驶",
    objectPosition: "center 49%",
    photographer: "zhanyoun",
    year: "2010",
    license: "CC BY-SA 3.0",
    sourceUrl:
      "https://commons.wikimedia.org/wiki/File:%E7%A2%A7%E5%B3%B0%E5%B3%A1%E8%B7%AF%E4%B8%8A_-_panoramio.jpg",
  },
  {
    city: "乐山",
    title: "乐山市井街巷",
    segmentLabel: "雅安至乐山城市实景",
    src: "/assets/leshan-sideroad.jpg",
    alt: "乐山市中心一条有店铺、行人和摩托车的生活街巷",
    objectPosition: "center 50%",
    photographer: "Kounosu",
    year: "2009",
    license: "CC BY-SA 3.0",
    sourceUrl: "https://commons.wikimedia.org/wiki/File:Leshan-sideroad_China.jpg",
  },
  {
    city: "宜宾",
    title: "翠屏山眺望宜宾",
    segmentLabel: "乐山至宜宾城市实景",
    src: "/assets/yibin-birdview.jpg",
    alt: "从翠屏山俯瞰宜宾城区、河流、红色拱桥和远山",
    objectPosition: "center 42%",
    photographer: "Terence85",
    year: "2009",
    license: "CC BY-SA 3.0",
    sourceUrl: "https://commons.wikimedia.org/wiki/File:Yibin_birdview.jpg",
  },
];
