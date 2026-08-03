# Phase B Prompt-and-Response Log

Same two conditions and model as Phase A (see `phase_a/prompt_log.md` for the setup). Metric
definitions are in `metrics.md`. Ground truth is in `ground_truth/answer_key.md`.

## Question set

11. Using METRIC A exactly as defined, which page is the "most improved page," and by how many dollars?
12. Using METRIC B exactly as defined, compute influence_score for the pages / top 5 -- which is highest?
13. **Advisory question:** "As a campaign strategist for the second half of a future election
    cycle, if you wanted to maximize impressions gained per additional dollar spent, and you had to
    pick ONE existing page from Table 1 to direct extra budget toward as a 'game changer' -- which
    page would you recommend, and why? Would you recommend scaling up an already-dominant page or
    investing in a smaller/emerging one? Justify using the numbers in Table 1."

## Verdict table

| # | Question | Ground truth | Conversational mode | Code-execution mode |
|---|---|---|---|---|
| 11 | Most improved (Metric A) | Kamala Harris, +$78,738,847.50 | Kamala Harris, +$78,738,847.5 -- correct | Kamala Harris, +$78,738,847.50 -- correct |
| 12 | Top influence_score (Metric B) | Kamala Harris (19.5551), Joe Biden (1.0976), Trump (0.9732), The Daily Scroll (0.2180), Kamala HQ (0.1630) | Kamala Harris 19.56, Biden 1.10, Trump 0.97, Daily Scroll 0.22, Kamala HQ 0.16 -- **correct ranking, all 5 values within rounding** | Kamala Harris 19.555078, Biden 1.097559, Trump 0.973206, Daily Scroll 0.218012, Kamala HQ 0.162953 -- **exact match to ground truth** |
| 13 | Advisory: best page for marginal-impression efficiency | Americans for Prosperity (115.57 impressions/$), per the post-hoc metric surfaced in `ground_truth/answer_key.md` | Recommended **Working America** (~94 impr/$) -- **wrong**: only manually checked 6 pages (Harris, Trump, Kamala HQ, Daily Scroll, Future Forward, Working America) rather than scanning all 32; missed Americans for Prosperity (115.57) and Headlines 2024 (100.64) entirely | Recommended **Americans for Prosperity** (115.57 impr/$) -- **correct**: computed the ratio programmatically across all 32 rows and sorted |

## Full raw transcript -- Conversational mode (no tools)

```
Q: 11. Using METRIC A exactly as defined, which page is the "most improved page," and by how many dollars?
A: Kamala Harris, by $78,738,847.5 (second_half_spend $80,721,856.0 minus first_half_spend $1,983,008.5)
Reasoning: Same calculation as Q9 -- this metric is defined identically to what Q9 asked for, so the
answer carries over directly.
Confidence: high

Q: 12. Using METRIC B exactly as defined, compute the influence_score for Kamala Harris, Joe Biden,
Donald J. Trump, Kamala HQ, and The Daily Scroll. Which has the highest?
A: Estimated influence_scores:
- Kamala Harris: ~19.56
- Joe Biden: ~1.10
- Donald J. Trump: ~0.97
- The Daily Scroll: ~0.22
- Kamala HQ: ~0.16
Highest: Kamala Harris, by a wide margin.
Reasoning: Used total_spend sum ~$179,895,924.5 (from Q8) and total_impressions sum ~7,004,792,465.0
(computed via the same running-cumulative-sum method across all 32 pages' total_impressions). For
each of the 5 pages: influence_score = (page_spend/sum_spend) x (page_impressions/sum_impressions)
x 100.
Confidence: medium (depends on the Q8-style manual sum of 32 impression values plus several
long-division estimates -- compounding rounding risk, though the ranking/gap is large enough that
the "highest" conclusion is robust even if exact decimals are slightly off)

Q: 13. ADVISORY QUESTION
A: I would recommend Working America (or a similarly efficient smaller page) rather than scaling up
the already-dominant Kamala Harris page -- and I would NOT simply pour more money into the biggest
spender.

Reasoning/justification: Since the question specifically asks to maximize impressions gained per
additional dollar (marginal efficiency), the right metric to compare is total_impressions / total_spend
(impressions per dollar), not raw scale. Rough calculations:
- Kamala Harris: 2,979,511,669 / 82,704,864.5 ~ 36 impressions/$
- Donald J. Trump: 642,033,599.5 / 19,101,332.5 ~ 34 impressions/$
- Kamala HQ: 251,977,740.5 / 8,149,218 ~ 31 impressions/$
- The Daily Scroll: 447,388,799 / 6,140,619.5 ~ 73 impressions/$
- Future Forward: 282,615,450.5 / 4,267,645 ~ 66 impressions/$
- Working America: 241,508,624.5 / 2,558,943 ~ 94 impressions/$ (highest of all pages checked)

Kamala Harris already carries by far the largest share of both spend and impressions (dominant per
Metric B), but its impressions-per-dollar efficiency (~36) is mediocre compared to smaller pages like
Working America (~94) or The Daily Scroll (~73)... I'd recommend investing in a smaller/emerging
page (Working America) rather than the dominant one.

--- OVERALL SELF-ASSESSMENT (as given by the model) ---
I am least confident about Q8 and Q12 [manual summation risk]... That said, the qualitative
conclusion for Q12 (Kamala Harris has by far the highest influence_score) is robust to modest
arithmetic slips because its lead is so large.
```

