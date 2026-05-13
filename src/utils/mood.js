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

const moodCombinationString = `喜悦 + 孤独
热闹后的独处，是灵魂在悄悄充电。
喜悦 + 宁静
心若安暖，清风自会翻动书页。
喜悦 + 忧郁
眼泪里的笑意，是成长最真实的勋章。
喜悦 + 愤怒
把不甘化作燃料，烧出一片新天地。
喜悦 + 放松
连发呆都带着甜味，这就是最好的此刻。
喜悦 + 活力
世界是我的游乐场，每一刻都在闪闪发光。
喜悦 + 浪漫
万物皆可爱，而你是最心动的那一抹亮色。
喜悦 + 焦虑
哪怕步履匆匆，口袋里也要装满糖霜。
喜悦 + 神秘
拆开礼物的瞬间，宇宙都在为我鼓掌。
孤独 + 宁静
沉默不是空白，而是内心的繁花盛开。
孤独 + 忧郁
允许自己在角落里，像旧唱片一样低吟。
孤独 + 愤怒
一个人的战场，也能长出坚硬的铠甲。
孤独 + 放松
切断喧嚣，只听呼吸在耳边低语。
孤独 + 活力
独自奔跑时，风声是最好的喝彩。
孤独 + 浪漫
与自己约会，月光也会格外温柔。
孤独 + 焦虑
在迷雾中独行，每一步都是踏实的探索。
孤独 + 神秘
深海般的寂静里，藏着未解的诗篇。
宁静 + 忧郁
淡淡的蓝调里，藏着抚平褶皱的力量。
宁静 + 愤怒
止水之下，暗流正积蓄着变革的能量。
宁静 + 放松
云朵般轻盈，连时光都走得慢了一些。
宁静 + 活力
静水流深，生命的张力在无声中爆发。
宁静 + 浪漫
岁月静好，是因为有人为你煮了热汤。
宁静 + 焦虑
锚定此刻，风暴眼中自有片刻安宁。
宁静 + 神秘
雾气散去的地方，是梦开始的原乡。
忧郁 + 愤怒
把灰色的雨滴，炼成燎原的星火。
忧郁 + 放松
像旧毛衣一样包裹自己，在软榻上融化。
忧郁 + 活力
伤口长出的翅膀，飞得比从前更高。
忧郁 + 浪漫
连遗憾都美得像一场，不愿醒来的雨。
忧郁 + 焦虑
在未知的迷宫里，即使爬行也是前行。
忧郁 + 神秘
深渊里回望，星空其实触手可及。
愤怒 + 放松
紧握的拳头松开，掌心躺着整个春天。
愤怒 + 活力
将雷霆震怒，转化为破土而出的野性。
愤怒 + 浪漫
炽热的爱意，往往披着带刺的红袍。
愤怒 + 焦虑
既然无处可逃，不如化作破浪的礁石。
愤怒 + 神秘
烈焰焚尽处，方见凤凰涅槃的密码。
放松 + 活力
像猫咪伸懒腰一样，唤醒全身的脉搏。
放松 + 浪漫
慵懒的午后，连空气都弥漫着粉红泡泡。
放松 + 焦虑
深呼吸一口，让紧绷的神经在此刻靠岸。
放松 + 神秘
半梦半醒之间，精灵正在窗台跳舞。
活力 + 浪漫
追着日落狂奔，去赴一场粉色的约。
活力 + 焦虑
即使心跳过速，也要冲向最高的山巅。
活力 + 神秘
跃入深蓝，做一只探索未知的海豚。
浪漫 + 焦虑
玫瑰即便带刺，也要在荆棘中热烈绽放。
浪漫 + 神秘
银河倾斜而下，我们是迷失在其中的星尘。
焦虑 + 神秘
迷雾重重，或许正是通往桃花源的密径。`;

const moodCombinationMap = (() => {
  const map = {};
  const lines = moodCombinationString.trim().split("\n");
  for (let i = 0; i < lines.length; i += 2) {
    const combination = lines[i]?.trim();
    const quote = lines[i + 1]?.trim();
    if (combination && quote) {
      map[combination] = quote;
    }
  }
  return map;
})();

export const getCombinationQuote = (mood1, mood2) => {
  const key1 = `${mood1} + ${mood2}`;
  const key2 = `${mood2} + ${mood1}`;
  return (
    moodCombinationMap[key1] ||
    moodCombinationMap[key2] ||
    "心情在此刻交织。复杂的思绪最终会沉淀为最温柔的丁香回响。"
  );
};
