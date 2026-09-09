import Animate from "@/src/components/Animate";
import FeatureCard from "@/src/components/ui/FeatureCard";

import type { Feature } from "@/src/types/Feature";

import TextToIcon from "@/src/utils/TextToLucideIcon";

export default function Features({ features }: { features: Feature[] }) {
	return (
		<section
			id="features"
			className="mt-20"
		>
			<div className="grid grid-flow-row grid-cols-3 gap-6">
				{features.map((feature, index) => {
					return (
						<Animate
							key={index}
							delay={index * 0.2}
							duration={1}
						>
							<FeatureCard
								key={feature.title}
								icon={({ ...props }) => (
									<TextToIcon
										name={feature.icon}
										{...props}
									/>
								)}
								color={feature.color}
								className="gap-4"
								title={feature.title}
								text={feature.text}
							/>
						</Animate>
					);
				})}
			</div>
		</section>
	);
}
