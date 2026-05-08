<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { App } from "@capacitor/app";

const route = useRoute();
const router = useRouter();

const HomeRoute = ["/", "/home"];
const RootRoute = [
  "/calendar",
  "/chat",
  "/scenery",
  "/profile",
  "/login",
  "/register",
];

const enableFooter = computed(() => {
  const showFooterRoutes = [...HomeRoute, ...RootRoute];
  console.log("当前路由:", route.path);
  return showFooterRoutes.includes(route.path);
});

onMounted(() => {
  App.addListener("backButton", ({ canGoBack }) => {
    if (HomeRoute.includes(route.path)) {
      App.exitApp();
      return;
    }
    if (RootRoute.includes(route.path)) {
      router.push("/home");
      return;
    }
    router.back();
  });
});
</script>

<template>
  <div
    class="app-container flex flex-column h-screen overflow-hidden bg-surface-50"
  >
    <!-- 主内容区域 -->
    <main class="main-content flex-1 flex flex-column overflow-hidden">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 底部导航栏 -->
    <nav
      v-if="enableFooter"
      class="bottom-nav w-full h-4rem bg-surface-0 flex justify-content-around align-items-center z-5 shadow-5"
    >
      <NavItem to="/calendar" icon="pi-calendar" label="日历" />
      <NavItem to="/chat" icon="pi-comments" label="聊天" />
      <NavItem to="/home" icon="pi-home" label="情绪" />
      <NavItem to="/scenery" icon="pi-map" label="风景" />
      <NavItem to="/profile" icon="pi-user" label="我的" />
    </nav>
  </div>
  <ConfirmDialog />
  <Toast />
</template>

<style scoped>
.bottom-nav {
  transition: box-shadow 0.3s ease;
}

.bottom-nav:focus-within {
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
}

/* 页面切换动画，不可去掉 */
.page-enter-active,
.page-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.bg-surface-0 {
  background-color: var(--p-surface-0);
}
</style>
