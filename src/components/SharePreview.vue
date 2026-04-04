<script setup>
import { ref } from "vue";
import { toPng } from "html-to-image";

const imageUrl = ref(null);

const share = async (element) => {
  if (!element) {
    throw new Error("Invalid element");
  }

  try {
    const dataUrl = await toPng(element, {
      cacheBust: true,
      backgroundColor: "#ffffff",
      filter: (node) => {
        return !(node.classList && node.classList.contains("no-share"));
      },
    });
    imageUrl.value = dataUrl;
    return dataUrl;
  } catch (error) {
    console.error("生成图片失败:", error);
    throw error;
  }
};

defineExpose({
  share,
});

const close = () => {
  imageUrl.value = null;
};
</script>

<template>
  <div
    v-if="imageUrl"
    class="share-preview-overlay fixed top-0 left-0 right-0 bottom-0 flex flex-column align-items-center justify-content-center p-4"
    @click="close"
  >
    <div class="preview-content flex flex-column align-items-center">
      <img
        :src="imageUrl"
        class="max-w-full border-round-xl shadow-8 mb-4 scalein animation-duration-300"
        style="max-height: 75vh"
        @click.stop
      />
      <div
        class="bg-black-alpha-60 text-white px-4 py-2 border-round-full backdrop-blur-md font-medium fadein animation-duration-500"
      >
        <i class="pi pi-info-circle mr-2"></i>
        请长按图片下载或分享
      </div>
    </div>
  </div>
</template>

<style scoped>
.share-preview-overlay {
  position: fixed;
  z-index: 9999;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(12px);
  cursor: pointer;
}

.backdrop-blur-md {
  backdrop-filter: blur(12px);
}
</style>
