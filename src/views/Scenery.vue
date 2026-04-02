<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const selectedLetter = ref(null);
const showDetails = ref(false);

const mockPins = [
  {
    id: 1,
    x: 30,
    y: 40,
    image:
      "https://images.unsplash.com/photo-1541339907198-e08756ebafe3?auto=format&fit=crop&w=800&q=80",
    text: "初春的图书馆，丁香花又要开了。",
    location: "图书馆",
  },
  {
    id: 2,
    x: 60,
    y: 20,
    image:
      "https://images.unsplash.com/photo-1523050853023-8c2d27443ef8?auto=format&fit=crop&w=800&q=80",
    text: "夕阳下的教学楼，心情也变得温暖。",
    location: "一教",
  },
  {
    id: 3,
    x: 45,
    y: 70,
    image:
      "https://images.unsplash.com/photo-1498243639359-f75cb752ee47?auto=format&fit=crop&w=800&q=80",
    text: "深夜的操场，适合慢跑和发呆。",
    location: "操场",
  },
];

const recentLetters = ref([
  ...mockPins,
  {
    id: 4,
    image:
      "https://images.unsplash.com/photo-1492538368677-f6e0afe31dcc?auto=format&fit=crop&w=800&q=80",
    text: "咖啡馆里的这杯拉花，让疲惫消散了。",
    location: "学生活动中心",
    author: "Lily",
  },
]);

const viewLetter = (letter) => {
  selectedLetter.value = letter;
  showDetails.value = true;
};
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="校园信笺"
      subtitle="拾取校园光影，定格丁香回响"
    >
      <template #controls>
        <Button
          icon="pi pi-search"
          rounded
          severity="primary"
          class="shadow-2 w-3rem h-3rem"
        />
      </template>
    </PageHeader>
    <div class="scenery-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <!-- 校园地图 -->
      <SchoolMap :pins="mockPins" @pin-click="viewLetter" class="mb-5" />

      <!-- 默认展示大家的分享 -->
      <div>
        <div class="flex flex-column gap-3 mb-6">
          <Button
            @click="router.push('/scenery/edit')"
            class="w-full py-5 border-round-3xl shadow-3 transition-all transform active:scale-95 flex align-items-center justify-content-center"
          >
            <i class="pi pi-camera text-3xl mr-3"></i>
            <span class="text-xl font-bold">分享此刻风景</span>
          </Button>
        </div>

        <section>
          <div class="flex justify-content-between align-items-end mb-4 px-1">
            <h3
              class="m-0 text-xl font-bold text-surface-900 border-left-4 border-primary pl-3"
            >
              最近的丁香回响
            </h3>
            <Button
              label="查看更多"
              icon="pi pi-arrow-right"
              iconPos="right"
              text
              severity="primary"
              class="p-0 text-sm font-bold"
            />
          </div>

          <div class="grid px-1">
            <div
              v-for="letter in recentLetters"
              :key="letter.id"
              class="col-6 p-2"
            >
              <Card
                class="border-round-2xl shadow-1 overflow-hidden transition-all hover:shadow-4 cursor-pointer border-none"
                @click="viewLetter(letter)"
              >
                <template #header>
                  <div class="relative h-8rem">
                    <img
                      :src="letter.image"
                      class="w-full h-full object-cover"
                    />
                    <div class="absolute top-0 right-0 m-2">
                      <i
                        class="pi pi-heart-fill text-pink-400 text-sm drop-shadow-sm"
                      ></i>
                    </div>
                  </div>
                </template>
                <template #content>
                  <p
                    class="text-xs text-surface-700 m-0 line-height-3 h-3rem overflow-hidden text-overflow-ellipsis font-medium"
                  >
                    {{ letter.text }}
                  </p>
                </template>
                <template #footer>
                  <div
                    class="flex align-items-center pt-2 border-top-1 border-surface-100"
                  >
                    <i
                      class="pi pi-map-marker text-xs text-surface-400 mr-1"
                    ></i>
                    <span class="text-xxs text-surface-400 font-bold">{{
                      letter.location
                    }}</span>
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </section>
      </div>

      <!-- 查看信笺详情 -->
      <Letter v-model:visible="showDetails" :letter="selectedLetter" />
    </div>
  </div>
</template>

<style scoped>
.object-cover {
  object-fit: cover;
}

.text-xxs {
  font-size: 0.65rem;
}

.drop-shadow-sm {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}
</style>
