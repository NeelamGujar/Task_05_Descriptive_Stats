# Task_05_Descriptive_Stats

Research Task 5: descriptive statistics and large language models -- from ground truth to LLM
judgment. Both Phase A (baseline factual Q&A) and Phase B (derived metrics and judgment questions)
are covered in this single repository, per the assignment's deliverable list.

## Dataset

The same 2024 Facebook political ads dataset used in Task 1 (`fb_ads_president_scored_anon.csv`,
246,745 rows). Source and download instructions: [`data/README.md`](data/README.md).

That full file is far too large to hand to a language model in a chat context, so
[`scripts/build_summary_tables.py`](scripts/build_summary_tables.py) rolls it up into two small,
LLM-context-sized tables (committed to this repo, since they're small derived artifacts, not "the
dataset"):

- **`data/page_season_stats.csv`** -- 32 rows, one per advertiser page that ran >=800 ads during
  the 2024 election season (Jan 1 - Nov 5, 2024). Columns cover ad volume, total spend/impressions,
  message-type mix, and a first-half/second-half spend split (season midpoint: 2024-06-03) for
  "most improved" style questions. This is the "player season stats" analog from the assignment.
- **`data/monthly_stats.csv`** -- 11 rows, one per calendar month, aggregated across the *entire*
  campaign (not just the 32 pages above). This is the "team game log" analog.

[`scripts/ground_truth_stats.py`](scripts/ground_truth_stats.py) computes the trustworthy answer
key from those two tables (standard library only, independent of pandas/polars) and writes
[`ground_truth/answer_key.md`](ground_truth/answer_key.md).

### Reproduce the ground truth

```bash
# place fb_ads_president_scored_anon.csv in data/ (see data/README.md)
python3 scripts/build_summary_tables.py    # writes the two small tables
python3 scripts/ground_truth_stats.py      # writes ground_truth/answer_key.md
```

## Experimental design

**Model:** Claude Sonnet 5, tested in two conditions, each as a genuinely fresh, isolated subagent
instance with no memory of the ground-truth computation above (not just told not to look -- an
actually separate context window that never saw it):

- **Conversational mode**: given the two tables as pasted raw text, explicitly forbidden from
  using any tool (no Bash, no code execution, no file access). Simulates a plain chat LLM with no
  code interpreter.
- **Code-execution mode**: given the file paths on disk and instructed to write and run Python
  (pandas) to compute every answer.

The same 13 questions (10 factual, 3 judgment/derived-metric) were put to both conditions
identically. Full transcripts, verdicts, and metric definitions:

- [`phase_a/prompt_log.md`](phase_a/prompt_log.md) -- factual baseline questions
- [`phase_b/metrics.md`](phase_b/metrics.md) -- the two explicitly-defined derived metrics
- [`phase_b/prompt_log.md`](phase_b/prompt_log.md) -- judgment questions, including the advisory
  "which page should get the next dollar" question

## Summary of findings

**Phase A: 10/10 correct, in both modes.** Every factual question -- including summing 32
seven-to-eight-digit numbers by hand with no calculator (Q8) -- was answered exactly right in
conversational mode, and confirmed by the code-execution mode's `pandas` output. This was a
genuinely useful negative result: on a dataset this size, with single-lookup or single-column
questions, the risk of confident fabrication was lower than expected going in.

**Phase B: split verdict, and this is the headline finding.** Both explicitly defined metrics
(Metric A "most improved," Metric B "game changer" / influence score) were applied faithfully and
correctly in both modes -- Kamala Harris topped both, matching ground truth exactly.

The open-ended advisory question (Q13) is where the two modes diverged. Neither of the two
pre-defined metrics actually answers "which page should get the next marginal dollar" (Metric A is
about the past, Metric B rewards raw scale) -- so both agents, unprompted, invented the same third
metric: impressions per dollar spent. The **code-execution agent computed it across all 32 rows
and correctly identified Americans for Prosperity** (115.6 impressions/$) as the top page. The
**conversational agent manually checked only 6 of the 32 pages**, missed Americans for Prosperity
and Headlines 2024 entirely, and confidently recommended Working America -- the third-best page by
its own invented metric, presented as the best.

The failure wasn't in the model's reasoning (the diminishing-returns logic in both answers was
sound and nearly identical) -- it was in data coverage, and it was completely invisible from the
prose alone. "Highest of all pages checked" and "highest of all 32 pages" read identically
confident. That is exactly the "confidently wrong in a way you can't tell from the response alone"
failure mode the assignment's Phase A research questions ask about, except it took an open-ended
Phase B judgment question, not a Phase A factual one, to actually surface it.

## Reflections

**Where did the model succeed?** Any question resolving to a single lookup, a single-column
max/sort, or the two metrics I explicitly defined and specified the formula for -- in both modes,
with no observed errors across 26 total answered questions (13 questions x 2 conditions).

**Where did it fail, and why?** Only once, and specifically when three things lined up at once:
(1) the question was open-ended enough that the model had to invent its own analytical framing,
(2) that framing required scanning the *entire* table rather than a few salient rows, and (3) the
model had no code execution available to guarantee full coverage. Remove any one of those three
conditions and the failure didn't happen -- the code-execution agent hit the same open-ended
question and got it right, precisely because "scan all rows" is what `.sort_values()` does by
construction, not something a model has to remember to do exhaustively while composing prose.

**What this means for trusting an LLM with real analytical work:** trust it for retrieval and for
computing a metric you have precisely defined, in either mode, at this dataset scale. Do not trust
a conversational-only (no code execution) answer to an open-ended question that implicitly
requires an exhaustive scan of the data -- insist on code execution, or on the model showing its
full working set (not just its top candidates), for exactly that class of question. The gap here
was never about the model's reasoning quality; it was about whether "I checked" could be quietly
narrower than "I checked everything," and a reader has no way to tell which one they got from the
prose alone.

## Repository contents

```
README.md                       -- this file
data/README.md                  -- dataset source + placement instructions
data/page_season_stats.csv      -- derived small table (committed; ~32 rows)
data/monthly_stats.csv          -- derived small table (committed; 11 rows)
scripts/build_summary_tables.py -- derives the two small tables from the full source CSV
scripts/ground_truth_stats.py   -- computes the trustworthy answer key
ground_truth/answer_key.md      -- the answer key itself
phase_a/prompt_log.md           -- Phase A prompts, responses, verdicts
phase_b/metrics.md              -- the two explicitly-defined derived metrics
phase_b/prompt_log.md           -- Phase B prompts, responses, verdicts
visuals/                        -- (none produced this round; see Phase B log)
```
