export default function LoadingSpinner({
	size,
	color,
	thickness = 3,
	...props
}: {
	size: number;
	color?: string;
	thickness?: number;
	[key: string]: any;
}) {
	return (
		<div
			className="rounded-full animate-loading-spinner"
			style={{
				width: `${size}px`,
				height: `${size}px`,
				padding: `${thickness}px`,
				borderColor: color,
				borderWidth: `${thickness}px`,
				borderTopColor: "transparent",
			}}
			{...props}
		/>
	);
}
