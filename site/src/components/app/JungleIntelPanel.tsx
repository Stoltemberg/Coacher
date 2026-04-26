"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Compass, Radar } from "lucide-react";

export default function JungleIntelPanel() {
  const { jungleIntel: intel } = useBridge();

  const isEmpty = !intel || (!intel.enemy_jungler_name && !intel.enemy_jungler_champion);
  const sourceLabel = (value?: string | null) => {
    if (!value) return "fonte local";
    if (value === "summoner_spells") return "smite detectado";
    if (value === "roster") return "roster";
    if (value === "champion_kill") return "kill";
    if (value === "dragonkill") return "dragao";
    if (value === "heraldkill") return "arauto";
    if (value === "baronkill") return "barao";
    if (value === "hordekill") return "larvas";
    return value;
  };

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="soft-divider flex items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <Radar className="h-4 w-4 text-toxic" />
          <span className="text-[10px] font-black uppercase tracking-[0.18em] text-white/65">
            Jungle tracker
          </span>
        </div>
        {!isEmpty && intel && (
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[9px] font-mono uppercase tracking-[0.16em] text-white/50">
            confianca {Math.round(intel.confidence * 100)}%
          </span>
        )}
      </div>

      <div className="custom-scrollbar flex-1 overflow-y-auto p-4">
        <AnimatePresence mode="wait">
          {isEmpty ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex h-full flex-col items-center justify-center gap-4 text-center"
            >
              <div className="flex h-20 w-20 items-center justify-center rounded-full border border-white/10 bg-white/[0.03]">
                <Compass className="h-7 w-7 text-toxic/45" />
              </div>
              <div className="space-y-2">
                <p className="text-[11px] font-semibold text-white">Esperando leitura de selva</p>
                <p className="mx-auto max-w-[220px] text-[11px] leading-6 text-white/40">
                  Assim que o cliente fornecer dados de rota e rastros do jungler, este painel preenche automaticamente.
                </p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="content"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <div className="rounded-[24px] border border-white/8 bg-white/[0.04] p-4">
                <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
                  alvo prioritario
                </div>
                <div className="mt-2 text-lg font-semibold text-white">
                  {intel.enemy_jungler_champion || "Jungler inimigo"}
                </div>
                <div className="mt-1 text-[11px] text-white/45">
                  {intel.enemy_jungler_name || "Nome ainda nao identificado"}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-[22px] border border-white/8 bg-white/[0.04] p-4">
                  <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
                    Ultima leitura
                  </div>
                  <div className="mt-2 text-sm font-semibold text-white">
                    {intel.last_seen_clock || "--:--"}
                  </div>
                  <div className="mt-1 text-[11px] text-white/40">
                    {sourceLabel(intel.last_seen_source)}
                  </div>
                </div>
                <div className="rounded-[22px] border border-white/8 bg-white/[0.04] p-4">
                  <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
                    Lado provavel
                  </div>
                  <div className="mt-2 text-sm font-semibold text-white">
                    {intel.probable_side || "scanning"}
                  </div>
                  <div className="mt-1 text-[11px] text-white/40">
                    pressao recente na selva
                  </div>
                </div>
              </div>

              <div className="rounded-[24px] border border-white/8 bg-white/[0.04] p-4">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
                    Presenca em objetivos
                  </span>
                  <Activity className="h-4 w-4 text-white/30" />
                </div>
                <div className="space-y-3">
                  {Object.entries(intel.objective_presence).map(([objective, score]) => (
                    <div key={objective} className="space-y-1">
                      <div className="flex items-center justify-between text-[11px] text-white/55">
                        <span className="capitalize">{objective}</span>
                        <span>{score}</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-white/8">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${Math.max(8, (score / 4) * 100)}%` }}
                          className="h-full rounded-full bg-toxic"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-[24px] border border-white/8 bg-white/[0.04] p-4">
                <div className="mb-3 text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
                  Notas recentes
                </div>
                <div className="space-y-2">
                  {intel.notes.length > 0 ? (
                    intel.notes.slice(0, 4).map((note, idx) => (
                      <motion.div
                        key={`${note.clock}-${idx}`}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3"
                      >
                        <div className="mb-1 flex items-center justify-between gap-3">
                          <span className="text-[11px] font-semibold text-white">{note.title}</span>
                          <span className="text-[9px] font-mono uppercase tracking-[0.12em] text-white/30">
                            {note.clock}
                          </span>
                        </div>
                        <p className="text-[11px] leading-6 text-white/45">{note.detail}</p>
                      </motion.div>
                    ))
                  ) : (
                    <div className="rounded-2xl border border-dashed border-white/10 px-3 py-6 text-center text-[11px] text-white/35">
                      Nenhum rastro recente detectado.
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
