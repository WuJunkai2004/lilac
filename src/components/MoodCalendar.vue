<script setup>
import { ref, computed } from "vue";

const moodData = {
  23: "活力",
  22: "喜悦",
  21: "宁静",
  20: "疲惫",
  19: "忧郁",
  18: "生气",
  17: "焦虑",
  16: "期待",
  15: "伤心",
  14: "轻松",
};

const moodTypes = [
  { type: "活力", color: "#FFD8A8" },
  { type: "喜悦", color: "#FFD1DC" },
  { type: "宁静", color: "#E1BEE7" },
  { type: "疲惫", color: "#FFE4E1" },
  { type: "忧郁", color: "#ECEFF1" },
  { type: "生气", color: "#FFCDD2" },
  { type: "焦虑", color: "#FFF9C4" },
  { type: "期待", color: "#DCEDC8" },
  { type: "伤心", color: "#F5F5F5" },
  { type: "轻松", color: "#B2EBF2" },
];
const getMoodColor = (mood) => {
  const moodInfo = moodTypes.find((m) => m.type === mood);
  return moodInfo ? moodInfo.color : "transparent";
};
const getMoodCellClass = (day) => {
  // 如果是选中的日期，返回主题色背景
  if (day === theDay.value) {
    if (moodData[day]) {
      return "border-2 border-primary-400";
    }
    return "bg-primary-100 border-2 border-primary-400";
  }
  return `hover:surface-100`;
};

const getMoodCellStyle = (day) => {
  const mood = moodData[day];
  return {
    backgroundColor: getMoodColor(mood),
  };
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

        <!-- 日期格 -->
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
              getMoodCellClass(i),
            ]"
            :style="getMoodCellStyle(i)"
          >
            <span
              class="text-sm font-bold z-1"
              :class="
                theDay === i && !moodData[i]
                  ? 'text-primary-700'
                  : 'text-gray-700'
              "
              >{{ i }}</span
            >
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
