"use client";

import KineticHero from "@/components/animations/KineticHero";
import CoreSection from "@/components/sections/CoreSection";
import BentoFeatures from "@/components/sections/BentoFeatures";
import PersonalityDemo from "@/components/sections/PersonalityDemo";
import LiquidContent from "@/components/animations/LiquidContent";
import Image from "next/image";

export default function Home() {
  return (
    <LiquidContent>
      <main className="relative z-10">
        {/* Hero */}
        <KineticHero />

        {/* The Core */}
        <section id="core">
          <CoreSection />
        </section>

        {/* Features */}
        <section id="features">
          <BentoFeatures />
        </section>

        {/* Personality Demo */}
        <section id="personality">
          <PersonalityDemo />
        </section>

        {/* Vision Demonstration */}
        <section id="demo" className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <div className="relative aspect-video brutalist-border overflow-hidden group">
              <Image
                src="/gameplay_overlay.png"
                alt="Demonstração do Overlay de Gameplay"
                fill
                sizes="(max-width: 1280px) 100vw, 1200px"
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-1000"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
              <div className="absolute bottom-12 left-12">
                <h3 className="text-4xl uppercase">Rastreamento de Precisão.</h3>
                <p className="text-muted-foreground font-mono mt-2">MOTOR_DE_VISAO_V4.2.0</p>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section id="download" className="py-64 px-6 text-center">
          <div className="max-w-4xl mx-auto space-y-12">
            <h2 className="flex flex-col items-center font-black uppercase">
              <span className="text-[12vw] leading-[0.8]">Alcance</span>
              <span className="text-[8vw] leading-[0.8] opacity-50">O</span>
              <span className="text-[12vw] leading-[0.8]">Topo</span>
            </h2>
            <p className="text-2xl text-muted-foreground max-w-2xl mx-auto uppercase font-mono tracking-wider">
              Pare de jogar às cegas. Treine com a única plataforma neural que entende seu potencial real.
            </p>
            <div className="pt-12">
              <a
                href="/coacher_v1_setup.exe"
                download="coacher_v1_setup.exe"
                className="group relative inline-block px-16 py-8 bg-white text-black text-2xl font-black uppercase hover:bg-toxic transition-all duration-500 overflow-hidden"
              >
                <span className="relative z-10 font-black">OBTER ACESSO ELITE</span>
                <div className="absolute inset-0 bg-accent translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
              </a>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-12 px-6 border-t border-border flex flex-col md:flex-row justify-between items-center gap-8 text-[10px] font-mono text-muted-foreground uppercase tracking-[0.2em]">
          <div>© 2026 NEURAL_COACHER_PROG / TODOS OS DIREITOS RESERVADOS</div>
          <div>OTIMIZADO_PARA_VITORIA.SYS</div>
        </footer>
      </main>
    </LiquidContent>
  );
}
