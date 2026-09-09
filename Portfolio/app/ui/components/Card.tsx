import React from "react";

export function Card({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className="rounded-2xl shadow-md border border-neutral-800">
        <div className="p-6">
            {children}
        </div>
    </div>
  );
}
