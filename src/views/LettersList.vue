<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { resCheck, authCheck } from "#/check";
import storage from "#/storage";

const route = useRoute();
const router = useRouter();
const selectedLetter = ref(null);
const showDetails = ref(false);

const letters = ref([]);
const hasMore = ref(false);
const page = ref(1);
const limit = 10;
const loading = ref(false);
const scope = ref("all");
const mainTitle = {
  all: "所有信笺",
  liked: "我喜欢的",
  mine: "我的信笺",
};
const searchQuery = ref("");

const fetchLetters = async (isNewSearch = false) => {
  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  if (isNewSearch) {
    page.value = 1;
    letters.value = [];
  }

  loading.value = true;
  fetch("/api/letter/fetch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      page: page.value,
      limit: limit,
      keyword: searchQuery.value,
      scope: scope.value,
    }),
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        const mapped = res.data.list.map((item) => ({
          id: item.letter_id,
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
          letters.value = mapped;
        } else {
          letters.value.push(...mapped);
        }
        hasMore.value = res.data.has_more;
      }
    })
    .catch((error) => {
      console.error("Fetch error:", error);
    })
    .finally(() => {
      loading.value = false;
    });
};

const handleSearch = () => {
  fetchLetters(true);
};

const loadMore = () => {
  if (hasMore.value && !loading.value) {
    page.value++;
    fetchLetters();
  }
};

const viewLetter = (letter) => {
  selectedLetter.value = letter;
  showDetails.value = true;
};

onMounted(() => {
  // 解析参数type
  const type = route.query.type;
  if (["all", "liked", "mine"].includes(type)) {
    scope.value = type;
  }
  fetchLetters();
});
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      :title="mainTitle[scope]"
      :subtitle="`珍藏${scope === 'mine' ? '你在' : ''}这座校园留下的每一段回响`"
    >
      <template #controls>
        <Button
          icon="pi pi-chevron-left"
          rounded
          text
          severity="secondary"
          @click="router.back()"
        />
      </template>
    </PageHeader>

    <div class="px-4 mb-3 bg-fuchsia-50">
      <div class="relative w-full">
        <IconField>
          <InputIcon class="pi pi-search" />
          <InputText
            v-model="searchQuery"
            :placeholder="`搜索${mainTitle[scope]}内容...`"
            class="w-full border-round-3xl border-none shadow-1 py-3 pl-5"
            @keyup.enter="handleSearch"
          />
        </IconField>
      </div>
    </div>

    <div class="-letters-page flex-1 overflow-y-auto px-4 bg-fuchsia-50 pb-6">
      <div v-if="letters.length > 0">
        <div class="grid px-1 mt-2">
          <div v-for="letter in letters" :key="letter.id" class="col-6 p-2">
            <Card
              class="border-round-2xl shadow-1 overflow-hidden transition-all hover:shadow-4 cursor-pointer border-none"
              @click="viewLetter(letter)"
            >
              <template #header>
                <div class="relative h-8rem">
                  <img :src="letter.image" class="w-full h-full object-cover" />
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
                  <i class="pi pi-map-marker text-xs text-surface-400 mr-1"></i>
                  <span class="text-xxs text-surface-400 font-bold">{{
                    letter.location
                  }}</span>
                </div>
              </template>
            </Card>
          </div>
        </div>

        <div v-if="hasMore" class="flex justify-content-center mt-4">
          <Button
            label="加载更多"
            icon="pi pi-refresh"
            text
            @click="loadMore"
            :loading="loading"
          />
        </div>
      </div>

      <div
        v-else-if="!loading"
        class="flex flex-column align-items-center justify-content-center py-8"
      >
        <i class="pi pi-envelope text-6xl text-surface-200 mb-4"></i>
        <p class="text-surface-400 font-medium">你还没有发布过信笺哦</p>
        <Button
          label="去分享风景"
          icon="pi pi-camera"
          class="mt-4 border-round-3xl"
          @click="router.push('/scenery/edit')"
        />
      </div>

      <div v-else class="flex justify-content-center py-8">
        <ProgressSpinner />
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
