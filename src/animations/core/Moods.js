import DandelionEffect from "~/effects/DandelionEffect";
import CloudEffect from "~/effects/CloudEffect";
import ThunderCloudEffect from "~/effects/ThunderCloudEffect";

const MoodEffects = {
  忧郁: {
    name: "clouds",
    effect: CloudEffect,
    options: {
      count: 4,
    },
  },
  放松: {
    name: "dandelions",
    effect: DandelionEffect,
    options: {
      count: 20,
    },
  },
  愤怒: {
    name: "thunderclouds",
    effect: ThunderCloudEffect,
    options: {
      count: 1,
    },
  },
  宁静: {
    name: "dandelions-in-peace",
    effect: DandelionEffect,
    options: {
      count: 20,
    },
  },
};

export const loadMoodEffect = (mood) => {
  const moodEffect = MoodEffects[mood];
  if (moodEffect) {
    const result = [moodEffect.name, moodEffect.effect, moodEffect.options];
    return result;
  }
  return null;
};
