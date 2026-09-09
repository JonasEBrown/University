import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline";
}

export function Button({ variant = "default", className = "", ...props }: ButtonProps) {
  const base =
    "px-4 py-2 rounded-xl font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500";
  const styles =
    variant === "outline"
      ? "bg-transparent border border-slate-700 text-slate-200 hover:bg-slate-800"
      : "bg-indigo-600 text-white hover:bg-indigo-700";

  return <button className={`${base} ${styles} ${className}`} {...props} />;
}
