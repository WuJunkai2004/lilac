<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";
import { resCheck } from "#/check";

import "cropper-next-vue/style.css";
import { VueCropper } from "cropper-next-vue";

const router = useRouter();
const currentAvatar = ref("");
const selectedFile = ref(null);
const previewUrl = ref("");
const isUploading = ref(false);

const loadAvatar = async () => {
  const avatar = await storage.get("avatar");
  currentAvatar.value = avatar || "https://www.gravatar.com/avatar/0?d=mp";
};

onMounted(loadAvatar);

const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    previewUrl.value = URL.createObjectURL(file);
  }
};

const triggerFileInput = () => {
  document.getElementById("avatarInput").click();
};

const uploadAvatar = async () => {
  if (!selectedFile.value) return;

  isUploading.value = true;
  const formData = new FormData();
  formData.append("file", selectedFile.value);

  fetch("/api/user/avatar", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${await storage.get("token")}`,
    },
    body: formData,
  })
    .then(resCheck)
    .then(async (res) => {
      if (!res.success) {
        throw new Error(res.message || "上传失败");
      }
      const newAvatarUrl = res.data.avatar_url;
      // 更新本地存储，设置永不过期 (0)
      await storage.set("avatar", newAvatarUrl, 0);
      // 同时更新 profile 缓存（如果有）
      let profile = await storage.get("profile");
      if (profile) {
        profile.avatar_url = newAvatarUrl;
        await storage.set("profile", profile, 1); // profile 本身还是 1 小时过期
      }
      currentAvatar.value = newAvatarUrl;
      selectedFile.value = null;
      previewUrl.value = "";
      alert("头像上传成功！");
      router.back();
    })
    .catch((error) => {
      console.error("上传头像失败:", error);
      alert("上传失败，请稍后再试");
    })
    .finally(() => {
      isUploading.value = false;
    });
};

const goBack = () => {
  router.back();
};
</script>

<template>
  <div class="avatar-edit-page p-4 bg-surface-50 h-full flex flex-column">
    <header class="mb-5 flex align-items-center justify-content-between">
      <h1 class="text-2xl font-bold text-surface-900 m-0">修改头像</h1>
      <Button
        icon="pi pi-times"
        rounded
        text
        severity="secondary"
        @click="goBack"
        aria-label="Close"
      />
    </header>

    <div
      class="flex-grow-1 flex flex-column align-items-center justify-content-center"
    >
      <div class="preview-section mb-6 text-center">
        <p class="text-surface-500 mb-4">头像预览</p>
        <div class="avatar-display relative inline-block">
          <Avatar
            :image="previewUrl || currentAvatar"
            class="w-12rem h-12rem shadow-4 border-3 border-primary-100"
            shape="circle"
          />
          <div
            v-if="isUploading"
            class="absolute top-0 left-0 w-full h-full border-circle bg-black-alpha-40 flex align-items-center justify-content-center"
          >
            <i class="pi pi-spin pi-spinner text-4xl text-white"></i>
          </div>
        </div>
      </div>

      <input
        id="avatarInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="onFileChange"
      />

      <div class="actions flex flex-column gap-3 w-full max-w-20rem">
        <Button
          label="选择新头像"
          icon="pi pi-camera"
          severity="secondary"
          @click="triggerFileInput"
          fluid
        />
        <Button
          v-if="selectedFile"
          label="确认上传"
          icon="pi pi-upload"
          :loading="isUploading"
          @click="uploadAvatar"
          fluid
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.avatar-edit-page {
  min-height: 100vh;
}
</style>
