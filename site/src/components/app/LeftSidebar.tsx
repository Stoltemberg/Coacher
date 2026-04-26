"use client";

import type React from "react";
import { Activity, BarChart3, Crosshair, Settings, ShieldAlert, Sparkles, Trophy } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

interface LeftSidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const roleLabel = (value?: string | null) => {
  if (!value) return "sem role";
  const normalized = value.toLowerCase();
  if (normalized === "bottom") return "adc";
  if (normalized === "middle") return "mid";
  return normalized;
};

const navItems = [
  { id: "live", label: "Ao Vivo", icon: Activity },
  { id: "draft", label: "Draft", icon: Crosshair },
  { id: "postgame", label: "Pos-jogo", icon: Sparkles },
  { id: "progress", label: "Progressao", icon: BarChart3 },
  { id: "settings", label: "Configuracoes", icon: Settings },
];

export default function LeftSidebar({ activeTab, setActiveTab }: LeftSidebarProps) {
  const { auth, settings, performance, summary, logs, isReady } = useBridge();

  const profileName = auth?.user?.display_name || auth?.user?.email?.split("@")[0] || "player";
  const role = roleLabel(settings?.primary_role || performance?.role);
  const focus = performance?.focus_areas?.[0] || summary?.insights?.improvements?.[0] || "sem foco consolidado";
  const coachSignal = [...logs].reverse().find((entry) => entry.type !== "system")?.message || "Sem sinais recentes";

  return (
    <aside className="flex h-full w-[250px] flex-col overflow-hidden rounded-[28px] border border-white/[0.04] bg-[#050508] shadow-[0_0_50px_rgba(0,0,0,0.45)]">
      <div className="custom-scrollbar flex-1 space-y-5 overflow-y-auto p-5">
        <section className="rounded-[22px] border border-white/[0.05] bg-white/[0.03] p-4">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[#8B5CF6]/40 bg-[#8B5CF6]/10 text-lg font-black uppercase text-white">
              {profileName.slice(0, 1)}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-[20px] font-semibold tracking-[-0.04em] text-white">
                {profileName.toLowerCase()}
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="rounded-full border border-[#ADFF2F]/30 bg-[#ADFF2F]/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.16em] text-[#ADFF2F]">
                  {role}
                </span>
                <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-mono uppercase tracking-[0.14em] text-white/45">
                  {isReady ? "bridge online" : "bridge pendente"}
                </span>
              </div>
            </div>
          </div>
          <div className="mt-4 text-[10px] font-mono uppercase tracking-[0.14em] text-white/35">coach state</div>
          <div className="mt-2 h-2 rounded-full bg-white/[0.05]">
            <div
              className={`h-full rounded-full ${isReady ? "bg-[#2DE37C]" : "bg-amber-400"}`}
              style={{ width: isReady ? "100%" : "48%" }}
            />
          </div>
        </section>

        <section className="rounded-[22px] border border-white/[0.05] bg-white/[0.03] p-4">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <Trophy className="h-3.5 w-3.5 text-[#ADFF2F]" />
            snapshot
          </div>
          <div className="grid grid-cols-2 gap-3">
            <MiniStat label="partidas" value={`${performance?.matches_played || 0}`} />
            <MiniStat label="recorde" value={performance?.record || "--"} />
            <MiniStat label="win rate" value={performance ? `${Math.round(performance.win_rate)}%` : "--"} />
            <MiniStat label="goal" value={performance?.goal || settings?.player_goal || "--"} />
          </div>
          <div className="mt-3 rounded-[18px] border border-white/[0.04] bg-[#0A0A0C] p-3.5">
            <div className="text-[9px] font-bold uppercase tracking-[0.18em] text-white/28">foco</div>
            <div className="mt-2 line-clamp-4 text-[13px] font-semibold leading-6 text-white/88">{focus}</div>
          </div>
        </section>

        <section className="space-y-2">
          {navItems.map((item) => (
            <NavButton
              key={item.id}
              active={activeTab === item.id}
              icon={<item.icon className="h-4 w-4" />}
              label={item.label}
              onClick={() => setActiveTab(item.id)}
            />
          ))}
        </section>

        <section className="rounded-[22px] border border-white/[0.05] bg-white/[0.03] p-4">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <ShieldAlert className="h-3.5 w-3.5 text-rose-300" />
            prioridade atual
          </div>
          <div className="line-clamp-6 text-[12px] leading-6 text-white/62">{coachSignal}</div>
        </section>
      </div>
    </aside>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[16px] border border-white/[0.04] bg-[#0A0A0C] p-3">
      <div className="text-[14px] font-bold text-white">{value}</div>
      <div className="mt-1 text-[9px] font-bold uppercase tracking-[0.18em] text-white/28">{label}</div>
    </div>
  );
}

function NavButton({
  active,
  icon,
  label,
  onClick,
}: {
  active: boolean;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-[16px] border px-4 py-3 text-left transition-colors ${
        active
          ? "border-[#ADFF2F]/25 bg-[#ADFF2F]/10 text-[#ADFF2F]"
          : "border-white/[0.04] bg-white/[0.02] text-white/45 hover:border-white/10 hover:text-white/80"
      }`}
    >
      {icon}
      <span className="text-[11px] font-bold uppercase tracking-[0.16em]">{label}</span>
    </button>
  );
}
