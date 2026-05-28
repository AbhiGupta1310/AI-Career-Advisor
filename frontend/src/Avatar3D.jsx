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

  // Re-color model to match professional black & white theme
  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh && child.material) {
        const mat = child.material;
        const name = (mat.name || "").toLowerCase();
        const hex = "#" + (mat.color ? mat.color.getHexString() : "000000");

        // Map yellow/gold body parts -> dark metallic grey
        if (
          hex === "c8b43a" ||
          hex === "c8b43b" ||
          name.includes("body") ||
          name.includes("gold")
        ) {
          mat.color = new THREE.Color("#2a2a2a");
          mat.metalness = 0.8;
          mat.roughness = 0.2;
        }
        // Map grey/silver parts -> metallic silver
        else if (
          hex === "999999" ||
          hex === "aaaaaa" ||
          hex === "cccccc" ||
          name.includes("grey") ||
          name.includes("silver") ||
          name.includes("metal")
        ) {
          mat.color = new THREE.Color("#888888");
          mat.metalness = 0.9;
          mat.roughness = 0.1;
        }
        // Dark/black parts -> pure black with slight metallic
        else if (
          hex === "333333" ||
          hex === "222222" ||
          hex === "111111" ||
          hex === "000000"
        ) {
          mat.color = new THREE.Color("#0a0a0a");
          mat.metalness = 0.6;
          mat.roughness = 0.3;
        }
        // Anything else -> convert to grey scale
        else {
          const currentColor = mat.color.clone();
          const gray = (currentColor.r + currentColor.g + currentColor.b) / 3;
          mat.color = new THREE.Color(gray, gray, gray);
          mat.metalness = Math.min(mat.metalness + 0.3, 1);
          mat.roughness = Math.max(mat.roughness - 0.2, 0);
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
      <meshBasicMaterial color="#ffffff" wireframe />
    </mesh>
  );
}

export default function Avatar3D() {
  return (
    <Canvas
      camera={{ position: [0, 0.5, 5], fov: 45 }}
      style={{ height: "600px", width: "100%", pointerEvents: "none" }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 8, 5]} intensity={1.2} color="white" />
      <spotLight
        position={[-3, 5, 5]}
        angle={0.4}
        penumbra={1}
        intensity={0.8}
        color="white"
      />
      {/* White rim light */}
      <pointLight position={[0, 2, -3]} intensity={1.5} color="white" />
      {/* Soft fill light */}
      <pointLight position={[-3, -1, 3]} intensity={0.5} color="white" />
      {/* Highlight */}
      <pointLight position={[3, 0, 2]} intensity={0.4} color="white" />

      <Suspense fallback={<LoadingFallback />}>
        <Robot />
      </Suspense>

      <Environment preset="studio" />
    </Canvas>
  );
}
