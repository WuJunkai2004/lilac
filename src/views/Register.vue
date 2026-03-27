<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAlert } from "#/alert";
import storage from "#/storage";

const router = useRouter();
const { alerts, shows } = useAlert();

const username = ref("");
const password = ref("");
const confirmPassword = ref("");

const isValid = () => {
  if (!username.value) {
    alerts("提示", "请输入用户名");
    return false;
  }

  if (!password.value) {
    alerts("提示", "请输入密码");
    return false;
  }

  if (password.value !== confirmPassword.value) {
    alerts("提示", "两次输入的密码不一致");
    return false;
  }

  // 只能有字母、数字和下划线，且长度为3-16
  const usernameRegex = /^[a-zA-Z0-9_]{5,15}$/;
  // 密码必须至少8位，包含至少一个字母和一个数字
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,31}$/; // 最少8位，至少1个字母和1个数字

  if (usernameRegex.test(username.value)) {
    alerts("提示", "用户名必须为5-15位字母、数字或下划线");
    return false;
  }

  if (passwordRegex.test(password.value)) {
    alerts("提示", "密码必须至少8位，包含至少一个字母和一个数字，且不超过31位");
    return false;
  }

  return true;
};

const register = () => {
  if (!isValid()) {
    return;
  }

  fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: username.value,
      password: password.value,
    }),
  })
    .then((res) => res.json())
    .then(async (data) => {
      if (data.success) {
        await storage.set("token", data.token, 0);
        shows("注册成功", "欢迎加入，" + data.username + "！");
        router.push("/profile");
      } else {
        alerts("注册失败", data.message || "用户名已存在");
      }
    })
    .catch(() => {
      alerts("注册失败", "网络错误，请稍后再试");
    });
};
</script>

<template>
  <div
    class="register-page p-4 flex flex-column justify-content-center h-full overflow-y-auto bg-fuchsia-50"
  >
    <Card class="w-full max-w-28rem mx-auto shadow-4 border-round-xl">
      <template #title>
        <div class="text-center">
          <h1 class="text-3xl font-bold text-primary mb-2">注册新账号</h1>
          <p class="text-muted-color text-sm font-normal">
            开始你的心理疗愈与艺术分享
          </p>
        </div>
      </template>
      <template #content>
        <div class="flex flex-column gap-4 mt-2">
          <div class="flex flex-column gap-2">
            <label for="username" class="font-semibold text-sm">用户名</label>
            <InputText
              id="username"
              v-model="username"
              type="text"
              placeholder="请输入用户名"
              fluid
            />
          </div>
          <div class="flex flex-column gap-2">
            <label for="password" class="font-semibold text-sm">设置密码</label>
            <Password
              id="password"
              v-model="password"
              toggleMask
              placeholder="请输入密码"
              promptLabel="请填写密码"
              weakLabel="弱密码"
              mediumLabel="中等密码"
              strongLabel="强密码"
              fluid
            />
          </div>
          <div class="flex flex-column gap-2">
            <label for="confirmPassword" class="font-semibold text-sm"
              >确认密码</label
            >
            <Password
              id="confirmPassword"
              v-model="confirmPassword"
              :feedback="false"
              toggleMask
              placeholder="请再次输入密码"
              fluid
            />
          </div>

          <Button
            label="注册"
            icon="pi pi-user-plus"
            @click="register"
            class="mt-2"
            fluid
          />
        </div>
      </template>
      <template #footer>
        <div class="text-center text-sm">
          <span class="text-muted-color">已经有账号？</span>
          <router-link
            to="/login"
            class="text-primary font-semibold no-underline ml-1 hover:underline"
          >
            直接登录
          </router-link>
        </div>
      </template>
    </Card>
  </div>
</template>
