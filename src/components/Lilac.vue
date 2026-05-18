<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { resCheck, authCheck } from "#/check";
import SceneManager from "~/core/SceneManager";
import { loadMoodEffect } from "~/core/Moods";

const props = defineProps({
  activeMoods: {
    type: Array,
    default: () => [],
  },
});

const globalMoodData = ref([]);
const isLoading = ref(true);
const isVideoLoaded = ref(false);

const onVideoLoaded = () => {
  // 视频加载完成后延迟隐藏占位图，确保视频已开始渲染，避免出现暂停图标
  setTimeout(() => {
    isVideoLoaded.value = true;
  }, 500);
};
const canvasRef = ref(null);
let animationManager = null;

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

const initAnimations = () => {
  if (!canvasRef.value) {
    return;
  }

  animationManager = new SceneManager(canvasRef.value);
  updateAnimations();
  animationManager.start();
};

const updateAnimations = () => {
  if (!animationManager) {
    return;
  }

  const moodsToLoad = new Set([...props.activeMoods, currentGlobalMood.value]);
  const supportedMoods = ["忧郁", "放松", "愤怒", "宁静", "孤独"];

  supportedMoods.forEach((mood) => {
    const effectData = loadMoodEffect(mood);
    if (effectData) {
      const [name, EffectClass, options] = effectData;
      if (moodsToLoad.has(mood)) {
        animationManager.addEffect(name, EffectClass, options);
      } else {
        animationManager.removeEffect(name);
      }
    }
  });
};

watch(
  [currentGlobalMood, () => props.activeMoods],
  () => {
    updateAnimations();
  },
  { deep: true },
);

const handleResize = () => {
  animationManager?.onResize();
};

onMounted(() => {
  fetchOverview();
  initAnimations();
  window.addEventListener("resize", handleResize);
});

onUnmounted(() => {
  animationManager?.dispose();
  window.removeEventListener("resize", handleResize);
});
</script>

<template>
  <Card
    class="mood-visualization-container mb-4 border-round-3xl overflow-hidden shadow-4 bg-transparent p-0"
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
          class="absolute inset-0 w-full h-full object-cover z-1"
        />

        <!-- 视频底层背景 -->
        <video
          src="/lilac/background.mp4"
          autoplay
          muted
          loop
          playsinline
          @loadeddata="onVideoLoaded"
          class="absolute inset-0 w-full h-full object-cover z-0"
        ></video>

        <!-- Three.js Canvas -->
        <canvas
          ref="canvasRef"
          class="absolute inset-0 w-full h-full z-2 pointer-events-none"
        ></canvas>

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
