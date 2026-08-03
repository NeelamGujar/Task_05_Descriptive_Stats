# Ground Truth Answer Key

Computed directly from `data/page_season_stats.csv` and `data/monthly_stats.csv` by `scripts/ground_truth_stats.py`. This is the answer key Phase A/B LLM responses are checked against.

## Dataset shape
- Page table: 32 pages (advertisers with >=800 ads in the 2024 season)
- Month table: 11 months (Jan-Nov 2024)
- Total spend across all 32 pages: $179,895,924.50
- Total impressions across all 32 pages: 7,004,792,465

## Factual answers (Phase A)

- **Number of pages in the table:** 32
- **Number of months in the table:** 11
- **Page with the most total spend:** Kamala Harris ($82,704,864.50)
- **Page with the most total impressions:** Kamala Harris (2,979,511,669)
- **Page with the highest average spend per ad:** Future Forward ($3,526.98/ad)
- **Page with the highest attack-ad rate:** Liberators United (78.6%)
- **Month with the highest combined spend:** 2024-10 ($85,882,264.00)
- **Month with the highest combined impressions:** 2024-10 (3,674,073,772)
- **Month with the most ads run:** 2024-10 (85,172 ads)

Top 5 pages by total spend:
  - Kamala Harris: $82,704,864.50 across 55,171 ads
  - Joe Biden: $21,281,156.00 across 12,088 ads
  - Donald J. Trump: $19,101,332.50 across 22,935 ads
  - Kamala HQ: $8,149,218.00 across 7,564 ads
  - Tim Walz: $7,637,759.50 across 6,581 ads

## Derived metrics (Phase B)

**Metric 1 -- "Most improved page":** largest *absolute* increase in total spend from the first half of the season (2024-01-01 to 2024-06-03) to the second half (2024-06-04 to 2024-11-05).

Top 5 by absolute spend increase (second half minus first half):
  - Kamala Harris: +$78,738,847.50 (first half $1,983,008.50 -> second half $80,721,856.00)
  - Donald J. Trump: +$15,096,898.50 (first half $2,002,217.00 -> second half $17,099,115.50)
  - Kamala HQ: +$8,149,218.00 (first half $0.00 -> second half $8,149,218.00)
  - Tim Walz: +$7,637,759.50 (first half $0.00 -> second half $7,637,759.50)
  - The Daily Scroll: +$5,454,861.50 (first half $342,879.00 -> second half $5,797,740.50)

**Metric 2 -- "Most improved page (relative)":** same split, but as a percentage change, restricted to pages with nonzero first-half spend (percentage change is undefined for pages that started from zero).

Top 5 by percentage spend increase:
  - Forward Blue: +144534.6% (first half $595.00 -> second half $860,576.00)
  - Working America: +88436.8% (first half $2,887.00 -> second half $2,556,056.00)
  - Kamala Harris: +3970.7% (first half $1,983,008.50 -> second half $80,721,856.00)
  - Truly American: +1614.0% (first half $29,133.00 -> second half $499,341.00)
  - The Daily Scroll: +1590.9% (first half $342,879.00 -> second half $5,797,740.50)

**Metric 3 -- "Game changer" (influence score):** `influence_score = (total_spend / total_spend_all) * (total_impressions / total_impressions_all) * 100`, i.e. the product of a page's share of total spend and its share of total impressions, scaled by 100. Rewards pages that combine *both* heavy investment and heavy reach, rather than either alone (a page could have huge spend but poor reach, or vice versa).

Top 5 by influence score:
  - Kamala Harris: influence_score=19.5551
  - Joe Biden: influence_score=1.0976
  - Donald J. Trump: influence_score=0.9732
  - The Daily Scroll: influence_score=0.2180
  - Kamala HQ: influence_score=0.1630


## Post-hoc metric (surfaced during testing, not pre-defined)

Both subject agents independently invented an "impressions per dollar" efficiency ratio when
answering the Phase B advisory question, despite not being asked to. Ground truth for that ratio
across all 32 pages (`total_impressions / total_spend`), top 7:

- Americans for Prosperity: 115.57 impressions/$ (spend $1,002,428.00)
- Headlines 2024: 100.64 impressions/$ (spend $740,868.50)
- Working America: 94.38 impressions/$ (spend $2,558,943.00)
- The Voices of Today: 75.09 impressions/$ (spend $2,294,081.00)
- The Daily Scroll: 72.86 impressions/$ (spend $6,140,619.50)
- I Love My Freedom: 70.74 impressions/$ (spend $394,053.00)
- ParentsTogether Action: 69.83 impressions/$ (spend $881,144.50)

The true top page by this ratio is **Americans for Prosperity**, not Working America. See
`phase_b/prompt_log.md` for how each subject agent's answer compared.
