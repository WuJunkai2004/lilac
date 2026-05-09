# lilac echoes (丁香回响)

> 基于 AI 的心理疗愈与生成式公共艺术平台

lilac echoes 是一款移动端应用，将 AI 心理陪伴与校园公共艺术相结合，帮助用户记录情绪、获得 AI 心理支持，并通过地图信笺与校园社区产生情感共鸣。

## 功能

### 心情主页

- 10 种情绪类型（喜悦、孤独、宁静、忧郁、愤怒、放松、活力、浪漫、焦虑、神秘），各具独立配色、图标与诗意语录
- 支持多情绪融合（最多 3 种），以渐变色背景可视化呈现
- 浮动气泡动画与情绪指数展示

### AI 心理陪伴

- **每日 AI**：每天一位全新的 AI 伙伴，提供即时情感支持
- **长期 AI**：持续了解用户的 AI 伙伴，建立深层共鸣
- AI 回复支持完整 Markdown 渲染（代码块、引用、列表、图片等）
- 对话历史独立保存，支持清空

### 心情日历

- 自定义日历组件，按日期颜色标注情绪类型
- AI 生成每日心理总结、推荐活动（含校内地点）与今日美食

### 校园信笺

- 校园地图选点定位，拍照 + 文字创作信笺
- 支持公开/私密切换，社区可见并产生心情共鸣
- 浏览、搜索、点赞校园动态，支持图片缓存与分享

### 用户系统

- 注册/登录，含密码强度校验
- 头像裁剪上传（220×220 WebP）
- 个人统计（信笺数、获赞数、心情天数）

## 技术栈

| 类别 | 技术 |
|------|------|
| 前端框架 | Vue 3 (Composition API) |
| UI 组件 | PrimeVue 4 + PrimeFlex + PrimeIcons |
| 构建工具 | Vite + rolldown |
| 移动端 | Capacitor 8 (Android) |
| 原生能力 | Camera、Preferences、Share、App |
| 图片处理 | cropper-next-vue、html-to-image、Cache API |
| 内容渲染 | markdown-it + DOMPurify |

## 项目结构

```
src/
├── assets/main.css          # 全局样式（丁香紫主题）
├── components/              # 8 个自定义组件
│   ├── CachedImage.vue      # 带缓存的图片组件
│   ├── Letter.vue           # 信笺详情弹窗
│   ├── MoodCalendar.vue     # 心情日历组件
│   ├── PageHeader.vue       # 页面头部
│   ├── SchoolMap.vue        # 校园地图组件
│   └── SharePreview.vue     # 分享图片生成
├── router/index.js          # 路由配置（12 条路由）
├── utils/                   # 工具模块
│   ├── alert.js             # Toast / Confirm 封装
│   ├── check.js             # Fetch 响应校验 & 401 处理
│   ├── imageLoader.js       # IndexedDB 图片缓存 & v-cached-images 指令
│   ├── markdown.js          # Markdown 渲染 + XSS 过滤
│   ├── mood.js              # 情绪类型定义与查询
│   └── storage.js           # Capacitor Preferences 封装（含过期机制）
└── views/                   # 11 个页面
    ├── Home.vue             # 心情主页
    ├── Chat.vue             # AI 聊天
    ├── Calendar.vue         # 心情日历
    ├── Scenery.vue          # 校园信笺地图
    ├── SceneryEdit.vue      # 发布信笺
    ├── LettersList.vue      # 信笺列表/搜索
    ├── Login.vue            # 登录
    ├── Register.vue         # 注册
    ├── Profile.vue          # 个人中心
    ├── ProfileAvatar.vue    # 头像编辑
    └── About.vue            # 关于
```

## 开发

```bash
npm install
npm run dev          # 开发服务器（无后端代理）
npm run debug        # 开发服务器（需 .env 中配置 dev_backend）
npm run build        # 生产构建
npm run preview      # 预览生产构建（端口 5400）
```

## Android 构建

```bash
npm run build
npx cap sync android
cd android && ./gradlew assembleRelease
```

CI/CD 通过 GitHub Actions 自动触发（推送 `VERSION.txt` 或手动 dispatch），自动签名并发布 Release。

## 后端

后端为独立的 Python 服务，API 路径 `/api/...`，图片路径 `/image/...`。可通过 `script/gen_docs.js` 从 OpenAPI spec 生成 `api.md`。

## 版本

当前版本见 `VERSION.txt`，构建时自动附加 git short hash。
