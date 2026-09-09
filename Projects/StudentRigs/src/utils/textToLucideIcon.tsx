import * as LucideIcons from "lucide-react";

type IconName = keyof typeof LucideIcons;

export default function TextToIcon({
	name,
	className,
	...props
}: {
	name: IconName;
	className?: string;
	[key: string]: any;
}) {
	const Icon = LucideIcons[name] as LucideIcons.LucideIcon;
	if (!Icon) return null;
	return (
		<Icon
			className={className}
			{...props}
		/>
	);
}
