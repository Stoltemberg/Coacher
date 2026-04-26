"use client";

import { motion } from "framer-motion";
import { Gauge, Goal, ShieldCheck, Swords } from "lucide-react";

import type { PerformanceSnapshot, PostGameSummary } from "@/types/bridge";

interface ProgressionHeroProps {
  performance: PerformanceSnapshot | null;
  summary: PostGameSummary | null;
}

export default function ProgressionHero({ performance, summary }: ProgressionHeroProps) {
  const headline =
    performance?.headline || summary?.insights.headline || "Progressao pronta para telemetria";
  const description =
    summary?.insights.opening ||
    summary?.focus ||
    "Assim que performance e pos-jogo forem atualizados, este painel mostra o eixo principal da evolucao.";
  const confidence = summary?.confidence || "Sem calibragem recente";
  const winRate =
    performance && Number.isFinite(performance.win_rate)
      ? `${Math.round(performance.win_rate)}%`
      : "--";

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      className="app-surface overflow-hidden rounded-[32px]"
    >
      <div className="relative p-6 sm:p-7">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(173,255,47,0.10),transparent_30%),radial-gradient(circle_at_85%_10%,rgba(56,189,248,0.12),transparent_24%)]" />

        <div className="relative grid gap-6 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.9fr)]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#ADFF2F]/15 bg-[#ADFF2F]/8 px-3 py-1 text-[10px] font-black uppercase tracking-[0.18em] text-[#D7FF7A]">
              <Gauge className="h-4 w-4" />
              leitura de progressao
            </div>

            <h2 className="mt-5 max-w-3xl text-3xl font-black tracking-[-0.07em] text-white sm:text-[2.7rem] sm:leading-[1.02]">
              {headline}
            </h2>

            <p className="mt-4 max-w-2xl text-sm leading-7 text-white/64 sm:text-[15px]">
              {description}
            </p>

            <div className="mt-6 flex flex-wrap gap-3">
              <HeroChip icon={Swords} label="role" value={performance?.role || "nao definida"} />
              <HeroChip icon={Goal} label="goal" value={performance?.goal || "sem meta ativa"} />
              <HeroChip icon={ShieldCheck} label="confidence" value={confidence} />
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            <SpotlightCard
              label="record"
              value={performance?.record || "--"}
              detail={`${performance?.matches_played ?? 0} partidas rastreadas`}
            />
            <SpotlightCard
              label="win rate"
              value={winRate}
              detail={summary?.result || "resultado pendente"}
            />
            <SpotlightCard
              label="focus"
              value={summary?.focus || performance?.goal || "sem foco"}
              detail={summary?.duration || "sem duracao"}
            />
          </div>
        </div>
      </div>
    </motion.section>
  );
}

function HeroChip({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Gauge;
  label: string;
  value: string;
}) {
  return (
    <div className="inline-flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.04] px-3 py-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/[0.05]">
        <Icon className="h-4 w-4 text-[#ADFF2F]" />
      </div>
      <div>
        <div className="text-[9px] font-black uppercase tracking-[0.16em] text-white/35">{label}</div>
        <div className="text-[11px] font-semibold uppercase tracking-[0.06em] text-white/78">{value}</div>
      </div>
    </div>
  );
}

function SpotlightCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[24px] border border-white/8 bg-black/25 p-4 backdrop-blur-sm">
      <div className="text-[9px] font-black uppercase tracking-[0.16em] text-white/35">{label}</div>
      <div className="mt-3 text-lg font-semibold tracking-[-0.05em] text-white">{value}</div>
      <div className="mt-2 text-xs leading-5 text-white/55">{detail}</div>
    </div>
  );
}
