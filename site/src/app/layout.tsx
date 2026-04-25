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

import { BridgeProvider } from "@/contexts/BridgeContext";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    default: "Coacher - O Melhor Coach de LoL com IA",
    template: "%s | Coacher"
  },
  description: "Evolua no League of Legends. Treine com um coach que lê draft, matchup e macro em tempo real.",
  keywords: ["Coach LoL", "League of Legends Coach", "Análise de partida LoL", "Subir de elo no LoL", "Coach IA"],
  verification: {
    google: "-VKbAP2NTN8EiKybVj3xM7B1EGgUdxXz4FYcNA5pSXo"
  },
  openGraph: {
    title: "Coacher - O Melhor Coach de LoL com IA",
    description: "Evolua no League of Legends. Treine com um coach que lê draft, matchup e macro em tempo real.",
    url: "https://coacher.gg",
    siteName: "Coacher",
    type: "website"
  },
  twitter: {
    card: "summary_large_image",
    title: "Coacher - O Melhor Coach de LoL com IA",
    description: "Evolua no League of Legends. Treine com um coach que lê draft, matchup e macro em tempo real."
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const schemaMarkup = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Coacher",
    "applicationCategory": "GameApplication",
    "operatingSystem": "Windows",
    "description": "Treinador de inteligência artificial para League of Legends que analisa draft, matchup e macro em tempo real.",
    "offers": {
      "@type": "Offer",
      "price": "0.00",
      "priceCurrency": "BRL"
    }
  };

  return (
    <html
      lang="pt-BR"
      className={`${outfit.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaMarkup) }}
        />
      </head>
      <body className="min-h-full flex flex-col relative text-foreground selection:bg-toxic/30 bg-[#050508]">
        <BridgeProvider>
          {children}
        </BridgeProvider>
      </body>
    </html>
  );
}
