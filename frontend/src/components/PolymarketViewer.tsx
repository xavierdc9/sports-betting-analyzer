"use client";

import { useEffect, useState } from "react";
import type { PolymarketMarket } from "@/lib/types";
import { api } from "@/lib/api";

export default function PolymarketViewer() {
  const [markets, setMarkets] = useState<PolymarketMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string>("");

  useEffect(() => {
    setLoading(true);
    api
      .getPolymarkets(category || undefined)
      .then(setMarkets)
      .catch(() => setMarkets([]))
      .finally(() => setLoading(false));
  }, [category]);

  const categories = ["", "NFL", "NBA", "MLB"];

  return (
    <div>
      <div className="flex gap-2 mb-4">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              category === cat
                ? "bg-[var(--accent-blue)] text-white"
                : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] hover:text-white"
            }`}
          >
            {cat || "All"}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-[var(--text-secondary)]">Loading markets...</div>
      ) : markets.length === 0 ? (
        <div className="text-center text-[var(--text-secondary)] py-8">
          No prediction markets found.
        </div>
      ) : (
        <div className="space-y-4">
          {markets.map((market) => (
            <div
              key={market.id}
              className="bg-[var(--bg-card)] border border-[var(--border)] rounded p-4"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <p className="font-medium">{market.question}</p>
                  <p className="text-xs text-[var(--text-secondary)] mt-1">
                    <span className="bg-[var(--border)] px-2 py-0.5 rounded mr-2">
                      {market.category}
                    </span>
                    Volume: $
                    {parseInt(market.total_volume).toLocaleString()}
                  </p>
                </div>
                <span className="text-xs text-[var(--text-secondary)]">
                  Ends {new Date(market.end_date).toLocaleDateString()}
                </span>
              </div>

              <div className="space-y-2">
                {market.outcomes.map((outcome, i) => {
                  const pct = (parseFloat(outcome.price) * 100).toFixed(0);
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="flex justify-between text-sm mb-1">
                          <span>{outcome.name}</span>
                          <span className="font-mono">{pct}%</span>
                        </div>
                        <div className="w-full bg-[var(--border)] rounded-full h-2">
                          <div
                            className="bg-[var(--accent-blue)] h-2 rounded-full transition-all"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
