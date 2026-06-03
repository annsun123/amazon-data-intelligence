"""
Scrape Amazon Best Sellers pages for the Review Moat analysis.
Uses Playwright for JS-rendered content. 10 categories × 100 products = 1,000 rows.

Output: ../data/raw/2026-06-01_amazon_best_sellers_review-moat.csv
"""
import csv
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright

# --- Config ---
CATEGORIES = [
    ("Electronics", "Best-Sellers-Electronics/zgbs/electronics", "172282"),
    ("Home & Kitchen", "Best-Sellers-Home-Kitchen/zgbs/home-garden", "1055398"),
    ("Sports & Outdoors", "Best-Sellers-Sports-Outdoors/zgbs/sporting-goods", "3375251"),
    ("Pet Supplies", "Best-Sellers-Pet-Supplies/zgbs/pet-supplies", "2975312011"),
    ("Baby", "Best-Sellers-Baby/zgbs/baby-products", "165796011"),
    ("Office Products", "Best-Sellers-Office-Products/zgbs/office-products", "1064954"),
    ("Tools & Home Improvement", "Best-Sellers-Tools-Home-Improvement/zgbs/hi", "228013"),
    ("Health & Household", "Best-Sellers-Health-Household/zgbs/hpc", "3760901"),
    ("Toys & Games", "Best-Sellers-Toys-Games/zgbs/toys-and-games", "165793011"),
    ("Kitchen & Dining", "Best-Sellers-Kitchen-Dining/zgbs/kitchen", "284507"),
]

# Resolve relative to this script file, not the working directory
OUTPUT_DIR = (Path(__file__).resolve().parent.parent / "data" / "raw")
TODAY = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = OUTPUT_DIR / f"{TODAY}_amazon_best_sellers_review-moat.csv"
PAGE_TIMEOUT = 60_000  # 60 seconds
MIN_CARDS_THRESHOLD = 40  # warn if fewer than this many cards per page


# --- Parsing Helpers (unchanged) ---

def parse_int(text: str) -> int | None:
    if not text:
        return None
    try:
        return int(text.strip().replace(",", ""))
    except ValueError:
        return None


def parse_float(text: str) -> float | None:
    """Extract first numeric value from text like '4.4 out of 5 stars'."""
    if not text:
        return None
    match = re.search(r"(\d+\.?\d*)", str(text).strip())
    return float(match.group(1)) if match else None


def parse_price(text: str) -> float | None:
    """
    Parse price text. Handles: '$24.99', '$19.99 - $29.99', 'JPY 1,910', '₹499'.
    For ranges, returns the minimum.
    Returns None if unparseable.
    """
    if not text:
        return None
    # Try USD first
    usd = re.findall(r"\$(\d+\.?\d*)", text)
    if usd:
        return min(float(p) for p in usd)
    # Try numeric patterns (could be JPY, INR, etc.)
    nums = re.findall(r"(\d[\d,]*\.?\d*)", text)
    if nums:
        return min(float(n.replace(",", "")) for n in nums)
    return None


# --- Card-Level Extraction Helpers ---

def extract_asin_from_card(card) -> str | None:
    """
    Two-tier ASIN extraction:
    1. data-asin attribute on a descendant div
    2. /dp/XXXXXXXXXX/ pattern in any link href within the card
    """
    # Tier 1: data-asin on descendant
    asin_div = card.query_selector("div[data-asin]")
    if asin_div:
        asin = (asin_div.get_attribute("data-asin") or "").strip()
        if asin and len(asin) == 10:
            return asin

    # Tier 2: parse from /dp/ link href
    links = card.query_selector_all("a[href*='/dp/']")
    for link in links:
        href = link.get_attribute("href") or ""
        match = re.search(r"/dp/([A-Z0-9]{10})", href)
        if match:
            return match.group(1)

    return None


