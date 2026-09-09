"use client";

import { useState, useMemo } from "react";

import Button from "@/src/components/ui/Button";
import DnDList from "@/src/components/ui/DnDList";
import InputField from "@/src/components/ui/forms/InputField";
import MarkedSlider from "@/src/components/ui/sliders/MarkedSlider";

const componentPricing = {
	ramPerGB: 3.343,
	storagePerGB: 0.082,
	gpu: {
		Integrated: 0,
		"Mid-tier": 300,
		"High-end": 600,
	},
	peripherals: {
		Monitor: 120,
		Keyboard: 40,
		Mouse: 30,
		Headset: 60,
	},
};

const osCostMap: Record<string, number> = {
	"Windows 11": 120,
	Linux: 0,
};

const idealSetups: Record<
	string,
	{
		ram: number;
		storage: number;
		gpuTier: "Integrated" | "Mid-tier" | "High-end";
	}
> = {
	"General Use": { ram: 8, storage: 512, gpuTier: "Integrated" },
	"Studying & Coursework": { ram: 8, storage: 1024, gpuTier: "Integrated" },
	Gaming: { ram: 16, storage: 1024, gpuTier: "High-end" },
	"Content Creation": { ram: 32, storage: 2048, gpuTier: "High-end" },
	"Video Editing": { ram: 32, storage: 2048, gpuTier: "High-end" },
	Streaming: { ram: 16, storage: 1024, gpuTier: "Mid-tier" },
};

const gpuMap = { Integrated: 0, "Mid-tier": 1, "High-end": 2 };
const gpuReverseMap = ["Integrated", "Mid-tier", "High-end"];

const roundToNextPowerOf2 = (num: number) => 2 ** Math.ceil(Math.log2(num));

