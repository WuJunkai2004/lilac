<script setup>
import { ref } from "vue";
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";

const capturedImage = ref(null);
const letterText = ref("");
const selectedLetter = ref(null);
const showDetails = ref(false);

const mockPins = [
  {
    id: 1,
    x: 30,
    y: 40,
    image:
      "https://images.unsplash.com/photo-1541339907198-e08756ebafe3?auto=format&fit=crop&w=800&q=80",
    text: "初春的图书馆，丁香花又要开了。",
    location: "图书馆",
  },
  {
    id: 2,
    x: 60,
    y: 20,
    image:
      "https://images.unsplash.com/photo-1523050853023-8c2d27443ef8?auto=format&fit=crop&w=800&q=80",
    text: "夕阳下的教学楼，心情也变得温暖。",
    location: "一教",
  },
  {
    id: 3,
    x: 45,
    y: 70,
    image:
      "https://images.unsplash.com/photo-1498243639359-f75cb752ee47?auto=format&fit=crop&w=800&q=80",
    text: "深夜的操场，适合慢跑和发呆。",
    location: "操场",
  },
];

const recentLetters = ref([
  ...mockPins,
  {
    id: 4,
    image:
      "https://images.unsplash.com/photo-1492538368677-f6e0afe31dcc?auto=format&fit=crop&w=800&q=80",
    text: "咖啡馆里的这杯拉花，让疲惫消散了。",
    location: "学生活动中心",
    author: "Lily",
  },
]);

const takePhoto = async () => {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
    });
    capturedImage.value = image.webPath;
  } catch (error) {
    console.error("Camera failed:", error);
  }
};

const shareLetter = () => {
  if (!letterText.value.trim()) {
    console.warn("请写点什么吧");
    return;
  }
  capturedImage.value = null;
  letterText.value = "";
};

