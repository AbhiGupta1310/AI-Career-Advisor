import { useRef, useEffect, Suspense } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useGLTF, Environment, useAnimations } from "@react-three/drei";
import * as THREE from "three";

const lerp = (a, b, t) => a + (b - a) * t;

function Robot() {
  const group = useRef();
  const { scene, animations } = useGLTF("/robot.glb");
  const { actions } = useAnimations(animations, group);

  const mouse = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const onMouseMove = (e) => {
      mouse.current.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.current.y = -(e.clientY / window.innerHeight) * 2 + 1;
    };
    window.addEventListener("mousemove", onMouseMove);
    return () => window.removeEventListener("mousemove", onMouseMove);
  }, []);

  // Re-color model to match website neon vibe
  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh && child.material) {
        const mat = child.material;
        const name = (mat.name || "").toLowerCase();
        const hex = "#" + (mat.color ? mat.color.getHexString() : "000000");

        // Map yellow/gold body parts -> dark metallic purple
        if (
          hex === "c8b43a" ||
          hex === "c8b43b" ||
          name.includes("body") ||
          name.includes("gold")
        ) {
          mat.color = new THREE.Color("#2d1b69");
          mat.metalness = 0.6;
          mat.roughness = 0.3;
        }
        // Map grey/silver parts -> neon cyan metallic
        else if (
          hex === "999999" ||
          hex === "aaaaaa" ||
          hex === "cccccc" ||
          name.includes("grey") ||
          name.includes("silver") ||
          name.includes("metal")
        ) {
          mat.color = new THREE.Color("#0e7490");
          mat.metalness = 0.7;
          mat.roughness = 0.2;
        }
        // Dark/black parts -> deep purple-black
        else if (
          hex === "333333" ||
          hex === "222222" ||
          hex === "111111" ||
          hex === "000000"
        ) {
          mat.color = new THREE.Color("#1a0a2e");
          mat.metalness = 0.5;
          mat.roughness = 0.4;
        }
        // Anything else -> tint it slightly purple
        else {
          const currentColor = mat.color.clone();
          currentColor.lerp(new THREE.Color("#6d28d9"), 0.4);
          mat.color = currentColor;
          mat.metalness = Math.min(mat.metalness + 0.2, 1);
          mat.roughness = Math.max(mat.roughness - 0.1, 0);
        }

        mat.needsUpdate = true;
      }
    });
  }, [scene]);

  // Play idle animation
  useEffect(() => {
    if (actions) {
      const idleAction =
        actions["Idle"] || actions["idle"] || Object.values(actions)[0];
      if (idleAction) {
        idleAction.reset().fadeIn(0.5).play();
      }
    }
  }, [actions]);

  // Mouse tracking rotation
  useFrame(() => {
    if (group.current) {
      group.current.rotation.y = lerp(
        group.current.rotation.y,
        mouse.current.x * 0.5,
        0.1,
      );
      group.current.rotation.x = lerp(
        group.current.rotation.x,
        mouse.current.y * 0.1,
        0.1,
      );
    }
  });

  return (
    <group ref={group} position={[0, -1.8, 0]} scale={0.75}>
      <primitive object={scene} />
    </group>
  );
}

useGLTF.preload("/robot.glb");

function LoadingFallback() {
  const meshRef = useRef();
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 2;
    }
  });
  return (
    <mesh ref={meshRef}>
      <torusGeometry args={[0.5, 0.1, 16, 32]} />
      <meshBasicMaterial color="#a855f7" wireframe />
    </mesh>
  );
}

export default function Avatar3D() {
  return (
    <Canvas
      camera={{ position: [0, 0.5, 5], fov: 45 }}
      style={{ height: "600px", width: "100%", pointerEvents: "none" }}
    >
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1.5} color="white" />
      <spotLight
        position={[-3, 5, 5]}
        angle={0.4}
        penumbra={1}
        intensity={1}
        color="#d8b4fe"
      />
      {/* Purple rim light */}
      <pointLight position={[0, 2, -3]} intensity={2} color="#a855f7" />
      {/* Cyan accent */}
      <pointLight position={[-3, -1, 3]} intensity={0.8} color="#06b6d4" />
      {/* Pink highlight */}
      <pointLight position={[3, 0, 2]} intensity={0.6} color="#ec4899" />

      <Suspense fallback={<LoadingFallback />}>
        <Robot />
      </Suspense>

      <Environment preset="night" />
    </Canvas>
  );
}
