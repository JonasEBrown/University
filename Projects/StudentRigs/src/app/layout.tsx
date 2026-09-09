import "./globals.css";
import type { Metadata } from "next";
import { Montserrat } from "next/font/google";

import Header from "@/src/components/sections/Header";

const montserrat = Montserrat({
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "StudentRigs",
	description: "Power Your Studies, Play Your Games - We've Got You Covered",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body
				className={`h-screen w-screen text-white overflow-x-hidden overflow-y-scroll ${montserrat.className}`}
			>
				<Header />
				<main className="w-[90%] max-w-6xl mx-auto px-4 items-center">
					{children}
				</main>
			</body>
		</html>
	);
}
