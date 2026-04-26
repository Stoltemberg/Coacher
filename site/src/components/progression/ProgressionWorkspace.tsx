"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowLeft, Bot, ChevronRight, Sparkles, Trophy } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import ProgressionHero from "./ProgressionHero";
import ProgressionInsightRail from "./ProgressionInsightRail";
import ProgressionMetricGrid from "./ProgressionMetricGrid";
import ProgressionTimeline from "./ProgressionTimeline";

export default function ProgressionWorkspace() {
  const { performance, summary } = useBridge();

  return (
    <main className="min-h-screen overflow-hidden bg-[#050508] text-white">
      <div className="app-backdrop" />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="mb-5 rounded-[28px] border border-white/8 bg-black/30 px-5 py-4 backdrop-blur-xl">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.22em] text-[#ADFF2F]">
                <Bot className="h-4 w-4" />
                write scope isolado
              </div>
              <h1 className="mt-2 text-3xl font-black tracking-[-0.06em] text-white sm:text-4xl">
                Painel de Progressao
              </h1>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-white/58">
                View independente para leitura de performance, diagnostico por resumo e definicao
                de proximos focos. Nenhum acoplamento com o shell principal ainda.
              </p>
            </div>

            <div className="flex flex-wrap gap-3">
              <Link
                href="/desktop"
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[11px] font-mono uppercase tracking-[0.16em] text-white/70 transition-colors hover:bg-white hover:text-black"
              >
                <ArrowLeft className="h-4 w-4" />
                desktop
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-2 rounded-full border border-[#ADFF2F]/25 bg-[#ADFF2F]/8 px-4 py-2 text-[11px] font-mono uppercase tracking-[0.16em] text-[#D7FF7A] transition-colors hover:bg-[#ADFF2F] hover:text-black"
              >
                landing
                <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </header>

        <div className="grid flex-1 gap-4 xl:grid-cols-[minmax(0,1.55fr)_360px]">
          <div className="flex min-h-0 flex-col gap-4">
            <ProgressionHero performance={performance} summary={summary} />
            <ProgressionMetricGrid performance={performance} />
            <ProgressionTimeline summary={summary} />
          </div>

          <motion.aside
            initial={{ opacity: 0, x: 18 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
            className="flex min-h-0 flex-col gap-4"
          >
            <section className="app-surface overflow-hidden rounded-[28px]">
              <div className="soft-divider flex items-center justify-between px-5 py-4">
                <div>
                  <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
                    status do snapshot
                  </div>
                  <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
                    Cobertura atual
                  </div>
                </div>
                <Trophy className="h-5 w-5 text-[#ADFF2F]" />
              </div>

              <div className="grid gap-3 p-5">
                <CoverageCard
                  label="performance"
                  value={performance ? "sincronizada" : "aguardando"}
                  detail={
                    performance
                      ? `${performance.matches_played} partidas avaliadas`
                      : "snapshot ainda nao carregado"
                  }
                  tone="lime"
                />
                <CoverageCard
                  label="summary"
                  value={summary ? "pronto para leitura" : "sem resumo recente"}
                  detail={summary ? summary.result : "aguardando pos-jogo"}
                  tone="violet"
                />
                <CoverageCard
                  label="headline"
                  value={performance?.headline || summary?.title || "sem chamada ativa"}
                  detail={summary?.focus || performance?.goal || "defina um objetivo para gerar direcao"}
                  tone="cyan"
                />
              </div>
            </section>

            <ProgressionInsightRail performance={performance} summary={summary} />

            <section className="app-surface rounded-[28px] p-5">
              <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.22em] text-[#ADFF2F]">
                <Sparkles className="h-4 w-4" />
                leitura da view
              </div>
              <p className="mt-3 text-sm leading-6 text-white/62">
                Esta rota ja pode ser conectada por navegacao futura sem retrabalho de markup.
                O estado vem direto do `BridgeContext`, entao ela acompanha o backend atual.
              </p>
            </section>
          </motion.aside>
        </div>
      </div>
    </main>
  );
}

function CoverageCard({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  tone: "lime" | "violet" | "cyan";
}) {
  const toneClasses = {
    lime: "text-[#D7FF7A] border-[#ADFF2F]/15 bg-[#ADFF2F]/6",
    violet: "text-violet-200 border-violet-400/15 bg-violet-400/[0.06]",
    cyan: "text-sky-200 border-sky-400/15 bg-sky-400/[0.06]",
  } as const;

  return (
    <div className={`rounded-[22px] border p-4 ${toneClasses[tone]}`}>
      <div className="text-[9px] font-black uppercase tracking-[0.18em] text-white/38">{label}</div>
      <div className="mt-2 text-sm font-semibold uppercase tracking-[0.06em]">{value}</div>
      <div className="mt-2 text-xs leading-5 text-white/56">{detail}</div>
    </div>
  );
}
