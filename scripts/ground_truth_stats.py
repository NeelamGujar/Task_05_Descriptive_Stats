#!/usr/bin/env python3
"""Compute the trustworthy ground-truth answer key for the two small summary
tables (page_season_stats.csv, monthly_stats.csv) that get handed to the LLM.
Standard library only -- this is the answer key everything else is checked
against, so it deliberately does not depend on pandas/polars.

Writes ground_truth/answer_key.md.
"""

from __future__ import annotations

import csv
from pathlib import Path

PAGE_TABLE = Path("data/page_season_stats.csv")
MONTH_TABLE = Path("data/monthly_stats.csv")
OUTPUT = Path("ground_truth/answer_key.md")


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(row: dict, key: str) -> float:
    value = row.get(key, "")
    return float(value) if value not in ("", None) else 0.0


def main() -> None:
    pages = load_rows(PAGE_TABLE)
    months = load_rows(MONTH_TABLE)

    for row in pages:
        for key in ("num_ads", "total_spend", "total_impressions", "avg_spend_per_ad", "avg_audience_size",
                    "pct_attack_ads", "pct_advocacy_ads", "pct_issue_ads", "first_half_spend", "second_half_spend"):
            row[key] = num(row, key)
        row["spend_change"] = row["second_half_spend"] - row["first_half_spend"]
        row["spend_change_pct"] = (
            (row["spend_change"] / row["first_half_spend"] * 100) if row["first_half_spend"] > 0 else None
        )

    for row in months:
        for key in ("num_ads", "total_spend", "total_impressions", "num_active_pages"):
            row[key] = num(row, key)

    total_spend_all = sum(r["total_spend"] for r in pages)
    total_impressions_all = sum(r["total_impressions"] for r in pages)
    top_by_spend = sorted(pages, key=lambda r: r["total_spend"], reverse=True)
    top_by_impressions = sorted(pages, key=lambda r: r["total_impressions"], reverse=True)
    top_by_attack_rate = sorted(pages, key=lambda r: r["pct_attack_ads"], reverse=True)
    top_by_avg_spend_per_ad = sorted(pages, key=lambda r: r["avg_spend_per_ad"], reverse=True)
    improved = [r for r in pages if r["first_half_spend"] > 0]
    most_improved_abs = sorted(pages, key=lambda r: r["spend_change"], reverse=True)
    most_improved_pct = sorted(
        [r for r in improved], key=lambda r: r["spend_change_pct"], reverse=True
    )

    top_month_by_spend = sorted(months, key=lambda r: r["total_spend"], reverse=True)[0]
    top_month_by_impressions = sorted(months, key=lambda r: r["total_impressions"], reverse=True)[0]
    top_month_by_ads = sorted(months, key=lambda r: r["num_ads"], reverse=True)[0]

    lines: list[str] = []
    lines.append("# Ground Truth Answer Key")
    lines.append("")
    lines.append("Computed directly from `data/page_season_stats.csv` and `data/monthly_stats.csv` by "
                 "`scripts/ground_truth_stats.py`. This is the answer key Phase A/B LLM responses are checked against.")
    lines.append("")
    lines.append("## Dataset shape")
    lines.append(f"- Page table: {len(pages)} pages (advertisers with >=800 ads in the 2024 season)")
    lines.append(f"- Month table: {len(months)} months (Jan-Nov 2024)")
    lines.append(f"- Total spend across all 32 pages: ${total_spend_all:,.2f}")
    lines.append(f"- Total impressions across all 32 pages: {total_impressions_all:,.0f}")
    lines.append("")

    lines.append("## Factual answers (Phase A)")
    lines.append("")
    lines.append(f"- **Number of pages in the table:** {len(pages)}")
    lines.append(f"- **Number of months in the table:** {len(months)}")
    lines.append(f"- **Page with the most total spend:** {top_by_spend[0]['page_name']} "
                 f"(${top_by_spend[0]['total_spend']:,.2f})")
    lines.append(f"- **Page with the most total impressions:** {top_by_impressions[0]['page_name']} "
                 f"({top_by_impressions[0]['total_impressions']:,.0f})")
    lines.append(f"- **Page with the highest average spend per ad:** {top_by_avg_spend_per_ad[0]['page_name']} "
                 f"(${top_by_avg_spend_per_ad[0]['avg_spend_per_ad']:,.2f}/ad)")
    lines.append(f"- **Page with the highest attack-ad rate:** {top_by_attack_rate[0]['page_name']} "
                 f"({top_by_attack_rate[0]['pct_attack_ads']:.1%})")
    lines.append(f"- **Month with the highest combined spend:** {top_month_by_spend['month']} "
                 f"(${top_month_by_spend['total_spend']:,.2f})")
    lines.append(f"- **Month with the highest combined impressions:** {top_month_by_impressions['month']} "
                 f"({top_month_by_impressions['total_impressions']:,.0f})")
    lines.append(f"- **Month with the most ads run:** {top_month_by_ads['month']} "
                 f"({top_month_by_ads['num_ads']:,.0f} ads)")
    lines.append("")
    lines.append("Top 5 pages by total spend:")
    for row in top_by_spend[:5]:
        lines.append(f"  - {row['page_name']}: ${row['total_spend']:,.2f} across {row['num_ads']:,.0f} ads")
    lines.append("")

    lines.append("## Derived metrics (Phase B)")
    lines.append("")
    lines.append("**Metric 1 -- \"Most improved page\":** largest *absolute* increase in total spend from the "
                 "first half of the season (2024-01-01 to 2024-06-03) to the second half (2024-06-04 to "
                 "2024-11-05).")
    lines.append("")
    lines.append("Top 5 by absolute spend increase (second half minus first half):")
    for row in most_improved_abs[:5]:
        lines.append(
            f"  - {row['page_name']}: +${row['spend_change']:,.2f} "
            f"(first half ${row['first_half_spend']:,.2f} -> second half ${row['second_half_spend']:,.2f})"
        )
    lines.append("")
    lines.append("**Metric 2 -- \"Most improved page (relative)\":** same split, but as a percentage change, "
                 "restricted to pages with nonzero first-half spend (percentage change is undefined for pages "
                 "that started from zero).")
    lines.append("")
    lines.append("Top 5 by percentage spend increase:")
    for row in most_improved_pct[:5]:
        lines.append(
            f"  - {row['page_name']}: {row['spend_change_pct']:+.1f}% "
            f"(first half ${row['first_half_spend']:,.2f} -> second half ${row['second_half_spend']:,.2f})"
        )
    lines.append("")
    lines.append("**Metric 3 -- \"Game changer\" (influence score):** "
                 "`influence_score = (total_spend / total_spend_all) * (total_impressions / total_impressions_all) "
                 "* 100`, i.e. the product of a page's share of total spend and its share of total impressions, "
                 "scaled by 100. Rewards pages that combine *both* heavy investment and heavy reach, rather than "
                 "either alone (a page could have huge spend but poor reach, or vice versa).")
    lines.append("")
    for row in pages:
        row["influence_score"] = (row["total_spend"] / total_spend_all) * (row["total_impressions"] / total_impressions_all) * 100
    top_influence = sorted(pages, key=lambda r: r["influence_score"], reverse=True)
    lines.append("Top 5 by influence score:")
    for row in top_influence[:5]:
        lines.append(f"  - {row['page_name']}: influence_score={row['influence_score']:.4f}")
    lines.append("")

    output_path = OUTPUT
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    main()
