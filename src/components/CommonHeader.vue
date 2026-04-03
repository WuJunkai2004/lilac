<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  icon: {
    type: String,
    default: "",
  },
  icon_label: {
    type: String,
    default: "",
  },
});

defineEmits(["click"]);
</script>

<template>
  <header class="mb-3 flex align-items-center justify-content-between">
    <h1 class="text-2xl font-bold text-surface-900 m-0">{{ title }}</h1>
    <Button
      v-if="icon"
      :icon="icon"
      rounded
      text
      severity="secondary"
      @click="$emit('click')"
      :aria-label="icon_label || title"
    />
  </header>
</template>
