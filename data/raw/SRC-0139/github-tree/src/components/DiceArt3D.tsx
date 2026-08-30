import { forwardRef, useImperativeHandle, useRef, useMemo, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter.js';
import type { ProcessImageResult } from '../workers/imageProcessor';

export interface DiceArt3DRef {
  exportGLTF: () => void;
}

interface DiceArt3DProps {
  data: ProcessImageResult;
  invert: boolean;
}

// Generate dice face textures via Canvas API
function createDiceTexture(value: number, invert: boolean): THREE.CanvasTexture {
  const canvas = document.createElement('canvas');
  const size = 128; // Resolution of each face
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  // Background
  ctx.fillStyle = invert ? '#111' : '#f0f0f0';
  ctx.fillRect(0, 0, size, size);

  // Border / rounded corner effect
  ctx.strokeStyle = invert ? '#333' : '#ddd';
  ctx.lineWidth = 4;
  ctx.strokeRect(2, 2, size - 4, size - 4);

  // Dots
  ctx.fillStyle = invert ? '#fff' : '#111';
  const dotRadius = invert ? size * 0.1 : size * 0.14;
  const positions: number[][] = [];

  const center = size / 2;
  const offset = size * 0.25;

  switch (value) {
    case 1:
      positions.push([center, center]);
      break;
    case 2:
      positions.push([center - offset, center - offset], [center + offset, center + offset]);
      break;
    case 3:
      positions.push([center - offset, center - offset], [center, center], [center + offset, center + offset]);
      break;
    case 4:
      positions.push(
        [center - offset, center - offset], [center + offset, center - offset],
        [center - offset, center + offset], [center + offset, center + offset]
      );
      break;
    case 5:
      positions.push(
        [center - offset, center - offset], [center + offset, center - offset],
        [center, center],
        [center - offset, center + offset], [center + offset, center + offset]
      );
      break;
    case 6:
      positions.push(
        [center - offset, center - offset], [center - offset, center], [center - offset, center + offset],
        [center + offset, center - offset], [center + offset, center], [center + offset, center + offset]
      );
      break;
  }

  positions.forEach(([x, y]) => {
    ctx.beginPath();
    ctx.arc(x, y, dotRadius, 0, Math.PI * 2);
    ctx.fill();
  });

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

const DiceInstancedMesh = forwardRef<THREE.InstancedMesh, { data: ProcessImageResult, invert: boolean }>(({ data, invert }, forwardedRef) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  
  useImperativeHandle(forwardedRef, () => meshRef.current!);
  
  // Create textures and materials only once
  const materials = useMemo(() => {
    return [
      new THREE.MeshStandardMaterial({ map: createDiceTexture(1, invert), roughness: 0.4 }),
      new THREE.MeshStandardMaterial({ map: createDiceTexture(6, invert), roughness: 0.4 }),
      new THREE.MeshStandardMaterial({ map: createDiceTexture(2, invert), roughness: 0.4 }),
      new THREE.MeshStandardMaterial({ map: createDiceTexture(5, invert), roughness: 0.4 }),
      new THREE.MeshStandardMaterial({ map: createDiceTexture(3, invert), roughness: 0.4 }),
      new THREE.MeshStandardMaterial({ map: createDiceTexture(4, invert), roughness: 0.4 }),
    ];
  }, [invert]);

  // Handle positioning and rotation
  useEffect(() => {
    if (!meshRef.current) return;
    
    const dummy = new THREE.Object3D();
    const diceSize = 1;
    const padding = 0.05;
    const step = diceSize + padding;
    
    // Center grid
    const offsetX = (data.gridWidth * step) / 2;
    const offsetY = (data.gridHeight * step) / 2;

    for (let y = 0; y < data.gridHeight; y++) {
      for (let x = 0; x < data.gridWidth; x++) {
        const i = y * data.gridWidth + x;
        const value = data.diceValues[i];

        dummy.position.set(
          (x * step) - offsetX + (step / 2),
          -(y * step) + offsetY - (step / 2),
          0
        );

        dummy.rotation.set(0, 0, 0);

        switch (value) {
          case 1: dummy.rotation.y = -Math.PI / 2; break;
          case 6: dummy.rotation.y = Math.PI / 2; break;
          case 2: dummy.rotation.x = Math.PI / 2; break;
          case 5: dummy.rotation.x = -Math.PI / 2; break;
          case 3: dummy.rotation.set(0, 0, 0); break;
          case 4: dummy.rotation.y = Math.PI; break;
        }

        // Slight random rotation
        dummy.rotation.x += (Math.random() - 0.5) * 0.1;
        dummy.rotation.y += (Math.random() - 0.5) * 0.1;

        dummy.updateMatrix();
        meshRef.current.setMatrixAt(i, dummy.matrix);
      }
    }
    
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, [data, invert]);

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, data.gridWidth * data.gridHeight]}
    >
      <boxGeometry args={[1, 1, 1, 4, 4, 4]} />
      {materials.map((mat, i) => (
        <primitive key={i} object={mat} attach={`material-${i}`} />
      ))}
    </instancedMesh>
  );
});

const DiceArt3D = forwardRef<DiceArt3DRef, DiceArt3DProps>(({ data, invert }, ref) => {
  const meshRef = useRef<THREE.InstancedMesh>(null);

  useImperativeHandle(ref, () => ({
    exportGLTF: () => {
      if (!meshRef.current) return;
      const exporter = new GLTFExporter();
      exporter.parse(
        meshRef.current,
        (gltf) => {
          if (gltf instanceof ArrayBuffer) {
            const blob = new Blob([gltf], { type: 'application/octet-stream' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.style.display = 'none';
            link.href = url;
            link.download = `dice-art-3d-${Date.now()}.glb`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }
        },
        (err) => console.error(err),
        { binary: true }
      );
    }
  }));

  const maxDim = Math.max(data.gridWidth, data.gridHeight);
  const cameraZ = maxDim * 1.2;

  return (
    <div className="w-full h-full relative">
      <Canvas camera={{ position: [0, 0, cameraZ], fov: 45 }} gl={{ preserveDrawingBuffer: true }}>
        <color attach="background" args={[invert ? '#111827' : '#F3F4F6']} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 10]} intensity={1} castShadow />
        
        <DiceInstancedMesh data={data} invert={invert} ref={meshRef} />
        
        <OrbitControls 
          enablePan={true} 
          enableZoom={true} 
          enableRotate={true}
          maxDistance={cameraZ * 3}
          minDistance={10}
        />
        <Environment preset="city" environmentIntensity={0.5} />
      </Canvas>
    </div>
  );
});

export default DiceArt3D;
