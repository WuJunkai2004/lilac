<script setup>
import { ref } from "vue";

const selectedDate = ref(23);
const isPublic = ref(false);

const getAIReviewForDate = (day) => {
  const reviews = {
    23: "今天的你像三月的阳光一样充满活力。通过与 AI 伙伴的交流，你展现出了极强的行动力，建议保持这种节奏。",
    22: "喜悦是今日的主旋律。你分享的校园风景信笺得到了校友的共鸣，这种连接感让你的心理状态非常稳定。",
    default:
      "这一天你留下了深沉而宁静的回响。AI 观察到你在平衡学业与自我关怀方面做得很好。",
  };
  return reviews[day] || reviews.default;
};

const getRecommendation = (day) => {
  return {
    activity: day % 2 === 0 ? "在荷花池边冥想" : "去图书馆五楼看落日",
    food: day % 3 === 0 ? "三食堂的瓦罐汤" : "清真餐厅的牛肉拉面",
  };
};
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="心情日历"
      subtitle="回顾你的丁香足迹，感受情绪起伏"
    />
    <div class="calendar-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <MoodCalendar />

      <!-- 心理总结卡片 -->
      <section v-if="selectedDate" class="animate-fadein">
        <Card
          class="border-round-3xl shadow-2 overflow-hidden border-none relative"
        >
          <template #content>
            <div class="absolute top-0 right-0 p-4 opacity-10">
              <i class="pi pi-sparkles text-6xl text-primary"></i>
            </div>

            <div class="flex align-items-center justify-content-between mb-4">
              <div class="flex align-items-center">
                <div class="p-3 bg-primary-100 border-round-xl mr-3 shadow-sm">
                  <i class="pi pi-bolt text-primary text-xl"></i>
                </div>
                <h3 class="m-0 text-lg font-bold text-gray-800">
                  3月{{ selectedDate }}日 心理总结
                </h3>
              </div>
              <div class="flex align-items-center gap-2">
                <span class="text-xs text-muted-color">公开</span>
                <ToggleSwitch v-model="isPublic" size="small" />
              </div>
            </div>

            <p
              class="text-color-secondary line-height-3 italic mb-5 px-1 border-left-3 border-primary-200 pl-3"
            >
              "{{ getAIReviewForDate(selectedDate) }}"
            </p>

            <div class="grid">
              <div class="col-6">
                <div
                  class="p-3 bg-blue-50 border-round-2xl border-1 border-blue-100 shadow-sm"
                >
                  <div
                    class="text-xs text-blue-600 mb-2 font-bold flex align-items-center"
                  >
                    <i class="pi pi-map-marker mr-1"></i> 建议活动
                  </div>
                  <div class="text-sm text-blue-900 font-medium">
                    {{ getRecommendation(selectedDate).activity }}
                  </div>
                </div>
              </div>
              <div class="col-6">
                <div
                  class="p-3 bg-pink-50 border-round-2xl border-1 border-pink-100 shadow-sm"
                >
                  <div
                    class="text-xs text-pink-600 mb-2 font-bold flex align-items-center"
                  >
                    <i class="pi pi-heart mr-1"></i> 今日美食
                  </div>
                  <div class="text-sm text-pink-900 font-medium">
                    {{ getRecommendation(selectedDate).food }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- 情绪趋势图 -->
        <div class="mt-6 px-2">
          <div class="flex justify-content-between align-items-end mb-3">
            <span class="text-sm font-bold text-gray-700">本周情绪稳定性</span>
            <Tag value="稳步回升 ↑" severity="success" size="small" rounded />
          </div>
          <div
            class="w-full h-1rem bg-surface-200 border-round-3xl overflow-hidden flex shadow-inner"
          >
            <div class="h-full bg-primary-400" style="width: 40%"></div>
            <div class="h-full bg-pink-400" style="width: 25%"></div>
            <div class="h-full bg-blue-400" style="width: 20%"></div>
            <div class="h-full bg-orange-400" style="width: 15%"></div>
          </div>
        </div>
      </section>
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
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.shadow-inner {
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
}
</style>
