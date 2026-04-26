"use client";

import { Brain, Radar, Sparkles, Target, Trophy } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import type { DashboardView } from "./dashboard-phase";

interface RightSidebarProps {
  activeView: DashboardView;
}

export default function RightSidebar({ activeView }: RightSidebarProps) {
  const { jungleIntel, summary, performance, draftRecommendations, logs, gameState } = useBridge();

  const recentMemories = summary?.memory?.slice(-2).reverse() ?? [];
  const latestCoachCall = [...logs].reverse().find((entry) => entry.type !== "system");
  const latestCallHeadline = latestCoachCall?.call?.headline || latestCoachCall?.message;
  const latestCallAction = latestCoachCall?.call?.action || latestCoachCall?.call?.next_step;
  const topMetric = performance?.metrics?.[0];
  const topFocus = performance?.focus_areas?.[0];

  const viewCards =
    activeView === "draft"
      ? [
          {
            title: "selva e scout",
            icon: Radar,
            tone: "lime" as const,
            pills: [
              { label: "jungler", value: jungleIntel?.enemy_jungler_champion || "aguardando" },
              { label: "lado", value: jungleIntel?.probable_side || "sem lado" },
              { label: "confianca", value: jungleIntel ? `${Math.round(jungleIntel.confidence * 100)}%` : "--" },
            ],
            lines: [
              jungleIntel?.notes?.[0]?.detail || "Leitura de jungle ainda curta para draft.",
              draftRecommendations?.enemy_preview?.length
                ? `Preview inimigo: ${draftRecommendations.enemy_preview.slice(0, 3).join(", ")}`
                : "Sem preview inimigo relevante ainda.",
            ],
          },
          {
            title: "estado do draft",
            icon: Sparkles,
            tone: "violet" as const,
            pills: [
              { label: "fase", value: draftRecommendations?.stage || "draft aberta" },
              { label: "role", value: draftRecommendations?.role || "sem role" },
              { label: "slots", value: `${draftRecommendations?.enemy_preview?.length || 0}/5` },
            ],
            lines: [
              latestCallHeadline || "A call principal sobe quando o draft consolidar pick ou ban.",
              draftRecommendations?.locked_plan?.locked_focus
                ? `Foco travado: ${draftRecommendations.locked_plan.locked_focus}`
                : "Sem plano travado ainda.",
            ],
          },
          {
            title: "memoria util",
            icon: Brain,
            tone: "blue" as const,
            pills: [
              { label: "entradas", value: String(recentMemories.length) },
              { label: "fase", value: gameState.phase || "draft" },
            ],
            lines:
              recentMemories.length > 0
                ? recentMemories.map((entry) => `${entry.title}: ${entry.note}`)
                : ["A memoria sobe aqui quando o coach registrar padrao relevante entre lobby, draft e partida."],
          },
        ]
      : activeView === "postgame"
        ? [
            {
              title: "resultado e foco",
              icon: Trophy,
              tone: "lime" as const,
              pills: [
                { label: "resultado", value: summary?.result || "--" },
                { label: "duracao", value: summary?.duration || "--:--" },
                { label: "confianca", value: summary?.confidence || "normal" },
              ],
              lines: [
                summary?.focus || "Sem foco consolidado ainda.",
                summary?.insights?.next_steps?.[0] || "A proxima partida ainda nao ganhou objetivo operacional.",
              ],
            },
            {
              title: "prioridades",
              icon: Target,
              tone: "rose" as const,
              pills: [
                { label: "erros", value: String(summary?.insights?.improvements?.length || 0) },
                { label: "acertos", value: String(summary?.insights?.strengths?.length || 0) },
              ],
              lines: [
                summary?.insights?.improvements?.[0] || "Sem erro principal consolidado.",
                summary?.insights?.strengths?.[0] || "Sem acerto principal consolidado.",
              ],
            },
            {
              title: "memoria",
              icon: Brain,
              tone: "violet" as const,
              pills: [{ label: "entradas", value: String(recentMemories.length) }],
              lines:
                recentMemories.length > 0
                  ? recentMemories.map((entry) => `${entry.title}: ${entry.note}`)
                  : ["A memoria aparece aqui quando o review consolidar sinais entre partidas."],
            },
          ]
        : activeView === "progress"
          ? [
              {
                title: "snapshot",
                icon: Trophy,
                tone: "lime" as const,
                pills: [
                  { label: "partidas", value: String(performance?.matches_played || 0) },
                  { label: "recorde", value: performance?.record || "--" },
                ],
                lines: [
                  performance?.headline || "Sem headline de progressao ainda.",
                  performance?.goal || "Sem meta carregada.",
                ],
              },
              {
                title: "metrica lider",
                icon: Sparkles,
                tone: "blue" as const,
                pills: [
                  { label: "metrica", value: topMetric?.label || "--" },
                  { label: "atual", value: topMetric ? topMetric.current.toFixed(2) : "--" },
                  { label: "alvo", value: topMetric ? topMetric.target.toFixed(2) : "--" },
                ],
                lines: [
                  topFocus || "Sem foco atual consolidado.",
                  performance?.strongest_areas?.[0] || "Sem area forte consolidada.",
                ],
              },
              {
                title: "memoria recente",
                icon: Brain,
                tone: "violet" as const,
                pills: [{ label: "entradas", value: String(recentMemories.length) }],
                lines:
                  recentMemories.length > 0
                    ? recentMemories.map((entry) => `${entry.title}: ${entry.note}`)
                    : ["A memoria recente sobe aqui quando houver historico suficiente."],
              },
            ]
          : [
              {
                title: "selva",
                icon: Radar,
                tone: "lime" as const,
                pills: [
                  { label: "jungler", value: jungleIntel?.enemy_jungler_champion || "sem leitura" },
                  { label: "ultimo", value: jungleIntel?.last_seen_clock || "--:--" },
                  { label: "confianca", value: jungleIntel ? `${Math.round(jungleIntel.confidence * 100)}%` : "--" },
                ],
                lines: [
                  jungleIntel?.notes?.[0]?.detail || "Sem trilha recente do jungler inimigo.",
                  jungleIntel?.probable_side || "Sem lado provavel consolidado.",
                ],
              },
              {
                title: "foco de jogo",
                icon: Target,
                tone: "blue" as const,
                pills: [
                  { label: "role", value: performance?.role || "sem role" },
                  { label: "meta", value: performance?.goal || "sem meta" },
                ],
                lines: [
                  topFocus || "Sem area de foco consolidada.",
                  latestCallAction || latestCallHeadline || "O coach sobe a call principal assim que detectar janela real.",
                ],
              },
              {
                title: "memoria",
                icon: Brain,
                tone: "violet" as const,
                pills: [{ label: "entradas", value: String(recentMemories.length) }],
                lines:
                  recentMemories.length > 0
                    ? recentMemories.map((entry) => `${entry.title}: ${entry.note}`)
                    : ["A memoria da sessao aparece quando o coach registrar sinais relevantes."],
              },
            ];

  return (
    <div className="flex flex-col gap-3">
      {viewCards.map((card) => (
        <aside
          key={card.title}
          className="overflow-hidden rounded-[24px] border border-white/[0.05] bg-[#050508] shadow-[0_0_40px_rgba(0,0,0,0.38)]"
        >
          <div className="flex items-center gap-2 border-b border-white/[0.04] px-4 py-3 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <card.icon className={`h-4 w-4 ${toneClass(card.tone)}`} />
            {card.title}
          </div>
          <div className="space-y-3 p-4">
            <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-1">
              {card.pills.map((pill) => (
                <MiniPanel key={`${card.title}-${pill.label}`} label={pill.label} value={pill.value} tone={card.tone} />
              ))}
            </div>
            <div className="space-y-2">
              {card.lines.slice(0, 2).map((line) => (
                <p key={line} className="line-clamp-3 text-[11px] leading-5 text-white/56">
                  {line}
                </p>
              ))}
            </div>
          </div>
        </aside>
      ))}
    </div>
  );
}

function MiniPanel({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "lime" | "violet" | "blue" | "rose";
}) {
  return (
    <div className="rounded-[16px] border border-white/[0.05] bg-white/[0.03] px-3 py-3">
      <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/26">{label}</div>
      <div className={`mt-1 text-[13px] font-semibold ${toneClass(tone)}`}>{value}</div>
    </div>
  );
}

function toneClass(tone: "lime" | "violet" | "blue" | "rose") {
  switch (tone) {
    case "lime":
      return "text-[#ADFF2F]";
    case "violet":
      return "text-violet-300";
    case "blue":
      return "text-[#38BDF8]";
    case "rose":
      return "text-rose-300";
    default:
      return "text-white";
  }
}
