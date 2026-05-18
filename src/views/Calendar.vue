<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";
import { resCheck, authCheck } from "#/check";
import { useAlert } from "#/alert";
import { getMoodColor, getMoodIcon } from "#/mood";

const calenderRef = ref(null);
const router = useRouter();
const { alerts } = useAlert();

const moodData = ref({});
const moodDetail = ref({
  summary: "",
  activity: "",
  food: "",
});

const getAIReviewForDate = (day) => {
  if (moodDetail.value?.summary) {
    return moodDetail.value.summary;
  }
  if (!isExperienced()) {
    return "未来的一切都充满了未知和可能，希望你能在人生这个旅程中保持好奇和开放的心态。";
  }
  return "这一天你留下了深沉而宁静的回响。AI 观察到你在平衡学业与自我关怀方面做得很好。";
};

const getRecommendation = (day) => {
  return {
    activity:
      moodDetail.value?.activity ||
      (day % 2 === 0 ? "在荷花池边冥想" : "去图书馆五楼看落日"),
    food:
      moodDetail.value?.food ||
      (day % 3 === 0 ? "三食堂的瓦罐汤" : "清真餐厅的牛肉拉面"),
  };
};

const isToday = () => {
  if (!calenderRef.value) {
    return false;
  }
  const today = new Date();
  const selectedDate = calenderRef.value.getSelectedDate();
  return (
    today.getFullYear() === selectedDate.getFullYear() &&
    today.getMonth() === selectedDate.getMonth() &&
    today.getDate() === selectedDate.getDate()
  );
};

const isExperienced = () => {
  if (!calenderRef.value) {
    return false;
  }
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const selectedDate = calenderRef.value.getSelectedDate();
  selectedDate.setHours(0, 0, 0, 0);
  return selectedDate <= today;
};

const loadMoodDetail = async () => {
  if (!calenderRef.value) {
    return;
  }
  const selectedDay = calenderRef.value.getSelectedDay();
  const dateStr = calenderRef.value.getSelectedDateStr();

  if (!isExperienced() || !moodData.value[selectedDay]) {
    moodDetail.value = { summary: "", activity: "", food: "" };
  }
  fetch(`/api/mood/detail?date=${dateStr}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${await storage.get("token")}`,
    },
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        moodDetail.value = res.data;
      } else {
        moodDetail.value = { summary: "", activity: "", food: "" };
      }
    })
    .catch((error) => {
      console.error("Error fetching mood detail:", error);
      moodDetail.value = { summary: "", activity: "", food: "" };
    });
};

const loadMoodData = async () => {
  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  moodData.value = {};
  moodDetail.value = { summary: "", activity: "", food: "" };

  fetch(`/api/mood/calendar?month=${calenderRef.value.getSelectedMonthStr()}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${await storage.get("token")}`,
    },
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      for (let entry of res.data) {
        const day = new Date(entry.date).getDate();
        moodData.value[day] = entry.mood;
      }
      loadMoodDetail();
    })
    .catch((error) => {
      console.error("Error fetching mood data:", error);
      alerts("数据加载失败", "无法获取心情数据，请稍后再试");
    });
};

onMounted(() => {
  loadMoodData();
});
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="心情日历"
      subtitle="回顾你的丁香足迹，感受情绪起伏"
    />
    <div class="calendar-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <MoodCalendar
        :value="moodData"
        ref="calenderRef"
        @change-month="loadMoodData"
        @change-date="loadMoodDetail"
      />

      <!-- 心理总结卡片 -->
      <section v-if="calenderRef" class="animate-fadein">
        <Card
          class="border-round-3xl shadow-2 overflow-hidden border-none relative mb-4"
        >
          <template #content>
            <div class="absolute top-0 right-0 p-4 opacity-10">
              <i class="pi pi-sparkles text-6xl text-primary"></i>
            </div>

            <div class="flex align-items-center justify-content-between mb-4">
              <div class="flex align-items-center">
                <div class="p-3 bg-primary-100 border-round-xl mr-3 shadow-sm">
                  <i
                    :class="[
                      getMoodIcon(moodData[calenderRef.getSelectedDay()]),
                      'text-primary text-xl',
                    ]"
                  ></i>
                </div>
                <div class="flex flex-column">
                  <span class="text-base text-gray-500 font-medium mb-1">
                    {{ calenderRef.getSelectedMonth() }}月{{
                      calenderRef.getSelectedDay()
                    }}日
                  </span>
                  <h3 class="m-0 text-lg font-bold text-gray-800">心理总结</h3>
                </div>
              </div>
              <div
                v-if="moodData[calenderRef.getSelectedDay()]"
                class="px-4 py-2 border-round-2xl text-base font-bold shadow-sm"
                :style="{
                  backgroundColor: getMoodColor(
                    moodData[calenderRef.getSelectedDay()],
                  ),
                  color: '#4b5563',
                }"
              >
                {{ moodData[calenderRef.getSelectedDay()] }}
              </div>
            </div>

            <p
              class="text-color-secondary line-height-3 italic mb-5 px-1 border-left-3 border-primary-200 pl-3"
            >
              "{{ getAIReviewForDate(calenderRef.getSelectedDay()) }}"
            </p>

            <div
              v-if="moodDetail.activity || moodDetail.food || isToday()"
              class="grid"
            >
              <div v-if="moodDetail.activity || isToday()" class="col-6">
                <div
                  class="p-3 bg-blue-50 border-round-2xl border-1 border-blue-100 shadow-sm h-full"
                >
                  <div
                    class="text-xs text-blue-600 mb-2 font-bold flex align-items-center"
                  >
                    <i class="pi pi-map-marker mr-1"></i> 建议活动
                  </div>
                  <div class="text-sm text-blue-900 font-medium">
                    {{
                      getRecommendation(calenderRef.getSelectedDay()).activity
                    }}
                  </div>
                </div>
              </div>
              <div v-if="moodDetail.food || isToday()" class="col-6">
                <div
                  class="p-3 bg-pink-50 border-round-2xl border-1 border-pink-100 shadow-sm h-full"
                >
                  <div
                    class="text-xs text-pink-600 mb-2 font-bold flex align-items-center"
                  >
                    <i class="pi pi-heart mr-1"></i> 今日美食
                  </div>
                  <div class="text-sm text-pink-900 font-medium">
                    {{ getRecommendation(calenderRef.getSelectedDay()).food }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
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
