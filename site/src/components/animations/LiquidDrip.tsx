"use client";

import { motion, useScroll, useTransform, useVelocity, useSpring } from "framer-motion";
import { useEffect, useState } from "react";

export default function LiquidDrip() {
  const { scrollYProgress } = useScroll();
  const scrollVelocity = useVelocity(scrollYProgress);
  
  // Smooth out the velocity for the drip stretching
  const smoothVelocity = useSpring(scrollVelocity, {
    damping: 50,
    stiffness: 400
  });

  // Transform velocity into scale and opacity
  const dripHeight = useTransform(smoothVelocity, [-1, 0, 1], [3, 1, 3]);
  const dripOpacity = useTransform(smoothVelocity, [-0.5, 0, 0.5], [0.6, 0.2, 0.6]);

  const { scrollY } = useScroll();
  const parallaxY = useTransform(scrollY, [0, 5000], [0, -2500]);

  const [isMobile, setIsMobile] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

  if (!isMounted) return null;

  const dripCount = isMobile ? 3 : 6;

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {/* SVG Filter Definition - Only render on Desktop */}
      {!isMobile && (
        <svg className="hidden">
          <defs>
            <filter id="goo">
              <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
              <feColorMatrix 
                in="blur" 
                mode="matrix" 
                values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" 
                result="goo" 
              />
              <feComposite in="SourceGraphic" in2="goo" operator="atop" />
            </filter>
          </defs>
        </svg>
      )}

      {/* Drip Elements */}
      <motion.div 
        className={`${!isMobile ? "liquid-goo" : ""} absolute inset-0 will-change-transform`}
        style={{ y: parallaxY }}
      >
        {[...Array(dripCount)].map((_, i) => (
          <motion.div
            key={`drip-${i}`}
            className={`absolute ${isMobile ? "bg-accent/20 blur-xl" : "bg-accent/40"} rounded-full`}
            style={{
              left: `${15 + i * (isMobile ? 30 : 15)}%`,
              top: "-50px",
              width: `${10 + (i % 3) * 5}px`,
              height: "100px",
              scaleY: dripHeight,
              opacity: dripOpacity,
            }}
            animate={{
              y: [0, 10, 0],
            }}
            transition={{
              duration: 2 + i,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        ))}
        
        {/* Static hanging drips */}
        {[...Array(isMobile ? 2 : 4)].map((_, i) => (
          <div
            key={`static-${i}`}
            className="absolute bg-accent/20 rounded-full opacity-30"
            style={{
              left: `${30 + i * (isMobile ? 40 : 20)}%`,
              top: "-20px",
              width: "40px",
              height: "60px",
              filter: "blur(4px)"
            }}
          />
        ))}
      </motion.div>
    </div>
  );
}
