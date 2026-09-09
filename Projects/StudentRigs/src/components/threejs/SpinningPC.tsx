"use client";

import { useState, useEffect, Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { Environment, Lightformer, Preload, useGLTF } from "@react-three/drei";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import * as THREE from "three";

import LoadingSpinner from "@/src/components/ui/LoadingSpinner";
import AutoOrbitControls from "@/src/components/threejs/AutoOrbitControls";

import UseCachedGLTF from "@/src/utils/UseCachedGLTF";

const SRC: string = "/models/pc/scene.gltf";

function LoadingWindow() {
	return (
		<div className="size-full inset-0 z-10 flex items-center justify-center bg-(--border)">
			<LoadingSpinner
				size={40}
				thickness={3}
				color="var(--purple-accent)"
			/>
		</div>
	);
}

function PCModel({
	setCenter,
	onReady,
	...props
}: {
	setCenter: (v: THREE.Vector3) => void;
	onReady?: () => void;
	[key: string]: any;
}) {
	const gltf = UseCachedGLTF(SRC);
	const scene: THREE.Object3D | null = gltf?.scene ?? null;

	useEffect(() => {
		if (!scene) return;

		const box = new THREE.Box3().setFromObject(scene);
		const c = new THREE.Vector3();
		box.getCenter(c);
		setCenter(c);

		scene.traverse((child) => {
			if (child instanceof THREE.Mesh) {
				if (child.isMesh) {
					const bbox = new THREE.Box3().setFromObject(child);
					const size = bbox.getSize(new THREE.Vector3());
					if (size.y < 0.1 && size.x > 1 && size.z > 1)
						child.removeFromParent();
				}

				const mat = child.material as THREE.MeshStandardMaterial;
				if (mat.opacity < 0.6 || mat.color.getHex() === 0x000000) {
					mat.transparent = true;
					mat.opacity = 0.35;
					mat.roughness = 0;
					mat.metalness = 0;
					mat.envMapIntensity = 2;
					mat.color = new THREE.Color(0x1c1c1c);
				} else if (
					mat.name === "Material.005" ||
					mat.name === "Material.040" ||
					mat.name === "Material.043" ||
					mat.name === "Material.054" ||
					mat.name === "ROGTRANSPARENT"
				) {
					mat.emissive = new THREE.Color(0xffccff);
					mat.emissiveIntensity = 3;
				} else {
					mat.metalness = 0.25;
					mat.roughness = 0.2;
				}
			}
		});

		onReady?.();
	}, [scene]);

	return scene ? (
		<primitive
			object={scene}
			scale={0.5}
			{...props}
		/>
	) : (
		<></>
	);
}

export default function SpinningPC() {
	const [center, setCenter] = useState<THREE.Vector3>(
		new THREE.Vector3(0, 0, 0)
	);
	const [modelReady, setModelReady] = useState<boolean>(false);

	return (
		<div className="size-full">
			{!modelReady && <LoadingWindow />}
			<Canvas
				camera={{ position: [0, 0, 0], fov: 60 }}
				gl={{
					toneMapping: THREE.ACESFilmicToneMapping,
					outputColorSpace: THREE.SRGBColorSpace,
				}}
			>
				<color
					attach="background"
					args={["#1f1f1f"]}
				/>
				<AutoOrbitControls
					target={center}
					distance={3.5}
					speed={5}
					autoRotate
				/>
				<Suspense fallback={<LoadingWindow />}>
					<PCModel
						setCenter={setCenter}
						position={[0, 0.075, 0]}
						onReady={() => setModelReady(true)}
					/>
				</Suspense>
				<Environment resolution={512}>
					<Lightformer
						form="rect"
						intensity={10}
						rotation-x={Math.PI / 4}
						position={[4, 4, 4]}
						scale={[20, 2, 20]}
						color="#ffffff"
						onUpdate={(self) => self.lookAt(0, 1, 0)}
					/>
					<Lightformer
						form="rect"
						intensity={10}
						rotation-x={-Math.PI / 4}
						position={[-4, 4, -4]}
						scale={[20, 2, 20]}
						color="#ffffff"
						onUpdate={(self) => self.lookAt(0, 1, 0)}
					/>
				</Environment>
				<EffectComposer>
					<Bloom
						luminanceThreshold={0.5}
						luminanceSmoothing={0.9}
						intensity={0.5}
					/>
				</EffectComposer>
				<Preload all />
			</Canvas>
		</div>
	);
}
