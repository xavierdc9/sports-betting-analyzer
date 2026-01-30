"use client";

import { useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import OddsTable from "@/components/OddsTable";
import type { Event, Sport } from "@/lib/types";
import { api } from "@/lib/api";

export default function OddsPage() {
  const [sports, setSports] = useState<Sport[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedSport, setSelectedSport] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getSports().then(setSports).catch(() => setSports([]));
  }, []);

  useEffect(() => {
    setLoading(true);
    api
      .getEvents(selectedSport || undefined)
      .then(setEvents)
      .catch(() => setEvents([]))
      .finally(() => setLoading(false));
  }, [selectedSport]);

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-1">Odds Comparison</h2>
            <p className="text-[var(--text-secondary)] text-sm">
              Compare odds across bookmakers
            </p>
          </div>
          <select
            value={selectedSport}
            onChange={(e) => setSelectedSport(e.target.value)}
            className="bg-[var(--bg-secondary)] border border-[var(--border)] rounded px-3 py-1 text-sm"
          >
            <option value="">All Sports</option>
            {sports.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-[var(--text-secondary)]">Loading...</div>
        ) : (
          <OddsTable events={events} />
        )}
      </main>
    </div>
  );
}
