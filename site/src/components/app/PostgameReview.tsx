"use client";

import type React from "react";
import { AlertTriangle, CheckCircle2, Sparkles, TimerReset } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import CoachCallCard from "./CoachCallCard";
import StatusRail from "./StatusRail";

export default function PostgameReview() {
  const { summary, performance } = useBridge();

  if (!summary) {
    return (
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] px-6 py-8 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-violet-300">Pos-jogo</div>
        <div className="mt-4 text-[14px] leading-7 text-white/48">
          O review sobe aqui assim que uma partida for encerrada e o coach consolidar resumo, erros principais e proximo foco.
        </div>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.18em] text-violet-300">
            <Sparkles className="h-4 w-4" />
            Pos-jogo
          </div>
          <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
            {summary.result} | {summary.duration}
          </div>
        </div>
        <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <CoachCallCard
            eyebrow="review principal"
            title={summary.focus || summary.insights.headline}
            detail={summary.insights.opening}
            tags={[summary.scoreline, summary.confidence, performance?.role || "role"]}
          />
          <StatusRail
            items={[
              { label: "resultado", value: summary.result, detail: summary.scoreline, tone: "warning" },
              { label: "recorde", value: performance?.record || "--", detail: `${performance?.matches_played || 0} partidas`, tone: "neutral" },
              { label: "foco", value: performance?.focus_areas?.[0] || "sem foco", detail: performance?.goal || "sem meta", tone: "focus" },
              { label: "confianca", value: summary.confidence, detail: summary.title, tone: "live" },
            ]}
          />
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr_1fr]">
        <ReviewPanel
          icon={<AlertTriangle className="h-4 w-4 text-rose-300" />}
          title="erros principais"
          items={summary.insights.improvements.slice(0, 3)}
        />
        <ReviewPanel
          icon={<CheckCircle2 className="h-4 w-4 text-[#ADFF2F]" />}
          title="acertos"
          items={summary.insights.strengths.slice(0, 3)}
        />
        <ReviewPanel
          icon={<TimerReset className="h-4 w-4 text-[#38BDF8]" />}
          title="proxima partida"
          items={summary.insights.next_steps.slice(0, 3)}
        />
      </div>
    </div>
  );
}

function ReviewPanel({
  icon,
  title,
  items,
}: {
  icon: React.ReactNode;
  title: string;
  items: string[];
}) {
  return (
    <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
      <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
        {icon}
        {title}
      </div>
      {items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item} className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] px-4 py-3 text-[12px] leading-6 text-white/74">
              {item}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-[12px] leading-6 text-white/40">Sem itens consolidados aqui ainda.</div>
      )}
    </section>
  );
}

