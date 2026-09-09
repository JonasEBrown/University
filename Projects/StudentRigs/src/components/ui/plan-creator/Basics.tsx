import { useReducer } from "react";
import { motion } from "motion/react";

import InputField from "@/src/components/ui/forms/InputField";
import Card from "@/src/components/ui/Card";

type BasicsForm = {
	budget: string;
};

type Action = { type: "setBudget"; payload: string };

function formReducer(state: BasicsForm, action: Action): BasicsForm {
	switch (action.type) {
		case "setBudget":
			return { ...state, budget: action.payload };
		default:
			return state;
	}
}

export default function Basics() {
	const [form, dispatch] = useReducer(formReducer, {
		budget: "£",
	});

	return (
		<motion.div
			className="flex flex-col gap-6"
			animate={{
				opacity: 1,
				y: 0,
			}}
			initial={{
				opacity: 0,
				y: 30,
			}}
			transition={{
				duration: 1,
			}}
		>
			<Card className="p-5 items-center">
				<div className="w-full">
					<h2 className="text-2xl font-semibold text-(--primary-text) mb-5">
						What's your budget?
					</h2>
					<InputField
						name="budget"
						value={form.budget}
						onChange={(value) => {
							const amount = value.replace(/^£/, "");
							if (/^\d*(\.\d{0,2})?$/.test(amount))
								dispatch({
									type: "setBudget",
									payload: `£${amount}`,
								});
						}}
					/>
				</div>
			</Card>
			<Card></Card>
		</motion.div>
	);
}
