<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { resCheck } from "#/check";
import storage from "#/storage";

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
          avatar: item.avatar || "/images/avatar.webp",
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
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
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
                        :class="[
                          letter.is_liked
                            ? 'pi pi-heart-fill text-pink-400'
                            : 'pi pi-heart text-white',
                          'text-sm drop-shadow-sm',
                        ]"
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
