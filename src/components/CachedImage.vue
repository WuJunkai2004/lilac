<script setup>
import { ref, watch, onMounted } from "vue";
import imageLoader from "#/imageLoader";

const props = defineProps({
  src: {
    type: String,
    required: true,
  },
  alt: {
    type: String,
    default: "",
  },
  class: {
    type: String,
    default: "",
  },
  placeholder: {
    type: String,
    default:
      "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7", // 1x1 transparent gif
  },
});

const displaySrc = ref(props.placeholder);
const loading = ref(true);
const error = ref(false);

const loadImage = async () => {
  if (!props.src) return;

  loading.value = true;
  error.value = false;

  try {
    const cachedUrl = await imageLoader.getCachedImage(props.src);
    displaySrc.value = cachedUrl;
  } catch (e) {
    console.error("Failed to load image:", props.src, e);
    displaySrc.value = props.src; // Fallback to original URL
    error.value = true;
  } finally {
    loading.value = false;
  }
};

onMounted(loadImage);

watch(
  () => props.src,
  (newSrc) => {
    if (newSrc) {
      loadImage();
    }
  },
);

// 如果是 Blob URL，理论上在组件销毁时可以释放，
// 但因为我们可能会在多个地方使用同一个 URL，直接释放可能会导致其他地方图片失效。
// 通常 IndexedDB 管理的 Blob 我们不手动销毁，或者通过更复杂的引用计数。
// 在这个简单的实现中，我们让浏览器自动管理。
</script>

<template>
  <div class="cached-image-container" :class="props.class">
    <img
      v-if="!error"
      :src="displaySrc"
      :alt="props.alt"
      v-bind="$attrs"
      class="cached-image"
      :class="{ 'is-loading': loading }"
      @load="loading = false"
      @error="error = true"
    />
    <div
      v-else
      class="error-placeholder flex align-items-center justify-content-center bg-surface-100 text-surface-400"
    >
      <i class="pi pi-image text-2xl"></i>
    </div>

    <div
      v-if="loading && !displaySrc.startsWith('blob:')"
      class="loading-overlay"
    >
      <!-- 可以放一个微小的转圈或者渐变 -->
    </div>
  </div>
</template>

<style scoped>
.cached-image-container {
  position: relative;
  overflow: hidden;
  display: inline-block;
  width: 100%;
  height: 100%;
}

.cached-image {
  width: 100%;
  height: 100%;
  display: block;
  transition: opacity 0.3s ease;
}

.is-loading {
  opacity: 0.6;
}

.error-placeholder {
  width: 100%;
  height: 100%;
  aspect-ratio: 16/9;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
