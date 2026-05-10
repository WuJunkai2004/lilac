export const moodTypes = [
  {
    type: "喜悦",
    color: "#FFD1DC",
    icon: "pi pi-heart-fill",
    quote: "分享快乐，双倍幸福。",
  },
  {
    type: "孤独",
    color: "#B0BEC5",
    icon: "pi pi-moon",
    quote: "在静谧中与自己对话。",
  },
  {
    type: "宁静",
    color: "#E1BEE7",
    icon: "pi pi-wave-pulse",
    quote: "心如止水，静候花开。",
  },
  {
    type: "忧郁",
    color: "#ECEFF1",
    icon: "pi pi-cloud",
    quote: "在泪水中寻找星光。",
  },
  {
    type: "愤怒",
    color: "#FFCDD2",
    icon: "pi pi-bolt",
    quote: "冷静是化解愤怒的良方。",
  },
  {
    type: "放松",
    color: "#B2EBF2",
    icon: "pi pi-sun",
    quote: "放慢脚步，感受微风。",
  },
  {
    type: "活力",
    color: "#FFD8A8",
    icon: "pi pi-crown",
    quote: "生活充满了无限可能。",
  },
  {
    type: "浪漫",
    color: "#F8BBD0",
    icon: "pi pi-star-fill",
    quote: "丁香花开，是诗意的守候。",
  },
  {
    type: "焦虑",
    color: "#FFF9C4",
    icon: "pi pi-exclamation-triangle",
    quote: "深呼吸，一切都会好起来。",
  },
  {
    type: "神秘",
    color: "#D1C4E9",
    icon: "pi pi-sparkles",
    quote: "未知的世界，藏着惊喜。",
  },
];

export const getMoodColor = (mood) => {
  const moodInfo = moodTypes.find((m) => m.type === mood);
  return moodInfo ? moodInfo.color : "transparent";
};

export const getMoodIcon = (mood) => {
  const moodInfo = moodTypes.find((m) => m.type === mood);
  return moodInfo ? moodInfo.icon : "pi pi-question";
};

export const getMoodQuote = (mood) => {
  const moodInfo = moodTypes.find((m) => m.type === mood);
  return moodInfo ? moodInfo.quote : "";
};