def extract_title_from_card(card) -> str:
    """
    Four-tier title extraction, all using stable selectors:
    1. img[alt] — most reliable, present on every product card
    2. div[class*="line-clamp"] — semantic substring survives CSS rehash
    3. a[href*="/dp/"] title attribute
    4. Longest plain text block that doesn't look like price/rating/review count
    """
    # Tier 1: product image alt text
    img = card.query_selector("img[alt]")
    if img:
        alt = (img.get_attribute("alt") or "").strip()
        if alt and len(alt) >= 10:
            return alt

    # Tier 2: line-clamp div (Amazon's title truncation)
    clamp = card.query_selector("div[class*='line-clamp']")
    if clamp:
        text = clamp.inner_text().strip()
        if text and len(text) >= 10:
            return text

    # Tier 3: /dp/ link title attribute or inner text
    link = card.query_selector("a[href*='/dp/']")
    if link:
        title_attr = (link.get_attribute("title") or "").strip()
        if title_attr and len(title_attr) >= 10:
            return title_attr
        link_text = link.inner_text().strip()
        if link_text and len(link_text) >= 10:
            return link_text

    # Tier 4: find longest text block that isn't price/rating/review
    all_elements = card.query_selector_all("*")
    candidates = []
    for el in all_elements:
        text = (el.inner_text() or "").strip()
        if not text or len(text) < 10:
            continue
        # Exclude elements that look like non-title data
        lower = text.lower()
        if any(kw in lower for kw in ("out of 5", "ratings", "sponsored", "$")):
            continue
        candidates.append(text)

    # Return the longest remaining text (likely the title)
    if candidates:
        return max(candidates, key=len)

    return ""


def extract_rating_from_card(card) -> float | None:
    """
    Two-tier rating extraction:
    1. span.a-icon-alt — stable semantic class (primary, works in 597/600 rows)
    2. a[aria-label*='stars'] — fallback via review link aria-label
    """
    # Tier 1: a-icon-alt span
    el = card.query_selector("span.a-icon-alt")
    if el:
        rating = parse_float(el.inner_text())
        if rating is not None:
            return rating

    # Tier 2: aria-label on review/stars link
    review_link = card.query_selector("a[aria-label*='stars'], a[aria-label*='out of']")
    if review_link:
        aria = (review_link.get_attribute("aria-label") or "").strip()
        # "4.4 out of 5 stars, 276,018 ratings" → 4.4
        match = re.search(r"(\d+\.?\d*)\s*out of", aria)
        if match:
            return float(match.group(1))

    return None


def extract_review_count_from_card(card) -> int:
    """
    Three-tier review count extraction:
    1. a[aria-label*='ratings'] — parse from aria-label ("276,018 ratings" → 276018)
    2. Review link's a-size-small span — direct number text
    3. Card-wide text scan for "X,XXX ratings" pattern
    Default: 0 (not None — distinguishes "no reviews" from "failed to extract")
    """
    # Tier 1: aria-label on the review link
    review_link = card.query_selector(
        "a[aria-label*='ratings'], a[aria-label*='stars']"
    )
    if review_link:
        aria = (review_link.get_attribute("aria-label") or "").strip()
        match = re.search(r"(\d[\d,]+)\s*ratings?", aria)
        if match:
            return parse_int(match.group(1)) or 0

    # Tier 2: span.a-size-small inside a product-reviews link
    count_el = card.query_selector(
        "a[href*='product-reviews'] span.a-size-small, "
        "a[href*='customerReviews'] span.a-size-small"
    )
    if count_el:
        count = parse_int(count_el.inner_text())
        if count is not None:
            return count

    # Tier 3: card-wide text scan for ratings count
    card_text = card.inner_text() or ""
    match = re.search(r"(\d[\d,]*)\s*ratings?", card_text, re.IGNORECASE)
    if match:
        return parse_int(match.group(1)) or 0

    # Default: genuinely zero reviews
    return 0


