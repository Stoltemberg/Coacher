"use client";

import { useEffect, useRef } from "react";
import anime from "animejs";
import NeuralBrain from "./NeuralBrain";


export default function KineticHero() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Split text into letters for the "Premium" staggering effect
    const letters = containerRef.current.querySelectorAll(".letter");

    anime.timeline({
      easing: "easeOutExpo",
    })
      .add({
        targets: letters,
        translateY: [100, 0],
        rotateZ: [10, 0],
        opacity: [0, 1],
        delay: anime.stagger(40, { start: 500 }),
        duration: 1500,
      })
      .add({
        targets: ".hero-sub",
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 1000,
      }, "-=1000")
      .add({
        targets: ".hero-btn",
        scale: [0.9, 1],
        opacity: [0, 1],
        duration: 800,
      }, "-=800");

  }, []);

  const lines = ["COACHER."];

  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div ref={containerRef} className="relative flex flex-col items-center justify-center min-h-[95vh] text-center px-4 overflow-hidden">
      <NeuralBrain />
      <h1 className="relative z-10 flex flex-col items-center gap-0 font-black tracking-tighter w-full max-w-[95vw]">
        {lines.map((line, lineIdx) => (
          <div key={lineIdx} className="line block w-full whitespace-nowrap">
            {line.split("").map((l, i) => (
              <span
                key={i}
                className="letter inline-block text-[clamp(2rem,14vw,20vw)] leading-[0.75]"
              >
                {l}
              </span>
            ))}
          </div>
        ))}
      </h1>

      <p className="hero-sub relative z-10 max-w-2xl mt-12 text-lg md:text-2xl text-muted-foreground font-mono opacity-0 uppercase tracking-[0.3em] text-white">
        [ NEURAL_COACHER ] - PERFORMANCE DE ELITE EM TEMPO REAL.
      </p>

      <div className="hero-btn relative z-10 mt-12 flex flex-col sm:flex-row gap-6 opacity-0">
        <button
          onClick={() => scrollTo("download")}
          className="px-10 py-5 bg-accent text-white font-bold hover:bg-violet-600 transition-all active:scale-95 text-lg"
        >
          OBTER O CÉREBRO
        </button>
        <button
          onClick={() => scrollTo("features")}
          className="px-10 py-5 border border-border text-foreground font-bold hover:bg-white/5 transition-all text-lg"
        >
          VER DECK DE DADOS
        </button>
      </div>
    </div>
  );
}
