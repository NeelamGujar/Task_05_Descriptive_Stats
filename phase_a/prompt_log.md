# Phase A Prompt-and-Response Log

**Model and version:** Claude Sonnet 5 (`claude-sonnet-5`), via two isolated subagent instances
spawned within Claude Code, each given a fresh context with no memory of how the ground truth was
computed (i.e. each was genuinely blind to the answer key, not just told not to peek).

**Data handed to the model:** the two derived summary tables (`page_season_stats.csv`,
`monthly_stats.csv`), pasted directly as raw CSV text inside the prompt -- see
`scripts/build_summary_tables.py` for how they were derived from the full 246,745-row ads dataset.

**Two conditions, run in parallel with identical questions:**

- **Conversational mode**: instructed to use *no tools whatsoever* -- no Bash, no code execution,
  no file access -- and to reason purely over the pasted table text, showing manual arithmetic in
  prose. This simulates a plain chat LLM with no code interpreter.
- **Code-execution mode**: given the actual file paths on disk and instructed to write and run
  Python (pandas) to compute every answer, rather than eyeballing values.

Full raw transcripts are below, verbatim from each subagent's response.

---

## Question set (asked identically to both modes)

1. How many pages (advertisers) are in Table 1?
2. How many months does Table 2 cover?
3. Which page had the highest total_spend?
4. Which page had the highest total_impressions?
5. What was the avg_spend_per_ad for "Donald J. Trump"?
6. Which month had the highest total_spend?
7. Which page had the highest pct_attack_ads?
8. What is the SUM of total_spend across all 32 pages in Table 1?
9. Which page had the largest absolute increase in spend from first_half_spend to second_half_spend?
10. Rank the top 3 months in Table 2 by num_active_pages, highest first.

## Verdict table (checked against `ground_truth/answer_key.md`)

| # | Question | Ground truth | Conversational mode | Code-execution mode |
|---|---|---|---|---|
| 1 | # pages | 32 | 32 -- correct | 32 -- correct |
| 2 | # months | 11 | 11 -- correct | 11 -- correct |
| 3 | Top page by total_spend | Kamala Harris ($82,704,864.50) | Kamala Harris -- correct | Kamala Harris -- correct |
| 4 | Top page by total_impressions | Kamala Harris (2,979,511,669) | Kamala Harris -- correct | Kamala Harris -- correct |
| 5 | Trump avg_spend_per_ad | $832.85 | $832.85 -- correct | $832.85 -- correct (also correctly noted the "Lara Trump" row is a different page and not what was asked) |
| 6 | Top month by spend | 2024-10 ($85,882,264.00) | 2024-10 -- correct | 2024-10 -- correct |
| 7 | Top page by pct_attack_ads | Liberators United (0.7856) | Liberators United -- correct | Liberators United -- correct |
| 8 | Sum of total_spend, 32 pages | $179,895,924.50 | $179,895,924.50 -- **exactly correct**, via a full manual running-sum shown in its reasoning | $179,895,924.50 -- correct (`df1.total_spend.sum()`) |
| 9 | Biggest absolute spend increase | Kamala Harris (+$78,738,847.50) | Kamala Harris, +$78,738,847.5 -- correct | Kamala Harris, +$78,738,847.50 -- correct |
| 10 | Top 3 months by active pages | Oct (1,261), Aug (915), Jul (911) | Oct, Aug, Jul -- correct, exact numbers | Oct, Aug, Jul -- correct, exact numbers |

**Result: 10/10 correct in both modes.** This is itself a finding worth noting -- see
`README.md` for discussion. The standout result is Q8: manually summing 32 seven/eight-digit
decimal numbers in plain text, with no calculator, produced the *exact* correct total in the
conversational-mode run. That is not guaranteed to replicate reliably (see Research Questions
discussion in the README), but it did not fail here.

## Full raw transcript -- Conversational mode (no tools)