def extract_price_from_card(card) -> tuple[float | None, str]:
    """
    Multi-tier price extraction using stable selectors and text patterns:
    1. span.a-price span.a-offscreen — Amazon's standard price component
    2. span.a-price — the whole price component (fallback if offscreen missing)
    3. span.a-color-price — semantic class on Best Sellers cards
    4. Any span containing '$' in text
    5. Card-wide regex for $NNN or NNN price pattern
    Returns (parsed_float, raw_text).
    """
    # Tier 1: Amazon's standard price component (offscreen variant)
    offscreen = card.query_selector("span.a-price span.a-offscreen")
    if offscreen:
        text = offscreen.inner_text().strip()
        parsed = parse_price(text)
        if parsed is not None:
            return parsed, text

    # Tier 2: Whole a-price component (may contain multi-part prices)
    aprice = card.query_selector("span.a-price")
    if aprice:
        text = aprice.inner_text().strip()
        parsed = parse_price(text)
        if parsed is not None:
            return parsed, text

    # Tier 3: a-color-price (semantic, not hashed, used on Best Sellers)
    price_el = card.query_selector("span.a-color-price")
    if price_el:
        text = price_el.inner_text().strip()
        parsed = parse_price(text)
        if parsed is not None:
            return parsed, text

    # Tier 4: any span with dollar sign
    all_spans = card.query_selector_all("span")
    for span in all_spans:
        text = span.inner_text().strip()
        if "$" in text:
            parsed = parse_price(text)
            if parsed is not None:
                return parsed, text

    # Tier 5: card-wide regex for dollar amount (USD)
    card_text = card.inner_text() or ""
    match = re.search(r"\$\d[\d,]*\.?\d*", card_text)
    if match:
        parsed = parse_price(match.group(0))
        if parsed is not None:
            return parsed, match.group(0)

    # Tier 6: card-wide regex for any currency (JPY, EUR, GBP prefix or plain numbers near price indicators)
    for pattern in [
        r"(?:JPY|EUR|GBP)\s*\d[\d,]*\.?\d*",
        r"\d[\d,]*\.?\d*\s*(?:JPY|EUR|GBP)",
        r"¥\s*\d[\d,]*",
    ]:
        match = re.search(pattern, card_text)
        if match:
            parsed = parse_price(match.group(0))
            if parsed is not None:
                return parsed, match.group(0)

    return None, ""


def extract_is_sponsored_from_card(card) -> bool:
    """Text-based sponsored check — no selector dependency."""
    return "Sponsored" in (card.inner_text() or "")


# --- Main Scraper ---

def scrape_category(page, cat_name: str, slug: str, cat_id: str) -> list[dict]:
    """Scrape pages 1+2 of a category Best Sellers list. Returns up to 100 product dicts."""
    rows = []

    for pg in (1, 2):
        # Fixed URL: no category ID inside the ref parameter
        url = (
            f"https://www.amazon.com/{slug}"
            f"/ref=zg_bs_pg_{pg}?_encoding=UTF8&pg={pg}"
        )
        print(f"  Page {pg}: {url[:80]}...")

        # Navigate
        try:
            page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
        except Exception as e:
            print(f"    [ERR] Page navigation failed: {e}")
            continue

        # Wait for product cards to populate — try gridItemRoot or data-asin
        try:
            page.wait_for_function(
                "document.querySelectorAll('div[id^=\"gridItemRoot\"], div[data-asin]').length >= 40",
                timeout=15_000,
            )
        except Exception:
            print("    [WARN] Slow grid load, continuing anyway...")

        # Scroll progressively to trigger ALL lazy-loaded content
        # Amazon lazy-loads cards as you scroll down — one scroll isn't always enough
        for step in range(3):
            page.evaluate(f"window.scrollTo(0, document.body.scrollHeight * {(step + 1) / 3})")
            page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1_500)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        # Union-based card discovery: combine gridItemRoot + data-asin containers
        grid_cards = page.query_selector_all("div[id^='gridItemRoot']")
        asin_cards = page.query_selector_all("div[data-asin]")
        print(f"    gridItemRoot={len(grid_cards)}, data-asin={len(asin_cards)}")

        # Merge by unique ASIN, keeping gridItemRoot containers when available
        # (they are more complete) but adding any missing ASINs from data-asin
        cards_by_asin = {}
        for card in grid_cards:
            asin = extract_asin_from_card(card)
            if asin:
                cards_by_asin[asin] = card
        for card in asin_cards:
            asin = extract_asin_from_card(card)
            if asin and asin not in cards_by_asin:
                cards_by_asin[asin] = card
        cards = list(cards_by_asin.values())
        print(f"    Merged: {len(cards)} unique product cards")

        if len(cards) < MIN_CARDS_THRESHOLD:
            print(f"    [WARN] Only {len(cards)} cards on page {pg} (expected >=50)")

        # Extract fields from each card
        for card in cards:
            asin = extract_asin_from_card(card)
            if not asin:
                continue  # genuinely unidentifiable card

            # Rank badge
            rank_el = card.query_selector("span.zg-bdg-text")
            rank_text = rank_el.inner_text() if rank_el else ""
            rank = parse_int(rank_text.replace("#", ""))

            # Extract all fields using pattern-based helpers
            title = extract_title_from_card(card)
            rating = extract_rating_from_card(card)
            review_count = extract_review_count_from_card(card)
            price, price_raw = extract_price_from_card(card)
            is_sponsored = extract_is_sponsored_from_card(card)

            rows.append({
                "category": cat_name,
                "bsr_rank": rank,
                "asin": asin,
                "title": title,
                "rating": rating,
                "review_count": review_count,
                "price": price,
                "price_raw": price_raw,
                "is_sponsored": is_sponsored,
            })

        # Delay between pages (randomized, polite)
        if pg < 2:
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

    # Deduplicate by ASIN, keep lowest rank
    seen = {}
    for r in rows:
        a = r["asin"]
        if a not in seen or (
            r["bsr_rank"] is not None
            and (seen[a]["bsr_rank"] is None or r["bsr_rank"] < seen[a]["bsr_rank"])
        ):
            seen[a] = r
    rows = sorted(seen.values(), key=lambda r: r["bsr_rank"] or 999)

    return rows


