"use client";

import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";

const COUNT = 1200;
const NEURAL_POSITIONS = new Float32Array(COUNT * 3);
for (let i = 0; i < COUNT; i++) {
  NEURAL_POSITIONS[i * 3] = (Math.random() - 0.5) * 20;
  NEURAL_POSITIONS[i * 3 + 1] = (Math.random() - 0.5) * 20;
  NEURAL_POSITIONS[i * 3 + 2] = (Math.random() - 0.5) * 20;
}

function NeuralField() {
  const pointsRef = useRef<THREE.Points>(null);

  useFrame((state) => {
    if (!pointsRef.current) return;
    const time = state.clock?.getElapsedTime() || (typeof performance !== 'undefined' ? performance.now() / 1000 : 0);
    pointsRef.current.rotation.y = time * 0.05;
    pointsRef.current.rotation.x = time * 0.03;
  });

  return (
    <group>
      <Points ref={pointsRef} positions={NEURAL_POSITIONS} stride={3}>
        <PointMaterial
          transparent
          color="#adff2f"
          size={0.08}
          sizeAttenuation={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.6}
        />
      </Points>
      {/* Subtle background glow */}
      <Sphere args={[10, 16, 16]}>
        <meshBasicMaterial color="#adff2f" transparent opacity={0.05} side={THREE.BackSide} />
      </Sphere>
    </group>
  );
}

export default function NeuralBrain() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }} dpr={[1, 2]}>
        <NeuralField />
      </Canvas>
    </div>
  );
}
