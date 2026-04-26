"use client";

import type React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Brain, ShieldBan, Sparkles, Swords } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

interface TacticalModeSectionProps {
  isChampSelect: boolean;
}

export default function TacticalModeSection({ isChampSelect }: TacticalModeSectionProps) {
  const { draftRecommendations, matchIntel, jungleIntel } = useBridge();
  const recommendations = draftRecommendations?.recommendations ?? [];
  const topPick = recommendations[0];
  const bestBan = draftRecommendations?.best_ban;
  const lockedPlan = draftRecommendations?.locked_plan;
  const enemyPreview = draftRecommendations?.enemy_preview ?? [];

  if (!isChampSelect) {
    return (
      <section className="rounded-[28px] border border-white/[0.04] bg-[#050508] shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="flex items-center justify-between border-b border-white/[0.04] px-6 py-3">
          <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-violet-300">
            Modo Tatico
          </div>
          <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
            inativo fora da champ select
          </div>
        </div>
        <div className="grid gap-3 px-6 py-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)]">
          <CompactCard
            icon={<Sparkles className="h-4 w-4 text-violet-300" />}
            label="estado do draft"
            value="Draft recolhido nesta fase."
            detail="Durante a partida, esta area mostra apenas disponibilidade real do modulo tatico."
          />
          <CompactCard
            icon={<ShieldBan className="h-4 w-4 text-rose-300" />}
            label="roster carregado"
            value={`${matchIntel.length}/5 inimigos monitorados`}
            detail={jungleIntel?.enemy_jungler_champion ? `Jungler detectado: ${jungleIntel.enemy_jungler_champion}` : "Jungler ainda sem leitura completa."}
          />
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-[28px] border border-white/[0.04] bg-[#050508] shadow-[0_0_50px_rgba(0,0,0,0.45)]">
      <div className="flex items-center justify-between border-b border-white/[0.04] px-5 py-3.5">
        <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-violet-300">
          Modo Tatico
        </div>
        <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
          {draftRecommendations?.stage || "draft aberta"}
        </div>
      </div>

      <div className="grid gap-3 p-4 xl:grid-cols-[180px_minmax(0,1fr)_230px]">
        <aside className="space-y-3 rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-3">
          <div>
            <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-rose-300">
              <ShieldBan className="h-3.5 w-3.5" />
              melhor ban
            </div>
            {bestBan ? (
              <div className="rounded-[14px] border border-white/[0.05] bg-[#0A0A0C] p-3">
                <div className="text-[16px] font-semibold tracking-[-0.04em] text-white">
                  {bestBan.champion}
                </div>
                <div className="mt-1.5 text-[10px] uppercase tracking-[0.16em] text-white/35">
                  {bestBan.focus || "ban prioritario"}
                </div>
                <div className="mt-2.5 space-y-1.5">
                  {bestBan.reasons?.slice(0, 3).map((reason) => (
                    <div key={reason} className="line-clamp-2 text-[11px] leading-5 text-white/65">
                      {reason}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <EmptyBlock text="Aguardando leitura de ban." />
            )}
          </div>

          <div>
            <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
              <Swords className="h-3.5 w-3.5 text-[#ADFF2F]" />
              preview inimigo
            </div>
            <div className="flex flex-wrap gap-2">
              {enemyPreview.length > 0 ? (
                enemyPreview.map((enemy) => (
                  <span
                    key={enemy}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.14em] text-white/55"
                  >
                    {enemy}
                  </span>
                ))
              ) : (
                <EmptyInline text="Nenhum campeao revelado ainda." />
              )}
            </div>
          </div>

          <div>
            <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
              roster inimigo
            </div>
            <div className="space-y-2">
              {matchIntel.length > 0 ? (
                matchIntel.slice(0, 5).map((player) => (
                  <div
                    key={player.name}
                    className="rounded-[14px] border border-white/[0.05] bg-[#0A0A0C] px-3 py-2.5"
                  >
                    <div className="text-[12px] font-semibold text-white">{player.name}</div>
                    <div className="mt-1 line-clamp-1 text-[10px] text-white/45">
                      {player.champion || "sem campeao"} | {player.rank || "--"} | {player.winrate || "--"}
                    </div>
                  </div>
                ))
              ) : (
                <EmptyInline text="Rank e win rate aparecem aqui assim que o scraping terminar." />
              )}
            </div>
          </div>
        </aside>

        <main className="space-y-4">
          <div className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-3.5">
            <div className="mb-2.5 text-[9px] font-bold uppercase tracking-[0.18em] text-violet-300">
              melhor escolha agora
            </div>
            <AnimatePresence mode="wait">
              {topPick ? (
                <motion.div
                  key={`pick-${topPick.champion}`}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 12 }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-[20px] font-semibold tracking-[-0.05em] text-white">
                        {topPick.champion}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {[
                          topPick.focus,
                          topPick.context,
                          topPick.window,
                          topPick.familiarity,
                        ]
                          .filter(Boolean)
                          .map((badge) => (
                            <motion.span
                              key={badge}
                              layout
                            className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/45"
                          >
                            {badge}
                          </motion.span>
                        ))}
                      </div>
                    </div>
                    <div className="rounded-[16px] border border-[#ADFF2F]/20 bg-[#ADFF2F]/10 px-3 py-2.5 text-right">
                      <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-[#ADFF2F]">
                        score
                      </div>
                      <div className="mt-1 text-[20px] font-semibold tracking-[-0.04em] text-white">
                        {topPick.score.toFixed(2)}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid gap-3 lg:grid-cols-2">
                    <InfoPanel
                      title="motivos"
                      items={topPick.reasons?.slice(0, 2) || []}
                      empty="Sem justificativa consolidada."
                    />
                    <InfoPanel
                      title="plano de lane"
                      items={[
                        topPick.lane_plan_summary,
                        topPick.lane_win_condition,
                        topPick.lane_fail_condition,
                      ].filter(Boolean).slice(0, 2) as string[]}
                      empty="Sem plano de lane consolidado."
                    />
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="pick-loading"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 12 }}
                  className="space-y-3"
                >
                  <CompactLoadingCard
                    title="Aguardando pick relevante"
                    detail="Este bloco sobe quando a role e os picks revelados ficarem claros."
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <div className="grid gap-2 lg:grid-cols-3">
            <MetricCard
              label="role"
              value={draftRecommendations?.role || "sem role"}
              detail={`fase ${draftRecommendations?.stage || "draft"}`}
            />
            <MetricCard
              label="enemy stats"
              value={`${matchIntel.length}/5`}
              detail="players com rank/wr carregados"
            />
            <MetricCard
              label="selva"
              value={jungleIntel?.enemy_jungler_champion || "sem leitura"}
              detail={jungleIntel?.probable_side || "lado indefinido"}
            />
          </div>
        </main>

        <aside className="rounded-[18px] border border-violet-400/20 bg-[linear-gradient(180deg,rgba(139,92,246,0.10),rgba(5,5,8,0.65))] p-3.5">
          <div className="mb-2.5 flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.18em] text-violet-300">
            <Brain className="h-4 w-4" />
            sugestao do coach
          </div>
          <AnimatePresence mode="wait">
            {lockedPlan ? (
              <motion.div
                key={`locked-${lockedPlan.champion}`}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
                className="space-y-4"
              >
                <div>
                <div className="text-[18px] font-semibold tracking-[-0.04em] text-white">
                  {lockedPlan.champion}
                </div>
                  <div className="mt-1 text-[11px] uppercase tracking-[0.16em] text-white/35">
                    {lockedPlan.locked_focus} | vs {lockedPlan.enemy_anchor || "lane"}
                  </div>
                </div>
              <div className="line-clamp-4 text-[12px] leading-6 text-white/80">{lockedPlan.plan}</div>
              <InfoPanel
                title="prioridades"
                items={[
                  lockedPlan.lane_win_condition,
                  lockedPlan.lane_fail_condition,
                  lockedPlan.first_reset_focus,
                  lockedPlan.first_item_plan,
                ].filter(Boolean).slice(0, 3)}
                empty="Sem prioridades adicionais."
                compact
              />
              </motion.div>
            ) : topPick ? (
              <motion.div
                key={`coach-${topPick.champion}`}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
                className="space-y-4"
              >
                <div className="text-[16px] font-semibold tracking-[-0.04em] text-white">
                  {topPick.champion}
                </div>
                <div className="line-clamp-4 text-[12px] leading-6 text-white/75">
                  {topPick.lane_plan_summary ||
                    topPick.reasons?.[0] ||
                    "O coach ainda esta consolidando a melhor call principal."}
                </div>
                <InfoPanel
                  title="build e spikes"
                  items={[...(topPick.build_focus || []), ...(topPick.power_spikes || [])].slice(0, 3)}
                  empty="Sem build ou spikes relevantes ainda."
                  compact
                />
              </motion.div>
            ) : (
              <motion.div
                key="coach-loading"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 12 }}
              >
                <CompactLoadingCard
                  title="Coach montando a call"
                  detail="Este card sobe assim que ban, pick ou plano travado forem consolidados."
                />
              </motion.div>
            )}
          </AnimatePresence>
        </aside>
      </div>
    </section>
  );
}

function CompactCard({
  icon,
  label,
  value,
  detail,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-3.5">
      <div className="mb-1.5 flex items-center gap-2 text-[9px] font-bold uppercase tracking-[0.18em] text-white/35">
        {icon}
        {label}
      </div>
      <div className="text-[13px] font-semibold text-white">{value}</div>
      <div className="mt-1.5 text-[10px] leading-5 text-white/48">{detail}</div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] px-3 py-2.5">
      <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{label}</div>
      <div className="mt-1 text-[14px] font-semibold text-white">{value}</div>
      <div className="mt-1 text-[10px] text-white/42">{detail}</div>
    </div>
  );
}

function InfoPanel({
  title,
  items,
  empty,
  compact = false,
}: {
  title: string;
  items: string[];
  empty: string;
  compact?: boolean;
}) {
  return (
    <div className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] p-3">
      <div className="mb-3 text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{title}</div>
      {items.length > 0 ? (
        <div className={compact ? "space-y-2" : "space-y-3"}>
          {items.map((item) => (
            <div key={item} className={`text-white/72 ${compact ? "line-clamp-3 text-[11px] leading-5" : "line-clamp-3 text-[12px] leading-6"}`}>
              {item}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-[11px] leading-5 text-white/42">{empty}</div>
      )}
    </div>
  );
}

function EmptyBlock({ text }: { text: string }) {
  return (
    <div className="rounded-[16px] border border-dashed border-white/10 px-3 py-4 text-[11px] leading-5 text-white/40">
      {text}
    </div>
  );
}

function EmptyInline({ text }: { text: string }) {
  return <div className="text-[12px] leading-6 text-white/40">{text}</div>;
}

function CompactLoadingCard({
  title,
  detail,
}: {
  title: string;
  detail: string;
}) {
  return (
    <div className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] p-3">
      <div className="text-[13px] font-semibold text-white">{title}</div>
      <div className="mt-1.5 text-[11px] leading-5 text-white/48">{detail}</div>
      <div className="mt-3 space-y-2">
        {[0, 1].map((line) => (
          <motion.div
            key={line}
            initial={{ opacity: 0.3 }}
            animate={{ opacity: [0.25, 0.55, 0.25] }}
            transition={{ duration: 1.6, repeat: Infinity, delay: line * 0.12 }}
            className={`h-2 rounded-full bg-white/[0.08] ${line === 0 ? "w-[88%]" : "w-[72%]"}`}
          />
        ))}
      </div>
    </div>
  );
}
