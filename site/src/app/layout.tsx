import type { Metadata } from "next";
import { Outfit, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["400", "700", "900"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Coacher | LoL Intelligence",
  description: "Real-time League of Legends coaching with a personality. Dominate the Rift.",
};

import LiquidDrip from "@/components/animations/LiquidDrip";
import SmoothScroll from "@/components/animations/SmoothScroll";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${outfit.variable} ${jetbrainsMono.variable} h-full antialiased selection:bg-violet-500/30`}
    >
      <body className="min-h-full flex flex-col relative">
        <SmoothScroll>
          <LiquidDrip />
          <div className="noise-overlay" />
          {children}
        </SmoothScroll>
      </body>
    </html>
  );
}
