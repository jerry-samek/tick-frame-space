// viewport.component.ts
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import * as THREE from 'three';
import { ViewconePacket, ViewconeService } from '../../services/viewcone.service';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

@Component({
  selector: 'app-viewport',
  template: '<div #container style="width:100%;height:100vh;"></div>'
})
export class ViewportComponent implements OnInit {
  @ViewChild('container', { static: true }) container!: ElementRef<HTMLDivElement>;

  constructor(private readonly viewcone: ViewconeService) {
  }

  ngOnInit() {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111111);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(50, 50, 150);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    this.container.nativeElement.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(1, 1, 1);
    scene.add(light);

    let instanced: THREE.InstancedMesh | null = null;

    this.viewcone.connect().subscribe((packet: ViewconePacket) => {
      let instances = 0;
      for (const b of packet.bricks) {
        instances += b.energyU8.length;
      }

      if (!instanced || instanced.count < instances) {
        if (instanced) scene.remove(instanced);
        const geo = new THREE.BoxGeometry(1, 1, 1);
        const mat = new THREE.MeshPhongMaterial({ vertexColors: true });
        instanced = new THREE.InstancedMesh(geo, mat, instances);
        scene.add(instanced);
      }

      const dummy = new THREE.Object3D();
      const color = new THREE.Color();
      let i = 0;
      for (const b of packet.bricks) {
        const [ox, oy, oz] = b.origin;
        const [dx, dy, dz] = b.dims;
        const energies = b.energyU8;
        for (let z = 0; z < dz; z++) {
          for (let y = 0; y < dy; y++) {
            for (let x = 0; x < dx; x++) {
              const idx = x + y * dx + z * dx * dy;
              const e = energies[idx];
              if (e === 0) continue;
              dummy.position.set(ox + x, oy + y, oz + z);
              dummy.updateMatrix();
              instanced!.setMatrixAt(i, dummy.matrix);
              color.setRGB(e / 255, (e / 255) * 0.5, 1.0 - e / 255);
              instanced!.setColorAt(i, color);
              i++;
            }
          }
        }
      }
      instanced!.instanceMatrix.needsUpdate = true;
      if (instanced!.instanceColor) instanced!.instanceColor.needsUpdate = true;
    });

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }

    animate();
  }
}
