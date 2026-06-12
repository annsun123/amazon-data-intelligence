interface TrendScoreProps {
  score: number;
  size?: "sm" | "md" | "lg";
}

function scoreColor(score: number): string {
  if (score >= 70) return "text-green-600 bg-green-50 border-green-200";
  if (score >= 40) return "text-yellow-600 bg-yellow-50 border-yellow-200";
  return "text-red-600 bg-red-50 border-red-200";
}

export default function TrendScore({ score, size = "md" }: TrendScoreProps) {
  const sizes = {
    sm: "text-sm px-2 py-0.5",
    md: "text-lg px-3 py-1",
    lg: "text-2xl px-4 py-2",
  };

  return (
    <span
      className={`${sizes[size]} font-bold rounded-lg border ${scoreColor(score)} inline-flex items-center gap-1`}
    >
      {score}
      <span className="text-xs font-normal">/100</span>
    </span>
  );
}
