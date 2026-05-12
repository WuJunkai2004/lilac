export default class Effect {
  constructor(scene, camera, config = {}) {
    this.scene = scene;
    this.camera = camera;
    this.config = config;
    this.active = true;
  }

  /**
   * 初始化资源 (贴图, 材质, 物体)
   * @param {number} width 初始宽度
   * @param {number} height 初始高度
   */
  init(width, height) {}

  /**
   * 每帧更新逻辑
   * @param {number} time 当前总时间
   * @param {Object} dimensions 屏幕尺寸 { width, height }
   */
  update(time, dimensions) {}

  /**
   * 处理窗口尺寸变化
   */
  onResize(width, height) {}

  /**
   * 销毁资源，从场景中移除物体
   */
  dispose() {
    this.active = false;
  }
}
