"use client";

import { AlertTriangle, Sparkles, Target } from "lucide-react";
import { motion } from "framer-motion";

import type { CoachCallSnapshot } from "@/types/bridge";
import { classifyCoachRead, splitCoachCall } from "./coach-call";

export default function CoachCallCard({
  eyebrow = "call principal",
  title,
  detail,
  tags = [],
  compact = false,
  call,
}: {
  eyebrow?: string;
  title: string;
  detail?: string;
  tags?: string[];
  compact?: boolean;
  call?: CoachCallSnapshot;
}) {
  const fallbackCall = splitCoachCall(title);
  const headline = call?.headline || fallbackCall.headline;
  const reads = [call?.risk, call?.action, call?.next_step, ...fallbackCall.reads].filter(
    (read, index, source): read is string => Boolean(read) && source.indexOf(read) === index,
  );
  const supportingDetail = detail && !reads.includes(detail) ? detail : undefined;

  return (
    <motion.section
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-[24px] border border-[#ADFF2F]/16 bg-[linear-gradient(180deg,rgba(173,255,47,0.08),rgba(10,10,12,0.92))] shadow-[0_20px_60px_rgba(0,0,0,0.35)] ${
        compact ? "p-4" : "p-6"
      }`}
    >
      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#ADFF2F]">
        <Sparkles className="h-4 w-4" />
        {eyebrow}
      </div>
      <div className={`mt-3 font-semibold text-white ${compact ? "text-[18px] leading-7" : "text-[26px] leading-[1.35]"}`}>
        {headline}
      </div>
      {reads.length > 0 || supportingDetail ? (
        <div className="mt-3 space-y-2">
          {reads.slice(0, 3).map((read, index) => (
            <OperationalRead key={read} index={index} text={read} compact={compact} />
          ))}
          {supportingDetail ? (
            <OperationalRead index={reads.length} text={supportingDetail} compact={compact} muted />
          ) : null}
        </div>
      ) : null}
      {tags.length > 0 ? (
        <div className="mt-4 flex flex-wrap gap-2">
          {tags.filter(Boolean).map((tag) => (
            <span
              key={tag}
              className="rounded-full border border-white/10 bg-black/20 px-2.5 py-1 text-[9px] font-mono uppercase tracking-[0.14em] text-white/42"
            >
              {tag}
            </span>
          ))}
        </div>
      ) : null}
    </motion.section>
  );
}

function OperationalRead({
  text,
  index,
  compact,
  muted = false,
}: {
  text: string;
  index: number;
  compact: boolean;
  muted?: boolean;
}) {
  const kind = classifyCoachRead(text, index);
  const config = {
    risco: { label: "risco", tone: "text-amber-300", Icon: AlertTriangle },
    execucao: { label: "execução", tone: "text-[#ADFF2F]", Icon: Target },
    leitura: { label: "leitura", tone: "text-[#38BDF8]", Icon: Sparkles },
    proximo: { label: "próximo passo", tone: "text-violet-300", Icon: Sparkles },
  }[kind];
  const { label, tone, Icon } = config;

  return (
    <div className="rounded-[12px] border border-white/[0.05] bg-black/20 px-3 py-2">
      <div className={`mb-1 flex items-center gap-1.5 text-[9px] font-bold uppercase ${muted ? "text-white/28" : tone}`}>
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <p className={`line-clamp-2 ${muted ? "text-white/44" : "text-white/62"} ${compact ? "text-[11px] leading-5" : "text-[13px] leading-6"}`}>
        {text}
      </p>
    </div>
  );
}
