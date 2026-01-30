export interface Sport {
  id: string;
  key: string;
  title: string;
  active: boolean;
  created_at: string;
}

export interface Event {
  id: string;
  external_id: string;
  sport_id: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface OddsRecord {
  id: string;
  event_id: string;
  bookmaker_id: string;
  market_type: string;
  outcome_name: string;
  price: string;
  point: string | null;
  scraped_at: string;
}

export interface Alert {
  id: string;
  alert_type: "arbitrage" | "value_bet" | "line_movement";
  event_id: string;
  title: string;
  details: Record<string, unknown> | null;
  is_read: boolean;
  created_at: string;
}

export interface Bookmaker {
  id: string;
  key: string;
  name: string;
  is_exchange: boolean;
  active: boolean;
}

export interface PolymarketOutcome {
  name: string;
  price: string;
  volume: string;
}

export interface PolymarketMarket {
  id: string;
  question: string;
  category: string;
  end_date: string;
  active: boolean;
  total_volume: string;
  outcomes: PolymarketOutcome[];
  source: string;
  url: string | null;
}
