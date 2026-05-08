<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="lilac echoes"
      subtitle="感受全校的心情流转"
    >
      <template #controls>
        <div class="flex flex-column align-items-end">
          <span class="text-xs text-muted-color">当前时间</span>
          <span class="text-sm font-semibold text-primary">{{
            currentTime
          }}</span>
        </div>
      </template>
    </PageHeader>
    <div class="home-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <Card
        class="mood-visualization-container mb-6 border-round-3xl overflow-hidden shadow-4"
        :style="cardGradientStyle"
      >
        <template #content>
          <div
            class="relative overflow-hidden flex flex-column align-items-center justify-content-center"
            style="height: 300px"
          >
            <!-- 背景融合效果 -->
            <div
              class="mood-fusion-layer absolute inset-0 transition-all duration-1000 border-round-3xl"
              :style="fusionStyle"
            ></div>

            <!-- 漂浮的气泡 -->
            <div
              v-for="(bubble, index) in moodBubbles"
              :key="index"
              class="mood-bubble"
              :style="bubbleStyle(bubble)"
            ></div>

            <div
              class="text-center z-2 relative flex flex-column align-items-center justify-content-center h-full"
            >
              <div
                class="text-6xl font-bold text-primary-900 mb-2 drop-shadow-sm transition-all"
              >
                {{ currentGlobalMood }}
              </div>
              <Tag
                value="全校情绪指数：85%"
                class="bg-white-alpha-40 border-round-3xl text-primary font-bold backdrop-blur-sm px-3"
              />
            </div>
          </div>
        </template>
      </Card>

      <section class="mb-6">
        <div class="flex justify-content-between align-items-end mb-4">
          <h3 class="m-0 text-lg font-semibold text-gray-800">
            你现在的感觉如何？
          </h3>
          <span class="text-xs text-primary font-medium">点击图标融合心境</span>
        </div>

        <div class="grid px-1">
          <div v-for="mood in moods" :key="mood.label" class="col-4 p-1">
            <Button
              @click="toggleMood(mood)"
              :severity="
                activeMoods.includes(mood.label) ? 'primary' : 'secondary'
              "
              :outlined="!activeMoods.includes(mood.label)"
              class="w-full flex-column py-4 border-round-2xl transition-all shadow-1"
            >
              <i :class="[mood.icon, 'text-3xl mb-2']"></i>
              <span class="text-xs font-bold">{{ mood.label }}</span>
            </Button>
          </div>
        </div>
      </section>

      <div
        v-if="activeMoods.length > 0"
        class="mt-4 mb-4 p-4 surface-card border-round-2xl animate-fadein shadow-2 border-left-3 border-primary"
      >
        <div class="flex align-items-center mb-2">
          <i class="pi pi-sparkles text-primary mr-2"></i>
          <span class="text-sm font-bold text-primary">心情共鸣</span>
        </div>
        <p class="text-color-secondary italic m-0 line-height-3 text-sm">
          "{{ mixedQuote }}"
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { moodTypes } from "#/mood";

const currentGlobalMood = ref("宁静");
const activeMoods = ref([]);
const currentTime = ref(
  new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
);

const moods = moodTypes.map((m) => ({
  label: m.type,
  icon: m.icon,
  color: m.color,
  quote: m.quote,
}));

const moodBubbles = ref([
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
  {
    size: 80,
    x: 75,
    y: 60,
    color: "var(--fuchsia-400)",
    opacity: 0.5,
    delay: "2s",
  },
  {
    size: 120,
    x: 10,
    y: 70,
    color: "var(--pink-200)",
    opacity: 0.4,
    delay: "1.5s",
  },
]);

const cardGradientStyle = {
  background:
    "radial-gradient(circle at 50% 50%, #fff 0%, var(--fuchsia-50) 100%)",
};

const fusionStyle = computed(() => {
  if (activeMoods.value.length === 0) return { background: "transparent" };

  const colors = activeMoods.value.map((label) => {
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

const mixedQuote = computed(() => {
  if (activeMoods.value.length === 0) return "";
  if (activeMoods.value.length === 1) {
    return moods.find((m) => m.label === activeMoods.value[0])?.quote;
  }
  return "心情在此刻交织。复杂的思绪最终会沉淀为最温柔的丁香回响。";
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

const toggleMood = (mood) => {
  const index = activeMoods.value.indexOf(mood.label);
  if (index > -1) {
    activeMoods.value.splice(index, 1);
  } else {
    if (activeMoods.value.length >= 3) {
      activeMoods.value.shift();
    }
    activeMoods.value.push(mood.label);
  }
};

onMounted(() => {
  setInterval(() => {
    currentTime.value = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }, 1000);
});
</script>

<style scoped>
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

.animate-fadein {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drop-shadow-sm {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.bg-white-alpha-40 {
  background-color: rgba(255, 255, 255, 0.4);
}

.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}
</style>
