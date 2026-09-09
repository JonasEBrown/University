import { motion } from "motion/react";
import { useState, useEffect } from "react";

const variants = {
	inactive: {
		opacity: 0,
		y: 30,
	},
	active: {
		opacity: 1,
		y: 0,
	},
};

export default function Animate({
	duration,
	delay,
	children,
	...props
}: {
	duration?: number;
	delay?: number;
	children?: any;
	[key: string]: any;
}) {
	const [status, setStatus] = useState<string>("inactive");

	useEffect(() => {
		setTimeout(() => setStatus("active"), (delay ?? 0) * 1000);
	}, [status]);

	return (
		<motion.div
			initial="inactive"
			animate={status}
			variants={variants}
			transition={
				duration
					? {
							duration: duration,
					  }
					: undefined
			}
			{...props}
		>
			{children}
		</motion.div>
	);
}
