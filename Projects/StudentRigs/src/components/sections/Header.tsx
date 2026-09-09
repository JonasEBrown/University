import Link from "next/link";
import { PcCase } from "lucide-react";

import Button from "@/src/components/ui/Button";

export default function Header() {
	return (
		<header className="sticky top-0 z-50 h-16 bg-(--background)">
			<div className="w-screen h-full flex items-center justify-between px-5">
				<Link
					href="/"
					className="h-full flex items-center"
				>
					<PcCase className="h-full w-9 aspect-square drop-shadow-[0_1.2px_1.2px_rgba(0,0,0,1)]" />
					<p className="font-bold text-xl px-2 drop-shadow-[0_1.2px_1.2px_rgba(0,0,0,1)]">
						StudentRigs
					</p>
				</Link>
				<Button
					href=""
					className="inline-flex items-center mr-3"
				>
					<PcCase className="w-5 h-5 mr-2" />
					Build your PC
				</Button>
			</div>
		</header>
	);
}
