<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";
import { useAlert } from "#/alert";
import storage from "#/storage";
import { resCheck, authCheck } from "#/check";

const router = useRouter();
const { alerts, shows } = useAlert();
import { moodTypes } from "#/mood";

// 表单数据
const capturedImage = ref(null);
const letterText = ref("");
const selectedMood = ref("宁静");
const isPublic = ref(true);
const onlyImage = ref(false);
const location = ref({ x: 50, y: 50, name: "" });

const moods = moodTypes.map((m) => ({
  label: m.type,
  icon: m.icon,
  color: m.color,
}));

const takePhoto = async (source = CameraSource.Camera) => {
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Uri, // 恢复为 Uri 以便转为 Blob
      source: source,
    });
    capturedImage.value = image.webPath;
  } catch (error) {
    console.error("Camera failed:", error);
  }
};

const handleMapClick = (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 100;
  const y = ((event.clientY - rect.top) / rect.height) * 100;
  location.value = {
    ...location.value,
    x: Math.round(x * 100) / 100,
    y: Math.round(y * 100) / 100,
  };
};

const publishLetter = async () => {
  const content = letterText.value.trim();
  // 校验逻辑：content 和 image 至少有一个非空
  if (!capturedImage.value && !content) {
    alerts("提示", "请先拍摄风景图片或写下此刻的心情");
    return;
  }

  const token = await storage.get("token");
  if (!token) {
    alerts("未登录", "请先登录后再发布信笺");
    router.push("/login");
    return;
  }

  const formData = new FormData();
  formData.append("content", content || "");
  formData.append("mood", selectedMood.value);
  formData.append("latitude", location.value.y);
  formData.append("longitude", location.value.x);
  formData.append("location", location.value.name || "校园角落");
  formData.append("is_public", isPublic.value ? 1 : 0);

  if (capturedImage.value) {
    // 将 Capacitor 的 webPath 转换为 Blob 上传
    const response = await fetch(capturedImage.value);
    const blob = await response.blob();
    formData.append("image", blob, "scenery.jpg");
  }

  fetch("/api/letter/share", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        shows("发布成功", "你的信笺已化作丁香回响，飘落在校园角落。");
        router.push("/scenery");
      } else {
        alerts("发布失败", res.message || "服务器开小差了，请稍后再试");
      }
    })
    .catch((err) => {
      console.error("Publish error:", err);
      alerts("发布失败", "网络请求异常");
    });
};

onMounted(() => {
  // 默认开启摄像头或让用户选择
});
</script>

