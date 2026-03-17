"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Stars, PerspectiveCamera, Float, Text, MeshDistortMaterial } from "@react-three/drei";
import { Suspense } from "react";

function EngineCore() {
  return (
    <Float speed={2} rotationIntensity={1} floatIntensity={2}>
      <mesh>
        <sphereGeometry args={[1, 32, 32]} />
        <MeshDistortMaterial
          color="#3b82f6"
          speed={3}
          distort={0.4}
          radius={1}
        />
      </mesh>
      <Text
        position={[0, 1.5, 0]}
        fontSize={0.2}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        O-SOCIAL ENGINE
      </Text>
    </Float>
  );
}

function Grid() {
  return (
    <gridHelper args={[20, 20, "#1e293b", "#0f172a"]} rotation={[0, 0, 0]} />
  );
}

export default function MetaverseCanvas() {
  return (
    <div className="w-full h-[500px] bg-slate-950 rounded-3xl overflow-hidden border border-slate-800 shadow-2xl relative">
      <div className="absolute top-6 left-6 z-10">
        <h2 className="text-white font-bold text-lg tracking-tight">Metaverse Office v0.1</h2>
        <p className="text-slate-500 text-xs">Arraste para rotacionar • Scroll para zoom</p>
      </div>
      
      <Canvas shadows>
        <Suspense fallback={null}>
          <PerspectiveCamera makeDefault position={[5, 5, 5]} />
          <OrbitControls enableDamping dampingFactor={0.05} />
          
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} color="#3b82f6" />
          <spotLight position={[-10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
          
          <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
          <Grid />
          
          <EngineCore />
          
          {/* Room markers */}
          <Text position={[-5, 0, -5]} rotation={[0, Math.PI / 4, 0]} fontSize={0.5} color="#1d4ed8">X ROOM</Text>
          <Text position={[5, 0, -5]} rotation={[0, -Math.PI / 4, 0]} fontSize={0.5} color="#ea580c">REDDIT ROOM</Text>
          <Text position={[0, 0, 5]} rotation={[0, Math.PI, 0]} fontSize={0.5} color="#059669">ANALYTICS</Text>
          
        </Suspense>
      </Canvas>
    </div>
  );
}
