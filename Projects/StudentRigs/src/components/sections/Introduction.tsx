import { useState } from "react";
import * as LucideIcons from "lucide-react";

import Tag from "@/src/components/ui/Tag";
import Button from "@/src/components/ui/Button";
import SpinningPC from "@/src/components/threejs/SpinningPC";

import type { Tag as TagType } from "@/src/types/Tag";

import TextToIcon from "@/src/utils/TextToLucideIcon";

export default function Main({ tags }: { tags: TagType[] }) {
	const [loaded, setLoaded] = useState<boolean>(false);

	return (
		<section
			id=""
			className="pt-20 grid lg:grid-cols-2 gap-x-10 gap-y-5"
		>
			<div>
				<h1 className="text-5xl font-extrabold accent-gradient-text">
					Power Up Your Studies & Level Up In-Game
				</h1>
				<div className="pt-2.5 flex gap-2">
					{tags.map((tag) => (
						<Tag
							key={tag.text}
							icon={({ ...props }) => (
								<TextToIcon
									name={tag.icon}
									style={{
										color: `${tag.color}`,
									}}
									{...props}
								/>
							)}
							text={tag.text}
						/>
					))}
				</div>
				<p className="text-(--secondary-text) text-lg">
					Designed for students, built for performance. Whether you're
					acing assignments or exploring new worlds, we support your
					academic journey and gaming adventures.
				</p>
				<div className="flex mt-5 gap-3 h-10">
					<Button
						href="/build"
						className="inline-flex items-center"
					>
						<LucideIcons.PcCase className="w-5 h-5 mr-2" />
						Build your PC
					</Button>
					<Button
						href="#plans"
						className="inline-flex items-center"
					>
						See Plans
					</Button>
				</div>
			</div>
			<div className="flex items-center aspect-video rounded-3xl border border-(--border) bg-(--border) overflow-hidden justify-center">
				<SpinningPC show={loaded} />
			</div>
		</section>
	);
}
