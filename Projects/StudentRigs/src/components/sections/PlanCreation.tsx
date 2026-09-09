import { useEffect, useState } from "react";

import Basics from "@/src/components/ui/plan-creator/Basics";

const stages: React.ReactElement[] = [<Basics />];

export default function PlanCreation({ className }: { className?: string }) {
	const [stage, setStage] = useState<number>(1);

	useEffect(() => {
		setTimeout(() => setStage(2), 3000);
	}, [stage]);

	return (
		<section
			id="plan-creation"
			className={`px-4 py-16 border-t border-(--border) pt-5 ${className}`}
		>
			<h2 className="text-3xl font-bold my-8 text-(--primary-text) bg-(--background)">
				Create your plan
			</h2>
			<div className="flex-grow gap-6 justify-center">
				{stages.slice(0, stage)}
			</div>
		</section>
	);
}
