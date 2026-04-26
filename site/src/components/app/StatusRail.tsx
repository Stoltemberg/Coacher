"use client";

import { AlertTriangle, Eye, Radar, Shield } from "lucide-react";

const icons = {
  neutral: Shield,
  live: Radar,
  focus: Eye,
  warning: AlertTriangle,
};

export default function StatusRail({
  items,
}: {
  items: Array<{
    label: string;
    value: string;
    detail?: string;
    tone?: "neutral" | "live" | "focus" | "warning";
  }>;
}) {
  return (
    <div className="grid gap-3 lg:grid-cols-4">
      {items.map((item) => {
        const Icon = icons[item.tone || "neutral"];
        return (
          <div
            key={`${item.label}-${item.value}`}
            className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] px-4 py-3"
          >
            <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">
              <Icon className={`h-3.5 w-3.5 ${item.tone === "focus" ? "text-[#ADFF2F]" : item.tone === "live" ? "text-[#38BDF8]" : item.tone === "warning" ? "text-amber-300" : "text-white/40"}`} />
              {item.label}
            </div>
            <div className="mt-2 text-[14px] font-semibold uppercase tracking-[0.04em] text-white">
              {item.value}
            </div>
            {item.detail ? <div className="mt-1 text-[10px] leading-5 text-white/42">{item.detail}</div> : null}
          </div>
        );
      })}
    </div>
  );
}

