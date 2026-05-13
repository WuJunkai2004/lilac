<script setup>
import { ref, computed, onMounted } from "vue";
import { moodTypes } from "#/mood";

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

const mixedQuote = computed(() => {
  if (activeMoods.value.length === 0) {
    return "";
  }
  if (activeMoods.value.length === 1) {
    return moods.find((m) => m.label === activeMoods.value[0])?.quote;
  }
  return "心情在此刻交织。复杂的思绪最终会沉淀为最温柔的丁香回响。";
});

const toggleMood = (mood) => {
  const index = activeMoods.value.indexOf(mood.label);
  if (index > -1) {
    activeMoods.value.splice(index, 1);
  } else {
    if (activeMoods.value.length >= 2) {
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
      <Lilac :activeMoods="activeMoods" />

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

<style scoped>
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
</style>
