"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "📊" },
  { href: "/odds", label: "Odds", icon: "📈" },
  { href: "/alerts", label: "Alerts", icon: "🔔" },
  { href: "/polymarket", label: "Polymarket", icon: "🔮" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-[var(--bg-secondary)] border-r border-[var(--border)] min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-lg font-bold text-white">Betting Analyzer</h1>
        <p className="text-xs text-[var(--text-secondary)]">v0.1.0</p>
      </div>
      <nav className="space-y-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded text-sm transition-colors ${
                active
                  ? "bg-[var(--accent-blue)] text-white"
                  : "text-[var(--text-secondary)] hover:text-white hover:bg-[var(--border)]"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
