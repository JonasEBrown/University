import { useEffect, useState } from "react";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltfCache: Record<string, any> = {};

export default function UseCachedGLTF(src: string) {
	const [model, setModel] = useState<any>(gltfCache[src] || null);

	useEffect(() => {
		if (gltfCache[src]) return;

		const loader = new GLTFLoader();
		loader.load(src, (gltf) => {
			gltfCache[src] = gltf;
			setModel(gltf);
		});
	}, [src]);

	return model;
}
