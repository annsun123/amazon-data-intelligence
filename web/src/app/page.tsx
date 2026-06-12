import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="text-center py-16">
        <h1 className="text-4xl font-bold text-brand-900 mb-4">
          Pet Supplies Data Intelligence
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-8">
          Cross-platform trend signals for Amazon Pet Supplies sellers. Spot
          what&apos;s trending before it peaks — using Google Trends, Reddit
          signals, and marketplace data.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/tools/trend-scanner"
            className="px-6 py-3 bg-brand-500 text-white rounded-lg font-medium hover:bg-brand-700"
          >
            Try Trend Scanner →
          </Link>
          <Link
            href="/blog"
            className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:border-brand-500 text-gray-700"
          >
            Read Research
          </Link>
        </div>
      </section>

      {/* Three value props */}
      <section className="grid md:grid-cols-3 gap-8">
        {[
          {
            title: "Trend Signals",
            desc: "Google Trends + Reddit + BSR data combined into a single TrendScore.",
            icon: "📊",
          },
          {
            title: "Pet-First Research",
            desc: "Deep analysis of pet sub-niches: dog food, cat litter, pet tech, and more.",
            icon: "🐾",
          },
          {
            title: "Free Tools",
            desc: "Chrome extension overlays trend data on Amazon product pages. Web tools for deep dives.",
            icon: "🛠️",
          },
        ].map((item) => (
          <div
            key={item.title}
            className="p-6 border border-gray-200 rounded-xl"
          >
            <div className="text-3xl mb-3">{item.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
            <p className="text-gray-500 text-sm">{item.desc}</p>
          </div>
        ))}
      </section>

      {/* Latest */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Latest Research</h2>
        <div className="border border-gray-200 rounded-xl p-6">
          <span className="text-xs text-brand-500 font-medium">
            June 2026 · Deep Dive
          </span>
          <h3 className="text-xl font-semibold mt-1 mb-2">
            Pet Supplies Market Landscape: Where the Growth Is
          </h3>
          <p className="text-gray-500 mb-4">
            We analyzed 20+ pet sub-categories across search trends, BSR
            momentum, and Reddit discussion volume. Here are the 5
            highest-signal opportunities.
          </p>
          <Link
            href="/blog/pet-supplies-landscape"
            className="text-brand-500 font-medium hover:underline"
          >
            Read full report →
          </Link>
        </div>
      </section>
    </div>
  );
}
