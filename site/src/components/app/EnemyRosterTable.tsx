"use client";

import { useMemo } from "react";
import { Swords } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

export default function EnemyRosterTable({ compact = false }: { compact?: boolean }) {
  const { matchIntel, gameState } = useBridge();

  const rows = useMemo(() => {
    return matchIntel
      .slice()
      .sort((a, b) => a.name.localeCompare(b.name))
      .slice(0, 5);
  }, [matchIntel]);

  return (
    <section className="rounded-[24px] border border-white/[0.05] bg-white/[0.02]">
      <div className="flex items-center gap-2 border-b border-white/[0.05] px-4 py-3 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
        <Swords className="h-4 w-4 text-rose-300" />
        Time inimigo
      </div>
      {rows.length > 0 ? (
        <div className="divide-y divide-white/[0.04]">
          {rows.map((player) => (
            <div key={player.name} className={`grid grid-cols-[minmax(0,1.3fr)_0.8fr_0.7fr] items-center gap-3 px-4 ${compact ? "py-2.5" : "py-3"}`}>
              <div className="min-w-0">
                <div className="truncate text-[12px] font-semibold text-white">{player.name}</div>
                <div className="truncate text-[10px] text-white/38">{player.champion || "sem campeao"}</div>
              </div>
              <div className="text-[11px] font-semibold text-white/72">{player.rank || "--"}</div>
              <div className="text-right text-[11px] font-semibold text-[#ADFF2F]">{player.winrate || "--"}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="px-4 py-5 text-[12px] leading-6 text-white/40">
          Roster inimigo ainda nao carregado. O coach preenche esta mesa quando o cliente ou o scraping entregarem os nomes.
          {gameState.phase ? ` Fase atual: ${gameState.phase}.` : ""}
        </div>
      )}
    </section>
  );
}

