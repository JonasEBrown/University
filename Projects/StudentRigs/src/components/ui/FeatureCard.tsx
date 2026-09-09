import Card from "@/src/components/ui/Card";

export default function FeatureCard({
	title,
	text,
	icon: Icon,
	color,
	className,
	childrenClassName,
	children,
	...props
}: {
	title?: string;
	text?: string;
	icon?: any;
	color?: string;
	className?: string;
	childrenClassName?: string;
	children?: any;
	[key: string]: any;
}) {
	return (
		<Card
			className={`flex-grow h-full items-start ${className}`}
			{...props}
		>
			{Icon && (
				<div
					className="self-center rounded-[40%] p-3 border-2 bg-(--background) aspect-square size-18 items-center flex justify-center"
					style={{
						borderColor: `${color}`,
					}}
				>
					<Icon
						className="size-[90%]"
						style={{
							color: `${color}`,
						}}
					/>
				</div>
			)}
			<div className="flex flex-col flex-grow justify-between">
				{title && (
					<h1 className="text-lg font-semibold text-(--primary-text)">
						{title}
					</h1>
				)}
				{text && (
					<p className="text-sm text-(--secondary-text)">{text}</p>
				)}
				<div className={`flex-grow ${childrenClassName}`}>
					{children}
				</div>
			</div>
		</Card>
	);
}
