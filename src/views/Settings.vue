<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";
import { resCheck, authCheck } from "#/check";
import { useAlert } from "#/alert";

const router = useRouter();
const { shows } = useAlert();

const username = ref("");
const signature = ref("");

// Dialog visibility
const showUsernameDialog = ref(false);
const showPasswordDialog = ref(false);
const showSignatureDialog = ref(false);

// Form data
const newUsername = ref("");
const newSignature = ref("");
const passwordForm = ref({
  old_password: "",
  new_password: "",
  confirm_password: "",
});

const loadUserInfo = async () => {
  const savedUser = await storage.get("user");
  const savedSignature = await storage.get("signature");

  username.value = savedUser || "未登录";
  signature.value = savedSignature || "心怀丁香，回响校园";

  newUsername.value = username.value;
  newSignature.value = signature.value;
};

onMounted(loadUserInfo);

const updateUsername = async () => {
  if (!newUsername.value) {
    shows("提示", "请输入新用户名", "warn");
    return;
  }

  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  fetch("/api/profile/username", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ username: newUsername.value }),
  })
    .then(resCheck)
    .then(authCheck)
    .then(async (res) => {
      if (res.success) {
        username.value = newUsername.value;
        await storage.set("user", newUsername.value, 0);
        // 同时更新 profile 缓存（如果有）
        const profile = await storage.get("profile");
        if (profile) {
          profile.username = newUsername.value;
          storage.set("profile", profile, 1);
        }
        shows("成功", "用户名更新成功", "success");
        showUsernameDialog.value = false;
      } else {
        shows("失败", res.message || "更新失败", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      shows("错误", "网络错误", "error");
    });
};

const updatePassword = async () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    shows("提示", "请完整填写密码信息", "warn");
    return;
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    shows("错误", "两次输入的新密码不一致", "error");
    return;
  }

  const token = await storage.get("token");
  if (!token) {
    router.push("/login");
    return;
  }

  fetch("/api/profile/password", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    }),
  })
    .then(resCheck)
    .then(authCheck)
    .then((res) => {
      if (res.success) {
        shows("成功", "密码更新成功", "success");
        showPasswordDialog.value = false;
        passwordForm.value = {
          old_password: "",
          new_password: "",
          confirm_password: "",
        };
      } else {
        shows("失败", res.message || "更新失败", "error");
      }
    })
    .catch((err) => {
      console.error(err);
      shows("错误", "网络错误", "error");
    });
};

const updateSignature = async () => {
  signature.value = newSignature.value;
  await storage.set("signature", newSignature.value, 0);
  shows("成功", "签名更新成功", "success");
  showSignatureDialog.value = false;
};

const settingsItems = [
  {
    label: "修改用户名",
    icon: "pi pi-user-edit",
    color: "text-blue-500",
    bg: "bg-blue-50",
    action: () => {
      newUsername.value = username.value;
      showUsernameDialog.value = true;
    },
  },
  {
    label: "修改头像",
    icon: "pi pi-image",
    color: "text-purple-500",
    bg: "bg-purple-50",
    action: () => router.push("/profile/avatar"),
  },
  {
    label: "修改签名",
    icon: "pi pi-pencil",
    color: "text-green-500",
    bg: "bg-green-50",
    action: () => {
      newSignature.value = signature.value;
      showSignatureDialog.value = true;
    },
  },
  {
    label: "修改密码",
    icon: "pi pi-lock",
    color: "text-orange-500",
    bg: "bg-orange-50",
    action: () => {
      passwordForm.value = {
        old_password: "",
        new_password: "",
        confirm_password: "",
      };
      showPasswordDialog.value = true;
    },
  },
];
</script>

<template>
  <div class="settings-page p-4 bg-surface-50 h-full overflow-y-auto">
    <CommonHeader
      title="用户设置"
      icon="pi pi-chevron-left"
      icon_label="Back"
      @click="router.back()"
    />

    <div class="flex flex-column gap-3 mt-4">
      <Card
        v-for="item in settingsItems"
        :key="item.label"
        class="border-round-xl shadow-1 active:surface-100 cursor-pointer transition-colors border-none"
        @click="item.action"
      >
        <template #content>
          <div class="flex align-items-center justify-content-between">
            <div class="flex align-items-center">
              <div :class="['p-2 border-round-lg mr-3 shadow-sm', item.bg]">
                <i :class="[item.icon, 'text-lg', item.color]"></i>
              </div>
              <span class="font-bold text-surface-700">{{ item.label }}</span>
            </div>
            <i class="pi pi-chevron-right text-surface-300"></i>
          </div>
        </template>
      </Card>
    </div>

    <!-- Username Dialog -->
    <Dialog
      v-model:visible="showUsernameDialog"
      header="修改用户名"
      modal
      class="w-11 max-w-25rem"
    >
      <div class="flex flex-column gap-2 py-2">
        <label for="username" class="font-semibold text-sm">新用户名</label>
        <InputText
          id="username"
          v-model="newUsername"
          autocomplete="off"
          class="w-full"
        />
      </div>
      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button
            label="取消"
            text
            severity="secondary"
            @click="showUsernameDialog = false"
          />
          <Button label="确定" @click="updateUsername" />
        </div>
      </template>
    </Dialog>

    <!-- Signature Dialog -->
    <Dialog
      v-model:visible="showSignatureDialog"
      header="修改个性签名"
      modal
      class="w-11 max-w-25rem"
    >
      <div class="flex flex-column gap-2 py-2">
        <label for="signature" class="font-semibold text-sm">新签名</label>
        <Textarea
          id="signature"
          v-model="newSignature"
          rows="3"
          class="w-full"
        />
      </div>
      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button
            label="取消"
            text
            severity="secondary"
            @click="showSignatureDialog = false"
          />
          <Button label="确定" @click="updateSignature" />
        </div>
      </template>
    </Dialog>

    <!-- Password Dialog -->
    <Dialog
      v-model:visible="showPasswordDialog"
      header="修改密码"
      modal
      class="w-11 max-w-25rem"
    >
      <div class="flex flex-column gap-3 py-2">
        <div class="flex flex-column gap-2">
          <label class="font-semibold text-sm">旧密码</label>
          <Password
            v-model="passwordForm.old_password"
            :feedback="false"
            toggleMask
            class="w-full"
            inputClass="w-full"
          />
        </div>
        <div class="flex flex-column gap-2">
          <label class="font-semibold text-sm">新密码</label>
          <Password
            v-model="passwordForm.new_password"
            toggleMask
            class="w-full"
            inputClass="w-full"
          />
        </div>
        <div class="flex flex-column gap-2">
          <label class="font-semibold text-sm">确认新密码</label>
          <Password
            v-model="passwordForm.confirm_password"
            :feedback="false"
            toggleMask
            class="w-full"
            inputClass="w-full"
          />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button
            label="取消"
            text
            severity="secondary"
            @click="showPasswordDialog = false"
          />
          <Button label="确定" @click="updatePassword" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.active\:surface-100:active {
  background-color: var(--surface-100) !important;
}

:deep(.p-password-input) {
  width: 100%;
}
</style>
