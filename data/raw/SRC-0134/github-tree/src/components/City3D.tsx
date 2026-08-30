import { useMemo, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";
import { CityBlock } from "@/lib/github";

const BLOCK_SPACING = 0.35;
const MAX_HEIGHT = 4;
const BLOCKS_PER_ROW = 52; // weeks in a year

function seededRandom(seed: number) {
  return ((seed * 9301 + 49297) % 233280) / 233280;
}

function Building3D({ block, position, index }: { block: CityBlock; position: [number, number, number]; index: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const height = Math.max(block.height * MAX_HEIGHT, 0.15);
  const [hovered, setHovered] = useState(false);

  // Deterministic window emissive
  const windowLights = useMemo(() => {
    const lights: { pos: [number, number, number]; lit: boolean }[] = [];
    const rows = Math.max(Math.floor(height / 0.4), 1);
    const cols = 2;
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        lights.push({
          pos: [
            (c - 0.5) * 0.12,
            -height / 2 + 0.15 + r * 0.4,
            0.151,
          ],
          lit: seededRandom(index * 31 + r * 7 + c) > 0.35,
        });
      }
    }
    return lights;
  }, [height, index]);

  return (
    <group position={position}>
      {/* Building body */}
      <mesh
        ref={meshRef}
        position={[0, height / 2, 0]}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[0.28, height, 0.28]} />
        <meshStandardMaterial
          color={hovered ? "#3a4a6b" : "#1a2540"}
          emissive={hovered ? "#2a3a5b" : "#0a1020"}
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* Windows on all 4 sides */}
      {windowLights.map((w, i) => {
        if (!w.lit) return null;
        const y = height / 2 + w.pos[1];
        return (
          <group key={i}>
            {/* Front */}
            <mesh position={[w.pos[0], y, 0.141]}>
              <planeGeometry args={[0.06, 0.08]} />
              <meshStandardMaterial color="#f5c542" emissive="#f5c542" emissiveIntensity={1.5} toneMapped={false} />
            </mesh>
            {/* Back */}
            <mesh position={[w.pos[0], y, -0.141]} rotation={[0, Math.PI, 0]}>
              <planeGeometry args={[0.06, 0.08]} />
              <meshStandardMaterial color="#f5c542" emissive="#f5c542" emissiveIntensity={1.5} toneMapped={false} />
            </mesh>
            {/* Left */}
            <mesh position={[-0.141, y, w.pos[0]]} rotation={[0, -Math.PI / 2, 0]}>
              <planeGeometry args={[0.06, 0.08]} />
              <meshStandardMaterial color="#f5c542" emissive="#f5c542" emissiveIntensity={1.5} toneMapped={false} />
            </mesh>
            {/* Right */}
            <mesh position={[0.141, y, w.pos[0]]} rotation={[0, Math.PI / 2, 0]}>
              <planeGeometry args={[0.06, 0.08]} />
              <meshStandardMaterial color="#f5c542" emissive="#f5c542" emissiveIntensity={1.5} toneMapped={false} />
            </mesh>
          </group>
        );
      })}

      {/* Antenna for tall buildings */}
      {block.height > 0.85 && (
        <group position={[0, height + 0.2, 0]}>
          <mesh>
            <cylinderGeometry args={[0.008, 0.008, 0.4]} />
            <meshStandardMaterial color="#667" />
          </mesh>
          <mesh position={[0, 0.22, 0]}>
            <sphereGeometry args={[0.025, 8, 8]} />
            <meshStandardMaterial color="#e8922d" emissive="#e8922d" emissiveIntensity={2} toneMapped={false} />
          </mesh>
        </group>
      )}

      {/* Tooltip */}
      {hovered && (
        <Html position={[0, height + 0.5, 0]} center>
          <div className="bg-popover border border-border rounded-lg px-3 py-1.5 shadow-lg pointer-events-none whitespace-nowrap">
            <div className="text-xs font-semibold text-foreground">{block.date}</div>
            <div className="text-[10px] text-muted-foreground font-mono">🏢 {block.count} commits</div>
          </div>
        </Html>
      )}
    </group>
  );
}

