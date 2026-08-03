#!/usr/bin/env python3
"""Derive small, LLM-context-sized summary tables from the full 2024 Facebook
political ads CSV (same file used in Task 1/2). Standard library only.

The source file is 246,745 rows -- far too large to hand to a language model
in a chat context. This script rolls it up into two small "season"-shaped
tables that a language model can actually be handed directly:

- page_season_stats.csv: one row per advertiser page (~40 rows), analogous
  to a player's season stats -- ads run, total spend, reach, message mix,
  and a first-half/second-half spend split for "most improved" style
  questions.
- monthly_stats.csv: one row per calendar month of the campaign (~13 rows),
  analogous to a team's per-game log.

Both tables use exact arithmetic (midpoint of the source's lower/upper-bound
spend and impressions dictionaries, matching Task 1's approach) so they can
serve as ground truth once loaded.
"""

from __future__ import annotations

import ast
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SOURCE_CSV = Path("data/fb_ads_president_scored_anon.csv")
PAGE_TABLE_OUT = Path("data/page_season_stats.csv")
MONTH_TABLE_OUT = Path("data/monthly_stats.csv")
MIN_ADS_FOR_INCLUSION = 800  # keep the page table small: only pages with real volume
SEASON_YEAR = "2024"  # treat the 2024 election year as "the season" (99% of rows fall here)


def is_blankish(value: str) -> bool:
    return value is None or value.strip() == ""


def midpoint_from_bound(raw_token: str) -> float | None:
    if is_blankish(raw_token):
        return None
    try:
        decoded = ast.literal_eval(raw_token)
    except (ValueError, SyntaxError):
        return None
    if not isinstance(decoded, dict):
        return None
    lower = decoded.get("lower_bound")
    upper = decoded.get("upper_bound")
    try:
        lower = float(lower) if lower is not None else None
        upper = float(upper) if upper is not None else None
    except (TypeError, ValueError):
        return None
    if lower is None and upper is None:
        return None
    if lower is None:
        lower = upper
    if upper is None:
        upper = lower
    return (lower + upper) / 2


def date_from_text(raw_token: str) -> datetime | None:
    if is_blankish(raw_token):
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(raw_token.strip(), fmt)
        except ValueError:
            continue
    return None


def main() -> None:
    if not SOURCE_CSV.exists():
        raise SystemExit(f"Could not find {SOURCE_CSV}. See data/README.md for download instructions.")

    per_page = defaultdict(lambda: {
        "num_ads": 0,
        "total_spend": 0.0,
        "total_impressions": 0.0,
        "audience_sizes": [],
        "attack_count": 0,
        "advocacy_count": 0,
        "issue_count": 0,
        "dates": [],
        "spend_by_date": [],  # (date, spend) pairs for half-split
    })
    per_month = defaultdict(lambda: {"num_ads": 0, "total_spend": 0.0, "total_impressions": 0.0, "pages": set()})

    all_dates: list[datetime] = []

    with SOURCE_CSV.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            page_name = row.get("page_name") or "(missing page)"
            spend = midpoint_from_bound(row.get("spend", ""))
            impressions = midpoint_from_bound(row.get("impressions", ""))
            audience = midpoint_from_bound(row.get("estimated_audience_size", ""))
            start_date = date_from_text(row.get("ad_delivery_start_time", ""))
            if start_date is None or start_date.strftime("%Y") != SEASON_YEAR:
                continue  # restrict "the season" to the 2024 election year

            page = per_page[page_name]
            page["num_ads"] += 1
            if spend is not None:
                page["total_spend"] += spend
            if impressions is not None:
                page["total_impressions"] += impressions
            if audience is not None:
                page["audience_sizes"].append(audience)
            if row.get("illuminating_msg_type_attack") == "1":
                page["attack_count"] += 1
            if row.get("illuminating_msg_type_advocacy") == "1":
                page["advocacy_count"] += 1
            if row.get("illuminating_msg_type_issue") == "1":
                page["issue_count"] += 1
            if start_date is not None:
                page["dates"].append(start_date)
                page["spend_by_date"].append((start_date, spend or 0.0))
                all_dates.append(start_date)

                month_key = start_date.strftime("%Y-%m")
                month = per_month[month_key]
                month["num_ads"] += 1
                month["total_spend"] += spend or 0.0
                month["total_impressions"] += impressions or 0.0
                month["pages"].add(page_name)

    campaign_start, campaign_end = min(all_dates), max(all_dates)
    campaign_midpoint = campaign_start + (campaign_end - campaign_start) / 2

    # Page-level table, restricted to pages with enough volume to keep it small.
    page_rows = []
    for page_name, stats in per_page.items():
        if stats["num_ads"] < MIN_ADS_FOR_INCLUSION:
            continue
        first_half_spend = sum(s for d, s in stats["spend_by_date"] if d <= campaign_midpoint)
        second_half_spend = sum(s for d, s in stats["spend_by_date"] if d > campaign_midpoint)
        avg_audience = (sum(stats["audience_sizes"]) / len(stats["audience_sizes"])) if stats["audience_sizes"] else None
        page_rows.append({
            "page_name": page_name,
            "num_ads": stats["num_ads"],
            "total_spend": round(stats["total_spend"], 2),
            "total_impressions": round(stats["total_impressions"], 2),
            "avg_spend_per_ad": round(stats["total_spend"] / stats["num_ads"], 2),
            "avg_audience_size": round(avg_audience, 2) if avg_audience is not None else "",
            "pct_attack_ads": round(stats["attack_count"] / stats["num_ads"], 4),
            "pct_advocacy_ads": round(stats["advocacy_count"] / stats["num_ads"], 4),
            "pct_issue_ads": round(stats["issue_count"] / stats["num_ads"], 4),
            "first_ad_date": min(stats["dates"]).date().isoformat() if stats["dates"] else "",
            "last_ad_date": max(stats["dates"]).date().isoformat() if stats["dates"] else "",
            "first_half_spend": round(first_half_spend, 2),
            "second_half_spend": round(second_half_spend, 2),
        })

    page_rows.sort(key=lambda r: r["total_spend"], reverse=True)

    with PAGE_TABLE_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(page_rows[0].keys()))
        writer.writeheader()
        writer.writerows(page_rows)

    # Monthly table.
    month_rows = []
    for month_key, stats in sorted(per_month.items()):
        month_rows.append({
            "month": month_key,
            "num_ads": stats["num_ads"],
            "total_spend": round(stats["total_spend"], 2),
            "total_impressions": round(stats["total_impressions"], 2),
            "num_active_pages": len(stats["pages"]),
        })

    with MONTH_TABLE_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(month_rows[0].keys()))
        writer.writeheader()
        writer.writerows(month_rows)

    print(f"Campaign window: {campaign_start.date()} to {campaign_end.date()} (midpoint {campaign_midpoint.date()})")
    print(f"Wrote {PAGE_TABLE_OUT} with {len(page_rows)} pages (threshold: >= {MIN_ADS_FOR_INCLUSION} ads)")
    print(f"Wrote {MONTH_TABLE_OUT} with {len(month_rows)} months")


if __name__ == "__main__":
    main()
