"use client";

import Card from "@/src/components/ui/Card";
import Button from "@/src/components/ui/Button";

import type { Plan } from "@/src/types/Plan";

import TextToIcon from "@/src/utils/TextToLucideIcon";
import ParseText from "@/src/utils/ParseText";

export default function FeatureCard({
	plan,
	className,
	onChoose,
	current,
	children,
	...props
}: {
	plan: Plan;
	className?: string;
	onChoose?: (plan: Plan) => void;
	current?: boolean;
	children?: any;
	[key: string]: any;
}) {
	return (
		<Card
			className={`flex-grow h-full items-start flex flex-col ${className} ${
				current ? "bg-(--secondary-text)/15" : ""
			} ${plan.border}`}
			{...props}
		>
			<div className="flex flex-col flex-grow justify-between px-1">
				<div className="mb-6">
					<h1 className={`text-4xl font-semibold ${plan.color}`}>
						{plan.name}
					</h1>
					<h2 className="text-xl font-semibold text-(--secondary-text)/70">
						{plan.title}
					</h2>
					<h1 className="text-lg font-semibold mb-5">
						{plan.price === 0
							? "Free"
							: `£${plan.price} + build cost`}
					</h1>
					<p className="text-sm text-(--secondary-text) mt-4 mb-2 h-18">
						{ParseText(plan.desc)}
					</p>
					<ul className="space-y-2 text-sm mb-4">
						{plan.features.map((feature) => {
							return (
								<li
									key={feature.text}
									className="flex justify-start items-center gap-2 text-(--secondary-text)"
								>
									<TextToIcon
										name={feature.icon}
										style={{
											color: `${feature.color}`,
										}}
									/>
									{ParseText(feature.text)}
								</li>
							);
						})}
					</ul>
				</div>
				{current ? (
					<div className="self-center my-5 button-animation text-(--background) bg-(--primary-text)">
						Selected
					</div>
				) : (
					<Button
						onClick={() => {
							if (onChoose) return onChoose(plan);
						}}
						className="self-center my-5"
					>
						Select plan
					</Button>
				)}
				{children && <div className="flex flex-col"> {children}</div>}
			</div>
		</Card>
	);
}
