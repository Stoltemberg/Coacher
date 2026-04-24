"use client";

import { motion, type Variants } from "framer-motion";

const smoothEase = [0.16, 1, 0.3, 1] as const;

const containerVariants: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.065,
      delayChildren: 0.25,
    },
  },
};

const letterVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 96,
    rotateX: -90,
    filter: "blur(12px)",
  },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    filter: "blur(0px)",
    transition: {
      duration: 0.9,
      ease: smoothEase,
    },
  },
};

const contentVariants: Variants = {
  hidden: {
    opacity: 0,
    y: 28,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.9,
      ease: smoothEase,
      delay: 0.95,
    },
  },
};

export default function KineticHero() {
  const title = "COACHER.";

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="relative flex min-h-[95vh] flex-col items-center justify-center overflow-hidden px-4 text-center">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-1/2 h-[42rem] w-[42rem] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,_rgba(173,255,47,0.08)_0%,_rgba(87,33,255,0.06)_42%,_transparent_72%)] blur-3xl" />
        <div className="absolute inset-x-[12%] top-[22%] h-px bg-gradient-to-r from-transparent via-toxic/35 to-transparent" />
      </div>

      <motion.h1
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="relative z-10 flex w-full max-w-[95vw] flex-col items-center gap-0 font-black tracking-tighter"
      >
        <span className="block whitespace-nowrap [perspective:1200px]">
          {title.split("").map((letter, index) => (
            <motion.span
              key={`${letter}-${index}`}
              variants={letterVariants}
              className="inline-block text-[clamp(2rem,14vw,20vw)] leading-[0.75] text-white drop-shadow-[0_0_24px_rgba(173,255,47,0.12)]"
            >
              {letter}
            </motion.span>
          ))}
        </span>
      </motion.h1>

      <motion.p
        initial="hidden"
        animate="visible"
        variants={contentVariants}
        className="hero-sub relative z-10 mt-12 max-w-2xl font-mono text-lg uppercase tracking-[0.3em] text-white md:text-2xl"
      >
        [ COACHER ] - performance competitiva em tempo real.
      </motion.p>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={contentVariants}
        className="hero-btn relative z-10 mt-12 flex flex-col gap-6 sm:flex-row"
      >
        <button
          onClick={() => scrollTo("download")}
          className="rounded-none bg-accent px-10 py-5 text-lg font-bold text-white transition-all hover:bg-violet-600 active:scale-95"
        >
          BAIXAR APP
        </button>
        <button
          onClick={() => scrollTo("features")}
          className="border border-border px-10 py-5 text-lg font-bold text-foreground transition-all hover:bg-white/5"
        >
          VER RECURSOS
        </button>
      </motion.div>
    </section>
  );
}
