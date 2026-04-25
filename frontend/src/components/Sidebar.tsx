"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/overview", label: "Overview", icon: "📊" },
  { href: "/forecast", label: "Forecast", icon: "📈" },
  { href: "/drivers", label: "Drivers", icon: "⚡" },
  { href: "/segmentation", label: "Segments", icon: "🎯" },
  { href: "/explainability", label: "Explain", icon: "🧠" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-[220px] flex flex-col py-6 px-4 border-r border-white/[0.06] bg-[#12141f]/80 backdrop-blur-xl z-50">
      {/* Logo */}
      <div className="flex items-center gap-3 px-3 mb-10">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
          RA
        </div>
        <div>
          <h1 className="text-sm font-bold text-white leading-tight">Retail</h1>
          <p className="text-[10px] text-slate-400 leading-tight">Analytics & Forecasting</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`sidebar-link ${pathname === item.href ? "active" : ""}`}
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 pt-4 border-t border-white/[0.06]">
        <p className="text-[10px] text-slate-500">v1.0.0 • Strategy Pattern</p>
      </div>
    </aside>
  );
}
