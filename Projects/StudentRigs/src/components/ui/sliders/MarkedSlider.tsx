"use client";

import { useEffect } from "react";
import * as Slider from "@radix-ui/react-slider";

export interface Marker {
	label: string;
	value: number;
}

export type MarkerType = Marker | number;

export default function MarkedSlider({
	value,
	setValue,
	min,
	max,
	step,
	color,
	markers,
	className,
}: {
	value: number;
	setValue: (value: number) => void;
	min: number;
	max: number;
	step?: number;
	color?: string;
	markers?: MarkerType[];
	className?: string;
	[key: string]: any;
}) {
	const processedMarkers: Marker[] = [...new Set(markers)]
		.map((marker) =>
			typeof marker === "number"
				? {
						label: String(marker),
						value: marker,
				  }
				: marker
		)
		.filter((marker) => marker.value >= min && marker.value <= max);

	console.log(markers, processedMarkers);

	const range = max - min;
	const paddingPercent = 5;
	const sliderWidthPercent = 100 - 2 * paddingPercent;

	const markerPercent = (val: number) =>
		paddingPercent + ((val - min) / range) * sliderWidthPercent;

	return (
		<div className={`relative w-full h-12 my-4 ${className}`}>
			<div className="absolute top-1.5 h-3 rounded-full bg-(--border) w-full z-0 outline-(--border) outline-4" />

			<div
				className="absolute top-1.5 h-3 rounded-l-full z-0"
				style={{
					backgroundColor: color,
					width: `${paddingPercent}%`,
				}}
			/>

			<div className="absolute top-0 left-0 w-full h-12 pointer-events-none">
				{processedMarkers.map((marker) => {
					return (
						<div
							key={marker.value}
							className="absolute flex flex-col items-center -translate-x-1/2 z-1 translate-y-2/13 select-none pointer-events-none"
							style={{
								left: `${markerPercent(marker.value)}%`,
							}}
						>
							<div className="w-1 h-3 bg-(--primary-text) rounded-sm" />
							<span className="text-xs text-(--primary-text) mt-2">
								{marker.label}
							</span>
						</div>
					);
				})}
			</div>

			<Slider.Root
				className="relative flex items-center h-3"
				value={[value]}
				min={min}
				max={max}
				step={step || 1}
				onValueChange={(vals) => {
					let pos = vals[0];

					processedMarkers.forEach((marker) => {
						if (Math.abs(pos - marker.value) <= min / 4)
							pos = marker.value;
					});

					setValue(pos);
				}}
				style={{
					width: `${100 + 3 - 2 * paddingPercent}%`,
					left: `${paddingPercent - 1.5}%`,
				}}
			>
				<Slider.Track className="bg-transparent relative flex-1 h-3 rounded-full z-0">
					<div
						className="absolute h-full translate-y-1/2"
						style={{
							backgroundColor: color,
							left: 0,
							width: `${((value - min) / range) * 100}%`,
							borderTopRightRadius: `${
								(value - min) / range === 1
									? "calc(infinity * 1px)"
									: "0%"
							}`,
							borderBottomRightRadius: `${
								(value - min) / range === 1
									? "calc(infinity * 1px)"
									: "0%"
							}`,
						}}
					/>
				</Slider.Track>

				<Slider.Thumb className="block w-5 h-5 bg-white rounded-full shadow translate-y-1/4 z-10" />
			</Slider.Root>
		</div>
	);
}
