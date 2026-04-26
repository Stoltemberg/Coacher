"use client";

import { useBridge } from "@/contexts/BridgeContext";
import type { DraftRecommendationsSnapshot } from "@/types/bridge";
import { motion } from "framer-motion";
import { ShieldCheck, Sparkles, Swords } from "lucide-react";

const normalizeChampionName = (value: string) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9\s'-]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

interface MatchIntelPanelProps {
  tacticalMode?: boolean;
}

export default function MatchIntelPanel({ tacticalMode = false }: MatchIntelPanelProps) {
  const { draftRecommendations, matchIntel, settings } = useBridge();
  const hasRecommendations = Boolean(draftRecommendations?.recommendations?.length);
  const preferredPool = settings?.preferred_champion_pool ?? [];
  const preferredPoolSet = new Set(preferredPool.map(normalizeChampionName));
  const recommendedPicks = [...(draftRecommendations?.recommendations ?? [])].sort((left, right) => {
    if (!(settings?.prioritize_pool_picks && preferredPoolSet.size > 0)) {
      return right.score - left.score;
    }

    const leftPreferred = preferredPoolSet.has(normalizeChampionName(left.champion));
    const rightPreferred = preferredPoolSet.has(normalizeChampionName(right.champion));

    if (leftPreferred !== rightPreferred) {
      return leftPreferred ? -1 : 1;
    }

    return right.score - left.score;
  });
  const visiblePicks = tacticalMode ? recommendedPicks.slice(0, 4) : recommendedPicks.slice(0, 3);
  const bestBan = draftRecommendations?.best_ban;
  const lockedPlan = draftRecommendations?.locked_plan;
  const lockedFocus = lockedPlan?.locked_focus;
  const isBanStage = draftRecommendations?.stage === "ban";
  const isPickStage = draftRecommendations?.stage === "pick";
  const isLockedStage = draftRecommendations?.stage === "locked";
  const familiarityLabel = (value?: string) => {
    if (value === "main") return "teu main";
    if (value === "pool") return "tua pool";
    return "fora da pool";
  };
  const banFocusLabel = (value?: string) => {
    if (value === "anti-lane") return "anti-lane";
    if (value === "anti-pool") return "anti-pool";
    if (value === "anti-role") return "anti-role";
    return "anti-comp";
  };
  const pickFocusLabel = (value?: string) => {
    if (value === "comfort-pick") return "comfort pick";
    if (value === "anti-lane") return "anti-lane";
    return "anti-comp";
  };
  const pickFocusDescription = (value?: string) => {
    if (value === "comfort-pick") return "resposta boa sem sair do teu conforto";
    if (value === "anti-lane") return "prioriza vencer rota e matchup";
    return "prioriza responder a composicao inimiga";
  };
  const pickContextLabel = (value?: string) => {
    if (value === "lane-revealed") return "rota revelada";
    if (value === "duo-forming") return "dupla inimiga";
    if (value === "role-revealed") return "role revelada";
    return "leitura de comp";
  };
  const pickWindowLabel = (value?: string) => {
    if (value === "blind-slot") return "slot blind";
    if (value === "answer-slot") return "slot resposta";
    if (value === "contest-slot") return "slot contest";
    if (value === "adc-revealed") return "adc revelado";
    if (value === "support-revealed") return "suporte revelado";
    if (value === "duo-answered") return "dupla fechando";
    if (value === "lane-semi") return "semi-respondida";
    if (value === "lane-answered") return "respondida";
    if (value === "map-blind") return "mapa cego";
    if (value === "map-semi") return "mapa semi";
    if (value === "map-answered") return "mapa respondido";
    if (value === "blue-open") return "azul cedo";
    if (value === "red-answer") return "vermelho tarde";
    if (value === "info-exposed") return "lado exposto";
    if (value === "info-answering") return "lado respondendo";
    if (value === "comfort-window") return "conforto pesa";
    if (value === "response-open") return "ainda podem responder";
    if (value === "draft-open") return "draft aberta";
    if (value === "lane-partial") return "lane parcial";
    if (value === "lane-complete") return "lane fechada";
    if (value === "lane-shaped") return "lane desenhada";
    return "draft mais fechada";
  };
  const showPickWindow = (pick: DraftRecommendationsSnapshot["recommendations"][number]) => {
    const text = (pick.reasons || []).join(" ").toLowerCase();
    if (pick.window === "blind-slot") {
      return !text.includes("blind") && !text.includes("cego");
    }
    if (pick.window === "answer-slot") {
      return !text.includes("responde") && !text.includes("counter");
    }
    if (pick.window === "contest-slot") {
      return !text.includes("contest") && !text.includes("consistencia");
    }
    if (pick.window === "adc-revealed") {
      return !text.includes("adc") && !text.includes("suporte");
    }
    if (pick.window === "support-revealed") {
      return !text.includes("suporte") && !text.includes("lane no papel");
    }
    if (pick.window === "duo-answered") {
      return !text.includes("dupla") && !text.includes("bot lane") && !text.includes("desenhada");
    }
    if (pick.window === "lane-semi") {
      return !text.includes("comecou a responder") && !text.includes("estabilidade");
    }
    if (pick.window === "lane-answered") {
      return !text.includes("bem respondida") && !text.includes("matchup") && !text.includes("cirurgico");
    }
    if (pick.window === "map-blind") {
      return !text.includes("mapa") && !text.includes("cego");
    }
    if (pick.window === "map-semi") {
      return !text.includes("mapa") && !text.includes("desenhar") && !text.includes("consistencia");
    }
    if (pick.window === "map-answered") {
      return !text.includes("mapa") && !text.includes("jungle") && !text.includes("respondido");
    }
    if (pick.window === "blue-open") {
      return !text.includes("lado azul") && !text.includes("estavel") && !text.includes("blind");
    }
    if (pick.window === "red-answer") {
      return !text.includes("lado vermelho") && !text.includes("cirurgico") && !text.includes("responder");
    }
    if (pick.window === "info-exposed") {
      return !text.includes("mostrou mais") && !text.includes("conforto");
    }
    if (pick.window === "info-answering") {
      return !text.includes("respondendo") && !text.includes("mais informacao") && !text.includes("cirurgico");
    }
    if (pick.window === "comfort-window") {
      return !(pick.familiarity === "main" || pick.familiarity === "pool") || !text.includes("conforto");
    }
    if (pick.window === "response-open") {
      return !text.includes("resposta") && !text.includes("cuidado");
    }
    if (pick.window === "lane-partial") {
      return !text.includes("metade da lane") && !text.includes("nao mostrou tudo");
    }
    if (pick.window === "lane-complete") {
      return !text.includes("lane inimiga") && !text.includes("praticamente fechada");
    }
    if (pick.window === "lane-shaped") {
      return !text.includes("counter") && !text.includes("matchup");
    }
    return false;
  };
  const banFocusDescription = (value?: string) => {
    if (value === "anti-lane") return "protege mais a tua lane e o teu pick";
    if (value === "anti-pool") return "corta picks que atrapalham teu conforto";
    if (value === "anti-role") return "limpa uma ameaca geral da role nessa fase";
    return "quebra mais a estrutura da comp inimiga";
  };
  const banContextLabel = (value?: string) => {
    if (value === "duo-forming") return "quebra dupla";
    if (value === "role-revealed") return "pick revelado";
    return "leitura de comp";
  };
  const banWindowLabel = (value?: string) => {
    if (value === "blind-slot") return "slot blind";
    if (value === "answer-slot") return "slot resposta";
    if (value === "contest-slot") return "slot contest";
    if (value === "adc-revealed") return "adc revelado";
    if (value === "support-revealed") return "suporte revelado";
    if (value === "duo-answered") return "dupla fechando";
    if (value === "lane-semi") return "semi-respondida";
    if (value === "lane-answered") return "respondida";
    if (value === "map-blind") return "mapa cego";
    if (value === "map-semi") return "mapa semi";
    if (value === "map-answered") return "mapa respondido";
    if (value === "blue-open") return "azul cedo";
    if (value === "red-answer") return "vermelho tarde";
    if (value === "info-exposed") return "lado exposto";
    if (value === "info-answering") return "lado respondendo";
    if (value === "protect-pick") return "protege teu pick";
    if (value === "lane-protect") return "protege tua lane";
    if (value === "draft-open") return "draft aberta";
    if (value === "lane-partial") return "lane parcial";
    if (value === "lane-complete") return "lane fechada";
    if (value === "map-open") return "mapa aberto";
    if (value === "map-shaped") return "mapa desenhado";
    return "draft mais fechada";
  };
  const showBanWindow = (ban?: DraftRecommendationsSnapshot["best_ban"]) => {
    const text = (ban?.reasons || []).join(" ").toLowerCase();
    if (!ban?.window) return false;
    if (ban.window === "blind-slot") {
      return !text.includes("blind") && !text.includes("cego");
    }
    if (ban.window === "answer-slot") {
      return !text.includes("cirurgico") && !text.includes("responde");
    }
    if (ban.window === "contest-slot") {
      return !text.includes("contest") && !text.includes("estabilizar");
    }
    if (ban.window === "adc-revealed") {
      return !text.includes("adc") && !text.includes("suporte");
    }
    if (ban.window === "support-revealed") {
      return !text.includes("suporte") && !text.includes("oculta");
    }
    if (ban.window === "duo-answered") {
      return !text.includes("dupla") && !text.includes("precis") && !text.includes("desenhada");
    }
    if (ban.window === "lane-semi") {
      return !text.includes("comecou a responder") && !text.includes("segurar");
    }
    if (ban.window === "lane-answered") {
      return !text.includes("bem respondida") && !text.includes("precis") && !text.includes("cirurgico");
    }
    if (ban.window === "map-blind") {
      return !text.includes("mapa") && !text.includes("cego");
    }
    if (ban.window === "map-semi") {
      return !text.includes("mapa") && !text.includes("semi") && !text.includes("ritmo");
    }
    if (ban.window === "map-answered") {
      return !text.includes("mapa") && !text.includes("precis") && !text.includes("respondido");
    }
    if (ban.window === "blue-open") {
      return !text.includes("lado azul") && !text.includes("seguro") && !text.includes("blind");
    }
    if (ban.window === "red-answer") {
      return !text.includes("lado vermelho") && !text.includes("cirurgico") && !text.includes("responde");
    }
    if (ban.window === "info-exposed") {
      return !text.includes("mostrou mais") && !text.includes("protege");
    }
    if (ban.window === "info-answering") {
      return !text.includes("respondendo") && !text.includes("mais informacao") && !text.includes("cirurgico");
    }
    if (ban.window === "protect-pick") {
      return !text.includes("pune direto") && !text.includes("protege");
    }
    if (ban.window === "lane-protect") {
      return !text.includes("lane");
    }
    if (ban.window === "lane-partial") {
      return !text.includes("lane") && !text.includes("dupla");
    }
    if (ban.window === "lane-complete") {
      return !text.includes("fechada") && !text.includes("cirurgico");
    }
    if (ban.window === "map-open") {
      return !text.includes("mapa") && !text.includes("estrutura");
    }
    if (ban.window === "map-shaped") {
      return !text.includes("mapa") && !text.includes("engage");
    }
    return false;
  };
  const stageContextDescription = () => {
    if (isBanStage) {
      return "fase mais aberta da draft, entao o ban tende a limpar ameaca geral de role ou estilo";
    }
    if (isPickStage) {
      return "com teu pick aparecendo, o ban sobe de valor quando protege tua lane ou teu conforto";
    }
    return "a draft ja esta mais fechada e a leitura vira plano de lane";
  };
  const lockedFocusLabel = (value?: string) => {
    if (value === "danger") return "erro crítico";
    if (value === "duo") return "dupla";
    if (value === "map") return "mapa";
    if (value === "win") return "win condition";
    if (value === "synergy") return "sinergia";
    if (value === "reset") return "reset e loja";
    return "matchup";
  };
  const lockedSectionClass = (active: boolean, tone: "neutral" | "toxic" | "rose" = "neutral") => {
    if (active) {
      if (tone === "toxic") {
        return "rounded-2xl border border-toxic/20 bg-toxic/10 px-3 py-3";
      }
      if (tone === "rose") {
        return "rounded-2xl border border-rose-300/20 bg-rose-300/[0.08] px-3 py-3";
      }
      return "rounded-2xl border border-white/15 bg-white/[0.08] px-3 py-3";
    }
    if (tone === "toxic") {
      return "rounded-2xl border border-toxic/10 bg-toxic/[0.04] px-3 py-3 opacity-80";
    }
    if (tone === "rose") {
      return "rounded-2xl border border-rose-300/10 bg-rose-300/[0.04] px-3 py-3 opacity-80";
    }
    return "rounded-2xl border border-white/8 bg-black/20 px-3 py-3 opacity-80";
  };
  const lockedFocusIsMap = lockedFocus === "map";
  const lockedFocusIsDuo = lockedFocus === "duo";
  const lockedFocusIsWin = lockedFocus === "win";
  const lockedFocusIsSynergy = lockedFocus === "synergy";
  const hideOpeningCard = lockedFocusIsMap && !!lockedPlan?.map_plan_summary;
  const hideFirstResetCard = (lockedFocus === "reset" && !!lockedPlan?.reset_adjustment) || (lockedFocusIsMap && !!lockedPlan?.reset_adjustment);
  const hideLaneWindows = lockedFocusIsMap && !!lockedPlan?.map_plan_summary;
  const hideRecommendedSetup = lockedFocusIsDuo && !!lockedPlan?.synergy_summary;
  const hidePowerSpikes = lockedFocusIsDuo && !!lockedPlan?.fight_plan_summary;
  const hideBuildFocus = lockedFocusIsMap && (!!lockedPlan?.first_item_plan || !!lockedPlan?.reset_adjustment);
  const hideDangerLine = (lockedFocus === "danger" && !!lockedPlan?.lane_fail_condition) || (lockedFocusIsWin && !!lockedPlan?.lane_fail_condition);
  const hideWinResetCard = lockedFocusIsWin && (!!lockedPlan?.lane_win_condition || !!lockedPlan?.plan);
  const hideMapPlanTile = lockedFocusIsWin && !!lockedPlan?.lane_win_condition;
  const hideFightPlanTile = lockedFocusIsSynergy && !!lockedPlan?.synergy_summary;
  const hideTeamPlanTile = (lockedFocusIsSynergy && !!lockedPlan?.synergy_summary) || (lockedFocusIsWin && !!lockedPlan?.lane_win_condition);
  const hideSynergyTile = lockedFocusIsSynergy && !!lockedPlan?.team_plan_summary;
  const hideWinFirstItem = lockedFocusIsWin && !!lockedPlan?.first_reset_focus;
  const hideWinLanePlan = lockedFocusIsWin && !!lockedPlan?.lane_win_condition;
  const hideSynergyOpening = lockedFocusIsSynergy && !!lockedPlan?.synergy_summary;
  const pickHasComfortBadge = (pick: DraftRecommendationsSnapshot["recommendations"][number]) =>
    pick.familiarity === "main" || pick.familiarity === "pool" || preferredPoolSet.has(normalizeChampionName(pick.champion));

  if ((!matchIntel || matchIntel.length === 0) && !hasRecommendations) {
    return (
      <div className="app-surface w-full overflow-hidden rounded-[24px]">
        <div className="soft-divider flex items-center justify-between px-4 py-3">
          <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/65">
            {tacticalMode ? "Leitura de draft" : "Time inimigo"}
          </span>
          <div className="h-2 w-2 rounded-full bg-toxic shadow-[0_0_12px_rgba(173,255,47,0.6)]" />
        </div>
        <div className={`flex items-center gap-4 px-4 ${tacticalMode ? "py-7" : "py-5"}`}>
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Swords className="h-5 w-5 text-toxic/60" />
          </div>
          <div className="space-y-1">
            <p className="text-[11px] font-semibold text-white">Aguardando leitura de draft</p>
            <p className="text-[11px] text-white/45">
              {tacticalMode
                ? "Assim que a composicao aparecer, o modo tatico destaca counters e leituras de draft aqui."
                : "Os nomes inimigos aparecem aqui assim que o cliente liberar a composicao."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-surface flex h-full flex-col overflow-hidden rounded-[24px]">
      <div className="soft-divider flex items-center justify-between px-4 py-3">
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-white/65">
          {tacticalMode ? "Draft tático" : "Time inimigo"}
        </span>
        <div className="flex items-center gap-2">
          {tacticalMode && (
            <span className="rounded-full border border-toxic/25 bg-toxic/10 px-3 py-1 text-[9px] font-mono uppercase tracking-[0.16em] text-toxic">
              {isLockedStage ? "plano travado" : isBanStage ? "fase de ban" : "fase de pick"}
            </span>
          )}
          <Swords className="h-4 w-4 text-toxic" />
        </div>
      </div>

      <div className={`custom-scrollbar overflow-y-auto p-3 ${tacticalMode ? "space-y-4" : "space-y-3"}`}>
        {hasRecommendations && !isBanStage ? (
          <div className={`rounded-2xl border border-toxic/20 bg-toxic/10 ${tacticalMode ? "p-4" : "p-3"}`}>
            <div className="mb-2 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-toxic" />
              <span className="text-[10px] font-black uppercase tracking-[0.18em] text-white/75">
                {isPickStage ? "melhor pick jogável agora" : "melhores picks agora"}
              </span>
              {tacticalMode && <Sparkles className="h-3.5 w-3.5 text-toxic/80" />}
            </div>
            {settings?.prioritize_pool_picks && preferredPool.length > 0 ? (
              <div className="mb-3 text-[10px] leading-5 text-white/45">
                Picks da tua pool sobem na lista quando aparecem nas recomendacoes.
              </div>
            ) : null}
            <div className={tacticalMode ? "grid gap-3 xl:grid-cols-2" : "space-y-2"}>
              {visiblePicks.map((pick, index) => {
                const hasComfortBadge = pickHasComfortBadge(pick);
                const showFamiliarityText = !hasComfortBadge;
                const showFocusDescription = !pick.lane_plan_summary;
                const showCompStyle = !(pick.lane_plan_summary && pick.build_focus.length > 0);
                return (
                <div
                  key={pick.champion}
                  className={`rounded-2xl border ${index === 0 && tacticalMode ? "border-toxic/20 bg-toxic/[0.08]" : "border-white/8 bg-black/20"} ${tacticalMode ? "px-4 py-4" : "px-3 py-3"}`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <div className={`${tacticalMode ? "text-sm" : "text-[11px]"} font-semibold text-white`}>
                          {pick.champion}
                        </div>
                        {tacticalMode ? (
                          <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-white/55">
                            {pickFocusLabel(pick.focus)}
                          </span>
                        ) : null}
                        {tacticalMode && pick.context ? (
                          <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-white/45">
                            {pickContextLabel(pick.context)}
                          </span>
                        ) : null}
                        {tacticalMode && pick.window && showPickWindow(pick) ? (
                          <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-white/38">
                            {pickWindowLabel(pick.window)}
                          </span>
                        ) : null}
                        {pick.familiarity === "main" ? (
                          <span className="rounded-full border border-toxic/20 bg-toxic/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-toxic">
                            teu main
                          </span>
                        ) : pick.familiarity === "pool" || preferredPoolSet.has(normalizeChampionName(pick.champion)) ? (
                          <span className="rounded-full border border-toxic/20 bg-toxic/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-toxic">
                            tua pool
                          </span>
                        ) : null}
                      </div>
                      <div className="mt-1 text-[10px] text-white/42">
                        {(pick.reasons || []).slice(0, 2).join(" | ")}
                      </div>
                      {tacticalMode ? (
                        <div className="mt-2 space-y-1">
                          {showFamiliarityText ? (
                            <div className="text-[9px] uppercase tracking-[0.14em] text-white/32">
                              {familiarityLabel(pick.familiarity)}
                            </div>
                          ) : null}
                          {showFocusDescription ? (
                            <div className="text-[10px] text-white/32">
                              {pickFocusDescription(pick.focus)}
                            </div>
                          ) : null}
                          {pick.lane_plan_summary ? (
                            <div className="text-[10px] text-white/52">
                              plano da lane: {pick.lane_plan_summary}
                            </div>
                          ) : null}
                          {pick.lane_win_condition ? (
                            <div className="text-[10px] text-toxic/70">
                              vence a lane por: {pick.lane_win_condition}
                            </div>
                          ) : null}
                          {pick.lane_fail_condition ? (
                            <div className="text-[10px] text-rose-200/55">
                              perde se: {pick.lane_fail_condition}
                            </div>
                          ) : null}
                        </div>
                      ) : null}
                      {tacticalMode && pick.power_spikes?.[0] ? (
                        <div className="mt-1 text-[10px] text-white/32">
                          spike: {pick.power_spikes[0]}
                        </div>
                      ) : null}
                    </div>
                    <div className="rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-toxic">
                      {Math.round(pick.score)}
                    </div>
                  </div>
                  {tacticalMode && (
                    <div className="mt-3 space-y-2">
                      {showCompStyle ? (
                        <div className="text-[10px] uppercase tracking-[0.14em] text-white/35">
                          {pick.comp_style}
                        </div>
                      ) : null}
                      {pick.build_focus.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                          {pick.build_focus.slice(0, 3).map((focus) => (
                            <span
                              key={focus}
                              className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] uppercase tracking-[0.12em] text-white/55"
                            >
                              {focus}
                            </span>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  )}
                </div>
              )})}
            </div>
          </div>
        ) : null}

        {tacticalMode && bestBan && isBanStage ? (
          <div className="rounded-2xl border border-amber-400/20 bg-amber-400/10 p-4">
            <div className="mb-2 flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-amber-300" />
              <span className="text-[10px] font-black uppercase tracking-[0.18em] text-white/75">
                melhor ban agora
              </span>
            </div>
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold text-white">{bestBan.champion}</div>
                  <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-amber-200">
                    {banFocusLabel(bestBan.focus)}
                  </span>
                  {bestBan.context ? (
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-white/45">
                      {banContextLabel(bestBan.context)}
                    </span>
                  ) : null}
                  {bestBan.window && showBanWindow(bestBan) ? (
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-white/38">
                      {banWindowLabel(bestBan.window)}
                    </span>
                  ) : null}
                </div>
                <div className="mt-1 text-[10px] text-white/48">{(bestBan.reasons || []).slice(0, 2).join(" | ")}</div>
                {bestBan.focus === "anti-role" || bestBan.focus === "anti-comp" ? (
                  <div className="mt-2 text-[10px] text-white/38">{banFocusDescription(bestBan.focus)}</div>
                ) : null}
                {!bestBan.reasons?.length ? (
                  <div className="mt-1 text-[10px] text-white/28">{stageContextDescription()}</div>
                ) : null}
              </div>
              <div className="rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-amber-200">
                {Math.round(bestBan.score)}
              </div>
            </div>
          </div>
        ) : null}

        {tacticalMode && lockedPlan && isLockedStage ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-4">
            <div className="mb-2 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-toxic" />
              <span className="text-[10px] font-black uppercase tracking-[0.18em] text-white/75">
                plano depois do lock
              </span>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold text-white">
                    {lockedPlan.champion} vs {lockedPlan.enemy_anchor}
                  </div>
                  <span className="rounded-full border border-toxic/20 bg-toxic/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-[0.16em] text-toxic">
                    {lockedPlan.locked_focus === "danger" ? "erro critico" : lockedFocusLabel(lockedPlan.locked_focus)}
                  </span>
                </div>
                <div className="mt-1 text-[10px] uppercase tracking-[0.14em] text-toxic/80">
                  matchup {lockedPlan.verdict}
                </div>
              </div>
              <div className="text-[11px] leading-6 text-white/72">
                {lockedPlan.plan}
              </div>
              {lockedPlan.lane_plan && !hideWinLanePlan ? (
                <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                  <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">lane</div>
                  <div className="mt-1 text-[10px] text-white/68">{lockedPlan.lane_plan}</div>
                </div>
              ) : null}
              {lockedPlan.lane_windows?.length && !hideLaneWindows ? (
                <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                  <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">janelas da lane</div>
                  <div className="mt-2 space-y-1.5">
                    {lockedPlan.lane_windows.map((window) => (
                      <div key={window} className="text-[10px] text-white/68">
                        {window}
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
              {lockedPlan.lane_win_condition || lockedPlan.lane_fail_condition ? (
                <div className="grid gap-2 lg:grid-cols-2">
                  {lockedPlan.lane_win_condition ? (
                    <div className={lockedSectionClass(lockedPlan.locked_focus === "win", "toxic")}>
                      <div className="text-[9px] uppercase tracking-[0.12em] text-toxic/70">condicao de vitoria</div>
                      <div className="mt-1 text-[10px] text-white/68">{lockedPlan.lane_win_condition}</div>
                    </div>
                  ) : null}
                  {lockedPlan.lane_fail_condition ? (
                    <div className={lockedSectionClass(lockedPlan.locked_focus === "danger", "rose")}>
                      <div className="text-[9px] uppercase tracking-[0.12em] text-rose-200/70">erro que mais perde</div>
                      <div className="mt-1 text-[10px] text-white/68">{lockedPlan.lane_fail_condition}</div>
                    </div>
                  ) : null}
                </div>
              ) : null}
              {lockedPlan.danger && !hideDangerLine ? (
                <div className="text-[10px] text-white/45">
                  cuidado: {lockedPlan.danger}
                </div>
              ) : null}
              <div className="grid gap-2 lg:grid-cols-2">
                {!hideOpeningCard && !hideSynergyOpening ? (
                  <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                    <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">opening</div>
                    <div className="mt-1 text-[10px] text-white/68">{lockedPlan.opening_plan}</div>
                  </div>
                ) : null}
                {!hideFirstResetCard && !hideWinResetCard ? (
                  <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                    <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">primeiro reset</div>
                    <div className="mt-1 text-[10px] text-white/68">{lockedPlan.first_reset_focus}</div>
                  </div>
                ) : null}
              </div>
              {(lockedPlan.reset_adjustment || lockedPlan.map_plan_summary || lockedPlan.fight_plan_summary || lockedPlan.team_plan_summary || lockedPlan.synergy_summary) ? (
                <div className="grid gap-2 lg:grid-cols-2 xl:grid-cols-4">
                  {lockedPlan.reset_adjustment ? (
                    <div className={lockedSectionClass(lockedPlan.locked_focus === "reset")}>
                      <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">ajuste de reset</div>
                      <div className="mt-1 text-[10px] text-white/68">{lockedPlan.reset_adjustment}</div>
                    </div>
                  ) : null}
                    {lockedPlan.map_plan_summary && !hideMapPlanTile ? (
                      <div className={lockedSectionClass(lockedFocusIsMap)}>
                        <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">plano de mapa</div>
                        <div className="mt-1 text-[10px] text-white/68">{lockedPlan.map_plan_summary}</div>
                      </div>
                    ) : null}
                    {lockedPlan.fight_plan_summary && !hideFightPlanTile ? (
                      <div className={lockedSectionClass(lockedFocusIsDuo || lockedFocusIsSynergy)}>
                        <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">como tua comp luta</div>
                        <div className="mt-1 text-[10px] text-white/68">{lockedPlan.fight_plan_summary}</div>
                      </div>
                    ) : null}
                    {lockedPlan.team_plan_summary && !hideTeamPlanTile ? (
                      <div className={lockedSectionClass(lockedFocusIsSynergy || lockedFocusIsMap)}>
                        <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">plano da comp</div>
                        <div className="mt-1 text-[10px] text-white/68">{lockedPlan.team_plan_summary}</div>
                      </div>
                    ) : null}
                    {lockedPlan.synergy_summary && !hideSynergyTile ? (
                      <div className={`${lockedSectionClass(lockedFocusIsSynergy || lockedFocusIsDuo)} xl:col-span-2`}>
                        <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">sinergia aliada</div>
                        <div className="mt-1 text-[10px] text-white/68">{lockedPlan.synergy_summary}</div>
                      </div>
                    ) : null}
                </div>
              ) : null}
              {lockedPlan.first_item_plan && !hideFirstResetCard && !hideWinFirstItem ? (
                <div className={lockedSectionClass(lockedPlan.locked_focus === "reset" || lockedFocusIsMap)}>
                  <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">primeiro item</div>
                  <div className="mt-1 text-[10px] text-white/68">{lockedPlan.first_item_plan}</div>
                </div>
              ) : null}
              {lockedPlan.recommended_setup && !hideRecommendedSetup ? (
                <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                  <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">setup recomendado</div>
                  <div className="mt-1 text-[10px] text-white/68">{lockedPlan.recommended_setup}</div>
                </div>
              ) : null}
              {lockedPlan.build_focus?.length && !hideBuildFocus ? (
                <div className="flex flex-wrap gap-2">
                  {lockedPlan.build_focus.map((focus) => (
                    <span
                      key={focus}
                      className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[9px] uppercase tracking-[0.12em] text-white/55"
                    >
                      {focus}
                    </span>
                  ))}
                </div>
              ) : null}
              {lockedPlan.power_spikes?.length && !hidePowerSpikes ? (
                <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                  <div className="text-[9px] uppercase tracking-[0.12em] text-white/35">picos de poder</div>
                  <div className="mt-1 text-[10px] text-white/68">
                    {lockedPlan.power_spikes.join(" • ")}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        <div className={`grid gap-2 ${tacticalMode ? "grid-cols-1 2xl:grid-cols-2" : "grid-cols-1"}`}>
          {matchIntel.map((player, idx) => (
            <motion.div
              key={player.name}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.06 }}
              className={`rounded-2xl border border-white/8 bg-white/[0.04] transition-colors hover:border-white/15 hover:bg-white/[0.06] ${
                tacticalMode ? "px-4 py-4" : "px-3 py-3"
              }`}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex flex-col">
                  <span
                    className={`truncate font-semibold text-white ${
                      tacticalMode ? "max-w-[220px] text-[12px]" : "max-w-[140px] text-[11px]"
                    }`}
                  >
                    {player.name}
                  </span>
                  <span className="text-[10px] text-white/45">
                    {player.champion || "Desconhecido"}
                  </span>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="block text-[9px] uppercase tracking-[0.12em] text-white/35">
                      elo
                    </span>
                    <span className="text-[11px] font-semibold text-violet-300">
                      {player.rank === "Carregando"
                        ? "carregando"
                        : player.rank === "Indisponivel"
                          ? "--"
                          : player.rank || "--"}
                    </span>
                  </div>
                  <div className="min-w-[52px] text-right">
                    <span className="block text-[9px] uppercase tracking-[0.12em] text-white/35">
                      wr
                    </span>
                    <span className="text-[11px] font-semibold text-toxic">
                      {player.winrate === "..."
                        ? "..."
                        : player.winrate === "Indisponivel"
                          ? "--"
                          : player.winrate || "--"}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
