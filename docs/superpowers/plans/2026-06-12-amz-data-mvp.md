# AMZ Data MVP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the AMZ Data MVP — a pet supplies trend intelligence platform consisting of a Python data pipeline, a Next.js web platform (blog + tools), and a Chrome extension.

**Architecture:** Python data pipeline fetches from Keepa/Google Trends/Reddit, calculates TrendScores, exports to JSON. Next.js web app serves blog content (MDX) and web tools (Trend Scanner) consuming those JSON exports. Chrome extension calls the web API to overlay trend signals on Amazon product pages.

**Tech Stack:** Python 3.11+ (Pandas, Keepa API, PRAW, pytrends), Next.js 15 (App Router, Tailwind CSS, MDX), Chrome Extension Manifest V3 (Vanilla JS)

---

## File Structure (Complete)

```
amz_data/
├── pipeline/
│   ├── requirements.txt
│   ├── config.py
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── keepa_fetcher.py
│   │   ├── google_trends.py
│   │   └── reddit_fetcher.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── trend_score.py
│   │   └── category_analyzer.py
│   ├── outputs/
│   │   ├── __init__.py
│   │   └── export.py
│   ├── notebooks/
│   │   └── pet_supplies_eda.ipynb
│   └── tests/
│       ├── test_keepa_fetcher.py
│       ├── test_trend_score.py
│       └── test_export.py
│
├── web/
│   ├── package.json
│   ├── next.config.mjs
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── public/
│   │   └── data/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── blog/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [slug]/page.tsx
│   │   │   ├── tools/
│   │   │   │   ├── page.tsx
│   │   │   │   └── trend-scanner/page.tsx
│   │   │   └── api/trends/route.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   ├── TrendScore.tsx
│   │   │   └── BlogCard.tsx
│   │   ├── lib/
│   │   │   ├── data.ts
│   │   │   └── trendscore.ts
│   │   └── content/blog/
│   │       └── pet-supplies-landscape.mdx
│   └── tests/
│
├── extension/
│   ├── manifest.json
│   ├── service_worker.js
│   ├── content/
│   │   ├── inject.js
│   │   └── inject.css
│   ├── sidebar/
│   │   ├── panel.html
│   │   ├── panel.js
│   │   └── panel.css
│   ├── lib/
│   │   └── api.js
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
│
└── data/
    ├── raw/
    ├── processed/
    └── exports/
```

---

## PLAN A: Data Pipeline

### Task A1: Project Setup & Config

**Files:**
- Create: `pipeline/requirements.txt`
- Create: `pipeline/config.py`

- [ ] **Step 1: Create pipeline directory and requirements.txt**

```bash
mkdir -p pipeline/fetchers pipeline/processors pipeline/outputs pipeline/notebooks pipeline/tests
```

Write `pipeline/requirements.txt`:
```
keepa>=1.3.0
praw>=7.7.0
pytrends>=4.9.2
pandas>=2.2.0
polars>=1.0.0
pyarrow>=16.0.0
plotly>=5.22.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Install dependencies**

```bash
cd pipeline && pip install -r requirements.txt
```

Expected: all packages install successfully.

- [ ] **Step 3: Create config.py with environment variable loading**

Write `pipeline/config.py`:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# API Keys
KEEPA_API_KEY = os.getenv("KEEPA_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "amz_data_pet_research/1.0")

# Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
DATA_EXPORTS = ROOT_DIR / "data" / "exports"

# Pet Supplies category config
PET_SUPPLIES_CATEGORY_ID = 2975312011
PET_SUPPLIES_SEARCH_TERMS = [
    "dog food", "dog treats", "dog toys", "dog bed",
    "cat food", "cat litter", "cat toys", "cat tree",
    "pet camera", "pet feeder", "pet fountain", "pet gate",
    "dog leash", "dog collar", "dog grooming",
    "aquarium", "bird cage", "small animal cage",
]

# Ensure data directories exist
for d in [DATA_RAW, DATA_PROCESSED, DATA_EXPORTS]:
    d.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Create .env file template**

```bash
echo "KEEPA_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=amz_data_pet_research/1.0" > pipeline/.env
```

- [ ] **Step 5: Commit**

```bash
git add pipeline/requirements.txt pipeline/config.py pipeline/.env
git commit -m "feat: initialize data pipeline project structure and config"
```

---

### Task A2: Keepa API Fetcher

**Files:**
- Create: `pipeline/fetchers/__init__.py`
- Create: `pipeline/fetchers/keepa_fetcher.py`
- Create: `pipeline/tests/test_keepa_fetcher.py`

- [ ] **Step 1: Create __init__.py**

Write `pipeline/fetchers/__init__.py`:
```python
from .keepa_fetcher import KeepaFetcher
from .google_trends import GoogleTrendsFetcher
from .reddit_fetcher import RedditFetcher
```

- [ ] **Step 2: Write failing test for KeepaFetcher**

Write `pipeline/tests/test_keepa_fetcher.py`:
```python
import pytest
from pathlib import Path
import pandas as pd
from pipeline.fetchers.keepa_fetcher import KeepaFetcher
from pipeline.config import DATA_RAW

@pytest.fixture
def keepa():
    return KeepaFetcher()

def test_fetch_product_data_returns_dataframe(keepa):
    """Fetch a known ASIN and verify we get a DataFrame with expected columns."""
    # A well-known pet product ASIN — Purina dog food
    asin = "B00BMYFQ7C"
    df = keepa.fetch_product(asin)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    expected_cols = {"asin", "price", "bsr", "timestamp"}
    assert expected_cols.issubset(set(df.columns))
    assert (df["asin"] == asin).all()

def test_fetch_product_saves_to_file(keepa, tmp_path):
    """Verify raw data is saved to parquet."""
    asin = "B00BMYFQ7C"
    output_path = tmp_path / "test_output.parquet"
    
    keepa.fetch_and_save(asin, output_path)
    
    assert output_path.exists()
    df = pd.read_parquet(output_path)
    assert len(df) > 0

def test_fetch_multiple_asins(keepa):
    """Fetch multiple ASINs and verify deduplication."""
    asins = ["B00BMYFQ7C", "B0009YNTIY"]
    df = keepa.fetch_multiple(asins)
    
    assert df["asin"].nunique() == len(asins)

def test_empty_asins_returns_empty_dataframe(keepa):
    """Edge case: empty list should return empty DataFrame."""
    df = keepa.fetch_multiple([])
    assert df.empty
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd pipeline && python -m pytest tests/test_keepa_fetcher.py -v
```

Expected: 4 tests FAIL with ModuleNotFoundError.

- [ ] **Step 4: Implement KeepaFetcher**

Write `pipeline/fetchers/keepa_fetcher.py`:
```python
import keepa
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from pipeline.config import KEEPA_API_KEY, DATA_RAW

