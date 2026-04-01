# Refer-SportsMOT

A language-annotated evaluation set for referring multi-object tracking in team-sports video.

## Contents

- `annotations/`: benchmark annotations for `train`, `val`, and `test`
- `metadata/`: sequence-level split manifest and sanitized sequence metadata
- `evaluation/`: evaluation script and prediction schema
- `annotation_guidelines.md`: annotation protocol
- `taxonomy.md`: query type definitions
- `summary.json`: dataset statistics

## Statistics

- Sequences: 116
- Labeled tracks: 2,145
- Expressions: 7,291

### Query Distribution

| Type | Count | % |
|------|-------|---|
| Appearance | 1,972 | 27.0% |
| Spatial | 1,979 | 27.1% |
| Composite | 1,915 | 26.3% |
| Jersey # | 1,197 | 16.4% |
| Action | 228 | 3.1% |

## License

SoccerNet-derived annotations comply with CC BY-NC-SA 4.0.
