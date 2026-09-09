import { Vector3 } from "three";
import { useRef, useState, useEffect } from "react";
import { OrbitControls } from "@react-three/drei";

export default function AutoOrbitControls({
	target,
	distance,
	speed,
	delay = 0,
	startAngle = -Math.PI / 4,
	autoRotate = false,
	...props
}: {
	target: Vector3;
	distance: number;
	speed: number;
	delay?: number;
	startAngle?: number;
	autoRotate?: boolean;
	[key: string]: any;
}) {
	const orbitControlsRef = useRef<any>(null);
	const [currentSpeed, setCurrentSpeed] = useState(0);
	const [doAutoRotate, setDoAutoRotate] = useState(autoRotate && !delay);

	useEffect(() => {
		if (orbitControlsRef.current) {
			orbitControlsRef.current.target.copy(target);
			orbitControlsRef.current.object.position.set(
				target.x + distance * Math.sin(startAngle),
				target.y,
				target.z + distance * Math.cos(startAngle)
			);
			orbitControlsRef.current.update();
		}

		setTimeout(() => {
			setDoAutoRotate(autoRotate);
			setCurrentSpeed(speed);
		}, delay * 1000);
	}, [target]);

	return (
		<OrbitControls
			autoRotate={doAutoRotate}
			autoRotateSpeed={currentSpeed}
			minDistance={distance}
			maxDistance={distance}
			ref={orbitControlsRef}
			maxPolarAngle={Math.PI / 2}
			{...props}
		/>
	);
}
