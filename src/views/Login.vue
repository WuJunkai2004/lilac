<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAlert } from "#/alert";
import storage from "#/storage";

const router = useRouter();
const { alerts, shows } = useAlert();

const username = ref("");
const password = ref("");

const login = () => {
  if (!username.value) {
    alerts("提示", "请输入用户名");
    return;
  }
  if (!password.value) {
    alerts("提示", "请输入密码");
    return;
  }

  fetch("/api/login", {
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
        shows("登录成功", "欢迎回来，" + data.username + "！");
        router.push("/profile");
      } else {
        alerts("登录失败", data.message || "用户名或密码错误");
      }
    })
    .catch(() => {
      alerts("登录失败", "网络错误，请稍后再试");
    });
};
</script>

<template>
  <div
    class="login-page p-4 flex flex-column justify-content-center h-full overflow-y-auto bg-fuchsia-50"
  >
    <Card class="w-full max-w-25rem mx-auto shadow-4 border-round-xl">
      <template #title>
        <div class="text-center">
          <h1 class="text-3xl font-bold text-primary mb-2">lilac echoes</h1>
          <p class="text-muted-color text-sm font-normal">
            登录以继续你的心理疗愈之旅
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
            <label for="password" class="font-semibold text-sm">密码</label>
            <Password
              id="password"
              v-model="password"
              :feedback="false"
              toggleMask
              placeholder="请输入密码"
              fluid
            />
          </div>

          <Button
            label="登录"
            icon="pi pi-sign-in"
            @click="login"
            class="mt-2"
            fluid
          />
        </div>
      </template>
      <template #footer>
        <div class="text-center text-sm">
          <span class="text-muted-color">没有账号？</span>
          <router-link
            to="/register"
            class="text-primary font-semibold no-underline ml-1 hover:underline"
          >
            立即注册
          </router-link>
        </div>
      </template>
    </Card>
  </div>
</template>
