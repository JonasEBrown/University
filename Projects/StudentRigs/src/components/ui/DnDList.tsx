"use client";

import {
	DndContext,
	closestCenter,
	useSensor,
	useSensors,
	PointerSensor,
} from "@dnd-kit/core";
import {
	arrayMove,
	SortableContext,
	useSortable,
	verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import Card from "@/src/components/ui/Card";

import type {
	DnDListItem,
	DnDListItem as DnDListItemType,
} from "@/src/types/DnDListItem";

function DnDListItem({ id, text }: DnDListItemType) {
	const {
		attributes,
		listeners,
		setNodeRef,
		transform,
		transition,
		isDragging,
	} = useSortable({ id: id });

	return (
		<div
			ref={setNodeRef}
			style={{
				transform: CSS.Transform.toString(transform),
				transition,
				opacity: isDragging ? 0.5 : 1,
			}}
			{...attributes}
			{...listeners}
			className="p-3 mb-2 input-field"
		>
			{text}
		</div>
	);
}

export default function DnDList({
	title,
	items,
	setItems,
	className,
}: {
	title?: string;
	items: string[];
	setItems: (items: string[]) => void;
	className?: string;
	[key: string]: any;
}) {
	const sensors = useSensors(useSensor(PointerSensor));

	const handleDragEnd = (e: any) => {
		const { active, over } = e;
		if (!over) return;
		if (active.id !== over.id) {
			const oldIndex = items.findIndex((item) => item === active.id);
			const newIndex = items.findIndex((item) => item === over.id);
			setItems(arrayMove(items, oldIndex, newIndex));
		}
	};

	return (
		<div>
			<h2 className="text-xl font-semibold mb-2">{title}</h2>
			<DndContext
				sensors={sensors}
				collisionDetection={closestCenter}
				onDragEnd={handleDragEnd}
			>
				<SortableContext
					items={items}
					strategy={verticalListSortingStrategy}
				>
					{items.map((item, index) => (
						<div className="flex gap-3">
							<div className="p-3 mb-2 rounded-lg outline outline-(--secondary-text)/22 text-center w-10">
								{index + 1}
							</div>
							<DnDListItem
								key={item}
								id={item}
								text={item}
							/>
						</div>
					))}
				</SortableContext>
			</DndContext>
		</div>
	);
}
