import "./globals.css";
import type { Metadata } from "next";

import { Cpu } from "lucide-react";
import { Button } from "@/old/ui/Button";

export const metadata: Metadata = {
  title: "Exeter PC Builder",
  description: "Custom PC builds for students and locals in Exeter",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
        <header className="sticky top-0 z-20 bg-slate-950/80 backdrop-blur border-b border-slate-800">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-xl">
              <Cpu className="w-6 h-6 text-indigo-400" /> Exeter PC Builders
            </div>
            <nav className="hidden md:flex gap-6 text-sm">
              <a href="#features" className="hover:underline">
                Features
              </a>
              <a href="#pricing" className="hover:underline">
                Pricing
              </a>
              <a href="#how" className="hover:underline">
                How it works
              </a>
              <a href="#extras" className="hover:underline">
                Extras
              </a>
              <a href="#faq" className="hover:underline">
                FAQ
              </a>
              <a href="#contact" className="hover:underline">
                Contact
              </a>
            </nav>
            <Button
              className="rounded-2xl bg-indigo-600 hover:bg-indigo-700"
            >
              Get a Quote
            </Button>
          </div>
        </header>
        {children}
      </body>
    </html>
  );
}
