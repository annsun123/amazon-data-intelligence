export interface TrendResult {
  keyword: string;
  trend_score: number;
  components: {
    bsr_momentum: number;
    google_trends: number;
    reddit_signal: number;
    velocity: number;
  };
  data_quality: "good" | "partial" | "insufficient";
}

export interface TrendData {
  generated_at: string;
  scores: TrendResult[];
}

export async function loadTrendData(): Promise<TrendData> {
  const res = await fetch("/data/pet_supplies_trend_scores.json");
  if (!res.ok) {
    return { generated_at: "", scores: [] };
  }
  return res.json();
}
