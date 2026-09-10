import { Binoculars, Camera, Star } from "@phosphor-icons/react";

export const LEVELS = [
  {
    id: "south-sichuan",
    number: 1,
    name: "川南城市线",
    summary: "成都 → 宜宾",
    status: "active",
  },
  {
    id: "hexi-corridor",
    number: 2,
    name: "河西走廊",
    summary: "未解锁",
    status: "locked",
  },
  {
    id: "southeast-coast",
    number: 3,
    name: "东南海岸",
    summary: "未解锁",
    status: "locked",
  },
];

export const MAP_EVENTS = [
  {
    id: "lookout",
    label: "山谷观景点",
    coordinates: [103.34, 29.78],
    color: "amber",
    icon: Binoculars,
  },
  {
    id: "hidden-stamp",
    label: "隐藏城市章",
    coordinates: [103.62, 29.36],
    color: "violet",
    icon: Star,
  },
  {
    id: "photo-stop",
    label: "实景拍摄点",
    coordinates: [104.04, 29.12],
    color: "green",
    icon: Camera,
  },
];

export const FORK_EVENT = {
  id: "panda-town-fork",
  triggerCityIndex: 0,
  triggerLetters: 2,
  title: "岔路口：熊猫古镇",
  description: "前方道路分岔。两条路线都会抵达雅安，但沿途的资源与触发条件不同。",
  choices: [
    {
      id: "national-road",
      title: "走国道",
      detail: "可能发现隐藏城市章",
      moneyDelta: -40,
      staminaDelta: -2,
      luckDelta: 15,
    },
    {
      id: "expressway",
      title: "走高速",
      detail: "连击奖励 +20%",
      moneyDelta: -70,
      staminaDelta: 4,
      luckDelta: 0,
    },
  ],
};
