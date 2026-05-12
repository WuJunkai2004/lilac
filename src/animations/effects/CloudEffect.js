import * as THREE from "three";
import Effect from "~/core/Effect";

export default class CloudEffect extends Effect {
  init(width, height) {
    this.clouds = [];
    const loader = new THREE.TextureLoader();

    // 加载云的贴图，如果没有则会显示为白色方块（提示用户添加素材）
    this.texture = loader.load("/lilac/cloud.png");

    this.material = new THREE.SpriteMaterial({
      map: this.texture,
      transparent: true,
      opacity: 0.65,
      depthTest: false,
    });

    const count = this.config.count || 3; // 默认 3-4 朵

    for (let i = 0; i < count; i++) {
      const cloud = new THREE.Sprite(this.material);
      this.resetCloud(cloud, width, height, true);
      this.scene.add(cloud);
      this.clouds.push(cloud);
    }
  }

  resetCloud(cloud, width, height, isInitial = false) {
    // 位置：画面上方 1/6 处
    const topZoneHeight = height / 6;
    const y = height / 2 - Math.random() * topZoneHeight * 0.8 - 15;

    // x 坐标：随机分布
    const x = Math.random() * width - width / 2;

    cloud.position.set(x, y, 0);

    // 略微放大尺寸：基于宽度，长宽比为 2:1
    // 从 70-120 放大到 100-160
    const cloudWidth = 70 + Math.random() * 100;
    cloud.scale.set(cloudWidth, cloudWidth / 2, 1);

    cloud.userData = {
      baseX: x,
      swingSpeed: 0.0003 + Math.random() * 0.0004,
      swingRange: 15 + Math.random() * 20, // 缩小摆动范围
      offset: Math.random() * Math.PI * 2,
    };
  }

  update(time, { width, height }) {
    this.clouds.forEach((cloud) => {
      const { baseX, swingSpeed, swingRange, offset } = cloud.userData;

      // 左右摆动逻辑
      cloud.position.x =
        baseX + Math.sin(time * swingSpeed + offset) * swingRange;

      // 极小幅度的垂直浮动，近乎不动 (从 0.1 降至 0.02)
      cloud.position.y += Math.sin(time * swingSpeed * 1.2 + offset) * 0.02;
    });
  }

  onResize(width, height) {
    // 重新调整位置以适配新尺寸
    this.clouds.forEach((cloud) => {
      this.resetCloud(cloud, width, height, true);
    });
  }

  dispose() {
    super.dispose();
    this.clouds.forEach((cloud) => {
      this.scene.remove(cloud);
    });
    this.texture.dispose();
    this.material.dispose();
  }
}
