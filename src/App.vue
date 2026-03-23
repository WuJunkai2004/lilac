<template>
  <div
    class="app-container flex flex-column h-screen overflow-hidden bg-surface-50"
  >
    <!-- 主内容区域 -->
    <main class="main-content flex-1 overflow-y-auto">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 底部导航栏 -->
    <nav
      class="bottom-nav fixed bottom-0 left-0 w-full h-5rem bg-surface-0 flex justify-content-around align-items-center z-5"
    >
      <NavItem to="/calendar" icon="pi-calendar" label="日历" />
      <NavItem to="/chat" icon="pi-comments" label="聊天" />
      <NavItem to="/home" icon="pi-home" label="情绪" />
      <NavItem to="/scenery" icon="pi-map" label="风景" />
      <NavItem to="/profile" icon="pi-user" label="我的" />
    </nav>
  </div>
</template>

<style scoped>
.main-content {
  padding-bottom: 5rem; /* 对应导航栏高度 */
}

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
