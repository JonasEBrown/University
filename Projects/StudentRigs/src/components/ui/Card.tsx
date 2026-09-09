export default function Card({
	className,
	children,
	...props
}: {
	className?: string;
	children?: any;
	[key: string]: any;
}) {
	return (
		<div
			className={`flex rounded-2xl border bg-(--border) border-(--border) p-5 shadow-sm ${className}`}
			{...props}
		>
			{children}
		</div>
	);
}
