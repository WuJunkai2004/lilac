import * as THREE from "three";

export default class SceneManager {
  constructor(canvas) {
    if (!canvas) throw new Error("Canvas element is required");
    this.canvas = canvas;
    this.effects = new Map();
    this.animationId = null;

    this.initThree();
  }

  initThree() {
    this.width = this.canvas.clientWidth;
    this.height = this.canvas.clientHeight;

    this.scene = new THREE.Scene();

    // 使用正交相机适配 2D UI
    this.camera = new THREE.OrthographicCamera(
      this.width / -2,
      this.width / 2,
      this.height / 2,
      this.height / -2,
      1,
      1000,
    );
    this.camera.position.z = 10;

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      alpha: true,
      antialias: true,
    });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  }

  addEffect(name, EffectClass, config = {}) {
    if (this.effects.has(name)) return;
    const effect = new EffectClass(this.scene, this.camera, config);
    effect.init(this.width, this.height);
    this.effects.set(name, effect);
    return effect;
  }

  removeEffect(name) {
    const effect = this.effects.get(name);
    if (effect) {
      effect.dispose();
      this.effects.delete(name);
    }
  }

  start() {
    const animate = () => {
      this.animationId = requestAnimationFrame(animate);
      this.render();
    };
    animate();
  }

  render() {
    const time = Date.now();
    const dimensions = { width: this.width, height: this.height };

    this.effects.forEach((effect) => {
      if (effect.active) {
        effect.update(time, dimensions);
      }
    });

    this.renderer.render(this.scene, this.camera);
  }

  onResize() {
    this.width = this.canvas.clientWidth;
    this.height = this.canvas.clientHeight;

    this.renderer.setSize(this.width, this.height);

    this.camera.left = this.width / -2;
    this.camera.right = this.width / 2;
    this.camera.top = this.height / 2;
    this.camera.bottom = this.height / -2;
    this.camera.updateProjectionMatrix();

    this.effects.forEach((effect) => effect.onResize(this.width, this.height));
  }

  dispose() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }

    this.effects.forEach((effect) => effect.dispose());
    this.effects.clear();

    this.renderer.dispose();
    this.scene.clear();
  }
}
