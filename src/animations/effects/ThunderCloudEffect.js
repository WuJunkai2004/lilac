import * as THREE from "three";
import Effect from "~/core/Effect";

export default class ThunderCloudEffect extends Effect {
  init(width, height) {
    const loader = new THREE.TextureLoader();

    // 使用专属雷云贴图
    this.texture = loader.load("/lilac/thunder.png");

    // 取消滤镜
    this.material = new THREE.SpriteMaterial({
      map: this.texture,
      transparent: true,
      opacity: 0.8,
      depthTest: false,
    });

    this.cloud = new THREE.Sprite(this.material);
    this.resetCloud(this.cloud, width, height);
    this.scene.add(this.cloud);
  }

  resetCloud(cloud, width, height) {
    // 位置：画面右上角，上方 1/5 处
    // x 坐标：在右侧 1/4 区域内
    const x = width / 2 - width / 4 + (Math.random() * width) / 8;
    // y 坐标：上方 1/5 处
    const topZoneHeight = height / 5;
    const y = height / 2 - Math.random() * topZoneHeight * 0.5 - 20;

    cloud.position.set(x, y, 1); // 稍微在其他云层前面

    // 尺寸：比普通云略大
    const cloudWidth = 150 + Math.random() * 50;
    cloud.scale.set(cloudWidth, cloudWidth / 2, 1);

    cloud.userData = {
      baseX: x,
      baseY: y,
      swingSpeed: 0.0005,
      swingRangeX: 20,
      swingRangeY: 10,
      offset: Math.random() * Math.PI * 2,
    };
  }

  update(time, { width, height }) {
    if (!this.cloud) return;

    const { baseX, baseY, swingSpeed, swingRangeX, swingRangeY, offset } =
      this.cloud.userData;

    // 左右飘荡
    this.cloud.position.x =
      baseX + Math.sin(time * swingSpeed + offset) * swingRangeX;

    // 上下飘荡
    this.cloud.position.y =
      baseY + Math.cos(time * swingSpeed * 0.8 + offset) * swingRangeY;
  }

  onResize(width, height) {
    if (this.cloud) {
      this.resetCloud(this.cloud, width, height);
    }
  }

  dispose() {
    super.dispose();
    if (this.cloud) {
      this.scene.remove(this.cloud);
    }
    if (this.texture) this.texture.dispose();
    if (this.material) this.material.dispose();
  }
}
