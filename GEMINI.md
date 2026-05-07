## 技术栈
使用 Vue + PrimeVue + PrimeFlex 作为前端框架和UI组件库，使用 Vite 作为构建工具，使用原生fetch进行数据请求。

## 开发规范
1. 使用 script...template...style 的单文件组件结构，保持代码清晰和模块化。
2. 使用 ES6+ 的语法特性，如箭头函数、解构赋值、模板字符串等，提升代码的可读性和简洁性。
3. 使用 PrimeVue 提供的组件库来构建用户界面，遵循其设计规范和组件使用方式。应当优先使用 PrimeVue 的组件来实现常见的UI元素，如按钮、表格、输入框等，以保持界面的一致性和美观性。
4. 使用 PrimeFlex 来实现响应式布局，确保应用在移动端设备上的良好展示。

## 对于fetch
始终使用fetch...then...catch的方式来处理fetch的结果，避免出现未处理的Promise错误。
可以从/src/utils/check.js 导入resCheck，来解析响应为JSON格式，并检查响应状态码是否为200。如果状态码不为200，则抛出一个错误。
可以从/src/utils/check.js 导入authCheck，来检查响应是否依然有效，如果无效则抛出一个错误，提示用户重新登录。

```javascript
import { resCheck, authCheck } from '#/check';
fetch(url, options)
  .then(resCheck) // 解析响应并检查状态码
  .then(authCheck) // 检查响应是否有效
  .then(res => {
    // 处理数据
  })
  .catch(error => {
    // 处理错误
    console.error('Fetch error:', error);
  });
```