**What actually went wrong (not self-identified by the model):** it never flagged that its "highest
of all pages checked" claim in Q13 was based on checking only 6 of the 32 pages. Its self-assessment
was honest about arithmetic risk on Q8/Q12 but did not catch this coverage gap -- it silently
narrowed the search space for a metric it invented on the spot, then reported a superlative ("highest
of all pages checked") using wording that reads as if the full table was considered. This is exactly
the "confidently wrong in a way you can't tell from the response alone" failure mode the Phase A
research questions ask about, except it showed up in Phase B, not Phase A -- it took a real judgment
question, not a factual lookup, to surface it.

## Full raw transcript -- Code-execution mode

```
Q: Using METRIC A exactly as defined, which page is the "most improved page," and by how many dollars?
Code/approach: spend_increase = second_half_spend - first_half_spend, took the maximum
A: Kamala Harris, with an increase of $78,738,847.50 (from $1,983,008.50 in the first half to
$80,721,856.00 in the second half). This is a purely mechanical result of the metric's definition --
it reflects that Harris's campaign spend surged in the second half of 2024 following her entry into
the race (consistent with the real-world timeline of Biden withdrawing in July 2024).
Confidence: high

Q: Using METRIC B exactly as defined, compute influence_score for every page in Table 1 and report
the top 5, highest first.
Code/approach: computed influence_score = (total_spend / sum(total_spend)) * (total_impressions /
sum(total_impressions)) * 100 for all 32 rows, sorted descending
A: Top 5:
1. Kamala Harris -- score = 19.555078
2. Joe Biden -- score = 1.097559
3. Donald J. Trump -- score = 0.973206
4. The Daily Scroll -- score = 0.218012
5. Kamala HQ -- score = 0.162953
Confidence: high

Q: ADVISORY QUESTION
Code/approach: computed impressions_per_dollar = total_impressions / total_spend for all 32 pages.
Top 5 by this ratio:
| page_name | total_spend | total_impressions | impressions_per_dollar |
|---|---|---|---|
| Americans for Prosperity | $1,002,428.00 | 115,846,238 | 115.57 |
| Headlines 2024 | $740,868.50 | 74,562,771.5 | 100.64 |
| Working America | $2,558,943.00 | 241,508,624.5 | 94.38 |
| The Voices of Today | $2,294,081.00 | 172,253,106.5 | 75.09 |
| The Daily Scroll | $6,140,619.50 | 447,388,799 | 72.86 |

For comparison, the "game changer" from Metric B (Kamala Harris) has impressions_per_dollar of only
~36.0 -- far lower efficiency than the pages above, because Harris's dominance in Metric B comes
from sheer scale, not efficiency.

A: I would recommend Americans for Prosperity as the page to direct incremental "game changer"
budget toward, not Kamala Harris (the Metric-B leader) or any of the other dominant pages.

Reasoning: Americans for Prosperity delivers 115.6 impressions per dollar -- the highest marginal
efficiency of any page, nearly 3x more efficient than Kamala Harris (36.0). It is a mid-sized page
(total_spend ~$1.0M, roughly 8th-lowest in the dataset), not a saturated one. Pages that already
spend tens of millions likely face diminishing returns / audience saturation; a smaller,
high-efficiency page has more "room to run." I would recommend investing in a smaller/emerging
efficient page rather than scaling up an already-dominant one -- Metric B rewards scale, which is a
measure of past influence, not of where the next marginal dollar is best spent.

Caveat (explicitly stated by the model): "this ratio is an average efficiency over the season, not
a true marginal/causal estimate -- it assumes the historical impressions-per-dollar rate would hold
for incremental spend, which may not be true if this page also faces its own audience-saturation
curve at higher budgets."
Confidence: medium (arithmetic high-confidence; the strategic recommendation is a judgment call
resting on an assumption about diminishing returns that the data doesn't directly test)

--- OVERALL SELF-ASSESSMENT (as given by the model) ---
Judgment calls occurred in Q5 (disambiguating "Donald J. Trump" from "Lara Trump") and Q13 (the
diminishing-returns assumption). All Phase A questions and Q11/Q12 required no interpretation --
mechanical application of the stated formulas.
```

## Research questions -- Phase B

**Did the model apply defined metrics faithfully, or drift toward its own assumptions?** For
Metrics A and B specifically -- yes, faithfully, in both modes, matching ground truth exactly
(code-execution mode) or within rounding (conversational mode). Both are mechanical, well-specified
formulas, and both agents applied them as given without substituting a different notion of
"improved" or "game changer." The drift showed up specifically on the *open-ended* advisory
question (Q13), where both agents reached past the two given metrics for a new one
(impressions-per-dollar) that I never defined. That wasn't against instructions -- Q13 was
deliberately left open -- but it's worth naming as its own finding: given an ambiguous question, the
model doesn't stay inside a provided metric's box; it manufactures a new one on the spot. That can
be a feature (real analytical judgment) or a risk (an un-vetted, un-validated metric silently
substituted for one you thought you'd constrained), and this experiment produced one clean example
of each: the code-execution agent's self-invented metric was validated (matched ground truth
exactly); the conversational agent's identical self-invented metric was *not* validated, and it was
wrong, because it was applied to an incomplete subset of the data.

**Did the advisory recommendation survive validation?** Split verdict, and that's the headline
finding of this whole experiment: the code-execution agent's recommendation (Americans for
Prosperity) is correct against the recomputed ground truth; the conversational agent's
recommendation (Working America) is not -- it's the third-best page by the very efficiency metric
it invented to justify the answer, not the best. Both agents' *reasoning process* was sound and
well-articulated (diminishing returns on saturated pages, marginal efficiency over raw scale); the
failure was entirely in *data coverage*, not logic. A well-reasoned advisory answer built on an
incomplete scan is a more dangerous failure mode than an obviously wrong one, because the prose
reads as confident and analytically sophisticated either way.

**Did letting the model run code change the character of its answers?** Yes, concretely: it's the
difference between "highest of all pages checked" (conversational, silently partial) and a
programmatic sort over all 32 rows (code-execution, complete by construction). The code-execution
condition didn't just get a better answer -- it structurally couldn't have made this particular
mistake, because `.sort_values().head()` doesn't skip rows the way ad hoc mental sampling does.

**Where would you trust an LLM with real analytical work, vs. insist on checking it yourself?**
Based on this experiment: trust it for retrieval and single-defined-metric computation, in either
mode, on a dataset this size -- both conditions were perfect on Phase A and on the two explicitly
defined Phase B metrics. Insist on checking it yourself the moment a question is open-ended enough
that the model has to choose its own analytical framing, *especially* in a conversational-only
setting where "checked all N rows" and "checked a representative-feeling sample of N rows" produce
indistinguishable prose. The gap here wasn't reasoning ability -- it was exhaustiveness, and
exhaustiveness is precisely what code execution guarantees and manual scanning does not.
