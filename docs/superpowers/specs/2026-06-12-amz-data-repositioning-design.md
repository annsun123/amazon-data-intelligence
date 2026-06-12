# AMZ Data — Repositioning Design Spec

**Date:** 2026-06-12
**Status:** Approved
**Version:** 1.0

## 1. Project Identity

- **Name:** AMZ Data
- **Tagline:** "The data insights that really help Amazon Sellers."
- **Phase 1 Focus:** Pet Supplies category
- **Future Scope:** Expand to Home & Kitchen, Sports & Fitness, Baby, and beyond

## 2. Product Architecture

Three components, one brand:

```
amzdata.com
├── Blog / Research — 深度品类报告 + 每周趋势简报
├── Tools (Web) — Trend Scanner, Niche Compare, ASIN Deep Look
└── Chrome Extension — 浏览 Amazon 时实时叠加趋势信号
```

### 2.1 Blog / Research

Content types:
- **Monthly deep-dive report** — Complete analysis of one pet sub-niche (competitive landscape, growth trajectory, review gap analysis, opportunity scoring)
- **Weekly trend brief** — "Top 5 trending pet sub-niches this week" with signal data
- **Methodology explainers** — Open-source our analysis logic to build trust

### 2.2 Web Tools

| Tool | Function | Priority |
|------|----------|:--------:|
| Trend Scanner | Input keyword → trend score + signal breakdown | P0 |
| Niche Compare | Side-by-side comparison of 2-3 sub-niches | P2 |
| ASIN Deep Look | Multi-dimension data for a single ASIN | P2 |

### 2.3 Chrome Extension

- **Core:** TrendScore badge injected into Amazon pet product pages
- **Sidebar panel:** Google Trends overlay, TikTok mention velocity, Reddit discussion heat, competitive density estimate
- **Link:** One-click jump to full web analysis

## 3. Data Stack

| Source | What It Provides | Use |
|--------|-----------------|-----|
| Keepa API | BSR history, price history, Buy Box | Category trend baseline |
| Google Trends | Search volume trajectory | Leading indicator (1-3 weeks ahead of BSR) |
| Reddit API | r/dogs, r/cats, r/Pets discussions | Consumer pain points & demand signals |
| TikTok (scraper/3rd party) | Hashtag mention velocity | Viral product early warning |
| Amazon public data | Best Sellers, Movers & Shakers | Real-time validation |

**Data pipeline:** Python (Pandas/Polars) → Parquet (analysis) → Supabase/Postgres (web serving)

## 4. Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Web Frontend | Next.js + Tailwind CSS | Blog + Tools on same domain, SEO-friendly |
| Chrome Extension | Vanilla JS/TS, Manifest V3 | Lightweight, independent of web stack |
| Data Pipeline | Python (Pandas/Polars) | Existing skill set |
| Data Storage | Local Parquet → Supabase | Parquet for fast analysis, DB for web |
| Visualization | Plotly / Observable Plot | Interactive charts embedded in blog & tools |
| Deployment | Vercel (web) + Chrome Web Store (extension) | Minimal ops overhead |
| Task Scheduling | GitHub Actions or cron | Scheduled data refresh |

## 5. Build Sequence (MVP — 4 weeks)

### Week 1-2: Data Foundation
- Keepa API integration → pull Pet Supplies BSR/price history
- Google Trends + Reddit API integration
- Pipeline script → first parquet output
- Deliverable: First pet category deep-dive report (blog launch content)

### Week 2-3: Web Platform MVP
- Next.js project scaffold
- Blog module (MDX rendering + chart embedding)
- Trend Scanner tool v1 (keyword → trend chart)
- Deliverable: amzdata.com live with 1 report + 1 tool

### Week 3-4: Chrome Extension MVP
- Manifest V3 project
- Core: TrendScore badge injection on Amazon pet product pages
- Sidebar: Basic signal panel
- Deliverable: Submitted to Chrome Web Store

### Week 4+: Content Cadence + Iteration
- Weekly: 1 trend brief
- Biweekly: 1 tool iteration
- Monthly: 1 deep-dive category report

## 6. Content Strategy (Pet Supplies)

### First 3 Deep-Dive Reports (Months 1-3)
1. **Dog Food Sub-niche Map** — Premium vs budget, wet vs dry, breed-specific, trending ingredients
2. **Pet Tech Landscape** — Smart feeders, GPS trackers, pet cameras — growth trajectory analysis
3. **Cat Products Opportunity Scan** — Litter boxes, toys, furniture — under-served sub-niches

### Weekly Trend Brief Format
- 5 trending sub-niches with TrendScore
- 1 "Signal of the Week" deep zoom
- Data sources annotated for each signal

### Reddit Content Strategy
- Post methodology summaries ("How we analyze Amazon Pet Supplies trends")
- Post surprising findings ("We analyzed 10,000 pet product reviews and found...")
- Post data visualizations standalone (high shareability)

### GitHub Content Strategy
- Open-source data pipeline scripts
- Methodology documentation
- Sample datasets (anonymized)

## 7. Key Design Decisions

1. **Single category first.** Depth over breadth. Establish authority in Pet Supplies before expanding.
2. **Free content + tools as growth engine.** No paywall on MVP. Audience first, monetization later.
3. **Extension is a data flywheel.** User browsing behavior shows what niches are being actively researched — this is proprietary data no competitor has.
4. **Open methodology.** Publishing our analysis code builds trust and attracts technical audience (GitHub).
5. **TrendScore is the central metric.** A composite 0-100 score combining search momentum, social signals, competitive density, and review velocity — simple enough to understand at a glance, backed by rigorous data.

## 8. Success Metrics (3-month targets)

| Metric | Target |
|--------|--------|
| Blog posts published | 3 deep-dive + 12 weekly briefs |
| Web tools live | Trend Scanner v1 |
| Chrome Extension | Published on Chrome Web Store |
| Reddit | First post 50+ upvotes |
| GitHub stars | 20+ |
| Newsletter subscribers | 100+ |
| Community (Discord) | 50+ members |

## 9. What We Explicitly Defer

- Paid subscriptions / paywalls (Phase 2+)
- Multi-category expansion (after Pet Supplies authority established)
- Niche Compare and ASIN Deep Look tools (P2, after Trend Scanner)
- TikTok scraper (start with Google Trends + Reddit, add TikTok later)
- Community monetization (free Discord only in Phase 1)
