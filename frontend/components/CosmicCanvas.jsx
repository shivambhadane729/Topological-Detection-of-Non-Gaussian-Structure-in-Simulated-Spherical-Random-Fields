'use client';

import { useEffect, useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Float, Line, Sparkles, Stars } from '@react-three/drei';
import * as THREE from 'three';

const TARGETS = {
  bang: [0, 0, 8],
  expansion: [0, 0.3, 8.5],
  cmb: [0, 0, 6.6],
  patterns: [0, 0, 6.2],
  stats: [0, 0, 8.8],
  topology: [0, 0, 7.2],
  engine: [0, 0, 6.4],
  detected: [0, 0, 6.8],
  ending: [0, 0, 9.2],
};

function makeCmbTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, '#080808');
  gradient.addColorStop(0.45, '#1a1a1a');
  gradient.addColorStop(1, '#050505');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < 5200; i += 1) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const radius = Math.random() * 12 + 2;
    const hot = Math.random() > 0.5;
    const alpha = 0.03 + Math.random() * 0.08;
    const color = hot ? `hsla(0, 0%, ${70 + Math.random() * 18}%, ${alpha})` : `hsla(0, 0%, ${55 + Math.random() * 18}%, ${alpha})`;
    const noise = ctx.createRadialGradient(x, y, 0, x, y, radius);
    noise.addColorStop(0, color);
    noise.addColorStop(1, 'transparent');
    ctx.fillStyle = noise;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.needsUpdate = true;
  return texture;
}

function CameraRig({ sceneKey }) {
  const { camera } = useThree();
  const cameraTarget = useRef(new THREE.Vector3(...TARGETS[sceneKey]));
  const lookTarget = useRef(new THREE.Vector3(0, 0, 0));

  useEffect(() => {
    cameraTarget.current.set(...TARGETS[sceneKey]);
  }, [sceneKey]);

  useFrame((state, delta) => {
    camera.position.lerp(cameraTarget.current, 0.05);
    camera.lookAt(lookTarget.current);
    camera.position.x += Math.sin(state.clock.elapsedTime * 0.3) * 0.0015;
    camera.position.y += Math.cos(state.clock.elapsedTime * 0.25) * 0.0012;
  });

  return null;
}

function BigBangScene() {
  const core = useRef();
  const shell = useRef();

  useFrame((state, delta) => {
    if (core.current) {
      core.current.rotation.y += delta * 0.2;
      core.current.rotation.x += delta * 0.06;
      core.current.scale.setScalar(1.05 + Math.sin(state.clock.elapsedTime * 2.2) * 0.04);
    }
    if (shell.current) {
      shell.current.rotation.z -= delta * 0.1;
      shell.current.scale.setScalar(1.15 + Math.sin(state.clock.elapsedTime * 1.1) * 0.05);
    }
  });

  return (
    <group>
      <Sparkles count={220} scale={10} size={3.2} speed={0.55} color="#ffffff" />
      <group ref={shell}>
        <mesh>
          <sphereGeometry args={[1.45, 64, 64]} />
          <meshBasicMaterial color="#ffffff" transparent opacity={0.12} />
        </mesh>
      </group>
      <group ref={core}>
        <mesh>
          <sphereGeometry args={[0.85, 64, 64]} />
          <meshPhysicalMaterial color="#f5f5f5" emissive="#ffffff" emissiveIntensity={0.6} roughness={0.12} metalness={0.05} transparent opacity={0.9} />
        </mesh>
        <mesh>
          <ringGeometry args={[1.3, 1.55, 96]} />
          <meshBasicMaterial color="#e5e5e5" transparent opacity={0.25} side={THREE.DoubleSide} />
        </mesh>
      </group>
    </group>
  );
}

function ExpansionScene() {
  const cloud = useRef();

  useFrame((state, delta) => {
    if (cloud.current) {
      cloud.current.rotation.y += delta * 0.08;
      cloud.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.08) * 0.18;
    }
  });

  return (
    <group ref={cloud}>
      <Sparkles count={360} scale={14} size={2.8} speed={0.42} color="#d4d4d4" />
      <Float floatIntensity={2.2} rotationIntensity={0.7}>
        <mesh position={[-1.8, 0.6, 0]}>
          <sphereGeometry args={[0.75, 40, 40]} />
          <meshPhysicalMaterial color="#d4d4d4" emissive="#ffffff" emissiveIntensity={0.18} transparent opacity={0.9} />
        </mesh>
      </Float>
      <Float floatIntensity={1.8} rotationIntensity={0.5}>
        <mesh position={[1.7, -0.4, -0.5]}>
          <sphereGeometry args={[0.95, 44, 44]} />
          <meshPhysicalMaterial color="#bdbdbd" emissive="#ffffff" emissiveIntensity={0.16} transparent opacity={0.85} />
        </mesh>
      </Float>
      <mesh>
        <planeGeometry args={[12, 8, 1, 1]} />
        <meshBasicMaterial color="#0b0b0b" transparent opacity={0.45} />
      </mesh>
    </group>
  );
}

