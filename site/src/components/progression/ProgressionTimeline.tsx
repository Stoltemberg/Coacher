"use client";

import { motion } from "framer-motion";
import { Clock3, MemoryStick, TimerReset } from "lucide-react";

import type { PostGameSummary } from "@/types/bridge";

interface ProgressionTimelineProps {
  summary: PostGameSummary | null;
}

export default function ProgressionTimeline({ summary }: ProgressionTimelineProps) {
  const timeline = summary?.timeline ?? [];
  const memories = summary?.memory ?? [];
  const adaptive = summary?.insights.adaptive;

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.65, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
      className="grid gap-4 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.95fr)]"
    >
      <section className="app-surface overflow-hidden rounded-[28px]">
        <div className="soft-divider flex items-center justify-between px-5 py-4">
          <div>
            <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
              timeline
            </div>
            <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
              Momentos que puxaram a progressao
            </div>
          </div>
          <Clock3 className="h-5 w-5 text-[#ADFF2F]" />
        </div>

        <div className="custom-scrollbar max-h-[520px] space-y-3 overflow-y-auto p-5">
          {timeline.length > 0 ? (
            timeline.map((entry, index) => (
              <article
                key={`${entry.clock}-${entry.phase}-${index}`}
                className="rounded-[22px] border border-white/8 bg-white/[0.03] p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-mono uppercase tracking-[0.14em] text-white/48">
                    {entry.clock}
                  </span>
                  <span className="text-[10px] font-black uppercase tracking-[0.16em] text-sky-200">
                    {entry.phase}
                  </span>
                  <span className="text-[10px] uppercase tracking-[0.16em] text-white/28">
                    {entry.category}
                  </span>
                </div>

                <p className="mt-3 text-sm leading-6 text-white/78">{entry.text}</p>
                <p className="mt-2 text-xs leading-5 text-white/46">{entry.impact}</p>
              </article>
            ))
          ) : (
            <EmptyState
              title="Linha do tempo vazia"
              description="Quando um resumo de pos-jogo for enviado, os eventos-chave da partida aparecem aqui."
            />
          )}
        </div>
      </section>

      <div className="grid gap-4">
        <section className="app-surface overflow-hidden rounded-[28px]">
          <div className="soft-divider flex items-center justify-between px-5 py-4">
            <div>
              <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
                memoria
              </div>
              <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
                Registro recente
              </div>
            </div>
            <MemoryStick className="h-5 w-5 text-violet-300" />
          </div>

          <div className="grid gap-3 p-5">
            {memories.length > 0 ? (
              memories.slice(-4).reverse().map((entry, index) => (
                <div
                  key={`${entry.title}-${index}`}
                  className="rounded-[22px] border border-white/8 bg-white/[0.03] p-4"
                >
                  <div className="text-[10px] font-black uppercase tracking-[0.16em] text-white/32">
                    {entry.title}
                  </div>
                  <p className="mt-2 text-sm leading-6 text-white/68">{entry.note}</p>
                  {entry.meta ? (
                    <div className="mt-2 text-[10px] font-mono uppercase tracking-[0.14em] text-white/30">
                      {entry.meta}
                    </div>
                  ) : null}
                </div>
              ))
            ) : (
              <EmptyState
                title="Sem memoria recente"
                description="As anotacoes de repeticao, recuperacao e sinais do coach entram neste bloco."
              />
            )}
          </div>
        </section>

        <section className="app-surface overflow-hidden rounded-[28px]">
          <div className="soft-divider flex items-center justify-between px-5 py-4">
            <div>
              <div className="text-[10px] font-black uppercase tracking-[0.22em] text-white/42">
                adaptive
              </div>
              <div className="mt-1 text-lg font-semibold tracking-[-0.04em] text-white">
                Padroes do resumo
              </div>
            </div>
            <TimerReset className="h-5 w-5 text-sky-300" />
          </div>

          <div className="grid gap-3 p-5">
            <AdaptiveBlock
              title="repetidos"
              items={adaptive?.repeated_patterns ?? []}
              emptyMessage="Nenhum padrao repetido identificado."
            />
            <AdaptiveBlock
              title="recuperados"
              items={adaptive?.recovered_patterns ?? []}
              emptyMessage="Sem recuperacoes marcadas neste ciclo."
            />
            <AdaptiveBlock
              title="pressao por fase"
              items={adaptive?.phase_pressure ?? []}
              emptyMessage="Pressao por fase ainda nao mapeada."
            />
          </div>
        </section>
      </div>
    </motion.section>
  );
}

function AdaptiveBlock({
  title,
  items,
  emptyMessage,
}: {
  title: string;
  items: string[];
  emptyMessage: string;
}) {
  return (
    <div className="rounded-[22px] border border-white/8 bg-white/[0.03] p-4">
      <div className="text-[10px] font-black uppercase tracking-[0.18em] text-white/36">{title}</div>
      <div className="mt-3 space-y-2">
        {items.length > 0 ? (
          items.map((item) => (
            <div
              key={`${title}-${item}`}
              className="rounded-[16px] bg-white/[0.04] px-3 py-2 text-sm leading-6 text-white/72"
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

function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-[24px] border border-dashed border-white/12 bg-black/20 p-5">
      <div className="text-sm font-semibold text-white">{title}</div>
      <p className="mt-2 text-sm leading-6 text-white/46">{description}</p>
    </div>
  );
}
