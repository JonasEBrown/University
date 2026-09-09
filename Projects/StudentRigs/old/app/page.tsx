"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
	Cpu,
	Wrench,
	GraduationCap,
	MapPin,
	Shield,
	Zap,
	ShoppingCart,
	PhoneCall,
	Mail,
	Check,
	Stars,
	Trophy,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/old/ui/Card";
import { Button } from "@/old/ui/Button";
import { Input } from "@/old/ui/Input";
import { Textarea } from "@/old/ui/Textarea";
import { Accordion, AccordionItem } from "@/old/ui/Accordion";

export default function Home() {
	// contact form state
	const [name, setName] = useState("");
	const [email, setEmail] = useState("");
	const [uniArea, setUniArea] = useState("");
	const [budget, setBudget] = useState("");
	const [message, setMessage] = useState("");
	const [submitting, setSubmitting] = useState(false);
	const [sent, setSent] = useState(false);

	// checkout loading state
	const [checkoutLoading, setCheckoutLoading] = useState(false);

	const handleCheckout = async (plan: string) => {
		try {
			setCheckoutLoading(true);
			const res = await fetch("/api/checkout", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ plan }),
			});
			const data = await res.json();
			if (res.ok && data?.url) {
				window.location.href = data.url;
			} else {
				console.error(data);
				alert("Unable to start checkout. Check console for details.");
			}
		} catch (err) {
			console.error(err);
			alert("Checkout failed. See console.");
		} finally {
			setCheckoutLoading(false);
		}
	};

	const handleContact = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!name || !email)
			return alert("Please include your name and email.");
		setSubmitting(true);
		try {
			const res = await fetch("/api/contact", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ name, email, uniArea, budget, message }),
			});
			const data = await res.json();
			if (res.ok) {
				setSent(true);
				setName("");
				setEmail("");
				setUniArea("");
				setBudget("");
				setMessage("");
			} else {
				console.error(data);
				alert("Failed to send contact – check console for details.");
			}
		} catch (err) {
			console.error(err);
			alert("Failed to send contact");
		} finally {
			setSubmitting(false);
		}
	};

	const Feature = ({
		icon: Icon,
		title,
		desc,
	}: {
		icon: any;
		title: string;
		desc: string;
	}) => (
		<motion.div
			initial={{ opacity: 0, y: 16 }}
			whileInView={{ opacity: 1, y: 0 }}
			viewport={{ once: true }}
			transition={{ duration: 0.35 }}
			className="flex gap-4 rounded-2xl border border-slate-800 p-5 shadow-sm bg-slate-900"
		>
			<div className="rounded-xl p-3 border border-slate-700 bg-slate-800">
				<Icon className="w-6 h-6 text-indigo-400" />
			</div>
			<div>
				<h3 className="text-lg font-semibold text-white">{title}</h3>
				<p className="text-sm text-slate-400">{desc}</p>
			</div>
		</motion.div>
	);

	const Bullet = ({ children }: { children: React.ReactNode }) => (
		<li className="flex items-start gap-2 text-slate-300">
			<Check className="w-5 h-5 mt-0.5 text-indigo-400" />{" "}
			<span>{children}</span>
		</li>
	);

	return (
		<>
			<section className="relative overflow-hidden">
				<div className="max-w-6xl mx-auto px-4 py-20 grid lg:grid-cols-2 gap-10 items-center">
					<motion.div
						initial={{ opacity: 0, y: 16 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ duration: 0.5 }}
					>
						<div className="inline-flex items-center gap-2 text-xs border border-slate-700 rounded-full px-3 py-1 mb-4 text-slate-300">
							<Zap className="w-4 h-4 text-yellow-400" />{" "}
							Student-friendly • Exeter & nearby
						</div>
						<h1 className="text-4xl md:text-5xl font-extrabold leading-tight bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
							Custom PCs for Students & Exeter Locals
						</h1>
						<p className="mt-4 text-slate-300 text-lg">
							Get a powerful, quiet, and affordable PC tailored to
							your course, gaming, or creative work. We build,
							optimise, and support—so you can focus on what
							matters.
						</p>
						<div className="mt-6 flex flex-wrap gap-3">
							<Button
								size="lg"
								className="rounded-2xl bg-indigo-600 hover:bg-indigo-700"
								onClick={() => handleCheckout("student")}
							>
								<ShoppingCart className="w-5 h-5 mr-2" /> Book a
								Build Consult
							</Button>
							<Button
								size="lg"
								variant="outline"
								className="rounded-2xl border-slate-700 text-slate-300 hover:bg-slate-800"
								onClick={() =>
									document
										.getElementById("pricing")
										?.scrollIntoView({ behavior: "smooth" })
								}
							>
								See Pricing
							</Button>
						</div>
						<div className="mt-6 flex items-center gap-4 text-sm text-slate-400">
							<div className="flex items-center gap-2">
								<Shield className="w-4 h-4 text-green-400" />{" "}
								2-year build warranty
							</div>
							<div className="flex items-center gap-2">
								<MapPin className="w-4 h-4 text-blue-400" />{" "}
								Free Exeter delivery & setup
							</div>
						</div>
					</motion.div>

					<motion.div
						initial={{ opacity: 0, scale: 0.98 }}
						animate={{ opacity: 1, scale: 1 }}
						transition={{ duration: 0.6 }}
						className="relative"
					>
						<div className="aspect-video rounded-3xl border border-slate-800 shadow-xl bg-slate-900 grid place-items-center">
							<Cpu className="w-24 h-24 text-indigo-400" />
						</div>
						<div className="absolute -bottom-5 -left-5 bg-slate-800/90 rounded-2xl border border-slate-700 shadow p-3 text-sm flex items-center gap-2">
							<GraduationCap className="w-4 h-4 text-yellow-400" />{" "}
							Student discounts available
						</div>
					</motion.div>
				</div>
			</section>

			{/* Features */}
			<section
				id="features"
				className="max-w-6xl mx-auto px-4 py-14"
			>
				<div className="grid md:grid-cols-3 gap-6">
					<Feature
						icon={Wrench}
						title="Bespoke Build"
						desc="We spec and assemble your PC around your budget, course software, and games."
					/>
					<Feature
						icon={Shield}
						title="Stress-tested"
						desc="Each machine is thermally profiled, cable-managed, and burn-in tested."
					/>
					<Feature
						icon={Zap}
						title="Performance Tuned"
						desc="Firmware updates, XMP/EXPO, fan curves, and OS debloat for snappy performance."
					/>
					<Feature
						icon={MapPin}
						title="Local Service"
						desc="Free delivery, on-site setup in Exeter, plus lifetime basic support."
					/>
					<Feature
						icon={GraduationCap}
						title="Student Focused"
						desc="Advice for CAD, MATLAB, Python/AI, Adobe, and gaming—no fluff."
					/>
					<Feature
						icon={Cpu}
						title="Upgrade-ready"
						desc="Modular parts, clear upgrade paths, and honest guidance as needs grow."
					/>
				</div>
			</section>

			<section
				id="pricing"
				className="bg-(--background) border-t border-(--border)"
			>
				<div className="max-w-6xl mx-auto px-4 py-16">
					<h2 className="text-3xl font-bold mb-8 text-(--primary-text)">
						Simple pricing
					</h2>
					<div className="grid md:grid-cols-3 gap-6">
						{[
							{
								title: "Student Essentials",
								desc: "Great for coursework and light gaming",
								price: "£699–£899",
								bullets: [
									"AMD/Intel 6-core CPU",
									"16GB RAM, 1TB NVMe",
									"Entry-level GPU for 1080p",
									"Compact, ready-to-go setup",
								],
								plan: "student",
							},
							{
								title: "Creator / STEM",
								desc: "Perfect for Adobe, CAD, coding, and AI starters",
								price: "£999–£1,399",
								bullets: [
									"8–12 core CPU",
									"32GB RAM, 2TB NVMe + RTX GPU",
									"Whisper-quiet case",
									"Delivered fully setup, OS installed",
								],
								plan: "creator",
							},
							{
								title: "Custom & Gaming",
								desc: "Max FPS or showcase aesthetic builds",
								price: "From £1,499",
								bullets: [
									"Curated high-end parts",
									"Full customisation options (even OS)",
									"Advanced airflow + temps",
									"Plug-and-play delivery",
								],
								plan: "custom",
							},
						].map((p) => (
							<FeatureCard
								key={p.title}
								title={p.title}
								desc={p.desc}
							>
								<div className="text-4xl font-extrabold text-(--primary-accent) mb-2">
									{p.price}
								</div>
								<ul className="space-y-2 text-sm mb-4">
									{p.bullets.map((b) => (
										<li
											key={b}
											className="flex items-start gap-2 text-(--secondary-text)"
										>
											<Check className="w-5 h-5 mt-0.5 text-(--primary-accent)" />{" "}
											{b}
										</li>
									))}
								</ul>
								<Button
									href=""
									className="w-full rounded-2xl bg-(--primary-accent) hover:bg-(--primary-accent)/80"
								>
									Choose plan
								</Button>
							</FeatureCard>
						))}
					</div>
					<p className="text-xs text-(--secondary-text) mt-4">
						Prices include build, OS install, drivers, optimisation,
						and local delivery. Parts may vary by stock.
					</p>
				</div>
			</section>
		</>
	);
}
