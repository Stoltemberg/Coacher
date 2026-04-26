"use client";

import { BarChart3, Focus, Trophy } from "lucide-react";

import { useBridge } from "@/contexts/BridgeContext";

export default function ProgressionDashboard() {
  const { performance, summary } = useBridge();

  if (!performance) {
    return (
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] px-6 py-8 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="text-[12px] font-bold uppercase tracking-[0.18em] text-[#38BDF8]">Progressao</div>
        <div className="mt-4 text-[14px] leading-7 text-white/48">
          O painel de progressao sobe quando houver snapshot suficiente de desempenho e historico recente de partidas.
        </div>
      </section>
    );
  }

  return (
    <div className="space-y-4">
      <section className="rounded-[30px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_50px_rgba(0,0,0,0.45)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-[12px] font-bold uppercase tracking-[0.18em] text-[#38BDF8]">
            <BarChart3 className="h-4 w-4" />
            Progressao
          </div>
          <div className="rounded-full border border-white/8 bg-white/[0.03] px-3 py-1 text-[10px] font-mono uppercase tracking-[0.16em] text-white/35">
            {performance.matches_played} partidas
          </div>
        </div>

        <div className="grid gap-4 xl:grid-cols-4">
          <ProgressStat label="headline" value={performance.headline} detail={performance.role} />
          <ProgressStat label="record" value={performance.record} detail={`${Math.round(performance.win_rate)}% win rate`} />
          <ProgressStat label="goal" value={performance.goal} detail={performance.role} />
          <ProgressStat label="foco atual" value={performance.focus_areas[0] || "sem foco"} detail={performance.strongest_areas[0] || "sem ponto forte"} />
        </div>
      </section>

      <div className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <Trophy className="h-4 w-4 text-[#ADFF2F]" />
            metricas principais
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {performance.metrics.map((metric) => (
              <div key={metric.id} className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-4">
                <div className="text-[10px] font-bold uppercase tracking-[0.16em] text-white/30">{metric.label}</div>
                <div className="mt-2 flex items-end justify-between gap-3">
                  <div className="text-[24px] font-semibold tracking-[-0.05em] text-white">{metric.current.toFixed(2)}</div>
                  <div className="text-[10px] uppercase tracking-[0.14em] text-white/35">alvo {metric.target.toFixed(2)}</div>
                </div>
                <div className="mt-2 h-2 rounded-full bg-white/[0.05]">
                  <div
                    className={`h-full rounded-full ${metric.status === "ahead" ? "bg-[#2DE37C]" : metric.status === "close" ? "bg-[#38BDF8]" : "bg-amber-300"}`}
                    style={{ width: `${Math.min(100, Math.max(8, (metric.current / Math.max(metric.target, 0.01)) * 100))}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-[28px] border border-white/[0.05] bg-[#050508] p-4 shadow-[0_0_40px_rgba(0,0,0,0.38)]">
          <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/35">
            <Focus className="h-4 w-4 text-violet-300" />
            padroes e memoria
          </div>
          <div className="space-y-3">
            <Stack label="areas fortes" items={performance.strongest_areas} />
            <Stack label="areas de foco" items={performance.focus_areas} />
            <Stack
              label="padroes recentes"
              items={summary?.insights?.adaptive?.repeated_patterns?.slice(0, 3) || []}
              empty="Sem padrao repetido consolidado ainda."
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function ProgressStat({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[20px] border border-white/[0.05] bg-white/[0.03] p-4">
      <div className="text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{label}</div>
      <div className="mt-2 text-[18px] font-semibold tracking-[-0.04em] text-white">{value}</div>
      <div className="mt-1 text-[11px] text-white/42">{detail}</div>
    </div>
  );
}

function Stack({
  label,
  items,
  empty,
}: {
  label: string;
  items: string[];
  empty?: string;
}) {
  return (
    <div className="rounded-[18px] border border-white/[0.05] bg-white/[0.03] p-4">
      <div className="mb-3 text-[9px] font-bold uppercase tracking-[0.16em] text-white/28">{label}</div>
      {items.length > 0 ? (
        <div className="space-y-2">
          {items.slice(0, 3).map((item) => (
            <div key={item} className="text-[12px] leading-6 text-white/74">{item}</div>
          ))}
        </div>
      ) : (
        <div className="text-[12px] leading-6 text-white/40">{empty || "Sem itens consolidados."}</div>
      )}
    </div>
  );
}
