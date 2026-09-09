"use client";

import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

import Plans from "@/src/components/sections/Plans";
import PlanCreation from "@/src/components/sections/PlanCreation";

import PlanDataRaw from "@/src/data/plans.json";
import CostsRaw from "@/src/data/costs.json";

import type { Plan } from "@/src/types/Plan";
import type { Costs } from "@/src/types/Costs";

export default function PlanPage({
	searchParams,
}: {
	searchParams: { plan?: string };
}) {
	return (
		<>
			<Plans
				plans={PlanDataRaw as Plan[]}
				costs={CostsRaw as Costs}
				current={searchParams.plan}
			/>
			{searchParams.plan && (
				<>
					<PlanCreation />
					<div className="size-25" />
				</>
			)}
		</>
	);
}
