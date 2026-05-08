import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    // 根路径重定向到 /home
    path: "/",
    redirect: "/home",
  },
  {
    // 直接访问 /home 加载 Home 组件
    path: "/home",
    name: "Home",
    component: () => import("@/views/Home.vue"),
  },
  {
    // 情绪日历功能，用户可以记录每天的情绪状态，并查看历史记录。
    path: "/calendar",
    name: "Calendar",
    component: () => import("@/views/Calendar.vue"),
  },
  {
    // 聊天功能，用户可以与 AI 进行对话，获取情绪支持和建议。
    path: "/chat",
    name: "Chat",
    component: () => import("@/views/Chat.vue"),
  },
  {
    path: "/scenery",
    name: "Scenery",
    component: () => import("@/views/Scenery.vue"),
  },
  {
    // 风景编辑页面，用户可以上传和编辑自己的风景图片，作为情绪日记的一部分。
    path: "/scenery/edit",
    name: "SceneryEdit",
    component: () => import("@/views/SceneryEdit.vue"),
  },
  {
    // 用户个人资料页面，用户可以查看和编辑自己的信息。
    path: "/profile",
    name: "Profile",
    component: () => import("@/views/Profile.vue"),
  },
  {
    // 修改头像页面
    path: "/profile/avatar",
    name: "ProfileAvatar",
    component: () => import("@/views/ProfileAvatar.vue"),
  },
  {
    // 信笺搜索页面
    path: "/letters/list",
    name: "LettersList",
    component: () => import("@/views/LettersList.vue"),
  },
  {
    // 关于页面
    path: "/about",
    name: "About",
    component: () => import("@/views/About.vue"),
  },
  {
    // 登录页面，当用户访问个人资料或其他需要认证的页面时，如果未登录，会被重定向到登录页面。
    path: "/login",
    name: "Login",
    component: () => import("@/views/Login.vue"),
  },
  {
    // 注册页面，用户可以创建一个新账户以使用应用的功能。
    path: "/register",
    name: "Register",
    component: () => import("@/views/Register.vue"),
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
