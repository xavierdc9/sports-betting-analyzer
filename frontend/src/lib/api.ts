import type { Alert, Event, OddsRecord, PolymarketMarket, Sport } from "./types";

const BASE = "";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  getSports: () => fetchJson<Sport[]>("/api/sports?active_only=true"),
  getEvents: (sportId?: string) => {
    const params = new URLSearchParams();
    if (sportId) params.set("sport_id", sportId);
    params.set("completed", "false");
    params.set("limit", "50");
    return fetchJson<Event[]>(`/api/events?${params}`);
  },
  getOdds: (eventId: string) =>
    fetchJson<OddsRecord[]>(`/api/odds?event_id=${eventId}&limit=200`),
  getOddsHistory: (eventId: string) =>
    fetchJson<OddsRecord[]>(`/api/odds/event/${eventId}/history`),
  getAlerts: (unreadOnly = false) =>
    fetchJson<Alert[]>(`/api/alerts?unread_only=${unreadOnly}&limit=50`),
  markAlertRead: (alertId: string) =>
    fetch(`/api/alerts/${alertId}/read`, { method: "PATCH" }),
  getPolymarkets: (category?: string) => {
    const params = category ? `?category=${category}` : "";
    return fetchJson<PolymarketMarket[]>(`/api/polymarket/markets${params}`);
  },
};
