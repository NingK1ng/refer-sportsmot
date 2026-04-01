# Refer-SportsMOT Anonymous Supplementary Package

This package is prepared for anonymous peer review.

## Contents

- `annotations/`: benchmark annotations for `train`, `val`, and `test`
- `metadata/refer_split_manifest.json`: deterministic sequence-level split definition
- `metadata/sequence_manifest_public.json`: sanitized sequence metadata without local paths
- `evaluation/eval_rmot.py`: evaluation script for canonical prediction files
- `evaluation/prediction_template.json`: prediction schema example
- `annotation_guidelines.md`
- `taxonomy.md`
- `reconstruct_from_official_data.md`
- `summary.json`

## What Is Included

The published benchmark contains only labeled target tracks with at least one retained referring expression.

- Sequences: 116
- Labeled tracks: 2145
- Expressions: 6099

### Query Distribution

- appearance: 1972
- jersey_number: 5
- spatial: 1979
- action: 228
- composite: 1915

## What Is Not Included

- raw videos or frames
- local evidence crops
- local absolute paths
- run logs or API credentials

Raw benchmark media are omitted to respect the licenses of the underlying datasets. Reviewers should obtain the official SportsMOT and SoccerNet-Tracking training data separately if they want to reconstruct the media side of the benchmark.

## Evaluation

The evaluation script expects a benchmark annotation JSON and a prediction JSON in the canonical schema.

Example:

```bash
python evaluation/eval_rmot.py \
  --gt annotations/refer_test.json \
  --pred evaluation/prediction_template.json \
  --sportsmot-root /path/to/sportsmot_publish/dataset \
  --soccernet-root /path/to/SoccerNet/tracking
```

The prediction template is only a schema example and will not produce meaningful scores.
