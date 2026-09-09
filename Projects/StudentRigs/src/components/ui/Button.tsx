"use client";

import Link from "next/link";

export default function Button({
	href,
	onClick,
	className,
	children,
	type,
	...props
}: {
	href?: string;
	onClick?: (...props: any[]) => void;
	className?: string;
	children?: any;
	type?: "button" | "submit" | "reset";
	[key: string]: any;
}) {
	return href ? (
		<Link
			href={href}
			{...props}
		>
			<span
				onClick={onClick}
				className={`button-animation ${className}`}
			>
				{children}
			</span>
		</Link>
	) : (
		<button
			onClick={onClick}
			className={`button-animation cursor-pointer ${className}`}
			type={type}
			{...props}
		>
			{children}
		</button>
	);
}