function CmbSphere({ tone = 'cmb' }) {
  const texture = useMemo(makeCmbTexture, []);
  const sphere = useRef();
  const atmosphere = useRef();

  useEffect(() => () => texture.dispose(), [texture]);

  useFrame((state, delta) => {
    if (sphere.current) sphere.current.rotation.y += delta * 0.12;
    if (atmosphere.current) atmosphere.current.rotation.y -= delta * 0.05;
  });

  return (
    <group>
      <mesh ref={sphere}>
        <sphereGeometry args={[1.75, 96, 96]} />
        <meshPhysicalMaterial
          map={texture}
          color="#ffffff"
          emissive="#ffffff"
          emissiveIntensity={0.14}
          roughness={0.2}
          metalness={0.1}
          clearcoat={0.3}
        />
      </mesh>
      <mesh ref={atmosphere}>
        <sphereGeometry args={[1.9, 96, 96]} />
        <meshBasicMaterial color="#d4d4d4" transparent opacity={0.06} />
      </mesh>
      <Sparkles count={160} scale={5.5} size={2.4} speed={0.35} color="#e5e5e5" />
    </group>
  );
}

function TopologyScene() {
  const core = useRef();
  const ring = useRef();
  const points = useMemo(() => [
    [-2.5, -0.8, 0],
    [-1.2, 1.2, 0.5],
    [0.4, 0.2, -0.4],
    [1.6, 1.1, 0.4],
    [2.4, -0.6, 0],
    [0.8, -1.5, 0.3],
    [-1.7, -1.4, -0.5],
  ], []);

  useFrame((state, delta) => {
    if (core.current) core.current.rotation.y += delta * 0.18;
    if (ring.current) ring.current.rotation.z += delta * 0.12;
  });

  return (
    <group>
      <Float floatIntensity={1.8} rotationIntensity={0.45}>
        <mesh ref={core}>
          <torusKnotGeometry args={[1.2, 0.34, 180, 20]} />
          <meshPhysicalMaterial color="#e5e5e5" emissive="#ffffff" emissiveIntensity={0.12} roughness={0.15} metalness={0.2} />
        </mesh>
      </Float>
      <group ref={ring}>
        <mesh>
          <torusGeometry args={[2.1, 0.06, 16, 120]} />
          <meshBasicMaterial color="#bdbdbd" transparent opacity={0.28} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[2.45, 0.04, 16, 120]} />
          <meshBasicMaterial color="#e5e5e5" transparent opacity={0.22} />
        </mesh>
      </group>
      <Line points={points} color="#f5f5f5" lineWidth={1.5} transparent opacity={0.38} />
      <Sparkles count={180} scale={6.5} size={2.1} speed={0.4} color="#f5f5f5" />
    </group>
  );
}

function EngineScene() {
  const ring = useRef();

  useFrame((state, delta) => {
    if (ring.current) ring.current.rotation.z += delta * 0.1;
  });

  return (
    <group>
      <Sparkles count={260} scale={7} size={2.2} speed={0.35} color="#f5f5f5" />
      <mesh>
        <sphereGeometry args={[0.9, 64, 64]} />
        <meshPhysicalMaterial color="#e5e5e5" emissive="#ffffff" emissiveIntensity={0.16} roughness={0.16} metalness={0.08} />
      </mesh>
      <group ref={ring}>
        <mesh>
          <torusGeometry args={[1.9, 0.12, 24, 160]} />
          <meshBasicMaterial color="#d4d4d4" transparent opacity={0.2} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[2.35, 0.06, 20, 160]} />
          <meshBasicMaterial color="#bdbdbd" transparent opacity={0.16} />
        </mesh>
      </group>
      <Float floatIntensity={2.2} rotationIntensity={0.7}>
        <mesh position={[-1.8, 0.6, 0.5]}>
          <sphereGeometry args={[0.18, 24, 24]} />
          <meshBasicMaterial color="#e5e5e5" />
        </mesh>
      </Float>
      <Float floatIntensity={2.3} rotationIntensity={0.7}>
        <mesh position={[1.9, -0.5, -0.3]}>
          <sphereGeometry args={[0.18, 24, 24]} />
          <meshBasicMaterial color="#c4b5fd" />
        </mesh>
      </Float>
    </group>
  );
}

