import * as THREE from "three";
import Effect from "~/core/Effect";

export default class PaperPlaneEffect extends Effect {
  init(width, height) {
    this.planes = [];
    const loader = new THREE.TextureLoader();

    // 加载纸飞机贴图
    this.texture = loader.load("/lilac/paperplane.png");

    // 纸飞机高宽比 1:2 (宽是高的两倍)
    this.planeWidth = 40;
    this.planeHeight = 20;

    this.material = new THREE.MeshBasicMaterial({
      map: this.texture,
      transparent: true,
      depthTest: false,
    });

    this.geometry = new THREE.PlaneGeometry(this.planeWidth, this.planeHeight);

    // 轨迹材质
    this.trailMaterial = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.5,
      blending: THREE.AdditiveBlending,
    });

    const count = this.config.count || 3;

    for (let i = 0; i < count; i++) {
      this.createPlane(width, height, i * (2000 / count));
    }
  }

  createPlane(width, height, delay = 0) {
    const mesh = new THREE.Mesh(this.geometry, this.material);

    // 轨迹记录
    const maxTrailPoints = 40;
    const trailGeometry = new THREE.BufferGeometry();
    const trailPositions = new Float32Array(maxTrailPoints * 3);
    trailGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(trailPositions, 3),
    );
    const trail = new THREE.Line(trailGeometry, this.trailMaterial);

    const planeData = {
      mesh,
      trail,
      initialDelay: delay,
      startTimeSet: false,
      startTime: 0,
      duration: 2500 + Math.random() * 1000,
      pathPoints: this.generatePath(width, height),
      history: [],
      maxTrailPoints,
    };

    mesh.visible = false;
    trail.visible = false;

    this.scene.add(mesh);
    this.scene.add(trail);
    this.planes.push(planeData);
  }

  generatePath(width, height) {
    // 起点：左边中部 (在屏幕外一点)
    const startX = -width / 2 - 60;
    const startY = (Math.random() - 0.5) * (height * 0.3); // 屏幕中间 30% 区域

    // 终点：右上方
    const endX = width / 2 + 100;
    const endY = height / 2 + 60;

    // 控制点：形成向右上飞行的弧线
    // 先水平飞行一段再向上拉升，避免终点处向下俯冲
    const cpX = startX + (endX - startX) * 0.5;
    const cpY = startY;

    return new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(startX, startY, 0),
      new THREE.Vector3(cpX, cpY, 0),
      new THREE.Vector3(endX, endY, 0),
    );
  }

  update(time, { width, height }) {
    this.planes.forEach((plane) => {
      // 初始化开始时间
      if (!plane.startTimeSet) {
        plane.startTime = time + plane.initialDelay;
        plane.startTimeSet = true;
      }

      if (time < plane.startTime) return;

      let t = (time - plane.startTime) / plane.duration;

      if (t >= 1) {
        // 重置
        plane.startTime = time + Math.random() * 1000;
        plane.pathPoints = this.generatePath(width, height);
        plane.history = [];
        plane.mesh.visible = false;
        plane.trail.visible = false;
        return;
      }

      plane.mesh.visible = true;
      plane.trail.visible = true;

      // 获取当前位置
      const pos = plane.pathPoints.getPoint(t);
      plane.mesh.position.copy(pos);

      // 获取切线方向并旋转
      const tangentT = Math.min(t, 0.99);
      const tangent = plane.pathPoints.getTangent(tangentT);
      const angle = Math.atan2(tangent.y, tangent.x);
      // 顺时针旋转 30 度 (减去 PI/6)
      plane.mesh.rotation.z = angle - Math.PI / 6;

      // 更新轨迹
      plane.history.push(pos.clone());
      if (plane.history.length > plane.maxTrailPoints) {
        plane.history.shift();
      }

      const positions = plane.trail.geometry.attributes.position.array;
      for (let i = 0; i < plane.maxTrailPoints; i++) {
        const point = plane.history[i] || pos;
        positions[i * 3] = point.x;
        positions[i * 3 + 1] = point.y;
        positions[i * 3 + 2] = point.z;
      }
      plane.trail.geometry.attributes.position.needsUpdate = true;

      plane.trail.geometry.setDrawRange(0, plane.history.length);
    });
  }

  dispose() {
    super.dispose();
    this.planes.forEach((plane) => {
      this.scene.remove(plane.mesh);
      this.scene.remove(plane.trail);
      plane.trail.geometry.dispose();
    });
    this.texture.dispose();
    this.material.dispose();
    this.geometry.dispose();
    this.trailMaterial.dispose();
  }
}
