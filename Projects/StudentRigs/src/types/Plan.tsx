import * as LucideIcons from "lucide-react";

type IconName = keyof typeof LucideIcons;

export interface PlanFeature {
	icon: IconName;
	color: string;
	text: string;
}

export interface Plan {
	name: string;
	title: string;
	supportHours: number;
	desc: string;
	price?: number;
	features: PlanFeature[];
	color: string;
	border: string;
	plan: string;
}
