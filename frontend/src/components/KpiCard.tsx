"use client";

import { useEffect, useRef, useState } from "react";

interface KpiCardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  icon: string;
  color: "cyan" | "violet" | "emerald" | "amber" | "rose";
  delay?: number;
}

const COLOR_MAP = {
  cyan: "from-cyan-400/20 to-cyan-400/5 border-cyan-400/20 text-cyan-400",
  violet: "from-violet-400/20 to-violet-400/5 border-violet-400/20 text-violet-400",
  emerald: "from-emerald-400/20 to-emerald-400/5 border-emerald-400/20 text-emerald-400",
  amber: "from-amber-400/20 to-amber-400/5 border-amber-400/20 text-amber-400",
  rose: "from-rose-400/20 to-rose-400/5 border-rose-400/20 text-rose-400",
};

export default function KpiCard({ label, value, prefix = "", suffix = "", icon, color, delay = 0 }: KpiCardProps) {
  const [displayed, setDisplayed] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const target = value;
    const duration = 1200;
    const startTime = performance.now();

    const timer = setTimeout(() => {
      const animate = (currentTime: number) => {
        const elapsed = currentTime - startTime - delay;
        if (elapsed < 0) {
          requestAnimationFrame(animate);
          return;
        }
        const progress = Math.min(elapsed / duration, 1);
        // Ease out cubic
        const eased = 1 - Math.pow(1 - progress, 3);
        setDisplayed(Math.floor(target * eased));
        if (progress < 1) requestAnimationFrame(animate);
        else setDisplayed(target);
      };
      requestAnimationFrame(animate);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  const formatNumber = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return n.toLocaleString();
  };

  const colorClasses = COLOR_MAP[color];

  return (
    <div
      ref={ref}
      className={`glass-card gradient-border p-5 bg-gradient-to-br ${colorClasses} animate-fade-in-up`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-2xl">{icon}</span>
        <div className={`w-2 h-2 rounded-full bg-current animate-pulse-glow`} />
      </div>
      <p className="text-[11px] uppercase tracking-wider text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-white">
        {prefix}{formatNumber(displayed)}{suffix}
      </p>
    </div>
  );
}
