<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: "",
  },
});
</script>

<template>
  <div class="px-4 pt-4">
    <header
      class="page-header flex align-items-center justify-content-between mb-6"
    >
      <div>
        <h1 class="text-3xl font-bold text-primary m-0">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-muted-color m-0 mt-1">
          {{ subtitle }}
        </p>
      </div>
      <div class="header-controls">
        <slot name="controls"></slot>
      </div>
    </header>
  </div>
</template>
