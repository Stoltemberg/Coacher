"use client";

import { Activity, Cpu, Crosshair, Settings2, Sparkles } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";
import type { DashboardView } from "./dashboard-phase";
import { phaseCopy } from "./dashboard-phase";

interface TopNavbarProps {
  activeView: DashboardView;
}

const viewMeta: Record<DashboardView, { label: string; blurb: string; icon: typeof Activity }> = {
  live: { label: "Ao Vivo", blurb: "comando de partida", icon: Activity },
  draft: { label: "Draft", blurb: "pick, ban e plano", icon: Crosshair },
  postgame: { label: "Pos-jogo", blurb: "review da ultima partida", icon: Sparkles },
  progress: { label: "Progressao", blurb: "metricas e padroes", icon: Cpu },
  settings: { label: "Configuracoes", blurb: "voz, role e filtros", icon: Settings2 },
};

export default function TopNavbar({ activeView }: TopNavbarProps) {
  const { gameState, isReady, jungleIntel, draftRecommendations, auth } = useBridge();
  const meta = viewMeta[activeView];
  const Icon = meta.icon;
  const confidence = jungleIntel ? Math.round(jungleIntel.confidence * 100) : null;
  const identity = auth?.user?.display_name || auth?.user?.email?.split("@")[0] || "coach";

  return (
    <div className="flex h-[72px] items-center justify-between border-b border-white/[0.04] px-6">
      <div className="flex items-center gap-4">
        <div className="text-[15px] font-black uppercase tracking-[0.18em] text-white">
          COACHER<span className="text-[#8B5CF6]">.</span>
        </div>
        <div className="hidden items-center gap-2 rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.16em] text-white/45 lg:flex">
          <span className={`h-2 w-2 rounded-full ${isReady ? "bg-[#2DE37C]" : "bg-amber-400"}`} />
          bridge {isReady ? "online" : "pendente"}
        </div>
        <div className="hidden rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35 xl:block">
          {identity}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/8 bg-white/[0.03] text-white/65">
          <Icon className="h-4 w-4" />
        </div>
        <div className="flex flex-col items-center">
          <span className="text-[12px] font-black uppercase tracking-[0.22em] text-white">
            {meta.label}
          </span>
          <span className="mt-1 text-[10px] font-mono uppercase tracking-[0.18em] text-white/35">
            {meta.blurb}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3">
        <div className="hidden rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.16em] text-white/45 xl:block">
          {phaseCopy(gameState.phase)}
        </div>
        {draftRecommendations?.stage ? (
          <div className="hidden rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.16em] text-white/45 xl:block">
            {draftRecommendations.stage}
          </div>
        ) : null}
        {confidence !== null ? (
          <div className="hidden rounded-full border border-white/8 bg-white/[0.03] px-3 py-1.5 text-[10px] font-mono uppercase tracking-[0.16em] text-white/45 xl:block">
            selva {confidence}%
          </div>
        ) : null}
      </div>
    </div>
  );
}
