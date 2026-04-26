"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { useMemo } from "react";

interface HudPanelProps {
  title: string;
  icon: LucideIcon;
  children: React.ReactNode;
  className?: string;
  idSuffix?: string;
  subtitle?: string;
}

export function HudPanel({
  title,
  icon: Icon,
  children,
  className = "",
  idSuffix = "SYS",
  subtitle = "Painel ativo do coach desktop",
}: HudPanelProps) {
  const panelId = useMemo(() => {
    const source = `${title}:${idSuffix}`;
    const checksum = Array.from(source).reduce((total, char) => total + char.charCodeAt(0), 0);
    return `0x${checksum.toString(16).toUpperCase().padStart(2, "0")}_${idSuffix}`;
  }, [idSuffix, title]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      className={`app-surface floating-glow relative flex flex-col overflow-hidden rounded-[28px] ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(173,255,47,0.06),_transparent_32%)] opacity-70" />

      <header className="soft-divider relative flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Icon className="h-4 w-4 text-toxic" />
          </div>
          <div className="space-y-0.5">
            <span className="block text-[10px] font-black uppercase tracking-[0.24em] text-white/92">
              {title}
            </span>
            <span className="block text-[10px] text-white/45">
              {subtitle}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[9px] font-mono uppercase tracking-[0.18em] text-white/45">
            {panelId}
          </span>
          <span className="h-2 w-2 rounded-full bg-toxic shadow-[0_0_14px_rgba(173,255,47,0.7)]" />
        </div>
      </header>

      <div className="relative flex-1 overflow-hidden">{children}</div>
    </motion.div>
  );
}
