"use client";

import dynamic from "next/dynamic";
import { TrendResult } from "@/lib/data";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

interface TrendChartProps {
  results: TrendResult[];
}

export default function TrendChart({ results }: TrendChartProps) {
  const sorted = [...results].sort((a, b) => b.trend_score - a.trend_score);

  const data = [
    {
      type: "bar" as const,
      x: sorted.map((r) => r.keyword),
      y: sorted.map((r) => r.trend_score),
      marker: {
        color: sorted.map((r) =>
          r.trend_score >= 70
            ? "#16a34a"
            : r.trend_score >= 40
              ? "#ca8a04"
              : "#dc2626"
        ),
      },
      text: sorted.map((r) => `${r.trend_score}/100`),
      textposition: "outside" as const,
    },
  ];

  const layout = {
    title: "Pet Supplies TrendScores",
    yaxis: { title: "TrendScore", range: [0, 100] },
    xaxis: { tickangle: -30 },
    margin: { t: 40, b: 100 },
    height: 400,
  };

  return (
    <Plot data={data} layout={layout} style={{ width: "100%" }} />
  );
}
