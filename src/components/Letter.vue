<script setup>
import { ref, watch } from "vue";
import storage from "#/storage";
import { resCheck, authCheck } from "#/check";
import imageLoader from "#/imageLoader";

const visible = defineModel("visible", { type: Boolean, default: false });
const props = defineProps({
  letter: {
    type: Object,
    default: null,
  },
});

const isLiked = ref(false);
const likesCount = ref(0);
const loading = ref(false);
const letterRef = ref(null);
const sharePreviewRef = ref(null);
const cachedAvatar = ref("");

const updateAvatar = async (avatarUrl) => {
  if (avatarUrl) {
    cachedAvatar.value = await imageLoader.getCachedImage(avatarUrl);
  } else {
    cachedAvatar.value = "";
  }
};

watch(
  () => props.letter,
  (newLetter) => {
    if (newLetter) {
      isLiked.value = newLetter.is_liked || false;
      likesCount.value = newLetter.likes || 0;
      updateAvatar(newLetter.avatar);
    }
  },
  { immediate: true },
);

const handleLike = async () => {
  if (loading.value || !props.letter) {
    return;
  }

  const token = await storage.get("token");
  if (!token) {
    console.error("未登录，无法点赞");
    return;
  }

  loading.value = true;
  fetch("/api/letter/like", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      letter_id: props.letter.id,
    }),
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        isLiked.value = res.data.is_liked;
        likesCount.value = res.data.likes_count;
        // 同步回父组件引用的对象
        if (props.letter) {
          props.letter.likes = res.data.likes_count;
          props.letter.is_liked = res.data.is_liked;
        }
      }
    })
    .catch((error) => {
      console.error("点赞失败:", error);
    })
    .finally(() => {
      loading.value = false;
    });
};

const handleShare = async () => {
  if (!letterRef.value || !sharePreviewRef.value) {
    return;
  }

  try {
    await sharePreviewRef.value.share(letterRef.value);
  } catch (error) {
    console.error("生成图片失败:", error);
  }
};
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    dismissableMask
    :showHeader="false"
    class="border-round-3xl overflow-hidden max-w-26rem w-full m-3 p-0"
  >
    <div v-if="letter" class="overflow-hidden" ref="letterRef">
      <div class="relative">
        <CachedImage
          :src="letter.image"
          class="w-full block h-20rem img-contain"
        />
        <Button
          icon="pi pi-times"
          rounded
          text
          severity="secondary"
          @click="visible = false"
          class="absolute top-0 right-0 m-3 w-2.5rem h-2.5rem bg-black-alpha-50 text-white backdrop-blur-sm border-none hover:bg-black-alpha-60 transition-colors no-share"
        />
      </div>
      <div class="p-4 bg-surface-0">
        <div class="flex align-items-center mb-4">
          <Avatar
            :image="cachedAvatar"
            class="mr-2 bg-primary-50 text-primary shadow-sm"
            shape="circle"
          />
          <span class="font-bold text-surface-900 text-lg">{{
            letter.author || "匿名校友"
          }}</span>
        </div>
        <p class="text-surface-700 line-height-4 mb-5 text-lg italic">
          "{{ letter.text }}"
        </p>
        <Divider />
        <div class="flex justify-content-between align-items-center pt-2">
          <span
            class="text-xs text-surface-400 flex align-items-center font-medium"
          >
            <i class="pi pi-clock mr-1"></i>
            {{ letter.time || "10分钟前" }}
          </span>
          <div class="flex gap-4">
            <Button
              :icon="isLiked ? 'pi pi-heart-fill' : 'pi pi-heart'"
              :label="String(likesCount)"
              text
              :severity="isLiked ? 'danger' : 'secondary'"
              class="p-0 text-xs gap-1 font-bold"
              @click="handleLike"
              :loading="loading"
            />
            <Button
              icon="pi pi-share-alt"
              text
              severity="secondary"
              class="p-0 no-share"
              @click="handleShare"
            />
          </div>
        </div>
      </div>
    </div>
  </Dialog>

  <SharePreview ref="sharePreviewRef" />
</template>

<style scoped>
.bg-black-alpha-50 {
  background-color: rgba(0, 0, 0, 0.5);
}

.bg-black-alpha-60 {
  background-color: rgba(0, 0, 0, 0.6);
}

.backdrop-blur-sm {
  backdrop-filter: blur(8px);
}

.img-contain :deep(.cached-image) {
  object-fit: contain;
  background-color: var(--surface-50);
}

.max-w-26rem {
  max-width: 26rem;
}

:deep(.p-dialog-content) {
  padding: 0 !important;
}
</style>