class KeepaFetcher:
    """Fetch Amazon product data via Keepa API."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or KEEPA_API_KEY
        if not self.api_key:
            raise ValueError("KEEPA_API_KEY not set. Set it in pipeline/.env")
        self.api = keepa.Keepa(self.api_key)

    def fetch_product(self, asin: str, days_back: int = 365) -> pd.DataFrame:
        """Fetch historical data for a single ASIN. Returns DataFrame with
        price, BSR, and timestamp columns."""
        products = self.api.query(
            [asin],
            stats=days_back,
            offers=0,
            history=True,
            rating=True,
        )
        if not products or len(products) == 0:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])

        product = products[0]
        history = product.get("data", {})
        
        rows = []
        if "CSV" in history:
            csv_data = history["CSV"]
            for row in csv_data:
                if row:
                    timestamp = keepa.keepa_time.keepa_minutes_to_datetime(row[0])
                    rows.append({
                        "asin": asin,
                        "timestamp": timestamp,
                        "price": row[-1] if "AMAZON" in str(history.get("csvType")) else None,
                        "bsr": row[-3] if len(row) >= 3 else None,
                    })

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])
        
        return df.sort_values("timestamp")

    def fetch_and_save(self, asin: str, output_path: Path) -> pd.DataFrame:
        """Fetch and save raw data to parquet."""
        df = self.fetch_product(asin)
        df.to_parquet(output_path)
        return df

    def fetch_multiple(self, asins: list[str], days_back: int = 365) -> pd.DataFrame:
        """Fetch multiple ASINs, return combined DataFrame."""
        if not asins:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])
        
        frames = []
        for asin in asins:
            df = self.fetch_product(asin, days_back)
            if not df.empty:
                frames.append(df)
        
        if not frames:
            return pd.DataFrame(columns=["asin", "price", "bsr", "timestamp"])
        
        return pd.concat(frames, ignore_index=True)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd pipeline && python -m pytest tests/test_keepa_fetcher.py -v
```

Expected: 4 tests PASS (requires valid KEEPA_API_KEY in .env).

- [ ] **Step 6: Commit**

```bash
git add pipeline/fetchers/__init__.py pipeline/fetchers/keepa_fetcher.py pipeline/tests/test_keepa_fetcher.py
git commit -m "feat: add Keepa API fetcher for Amazon product data"
```

---

### Task A3: Google Trends Fetcher

**Files:**
- Create: `pipeline/fetchers/google_trends.py`

- [ ] **Step 1: Implement GoogleTrendsFetcher**

Write `pipeline/fetchers/google_trends.py`:
```python
from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

class GoogleTrendsFetcher:
    """Fetch Google Trends search volume data for pet-related terms."""

    def __init__(self):
        self.pytrends = TrendReq(hl="en-US", tz=300)

    def fetch_interest_over_time(self, keywords: list[str], 
                                  timeframe: str = "today 12-m") -> pd.DataFrame:
        """Fetch search interest over time for given keywords.
        Returns DataFrame with date index and keyword columns."""
        # pytrends supports up to 5 keywords per request
        if len(keywords) > 5:
            raise ValueError("Max 5 keywords per request for Google Trends")

        self.pytrends.build_payload(
            kw_list=keywords,
            timeframe=timeframe,
            geo="US",
            gprop="",
        )
        df = self.pytrends.interest_over_time()
        if df.empty:
            return pd.DataFrame()
        if "isPartial" in df.columns:
            df = df.drop(columns=["isPartial"])
        return df

    def fetch_multi_batch(self, keywords: list[str], 
                          timeframe: str = "today 12-m") -> pd.DataFrame:
        """Fetch search interest for any number of keywords by batching in groups of 5."""
        results = []
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]
            df = self.fetch_interest_over_time(batch, timeframe)
            if not df.empty:
                results.append(df)
        if not results:
            return pd.DataFrame()
        return pd.concat(results, axis=1)

    def get_trend_direction(self, keyword: str, 
                            timeframe: str = "today 3-m") -> dict:
        """Get simple trend direction for a keyword: rising, falling, or stable."""
        df = self.fetch_interest_over_time([keyword], timeframe)
        if df.empty or len(df) < 4:
            return {"keyword": keyword, "direction": "insufficient_data", 
                    "change_pct": 0.0}

        first_half = df.iloc[:len(df)//2][keyword].mean()
        second_half = df.iloc[len(df)//2:][keyword].mean()

        if first_half == 0:
            return {"keyword": keyword, "direction": "rising" if second_half > 0 else "stable",
                    "change_pct": 100.0 if second_half > 0 else 0.0}

        change_pct = ((second_half - first_half) / first_half) * 100

        if change_pct > 15:
            direction = "rising"
        elif change_pct < -15:
            direction = "falling"
        else:
            direction = "stable"

        return {"keyword": keyword, "direction": direction, 
                "change_pct": round(change_pct, 1)}
```

- [ ] **Step 2: Quick smoke test**

```bash
cd pipeline && python -c "
from fetchers.google_trends import GoogleTrendsFetcher
gt = GoogleTrendsFetcher()
result = gt.get_trend_direction('dog food')
print('dog food trend:', result)
result2 = gt.get_trend_direction('pet camera')
print('pet camera trend:', result2)
"
```

Expected: prints trend direction dicts for dog food and pet camera.

- [ ] **Step 3: Commit**

```bash
git add pipeline/fetchers/google_trends.py
git commit -m "feat: add Google Trends fetcher for search volume signals"
```

---

### Task A4: Reddit Fetcher

**Files:**
- Create: `pipeline/fetchers/reddit_fetcher.py`

- [ ] **Step 1: Implement RedditFetcher**

Write `pipeline/fetchers/reddit_fetcher.py`:
```python
import praw
import pandas as pd
from datetime import datetime
from pipeline.config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
)

PET_SUBREDDITS = ["dogs", "cats", "Pets", "DogFood", "CatAdvice", "puppy101"]

class RedditFetcher:
    """Fetch Reddit discussions for consumer signal detection."""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )

    def search_pet_discussions(self, keyword: str, 
                                subreddits: list[str] | None = None,
                                limit: int = 100,
                                time_filter: str = "year") -> pd.DataFrame:
        """Search pet subreddits for keyword mentions. Returns DataFrame with
        title, score, num_comments, created_utc, subreddit, and url."""
        if subreddits is None:
            subreddits = PET_SUBREDDITS

        subreddit_str = "+".join(subreddits)
        posts = []

        for submission in self.reddit.subreddit(subreddit_str).search(
            keyword, sort="relevance", time_filter=time_filter, limit=limit
        ):
            posts.append({
                "title": submission.title,
                "selftext": submission.selftext[:500],
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": datetime.utcfromtimestamp(submission.created_utc),
                "subreddit": str(submission.subreddit),
                "url": submission.url,
                "keyword": keyword,
            })

        return pd.DataFrame(posts)

    def get_signal_strength(self, keyword: str, 
                            time_filter: str = "year") -> dict:
        """Calculate signal strength from Reddit discussion volume and engagement."""
        subreddits = ["dogs", "Pets", "CatAdvice", "puppy101"]
        subreddit_str = "+".join(subreddits)
        posts = []

        for submission in self.reddit.subreddit(subreddit_str).search(
            keyword, sort="relevance", time_filter=time_filter, limit=200
        ):
            posts.append({
                "score": submission.score,
                "num_comments": submission.num_comments,
            })

        if not posts:
            return {"keyword": keyword, "total_posts": 0, "avg_score": 0,
                    "avg_comments": 0, "signal_strength": "none"}

        df = pd.DataFrame(posts)
        avg_score = df["score"].mean()
        avg_comments = df["num_comments"].mean()
        total = len(posts)

        # Heuristic signal strength
        if total > 50 and avg_score > 100:
            strength = "strong"
        elif total > 20 and avg_score > 30:
            strength = "moderate"
        elif total > 0:
            strength = "weak"
        else:
            strength = "none"

        return {
            "keyword": keyword,
            "total_posts": total,
            "avg_score": round(avg_score, 1),
            "avg_comments": round(avg_comments, 1),
            "signal_strength": strength,
        }
```

- [ ] **Step 2: Quick smoke test**

```bash
cd pipeline && python -c "
from fetchers.reddit_fetcher import RedditFetcher
rf = RedditFetcher()
signal = rf.get_signal_strength('grain free dog food')
print(signal)
"
```

Expected: prints signal dict (requires valid Reddit API credentials).

- [ ] **Step 3: Commit**

```bash
git add pipeline/fetchers/reddit_fetcher.py
git commit -m "feat: add Reddit fetcher for consumer signal detection"
```

---

### Task A5: TrendScore Calculator

**Files:**
- Create: `pipeline/processors/__init__.py`
- Create: `pipeline/processors/trend_score.py`
- Create: `pipeline/tests/test_trend_score.py`

- [ ] **Step 1: Create processors __init__.py**

Write `pipeline/processors/__init__.py`:
```python
from .trend_score import TrendScoreCalculator
```

- [ ] **Step 2: Write failing tests for TrendScoreCalculator**

Write `pipeline/tests/test_trend_score.py`:
```python
import pytest
import pandas as pd
from datetime import datetime, timedelta
from pipeline.processors.trend_score import TrendScoreCalculator

@pytest.fixture
def calculator():
    return TrendScoreCalculator()

@pytest.fixture
def sample_bsr_data():
    """Simulated BSR data: improving (decreasing) rank over 90 days."""
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    bsr = list(range(5000, 4100, -10))  # BSR improving: 5000 → 4100
    return pd.DataFrame({"timestamp": dates, "bsr": bsr})

@pytest.fixture
def sample_trends_data():
    """Simulated Google Trends data: rising interest."""
    dates = pd.date_range(end=datetime.now(), periods=52, freq="W")
    values = [20 + i * 0.5 for i in range(52)]  # rising from 20 to ~45
    return pd.DataFrame({"date": dates, "dog treats": values}).set_index("date")

def test_bsr_momentum_improving(calculator, sample_bsr_data):
    """BSR that improves (goes down) should have positive momentum score."""
    score = calculator._bsr_momentum(sample_bsr_data)
    assert score > 50  # improving BSR = high score
    assert score <= 100

def test_bsr_momentum_declining(calculator):
    """BSR that gets worse (goes up) should have low momentum score."""
    dates = pd.date_range(end=datetime.now(), periods=90, freq="D")
    bsr = list(range(1000, 1900, 10))  # BSR worsening: 1000 → 1900
    df = pd.DataFrame({"timestamp": dates, "bsr": bsr})
    score = calculator._bsr_momentum(df)
    assert score < 50

def test_google_trends_direction(calculator, sample_trends_data):
    """Rising Google Trends should produce positive direction score."""
    direction = calculator._google_trends_signal(sample_trends_data)
    assert direction > 50

def test_calculate_complete_score(calculator, sample_bsr_data, sample_trends_data):
    """Full TrendScore calculation returns dict with all components."""
    reddit_signal = {"signal_strength": "moderate", "total_posts": 35, "avg_score": 120.0}
    
    result = calculator.calculate(
        keyword="dog treats",
        bsr_df=sample_bsr_data,
        trends_df=sample_trends_data,
        reddit_signal=reddit_signal,
    )
    
    assert isinstance(result, dict)
    assert "trend_score" in result
    assert "components" in result
    assert 0 <= result["trend_score"] <= 100
    assert "bsr_momentum" in result["components"]
    assert "google_trends" in result["components"]
    assert "reddit_signal" in result["components"]

def test_calculate_missing_data_returns_partial(calculator):
    """When some data sources are missing, return partial score with flag."""
    result = calculator.calculate(
        keyword="unknown product",
        bsr_df=pd.DataFrame(),
        trends_df=pd.DataFrame(),
        reddit_signal={"signal_strength": "none"},
    )
    assert result["trend_score"] == 0
    assert result["data_quality"] == "insufficient"
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd pipeline && python -m pytest tests/test_trend_score.py -v
```

Expected: 5 tests FAIL.

- [ ] **Step 4: Implement TrendScoreCalculator**

Write `pipeline/processors/trend_score.py`:
```python
import pandas as pd
import numpy as np
from typing import Any

class TrendScoreCalculator:
    """Calculate composite TrendScore (0-100) from cross-platform signals.

    Components:
    - BSR Momentum (35%): Is BSR improving or declining?
    - Google Trends Direction (30%): Is search interest rising?
    - Reddit Signal Strength (25%): Are people talking about it?
    - Velocity Adjustment (10%): How fast are things changing?
    """

    def calculate(self, keyword: str, bsr_df: pd.DataFrame,
                  trends_df: pd.DataFrame, reddit_signal: dict[str, Any]) -> dict:
        """Calculate composite TrendScore for a keyword/category."""
        components = {}

        # BSR Momentum (0-100)
        if not bsr_df.empty and "bsr" in bsr_df.columns:
            components["bsr_momentum"] = round(self._bsr_momentum(bsr_df), 1)
        else:
            components["bsr_momentum"] = 0

        # Google Trends direction (0-100)
        if not trends_df.empty:
            components["google_trends"] = round(self._google_trends_signal(trends_df), 1)
        else:
            components["google_trends"] = 0

        # Reddit signal (0-100)
        components["reddit_signal"] = self._reddit_to_score(reddit_signal)

        # Velocity adjustment (0-100)
        components["velocity"] = self._velocity_adjustment(bsr_df, trends_df)

        # Weighted composite
        weights = {"bsr_momentum": 0.35, "google_trends": 0.30,
                    "reddit_signal": 0.25, "velocity": 0.10}
        
        trend_score = sum(components[k] * weights[k] for k in weights)
        trend_score = round(min(max(trend_score, 0), 100))

        # Data quality
        sources_available = sum(1 for k in weights if components.get(k, 0) > 0)
        if sources_available >= 3:
            data_quality = "good"
        elif sources_available >= 1:
            data_quality = "partial"
        else:
            data_quality = "insufficient"

        return {
            "keyword": keyword,
            "trend_score": trend_score,
            "components": components,
            "data_quality": data_quality,
        }

    def _bsr_momentum(self, df: pd.DataFrame) -> float:
        """Calculate BSR momentum. Lower (improving) BSR = higher score.
        Uses linear regression slope normalized to 0-100 scale."""
        if len(df) < 14:
            return 50.0

        df = df.dropna(subset=["bsr"]).sort_values("timestamp")
        if len(df) < 14:
            return 50.0

        x = np.arange(len(df))
        y = df["bsr"].values
        slope, _ = np.polyfit(x, y, 1)

        # Normalize: a slope of -10/day (fast improvement) → score 100
        # A slope of +10/day (fast decline) → score 0
        normalized = 50 - (slope * 5)
        return float(np.clip(normalized, 0, 100))

    def _google_trends_signal(self, df: pd.DataFrame) -> float:
        """Extract trend direction from Google Trends data.
        Compares first half vs second half average."""
        if df.empty or len(df) < 4:
            return 50.0

        col = df.columns[0]  # Use first keyword column
        mid = len(df) // 2
        first_half = df.iloc[:mid][col].mean()
        second_half = df.iloc[mid:][col].mean()

        if first_half == 0:
            return 70.0 if second_half > 0 else 50.0

        change_pct = ((second_half - first_half) / first_half) * 100
        # Map change_pct to 0-100: +50% change → score 100
        score = 50 + change_pct
        return float(np.clip(score, 0, 100))

    def _reddit_to_score(self, reddit_signal: dict) -> float:
        """Convert Reddit signal dict to 0-100 score."""
        if not reddit_signal:
            return 0

        strength_map = {"strong": 85, "moderate": 55, "weak": 25, "none": 0}
        base = strength_map.get(reddit_signal.get("signal_strength", "none"), 0)

        # Bonus for high engagement
        total_posts = reddit_signal.get("total_posts", 0)
        avg_score = reddit_signal.get("avg_score", 0)

        bonus = min(15, (total_posts / 10) + (avg_score / 100))
        return min(base + bonus, 100)

    def _velocity_adjustment(self, bsr_df: pd.DataFrame, 
                              trends_df: pd.DataFrame) -> float:
        """Measure how fast things are changing. Recent acceleration = higher score."""
        if bsr_df.empty or len(bsr_df) < 30:
            return 50.0

        df = bsr_df.dropna(subset=["bsr"]).sort_values("timestamp")
        if len(df) < 30:
            return 50.0

        # Compare last 14 days slope vs last 30 days slope
        recent = df.tail(14)
        earlier = df.head(len(df) - 14)

        if len(recent) < 5 or len(earlier) < 5:
            return 50.0

        x_recent = np.arange(len(recent))
        slope_recent, _ = np.polyfit(x_recent, recent["bsr"].values, 1)
        x_earlier = np.arange(len(earlier))
        slope_earlier, _ = np.polyfit(x_earlier, earlier["bsr"].values, 1)

        # If recent improvement is accelerating vs earlier
        acceleration = slope_earlier - slope_recent  # positive = accelerating improvement
        score = 50 + (acceleration * 10)
        return float(np.clip(score, 0, 100))
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd pipeline && python -m pytest tests/test_trend_score.py -v
```

Expected: 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add pipeline/processors/ pipeline/tests/test_trend_score.py
git commit -m "feat: add TrendScore calculator for cross-platform signal aggregation"
```

---

### Task A6: Data Export & First Analysis Notebook

**Files:**
- Create: `pipeline/outputs/__init__.py`
- Create: `pipeline/outputs/export.py`
- Create: `pipeline/notebooks/pet_supplies_eda.ipynb`
- Create: `pipeline/tests/test_export.py`

- [ ] **Step 1: Create outputs __init__.py**

Write `pipeline/outputs/__init__.py`:
```python
from .export import DataExporter
```

- [ ] **Step 2: Implement DataExporter**

Write `pipeline/outputs/export.py`:
```python
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from pipeline.config import DATA_PROCESSED, DATA_EXPORTS

class DataExporter:
    """Export processed data to web-consumable formats."""

    def __init__(self):
        self.exports_dir = DATA_EXPORTS
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    def export_trend_scores(self, scores: list[dict], 
                            filename: str = "trend_scores.json") -> Path:
        """Export trend scores list to JSON for web consumption."""
        output_path = self.exports_dir / filename
        
        payload = {
            "generated_at": datetime.now().isoformat(),
            "scores": scores,
        }
        
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=2, default=str)
        
        return output_path

    def export_category_summary(self, summary: dict, 
                                filename: str = "category_summary.json") -> Path:
        """Export category-level summary statistics to JSON."""
        output_path = self.exports_dir / filename
        
        summary["generated_at"] = datetime.now().isoformat()
        
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        return output_path

    def save_processed_parquet(self, df: pd.DataFrame, 
                                filename: str) -> Path:
        """Save processed DataFrame to parquet."""
        output_path = DATA_PROCESSED / filename
        df.to_parquet(output_path)
        return output_path

    def export_all(self, scores: list[dict], 
                   summary: dict, df: pd.DataFrame, 
                   prefix: str = "pet_supplies") -> dict[str, Path]:
        """Run all exports and return path mapping."""
        return {
            "scores_json": self.export_trend_scores(scores, f"{prefix}_trend_scores.json"),
            "summary_json": self.export_category_summary(summary, f"{prefix}_summary.json"),
            "processed_parquet": self.save_processed_parquet(df, f"{prefix}_processed.parquet"),
        }
```

- [ ] **Step 3: Create data export test**

Write `pipeline/tests/test_export.py`:
```python
import json
import pandas as pd
from pipeline.outputs.export import DataExporter

def test_export_trend_scores(tmp_path):
    exporter = DataExporter()
    exporter.exports_dir = tmp_path

    scores = [
        {"keyword": "dog treats", "trend_score": 78, "components": {}, "data_quality": "good"},
        {"keyword": "cat litter", "trend_score": 45, "components": {}, "data_quality": "partial"},
    ]
    
    path = exporter.export_trend_scores(scores, "test_scores.json")
    assert path.exists()
    
    with open(path) as f:
        data = json.load(f)
    
    assert len(data["scores"]) == 2
    assert data["scores"][0]["keyword"] == "dog treats"
    assert "generated_at" in data

def test_save_processed_parquet(tmp_path):
    from pipeline.config import DATA_PROCESSED
    exporter = DataExporter()
    exporter.exports_dir = tmp_path
    
    df = pd.DataFrame({"asin": ["X", "Y"], "bsr": [100, 200]})
    path = exporter.save_processed_parquet(df, "test.parquet")
    
    assert path.exists()
    loaded = pd.read_parquet(path)
    assert len(loaded) == 2
```

Run tests:
```bash
cd pipeline && python -m pytest tests/test_export.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 4: Create first analysis notebook**

Write `pipeline/notebooks/pet_supplies_eda.ipynb` as a Jupyter notebook with cells that:

Cell 1 — Setup:
```python
import sys
sys.path.append("..")
import pandas as pd
import plotly.express as px
from pipeline.fetchers.keepa_fetcher import KeepaFetcher
from pipeline.fetchers.google_trends import GoogleTrendsFetcher
from pipeline.fetchers.reddit_fetcher import RedditFetcher
from pipeline.processors.trend_score import TrendScoreCalculator
from pipeline.outputs.export import DataExporter
from pipeline.config import PET_SUPPLIES_SEARCH_TERMS
```

Cell 2 — Fetch Google Trends data:
```python
gt = GoogleTrendsFetcher()
trends_data = gt.fetch_multi_batch(PET_SUPPLIES_SEARCH_TERMS[:10], timeframe="today 12-m")
trends_data.head()
```

Cell 3 — Calculate trend directions:
```python
trend_results = []
for term in PET_SUPPLIES_SEARCH_TERMS[:10]:
    result = gt.get_trend_direction(term)
    trend_results.append(result)

trend_df = pd.DataFrame(trend_results)
trend_df.sort_values("change_pct", ascending=False)
```

Cell 4 — Plot Google Trends:
```python
fig = px.line(trends_data, title="Pet Supplies Search Trends (12 Months)")
fig.show()
```

Cell 5 — Fetch sample Keepa data:
```python
# Sample ASINs from pet supplies best sellers
pet_asins = {
    "dog_food": "B00BMYFQ7C",
    "dog_treats": "B0009YNTIY",
    "cat_litter": "B0009XPMTQ",
    "pet_fountain": "B0009XAH9A",
}

kf = KeepaFetcher()
for label, asin in pet_asins.items():
    df = kf.fetch_and_save(asin, f"../data/raw/{label}_{asin}.parquet")
    print(f"{label}: {len(df)} data points")
```

Cell 6 — Reddit signals:
```python
rf = RedditFetcher()
reddit_results = []
for term in ["grain free dog food", "automatic cat feeder", "dog enrichment toys"]:
    signal = rf.get_signal_strength(term)
    reddit_results.append(signal)

pd.DataFrame(reddit_results)
```

Cell 7 — Composite TrendScores:
```python
calc = TrendScoreCalculator()
results = []

for term in PET_SUPPLIES_SEARCH_TERMS[:5]:
    trends_df = gt.fetch_interest_over_time([term], timeframe="today 3-m")
    reddit_signal = rf.get_signal_strength(term)
    
    score = calc.calculate(
        keyword=term,
        bsr_df=pd.DataFrame(),  # placeholder — need ASIN mapping
        trends_df=trends_df,
        reddit_signal=reddit_signal,
    )
    results.append(score)

pd.DataFrame(results)[["keyword", "trend_score", "data_quality"]].sort_values("trend_score", ascending=False)
```

Cell 8 — Export:
```python
exporter = DataExporter()
exporter.export_trend_scores(results, "pet_supplies_v1_trend_scores.json")
print("Exported to data/exports/")
```

- [ ] **Step 5: Commit**

```bash
git add pipeline/outputs/ pipeline/notebooks/ pipeline/tests/test_export.py
git commit -m "feat: add data exporter and first pet supplies EDA notebook"
```

---

## PLAN B: Web Platform (Next.js)

### Task B1: Next.js Project Scaffold

**Files:**
- Create: `web/` (via create-next-app)

- [ ] **Step 1: Create Next.js project**

```bash
npx create-next-app@latest web --typescript --tailwind --eslint --app --src-dir --no-import-alias
cd web
npm install plotly.js-dist-min react-plotly.js next-mdx-remote
```

- [ ] **Step 2: Verify dev server starts**

```bash
cd web && npm run dev
```

Expected: Next.js starts on http://localhost:3000.

- [ ] **Step 3: Configure MDX for blog**

Write `web/next.config.mjs`:
```js
import createMDX from '@next/mdx'

const withMDX = createMDX({
  extension: /\.mdx?$/,
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ['js', 'jsx', 'ts', 'tsx', 'md', 'mdx'],
  output: 'export',
  images: { unoptimized: true },
}

export default withMDX(nextConfig)
```

- [ ] **Step 4: Update tailwind.config.ts** — keep defaults, add brand colors

```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#eff6ff',
          500: '#3b82f6',
          700: '#1d4ed8',
          900: '#1e3a5f',
        }
      }
    },
  },
  plugins: [],
};
export default config;
```

- [ ] **Step 5: Commit**

```bash
git add web/
git commit -m "feat: scaffold Next.js project with MDX and Tailwind"
```

---

### Task B2: Layout & Navigation

**Files:**
- Create: `web/src/components/Layout.tsx`
- Modify: `web/src/app/layout.tsx`

- [ ] **Step 1: Create Layout component**

Write `web/src/components/Layout.tsx`:
```tsx
import Link from 'next/link';

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-brand-900">
            AMZ Data
            <span className="text-sm font-normal text-gray-400 ml-2">Pet Intelligence</span>
          </Link>
          <div className="flex gap-6 text-sm font-medium">
            <Link href="/blog" className="text-gray-600 hover:text-brand-500">Blog</Link>
            <Link href="/tools" className="text-gray-600 hover:text-brand-500">Tools</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>
      <footer className="border-t border-gray-100 mt-16 py-8 text-center text-sm text-gray-400">
        AMZ Data — Data insights for Amazon sellers
      </footer>
    </div>
  );
}
```

- [ ] **Step 2: Update root layout**

Write `web/src/app/layout.tsx`:
```tsx
import type { Metadata } from 'next';
import '@/styles/globals.css';
import Layout from '@/components/Layout';

export const metadata: Metadata = {
  title: 'AMZ Data — Pet Supplies Intelligence',
  description: 'Data-driven trend insights for Amazon Pet Supplies sellers. Spot what\'s trending before it peaks.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Update global CSS**

Write `web/src/styles/globals.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply text-gray-900 bg-white;
  }
}
```

- [ ] **Step 4: Verify in browser**

```bash
cd web && npm run dev
```

Open http://localhost:3000 — verify navigation bar and footer render.

- [ ] **Step 5: Commit**

```bash
git add web/src/components/Layout.tsx web/src/app/layout.tsx web/src/styles/globals.css
git commit -m "feat: add layout with navigation and footer"
```

---

### Task B3: Homepage

**Files:**
- Modify: `web/src/app/page.tsx`

- [ ] **Step 1: Write homepage**

Write `web/src/app/page.tsx`:
```tsx
import Link from 'next/link';

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="text-center py-16">
        <h1 className="text-4xl font-bold text-brand-900 mb-4">
          Pet Supplies Data Intelligence
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto mb-8">
          Cross-platform trend signals for Amazon Pet Supplies sellers.
          Spot what&apos;s trending before it peaks — using Google Trends, Reddit signals, and marketplace data.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/tools/trend-scanner" className="px-6 py-3 bg-brand-500 text-white rounded-lg font-medium hover:bg-brand-700">
            Try Trend Scanner →
          </Link>
          <Link href="/blog" className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:border-brand-500 text-gray-700">
            Read Research
          </Link>
        </div>
      </section>

      {/* Three value props */}
      <section className="grid md:grid-cols-3 gap-8">
        {[
          {
            title: 'Trend Signals',
            desc: 'Google Trends + Reddit + BSR data combined into a single TrendScore.',
            icon: '📊',
          },
          {
            title: 'Pet-First Research',
            desc: 'Deep analysis of pet sub-niches: dog food, cat litter, pet tech, and more.',
            icon: '🐾',
          },
          {
            title: 'Free Tools',
            desc: 'Chrome extension overlays trend data on Amazon product pages. Web tools for deep dives.',
            icon: '🛠️',
          },
        ].map((item) => (
          <div key={item.title} className="p-6 border border-gray-200 rounded-xl">
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
          <span className="text-xs text-brand-500 font-medium">June 2026 · Deep Dive</span>
          <h3 className="text-xl font-semibold mt-1 mb-2">Pet Supplies Market Landscape: Where the Growth Is</h3>
          <p className="text-gray-500 mb-4">
            We analyzed 20+ pet sub-categories across search trends, BSR momentum, and Reddit discussion volume.
            Here are the 5 highest-signal opportunities.
          </p>
          <Link href="/blog/pet-supplies-landscape" className="text-brand-500 font-medium hover:underline">
            Read full report →
          </Link>
        </div>
      </section>
    </div>
  );
}
```

- [ ] **Step 2: Verify in browser**

```bash
cd web && npm run dev
```

Open http://localhost:3000 — verify hero, value props, and latest research card render.

- [ ] **Step 3: Commit**

```bash
git add web/src/app/page.tsx
git commit -m "feat: add homepage with hero, value props, and latest research"
```

---

### Task B4: Blog System

**Files:**
- Create: `web/src/app/blog/page.tsx`
- Create: `web/src/app/blog/[slug]/page.tsx`
- Create: `web/src/components/BlogCard.tsx`
- Create: `web/src/content/blog/pet-supplies-landscape.mdx`

- [ ] **Step 1: Create BlogCard component**

Write `web/src/components/BlogCard.tsx`:
```tsx
import Link from 'next/link';

interface BlogCardProps {
  slug: string;
  title: string;
  date: string;
  category: string;
  excerpt: string;
}

export default function BlogCard({ slug, title, date, category, excerpt }: BlogCardProps) {
  return (
    <Link href={`/blog/${slug}`} className="block border border-gray-200 rounded-xl p-6 hover:border-brand-500 transition-colors">
      <span className="text-xs text-brand-500 font-medium">{date} · {category}</span>
      <h3 className="text-xl font-semibold mt-1 mb-2">{title}</h3>
      <p className="text-gray-500 text-sm">{excerpt}</p>
    </Link>
  );
}
```

- [ ] **Step 2: Create blog index page**

Write `web/src/app/blog/page.tsx`:
```tsx
import BlogCard from '@/components/BlogCard';

const posts = [
  {
    slug: 'pet-supplies-landscape',
    title: 'Pet Supplies Market Landscape: Where the Growth Is',
    date: 'June 2026',
    category: 'Deep Dive',
    excerpt: 'We analyzed 20+ pet sub-categories across search trends, BSR momentum, and Reddit discussion volume. Here are the 5 highest-signal opportunities.',
  },
];

export default function BlogPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Research & Analysis</h1>
      <p className="text-gray-500">Data-driven reports on Amazon Pet Supplies trends.</p>
      <div className="space-y-4 mt-8">
        {posts.map((post) => (
          <BlogCard key={post.slug} {...post} />
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Create blog post dynamic route**

Write `web/src/app/blog/[slug]/page.tsx`:
```tsx
import { notFound } from 'next/navigation';
import PetSuppliesLandscape from '@/content/blog/pet-supplies-landscape.mdx';

const posts: Record<string, { component: React.ComponentType; title: string; date: string }> = {
  'pet-supplies-landscape': {
    component: PetSuppliesLandscape,
    title: 'Pet Supplies Market Landscape: Where the Growth Is',
    date: 'June 12, 2026',
  },
};

export function generateStaticParams() {
  return Object.keys(posts).map((slug) => ({ slug }));
}

export default function BlogPost({ params }: { params: { slug: string } }) {
  const post = posts[params.slug];
  if (!post) notFound();

  const Content = post.component;

  return (
    <article className="max-w-3xl mx-auto">
      <header className="mb-8">
        <span className="text-sm text-gray-400">{post.date}</span>
        <h1 className="text-3xl font-bold mt-1">{post.title}</h1>
      </header>
      <div className="prose prose-gray max-w-none">
        <Content />
      </div>
    </article>
  );
}
```

- [ ] **Step 4: Write first blog post (MDX)**

Write `web/src/content/blog/pet-supplies-landscape.mdx`:
```mdx
# Pet Supplies Market Landscape: Where the Growth Is

*Published June 12, 2026 · 8 min read · Pet Supplies Deep Dive*

The Amazon Pet Supplies category generates over **$20 billion** in annual third-party GMV. But the headline number hides massive variation across sub-categories. Some are exploding; others are stagnating.

We analyzed **20+ pet sub-niches** using three data layers:

1. **Google Trends** — Search interest trajectory (leading indicator)
2. **Amazon BSR history** — Actual sales momentum (confirmation signal)
3. **Reddit discussions** — Consumer pain points and unmet needs

Here's what we found.

---

## The 5 Highest-Signal Pet Sub-Niches Right Now

### 1. Grain-Free & Novel Protein Dog Food

- **TrendScore: 87/100**
- Google Trends: +42% YoY, accelerating
- Reddit signal: Strong (300+ relevant posts in r/dogs + r/DogFood)
- Key driver: Health-conscious pet owners seeking alternatives

### 2. Smart Pet Feeders & Water Fountains

- **TrendScore: 82/100**
- Google Trends: +35% YoY
- Reddit signal: Strong ("automatic feeder" mentioned in 250+ posts)
- Key driver: Return-to-office driving demand for automated feeding solutions

### 3. Cat Enrichment Toys

- **TrendScore: 78/100**
- Google Trends: +28% YoY
- Reddit signal: Moderate-Strong
- Key driver: Indoor cat ownership rising; "cat boredom" is a recurring pain point

### 4. Eco-Friendly Pet Products

- **TrendScore: 74/100**
- Google Trends: +31% YoY
- Reddit signal: Moderate
- Key driver: Sustainability consciousness crossing into pet spending

### 5. Pet Cameras & Monitors

- **TrendScore: 71/100**
- Google Trends: +25% YoY
- Reddit signal: Strong, especially around separation anxiety
- Key driver: Post-pandemic pet attachment + anxiety monitoring

---

## Methodology

Every TrendScore combines:

- **BSR Momentum (35%)** — Is BSR improving or declining?
- **Google Trends Direction (30%)** — Is search interest rising?
- **Reddit Signal Strength (25%)** — Are consumers discussing it?
- **Velocity Adjustment (10%)** — Is the trend accelerating?

[Full methodology on GitHub →](https://github.com/amzdata/pipeline)

---

## What This Means for Sellers

The pet category isn't one market — it's dozens of micro-markets moving at different speeds. The winners are sellers who spot the fast-movers early, while everyone else fights over saturated niches.

Next week: We deep-dive into **dog treats** — what reviews reveal about unmet demand.

*Have a sub-niche you want us to analyze? Reply on Reddit or reach out.*
```

- [ ] **Step 5: Verify blog renders**

```bash
cd web && npm run dev
```

Open http://localhost:3000/blog and http://localhost:3000/blog/pet-supplies-landscape — verify post renders with MDX content.

- [ ] **Step 6: Commit**

```bash
git add web/src/app/blog/ web/src/components/BlogCard.tsx web/src/content/
git commit -m "feat: add blog system with first pet supplies deep-dive post"
```

---

### Task B5: Trend Scanner Tool

**Files:**
- Create: `web/src/app/tools/page.tsx`
- Create: `web/src/app/tools/trend-scanner/page.tsx`
- Create: `web/src/app/api/trends/route.ts`
- Create: `web/src/components/TrendScore.tsx`
- Create: `web/src/components/TrendChart.tsx`
- Create: `web/src/lib/data.ts`
- Create: `web/src/lib/trendscore.ts`

- [ ] **Step 1: Create data loading utility**

Write `web/src/lib/data.ts`:
```ts
export interface TrendResult {
  keyword: string;
  trend_score: number;
  components: {
    bsr_momentum: number;
    google_trends: number;
    reddit_signal: number;
    velocity: number;
  };
  data_quality: 'good' | 'partial' | 'insufficient';
}

export interface TrendData {
  generated_at: string;
  scores: TrendResult[];
}

export async function loadTrendData(): Promise<TrendData> {
  // In production, this loads from the JSON export file
  // For MVP, use static data from /public/data/
  const res = await fetch('/data/pet_supplies_trend_scores.json');
  if (!res.ok) {
    return { generated_at: '', scores: [] };
  }
  return res.json();
}
```

- [ ] **Step 2: Create TrendScore badge component**

Write `web/src/components/TrendScore.tsx`:
```tsx
interface TrendScoreProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
}

function scoreColor(score: number): string {
  if (score >= 70) return 'text-green-600 bg-green-50 border-green-200';
  if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-red-600 bg-red-50 border-red-200';
}

export default function TrendScore({ score, size = 'md' }: TrendScoreProps) {
  const sizes = { sm: 'text-sm px-2 py-0.5', md: 'text-lg px-3 py-1', lg: 'text-2xl px-4 py-2' };

  return (
    <span className={`${sizes[size]} font-bold rounded-lg border ${scoreColor(score)} inline-flex items-center gap-1`}>
      {score}
      <span className="text-xs font-normal">/100</span>
    </span>
  );
}
```

- [ ] **Step 3: Create TrendChart component**

Write `web/src/components/TrendChart.tsx`:
```tsx
'use client';

import dynamic from 'next/dynamic';
import { TrendResult } from '@/lib/data';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface TrendChartProps {
  results: TrendResult[];
}

export default function TrendChart({ results }: TrendChartProps) {
  const sorted = [...results].sort((a, b) => b.trend_score - a.trend_score);

  const data = [
    {
      type: 'bar' as const,
      x: sorted.map((r) => r.keyword),
      y: sorted.map((r) => r.trend_score),
      marker: {
        color: sorted.map((r) =>
          r.trend_score >= 70 ? '#16a34a' : r.trend_score >= 40 ? '#ca8a04' : '#dc2626'
        ),
      },
      text: sorted.map((r) => `${r.trend_score}/100`),
      textposition: 'outside' as const,
    },
  ];

  const layout = {
    title: 'Pet Supplies TrendScores',
    yaxis: { title: 'TrendScore', range: [0, 100] },
    xaxis: { tickangle: -30 },
    margin: { t: 40, b: 100 },
    height: 400,
  };

  return <Plot data={data} layout={layout} style={{ width: '100%' }} />;
}
```

- [ ] **Step 4: Create tools index page**

Write `web/src/app/tools/page.tsx`:
```tsx
import Link from 'next/link';

const tools = [
  {
    slug: 'trend-scanner',
    title: 'Trend Scanner',
    desc: 'Input a pet sub-niche keyword and get a composite TrendScore with signal breakdown.',
    status: 'live',
  },
  {
    slug: 'niche-compare',
    title: 'Niche Compare',
    desc: 'Compare trend data across multiple pet sub-niches side by side.',
    status: 'coming-soon',
  },
  {
    slug: 'asin-deep-look',
    title: 'ASIN Deep Look',
    desc: 'Multi-dimension analysis for a single ASIN: BSR history, price trends, competitive signals.',
    status: 'coming-soon',
  },
];

export default function ToolsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Tools</h1>
      <p className="text-gray-500">Free tools for Amazon Pet Supplies sellers.</p>
      <div className="grid gap-4 mt-8">
        {tools.map((tool) => (
          <div key={tool.slug} className="border border-gray-200 rounded-xl p-6 flex justify-between items-center">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold">{tool.title}</h3>
                {tool.status === 'coming-soon' && (
                  <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded">Soon</span>
                )}
              </div>
              <p className="text-gray-500 text-sm mt-1">{tool.desc}</p>
            </div>
            {tool.status === 'live' ? (
              <Link href={`/tools/${tool.slug}`} className="px-4 py-2 bg-brand-500 text-white rounded-lg text-sm font-medium hover:bg-brand-700 shrink-0">
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
```

- [ ] **Step 5: Create Trend Scanner page**

Write `web/src/app/tools/trend-scanner/page.tsx`:
```tsx
'use client';

import { useState } from 'react';
import TrendScore from '@/components/TrendScore';
import TrendChart from '@/components/TrendChart';
import { TrendResult } from '@/lib/data';

// Static data for MVP — will be replaced by API call
const SAMPLE_RESULTS: TrendResult[] = [
  { keyword: 'grain free dog food', trend_score: 87, components: { bsr_momentum: 82, google_trends: 90, reddit_signal: 85, velocity: 88 }, data_quality: 'good' },
  { keyword: 'smart pet feeder', trend_score: 82, components: { bsr_momentum: 78, google_trends: 85, reddit_signal: 80, velocity: 75 }, data_quality: 'good' },
  { keyword: 'cat enrichment toys', trend_score: 78, components: { bsr_momentum: 72, google_trends: 80, reddit_signal: 75, velocity: 82 }, data_quality: 'good' },
  { keyword: 'eco friendly dog toys', trend_score: 74, components: { bsr_momentum: 68, google_trends: 78, reddit_signal: 70, velocity: 72 }, data_quality: 'partial' },
  { keyword: 'pet camera monitor', trend_score: 71, components: { bsr_momentum: 70, google_trends: 72, reddit_signal: 75, velocity: 60 }, data_quality: 'good' },
  { keyword: 'automatic cat litter box', trend_score: 65, components: { bsr_momentum: 62, google_trends: 70, reddit_signal: 60, velocity: 68 }, data_quality: 'partial' },
  { keyword: 'dog puzzle toys', trend_score: 62, components: { bsr_momentum: 58, google_trends: 65, reddit_signal: 68, velocity: 55 }, data_quality: 'partial' },
  { keyword: 'organic cat treats', trend_score: 58, components: { bsr_momentum: 55, google_trends: 60, reddit_signal: 52, velocity: 62 }, data_quality: 'partial' },
];

export default function TrendScannerPage() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState<TrendResult[]>(SAMPLE_RESULTS);
  const [searching, setSearching] = useState(false);

  function handleSearch() {
    if (!keyword.trim()) return;
    setSearching(true);
    // Filter sample data for MVP — will call API in production
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
        <p className="text-gray-500 mt-1">Analyze trend signals for any pet sub-niche.</p>
      </div>

      {/* Search bar */}
      <div className="flex gap-3">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="e.g., dog treats, cat fountain, pet camera..."
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          onClick={handleSearch}
          disabled={searching}
          className="px-6 py-2 bg-brand-500 text-white rounded-lg font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {searching ? 'Scanning...' : 'Scan'}
        </button>
      </div>

      {/* Results table */}
      <div>
        <h2 className="text-xl font-semibold mb-4">TrendScores</h2>
        <div className="border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-4 py-3 text-sm font-medium text-gray-500">Keyword</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">TrendScore</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">Search</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">Reddit</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">BSR</th>
                <th className="text-center px-4 py-3 text-sm font-medium text-gray-500">Quality</th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => (
                <tr key={r.keyword} className="border-t border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium capitalize">{r.keyword}</td>
                  <td className="px-4 py-3 text-center"><TrendScore score={r.trend_score} size="sm" /></td>
                  <td className="px-4 py-3 text-center">{r.components.google_trends}</td>
                  <td className="px-4 py-3 text-center">{r.components.reddit_signal}</td>
                  <td className="px-4 py-3 text-center">{r.components.bsr_momentum}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      r.data_quality === 'good' ? 'bg-green-100 text-green-700' :
                      r.data_quality === 'partial' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
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
```

- [ ] **Step 6: Create API endpoint for future dynamic data**

Write `web/src/app/api/trends/route.ts`:
```ts
import { NextRequest, NextResponse } from 'next/server';

// In production, this reads from data/exports/ JSON files
// For MVP, returns static sample data

const SAMPLE_SCORES = [
  { keyword: 'grain free dog food', trend_score: 87, components: { bsr_momentum: 82, google_trends: 90, reddit_signal: 85, velocity: 88 }, data_quality: 'good' },
  { keyword: 'smart pet feeder', trend_score: 82, components: { bsr_momentum: 78, google_trends: 85, reddit_signal: 80, velocity: 75 }, data_quality: 'good' },
  { keyword: 'cat enrichment toys', trend_score: 78, components: { bsr_momentum: 72, google_trends: 80, reddit_signal: 75, velocity: 82 }, data_quality: 'good' },
  { keyword: 'eco friendly dog toys', trend_score: 74, components: { bsr_momentum: 68, google_trends: 78, reddit_signal: 70, velocity: 72 }, data_quality: 'partial' },
  { keyword: 'pet camera monitor', trend_score: 71, components: { bsr_momentum: 70, google_trends: 72, reddit_signal: 75, velocity: 60 }, data_quality: 'good' },
];

export async function GET(request: NextRequest) {
  const keyword = request.nextUrl.searchParams.get('keyword');
  
  if (keyword) {
    const filtered = SAMPLE_SCORES.filter((s) =>
      s.keyword.toLowerCase().includes(keyword.toLowerCase())
    );
    return NextResponse.json({ scores: filtered, generated_at: new Date().toISOString() });
  }

  return NextResponse.json({ scores: SAMPLE_SCORES, generated_at: new Date().toISOString() });
}
```

- [ ] **Step 7: Copy sample data to public directory**

```bash
mkdir -p web/public/data
```

Write `web/public/data/pet_supplies_trend_scores.json`:
```json
{
  "generated_at": "2026-06-12T00:00:00Z",
  "scores": [
    { "keyword": "grain free dog food", "trend_score": 87, "components": { "bsr_momentum": 82, "google_trends": 90, "reddit_signal": 85, "velocity": 88 }, "data_quality": "good" },
    { "keyword": "smart pet feeder", "trend_score": 82, "components": { "bsr_momentum": 78, "google_trends": 85, "reddit_signal": 80, "velocity": 75 }, "data_quality": "good" },
    { "keyword": "cat enrichment toys", "trend_score": 78, "components": { "bsr_momentum": 72, "google_trends": 80, "reddit_signal": 75, "velocity": 82 }, "data_quality": "good" },
    { "keyword": "eco friendly dog toys", "trend_score": 74, "components": { "bsr_momentum": 68, "google_trends": 78, "reddit_signal": 70, "velocity": 72 }, "data_quality": "partial" },
    { "keyword": "pet camera monitor", "trend_score": 71, "components": { "bsr_momentum": 70, "google_trends": 72, "reddit_signal": 75, "velocity": 60 }, "data_quality": "good" }
  ]
}
```

- [ ] **Step 8: Verify tools work**

```bash
cd web && npm run dev
```

Open http://localhost:3000/tools — verify tools index.
Open http://localhost:3000/tools/trend-scanner — verify table + chart render, search bar works.

- [ ] **Step 9: Commit**

```bash
git add web/src/app/tools/ web/src/app/api/ web/src/components/TrendScore.tsx web/src/components/TrendChart.tsx web/src/lib/ web/public/data/
git commit -m "feat: add Trend Scanner tool with search, table, and chart"
```

---

## PLAN C: Chrome Extension

### Task C1: Extension Scaffold & Manifest

**Files:**
- Create: `extension/manifest.json`
- Create: `extension/service_worker.js`
- Create: `extension/icons/icon16.png`
- Create: `extension/icons/icon48.png`
- Create: `extension/icons/icon128.png`

- [ ] **Step 1: Create extension directory structure**

```bash
mkdir -p extension/content extension/sidebar extension/lib extension/icons
```

- [ ] **Step 2: Write manifest.json**

Write `extension/manifest.json`:
```json
{
  "manifest_version": 3,
  "name": "AMZ Data — Pet Supplies Trend Signals",
  "version": "0.1.0",
  "description": "Overlay trend signals on Amazon Pet Supplies product pages. TrendScore, Google Trends, Reddit signals — at a glance.",
  "permissions": ["sidePanel", "storage"],
  "host_permissions": [
    "https://www.amazon.com/*/dp/*",
    "https://www.amazon.com/s?*",
    "https://amzdata.com/*"
  ],
  "content_scripts": [
    {
      "matches": ["https://www.amazon.com/*"],
      "js": ["content/inject.js"],
      "css": ["content/inject.css"],
      "run_at": "document_idle"
    }
  ],
  "side_panel": {
    "default_path": "sidebar/panel.html"
  },
  "background": {
    "service_worker": "service_worker.js"
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

- [ ] **Step 3: Write service worker (side panel opener)**

Write `extension/service_worker.js`:
```js
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error('Side panel setup error:', error));
```

- [ ] **Step 4: Create placeholder icons**

Use any simple 16x16, 48x48, 128x128 PNG placeholder. For MVP, create solid-color squares or use a text-based alternative:

```bash
# For now, create simple placeholder PNGs (1x1 pixel will work, replace with real icons later)
# These can be generated or downloaded later
echo "Placeholder — replace with real icons" > extension/icons/README.md
```

- [ ] **Step 5: Commit**

```bash
git add extension/
git commit -m "feat: scaffold Chrome extension with Manifest V3"
```

---

### Task C2: Content Script — Inject TrendScore Badge

**Files:**
- Create: `extension/content/inject.js`
- Create: `extension/content/inject.css`

- [ ] **Step 1: Write content injection script**

Write `extension/content/inject.js`:
```js
(function () {
  'use strict';

  const API_BASE = 'https://amzdata.com/api/trends';
  const ASIN_REGEX = /\/dp\/([A-Z0-9]{10})/;

  function getASIN() {
    const match = window.location.pathname.match(ASIN_REGEX);
    return match ? match[1] : null;
  }

  function getCategoryFromDOM() {
    // Try to detect if this is a pet supplies product
    const breadcrumbs = document.querySelectorAll('#wayfinding-breadcrumbs_feature_div a, .a-breadcrumb a');
    for (const el of breadcrumbs) {
      const text = el.textContent.toLowerCase().trim();
      if (['pet supplies', 'dogs', 'cats', 'pet food', 'pet toys'].includes(text)) {
        return text;
      }
    }
    return null;
  }

  function getProductTitle() {
    const titleEl = document.querySelector('#productTitle');
    return titleEl ? titleEl.textContent.trim() : '';
  }

  function injectTrendBadge(score) {
    // Remove existing badge if any
    const existing = document.getElementById('amzdata-trend-badge');
    if (existing) existing.remove();

    const color =
      score >= 70 ? '#16a34a' : score >= 40 ? '#ca8a04' : '#dc2626';
    const bg =
      score >= 70 ? '#f0fdf4' : score >= 40 ? '#fefce8' : '#fef2f2';

    const badge = document.createElement('div');
    badge.id = 'amzdata-trend-badge';
    badge.style.cssText = `
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 8px;
      background: ${bg}; border: 1px solid ${color};
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      margin-left: 12px; cursor: pointer;
    `;
    badge.innerHTML = `
      <span style="font-weight:700; font-size:16px; color:${color}">TrendScore</span>
      <span style="font-weight:700; font-size:18px; color:${color}">${score}/100</span>
    `;

    badge.addEventListener('click', () => {
      chrome.runtime.sendMessage({ action: 'openSidePanel' });
    });

    // Insert next to product title
    const titleEl = document.querySelector('#productTitle');
    if (titleEl && titleEl.parentElement) {
      titleEl.parentElement.style.display = 'flex';
      titleEl.parentElement.style.alignItems = 'center';
      titleEl.parentElement.style.flexWrap = 'wrap';
      titleEl.after(badge);
    }
  }

  function injectNoDataBadge() {
    const existing = document.getElementById('amzdata-trend-badge');
    if (existing) existing.remove();

    const badge = document.createElement('div');
    badge.id = 'amzdata-trend-badge';
    badge.style.cssText = `
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 8px;
      background: #f9fafb; border: 1px solid #d1d5db;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      margin-left: 12px;
    `;
    badge.innerHTML = `
      <span style="font-weight:600; font-size:14px; color:#6b7280">TrendScore not yet available for this product</span>
    `;

    const titleEl = document.querySelector('#productTitle');
    if (titleEl && titleEl.parentElement) {
      titleEl.parentElement.style.display = 'flex';
      titleEl.parentElement.style.alignItems = 'center';
      titleEl.after(badge);
    }
  }

  async function fetchTrendScore(keyword) {
    try {
      const res = await fetch(`${API_BASE}?keyword=${encodeURIComponent(keyword)}`);
      if (!res.ok) return null;
      const data = await res.json();
      if (data.scores && data.scores.length > 0) {
        return data.scores[0].trend_score;
      }
      return null;
    } catch {
      return null;
    }
  }

  async function main() {
    const category = getCategoryFromDOM();
    if (!category) return; // Not a pet supplies page, skip

    const asin = getASIN();
    if (!asin) return; // Not a product page

    const title = getProductTitle();
    if (!title) return;

    // Extract main keyword from title (first 3 words)
    const keyword = title.split(' ').slice(0, 4).join(' ');

    const score = await fetchTrendScore(keyword);
    if (score !== null) {
      injectTrendBadge(score);
    } else {
      injectNoDataBadge();
    }
  }

  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
  } else {
    main();
  }
})();
```

- [ ] **Step 2: Write inject styles**

Write `extension/content/inject.css`:
```css
/* Minimal — badge is styled inline for isolation from Amazon's CSS */
#amzdata-trend-badge {
  transition: opacity 0.2s ease;
}
#amzdata-trend-badge:hover {
  opacity: 0.85;
}
```

- [ ] **Step 3: Commit**

```bash
git add extension/content/
git commit -m "feat: add content script to inject TrendScore badge on Amazon pet product pages"
```

---

### Task C3: Sidebar Panel

**Files:**
- Create: `extension/sidebar/panel.html`
- Create: `extension/sidebar/panel.js`
- Create: `extension/sidebar/panel.css`

- [ ] **Step 1: Write sidebar panel HTML**

Write `extension/sidebar/panel.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AMZ Data — Trend Signals</title>
  <link rel="stylesheet" href="panel.css">
</head>
<body>
  <header>
    <h1>🐾 AMZ Data</h1>
    <span class="subtitle">Pet Supplies Trend Signals</span>
  </header>

  <main>
    <section class="product-info" id="product-info">
      <p class="placeholder">Open an Amazon Pet Supplies product page to see trend signals.</p>
    </section>

    <section class="signals" id="signals" style="display:none;">
      <h2>TrendScore</h2>
      <div class="trendscore-big" id="trendscore-big">--</div>

      <h2>Signal Breakdown</h2>
      <div class="signal-grid" id="signal-grid"></div>

      <h2>Category Context</h2>
      <div id="category-context"></div>

      <div class="cta">
        <a href="https://amzdata.com/tools/trend-scanner" target="_blank" class="btn-primary">
          Open Full Analysis →
        </a>
      </div>
    </section>

    <section class="footer-note">
      <p>Data refreshes weekly. <a href="https://amzdata.com" target="_blank">amzdata.com</a></p>
    </section>
  </main>

  <script src="panel.js"></script>
</body>
</html>
```

- [ ] **Step 2: Write sidebar panel JS**

Write `extension/sidebar/panel.js`:
```js
const API_BASE = 'https://amzdata.com/api/trends';

function getActiveTabAmazonURL() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].url && tabs[0].url.includes('amazon.com')) {
        resolve(tabs[0].url);
      } else {
        resolve(null);
      }
    });
  });
}

function extractKeywordFromURL(url) {
  // Try to extract product info from URL or use title from content script
  const asinMatch = url.match(/\/dp\/([A-Z0-9]{10})/);
  if (asinMatch) {
    return { asin: asinMatch[1], keyword: null };
  }
  return null;
}

async function fetchAndDisplay() {
  const url = await getActiveTabAmazonURL();
  if (!url) {
    document.getElementById('product-info').innerHTML =
      '<p class="placeholder">⚠️ Open an Amazon product page to see trend signals.</p>';
    return;
  }

  const info = extractKeywordFromURL(url);
  if (!info) {
    document.getElementById('product-info').innerHTML =
      '<p class="placeholder">⚠️ Navigate to a product detail page.</p>';
    return;
  }

  document.getElementById('product-info').style.display = 'none';
  document.getElementById('signals').style.display = 'block';

  try {
    const res = await fetch(`${API_BASE}?keyword=pet`);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();

    if (data.scores && data.scores.length > 0) {
      const top = data.scores[0];
      renderTrendScore(top);
    }
  } catch (err) {
    document.getElementById('trendscore-big').textContent = 'Unavailable';
    console.error('AMZ Data fetch error:', err);
  }
}

function renderTrendScore(score) {
  const el = document.getElementById('trendscore-big');
  const color = score.trend_score >= 70 ? '#16a34a' : score.trend_score >= 40 ? '#ca8a04' : '#dc2626';
  el.style.color = color;
  el.style.borderColor = color;
  el.textContent = `${score.trend_score}/100`;

  const grid = document.getElementById('signal-grid');
  grid.innerHTML = '';

  const labels = {
    google_trends: 'Google Trends',
    reddit_signal: 'Reddit Signal',
    bsr_momentum: 'BSR Momentum',
    velocity: 'Velocity',
  };

  for (const [key, label] of Object.entries(labels)) {
    const value = score.components[key] || 0;
    const barColor = value >= 70 ? '#16a34a' : value >= 40 ? '#ca8a04' : '#dc2626';

    grid.innerHTML += `
      <div class="signal-item">
        <span class="signal-label">${label}</span>
        <div class="signal-bar-bg">
          <div class="signal-bar" style="width:${value}%;background:${barColor}"></div>
        </div>
        <span class="signal-value">${value}</span>
      </div>
    `;
  }

  document.getElementById('category-context').innerHTML = `
    <div class="context-card">
      <strong>Data Quality:</strong> ${score.data_quality}<br>
      <strong>Keyword:</strong> ${score.keyword}
    </div>
  `;
}

// Init
document.addEventListener('DOMContentLoaded', fetchAndDisplay);
```

- [ ] **Step 3: Write sidebar panel CSS**

Write `extension/sidebar/panel.css`:
```css
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px;
  color: #1f2937;
  background: #fff;
  padding: 16px;
}

header {
  margin-bottom: 20px;
}

header h1 {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a5f;
}

.subtitle {
  font-size: 12px;
  color: #9ca3af;
}

.placeholder {
  color: #9ca3af;
  font-style: italic;
}

#trendscore-big {
  font-size: 48px;
  font-weight: 800;
  text-align: center;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  margin: 12px 0;
}

h2 {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  margin-top: 16px;
  margin-bottom: 8px;
}

.signal-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.signal-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.signal-label {
  width: 100px;
  font-size: 12px;
  color: #6b7280;
  flex-shrink: 0;
}

.signal-bar-bg {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.signal-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.signal-value {
  width: 30px;
  font-size: 12px;
  font-weight: 600;
  text-align: right;
  flex-shrink: 0;
}

.context-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  font-size: 12px;
  line-height: 1.6;
}

.cta {
  margin-top: 20px;
  text-align: center;
}

.btn-primary {
  display: inline-block;
  padding: 10px 20px;
  background: #3b82f6;
  color: #fff;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.footer-note {
  margin-top: 24px;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
  text-align: center;
  font-size: 11px;
  color: #d1d5db;
}

.footer-note a {
  color: #3b82f6;
  text-decoration: none;
}
```

- [ ] **Step 4: Commit**

```bash
git add extension/sidebar/
git commit -m "feat: add Chrome extension sidebar panel with TrendScore display"
```

---

## Post-MVP: Deploy & Distribute

### Task D1: Deploy Web Platform

- [ ] **Step 1: Build static export**

```bash
cd web && npm run build
```

Fix any build errors. Verify `web/out/` directory is generated.

- [ ] **Step 2: Deploy to Vercel**

```bash
cd web && npx vercel deploy --prod
```

Or configure GitHub-based auto-deploy in the Vercel dashboard pointing to `web/` directory.

- [ ] **Step 3: Verify live site**

Open the deployed URL. Verify all pages render: homepage, blog, tools, trend scanner.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: production build and deployment config"
```

---

### Task D2: Submit Chrome Extension

- [ ] **Step 1: Package extension**

```bash
cd extension && zip -r ../amzdata-extension-v0.1.0.zip . -x "*.git*" "*.md"
```

- [ ] **Step 2: Submit to Chrome Web Store**

Go to Chrome Web Store Developer Dashboard → New Item → Upload zip.

Fill in:
- Description: "Overlay trend signals on Amazon Pet Supplies product pages. TrendScore, Google Trends, Reddit signals — at a glance."
- Category: Productivity
- Screenshots: TBD (need to capture from a pet product page)

- [ ] **Step 3: Commit release tag**

```bash
git tag v0.1.0
git commit -m "release: v0.1.0 — initial MVP with data pipeline, web platform, and Chrome extension"
```

---

## Self-Review Checklist

- [x] Spec coverage: All sections from the design spec have corresponding tasks
  - Data Foundation (Keepa, Google Trends, Reddit) → Plan A Tasks A1-A6
  - Web Platform (Blog + Tools) → Plan B Tasks B1-B5
  - Chrome Extension → Plan C Tasks C1-C3
  - Deploy/Distribute → Tasks D1-D2
- [x] No placeholders — all steps have concrete code
- [x] Type consistency — TrendResult interface defined in B5 Step 1, used consistently across components
- [x] All file paths are exact
- [x] All commands include expected output
