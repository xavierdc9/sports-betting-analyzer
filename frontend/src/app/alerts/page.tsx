"use client";

import Sidebar from "@/components/Sidebar";
import AlertsPanel from "@/components/AlertsPanel";

export default function AlertsPage() {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-1">Alerts</h2>
          <p className="text-[var(--text-secondary)] text-sm">
            Arbitrage opportunities, value bets, and line movement notifications
          </p>
        </div>
        <div className="max-w-2xl">
          <AlertsPanel />
        </div>
      </main>
    </div>
  );
}
