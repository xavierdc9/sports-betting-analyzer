import type { Alert, Event, OddsRecord, PolymarketMarket, Sport } from "./types";

const BASE = "";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function fetchJson<T>(url: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE}${url}`, { cache: "no-store" });
  } catch {
    throw new ApiError(0, "Network error — unable to reach the server");
  }

  if (res.status === 429) {
    throw new ApiError(429, "Rate limit exceeded — please wait a moment");
  }

  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(
      res.status,
      body || `Server error (${res.status})`
    );
  }

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
  markAlertRead: async (alertId: string) => {
    let res: Response;
    try {
      res = await fetch(`/api/alerts/${alertId}/read`, { method: "PATCH" });
    } catch {
      throw new ApiError(0, "Network error — unable to reach the server");
    }
    if (!res.ok) {
      throw new ApiError(res.status, `Failed to mark alert read (${res.status})`);
    }
  },
  getPolymarkets: (category?: string) => {
    const params = category ? `?category=${category}` : "";
    return fetchJson<PolymarketMarket[]>(`/api/polymarket/markets${params}`);
  },
};

/** Extract a user-friendly message from any caught error. */
export function getErrorMessage(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "An unexpected error occurred";
}
