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

    this.planeMaterial = new THREE.MeshBasicMaterial({
      map: this.texture,
      transparent: true,
      depthTest: false,
    });

    this.planeGeometry = new THREE.PlaneGeometry(
      this.planeWidth,
      this.planeHeight,
    );

    // 1. 构造非常尖锐的锐角三角形几何体
    // 顶点：A(顶点), B(左底角), C(右底角)
    // 顶点指向 (0,0,0)，底边在 X 轴负方向
    const triangleGeometry = new THREE.BufferGeometry();
    const triangleVertices = new Float32Array([
      0,
      0,
      0, // 顶点 (尖锐端)
      -50,
      3,
      0, // 底边左
      -50,
      -3,
      0, // 底边右
    ]);
    // 顶点颜色支持 Alpha 渐变 (虽然标准材质不支持 Alpha 顶点色，我们会在 Shader 中处理)
    // 这里我们用 R 通道存储该顶点的 Alpha 权重
    const triangleAlphas = new Float32Array([
      1.0, // 尖端最亮
      0.0, // 尾部透明
      0.0, // 尾部透明
    ]);

    triangleGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(triangleVertices, 3),
    );
    triangleGeometry.setAttribute(
      "vWeight",
      new THREE.BufferAttribute(triangleAlphas, 1),
    );

    // 2. 自定义着色器：结合实例透明度和顶点权重
    this.trailMaterial = new THREE.ShaderMaterial({
      transparent: true,
      depthTest: false,
      side: THREE.DoubleSide,
      vertexShader: `
        attribute float instanceAlpha;
        attribute float vWeight;
        varying float vFinalAlpha;
        void main() {
          vFinalAlpha = instanceAlpha * vWeight;
          gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying float vFinalAlpha;
        void main() {
          gl_FragColor = vec4(1.0, 1.0, 1.0, vFinalAlpha);
        }
      `,
    });

    // 3. 实例化网格
    this.maxParticles = 200;
    this.particles = [];
    this.instancedMesh = new THREE.InstancedMesh(
      triangleGeometry,
      this.trailMaterial,
      this.maxParticles,
    );

    this.instanceAlpha = new Float32Array(this.maxParticles);
    this.instancedMesh.geometry.setAttribute(
      "instanceAlpha",
      new THREE.InstancedBufferAttribute(this.instanceAlpha, 1),
    );

    this.scene.add(this.instancedMesh);

    const count = this.config.count || 3;
    for (let i = 0; i < count; i++) {
      this.createPlane(width, height, i * (2000 / count));
    }
  }

  createPlane(width, height, delay = 0) {
    const mesh = new THREE.Mesh(this.planeGeometry, this.planeMaterial);
    const planeData = {
      mesh,
      initialDelay: delay,
      startTimeSet: false,
      startTime: 0,
      duration: 4500 + Math.random() * 1000,
      pathPoints: this.generatePath(width, height),
      spawnTimer: 0,
    };
    mesh.visible = false;
    this.scene.add(mesh);
    this.planes.push(planeData);
  }

  generatePath(width, height) {
    const startX = -width / 2 - 60;
    const startY = (Math.random() - 0.5) * (height * 0.4);
    const endX = width / 2 + 100;
    const endY = height / 2 + 80;
    const cpX = startX + (endX - startX) * 0.4;
    const cpY = startY;
    return new THREE.QuadraticBezierCurve3(
      new THREE.Vector3(startX, startY, 0),
      new THREE.Vector3(cpX, cpY, 0),
      new THREE.Vector3(endX, endY, 0),
    );
  }

  update(time, { width, height }) {
    this.planes.forEach((plane) => {
      if (!plane.startTimeSet) {
        plane.startTime = time + plane.initialDelay;
        plane.startTimeSet = true;
      }
      if (time < plane.startTime) return;

      let t = (time - plane.startTime) / plane.duration;

      if (t >= 1) {
        plane.startTime = time + Math.random() * 1500;
        plane.pathPoints = this.generatePath(width, height);
        plane.mesh.visible = false;
        return;
      }

      plane.mesh.visible = true;

      // 获取当前位置
      const pos = plane.pathPoints.getPoint(t);
      plane.mesh.position.copy(pos);

      // 获取切线方向并旋转
      const tangentT = Math.min(t, 0.99);
      const tangent = plane.pathPoints.getTangent(tangentT);
      const angle = Math.atan2(tangent.y, tangent.x);
      // 顺时针旋转 30 度 (减去 PI/6)
      plane.mesh.rotation.z = angle - Math.PI / 6;

      // 生成锐角三角形尾迹
      if (time > plane.spawnTimer) {
        this.spawnSharpTriangle(pos, tangent, angle);
        plane.spawnTimer = time + 80; // 生成频率稍高
      }
    });

    // 更新粒子
    const tempMatrix = new THREE.Matrix4();
    const alphaAttr = this.instancedMesh.geometry.getAttribute("instanceAlpha");

    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.age += 16;
      const lifeRatio = p.age / p.maxAge;

      if (lifeRatio >= 1) {
        this.particles.splice(i, 1);
        continue;
      }

      // 荡开逻辑：沿法线方向轻微扩散
      p.pos.x += p.vx;
      p.pos.y += p.vy;

      // 整体透明度随寿命减弱
      const instanceAlpha = 0.7 * (1 - lifeRatio);

      tempMatrix.makeRotationZ(p.rotation);
      // 稍微随寿命变长一点
      const s = 1.0 + lifeRatio * 0.5;
      tempMatrix.scale(new THREE.Vector3(s, s, 1));
      tempMatrix.setPosition(p.pos);

      this.instancedMesh.setMatrixAt(i, tempMatrix);
      alphaAttr.setX(i, instanceAlpha);
    }

    // 隐藏不活跃实例
    const zeroMatrix = new THREE.Matrix4().makeScale(0, 0, 0);
    for (let i = this.particles.length; i < this.maxParticles; i++) {
      this.instancedMesh.setMatrixAt(i, zeroMatrix);
      alphaAttr.setX(i, 0);
    }

    this.instancedMesh.instanceMatrix.needsUpdate = true;
    alphaAttr.needsUpdate = true;
  }

  spawnSharpTriangle(pos, tangent, angle) {
    if (this.particles.length >= this.maxParticles) return;

    // 挂载点在机尾
    const offset = tangent.clone().multiplyScalar(-10);
    const spawnPos = pos.clone().add(offset);

    // 计算荡开速度：向机后方及其法线两侧
    const normal = new THREE.Vector3(-tangent.y, tangent.x, 0).normalize();
    const side = Math.random() > 0.5 ? 1 : -1;
    const spreadSpeed = 0.05 + Math.random() * 0.1;

    const vx = (normal.x * side * 0.3 - tangent.x * 0.7) * spreadSpeed;
    const vy = (normal.y * side * 0.3 - tangent.y * 0.7) * spreadSpeed;

    this.particles.push({
      pos: spawnPos,
      vx,
      vy,
      rotation: angle, // 初始方向与飞行方向一致
      age: 0,
      maxAge: 800 + Math.random() * 400,
    });
  }

  dispose() {
    super.dispose();
    this.planes.forEach((plane) => this.scene.remove(plane.mesh));
    this.scene.remove(this.instancedMesh);
    this.texture.dispose();
    this.planeMaterial.dispose();
    this.planeGeometry.dispose();
    this.instancedMesh.geometry.dispose();
    this.trailMaterial.dispose();
    this.instancedMesh.dispose();
  }
}
