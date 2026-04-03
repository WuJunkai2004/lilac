<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";
import debounce from "#/debounce";
import { resCheck } from "#/check";
import { useAlert } from "#/alert";

import "cropper-next-vue/style.css";
import { VueCropper } from "cropper-next-vue";

const { alerts, shows } = useAlert();
const router = useRouter();
const currentAvatar = ref("");
const selectedFile = ref(null);
const cropperUrl = ref("");
const previewUrl = ref("");
const isUploading = ref(false);
const cropperRef = ref(null);

const loadAvatar = async () => {
  const avatar = await storage.get("avatar");
  currentAvatar.value = avatar || "/image/avatar.webp";
};

onMounted(loadAvatar);

const onFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    if (cropperUrl.value) {
      URL.revokeObjectURL(cropperUrl.value);
    }
    cropperUrl.value = URL.createObjectURL(file);
  }
};

const triggerFileInput = () => {
  document.getElementById("avatarInput").click();
};

const refreshPreview = debounce(async () => {
  if (cropperRef.value) {
    const blob = await cropperRef.value.getCropBlob();
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value);
    }
    previewUrl.value = URL.createObjectURL(blob);
  }
}, 300);

const uploadAvatar = async () => {
  if (!selectedFile.value || !cropperRef.value) {
    return;
  }

  isUploading.value = true;
  const formData = new FormData();

  const blob = await cropperRef.value.getCropBlob();
  formData.append("file", blob, "avatar.webp");

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
      if (cropperUrl.value) {
        URL.revokeObjectURL(cropperUrl.value);
        cropperUrl.value = "";
      }
      shows("头像上传成功", "你的新头像已经更新啦！");
      router.back();
    })
    .catch((error) => {
      console.error("上传头像失败:", error);
      alerts("错误", "上传失败，请稍后再试", {
        icon: "pi pi-exclamation-triangle",
      });
    })
    .finally(() => {
      isUploading.value = false;
    });
};

const goBack = () => {
  if (cropperUrl.value) {
    URL.revokeObjectURL(cropperUrl.value);
  }
  router.back();
};
</script>

<template>
  <div class="avatar-edit-page p-4 bg-surface-50 h-full flex flex-column">
    <CommonHeader
      title="修改头像"
      icon="pi pi-times"
      icon_label="Close"
      @click="goBack"
    />

    <div
      class="flex-grow-1 flex flex-column overflow-y-auto align-items-center justify-content-center"
      :class="[selectedFile ? '' : 'pb-8']"
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

      <div v-if="selectedFile" class="cropper-container mb-6 w-full">
        <p class="text-surface-500 mb-4 text-center">调整裁剪区域</p>
        <div class="cropper-wrapper shadow-2 border-round overflow-hidden">
          <VueCropper
            ref="cropperRef"
            :img="cropperUrl"
            :full="true"
            :crop-layout="{ width: 220, height: 220 }"
            @real-time="refreshPreview"
            output-type="webp"
          />
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
          label="确认并上传"
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

.cropper-wrapper {
  background-color: var(--surface-200);
}
</style>
