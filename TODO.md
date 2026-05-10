# lilac echoes 项目进度计划

## 第一阶段：基础设施与布局
- [x] 初始化项目 (Vue 3 + PrimeVue + Capacitor)
- [x] 配置 GitHub Action 自动打包 Android APK
- [x] 卸载 axios，统一使用 fetch API
- [x] 搭建基础路由与底部导航栏 (Home, Calendar, Chat, Scenery, User)
- [x] 定义全局主题颜色（淡紫色调 lilac）

## 第二阶段：核心功能模块
- [ ] **首页 (情绪表达)**:
    - [ ] 动态情绪球/背景展示
    - [x] 全校情绪数据动态获取与聚合
- [x] **心情日历**:
    - [x] 基于 PrimeVue Calendar 的情绪记录展示
    - [x] 每日情绪趋势统计
- [ ] **智能聊天 (AI)**:
    - [x] 对接后端 AI 接口 (Fetch)
    - [x] 实现每日 AI 与 长期 AI 切换
    - [x] AI 心理状况总结展示
    - [ ] AI 个人总结
- [x] **校园风景 (地图拍照)**:
    - [x] 集成地图组件 (校园地图 + 定位标记)
    - [x] 调用 Capacitor Camera 拍照并上传
    - [x] 瀑布流展示校园动态
- [x] **用户中心**:
    - [x] 简单登录/注册
    - [x] 个人资料编辑与头像设置

## 第三阶段：跨平台与优化
- [x] 适配 Android 状态栏与手势
- [x] 性能优化 (图片压缩、资源预加载)
- [ ] 最终测试与 Bug 修复