def main():
    print("=== Amazon Best Sellers Scraper (Playwright) ===")
    print(f"Target: {len(CATEGORIES)} categories × 100 products = 1,000 rows")
    print(f"Output: {OUTPUT_FILE}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    scraped_at = datetime.now(timezone.utc).isoformat()
    all_rows = []
    stats = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            locale="en-US",
            timezone_id="America/New_York",
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        for cat_name, slug, cat_id in CATEGORIES:
            print(f"[{cat_name}]")
            try:
                cat_rows = scrape_category(page, cat_name, slug, cat_id)
                all_rows.extend(cat_rows)
                stats.append(f"  {cat_name}: {len(cat_rows)} products")
                print(f"  -> {len(cat_rows)} products collected")
            except Exception as e:
                print(f"  [FAILED]: {e}", file=sys.stderr)
                stats.append(f"  {cat_name}: FAILED — {e}")

            # Randomized delay between categories
            if cat_name != CATEGORIES[-1][0]:
                delay = random.uniform(2.0, 5.0)
                time.sleep(delay)

        browser.close()

    # --- Save ---
    fieldnames = [
        "category", "bsr_rank", "asin", "title", "rating",
        "review_count", "price", "price_raw", "is_sponsored", "scraped_at",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in all_rows:
            row["scraped_at"] = scraped_at
            writer.writerow(row)

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"Scrape Complete — {len(all_rows)} total products")
    print(f"Output: {OUTPUT_FILE}")
    for s in stats:
        print(s)

    # --- Data Quality ---
    if not all_rows:
        print("\n[WARN] No data collected. Exiting.")
        return

    null_titles = sum(1 for r in all_rows if not r["title"])
    null_ratings = sum(1 for r in all_rows if r["rating"] is None)
    null_prices = sum(1 for r in all_rows if r["price"] is None)
    zero_reviews = sum(1 for r in all_rows if (r["review_count"] or 0) == 0)
    sponsored = sum(1 for r in all_rows if r["is_sponsored"])
    num_categories = len(set(r["category"] for r in all_rows))

    print(f"\nQuality: {num_categories} categories")
    print(f"  Titles:    {len(all_rows) - null_titles}/{len(all_rows)} populated "
          f"({100 * (len(all_rows) - null_titles) / len(all_rows):.0f}%)")
    print(f"  Ratings:   {len(all_rows) - null_ratings}/{len(all_rows)} populated "
          f"({100 * (len(all_rows) - null_ratings) / len(all_rows):.0f}%)")
    print(f"  Reviews:   {len(all_rows) - zero_reviews}/{len(all_rows)} non-zero "
          f"({100 * (len(all_rows) - zero_reviews) / len(all_rows):.0f}%)")
    print(f"  Prices:    {len(all_rows) - null_prices}/{len(all_rows)} populated "
          f"({100 * (len(all_rows) - null_prices) / len(all_rows):.0f}%)")
    print(f"  Sponsored: {sponsored}")
    print(f"  Duplicates: {len(all_rows) - len(set(r['asin'] for r in all_rows))}")

    # Sample titles to verify quality
    sample_titles = [r["title"] for r in all_rows[:5] if r["title"]]
    print(f"\nSample titles: {sample_titles[:3]}")


if __name__ == "__main__":
    main()
