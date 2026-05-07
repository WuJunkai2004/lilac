<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

const goBack = () => {
  router.back();
};

const handleItemClick = (item) => {
  if (item.route) {
    if (item.route.startsWith("http")) {
      window.open(item.route, "_blank");
    } else {
      router.push(item.route);
    }
  }
};

const items = [
  {
    label: "当前版本",
    value: "V 1.0.0.0401",
    arrow: false,
    icon: "pi pi-tag",
    color: "text-blue-500",
    bg: "bg-blue-100",
  },
  {
    label: "功能介绍",
    arrow: true,
    icon: "pi pi-sparkles",
    color: "text-orange-500",
    bg: "bg-orange-100",
    route: "https://github.com/WuJunkai2004/lilac",
  },
  {
    label: "官网",
    arrow: true,
    icon: "pi pi-globe",
    color: "text-indigo-500",
    bg: "bg-indigo-100",
    route: "https://github.com/WuJunkai2004/lilac",
  },
];
</script>

<template>
  <div class="about-page pt-4 px-4 bg-surface-50 h-full flex flex-column">
    <!-- 顶部导航 -->
    <CommonHeader
      title="关于"
      icon="pi pi-times"
      icon_label="Close"
      @click="goBack"
    />

    <!-- Logo 区域 -->
    <div
      class="logo-section flex flex-column align-items-center justify-content-center py-6 relative"
    >
      <div class="bg-glow absolute"></div>

      <!-- 完整 Logo 展示 -->
      <div class="logo-container z-1 mb-4">
        <img src="/logo-full.png" alt="Lilac Logo" class="logo-img" />
      </div>

      <!-- 文字标识 -->
      <h2 class="text-2xl text-surface-900 z-1 m-0 tracking-wider">
        Lilac Echoes
      </h2>
    </div>

    <!-- 列表选项 -->
    <div class="mt-4 flex flex-column gap-3">
      <Card
        v-for="item in items"
        :key="item.label"
        class="border-round-xl shadow-1 active:surface-100 cursor-pointer transition-colors border-none"
        @click="handleItemClick(item)"
      >
        <template #content>
          <div class="flex align-items-center justify-content-between">
            <div class="flex align-items-center">
              <div :class="['p-2 border-round-lg mr-3 shadow-sm', item.bg]">
                <i :class="[item.icon, 'text-lg', item.color]"></i>
              </div>
              <span class="font-bold text-surface-700">{{ item.label }}</span>
            </div>

            <div class="flex align-items-center">
              <span
                v-if="item.value"
                class="mr-2 text-sm text-surface-400 font-medium"
              >
                {{ item.value }}
              </span>
              <i
                v-if="item.arrow"
                class="pi pi-chevron-right text-surface-300 text-xs"
              ></i>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- 底部信息 -->
    <footer
      class="mt-auto py-6 text-center text-surface-400 text-xs line-height-3"
    >
      <div class="mb-2">
        基于
        <span class="text-primary-400 font-medium">Vue</span> 技术架构
      </div>
    </footer>
  </div>
</template>

<style scoped>
.bg-glow {
  width: 100%;
  height: 300px;
  top: -50px;
  background: radial-gradient(
    circle,
    rgba(168, 85, 247, 0.08) 0%,
    rgba(59, 130, 246, 0.05) 40%,
    transparent 70%
  );
  filter: blur(40px);
}

/* Logo 样式 */
.logo-img {
  width: 120px;
  height: auto;
  border-radius: 28px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s ease;
  border: 4px solid white;
}

.tracking-wider {
  letter-spacing: 0.15em;
}

.badge-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  background-color: var(--red-500);
  border-radius: 50%;
  margin-left: 6px;
  vertical-align: middle;
}

.active\:surface-100:active {
  background-color: var(--surface-100) !important;
}
</style>
