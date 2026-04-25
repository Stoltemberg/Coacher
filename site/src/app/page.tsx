"use client";

import { motion } from "framer-motion";
import Image from "next/image";

import KineticHero from "@/components/animations/KineticHero";
import BentoFeatures from "@/components/sections/BentoFeatures";
import CoreSection from "@/components/sections/CoreSection";
import PersonalityDemo from "@/components/sections/PersonalityDemo";

const sectionTransition = {
  duration: 0.9,
  ease: [0.16, 1, 0.3, 1] as const,
};

export default function Home() {
  return (
    <main className="relative z-10">
      <h1 className="sr-only">Coach de LoL com IA - Evolua no League of Legends com o Coacher</h1>
      <KineticHero />

      <motion.section
        id="core"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={sectionTransition}
      >
        <CoreSection />
      </motion.section>

      <motion.section
        id="features"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ ...sectionTransition, delay: 0.05 }}
      >
        <BentoFeatures />
      </motion.section>

      <motion.section
        id="personality"
        initial={{ opacity: 0, y: 36 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.2 }}
        transition={{ ...sectionTransition, delay: 0.08 }}
      >
        <PersonalityDemo />
      </motion.section>

      <motion.section
        id="demo"
        className="px-6 py-32"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.25 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="mx-auto max-w-7xl">
          <motion.div
            className="group brutalist-border relative aspect-video overflow-hidden"
            initial={{ scale: 0.96, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            viewport={{ once: true, amount: 0.35 }}
            transition={{ duration: 1.05, ease: [0.16, 1, 0.3, 1] }}
          >
            <Image
              src="/gameplay_overlay.webp"
              alt="Demonstração do overlay de gameplay"
              fill
              sizes="(max-width: 1280px) 100vw, 1200px"
              className="object-cover grayscale transition-all duration-1000 group-hover:grayscale-0"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent" />
            <motion.div
              className="absolute bottom-12 left-12"
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.85, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            >
              <h3 className="text-4xl uppercase">Leitura de partida em tempo real.</h3>
              <p className="mt-2 font-mono text-muted-foreground">COACHER // overlay de decisão e análise</p>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      <motion.section
        id="download"
        className="px-6 py-64 text-center"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.25 }}
        transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="mx-auto max-w-4xl space-y-12">
          <motion.h2
            className="flex flex-col items-center font-black uppercase"
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.5 }}
            transition={{ duration: 0.85, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="text-[12vw] leading-[0.8]">Jogue</span>
            <span className="text-[8vw] leading-[0.8] opacity-50">Com</span>
            <span className="text-[12vw] leading-[0.8]">Plano</span>
          </motion.h2>

          <motion.p
            className="mx-auto max-w-2xl text-2xl font-mono uppercase tracking-wider text-muted-foreground"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.5 }}
            transition={{ duration: 0.85, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
          >
            Pare de jogar no instinto. Treine com um coach que lê draft, matchup, macro e teu padrão entre partidas.
          </motion.p>

          <motion.div
            className="pt-12"
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.5 }}
            transition={{ duration: 0.8, delay: 0.14, ease: [0.16, 1, 0.3, 1] }}
          >
            <a
              href="/coacher_v1_setup.exe"
              download="coacher_v1_setup.exe"
              className="group relative inline-block overflow-hidden bg-white px-16 py-8 text-2xl font-black uppercase text-black transition-all duration-500 hover:bg-toxic"
            >
              <span className="relative z-10 font-black">Baixar desktop app</span>
              <div className="absolute inset-0 translate-y-full bg-accent transition-transform duration-500 group-hover:translate-y-0" />
            </a>
          </motion.div>
        </div>
      </motion.section>

      <motion.footer
        className="flex flex-col items-center justify-between gap-8 border-t border-border px-6 py-12 text-[10px] font-mono uppercase tracking-[0.2em] text-muted-foreground md:flex-row"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div>© 2026 Coacher. Todos os direitos reservados.</div>
        <div>Produto desktop para análise e coaching de League of Legends.</div>
      </motion.footer>
    </main>
  );
}
