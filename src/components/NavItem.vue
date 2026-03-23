<script setup>
defineProps({
  to: {
    type: String,
    required: true,
  },
  icon: {
    type: String,
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
});
</script>

<template>
  <router-link
    :to="to"
    class="nav-item flex flex-column align-items-center no-underline transition-all transition-duration-200"
  >
    <i :class="['pi', icon, 'text-xl mb-1']"></i>
    <span class="text-xs font-bold">{{ label }}</span>
  </router-link>
</template>

<style scoped>
.nav-item {
  color: var(--p-surface-400);
  width: 20%;
  -webkit-tap-highlight-color: transparent;
}

/* 移除所有 hover 或 active 时的颜色变化，由父组件控制 */
.nav-item:hover,
.nav-item:active,
.nav-item:focus {
  color: inherit;
  background-color: transparent;
}

.router-link-active {
  color: var(--p-primary-color) !important;
}

.router-link-active i {
  transform: translateY(-2px);
  transition: transform 0.3s ease;
}
</style>
