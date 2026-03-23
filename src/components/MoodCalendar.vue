<script setup>
import { ref, computed } from "vue";

const moodTypes = [
  { type: "活力", color: "var(--p-orange-500)" },
  { type: "喜悦", color: "var(--p-pink-500)" },
  { type: "宁静", color: "var(--p-fuchsia-500)" },
  { type: "疲惫", color: "var(--p-zinc-500)" },
  { type: "忧郁", color: "var(--p-indigo-500)" },
];
const getMoodColor = (mood) => {
  const moodInfo = moodTypes.find((m) => m.type === mood);
  return moodInfo ? moodInfo.color : "transparent";
};

// 日历基础数据
const weekDays = ["日", "一", "二", "三", "四", "五", "六"];
const theYear = ref(new Date().getFullYear());
const theMonth = ref(new Date().getMonth() + 1);
const theDay = ref(new Date().getDate());

const daysInMonth = computed(() => {
  return new Date(theYear.value, theMonth.value, 0).getDate();
});

const firstDayOffset = computed(() => {
  return new Date(theYear.value, theMonth.value - 1, 1).getDay();
});

const isCurrentMonth = computed(() => {
  const now = new Date();
  return (
    theYear.value === now.getFullYear() && theMonth.value === now.getMonth() + 1
  );
});

const selectDay = (day) => {
  theDay.value = day;
};

const getMoodForDate = (day) => {
  const moodData = {
    23: { type: "活力", color: "var(--p-orange-500)" },
    22: { type: "喜悦", color: "var(--p-pink-500)" },
    21: { type: "宁静", color: "var(--p-fuchsia-500)" },
    20: { type: "疲惫", color: "var(--p-zinc-500)" },
    19: { type: "忧郁", color: "var(--p-indigo-500)" },
  };
  if (moodData[day]) {
    console.log(
      `获取到 ${theYear.value}年${theMonth.value}月${day}日 的心情数据:`,
      moodData[day],
    );
  }
  return moodData[day] || null;
};

// 月份切换逻辑
const monthGoBack = () => {
  if (theMonth.value === 1) {
    theMonth.value = 12;
    theYear.value -= 1;
  } else {
    theMonth.value -= 1;
  }
  if (isCurrentMonth.value) {
    theDay.value = new Date().getDate();
  } else {
    theDay.value = 1;
  }
};
const monthGoForward = () => {
  if (theMonth.value === 12) {
    theMonth.value = 1;
    theYear.value += 1;
  } else {
    theMonth.value += 1;
  }
  if (isCurrentMonth.value) {
    theDay.value = new Date().getDate();
  } else {
    theDay.value = 1;
  }
};
</script>

<template>
  <div class="flex align-items-center justify-content-between mb-4 px-2">
    <Button
      icon="pi pi-chevron-left"
      rounded
      outlined
      severity="primary"
      size="small"
      class="bg-white"
      @click="monthGoBack"
    />
    <div class="text-lg font-bold text-primary-900">
      {{ theYear }}年 {{ theMonth }}月
    </div>
    <Button
      icon="pi pi-chevron-right"
      rounded
      outlined
      severity="primary"
      size="small"
      class="bg-white"
      @click="monthGoForward"
    />
  </div>

  <!-- 日历网格 -->
  <Card
    class="calendar-card border-round-3xl shadow-3 overflow-hidden border-none mb-5"
  >
    <template #content>
      <div class="grid text-center mb-3">
        <div
          v-for="day in weekDays"
          :key="day"
          class="col text-xs font-bold text-primary-400 uppercase"
        >
          {{ day }}
        </div>
      </div>

      <div class="grid text-center">
        <!-- 空白格填充 -->
        <div
          v-for="empty in firstDayOffset"
          :key="'empty-' + empty"
          class="col-fixed p-1"
          style="width: 14.28%"
        ></div>

        <div
          v-for="i in daysInMonth"
          :key="i"
          class="col-fixed p-1"
          style="width: 14.28%"
        >
          <div
            @click="selectDay(i)"
            :class="[
              'date-cell w-full aspect-square border-round-xl flex flex-column align-items-center justify-content-center cursor-pointer transition-all relative',
              theDay === i
                ? 'bg-primary-100 border-2 border-primary-400'
                : 'bg-transparent hover:surface-100',
            ]"
          >
            <span
              class="text-sm font-bold z-1"
              :class="theDay === i ? 'text-primary-700' : 'text-gray-700'"
              >{{ i }}</span
            >
            <!-- 心情圆点 -->
            <div
              v-if="getMoodForDate(i)"
              class="mood-dot w-2 h-2 border-circle mt-1"
              :style="{ backgroundColor: getMoodForDate(i).color }"
            ></div>
            <!-- 装饰背景 -->
            <div
              v-if="theDay === i"
              class="absolute inset-0 bg-primary-500 opacity-10 border-round-xl"
            ></div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.calendar-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
}

.date-cell {
  min-height: 50px;
}

.aspect-square {
  aspect-ratio: 1 / 1;
}
</style>
