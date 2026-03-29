<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import storage from "#/storage";
import { resCheck } from "#/check";

const router = useRouter();
const user = ref(null);

const settings = [
  {
    label: "我的信笺",
    icon: "pi pi-envelope",
    color: "text-yellow-500",
    bg: "bg-yellow-50",
  },
  {
    label: "用户设置",
    icon: "pi pi-cog",
    color: "text-blue-500",
    bg: "bg-blue-50",
  },
  {
    label: "关于 lilac echoes",
    icon: "pi pi-info-circle",
    color: "text-fuchsia-500",
    bg: "bg-fuchsia-50",
  },
];

const loadUser = async () => {
  const savedToken = await storage.get("token");
  if (!savedToken) {
    user.value = null;
    router.push("/login");
    return;
  }

  // 1. 尝试从 storage 获取 profile (有效期 1 小时)
  const profile = await storage.get("profile");
  if (profile) {
    // 如果有缓存，直接设置
    user.value = {
      username: profile.username,
      avatar: profile.avatar_url,
      letterCount: profile.letter_count || 0,
      totalLikes: profile.total_likes || 0,
      moodDayCount: profile.mood_day_count || 0,
    };
    return;
  }
  // 2. 如果不存在或过期，从网络获取
  fetch("/api/user/profile", {
    method: "GET",
    headers: {
      Authorization: `Bearer ${savedToken}`,
    },
  })
    .then(resCheck)
    .then(async (res) => {
      if (!res.success) {
        throw new Error(res.message || "获取个人资料失败");
      }
      const data = res.data;
      // 3. 存入 storage，有效期 1 小时
      storage.set("profile", data, 1);
      // 更新长期存储的头像
      if (data.avatar_url) {
        storage.set("avatar", data.avatar_url, 0);
      }

      user.value = {
        username: data.username,
        avatar: data.avatar_url,
        letterCount: data.letter_count || 0,
        totalLikes: data.total_likes || 0,
        moodDayCount: data.mood_day_count || 0,
      };
    })
    .catch(async (error) => {
      console.error("加载个人资料失败:", error);
      // 降级处理：仅展示基础信息
      user.value = {
        username: await storage.get("user"),
        avatar: await storage.get("avatar"),
        letterCount: 0,
        totalLikes: 0,
        moodDayCount: 0,
      };
    });
};

onMounted(loadUser);

const logout = async () => {
  await storage.remove("user");
  await storage.remove("profile");
  await storage.remove("avatar");
  user.value = null;
  router.push("/login");
};

const changeAvatar = () => {
  router.push("/profile/avatar");
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
              :image="user.avatar || '/image/avatar.webp'"
              class="w-8rem h-8rem shadow-3 border-3 border-primary-100"
              shape="circle"
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
              <div class="text-xl font-bold text-primary">
                {{ user.letterCount }}
              </div>
              <div class="text-xs text-surface-500 font-medium mt-1">信笺</div>
            </div>
            <div class="col-4 border-right-1 border-surface-200">
              <div class="text-xl font-bold text-primary">
                {{ user.totalLikes }}
              </div>
              <div class="text-xs text-surface-500 font-medium mt-1">赞</div>
            </div>
            <div class="col-4">
              <div class="text-xl font-bold text-primary">
                {{ user.moodDayCount }}
              </div>
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
