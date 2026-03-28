<script setup>
defineProps({
  pins: {
    type: Array,
    default: () => [],
  },
});

defineEmits(["pin-click", "map-click"]);
</script>

<template>
  <div
    class="school-map-wrapper relative overflow-hidden border-round-3xl shadow-3 bg-white"
    @click="$emit('map-click', $event)"
  >
    <!-- 校园地图背景：使用 w-full h-auto 确保绝对等比例，不拉伸 -->
    <img
      src="/map.webp"
      alt="School Map"
      class="block w-full h-auto pointer-events-none"
    />

    <!-- 标记点覆盖层：高度会自动跟随图片高度 -->
    <div class="pins-overlay absolute inset-0 pointer-events-none">
      <div
        v-for="pin in pins"
        :key="pin.id"
        class="absolute pointer-events-auto cursor-pointer pin-marker z-10"
        :style="{ left: pin.x + '%', top: pin.y + '%' }"
        @click.stop="$emit('pin-click', pin)"
      >
        <i class="pi pi-map-marker text-3xl text-primary drop-shadow-sm"></i>
      </div>
    </div>

    <!-- 罗盘装饰 -->
    <div class="absolute bottom-0 right-0 m-3 z-20">
      <div
        class="bg-white-alpha-80 backdrop-blur-sm shadow-1 border-circle w-2.5rem h-2.5rem flex align-items-center justify-content-center"
      >
        <i class="pi pi-compass text-primary text-xl"></i>
      </div>
    </div>
  </div>
</template>

<style scoped>
.school-map-wrapper {
  width: 100%;
  /* 移除固定 aspect-ratio，让图片决定高度 */
  background-color: #f8fafc;
}

.backdrop-blur-sm {
  backdrop-filter: blur(8px);
}

.drop-shadow-sm {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.pin-marker {
  transform: translate(-50%, -100%);
  transform-origin: bottom center;
  transition: transform 0.2s ease-out;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-tap-highlight-color: transparent;
}

.z-20 {
  z-index: 20;
}
</style>
