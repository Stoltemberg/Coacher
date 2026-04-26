import type { CoachCallSnapshot } from "@/types/bridge";

export type CoachReadKind = "risco" | "execucao" | "leitura" | "proximo";

const riskPattern = /(nao|não|evita|cuidado|risco|perde|pun(e|i)|sem recurso|morrer|entrega|janela ruim)/;
const actionPattern = /(faz|joga|usa|procura|segura|reseta|base|compra|prioriza|pressiona|marca|espera|luta|roda)/;

export function splitCoachCall(value: string) {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (!normalized) {
    return {
      headline: "Aguardando leitura do coach.",
      reads: [] as string[],
    };
  }

  const parts = normalized
    .split(/(?<=[.!?])\s+/)
    .map((part) => part.trim())
    .filter(Boolean);

  if (parts.length <= 1) {
    const softLimit = 138;
    if (normalized.length <= softLimit) {
      return { headline: normalized, reads: [] as string[] };
    }
    const cutAt = normalized.lastIndexOf(" ", softLimit);
    const splitAt = cutAt > 80 ? cutAt : softLimit;
    return {
      headline: `${normalized.slice(0, splitAt).trim()}...`,
      reads: [normalized.slice(splitAt).trim()].filter(Boolean),
    };
  }

  return {
    headline: parts[0],
    reads: parts.slice(1, 3),
  };
}

export function classifyCoachRead(text: string, index: number): CoachReadKind {
  const lower = text.toLowerCase();
  if (riskPattern.test(lower)) return "risco";
  if (actionPattern.test(lower)) return "execucao";
  return index === 0 ? "leitura" : "proximo";
}

export function buildCoachCallSnapshot(
  message: string,
  type = "normal",
  category?: string | null,
  call?: CoachCallSnapshot,
): CoachCallSnapshot {
  if (call?.headline) {
    return {
      ...call,
      type: call.type || type,
      category: call.category ?? category ?? null,
    };
  }

  const fallback = splitCoachCall(message);
  const payload: CoachCallSnapshot = {
    headline: fallback.headline,
    type,
    category: category ?? null,
  };

  fallback.reads.forEach((read, index) => {
    const kind = classifyCoachRead(read, index);
    if (kind === "risco" && !payload.risk) payload.risk = read;
    else if (kind === "execucao" && !payload.action) payload.action = read;
    else if (!payload.next_step) payload.next_step = read;
  });

  return payload;
}
