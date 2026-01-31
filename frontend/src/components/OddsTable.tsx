"use client";

import { useEffect, useState } from "react";
import type { Event, OddsRecord } from "@/lib/types";
import { api, getErrorMessage } from "@/lib/api";
import ErrorBanner from "./ErrorBanner";

interface OddsTableProps {
  events: Event[];
}

interface GroupedOdds {
  [eventId: string]: OddsRecord[];
}

interface FailedEvents {
  [eventId: string]: string;
}

export default function OddsTable({ events }: OddsTableProps) {
  const [oddsByEvent, setOddsByEvent] = useState<GroupedOdds>({});
  const [failedEvents, setFailedEvents] = useState<FailedEvents>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (events.length === 0) {
      setLoading(false);
      return;
    }

    const displayed = events.slice(0, 10);

    Promise.all(
      displayed.map(async (event) => {
        try {
          const odds = await api.getOdds(event.id);
          return { eventId: event.id, odds, error: null };
        } catch (err) {
          return { eventId: event.id, odds: [], error: getErrorMessage(err) };
        }
      })
    ).then((results) => {
      const grouped: GroupedOdds = {};
      const failed: FailedEvents = {};
      for (const { eventId, odds, error } of results) {
        grouped[eventId] = odds;
        if (error) failed[eventId] = error;
      }
      setOddsByEvent(grouped);
      setFailedEvents(failed);
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

  // If ALL events failed, show a single error banner
  const displayedEvents = events.slice(0, 10);
  const allFailed =
    displayedEvents.length > 0 &&
    displayedEvents.every((e) => failedEvents[e.id]);

  if (allFailed) {
    const msg = Object.values(failedEvents)[0] || "Failed to load odds";
    return <ErrorBanner message={msg} />;
  }

  return (
    <div className="space-y-4">
      {displayedEvents.map((event) => {
        const odds = oddsByEvent[event.id] || [];
        const h2hOdds = odds.filter((o) => o.market_type === "h2h");
        const eventError = failedEvents[event.id];

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

            {eventError ? (
              <p className="text-xs text-red-400">
                Failed to load odds: {eventError}
              </p>
            ) : h2hOdds.length > 0 ? (
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
