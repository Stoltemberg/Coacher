export type DashboardView = "live" | "draft" | "postgame" | "progress" | "settings";

export function classifyDashboardView(input: {
  phase?: string | null;
  hasDraft: boolean;
  hasSummary: boolean;
}): DashboardView {
  const phase = (input.phase || "").toLowerCase();

  if (input.hasDraft || phase.includes("champ") || phase.includes("campe") || phase.includes("selec")) {
    return "draft";
  }

  if (phase.includes("progress") || phase.includes("inprogress") || phase.includes("partida") || phase.includes("game")) {
    return "live";
  }

  if (input.hasSummary) {
    return "postgame";
  }

  return "live";
}

export function phaseCopy(phase?: string | null) {
  const normalized = (phase || "").toLowerCase();
  if (normalized.includes("champ") || normalized.includes("campe") || normalized.includes("selec")) return "Selecao de Campeoes";
  if (normalized.includes("progress") || normalized.includes("inprogress")) return "Em partida";
  if (normalized.includes("lobby")) return "Lobby";
  if (normalized.includes("ready")) return "Pronto check";
  if (normalized.includes("matchmaking")) return "Fila";
  return phase || "Aguardando";
}
