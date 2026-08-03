# Phase B: Defined Metrics

Both metrics below were given to the subject model verbatim, in both conditions, as explicit
definitions it was instructed to apply rather than reinterpret. Exact computed values are in
`ground_truth/answer_key.md`.

## Metric A -- "Most improved page"

> The page with the largest **absolute increase** (`second_half_spend - first_half_spend`), in
> dollars.

**Why this definition:** the assignment's own example ("largest positive change in
points-per-game between the first and second half of the season") is explicitly an absolute,
not relative, comparison. `first_half_spend` / `second_half_spend` are pre-computed in
`page_season_stats.csv` by splitting each page's ad-delivery dates at the season midpoint
(2024-06-03), mirroring a "first half of season" vs. "second half of season" split.

**Known limitation, stated up front:** several pages (e.g. Kamala HQ, Tim Walz, Future Forward)
started at exactly $0 in the first half because they didn't exist as active advertisers yet (Harris
became the nominee in July 2024). An absolute-dollar metric will always favor whichever page had
the largest raw budget to grow from, which mechanically favors Kamala Harris regardless of what
"improvement" should mean. A relative/percentage version is documented in `ground_truth/answer_key.md`
as Metric 1b for comparison, but is undefined for $0-start pages, which is exactly the kind of
edge case a metric definition has to confront rather than paper over.

## Metric B -- "Game changer" (influence score)

> For each page: `influence_score = (page's total_spend / sum of total_spend across all pages) *
> (page's total_impressions / sum of total_impressions across all pages) * 100`.

**Why this definition:** the assignment's "game changer" example explicitly combines multiple
signals ("scoring, assists, and win rate") rather than ranking on one column. This metric rewards
pages that are large on *both* dimensions -- spend share and impression share -- rather than either
alone. A page with huge spend but poor reach (spend without impact), or huge reach on a shoestring
budget (viral but not necessarily well-resourced), scores lower than a page that is dominant on
both axes simultaneously. This is a multiplicative, not additive, combination on purpose: it
penalizes a page that is dominant on only one axis more than an additive average would.

**Known limitation, stated up front:** because it is multiplicative, a single very-large page
(Kamala Harris, at ~46% of total spend and ~43% of total impressions among these 32 pages) will
tend to dominate this metric almost by construction -- it isn't measuring efficiency or marginal
value, just simultaneous scale on two axes. This was intentional as a metric ("who already is a
big deal on both fronts"), and was NOT intended to answer "who should get the next incremental
dollar" -- see the advisory question in `prompt_log.md` for where this distinction actually
mattered.

## A metric neither one was given, but both invented anyway

Both subject agents, unprompted, computed `total_impressions / total_spend` ("impressions per
dollar") when answering the open-ended advisory question (Q13). This was not one of the two
metrics defined above. See `prompt_log.md` for how that went -- one agent got the "highest
efficiency" page right, the other got it wrong because it only checked a handful of pages instead
of scanning the full table for its own self-invented metric.
