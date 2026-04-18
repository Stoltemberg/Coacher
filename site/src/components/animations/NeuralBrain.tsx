"use client";

import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Sphere, Points, PointMaterial } from "@react-three/drei";
import * as THREE from "three";

const COUNT = 600;
const NEURAL_POSITIONS = new Float32Array(COUNT * 3);
for (let i = 0; i < COUNT; i++) {
  NEURAL_POSITIONS[i * 3] = (Math.random() - 0.5) * 15;
  NEURAL_POSITIONS[i * 3 + 1] = (Math.random() - 0.5) * 15;
  NEURAL_POSITIONS[i * 3 + 2] = (Math.random() - 0.5) * 15;
}

function NeuralField() {
  const pointsRef = useRef<THREE.Points>(null);

  useFrame((state) => {
    if (!pointsRef.current) return;
    pointsRef.current.rotation.y = state.clock.getElapsedTime() * 0.02;
    pointsRef.current.rotation.x = state.clock.getElapsedTime() * 0.01;
  });

  return (
    <group>
      <Points ref={pointsRef} positions={NEURAL_POSITIONS} stride={3}>
        <PointMaterial
          transparent
          color="#ffffff"
          size={0.015}
          sizeAttenuation={true}
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          opacity={0.2}
        />
      </Points>
      {/* Subtle background glow */}
      <Sphere args={[8, 16, 16]}>
        <meshBasicMaterial color="#8b5cf6" transparent opacity={0.02} side={THREE.BackSide} />
      </Sphere>
    </group>
  );
}

export default function NeuralBrain() {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden opacity-40">
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }} dpr={[1, 2]}>
        <NeuralField />
      </Canvas>
    </div>
  );
}