<template>
  <div class="flex flex-column h-full">
    <PageHeader
      class="flex-shrink-0"
      title="发布信笺"
      subtitle="记录并分享此刻的校园光影"
    >
      <template #controls>
        <Button
          icon="pi pi-times"
          rounded
          text
          severity="secondary"
          @click="router.back()"
        />
      </template>
    </PageHeader>

    <div
      class="edit-scenery-page flex-1 overflow-y-auto px-4 pb-6 bg-fuchsia-50"
    >
      <!-- 图片上传/预览 -->
      <section v-if="capturedImage" class="mb-4">
        <div class="relative animate-fadein">
          <img
            :src="capturedImage"
            class="w-full border-round-3xl shadow-4 block aspect-ratio-16-9 object-cover"
          />
          <!-- 仅发布图片开关 -->
          <div
            class="absolute bottom-0 right-0 m-3 px-3 py-2 bg-black-alpha-40 backdrop-blur-sm border-round-2xl flex align-items-center gap-2"
          >
            <span class="text-xs text-white font-bold">仅发布图片</span>
            <ToggleSwitch v-model="onlyImage" class="scale-75" />
          </div>
          <!-- 操作按钮 -->
          <div class="absolute top-0 right-0 m-3 flex gap-2">
            <Button
              v-if="onlyImage"
              icon="pi pi-image"
              rounded
              severity="secondary"
              class="bg-black-alpha-50 text-white backdrop-blur-sm border-none w-2.5rem h-2.5rem"
              @click="takePhoto(CameraSource.Photos)"
            />
            <Button
              v-if="onlyImage"
              icon="pi pi-camera"
              rounded
              severity="secondary"
              class="bg-black-alpha-50 text-white backdrop-blur-sm border-none w-2.5rem h-2.5rem"
              @click="takePhoto()"
            />
            <Button
              icon="pi pi-trash"
              rounded
              severity="danger"
              class="bg-red-500-alpha-50 text-white backdrop-blur-sm border-none w-2.5rem h-2.5rem"
              @click="capturedImage = null"
            />
          </div>
        </div>
      </section>

      <!-- 文字内容 & 拍摄按钮 -->
      <section v-if="!onlyImage || !capturedImage" class="mb-4 animate-fadein">
        <Card class="border-round-3xl shadow-2 border-none">
          <template #content>
            <div class="relative pt-1">
              <Textarea
                v-model="letterText"
                placeholder="此刻的心情，或是对这片风景的感悟..."
                rows="4"
                autoResize
                class="w-full border-none shadow-none text-lg p-0 focus:shadow-none bg-transparent mb-5"
              />
              <div class="absolute bottom-0 right-0 flex gap-2">
                <Button
                  icon="pi pi-image"
                  rounded
                  severity="secondary"
                  class="w-3.5rem h-3.5rem shadow-4"
                  @click="takePhoto(CameraSource.Photos)"
                />
                <Button
                  icon="pi pi-camera"
                  rounded
                  severity="primary"
                  class="w-3.5rem h-3.5rem shadow-4"
                  @click="takePhoto()"
                />
              </div>
            </div>
          </template>
        </Card>
      </section>

      <!-- 地图选点 -->
      <section class="mb-4">
        <div class="flex align-items-center justify-content-between mb-2 px-2">
          <span class="text-sm font-bold text-gray-700">标记地点</span>
          <span class="text-xs text-primary">点击地图进行标记</span>
        </div>
        <SchoolMap
          :pins="[{ id: 'current', x: location.x, y: location.y }]"
          @map-click="handleMapClick"
        />
        <div class="mt-2 px-2">
          <InputText
            v-model="location.name"
            placeholder="为这个地点起个名字 (如：图书馆前广场)"
            class="w-full border-round-2xl text-sm"
          />
        </div>
      </section>

      <!-- 心情选择 -->
      <section class="mb-4">
        <span class="block text-sm font-bold text-gray-700 mb-3 px-2"
          >此刻心情</span
        >
        <div class="flex gap-2 overflow-x-auto pb-2 px-1 scrollbar-hidden">
          <div v-for="mood in moods" :key="mood.label" class="flex-shrink-0">
            <Button
              @click="selectedMood = mood.label"
              :severity="selectedMood === mood.label ? 'primary' : 'secondary'"
              :outlined="selectedMood !== mood.label"
              class="flex-column py-3 px-4 border-round-2xl transition-all"
            >
              <i :class="[mood.icon, 'text-xl mb-1']"></i>
              <span class="text-xs">{{ mood.label }}</span>
            </Button>
          </div>
        </div>
      </section>

      <!-- 公开设置 -->
      <section class="mb-5">
        <div
          class="p-3 bg-white-alpha-60 border-round-2xl flex align-items-center justify-content-between shadow-1"
        >
          <div class="flex align-items-center">
            <i class="pi pi-globe text-primary mr-3 text-lg"></i>
            <div>
              <div class="text-sm font-bold">公开信笺</div>
              <div class="text-xs text-muted-color">
                所有人可见并产生心情共鸣
              </div>
            </div>
          </div>
          <ToggleSwitch v-model="isPublic" />
        </div>
      </section>

      <!-- 发布按钮 -->
      <Button
        label="发布信笺"
        icon="pi pi-send"
        class="w-full py-3 border-round-3xl shadow-4 text-lg font-bold"
        @click="publishLetter"
      />
    </div>
  </div>
</template>

<style scoped>
.aspect-ratio-16-9 {
  aspect-ratio: 16 / 9;
}

.object-cover {
  object-fit: cover;
}

.bg-black-alpha-50 {
  background-color: rgba(0, 0, 0, 0.5);
}

.bg-red-500-alpha-50 {
  background-color: rgba(239, 68, 68, 0.5);
}

.backdrop-blur-sm {
  backdrop-filter: blur(8px);
}

.scrollbar-hidden::-webkit-scrollbar {
  display: none;
}

.animate-fadein {
  animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
