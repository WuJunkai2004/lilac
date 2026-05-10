<script setup>
defineProps({
  letter: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["click"]);

const viewLetter = (item) => {
  emit("click", item);
};
</script>

<template>
  <Card
    class="border-round-2xl shadow-1 overflow-hidden transition-all hover:shadow-4 cursor-pointer border-none"
    @click="viewLetter(letter)"
  >
    <template #header>
      <div class="relative h-8rem">
        <CachedImage :src="letter.image" class="w-full h-full img-cover" />
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
      <div class="flex align-items-center pt-2 border-top-1 border-surface-100">
        <i class="pi pi-map-marker text-xs text-surface-400 mr-1"></i>
        <span class="text-xxs text-surface-400 font-bold">{{
          letter.location
        }}</span>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.img-cover :deep(.cached-image) {
  object-fit: full;
  image-rendering: smooth;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.text-xxs {
  font-size: 0.65rem;
}

.drop-shadow-sm {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}
</style>
