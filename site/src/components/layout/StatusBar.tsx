"use client";

import { Activity, Cpu, Shield, Wifi } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

export default function StatusBar() {
  const { gameState, isReady, settings } = useBridge();

  return (
    <div className="relative z-[100] flex shrink-0 items-center justify-between px-6 py-4">
      <div className="flex items-center gap-4">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.06] text-sm font-black text-white">
          C
        </div>
        <div className="space-y-1">
          <div className="text-[10px] font-black uppercase tracking-[0.28em] text-white">
            COACHER
          </div>
          <div className="text-[11px] text-white/45">
            Desktop coach for League of Legends
          </div>
        </div>
      </div>

      <div className="hidden items-center gap-3 lg:flex">
        <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/55">
          {gameState.phase || "Lobby"}
        </div>
        <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/55">
          {settings?.voice_personality === "minerva" ? "voz minerva" : "voz padrao"}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/55">
          <span className="inline-flex items-center gap-1.5">
            <Shield className={`h-3 w-3 ${settings?.hardcore_enabled ? "text-red-400" : "text-violet-400"}`} />
            {settings?.hardcore_enabled ? "hardcore" : "standard"}
          </span>
        </div>
        <div className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/55">
          <span className="inline-flex items-center gap-1.5">
            {isReady ? (
              <Activity className="h-3 w-3 text-toxic" />
            ) : (
              <Wifi className="h-3 w-3 text-amber-400" />
            )}
            {isReady ? "bridge online" : "bridge aguardando"}
          </span>
        </div>
        <div className="hidden rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[10px] font-mono uppercase tracking-[0.18em] text-white/55 md:block">
          <span className="inline-flex items-center gap-1.5">
            <Cpu className="h-3 w-3 text-white/45" />
            desktop v4.2.0
          </span>
        </div>
      </div>
    </div>
  );
}
