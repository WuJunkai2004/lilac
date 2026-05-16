import * as THREE from "three";
import Effect from "~/core/Effect";

export default class DandelionEffect extends Effect {
  init(width, height) {
    this.sprites = [];
    const loader = new THREE.TextureLoader();

    // 加载贴图
    this.texture = loader.load("/lilac/dandelion.png");

    // 使用基础材质
    this.material = new THREE.SpriteMaterial({
      map: this.texture,
      transparent: true,
      opacity: 0.8,
      depthTest: false,
    });

    const count = this.config.count || 20;

    for (let i = 0; i < count; i++) {
      const sprite = new THREE.Sprite(this.material);
      this.resetSprite(sprite, width, height, true);
      this.scene.add(sprite);
      this.sprites.push(sprite);
    }
  }

  resetSprite(sprite, width, height, isInitial = false) {
    // 初始分布或从左下区域重生
    // x: 屏幕左侧稍微靠外
    // y: 屏幕下半部分
    const xBase = isInitial
      ? Math.random() * width - width / 2
      : -width / 2 - 100;
    const yBase = isInitial
      ? (Math.random() * height) / 2 - height / 2
      : (Math.random() * height) / 4 - height / 2;

    sprite.position.set(xBase, yBase, 0);

    const scale = 12 + Math.random() * 18;
    sprite.scale.set(scale, scale, 1);

    // 降低速度：vx 为主，vy 较小
    // vx: 0.6 ~ 1.3
    // vy: 0.1 ~ 0.4
    sprite.userData = {
      vx: 0.6 + Math.random() * 0.7,
      vy: 0.1 + Math.random() * 0.3,
      swingSpeed: 0.0008 + Math.random() * 0.0015,
      swingRange: 10 + Math.random() * 20,
      rotationSpeed: (Math.random() - 0.5) * 0.015,
      offset: Math.random() * Math.PI * 2,
    };
  }

  update(time, { width, height }) {
    if (!this.lastTime) this.lastTime = time;
    const deltaTime = time - this.lastTime;
    this.lastTime = time;

    const timeRatio = deltaTime / 16.666;

    this.sprites.forEach((sprite) => {
      const { vx, vy, swingSpeed, swingRange, rotationSpeed, offset } =
        sprite.userData;

      // 基础位移，乘以 timeRatio 保证位移速度不随帧率改变
      sprite.position.x += vx * timeRatio;
      sprite.position.y += vy * timeRatio;

      // 柔和的摆动
      sprite.position.x += Math.sin(time * swingSpeed + offset) * 0.2;
      sprite.position.y += Math.cos(time * swingSpeed * 0.7 + offset) * 0.15;

      // 旋转
      sprite.material.rotation += rotationSpeed * timeRatio;

      // 边界检测
      if (
        sprite.position.x > width / 2 + 100 ||
        sprite.position.y > height / 4
      ) {
        this.resetSprite(sprite, width, height);
      }
    });
  }

  onResize(width, height) {
    // 可以在这里调整现有粒子的位置以适配新尺寸，或者直接重置超出边界的
  }

  dispose() {
    super.dispose();
    this.sprites.forEach((sprite) => {
      this.scene.remove(sprite);
    });
    this.texture.dispose();
    this.material.dispose();
  }
}
