"use client";

import { motion } from "framer-motion";
import { ArrowDownRight, ArrowUpRight, BarChart3, CircleDashed, Target } from "lucide-react";

import type { PerformanceSnapshot } from "@/types/bridge";

interface ProgressionMetricGridProps {
  performance: PerformanceSnapshot | null;
}

export default function ProgressionMetricGrid({ performance }: ProgressionMetricGridProps) {
  const metrics = performance?.metrics ?? [];

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.06, ease: [0.16, 1, 0.3, 1] }}
      className="grid gap-4 xl:grid-cols-[minmax(0,1.25fr)_320px]"
    >
      <section className="app-surface overflow-hidden rounded-[28px]">
        <div className="soft-divider flex items-center justify-between px-5 py-4">
          <div>
            <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
              performance
            </div>
            <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
              Metricas contra meta
            </div>
          </div>
          <BarChart3 className="h-5 w-5 text-[#ADFF2F]" />
        </div>

        <div className="grid gap-3 p-5 sm:grid-cols-2">
          {metrics.length > 0 ? (
            metrics.map((metric, index) => {
              const ratio = metric.target > 0 ? Math.max(0, Math.min(100, (metric.current / metric.target) * 100)) : 0;
              const isPositive = metric.delta >= 0;

              return (
                <motion.article
                  key={metric.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, duration: 0.35 }}
                  className="rounded-[24px] border border-white/8 bg-white/[0.03] p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-[9px] font-black uppercase tracking-[0.16em] text-white/35">
                        {metric.label}
                      </div>
                      <div className="mt-3 flex items-baseline gap-2">
                        <span className="text-3xl font-black tracking-[-0.07em] text-white">
                          {metric.current}
                        </span>
                        <span className="text-xs uppercase tracking-[0.14em] text-white/32">
                          / {metric.target}
                        </span>
                      </div>
                    </div>

                    <div
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-black uppercase tracking-[0.12em] ${
                        metric.status === "ahead"
                          ? "bg-[#ADFF2F]/12 text-[#D7FF7A]"
                          : metric.status === "close"
                            ? "bg-sky-400/12 text-sky-200"
                            : "bg-rose-400/12 text-rose-200"
                      }`}
                    >
                      {isPositive ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
                      {formatDelta(metric.delta)}
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="h-2 overflow-hidden rounded-full bg-white/8">
                      <div
                        className={`h-full rounded-full ${
                          metric.status === "ahead"
                            ? "bg-[#ADFF2F]"
                            : metric.status === "close"
                              ? "bg-sky-400"
                              : "bg-rose-400"
                        }`}
                        style={{ width: `${ratio}%` }}
                      />
                    </div>
                    <div className="mt-2 flex items-center justify-between text-[10px] uppercase tracking-[0.14em] text-white/32">
                      <span>meta</span>
                      <span>{Math.round(ratio)}% atingido</span>
                    </div>
                  </div>
                </motion.article>
              );
            })
          ) : (
            <EmptyPanel
              title="Sem metricas disponiveis"
              description="Assim que o snapshot de performance chegar, esta grade compara a execucao atual com a meta configurada."
            />
          )}
        </div>
      </section>

      <section className="app-surface overflow-hidden rounded-[28px]">
        <div className="soft-divider flex items-center justify-between px-5 py-4">
          <div>
            <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
              orientacao
            </div>
            <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
              Vetores da semana
            </div>
          </div>
          <Target className="h-5 w-5 text-violet-300" />
        </div>

        <div className="grid gap-3 p-5">
          <FocusList
            title="fortes"
            accent="lime"
            items={performance?.strongest_areas ?? []}
            emptyMessage="As fortalezas aparecem aqui quando houver leitura suficiente."
          />
          <FocusList
            title="foco"
            accent="violet"
            items={performance?.focus_areas ?? []}
            emptyMessage="Nenhum foco priorizado no snapshot atual."
          />
        </div>
      </section>
    </motion.section>
  );
}

function FocusList({
  title,
  items,
  emptyMessage,
  accent,
}: {
  title: string;
  items: string[];
  emptyMessage: string;
  accent: "lime" | "violet";
}) {
  const accentClasses = accent === "lime" ? "text-[#D7FF7A] bg-[#ADFF2F]/10" : "text-violet-200 bg-violet-400/10";

  return (
    <div className="rounded-[22px] border border-white/8 bg-white/[0.03] p-4">
      <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-[0.18em] text-white/45">
        <CircleDashed className="h-4 w-4" />
        {title}
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <span
              key={`${title}-${item}`}
              className={`rounded-full px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.06em] ${accentClasses}`}
            >
              {item}
            </span>
          ))
        ) : (
          <p className="text-sm leading-6 text-white/46">{emptyMessage}</p>
        )}
      </div>
    </div>
  );
}

function EmptyPanel({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="sm:col-span-2 rounded-[24px] border border-dashed border-white/12 bg-black/20 p-5">
      <div className="text-sm font-semibold text-white">{title}</div>
      <p className="mt-2 max-w-xl text-sm leading-6 text-white/48">{description}</p>
    </div>
  );
}

function formatDelta(delta: number) {
  return delta > 0 ? `+${delta}` : `${delta}`;
}
