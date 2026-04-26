import type { Metadata } from "next";

import ProgressionWorkspace from "@/components/progression/ProgressionWorkspace";

export const metadata: Metadata = {
  title: "Progressao",
  description: "Painel isolado de progressao orientado por performance e resumo de partidas.",
};

export default function ProgressionPage() {
  return <ProgressionWorkspace />;
}
