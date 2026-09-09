"use client";

import { useRouter } from "next/navigation";

import Introduction from "@/src/components/sections/Introduction";
import Features from "@/src/components/sections/Features";
import Plans from "@/src/components/sections/Plans";

import {
	Tags as TagData,
	Features as FeatureData,
} from "@/src/data/pages/home.json";

import PlanDataRaw from "@/src/data/plans.json";
import CostsRaw from "@/src/data/costs.json";

import type { Plan } from "@/src/types/Plan";
import type { Costs } from "@/src/types/Costs";

export default function HomePage() {
	const router = useRouter();

	return (
		<>
			<Introduction tags={TagData} />
			<Features features={FeatureData} />
			<Plans
				plans={PlanDataRaw as Plan[]}
				costs={CostsRaw as Costs}
				className="bg-(--background) border-t border-(--border) mt-20"
			/>
		</>
	);
}
