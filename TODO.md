# lilac echoes 项目进度计划

## 第一阶段：基础设施与布局 (已开始)
- [x] 初始化项目 (Vue 3 + PrimeVue + Capacitor)
- [x] 配置 GitHub Action 自动打包 Android APK
- [x] 卸载 axios，统一使用 fetch API
- [x] 搭建基础路由与底部导航栏 (Home, Calendar, Chat, Scenery, User)
- [x] 定义全局主题颜色（淡紫色调 lilac）

## 第二阶段：核心功能模块
- [ ] **首页 (情绪表达)**:
    - [ ] 动态情绪球/背景展示
    - [ ] 情绪选择与融合逻辑 (Canvas/WebGL)
- [ ] **心情日历**:
    - [ ] 基于 PrimeVue Calendar 的情绪记录展示
    - [ ] 每日情绪趋势统计
- [ ] **智能聊天 (AI)**:
    - [ ] 对接后端 AI 接口 (Fetch)
    - [ ] 实现每日 AI 与 长期 AI 切换
    - [ ] AI 总结展示
- [ ] **校园风景 (地图拍照)**:
    - [ ] 集成地图组件 (Leaflet/Mapbox)
    - [ ] 调用 Capacitor Camera 拍照并上传
    - [ ] 瀑布流展示校园动态
- [ ] **用户中心**:
    - [x] 简单登录/注册
    - [ ] 个人资料编辑与头像设置

## 第三阶段：跨平台与优化
- [ ] 适配 Android 状态栏与手势
- [ ] 性能优化 (图片压缩、资源预加载)
- [ ] 最终测试与 Bug 修复
