"use client";

import { useEffect, useState } from "react";
import type { Alert } from "@/lib/types";
import { api } from "@/lib/api";

const TYPE_COLORS: Record<string, string> = {
  arbitrage: "bg-green-600",
  value_bet: "bg-blue-600",
  line_movement: "bg-yellow-600",
};

export default function AlertsPanel() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getAlerts()
      .then(setAlerts)
      .catch(() => setAlerts([]))
      .finally(() => setLoading(false));
  }, []);

  const handleMarkRead = async (id: string) => {
    await api.markAlertRead(id);
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, is_read: true } : a)));
  };

  if (loading) return <div className="text-[var(--text-secondary)]">Loading alerts...</div>;

  if (alerts.length === 0) {
    return (
      <div className="text-center text-[var(--text-secondary)] py-8">
        No alerts yet. Alerts appear when arbitrage or value bets are detected.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`p-3 rounded border border-[var(--border)] ${
            alert.is_read ? "opacity-60" : ""
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span
              className={`text-xs px-2 py-0.5 rounded ${
                TYPE_COLORS[alert.alert_type] || "bg-gray-600"
              }`}
            >
              {alert.alert_type.replace("_", " ")}
            </span>
            {!alert.is_read && (
              <button
                onClick={() => handleMarkRead(alert.id)}
                className="text-xs text-[var(--text-secondary)] hover:text-white"
              >
                Mark read
              </button>
            )}
          </div>
          <p className="text-sm">{alert.title}</p>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            {new Date(alert.created_at).toLocaleString()}
          </p>
        </div>
      ))}
    </div>
  );
}
