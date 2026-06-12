"use client";

import { useState } from "react";
import TrendScore from "@/components/TrendScore";
import TrendChart from "@/components/TrendChart";
import { TrendResult } from "@/lib/data";

const SAMPLE_RESULTS: TrendResult[] = [
  {
    keyword: "grain free dog food",
    trend_score: 87,
    components: {
      bsr_momentum: 82,
      google_trends: 90,
      reddit_signal: 85,
      velocity: 88,
    },
    data_quality: "good",
  },
  {
    keyword: "smart pet feeder",
    trend_score: 82,
    components: {
      bsr_momentum: 78,
      google_trends: 85,
      reddit_signal: 80,
      velocity: 75,
    },
    data_quality: "good",
  },
  {
    keyword: "cat enrichment toys",
    trend_score: 78,
    components: {
      bsr_momentum: 72,
      google_trends: 80,
      reddit_signal: 75,
      velocity: 82,
    },
    data_quality: "good",
  },
  {
    keyword: "eco friendly dog toys",
    trend_score: 74,
    components: {
      bsr_momentum: 68,
      google_trends: 78,
      reddit_signal: 70,
      velocity: 72,
    },
    data_quality: "partial",
  },
  {
    keyword: "pet camera monitor",
    trend_score: 71,
    components: {
      bsr_momentum: 70,
      google_trends: 72,
      reddit_signal: 75,
      velocity: 60,
    },
    data_quality: "good",
  },
  {
    keyword: "automatic cat litter box",
    trend_score: 65,
    components: {
      bsr_momentum: 62,
      google_trends: 70,
      reddit_signal: 60,
      velocity: 68,
    },
    data_quality: "partial",
  },
  {
    keyword: "dog puzzle toys",
    trend_score: 62,
    components: {
      bsr_momentum: 58,
      google_trends: 65,
      reddit_signal: 68,
      velocity: 55,
    },
    data_quality: "partial",
  },
  {
    keyword: "organic cat treats",
    trend_score: 58,
    components: {
      bsr_momentum: 55,
      google_trends: 60,
      reddit_signal: 52,
      velocity: 62,
    },
    data_quality: "partial",
  },
];

export default function TrendScannerPage() {
  const [keyword, setKeyword] = useState("");
  const [results, setResults] = useState<TrendResult[]>(SAMPLE_RESULTS);
  const [searching, setSearching] = useState(false);

  function handleSearch() {
    if (!keyword.trim()) return;
    setSearching(true);
    setTimeout(() => {
      const filtered = SAMPLE_RESULTS.filter((r) =>
        r.keyword.toLowerCase().includes(keyword.toLowerCase())
      );
      setResults(filtered.length > 0 ? filtered : SAMPLE_RESULTS);
      setSearching(false);
    }, 500);
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Trend Scanner</h1>
        <p className="text-gray-500 mt-1">
          Analyze trend signals for any pet sub-niche.
        </p>
      </div>

      {/* Search bar */}
      <div className="flex gap-3">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="e.g., dog treats, cat fountain, pet camera..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          onClick={handleSearch}
          disabled={searching}
          className="px-6 py-2 bg-brand-500 text-white rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {searching ? "Scanning..." : "Scan"}
        </button>
      </div>

      {/* Results table */}
      <div>
        <h2 className="text-xl font-semibold mb-4">TrendScores</h2>
        <div className="border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">
                  Keyword
                </th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">
                  TrendScore
                </th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">
                  Search
                </th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">
                  Reddit
                </th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">
                  BSR
                </th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">
                  Quality
                </th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr
                  key={r.keyword}
                  className="border-t border-gray-100 hover:bg-gray-50"
                >
                  <td className="px-4 py-3 font-medium capitalize">
                    {r.keyword}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <TrendScore score={r.trend_score} size="sm" />
                  </td>
                  <td className="px-4 py-3 text-center">
                    {r.components.google_trends}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {r.components.reddit_signal}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {r.components.bsr_momentum}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${
                        r.data_quality === "good"
                          ? "bg-green-100 text-green-700"
                          : r.data_quality === "partial"
                            ? "bg-yellow-100 text-yellow-700"
                            : "bg-red-100 text-red-700"
                      }`}
                    >
                      {r.data_quality}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Chart */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Trend Overview</h2>
        <TrendChart results={results} />
      </div>
    </div>
  );
}
