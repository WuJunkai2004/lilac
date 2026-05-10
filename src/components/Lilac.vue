<script setup>
import { ref, computed, onMounted } from "vue";
import { moodTypes } from "#/mood";
import { resCheck, authCheck } from "#/check";

const props = defineProps({
  activeMoods: {
    type: Array,
    default: () => [],
  },
});

const globalMoodData = ref([]);
const isLoading = ref(true);
const isVideoLoaded = ref(false);
const canvasRef = ref(null);

const moods = moodTypes.map((m) => ({
  label: m.type,
  icon: m.icon,
  color: m.color,
  quote: m.quote,
}));

const currentGlobalMood = computed(() => {
  if (globalMoodData.value.length === 0) return "宁静";
  const sorted = [...globalMoodData.value].sort((a, b) => b.count - a.count);
  return sorted[0].mood;
});

const moodIndex = computed(() => {
  if (globalMoodData.value.length === 0) return 0;
  const total = globalMoodData.value.reduce((acc, curr) => acc + curr.count, 0);
  return Math.min(99, Math.floor(total / 2) + 60);
});

const moodBubbles = computed(() => {
  if (globalMoodData.value.length === 0) {
    return [
      {
        size: 100,
        x: 20,
        y: 30,
        color: "var(--fuchsia-300)",
        opacity: 0.6,
        delay: "0s",
      },
      {
        size: 150,
        x: 60,
        y: 10,
        color: "var(--purple-200)",
        opacity: 0.4,
        delay: "1s",
      },
    ];
  }

  return globalMoodData.value.map((item, index) => {
    const moodInfo =
      moodTypes.find((m) => m.type === item.mood) || moodTypes[2];
    return {
      size: 60 + Math.min(item.count * 15, 120),
      x: (index * 37 + 13) % 80,
      y: (index * 23 + 17) % 60,
      color: moodInfo.color,
      opacity: 0.3 + Math.min(item.count * 0.05, 0.4),
      delay: `${index * 0.7}s`,
    };
  });
});

const fusionStyle = computed(() => {
  if (props.activeMoods.length === 0) return { background: "transparent" };

  const colors = props.activeMoods.map((label) => {
    return moods.find((m) => m.label === label)?.color;
  });

  if (colors.length === 1) {
    return { background: `color-mix(in srgb, ${colors[0]}, transparent 85%)` };
  }

  const gradient = colors
    .map((c) => `color-mix(in srgb, ${c}, transparent 80%)`)
    .join(", ");
  return {
    background: `linear-gradient(135deg, ${gradient})`,
    filter: "blur(40px)",
  };
});

const bubbleStyle = (bubble) => ({
  width: `${bubble.size}px`,
  height: `${bubble.size}px`,
  left: `${bubble.x}%`,
  top: `${bubble.y}%`,
  backgroundColor: bubble.color,
  opacity: bubble.opacity,
  position: "absolute",
  borderRadius: "50%",
  filter: "blur(25px)",
  animation: `float 8s infinite ease-in-out ${bubble.delay}`,
});

const fetchOverview = async () => {
  try {
    isLoading.value = true;
    const today = new Date().toLocaleDateString("sv-SE");
    const data = await fetch(`/api/mood/overview?date=${today}`)
      .then(resCheck)
      .then(authCheck);
    if (data.success) {
      globalMoodData.value = data.data;
    }
  } catch (error) {
    console.error("Failed to fetch mood overview:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchOverview();
});
</script>

<template>
  <Card
    class="mood-visualization-container mb-6 border-round-3xl overflow-hidden shadow-4 bg-transparent p-0"
  >
    <template #content>
      <div
        class="relative overflow-hidden flex flex-column align-items-center justify-content-center border-round-3xl"
        style="aspect-ratio: 1 / 1"
      >
        <!-- 视频占位图 -->
        <img
          v-if="!isVideoLoaded"
          src="/lilac/background.webp"
          class="absolute inset-0 w-full h-full object-cover z-0"
        />

        <!-- 视频底层背景 -->
        <video
          src="/lilac/background.mp4"
          autoplay
          muted
          loop
          playsinline
          @loadeddata="isVideoLoaded = true"
          class="absolute inset-0 w-full h-full object-cover z-0"
        ></video>

        <!-- 背景融合效果 -->
        <div
          class="mood-fusion-layer absolute inset-0 transition-all duration-1000 z-1"
          :style="fusionStyle"
        ></div>

        <!-- 未来 Three.js Canvas -->
        <canvas
          ref="canvasRef"
          class="absolute inset-0 w-full h-full z-2 pointer-events-none"
        ></canvas>

        <!-- 漂浮的气泡 (保留作为占位) -->
        <template v-if="!isLoading">
          <div
            v-for="(bubble, index) in moodBubbles"
            :key="index"
            class="mood-bubble z-1"
            :style="bubbleStyle(bubble)"
          ></div>
        </template>
        <ProgressSpinner v-else style="width: 50px; height: 50px" class="z-3" />

        <div
          v-if="!isLoading"
          class="text-center z-3 relative flex flex-column align-items-center justify-content-center h-full"
        >
          <div
            class="text-6xl font-bold text-white mb-2 drop-shadow-md transition-all"
          >
            {{ currentGlobalMood }}
          </div>
          <Tag
            :value="`全校情绪指数：${moodIndex}%`"
            class="bg-white-alpha-40 border-round-3xl text-white font-bold backdrop-blur-sm px-3"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
:deep(.p-card-body) {
  padding: 0;
}

.mood-bubble {
  pointer-events: none;
}

@keyframes float {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(15px, 25px) scale(1.1);
  }
  66% {
    transform: translate(-10px, 15px) scale(0.9);
  }
}

.drop-shadow-md {
  filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.3));
}

.bg-white-alpha-40 {
  background-color: rgba(255, 255, 255, 0.4);
}

.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}
</style>
