"use client";

import { useRouter, useSearchParams } from "next/navigation";

import Animate from "@/src/components/Animate";
import PlanCard from "@/src/components/ui/PlanCard";

import type { Costs } from "@/src/types/Costs";
import type { Plan } from "@/src/types/Plan";

export default function Plans({
	plans,
	costs,
	current,
	className,
	...props
}: {
	plans: Plan[];
	costs: Costs;
	current?: string | null;
	className?: string;
	[key: string]: any;
}) {
	const router = useRouter();
	const params = useSearchParams();

	plans.forEach((plan) => {
		if (plan.price === 0) return;

		let assemblyHours: number =
			(costs.assembly.hours.min + costs.assembly.hours.max) / 2;

		let cost: number =
			assemblyHours * costs.assembly.costPerHour +
			plan.supportHours * costs.support.costPerHour;

		plan.price = Math.round(++cost / 10) * 10 - 1;
	});

	return (
		<section
			id="plans"
			className={className}
		>
			<div className="px-4 py-16">
				<h2 className="text-3xl font-bold mb-8 text-(--primary-text)">
					Our plans
				</h2>
				<div className="grid md:grid-cols-3 gap-6">
					{plans.map((plan, index) => {
						return (
							<Animate
								key={index}
								delay={index * 0.2}
								duration={1}
							>
								<PlanCard
									key={plan.name}
									plan={plan}
									onChoose={(plan) => {
										const newParams = new URLSearchParams(
											params.toString()
										);
										newParams.set("plan", plan.plan);
										router.push(
											`/plans/?${newParams.toString()}`
										);
									}}
									current={current === plan.plan}
								/>
							</Animate>
						);
					})}
				</div>
			</div>
		</section>
	);
}