function DetectedScene() {
  const ring = useRef();
  useFrame((state, delta) => {
    if (ring.current) ring.current.rotation.y += delta * 0.08;
  });

  return (
    <group>
      <mesh>
        <sphereGeometry args={[1.65, 96, 96]} />
        <meshPhysicalMaterial color="#f8fafc" emissive="#60a5fa" emissiveIntensity={0.2} roughness={0.24} metalness={0.1} />
      </mesh>
      <group ref={ring}>
        <mesh>
          <torusGeometry args={[2.5, 0.05, 18, 120]} />
          <meshBasicMaterial color="#f97316" transparent opacity={0.6} />
        </mesh>
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[2.05, 0.06, 18, 120]} />
          <meshBasicMaterial color="#22d3ee" transparent opacity={0.55} />
        </mesh>
      </group>
      <Sparkles count={240} scale={7.2} size={2.1} speed={0.38} color="#e5e5e5" />
      <Float floatIntensity={2} rotationIntensity={0.6}>
        <mesh position={[1.3, 0.9, 0.8]}>
          <sphereGeometry args={[0.22, 28, 28]} />
          <meshBasicMaterial color="#f5f5f5" />
        </mesh>
      </Float>
      <Float floatIntensity={2} rotationIntensity={0.6}>
        <mesh position={[-1.4, -0.7, -0.2]}>
          <sphereGeometry args={[0.22, 28, 28]} />
          <meshBasicMaterial color="#cfcfcf" />
        </mesh>
      </Float>
    </group>
  );
}

function EndingScene() {
  const web = useMemo(() => [
    [-3.8, -1.8, 0],
    [-2.2, 1.3, 0.2],
    [-0.8, 0.1, -0.1],
    [1.0, 1.8, 0.3],
    [2.7, -0.2, -0.2],
    [4.1, 1.4, 0.1],
  ], []);

  const webTwo = useMemo(() => [
    [-3.1, 0.9, -0.2],
    [-1.4, -1.1, 0.2],
    [0.6, -0.4, 0],
    [2.4, 1.1, -0.3],
    [3.9, -1.4, 0.3],
  ], []);

  return (
    <group>
      <Stars radius={28} depth={45} count={4500} factor={3.4} saturation={0} fade speed={0.55} />
      <Sparkles count={280} scale={10} size={2.3} speed={0.34} color="#f5f5f5" />
      <Line points={web} color="#d4d4d4" lineWidth={1.5} transparent opacity={0.24} />
      <Line points={webTwo} color="#a3a3a3" lineWidth={1.5} transparent opacity={0.2} />
      <mesh>
        <sphereGeometry args={[0.3, 24, 24]} />
        <meshBasicMaterial color="#f5f5f5" transparent opacity={0.6} />
      </mesh>
    </group>
  );
}

export default function CosmicCanvas({ scene }) {
  const key = scene?.kind || 'ending';
  const sceneColor = scene?.color || '#ffffff';

  return (
    <Canvas dpr={[1, 1.75]} camera={{ position: [0, 0, 8], fov: 50 }} gl={{ antialias: true, alpha: true }}>
      <color attach="background" args={['#000000']} />
      <fog attach="fog" args={['#000000', 7, 24]} />
      <ambientLight intensity={0.8} />
      <directionalLight position={[4, 5, 6]} intensity={0.9} color="#ffffff" />
      <pointLight position={[-4, -2, 4]} intensity={0.35} color="#ffffff" />
      <CameraRig sceneKey={key} />
      <group>
        <Stars radius={25} depth={48} count={3000} factor={3.2} saturation={0} fade speed={0.6} />
        <Sparkles count={80} scale={14} size={2.3} speed={0.2} color="#f5f5f5" />
        {key === 'bang' && <BigBangScene />}
        {key === 'expansion' && <ExpansionScene />}
        {(key === 'cmb' || key === 'patterns' || key === 'detected') && <CmbSphere tone={key} />}
        {key === 'stats' && <ExpansionScene />}
        {key === 'topology' && <TopologyScene />}
        {key === 'engine' && <EngineScene />}
        {key === 'ending' && <EndingScene />}
      </group>
    </Canvas>
  );
}