export default function BuildForm() {
	const [budget, setBudget] = useState<string>("£");
	const [listItems, setListItems] = useState<string[]>(
		Object.keys(idealSetups)
	);
	const [os, setOs] = useState<string>("Windows 11");

	const [ram, setRam] = useState<number>(0);
	const [storage, setStorage] = useState<number>(0);
	const [gpu, setGpu] = useState<number>(0);

	// New customisation fields (simplified)
	const [formFactor, setFormFactor] = useState<string>("Mid-tower");
	const [peripherals, setPeripherals] = useState<string[]>([]);
	const [aesthetics, setAesthetics] = useState<string>("No preference");

	// Logistics & Context
	const [urgency, setUrgency] = useState<string>("No rush");
	const [fileTransfer, setFileTransfer] = useState<boolean>(false);
	const [noiseSensitivity, setNoiseSensitivity] = useState<boolean>(false);
	const [networkPreference, setNetworkPreference] =
		useState<string>("Wi-Fi & Ethernet");

	// Compute min/best ranges
	const ranges = useMemo(() => {
		const top = idealSetups[listItems[0]];
		let minRam = roundToNextPowerOf2(top.ram);
		let bestRam = minRam;
		let minStorage = top.storage;
		let bestStorage = minStorage;
		let minGpu = gpuMap[top.gpuTier];
		let bestGpu = minGpu;

		listItems.slice(1).forEach((useCase, index) => {
			const ideal = idealSetups[useCase];
			const weight = 1 / 2 ** (index + 1);
			bestRam += (ideal.ram - bestRam) * weight;
			bestStorage += (ideal.storage - bestStorage) * weight;

			const idealGpu = gpuMap[ideal.gpuTier];
			if (idealGpu > bestGpu && weight >= 0.25) bestGpu = idealGpu;
		});

		bestRam = roundToNextPowerOf2(bestRam);
		bestStorage = Math.ceil(bestStorage / 128) * 128;

		if (ram < minRam) setRam(minRam);
		if (storage < minStorage) setStorage(minStorage);

		return { minRam, bestRam, minStorage, bestStorage, minGpu, bestGpu };
	}, [listItems]);

	const estimatedPrice = useMemo(() => {
		const gpuPrice = componentPricing.gpu[gpuReverseMap[gpu]];
		const ramPrice = ram * componentPricing.ramPerGB;
		const storagePrice = storage * componentPricing.storagePerGB;
		const osPrice = osCostMap[os] || 0;
		const peripheralsPrice = peripherals.reduce(
			(total, p) => total + (componentPricing.peripherals[p] || 0),
			0
		);

		return gpuPrice + ramPrice + storagePrice + osPrice + peripheralsPrice;
	}, [ram, storage, gpu, os, peripherals]);

	const overBudget = parseFloat(budget.replace(/^£/, "")) < estimatedPrice;

	const handleContinue = (e: any) => {
		e.preventDefault();
		console.log("Continue clicked", {
			ram,
			storage,
			gpu: gpuReverseMap[gpu],
			os,
			formFactor,
			peripherals,
			aesthetics,
			delivery,
			urgency,
			fileTransfer,
			noiseSensitivity,
			portNeeds,
			networkPreference,
		});
	};

	return (
		<div className="mx-4">
			<form onSubmit={handleContinue}>
				<div className="grid grid-cols-2 gap-6">
					<div className="space-y-3">
						<InputField
							name="budget"
							label="Budget (£)"
							value={budget}
							onChange={(value) => {
								const amount = value.replace(/^£/, "");
								if (/^\d*(\.\d{0,2})?$/.test(amount))
									setBudget(`£${amount}`);
							}}
						/>

						<select
							value={os}
							onChange={(e) => setOs(e.target.value)}
							className="input-field"
						>
							<option value="Windows 11">Windows 11</option>
							<option value="Linux">Linux</option>
						</select>

						<select
							value={formFactor}
							onChange={(e) => setFormFactor(e.target.value)}
							className="input-field"
						>
							<option value="Mini-ITX">Mini-ITX (compact)</option>
							<option value="Mid-tower">
								Mid-Tower (balanced)
							</option>
							<option value="Full-tower">
								Full-Tower (large)
							</option>
						</select>

						<select
							value={aesthetics}
							onChange={(e) => setAesthetics(e.target.value)}
							className="input-field"
						>
							<option value="No preference">No preference</option>
							<option value="RGB">RGB / flashy</option>
							<option value="Minimalist">
								Minimalist / clean
							</option>
							<option value="Silent">Silent / quiet build</option>
						</select>

						<select
							value={urgency}
							onChange={(e) => setUrgency(e.target.value)}
							className="input-field"
						>
							<option value="No rush">No rush</option>
							<option value="Moderate">Moderate urgency</option>
							<option value="High">High urgency</option>
						</select>

						<label className="flex items-center gap-2">
							<input
								type="checkbox"
								checked={fileTransfer}
								onChange={(e) =>
									setFileTransfer(e.target.checked)
								}
							/>
							Need files transferred from an old machine?
						</label>

						<label className="flex items-center gap-2">
							<input
								type="checkbox"
								checked={noiseSensitivity}
								onChange={(e) =>
									setNoiseSensitivity(e.target.checked)
								}
							/>
							Need this build to be quiet?
						</label>

						<select
							value={networkPreference}
							onChange={(e) =>
								setNetworkPreference(e.target.value)
							}
							className="input-field"
						>
							<option value="Wi-Fi & Ethernet">
								Wi-Fi & Ethernet
							</option>
							<option value="Ethernet only">Ethernet only</option>
							<option value="Wi-Fi only">Wi-Fi only</option>
						</select>

						<div className="space-y-2">
							<label className="text-sm font-medium">
								Peripherals Needed
							</label>
							<div className="flex gap-3 flex-wrap">
								{[
									"Monitor",
									"Keyboard",
									"Mouse",
									"Headset",
								].map((item) => (
									<label
										key={item}
										className="flex items-center gap-2"
									>
										<input
											type="checkbox"
											checked={peripherals.includes(item)}
											onChange={(e) =>
												setPeripherals((prev) =>
													e.target.checked
														? [...prev, item]
														: prev.filter(
																(p) =>
																	p !== item
														  )
												)
											}
										/>
										{item}
									</label>
								))}
							</div>
						</div>
					</div>
					<div>
						<div className="flex flex-col">
							<h2 className="text-xl font-semibold mb-3">
								Drag your priorities into order
							</h2>
							<DnDList
								items={listItems}
								setItems={setListItems}
								className="bg-transparent border-none"
							/>
						</div>
						<div
							className={`p-4 rounded-lg justify-between flex flex-col ${
								overBudget
									? "bg-(--red-accent)/60"
									: "bg-(--green-accent)/60"
							}`}
						>
							<h2 className="font-semibold text-xl">
								Estimated Build Specs
							</h2>
							<div className="px-5 my-6">
								<strong>RAM:</strong> {ram} GB
								<MarkedSlider
									value={ram}
									setValue={setRam}
									min={ranges.minRam}
									max={64}
									step={8}
									color="var(--green-accent)"
									markers={[8, 16, 32, 64]}
								/>
								<strong>Storage:</strong>{" "}
								{storage >= 1024
									? `${(storage / 1024).toFixed(2)} TB`
									: `${storage} GB`}
								<MarkedSlider
									value={storage}
									setValue={setStorage}
									min={ranges.minStorage}
									max={5120}
									step={64}
									color="var(--yellow-accent)"
									markers={[
										ranges.minStorage,
										...Array.from(
											{
												length:
													(5120 - ranges.minStorage) /
														1024 +
													1,
											},
											(_, i) => {
												return i * 1024;
											}
										),
										5120,
									].map((size) => ({
										label:
											size >= 1024
												? `${(size / 1024).toFixed(
														2
												  )} TB`
												: `${size}GB`,
										value: size,
									}))}
								/>
								<strong>GPU Tier:</strong> {gpuReverseMap[gpu]}
								<MarkedSlider
									value={gpu}
									setValue={setGpu}
									min={0}
									max={2}
									step={1}
									color="var(--blue-accent)"
									markers={[
										{ label: "Integrated", value: 0 },
										{ label: "Mid", value: 1 },
										{ label: "High", value: 2 },
									]}
								/>
							</div>
						</div>
					</div>
					<strong>Estimated Price:</strong> £
					{estimatedPrice.toFixed(2)}
					{overBudget && (
						<p className="text-(--orange-accent) font-semibold">
							Warning: Estimated build exceeds your budget!
						</p>
					)}
					<div className="flex w-full justify-center">
						<Button
							type="submit"
							className="my-5 w-90"
						>
							Continue plan
						</Button>
					</div>
				</div>
			</form>
		</div>
	);
}
