import { NextRequest, NextResponse } from "next/server";

const SAMPLE_SCORES = [
  {
    keyword: "grain free dog food",
    trend_score: 87,
    components: { bsr_momentum: 82, google_trends: 90, reddit_signal: 85, velocity: 88 },
    data_quality: "good",
  },
  {
    keyword: "smart pet feeder",
    trend_score: 82,
    components: { bsr_momentum: 78, google_trends: 85, reddit_signal: 80, velocity: 75 },
    data_quality: "good",
  },
  {
    keyword: "cat enrichment toys",
    trend_score: 78,
    components: { bsr_momentum: 72, google_trends: 80, reddit_signal: 75, velocity: 82 },
    data_quality: "good",
  },
  {
    keyword: "eco friendly dog toys",
    trend_score: 74,
    components: { bsr_momentum: 68, google_trends: 78, reddit_signal: 70, velocity: 72 },
    data_quality: "partial",
  },
  {
    keyword: "pet camera monitor",
    trend_score: 71,
    components: { bsr_momentum: 70, google_trends: 72, reddit_signal: 75, velocity: 60 },
    data_quality: "good",
  },
];

export const dynamic = "force-static";

export async function GET(request: NextRequest) {
  const keyword = request.nextUrl.searchParams.get("keyword");

  if (keyword) {
    const filtered = SAMPLE_SCORES.filter((s) =>
      s.keyword.toLowerCase().includes(keyword.toLowerCase())
    );
    return NextResponse.json({
      scores: filtered,
      generated_at: new Date().toISOString(),
    });
  }

  return NextResponse.json({
    scores: SAMPLE_SCORES,
    generated_at: new Date().toISOString(),
  });
}