function Park3D({ block, position }: { block: CityBlock; position: [number, number, number] }) {
  const [hovered, setHovered] = useState(false);
  return (
    <group position={position}
      onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
      {/* Ground patch */}
      <mesh position={[0, 0.01, 0]} receiveShadow>
        <boxGeometry args={[0.3, 0.02, 0.3]} />
        <meshStandardMaterial color="#2d6b3f" />
      </mesh>
      {/* Tree trunk */}
      <mesh position={[0, 0.12, 0]}>
        <cylinderGeometry args={[0.02, 0.025, 0.2]} />
        <meshStandardMaterial color="#5c3a1e" />
      </mesh>
      {/* Tree canopy */}
      <mesh position={[0, 0.28, 0]} castShadow>
        <sphereGeometry args={[0.1, 8, 8]} />
        <meshStandardMaterial color="#33a854" emissive="#1a5c2e" emissiveIntensity={0.2} />
      </mesh>
      {hovered && (
        <Html position={[0, 0.5, 0]} center>
          <div className="bg-popover border border-border rounded-lg px-3 py-1.5 shadow-lg pointer-events-none whitespace-nowrap">
            <div className="text-xs font-semibold text-foreground">{block.date}</div>
            <div className="text-[10px] text-muted-foreground font-mono">🌳 Park day</div>
          </div>
        </Html>
      )}
    </group>
  );
}

function Bridge3D({ block, position }: { block: CityBlock; position: [number, number, number] }) {
  const [hovered, setHovered] = useState(false);
  return (
    <group position={position}
      onPointerOver={() => setHovered(true)} onPointerOut={() => setHovered(false)}>
      <mesh position={[0, 0.08, 0]}>
        <boxGeometry args={[0.4, 0.03, 0.25]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      {/* Rails */}
      <mesh position={[-0.15, 0.15, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.12]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      <mesh position={[0.15, 0.15, 0]}>
        <cylinderGeometry args={[0.01, 0.01, 0.12]} />
        <meshStandardMaterial color="#8b7355" />
      </mesh>
      {hovered && (
        <Html position={[0, 0.4, 0]} center>
          <div className="bg-popover border border-border rounded-lg px-3 py-1.5 shadow-lg pointer-events-none whitespace-nowrap">
            <div className="text-xs font-semibold text-foreground">{block.date}</div>
            <div className="text-[10px] text-muted-foreground font-mono">🌉 Bridge</div>
          </div>
        </Html>
      )}
    </group>
  );
}

function GroundPlane({ width, depth }: { width: number; depth: number }) {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[width / 2, 0, depth / 2]} receiveShadow>
      <planeGeometry args={[width + 2, depth + 2]} />
      <meshStandardMaterial color="#0f1a2e" />
    </mesh>
  );
}

function Stars3D() {
  const starsRef = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const arr = new Float32Array(200 * 3);
    for (let i = 0; i < 200; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 40;
      arr[i * 3 + 1] = 5 + Math.random() * 15;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 40;
    }
    return arr;
  }, []);

  useFrame(({ clock }) => {
    if (starsRef.current) {
      starsRef.current.rotation.y = clock.getElapsedTime() * 0.01;
    }
  });

  return (
    <points ref={starsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.05} color="#f0e6c8" sizeAttenuation />
    </points>
  );
}

interface City3DProps {
  blocks: CityBlock[];
}

export default function City3D({ blocks }: City3DProps) {
  const rows = Math.ceil(blocks.length / BLOCKS_PER_ROW);
  const gridWidth = BLOCKS_PER_ROW * BLOCK_SPACING;
  const gridDepth = rows * BLOCK_SPACING;

  return (
    <div className="w-full h-[500px] rounded-lg overflow-hidden border border-border">
      <Canvas
        shadows
        camera={{ position: [gridWidth / 2, 6, gridDepth + 6], fov: 45 }}
        gl={{ preserveDrawingBuffer: true, antialias: true }}
      >
        <color attach="background" args={["#0a0f1e"]} />
        <fog attach="fog" args={["#0a0f1e", 10, 35]} />

        {/* Lighting */}
        <ambientLight intensity={0.15} />
        <directionalLight
          position={[8, 12, 5]}
          intensity={0.4}
          castShadow
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
        />
        <pointLight position={[gridWidth / 2, 8, gridDepth / 2]} intensity={0.3} color="#e8922d" />

        <Stars3D />
        <GroundPlane width={gridWidth} depth={gridDepth} />

        {/* City blocks in grid layout */}
        {blocks.map((block, i) => {
          const col = i % BLOCKS_PER_ROW;
          const row = Math.floor(i / BLOCKS_PER_ROW);
          const pos: [number, number, number] = [col * BLOCK_SPACING, 0, row * BLOCK_SPACING];

          if (block.type === "building") return <Building3D key={i} block={block} position={pos} index={i} />;
          if (block.type === "park") return <Park3D key={i} block={block} position={pos} />;
          return <Bridge3D key={i} block={block} position={pos} />;
        })}

        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          maxPolarAngle={Math.PI / 2.1}
          minDistance={2}
          maxDistance={25}
          target={[gridWidth / 2, 0, gridDepth / 2]}
        />
      </Canvas>
    </div>
  );
}
