<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";

const router = useRouter();
const user = ref(null);

const settings = [
  {
    label: "账号安全",
    icon: "pi pi-shield",
    color: "text-blue-500",
    bg: "bg-blue-50",
  },
  {
    label: "隐私设置",
    icon: "pi pi-lock",
    color: "text-green-500",
    bg: "bg-green-50",
  },
  {
    label: "我的成就",
    icon: "pi pi-trophy",
    color: "text-yellow-500",
    bg: "bg-yellow-50",
  },
  {
    label: "活动地点推荐",
    icon: "pi pi-map-marker",
    color: "text-red-500",
    bg: "bg-red-50",
  },
  {
    label: "关于 lilac echoes",
    icon: "pi pi-info-circle",
    color: "text-fuchsia-500",
    bg: "bg-fuchsia-50",
  },
];

const loadUser = async () => {
  const savedUser = await storage.get("user");
  console.log("加载用户信息:", savedUser);
  if (savedUser) {
    user.value = {
      username: savedUser,
      avatar: await storage.get("avatar"),
    };
  } else {
    user.value = null;
    router.push("/login");
  }
};

onMounted(loadUser);

const logout = async () => {
  await storage.remove("user");
  await loadUser();
  router.push("/login");
};

const changeAvatar = () => {
  alert("此处将调用摄像头/相册修改头像");
};
</script>

<template>
  <div class="profile-page p-4 bg-surface-50 h-full overflow-y-auto">
    <header class="mb-5 flex align-items-center justify-content-between">
      <h1 class="text-2xl font-bold text-surface-900 m-0">个人中心</h1>
      <Button
        v-if="user"
        icon="pi pi-sign-out"
        severity="secondary"
        text
        rounded
        @click="logout"
        aria-label="Logout"
      />
    </header>

    <div v-if="user" class="user-info-section mb-6 text-center">
      <Card class="border-round-2xl shadow-3 overflow-hidden border-none pt-4">
        <template #content>
          <div class="avatar-container relative inline-block mb-4">
            <Avatar
              :image="user.avatar || 'https://www.gravatar.com/avatar/0?d=mp'"
              class="w-8rem h-8rem shadow-3 border-3 border-primary-100"
              shape="circle"
            />
            <Button
              icon="pi pi-pencil"
              rounded
              class="absolute bottom-0 right-0 shadow-2 p-button-sm w-2.5rem h-2.5rem"
              @click="changeAvatar"
            />
          </div>
          <h2 class="text-2xl font-bold mb-1 text-surface-900">
            {{ user.username }}
          </h2>
          <p class="text-sm text-surface-500 italic mb-5">
            "心怀丁香，回响校园"
          </p>

          <Divider />

          <div class="grid mt-2 mb-2">
            <div class="col-4 border-right-1 border-surface-200">
              <div class="text-xl font-bold text-primary">12</div>
              <div class="text-xs text-surface-500 font-medium mt-1">信笺</div>
            </div>
            <div class="col-4 border-right-1 border-surface-200">
              <div class="text-xl font-bold text-primary">45</div>
              <div class="text-xs text-surface-500 font-medium mt-1">赞</div>
            </div>
            <div class="col-4">
              <div class="text-xl font-bold text-primary">7</div>
              <div class="text-xs text-surface-500 font-medium mt-1">心情</div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div v-else class="login-prompt mb-6">
      <Card class="border-round-2xl shadow-2 border-none py-6 text-center">
        <template #content>
          <i class="pi pi-user-circle text-7xl text-surface-200 mb-4"></i>
          <h3 class="text-xl font-bold mb-2">尚未登录</h3>
          <p class="text-sm text-surface-500 mb-6 px-4">
            登录后可同步你的信笺和 AI 伙伴记忆
          </p>
          <div class="flex flex-column gap-3 px-6">
            <Button
              label="登录"
              icon="pi pi-sign-in"
              @click="router.push('/login')"
              fluid
            />
            <Button
              label="注册"
              icon="pi pi-user-plus"
              severity="secondary"
              outlined
              @click="router.push('/register')"
              fluid
            />
          </div>
        </template>
      </Card>
    </div>

    <section v-if="user">
      <h3
        class="mb-4 text-lg font-bold border-left-4 border-primary pl-3 text-surface-800"
      >
        设置与工具
      </h3>
      <div class="flex flex-column gap-3">
        <div
          v-for="item in settings"
          :key="item.label"
          class="flex align-items-center justify-content-between p-3 surface-card border-round-xl shadow-1 active:surface-100 cursor-pointer transition-colors"
        >
          <div class="flex align-items-center">
            <div :class="['p-2 border-round-lg mr-3 shadow-sm', item.bg]">
              <i :class="[item.icon, 'text-lg', item.color]"></i>
            </div>
            <span class="font-bold text-surface-700">{{ item.label }}</span>
          </div>
          <i class="pi pi-chevron-right text-surface-300"></i>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.surface-card {
  background: var(--surface-0);
}

.shadow-inner {
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
}

.active\:surface-100:active {
  background-color: var(--surface-100) !important;
}
</style>
