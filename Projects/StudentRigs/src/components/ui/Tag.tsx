export default function Tag({
	text,
	icon: Icon,
	className,
	...props
}: {
	text: string;
	icon: any;
	className?: string;
	[key: string]: any;
}) {
	return (
		<div className="inline-flex items-center gap-2 text-xs border border-(--secondary-text)/35 rounded-full px-3 py-1 mb-4 text-(--secondary-text) size-fit">
			<Icon
				className={`w-4 h-4 ${className}`}
				{...props}
			/>
			{text}
		</div>
	);
}
