import Link from "next/link";

const tools = [
  {
    slug: "trend-scanner",
    title: "Trend Scanner",
    desc: "Input a pet sub-niche keyword and get a composite TrendScore with signal breakdown.",
    status: "live",
  },
  {
    slug: "niche-compare",
    title: "Niche Compare",
    desc: "Compare trend data across multiple pet sub-niches side by side.",
    status: "coming-soon",
  },
  {
    slug: "asin-deep-look",
    title: "ASIN Deep Look",
    desc: "Multi-dimension analysis for a single ASIN: BSR history, price trends, competitive signals.",
    status: "coming-soon",
  },
];

export default function ToolsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Tools</h1>
      <p className="text-gray-500">Free tools for Amazon Pet Supplies sellers.</p>
      <div className="grid gap-4 mt-8">
        {tools.map((tool) => (
          <div
            key={tool.slug}
            className="border border-gray-200 rounded-xl p-6 flex justify-between items-center"
          >
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">{tool.title}</h3>
                {tool.status === "coming-soon" && (
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">
                    Soon
                  </span>
                )}
              </div>
              <p className="text-gray-500 text-sm mt-1">{tool.desc}</p>
            </div>
            {tool.status === "live" ? (
              <Link
                href={`/tools/${tool.slug}`}
                className="px-4 py-2 bg-brand-500 text-white rounded-lg text-sm font-medium hover:bg-brand-700 shrink-0"
              >
                Open →
              </Link>
            ) : (
              <span className="px-4 py-2 bg-gray-100 text-gray-400 rounded-lg text-sm shrink-0 cursor-not-allowed">
                Coming Soon
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
