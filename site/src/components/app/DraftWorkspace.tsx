"use client";

import { Brain, Crosshair, ShieldBan, Swords } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import CoachCallCard from "./CoachCallCard";
import StatusRail from "./StatusRail";
import EnemyRosterTable from "./EnemyRosterTable";
import { phaseCopy } from "./dashboard-phase";

export default function DraftWorkspace() {
  const { draftRecommendations, jungleIntel, matchIntel, gameState } = useBridge();

  const topPick = draftRecommendations?.recommendations?.[0];
  const bestBan = draftRecommendations?.best_ban;
  const lockedPlan = draftRecommendations?.locked_plan;
  const stage = draftRecommendations?.stage || "pick";

  const heroTitle = lockedPlan
    ? `${lockedPlan.champion}: ${lockedPlan.plan}`
    : topPick
      ? `${topPick.champion}: ${topPick.lane_plan_summary || topPick.reasons?.[0] || "melhor call atual"}`
      : bestBan
        ? `Ban atual: ${bestBan.champion} para cortar ${bestBan.reasons?.[0] || "a resposta mais perigosa"}`
        : "O coach ainda esta consolidando a call principal do draft.";

  const heroDetail = lockedPlan
    ? lockedPlan.lane_fail_condition || lockedPlan.first_reset_focus || lockedPlan.first_item_plan
    : topPick?.lane_win_condition || topPick?.lane_fail_condition || topPick?.build_focus?.[0] || "Assim que picks e roles ficarem claros, o painel sobe a leitura principal.";

  const supportA =
    topPick?.reasons?.[0] ||
    bestBan?.reasons?.[0] ||
    jungleIntel?.notes?.[0]?.detail ||
    "Sem leitura secundaria forte ainda.";
  const supportB =
    lockedPlan?.lane_win_condition ||
    topPick?.lane_fail_condition ||
    topPick?.build_focus?.[0] ||
    "A call principal sobe quando o draft consolidar pick, ban ou plano travado.";

  return (
    <div className="space-y-4">
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.18em] text-violet-300">
            <Crosshair className="h-4 w-4" />
            Draft
          </div>
          <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
            {phaseCopy(gameState.phase)}
          </div>
        </div>

        <div className="grid gap-3 xl:grid-cols-[1.15fr_0.85fr]">
          <CoachCallCard
            eyebrow={lockedPlan ? "plano travado" : topPick ? "melhor escolha agora" : "janela do coach"}
            title={heroTitle}
            detail={heroDetail}
            compact
            tags={[
              draftRecommendations?.role || "role indefinida",
              topPick?.focus || bestBan?.focus || lockedPlan?.locked_focus || stage,
              topPick?.window || bestBan?.window || jungleIntel?.probable_side || "draft",
            ]}
          />
          <div className="grid gap-3">
            <StatusRail
              items={[
                {
                  label: "fase",
                  value: draftRecommendations?.stage || "draft aberta",
                  detail: phaseCopy(gameState.phase),
                  tone: "live",
                },
                {
                  label: "campeao",
                  value: gameState.championName || lockedPlan?.champion || "nao detectado",
                  detail: draftRecommendations?.role || "sem role",
                  tone: "neutral",
                },
                {
                  label: "inimigos",
                  value: `${matchIntel.length}/5 carregados`,
                  detail: draftRecommendations?.enemy_preview?.join(", ") || "preview vazio",
                  tone: "focus",
                },
              ]}
            />
            <CompactSupport title="janela e risco" lines={[supportA, supportB]} />
          </div>
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[220px_minmax(0,1fr)_260px]">
        <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-rose-300">
            <ShieldBan className="h-4 w-4" />
            melhor ban
          </div>
          {bestBan ? (
            <div className="space-y-3">
              <ValueChip label={bestBan.champion} sublabel={bestBan.focus || "prioritario"} tone="rose" />
              <div className="space-y-2">
                {bestBan.reasons?.slice(0, 3).map((reason) => (
                  <div key={reason} className="line-clamp-3 text-[11px] leading-5 text-white/65">
                    {reason}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <DraftEmpty text="Aguardando leitura de ban." />
          )}
        </section>

        <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-violet-300">
            <Brain className="h-4 w-4" />
            leituras de apoio
          </div>
          {topPick || lockedPlan ? (
            <div className="grid gap-3 lg:grid-cols-2">
              <InfoCluster
                title="motivos"
                items={
                  lockedPlan
                    ? [lockedPlan.danger, lockedPlan.synergy_summary, lockedPlan.first_reset_focus].filter(Boolean)
                    : topPick?.reasons?.slice(0, 2) || []
                }
              />
              <InfoCluster
                title="execucao"
                items={
                  lockedPlan
                    ? [lockedPlan.map_plan_summary, lockedPlan.fight_plan_summary].filter(Boolean)
                    : [topPick?.lane_plan_summary, topPick?.lane_win_condition].filter(Boolean) as string[]
                }
              />
            </div>
          ) : (
            <DraftEmpty text="Aguardando pick relevante para montar a call principal." />
          )}
        </section>

        <div className="grid gap-4">
          <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
            <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
              <Swords className="h-4 w-4" />
              preview inimigo
            </div>
            <div className="flex flex-wrap gap-2">
              {(draftRecommendations?.enemy_preview || []).length > 0 ? (
                draftRecommendations?.enemy_preview?.map((enemy) => (
                  <span
                    key={enemy}
                    className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.14em] text-white/55"
                  >
                    {enemy}
                  </span>
                ))
              ) : (
                <DraftEmpty text="Nenhum campeao revelado ainda." />
              )}
            </div>
          </section>
          {matchIntel.length > 0 ? <EnemyRosterTable compact /> : null}
        </div>
      </div>
    </div>
  );
}

function InfoCluster({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-[20px] border border-white/[0.05] bg-white/[0.03] p-4">
      <div className="mb-3 text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{title}</div>
      {items.length > 0 ? (
        <div className="space-y-2">
          {items.slice(0, 3).map((item) => (
            <div key={item} className="line-clamp-3 text-[11px] leading-5 text-white/72">
              {item}
            </div>
          ))}
        </div>
      ) : (
        <DraftEmpty text="Sem leitura consolidada ainda." />
      )}
    </div>
  );
}

function ValueChip({
  label,
  sublabel,
  tone,
}: {
  label: string;
  sublabel: string;
  tone: "rose" | "lime";
}) {
  return (
    <div className={`rounded-[18px] border px-3 py-3 ${tone === "rose" ? "border-rose-400/20 bg-rose-400/8" : "border-[#ADFF2F]/20 bg-[#ADFF2F]/8"}`}>
      <div className="text-[18px] font-semibold tracking-[-0.04em] text-white">{label}</div>
      <div className="mt-1 text-[10px] uppercase tracking-[0.16em] text-white/42">{sublabel}</div>
    </div>
  );
}

function DraftEmpty({ text }: { text: string }) {
  return <div className="text-[11px] leading-5 text-white/42">{text}</div>;
}

function CompactSupport({ title, lines }: { title: string; lines: string[] }) {
  return (
    <div className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-4">
      <div className="mb-3 text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{title}</div>
      <div className="space-y-2">
        {lines.slice(0, 2).map((line) => (
          <div key={line} className="line-clamp-2 text-[11px] leading-5 text-white/62">
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}
