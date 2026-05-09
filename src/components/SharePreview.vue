<script setup>
import { ref } from "vue";
import { toPng } from "html-to-image";
import { Share } from "@capacitor/share";

const imageUrl = ref(null);

const share = async (element) => {
  if (!element) {
    throw new Error("Invalid element");
  }

  try {
    const dataUrl = await toPng(element, {
      cacheBust: false,
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

const downloadImage = () => {
  if (!imageUrl.value) {
    return;
  }
  const link = document.createElement("a");
  link.download = `lilac-share-${new Date().getTime()}.png`;
  link.href = imageUrl.value;
  link.click();
};

const handleShare = async () => {
  if (!imageUrl.value) {
    return;
  }
  try {
    await Share.share({
      title: "分享图片",
      text: "来自 Lilac Echoes 的分享",
      files: [imageUrl.value],
      dialogTitle: "分享到",
    });
  } catch (error) {
    console.error("分享失败:", error);
    // 如果用户取消分享，通常会进入这里，可以不做特别处理
  }
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
      <div class="flex gap-3">
        <Button
          label="保存图片"
          icon="pi pi-download"
          class="p-button-rounded p-button-lg p-button-outlined text-white border-white shadow-5 fadein animation-duration-500"
          @click.stop="downloadImage"
        />
        <Button
          label="立即分享"
          icon="pi pi-share-alt"
          class="p-button-rounded p-button-lg shadow-5 fadein animation-duration-500"
          @click.stop="handleShare"
        />
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
