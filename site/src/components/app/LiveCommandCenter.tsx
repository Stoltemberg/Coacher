"use client";

import { Activity, Eye, Radar, Sparkles } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import CoachCallCard from "./CoachCallCard";
import StatusRail from "./StatusRail";
import EnemyRosterTable from "./EnemyRosterTable";
import JungleIntelPanel from "./JungleIntelPanel";
import { phaseCopy } from "./dashboard-phase";

export default function LiveCommandCenter() {
  const { gameState, logs, jungleIntel, performance, summary } = useBridge();

  const latestCall = [...logs].reverse().find((entry) => entry.type !== "system");
  const focusAreas = performance?.focus_areas?.slice(0, 2) || [];
  const strongAreas = performance?.strongest_areas?.slice(0, 2) || [];
  const timeline = summary?.timeline?.slice(-4).reverse() || [];

  const supportReadA =
    jungleIntel?.notes?.[0]?.detail ||
    focusAreas[0] ||
    "Sem leitura secundaria consolidada ainda.";
  const supportReadB =
    summary?.insights?.opening ||
    strongAreas[0] ||
    "O coach sobe sinais mais curtos aqui conforme a telemetria ganhar contexto.";

  const heroTitle =
    latestCall?.message ||
    summary?.focus ||
    "A leitura ao vivo entra aqui quando o coach detectar janela real de luta, reset, mapa ou objetivo.";

  const heroDetail =
    jungleIntel?.notes?.[0]?.detail ||
    summary?.insights?.opening ||
    "O command center prioriza a call principal do momento e rebaixa sinais secundarios para a rail de status.";

  return (
    <div className="space-y-4">
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
            <Eye className="h-4 w-4" />
            Ao vivo
          </div>
          <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
            {phaseCopy(gameState.phase)}
          </div>
        </div>

        <div className="grid gap-3 xl:grid-cols-[1.2fr_0.8fr]">
          <CoachCallCard
            eyebrow="janela do coach"
            title={heroTitle}
            detail={heroDetail}
            call={latestCall?.call}
            compact
            tags={[
              phaseCopy(gameState.phase),
              jungleIntel?.enemy_jungler_champion || "selva sem leitura",
              performance?.role || "role indefinida",
            ]}
          />
          <div className="rounded-[24px] border border-white/[0.05] bg-[linear-gradient(180deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01))] p-4">
            <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
              <Sparkles className="h-4 w-4 text-[#38BDF8]" />
              apoio imediato
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              <SignalTile
                label="selva"
                value={jungleIntel?.enemy_jungler_champion || "sem leitura"}
                detail={jungleIntel?.probable_side || "sem lado provavel"}
                tone="focus"
              />
              <SignalTile
                label="foco"
                value={focusAreas[0] || "sem foco"}
                detail={strongAreas[0] || "sem area forte"}
                tone="live"
              />
              <SignalTile
                label="pressao"
                value={summary?.confidence || "normal"}
                detail={summary?.result || latestCall?.type || "aguardando"}
                tone="neutral"
              />
            </div>
            <div className="mt-3 grid gap-2">
              <SupportLine label="leitura" text={supportReadA} />
              <SupportLine label="próximo passo" text={supportReadB} />
            </div>
          </div>
        </div>

        <div className="mt-3">
          <StatusRail
            items={[
              {
                label: "objetivo",
                value: jungleIntel?.notes?.[0]?.title || "sem objetivo prioritario",
                detail: jungleIntel?.notes?.[0]?.clock || "janela ainda abrindo",
                tone: "focus",
              },
              {
                label: "ultimo avistamento",
                value: jungleIntel?.last_seen_clock || "--:--",
                detail: jungleIntel?.last_seen_source || "sem avistamento ainda",
                tone: "live",
              },
              {
                label: "foco",
                value: performance?.role || "sem role",
                detail: performance?.goal || "sem meta carregada",
                tone: "neutral",
              },
            ]}
          />
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <Activity className="h-4 w-4 text-violet-300" />
            timeline curta
          </div>
          {timeline.length > 0 ? (
            <div className="space-y-3">
              {timeline.map((entry) => (
                <div
                  key={`${entry.clock}-${entry.text}`}
                  className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] px-4 py-3"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="text-[11px] font-bold uppercase tracking-[0.14em] text-white/55">
                      {entry.category}
                    </div>
                    <div className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/35">
                      {entry.clock}
                    </div>
                  </div>
                  <div className="mt-2 text-[12px] leading-6 text-white/78">{entry.text}</div>
                  <div className="mt-1 text-[10px] uppercase tracking-[0.14em] text-white/35">{entry.impact}</div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState text="A timeline curta entra quando houver sinais de partida ou um pos-jogo recente consolidado." />
          )}
        </section>

        <div className="grid gap-4">
          <EnemyRosterTable compact />
          <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
            <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
              <Radar className="h-4 w-4 text-[#ADFF2F]" />
              leitura da selva
            </div>
            <JungleIntelPanel />
          </section>
        </div>
      </div>
    </div>
  );
}

function SignalTile({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: string;
  detail: string;
  tone: "neutral" | "live" | "focus" | "warning";
}) {
  return (
    <div className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] px-4 py-3">
      <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{label}</div>
      <div className={`mt-2 text-[14px] font-semibold ${tone === "focus" ? "text-[#ADFF2F]" : tone === "live" ? "text-[#38BDF8]" : tone === "warning" ? "text-amber-200" : "text-white"}`}>
        {value}
      </div>
      <div className="mt-1 text-[10px] leading-5 text-white/42">{detail}</div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-[18px] border border-dashed border-white/10 px-4 py-5 text-[12px] leading-6 text-white/40">
      {text}
    </div>
  );
}

function SupportLine({ label, text }: { label: string; text: string }) {
  return (
    <div className="rounded-[14px] border border-white/[0.04] bg-black/20 px-3 py-2">
      <div className="text-[9px] font-bold uppercase tracking-[0.14em] text-white/26">{label}</div>
      <div className="mt-1 line-clamp-2 text-[11px] leading-5 text-white/58">{text}</div>
    </div>
  );
}
