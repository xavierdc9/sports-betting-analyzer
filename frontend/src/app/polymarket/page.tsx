"use client";

import Sidebar from "@/components/Sidebar";
import PolymarketViewer from "@/components/PolymarketViewer";

export default function PolymarketPage() {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-1">Prediction Markets</h2>
          <p className="text-[var(--text-secondary)] text-sm">
            Polymarket sports prediction markets (mock data)
          </p>
        </div>
        <PolymarketViewer />
      </main>
    </div>
  );
}
