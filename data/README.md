# Dataset placement

This project derives its small LLM-facing tables from the same 2024 Facebook political ads
dataset used in Task 1.

Source: Google Drive folder "2024 Facebook Political Ads"

https://drive.google.com/drive/folders/1e9FnDRyA-MWt_wLQHCctS5Dw60iC87oW?usp=sharing

Download and place the CSV here as:

```
data/fb_ads_president_scored_anon.csv
```

Then run:

```bash
python3 scripts/build_summary_tables.py
python3 scripts/ground_truth_stats.py
```

This regenerates `data/page_season_stats.csv`, `data/monthly_stats.csv`, and
`ground_truth/answer_key.md` from scratch.

The full 246,745-row source CSV is intentionally not committed to this repository (see
`.gitignore`). The two small derived tables (`page_season_stats.csv`, ~32 rows;
`monthly_stats.csv`, 11 rows) ARE committed -- they are generated artifacts small enough to review
directly, not "the dataset" the assignment asks you to exclude, and committing them makes the
prompt log's pasted data reproducible without needing the full source file.