const viewLetter = (letter) => {
  selectedLetter.value = letter;
  showDetails.value = true;
};
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="校园信笺"
      subtitle="拾取校园光影，定格丁香回响"
    >
      <template #controls>
        <Button
          icon="pi pi-search"
          rounded
          severity="primary"
          class="shadow-2 w-3rem h-3rem"
        />
      </template>
    </PageHeader>
    <div class="scenery-page flex-1 overflow-y-auto px-4 bg-fuchsia-50">
      <!-- 校园地图 -->
      <SchoolMap :pins="mockPins" @pin-click="viewLetter" class="mb-5" />

      <!-- 拍摄后的编辑区域 -->
      <div v-if="capturedImage" class="edit-letter-section animate-fadein">
        <Card
          class="mb-5 border-round-3xl shadow-4 overflow-hidden border-none"
        >
          <template #header>
            <div class="relative">
              <img
                :src="capturedImage"
                alt="Captured Photo"
                class="w-full block"
              />
              <Button
                icon="pi pi-times"
                rounded
                severity="secondary"
                @click="capturedImage = null"
                class="absolute top-0 right-0 m-3 w-2.5rem h-2.5rem bg-black-alpha-50 text-white backdrop-blur-sm border-none hover:bg-black-alpha-60 transition-colors"
              />
              <Tag
                value="图书馆前广场"
                icon="pi pi-map-marker"
                class="absolute bottom-0 left-0 m-3 bg-black-alpha-40 text-white backdrop-blur-sm px-3 py-1 border-none font-medium"
              />
            </div>
          </template>
          <template #content>
            <Textarea
              v-model="letterText"
              rows="3"
              placeholder="此刻你的心情如何？"
              autoResize
              class="w-full border-none shadow-none text-lg text-surface-800 bg-transparent p-0 focus:shadow-none"
            />
          </template>
          <template #footer>
            <Divider />
            <div class="flex justify-content-between align-items-center mt-2">
              <div
                class="flex align-items-center gap-2 cursor-pointer hover:text-primary transition-colors"
              >
                <i class="pi pi-tag text-surface-400"></i>
                <span class="text-xs text-surface-400 font-bold">添加标签</span>
              </div>
              <Button
                label="分享信笺"
                icon="pi pi-share-alt"
                rounded
                @click="shareLetter"
                class="px-5 shadow-2"
              />
            </div>
          </template>
        </Card>
      </div>

      <!-- 默认展示大家的分享 -->
      <div v-else>
        <div class="flex flex-column gap-3 mb-6">
          <Button
            @click="takePhoto"
            class="w-full py-5 border-round-3xl shadow-3 transition-all transform active:scale-95 flex align-items-center justify-content-center"
          >
            <i class="pi pi-camera text-3xl mr-3"></i>
            <span class="text-xl font-bold">分享此刻风景</span>
          </Button>
        </div>

        <section>
          <div class="flex justify-content-between align-items-end mb-4 px-1">
            <h3
              class="m-0 text-xl font-bold text-surface-900 border-left-4 border-primary pl-3"
            >
              最近的丁香回响
            </h3>
            <Button
              label="查看更多"
              icon="pi pi-arrow-right"
              iconPos="right"
              text
              severity="primary"
              class="p-0 text-sm font-bold"
            />
          </div>

          <div class="grid px-1">
            <div
              v-for="letter in recentLetters"
              :key="letter.id"
              class="col-6 p-2"
            >
              <Card
                class="border-round-2xl shadow-1 overflow-hidden transition-all hover:shadow-4 cursor-pointer border-none"
                @click="viewLetter(letter)"
              >
                <template #header>
                  <div class="relative h-8rem">
                    <img
                      :src="letter.image"
                      class="w-full h-full object-cover"
                    />
                    <div class="absolute top-0 right-0 m-2">
                      <i
                        class="pi pi-heart-fill text-pink-400 text-sm drop-shadow-sm"
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
                    <i
                      class="pi pi-map-marker text-xs text-surface-400 mr-1"
                    ></i>
                    <span class="text-xxs text-surface-400 font-bold">{{
                      letter.location
                    }}</span>
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </section>
      </div>

      <!-- 查看信笺详情 -->
      <Dialog
        v-model:visible="showDetails"
        modal
        dismissableMask
        :showHeader="false"
        class="border-round-3xl overflow-hidden max-w-26rem w-full m-3 p-0"
      >
        <div v-if="selectedLetter" class="overflow-hidden">
          <div class="relative">
            <img
              :src="selectedLetter.image"
              class="w-full block h-20rem object-cover"
            />
            <Button
              icon="pi pi-times"
              rounded
              text
              severity="secondary"
              @click="showDetails = false"
              class="absolute top-0 right-0 m-3 w-2.5rem h-2.5rem bg-black-alpha-50 text-white backdrop-blur-sm border-none hover:bg-black-alpha-60 transition-colors"
            />
          </div>
          <div class="p-4 bg-surface-0">
            <div class="flex align-items-center mb-4">
              <Avatar
                icon="pi pi-user"
                class="mr-2 bg-primary-50 text-primary shadow-sm"
                shape="circle"
              />
              <span class="font-bold text-surface-900 text-lg">{{
                selectedLetter.author || "匿名校友"
              }}</span>
            </div>
            <p class="text-surface-700 line-height-4 mb-5 text-lg italic">
              "{{ selectedLetter.text }}"
            </p>
            <Divider />
            <div class="flex justify-content-between align-items-center pt-2">
              <span
                class="text-xs text-surface-400 flex align-items-center font-medium"
              >
                <i class="pi pi-clock mr-1"></i>
                {{ selectedLetter.time || "10分钟前" }}
              </span>
              <div class="flex gap-4">
                <Button
                  icon="pi pi-heart"
                  label="12"
                  text
                  severity="secondary"
                  class="p-0 text-xs gap-1 font-bold"
                />
                <Button
                  icon="pi pi-share-alt"
                  text
                  severity="secondary"
                  class="p-0"
                />
              </div>
            </div>
          </div>
        </div>
      </Dialog>
    </div>
  </div>
</template>

<style scoped>
.inset-0 {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.bg-black-alpha-40 {
  background-color: rgba(0, 0, 0, 0.4);
}

.bg-black-alpha-50 {
  background-color: rgba(0, 0, 0, 0.5);
}

.bg-black-alpha-60 {
  background-color: rgba(0, 0, 0, 0.6);
}

.bg-white-alpha-80 {
  background-color: rgba(255, 255, 255, 0.8);
}

.backdrop-blur-sm {
  backdrop-filter: blur(8px);
}

.object-cover {
  object-fit: cover;
}

.text-xxs {
  font-size: 0.65rem;
}

.animate-fadein {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.drop-shadow-sm {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.max-w-26rem {
  max-width: 26rem;
}

:deep(.p-dialog-content) {
  padding: 0 !important;
}
</style>
