# Amazon Data Intelligence · 亚马逊数据洞察

**用数据回答 Amazon 卖家每天都在问的问题。**
**Data-driven answers to the questions Amazon sellers ask every day.**

我爬取真实的 Amazon 数据，用统计学方法做分析，然后把完整的分析过程——数据、代码、图表、结论——全部开源在这里。
I scrape real Amazon data, analyze it with statistical methods, and open-source the entire process — data, code, charts, and conclusions.

---

## 这里有什么 · What's Here

每篇分析 = 一个问题 + 一套数据 + 一套统计方法 + 一个可复现的 notebook + 一份说人话的结论。
Each analysis = one question + one dataset + one statistical approach + one reproducible notebook + one plain-language conclusion.

| # | 分析 Analysis | 日期 Date | 核心发现 Key Finding |
|---|-------------|-----------|---------------------|
| 001 | [**The Review Moat**](analyses/001-review-moat/) — 你需要多少评论才能在 Amazon 上竞争？How many reviews do you need to compete? | 2026.06 | 10 个品类中，有 3 个品类的评论数和排名无关；Amazon 存在"双层级"竞争结构 · Reviews don't predict rank in 3/10 categories; Amazon has a "Two-Tier" competitive structure |
| 002 | *Coming soon · 即将更新* | — | — |

---

## 为什么要做这个 · Why I Built This

市面上有大量的 Amazon 选品工具（Helium 10、Jungle Scout、SellerSprite 等），它们能告诉你**数据是什么**，但很少回答**数据意味着什么**。

比如：工具能告诉你某个竞品有多少条评论，但不会告诉你：
- 评论数和 BSR 排名的统计关系是什么？
- 多少评论才算"够了"？
- 有没有品类是评论数根本不重要的？

这些问题需要统计分析才能回答。而我恰好会。

There are plenty of Amazon seller tools out there. They show you **what the data is**, but rarely tell you **what the data means**. They'll show you how many reviews a competitor has. They won't tell you whether review count actually predicts rank in that category, or how many reviews are "enough." That requires statistical analysis — which is what I do here.

---

## 分析方法 · My Process

每篇分析都走同一个流程。Every analysis follows the same pipeline:

```
选题研究 → 方法论设计 → 数据采集 → 统计分析 → 质量审查 → 成文发布
Research → Methodology → Data Pipeline → Analysis → Review → Write-up
```

| 阶段 Phase | 做什么 What Happens |
|------------|---------------------|
| **选题 Research** | 从 Reddit / LinkedIn 的卖家社区里找大家真正关心的问题 · Find questions sellers actually care about |
| **方法论 Methodology** | 设计统计方案：用什么检验？检验什么假设？需要什么数据？· Design the statistical approach |
| **数据采集 Data Pipeline** | 写爬虫，从 Amazon 页面直接抓数据 · Scrape real Amazon data |
| **分析 Analysis** | 探索性分析 → 统计检验 → 可视化 → 找"反直觉"的发现 · EDA → tests → visualization → find surprises |
| **审查 Review** | 逐条验证数据声明，审计统计方法，评估表达质量 · Verify every claim, audit the stats |
| **成文 Write-up** | Notebook + 图表 + 说人话的结论，兼顾技术严谨和可读性 · Notebook + charts + plain-language conclusions |

---

## 技术栈 · Tech Stack

```
Python · pandas · scipy · statsmodels · scikit-learn
matplotlib · seaborn · Jupyter Notebook
BeautifulSoup (scraping · 爬虫) · Plotly (interactive charts · 交互图表)
```

---

## 目录结构 · Repo Structure

```
amazon-data-intelligence/
├── README.md                    ← 你在这里 · You are here
├── analyses/
│   ├── 001-review-moat/         ← 分析 001：Review Moat
│   │   ├── README.md            ← 这篇分析的摘要（建议先看）· Start here
│   │   ├── review_moat_analysis.ipynb
│   │   ├── dashboard.html
│   │   └── charts/
│   ├── 002-xxx/                 ← 下一篇… Next…
│   └── ...
├── data/
└── methodology/
```

---

## 关于我 · About Me

数据分析从业者，正在系统性地积累电商市场分析、统计建模和数据叙事的能力。

这个仓库的每篇分析都记录了我当时是怎么思考的、用了什么方法、踩了什么坑。

如果你也在做类似的事情，或者对某篇分析有建议，欢迎提 Issue 或者直接联系我。

Data professional building hands-on expertise in marketplace analytics, statistical modeling, and data storytelling. 

This repo's each analysis captures how I thought about the problem, what methods I chose, and what I learned along the way. If you're working on similar things or have feedback, feel free to open an Issue or reach out.

---

*始于 2026 年 6 月 · 持续更新中 · Started June 2026. Updated as I learn.*