```
Q: 1. How many pages (advertisers) are in Table 1?
A: 32
Reasoning: Counted the data rows in Table 1 (one row per page_name).
Confidence: high

Q: 2. How many months does Table 2 cover?
A: 11 months (2024-01 through 2024-11)
Reasoning: Counted rows in Table 2.
Confidence: high

Q: 3. Which page had the highest total_spend?
A: Kamala Harris ($82,704,864.5)
Reasoning: Single-column lookup/scan across all 32 rows; this value is far larger than the next highest (Joe Biden, $21,281,156.0).
Confidence: high

Q: 4. Which page had the highest total_impressions?
A: Kamala Harris (2,979,511,669.0)
Reasoning: Single-column scan; next closest is Joe Biden at ~649.9M, so Harris is far ahead.
Confidence: high

Q: 5. What was the avg_spend_per_ad for "Donald J. Trump"?
A: $832.85
Reasoning: Direct lookup of a single cell.
Confidence: high

Q: 6. Which month had the highest total_spend?
A: 2024-10 ($85,882,264.0)
Reasoning: Scanned the 11 monthly total_spend values; October is clearly the largest (next highest is September at $44,378,253.5).
Confidence: high

Q: 7. Which page had the highest pct_attack_ads?
A: Liberators United (0.7856)
Reasoning: Scanned all 32 pct_attack_ads values; close competitors were Right For America PAC (0.7751) and Americans for Prosperity (0.5764), but Liberators United was highest.
Confidence: high

Q: 8. What is the SUM of total_spend across all 32 pages in Table 1?
A: approximately $179,895,924.5
Reasoning: Manually added all 32 total_spend values in a running cumulative sum (shown in my work):
82,704,864.5 -> 103,986,020.5 -> 123,087,353.0 -> 131,236,571.0 -> 138,874,330.5 -> 145,014,950.0 ->
149,282,595.0 -> 153,529,093.5 -> 156,797,622.0 -> 159,429,594.5 -> 161,988,537.5 -> 164,397,451.0 ->
166,691,532.0 -> 168,349,442.0 -> 169,729,654.5 -> 171,080,711.5 -> 172,282,475.0 -> 173,284,903.0 ->
174,166,047.5 -> 175,027,218.5 -> 175,847,886.0 -> 176,588,754.5 -> 177,258,866.0 -> 177,787,340.0 ->
178,312,018.5 -> 178,706,071.5 -> 179,040,280.5 -> 179,360,434.0 -> 179,632,197.5 -> 179,751,365.5 ->
179,823,657.0 -> 179,895,924.5
Confidence: medium (manual 32-row summation -- arithmetic slip is plausible; would flag for a calculator double-check)

Q: 9. Which page had the largest absolute increase in spend from first_half_spend to second_half_spend?
A: Kamala Harris, an increase of $78,738,847.5 (from $1,983,008.5 to $80,721,856.0)
Reasoning: Computed (second_half - first_half) for each page; Harris's increase (~$78.7M) dwarfs the
next largest (Trump, ~$15.1M, and Kamala HQ/Tim Walz at ~$8.1M/$7.6M since they started at $0).
Confidence: high

Q: 10. Rank the top 3 months in Table 2 by num_active_pages, highest first.
A: 1st: 2024-10 (1,261 pages), 2nd: 2024-08 (915 pages), 3rd: 2024-07 (911 pages)
Reasoning: Compared all 11 num_active_pages values (543, 680, 652, 573, 687, 657, 911, 915, 877, 1261,
14) and ranked the top three; September (877) was close to but below July/August.
Confidence: high
```

## Full raw transcript -- Code-execution mode

```
Q: How many pages (advertisers) are in Table 1?
Code/approach: len(df1)
A: 32
Confidence: high

Q: How many months does Table 2 cover?
Code/approach: len(df2)
A: 11
Confidence: high

Q: Which page had the highest total_spend?
Code/approach: df1.loc[df1.total_spend.idxmax()]
A: Kamala Harris, with total_spend = $82,704,864.50
Confidence: high

Q: Which page had the highest total_impressions?
Code/approach: df1.loc[df1.total_impressions.idxmax()]
A: Kamala Harris, with total_impressions = 2,979,511,669
Confidence: high

Q: What was the avg_spend_per_ad for "Donald J. Trump"?
Code/approach: filtered rows containing "Trump" (case-insensitive)
A: Donald J. Trump = $832.85 (note: there is also a separate row "Lara Trump" = $1,283.92, which is a
different page and not what was asked)
Confidence: high

Q: Which month had the highest total_spend?
Code/approach: df2.loc[df2.total_spend.idxmax()]
A: 2024-10 (October 2024), with total_spend = $85,882,264.00
Confidence: high

Q: Which page had the highest pct_attack_ads?
Code/approach: df1.loc[df1.pct_attack_ads.idxmax()]
A: Liberators United, with pct_attack_ads = 0.7856 (78.56%)
Confidence: high

Q: What is the SUM of total_spend across all 32 pages in Table 1?
Code/approach: df1.total_spend.sum()
A: $179,895,924.50
Confidence: high

Q: Which page had the largest absolute increase in spend from first_half_spend to second_half_spend?
Code/approach: computed spend_increase = second_half_spend - first_half_spend, took idxmax
A: Kamala Harris -- first_half_spend = $1,983,008.50, second_half_spend = $80,721,856.00,
increase = $78,738,847.50
Confidence: high

Q: Rank the top 3 months in Table 2 by num_active_pages, highest first.
Code/approach: df2.sort_values('num_active_pages', ascending=False).head(3)
A:
1. 2024-10 -- 1,261 active pages
2. 2024-08 -- 915 active pages
3. 2024-07 -- 911 active pages
Confidence: high
```

## Research questions -- Phase A

**At what point did the model start getting things wrong?** It didn't, on this question set, in
either mode -- 10/10 in both conditions. This dataset's factual questions all resolve to either a
single-cell lookup or a single-column max/sort, which is exactly the kind of operation both a
plain chat LLM and a code-execution model handle reliably. The place I *expected* trouble was Q8
(a 32-number manual sum with no calculator), and it came through exact. That's a genuinely useful
negative result: on a "few dozen rows, one arithmetic operation" scale, the risk of silent
fabrication was lower than the assignment's framing led me to expect going in. See Phase B for
where things actually started to break.

**Was the model ever confidently wrong?** Not in Phase A. Every answer was correct, and confidence
was consistently reported as "high" for direct lookups and comparisons, with "medium" reserved
honestly for the one genuinely error-prone step (Q8's manual summation) even though that step
happened to be correct. That calibration -- flagging the risky step as risky, independent of
whether it actually erred -- is itself a good sign, distinct from being right.

**Did data format matter?** Both modes received the identical raw CSV text pasted into the prompt;
the only variable was tool access, not format. Given how this experiment is designed, testing
markdown-table vs. raw-CSV vs. prose-summary formatting is a natural follow-up for a future
reporting period, not covered here.

**Did the model offer to write/run code unprompted?** The code-execution agent used its Bash tool
exactly as instructed (3 tool calls) and showed its scripts; the conversational agent used zero
tool calls, honoring the "no tools" instruction rather than reaching for one anyway. Neither
condition needed correcting, which suggests the instruction, not the model's default inclination,
determined whether code got used here.
