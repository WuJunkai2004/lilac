<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { resCheck, authCheck } from "#/check";
import storage from "#/storage";
import imageLoader from "#/imageLoader";
import { useAlert } from "#/alert";

const { shows } = useAlert();
const router = useRouter();
const selectedLetter = ref(null);
const showDetails = ref(false);

const pins = ref([]);
const recentLetters = ref([]);
const hasMore = ref(false);
const page = ref(1);
const limit = 4;

const fetchLetters = async () => {
  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  fetch("/api/letter/fetch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      page: page.value,
      limit: limit,
      keyword: "",
    }),
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        const mapped = res.data.list.map((item) => ({
          id: item.letter_id,
          x: item.longitude,
          y: item.latitude,
          image: item.image,
          text: item.content,
          location: item.location,
          author: item.username,
          avatar: item.avatar || "/image/avatar.webp",
          time: item.created_at,
          likes: item.likes_count,
          is_liked: item.is_liked,
        }));

        if (page.value === 1) {
          recentLetters.value = mapped;
        } else {
          recentLetters.value.push(...mapped);
        }

        // 只有坐标有效的才显示在地图上
        pins.value = recentLetters.value.filter(
          (p) => p.x !== undefined && p.y !== undefined,
        );
        hasMore.value = res.data.has_more;

        // 预加载图片
        imageLoader.preloadImages(mapped.map((i) => i.image).filter(Boolean));
        imageLoader.preloadImages(mapped.map((i) => i.avatar).filter(Boolean));
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      shows("加载失败", "无法获取信笺数据", "error");
    });
};

const loadMore = () => {
  if (hasMore.value) {
    page.value++;
    fetchLetters();
  }
};

const viewLetter = (letter) => {
  selectedLetter.value = letter;
  showDetails.value = true;
};

const searchLetters = (keyword) => {
  router.push("/letters/list");
};

onMounted(() => {
  fetchLetters();
});
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
          @click="searchLetters"
        />
      </template>
    </PageHeader>
    <div class="scenery-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <!-- 校园地图 -->
      <SchoolMap :pins="pins" @pin-click="viewLetter" class="mb-5" />

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
              v-if="hasMore"
              label="查看更多"
              icon="pi pi-arrow-right"
              iconPos="right"
              text
              severity="primary"
              class="p-0 text-sm font-bold"
              @click="loadMore"
            />
          </div>

          <div class="grid px-1">
            <div
              v-for="letter in recentLetters"
              :key="letter.id"
              class="col-6 p-2"
            >
              <LetterCover :letter="letter" @click="viewLetter(letter)" />
            </div>
          </div>
        </section>
      </div>

      <!-- 查看信笺详情 -->
      <Letter v-model:visible="showDetails" :letter="selectedLetter" />
    </div>
  </div>
</template>

<style scoped></style>
