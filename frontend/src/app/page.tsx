"use client";

import { useCallback, useEffect, useState } from "react";
import Sidebar from "@/components/Sidebar";
import AlertsPanel from "@/components/AlertsPanel";
import OddsTable from "@/components/OddsTable";
import ErrorBanner from "@/components/ErrorBanner";
import type { Event, Sport } from "@/lib/types";
import { api, getErrorMessage } from "@/lib/api";

export default function Dashboard() {
  const [sports, setSports] = useState<Sport[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedSport, setSelectedSport] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [sportsError, setSportsError] = useState<string | null>(null);
  const [eventsError, setEventsError] = useState<string | null>(null);

  const loadSports = useCallback(() => {
    setSportsError(null);
    api
      .getSports()
      .then(setSports)
      .catch((err) => {
        setSports([]);
        setSportsError(getErrorMessage(err));
      });
  }, []);

  const loadEvents = useCallback(() => {
    setEventsError(null);
    setLoading(true);
    api
      .getEvents(selectedSport || undefined)
      .then(setEvents)
      .catch((err) => {
        setEvents([]);
        setEventsError(getErrorMessage(err));
      })
      .finally(() => setLoading(false));
  }, [selectedSport]);

  useEffect(() => { loadSports(); }, [loadSports]);
  useEffect(() => { loadEvents(); }, [loadEvents]);

  const apiConnected = !sportsError && !eventsError;

  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-6">
        <div className="mb-6">
          <h2 className="text-2xl font-bold mb-1">Dashboard</h2>
          <p className="text-[var(--text-secondary)] text-sm">
            Real-time odds comparison and betting analysis
          </p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard label="Active Sports" value={sportsError ? "—" : sports.length} />
          <StatCard label="Upcoming Events" value={eventsError ? "—" : events.length} />
          <StatCard label="Markets Tracked" value="h2h, spreads, totals" isText />
          <StatCard
            label="API Status"
            value={apiConnected ? "Connected" : "Error"}
            isText
            variant={apiConnected ? "default" : "error"}
          />
        </div>

        {sportsError && (
          <div className="mb-4">
            <ErrorBanner message={`Sports: ${sportsError}`} onRetry={loadSports} />
          </div>
        )}

        <div className="grid grid-cols-3 gap-6">
          {/* Main odds section */}
          <div className="col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Upcoming Events</h3>
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

            {eventsError ? (
              <ErrorBanner message={eventsError} onRetry={loadEvents} />
            ) : loading ? (
              <div className="text-[var(--text-secondary)]">Loading events...</div>
            ) : (
              <OddsTable events={events} />
            )}
          </div>

          {/* Alerts sidebar */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
            <AlertsPanel />
          </div>
        </div>
      </main>
    </div>
  );
}

function StatCard({
  label,
  value,
  isText,
  variant = "default",
}: {
  label: string;
  value: number | string;
  isText?: boolean;
  variant?: "default" | "error";
}) {
  const borderClass =
    variant === "error"
      ? "border-red-700/50"
      : "border-[var(--border)]";
  const valueClass =
    variant === "error" ? "text-red-400" : "";

  return (
    <div className={`bg-[var(--bg-card)] border ${borderClass} rounded p-4`}>
      <p className="text-xs text-[var(--text-secondary)] mb-1">{label}</p>
      <p className={`${isText ? "text-sm" : "text-2xl"} font-bold ${valueClass}`}>
        {value}
      </p>
    </div>
  );
}
