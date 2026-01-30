"use client";

import { useEffect, useState } from "react";
import type { Event, OddsRecord } from "@/lib/types";
import { api } from "@/lib/api";

interface OddsTableProps {
  events: Event[];
}

interface GroupedOdds {
  [eventId: string]: OddsRecord[];
}

export default function OddsTable({ events }: OddsTableProps) {
  const [oddsByEvent, setOddsByEvent] = useState<GroupedOdds>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (events.length === 0) {
      setLoading(false);
      return;
    }

    Promise.all(
      events.slice(0, 10).map(async (event) => {
        try {
          const odds = await api.getOdds(event.id);
          return { eventId: event.id, odds };
        } catch {
          return { eventId: event.id, odds: [] };
        }
      })
    ).then((results) => {
      const grouped: GroupedOdds = {};
      for (const { eventId, odds } of results) {
        grouped[eventId] = odds;
      }
      setOddsByEvent(grouped);
      setLoading(false);
    });
  }, [events]);

  if (loading) return <div className="text-[var(--text-secondary)]">Loading odds...</div>;

  if (events.length === 0) {
    return (
      <div className="text-center text-[var(--text-secondary)] py-8">
        No upcoming events found.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {events.slice(0, 10).map((event) => {
        const odds = oddsByEvent[event.id] || [];
        const h2hOdds = odds.filter((o) => o.market_type === "h2h");

        return (
          <div
            key={event.id}
            className="bg-[var(--bg-card)] border border-[var(--border)] rounded p-4"
          >
            <div className="flex justify-between items-center mb-3">
              <div>
                <p className="font-medium">
                  {event.away_team} @ {event.home_team}
                </p>
                <p className="text-xs text-[var(--text-secondary)]">
                  {new Date(event.commence_time).toLocaleString()}
                </p>
              </div>
            </div>

            {h2hOdds.length > 0 ? (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[var(--text-secondary)] text-xs">
                    <th className="text-left py-1">Outcome</th>
                    <th className="text-right py-1">Odds</th>
                    <th className="text-right py-1">Implied %</th>
                  </tr>
                </thead>
                <tbody>
                  {h2hOdds.map((o) => {
                    const price = parseFloat(o.price);
                    const implied = ((1 / price) * 100).toFixed(1);
                    return (
                      <tr key={o.id} className="border-t border-[var(--border)]">
                        <td className="py-1">{o.outcome_name}</td>
                        <td className="text-right font-mono">{price.toFixed(2)}</td>
                        <td className="text-right text-[var(--text-secondary)]">
                          {implied}%
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            ) : (
              <p className="text-xs text-[var(--text-secondary)]">No odds available</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
