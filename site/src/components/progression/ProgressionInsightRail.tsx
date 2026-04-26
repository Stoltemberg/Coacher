"use client";

import { BrainCircuit, RotateCcw, TrendingUp } from "lucide-react";

import type { PerformanceSnapshot, PostGameSummary } from "@/types/bridge";

interface ProgressionInsightRailProps {
  performance: PerformanceSnapshot | null;
  summary: PostGameSummary | null;
}

export default function ProgressionInsightRail({
  performance,
  summary,
}: ProgressionInsightRailProps) {
  const insights = summary?.insights;

  return (
    <section className="app-surface overflow-hidden rounded-[28px]">
      <div className="soft-divider flex items-center justify-between px-5 py-4">
        <div>
          <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
            summary
          </div>
          <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
            Diagnostico e proximo loop
          </div>
        </div>
        <BrainCircuit className="h-5 w-5 text-sky-300" />
      </div>

      <div className="grid gap-4 p-5">
        <RailBlock
          icon={TrendingUp}
          title="strengths"
          items={insights?.strengths ?? performance?.strongest_areas ?? []}
          emptyMessage="Sem forcas consolidadas no momento."
          accent="lime"
        />
        <RailBlock
          icon={RotateCcw}
          title="improvements"
          items={insights?.improvements ?? performance?.focus_areas ?? []}
          emptyMessage="Nenhuma melhoria priorizada ainda."
          accent="violet"
        />
        <RailBlock
          icon={BrainCircuit}
          title="next steps"
          items={insights?.next_steps ?? []}
          emptyMessage="O resumo ainda nao trouxe proximos passos."
          accent="cyan"
        />
      </div>
    </section>
  );
}

function RailBlock({
  icon: Icon,
  title,
  items,
  emptyMessage,
  accent,
}: {
  icon: typeof BrainCircuit;
  title: string;
  items: string[];
  emptyMessage: string;
  accent: "lime" | "violet" | "cyan";
}) {
  const accentClasses = {
    lime: "bg-[#ADFF2F]/10 text-[#D7FF7A]",
    violet: "bg-violet-400/10 text-violet-200",
    cyan: "bg-sky-400/10 text-sky-200",
  } as const;

  return (
    <div className="rounded-[22px] border border-white/8 bg-white/[0.03] p-4">
      <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.18em] text-white/42">
        <Icon className="h-4 w-4" />
        {title}
      </div>

      <div className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item) => (
            <div
              key={`${title}-${item}`}
              className={`rounded-[16px] px-3 py-2 text-sm leading-6 ${accentClasses[accent]}`}
            >
              {item}
            </div>
          ))
        ) : (
          <p className="text-sm leading-6 text-white/46">{emptyMessage}</p>
        )}
      </div>
    </div>
  );
}
