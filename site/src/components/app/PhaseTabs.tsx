"use client";

import { Activity, BarChart3, Crosshair, Settings, Sparkles } from "lucide-react";

import type { DashboardView } from "./dashboard-phase";

const tabs: Array<{
  id: DashboardView;
  label: string;
  icon: typeof Activity;
  blurb: string;
}> = [
  { id: "live", label: "Ao Vivo", icon: Activity, blurb: "call atual e leitura de mapa" },
  { id: "draft", label: "Draft", icon: Crosshair, blurb: "pick, ban e plano travado" },
  { id: "postgame", label: "Pos-jogo", icon: Sparkles, blurb: "erros, acertos e review" },
  { id: "progress", label: "Progressao", icon: BarChart3, blurb: "metricas e padroes" },
  { id: "settings", label: "Configuracoes", icon: Settings, blurb: "voz, role e filtros" },
];

export default function PhaseTabs({
  activeView,
  onChange,
}: {
  activeView: DashboardView;
  onChange: (view: DashboardView) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-white/[0.05] px-5 py-4">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const active = tab.id === activeView;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`group flex min-w-[165px] flex-1 items-start gap-3 rounded-[18px] border px-4 py-3 text-left transition-all lg:min-w-[180px] ${
              active
                ? "border-[#ADFF2F]/25 bg-[#ADFF2F]/10 shadow-[0_0_30px_rgba(173,255,47,0.08)]"
                : "border-white/[0.05] bg-white/[0.02] hover:border-white/12 hover:bg-white/[0.04]"
            }`}
          >
            <div
              className={`mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl border ${
                active ? "border-[#ADFF2F]/25 bg-[#ADFF2F]/12 text-[#ADFF2F]" : "border-white/8 bg-white/[0.04] text-white/45"
              }`}
            >
              <Icon className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <div className={`text-[11px] font-bold uppercase tracking-[0.16em] ${active ? "text-white" : "text-white/62"}`}>
                {tab.label}
              </div>
              <div className="mt-1 text-[10px] leading-5 text-white/38">{tab.blurb}</div>
            </div>
          </button>
        );
      })}
    </div>
  );
}

