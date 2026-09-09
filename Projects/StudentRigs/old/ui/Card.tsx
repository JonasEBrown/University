import { ReactNode } from "react";

export function Card({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-800 shadow-md p-4">
      {children}
    </div>
  );
}

export function CardHeader({ children }: { children: ReactNode }) {
  return <div className="mb-2">{children}</div>;
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <h3 className="text-lg font-semibold text-white">{children}</h3>;
}

export function CardContent({ children }: { children: ReactNode }) {
  return <div className="text-slate-300">{children}</div>;
}
