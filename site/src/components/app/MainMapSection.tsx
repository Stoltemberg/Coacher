"use client";

import Image from "next/image";
import { Eye, Radar, ShieldAlert, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { useBridge } from "@/contexts/BridgeContext";

interface MainMapSectionProps {
  isChampSelect: boolean;
}

const phaseLabel = (phase: string) => {
  const normalized = (phase || "").toLowerCase();
  if (normalized.includes("champ")) return "Selecao de Campeoes";
  if (normalized.includes("progress")) return "Em partida";
  if (normalized.includes("lobby")) return "Lobby";
  return phase || "Aguardando";
};

export default function MainMapSection({ isChampSelect }: MainMapSectionProps) {
  const { gameState, summary, logs, jungleIntel, matchIntel, draftRecommendations } = useBridge();

  const mapHeight = isChampSelect ? "h-[300px]" : "h-[520px]";
  const phase = gameState.phase || "Lobby";
  const focus = resolveFocus({
    isChampSelect,
    summary,
    logs,
    jungleIntel,
    draftRecommendations,
  });
  const recentReads = resolveReads({
    isChampSelect,
    summary,
    logs,
    jungleIntel,
    matchIntel,
    draftRecommendations,
  });
  const liveStatus = [
    {
      label: "fase",
      value: phaseLabel(phase),
      tone: "text-[#38BDF8]",
    },
    {
      label: "campeao",
      value: gameState.championName || "nao detectado",
      tone: "text-white",
    },
    {
      label: "selva",
      value: jungleIntel?.enemy_jungler_champion || "sem leitura",
      tone: "text-[#ADFF2F]",
    },
    {
      label: "inimigos",
      value: `${matchIntel.length}/5 carregados`,
      tone: "text-violet-300",
    },
  ];

  return (
    <section className="overflow-hidden rounded-[28px] border border-white/[0.04] bg-[#050508] shadow-[0_0_50px_rgba(0,0,0,0.45)]">
      <div className="flex items-center justify-between border-b border-white/[0.04] px-5 py-3">
        <div className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
          <Eye className="h-4 w-4" />
          Visao da Partida
        </div>
        <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/40">
          {phaseLabel(phase)}
        </div>
      </div>

      <div className={`relative overflow-hidden ${mapHeight}`}>
        <Image
          src="/map.png"
          alt="Mapa tatico"
          fill
          sizes="(max-width: 1600px) 100vw, 1400px"
          className="absolute inset-0 h-full w-full object-cover opacity-80"
        />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(173,255,47,0.10),transparent_36%),linear-gradient(180deg,rgba(5,5,8,0.15),rgba(5,5,8,0.82))]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[size:32px_32px] opacity-30" />

        {isChampSelect ? (
          <div className="absolute inset-4 z-10 grid items-start gap-3 lg:grid-cols-[380px_minmax(0,1fr)]">
            <motion.div
              layout
              transition={{ type: "spring", stiffness: 120, damping: 22 }}
              className="rounded-[20px] border border-[#ADFF2F]/20 bg-[#0A0A0C]/82 p-4 backdrop-blur-md"
            >
              <div className="mb-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
                <Sparkles className="h-4 w-4" />
                Janela do coach
              </div>
              <p className="text-[16px] font-semibold leading-7 tracking-[-0.05em] text-white">
                {focus.headline}
              </p>
              <p className="mt-2 line-clamp-2 text-[11px] leading-5 text-white/62">{focus.detail}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {focus.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/45"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </motion.div>

            <div className="grid gap-2 rounded-[20px] border border-white/[0.05] bg-[#0A0A0C]/72 p-3 backdrop-blur-sm lg:grid-cols-2">
              {liveStatus.map((item) => (
                <div
                  key={`hero-${item.label}`}
                  className="rounded-[14px] border border-white/[0.05] bg-white/[0.03] px-3 py-2"
                >
                  <div className="text-[8px] font-bold uppercase tracking-[0.16em] text-white/28">
                    {item.label}
                  </div>
                  <div className={`mt-1 text-[11px] font-semibold uppercase tracking-[0.08em] ${item.tone}`}>
                    {item.value}
                  </div>
                </div>
              ))}
            </div>

          </div>
        ) : (
          <>
            <motion.div
              layout
              transition={{ type: "spring", stiffness: 120, damping: 22 }}
              className="absolute left-6 top-6 z-10 max-w-[520px] rounded-[24px] border border-[#ADFF2F]/20 bg-[#0A0A0C]/82 p-6 backdrop-blur-md"
            >
              <div className="mb-3 flex items-center gap-2 text-[11px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
                <Sparkles className="h-4 w-4" />
                Janela do coach
              </div>
              <p className="text-[26px] font-semibold leading-10 tracking-[-0.05em] text-white">
                {focus.headline}
              </p>
              <p className="mt-4 text-[13px] leading-7 text-white/62">{focus.detail}</p>
              <div className="mt-5 flex flex-wrap gap-2">
                {focus.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.14em] text-white/45"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </motion.div>

            <AnimatePresence mode="wait">
              <motion.div
                key="live"
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 14 }}
                transition={{ duration: 0.25 }}
              className="absolute bottom-5 left-5 right-5 z-10"
            >
                <div className="grid gap-3 rounded-[22px] border border-white/[0.08] bg-[#0A0A0C]/78 p-4 backdrop-blur-sm xl:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
                  <div>
                    <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
                      <Radar className="h-3.5 w-3.5 text-[#38BDF8]" />
                      leituras ao vivo
                    </div>
                    <div className="grid gap-2 sm:grid-cols-2">
                      {recentReads.slice(0, 4).map((read, index) => (
                        <motion.div
                          key={`${read.label}-${index}`}
                          initial={{ opacity: 0, x: -8 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] px-3 py-3"
                        >
                          <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">
                            {read.label}
                          </div>
                          <div className="mt-1 text-[12px] leading-6 text-white/75">{read.value}</div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
                      <ShieldAlert className="h-3.5 w-3.5 text-amber-300" />
                      status da leitura
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      {liveStatus.map((item) => (
                        <motion.div
                          key={item.label}
                          initial={{ opacity: 0, scale: 0.98 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] px-3 py-3"
                        >
                          <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">
                            {item.label}
                          </div>
                          <div className={`mt-1 text-[12px] font-semibold uppercase tracking-[0.08em] ${item.tone}`}>
                            {item.value}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </>
        )}
      </div>
    </section>
  );
}

function resolveFocus({
  isChampSelect,
  summary,
  logs,
  jungleIntel,
  draftRecommendations,
}: {
  isChampSelect: boolean;
  summary: ReturnType<typeof useBridge>["summary"];
  logs: ReturnType<typeof useBridge>["logs"];
  jungleIntel: ReturnType<typeof useBridge>["jungleIntel"];
  draftRecommendations: ReturnType<typeof useBridge>["draftRecommendations"];
}) {
  if (isChampSelect && draftRecommendations?.locked_plan) {
    return {
      headline: draftRecommendations.locked_plan.lane_win_condition || draftRecommendations.locked_plan.plan,
      detail:
        draftRecommendations.locked_plan.lane_fail_condition ||
        draftRecommendations.locked_plan.reset_adjustment ||
        "Plano travado pelo draft. O coach prioriza execucao, setup e janela de lane.",
      tags: [
        draftRecommendations.role || "draft",
        draftRecommendations.locked_plan.locked_focus || "lock",
        draftRecommendations.locked_plan.enemy_anchor || "lane",
      ],
    };
  }

  if (logs.length > 0) {
    const priorityLog = [...logs].reverse().find((entry) => entry.type !== "system") || logs[logs.length - 1];
    return {
      headline: priorityLog.message,
      detail:
        jungleIntel?.notes?.[0]?.detail ||
        "Leitura principal derivada da ultima chamada do coach em tempo real.",
      tags: [
        priorityLog.type || "normal",
        jungleIntel?.probable_side || "mapa",
        jungleIntel?.enemy_jungler_champion || "sem jungler",
      ],
    };
  }

  if (summary) {
    return {
      headline: summary.focus || summary.insights.headline,
      detail: summary.insights.opening,
      tags: [summary.result || "summary", summary.confidence || "coach", summary.duration || "pos-jogo"],
    };
  }

  return {
    headline: "Leitura central aguardando telemetria suficiente do cliente.",
    detail: "Assim que o coach acumular sinais de draft, selva e live calls, este bloco vira o cockpit principal da partida.",
    tags: ["bridge", "telemetria", "coach"],
  };
}

function resolveReads({
  isChampSelect,
  summary,
  logs,
  jungleIntel,
  matchIntel,
  draftRecommendations,
}: {
  isChampSelect: boolean;
  summary: ReturnType<typeof useBridge>["summary"];
  logs: ReturnType<typeof useBridge>["logs"];
  jungleIntel: ReturnType<typeof useBridge>["jungleIntel"];
  matchIntel: ReturnType<typeof useBridge>["matchIntel"];
  draftRecommendations: ReturnType<typeof useBridge>["draftRecommendations"];
}) {
  if (isChampSelect && draftRecommendations) {
    const topPick = draftRecommendations.recommendations?.[0];
    return [
      {
        label: "melhor pick",
        value: topPick
          ? `${topPick.champion}: ${topPick.reasons?.[0] || topPick.lane_plan_summary || "sem detalhe adicional"}`
          : "Aguardando pick relevante",
      },
      {
        label: "melhor ban",
        value: draftRecommendations.best_ban
          ? `${draftRecommendations.best_ban.champion}: ${draftRecommendations.best_ban.reasons?.[0] || "corte prioritario"}`
          : "Sem ban consolidado ainda",
      },
      {
        label: "preview",
        value: draftRecommendations.enemy_preview?.length
          ? draftRecommendations.enemy_preview.join(", ")
          : "Composicao inimiga ainda abrindo",
      },
      {
        label: "role",
        value: draftRecommendations.role || "sem role definida",
      },
    ];
  }

  const recentLogs = [...logs].reverse().slice(0, 2);
  const jungleNote = jungleIntel?.notes?.[0];
  const summaryRead = summary?.reads?.[0];

  return [
    {
      label: "coach",
      value: recentLogs[0]?.message || summaryRead || "Sem call principal ainda.",
    },
    {
      label: "selva",
      value: jungleNote
        ? `${jungleNote.title}: ${jungleNote.detail}`
        : jungleIntel?.enemy_jungler_champion
          ? `${jungleIntel.enemy_jungler_champion} em ${jungleIntel.probable_side || "lado indefinido"}`
          : "Jungler inimigo ainda nao identificado",
    },
    {
      label: "time inimigo",
      value: matchIntel.length > 0
        ? `${matchIntel.length}/5 jogadores carregados`
        : "Roster inimigo ainda nao carregado",
    },
    {
      label: "ultimo sinal",
      value: recentLogs[1]?.message || "Aguardando nova chamada do coach.",
    },
  ];
}
