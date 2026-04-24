"use client";

import { useBridge } from "@/contexts/BridgeContext";
import { motion } from "framer-motion";
import { ShieldCheck, Sparkles, Swords } from "lucide-react";

const normalizeChampionName = (value: string) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9\s'-]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

interface MatchIntelPanelProps {
  tacticalMode?: boolean;
}

export default function MatchIntelPanel({ tacticalMode = false }: MatchIntelPanelProps) {
  const { draftRecommendations, matchIntel, settings } = useBridge();
  const hasRecommendations = Boolean(draftRecommendations?.recommendations?.length);
  const preferredPool = settings?.preferred_champion_pool ?? [];
  const preferredPoolSet = new Set(preferredPool.map(normalizeChampionName));
  const recommendedPicks = [...(draftRecommendations?.recommendations ?? [])].sort((left, right) => {
    if (!(settings?.prioritize_pool_picks && preferredPoolSet.size > 0)) {
      return right.score - left.score;
    }

    const leftPreferred = preferredPoolSet.has(normalizeChampionName(left.champion));
    const rightPreferred = preferredPoolSet.has(normalizeChampionName(right.champion));

    if (leftPreferred !== rightPreferred) {
      return leftPreferred ? -1 : 1;
    }

    return right.score - left.score;
  });
  const visiblePicks = tacticalMode ? recommendedPicks.slice(0, 4) : recommendedPicks.slice(0, 3);

  if ((!matchIntel || matchIntel.length === 0) && !hasRecommendations) {
    return (
      <div className="app-surface w-full overflow-hidden rounded-[24px]">
        <div className="soft-divider flex items-center justify-between px-4 py-3">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/65">
            {tacticalMode ? "Leitura de draft" : "Time inimigo"}
          </span>
          <div className="h-2 w-2 rounded-full bg-toxic shadow-[0_0_12px_rgba(173,255,47,0.6)]" />
        </div>
        <div className={`flex items-center gap-4 px-4 ${tacticalMode ? "py-7" : "py-5"}`}>
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Swords className="h-5 w-5 text-toxic/60" />
          </div>
          <div className="space-y-1">
            <p className="text-[11px] font-semibold text-white">Aguardando leitura de draft</p>
            <p className="text-[11px] text-white/45">
              {tacticalMode
                ? "Assim que a composicao aparecer, o modo tatico destaca counters e leituras de draft aqui."
                : "Os nomes inimigos aparecem aqui assim que o cliente liberar a composicao."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-surface flex h-full flex-col overflow-hidden rounded-[24px]">
      <div className="soft-divider flex items-center justify-between px-4 py-3">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/65">
          {tacticalMode ? "Draft tatico" : "Time inimigo"}
        </span>
        <div className="flex items-center gap-2">
          {tacticalMode && (
            <span className="rounded-full border border-toxic/25 bg-toxic/10 px-3 py-1 text-[9px] font-mono uppercase tracking-[0.16em] text-toxic">
              foco em picks
            </span>
          )}
          <Swords className="h-4 w-4 text-toxic" />
        </div>
      </div>

      <div className={`custom-scrollbar overflow-y-auto p-3 ${tacticalMode ? "space-y-4" : "space-y-3"}`}>
        {hasRecommendations ? (
          <div className={`rounded-2xl border border-toxic/20 bg-toxic/10 ${tacticalMode ? "p-4" : "p-3"}`}>
            <div className="mb-2 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-toxic" />
              <span className="text-[10px] font-black uppercase tracking-[0.18em] text-white/75">
                melhores picks agora
              </span>
              {tacticalMode && <Sparkles className="h-3.5 w-3.5 text-toxic/80" />}
            </div>
            {settings?.prioritize_pool_picks && preferredPool.length > 0 ? (
              <div className="mb-3 text-[10px] leading-5 text-white/45">
                Picks da tua pool sobem na lista quando aparecem nas recomendacoes.
              </div>
            ) : null}
            <div className={tacticalMode ? "grid gap-3 xl:grid-cols-2" : "space-y-2"}>
              {visiblePicks.map((pick) => (
                <div
                  key={pick.champion}
                  className={`rounded-2xl border border-white/8 bg-black/20 ${tacticalMode ? "px-4 py-4" : "px-3 py-3"}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <div className={`${tacticalMode ? "text-sm" : "text-[11px]"} font-semibold text-white`}>
                          {pick.champion}
                        </div>
                        {preferredPoolSet.has(normalizeChampionName(pick.champion)) ? (
                          <span className="rounded-full border border-toxic/20 bg-toxic/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-toxic">
                            tua pool
                          </span>
                        ) : null}
                      </div>
                      <div className="mt-1 text-[10px] text-white/42">
                        {(pick.reasons || []).slice(0, 2).join(" | ")}
                      </div>
                      {tacticalMode && pick.power_spikes?.[0] ? (
                        <div className="mt-2 text-[10px] text-white/32">
                          spike: {pick.power_spikes[0]}
                        </div>
                      ) : null}
                    </div>
                    <div className="rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-toxic">
                      {Math.round(pick.score)}
                    </div>
                  </div>
                  {tacticalMode && (
                    <div className="mt-3 space-y-2">
                      <div className="text-[10px] uppercase tracking-[0.14em] text-white/35">
                        {pick.comp_style}
                      </div>
                      {pick.build_focus.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {pick.build_focus.slice(0, 3).map((focus) => (
                            <span
                              key={focus}
                              className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] uppercase tracking-[0.12em] text-white/55"
                            >
                              {focus}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : null}

        <div className={`grid gap-2 ${tacticalMode ? "grid-cols-1 2xl:grid-cols-2" : "grid-cols-1"}`}>
          {matchIntel.map((player, idx) => (
            <motion.div
              key={player.name}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.06 }}
              className={`rounded-2xl border border-white/8 bg-white/[0.04] transition-colors hover:border-white/15 hover:bg-white/[0.06] ${
                tacticalMode ? "px-4 py-4" : "px-3 py-3"
              }`}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex flex-col">
                  <span
                    className={`truncate font-semibold text-white ${
                      tacticalMode ? "max-w-[220px] text-[12px]" : "max-w-[140px] text-[11px]"
                    }`}
                  >
                    {player.name}
                  </span>
                  <span className="text-[10px] text-white/45">
                    {player.champion || "Desconhecido"}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="block text-[9px] uppercase tracking-[0.12em] text-white/35">
                      elo
                    </span>
                    <span className="text-[11px] font-semibold text-violet-300">
                      {player.rank || "--"}
                    </span>
                  </div>
                  <div className="min-w-[52px] text-right">
                    <span className="block text-[9px] uppercase tracking-[0.12em] text-white/35">
                      wr
                    </span>
                    <span className="text-[11px] font-semibold text-toxic">
                      {player.winrate || "--"}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
