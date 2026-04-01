# Anonymous Package Note

This review package omits raw media, local evidence crops, and `human_audit/` exports. The document below describes the full internal pipeline used to construct the benchmark.

# Refer-SportsMOT Annotation Guidelines

## Current Pipeline

### 1. Protocol-Safe Source Selection
Refer-SportsMOT is built only from the official training partitions of the source benchmarks:
- SportsMOT: `train` and `val`
- SoccerNet-Tracking: `train`

No official benchmark test sequence is used for metadata extraction, expression generation, or model selection.

### 2. Sequence-Level Refer Split
Sequences are split at the sequence level into `refer-train`, `refer-val`, and `refer-test` using a deterministic seed (`42`). The split manifest is stored separately from the annotations so that all later steps read the same protocol definition.

### 3. Evidence Pack Construction
For each target track, the pipeline selects a representative frame using a visibility score that favors:
- larger visible boxes
- more central views
- lower crowding
- lower ambiguity among nearby players

Each target track is converted into an evidence pack containing:
- full frame path
- target crop
- local context crop
- three-frame action strip
- neighbor boxes in the representative frame
- geometric position and landmark facts
- dominant color estimates
- OCR number candidates when available
- motion vector and lifespan statistics

### 4. VLM Candidate Generation
A multimodal provider generates one candidate per query type:
- `appearance`
- `jersey_number`
- `spatial`
- `action`
- `composite`

The provider must return a fixed JSON contract with:
- `query`
- `type`
- `confidence`
- `evidence_fields`
- `status`

If evidence is insufficient, the provider must return `query = null` and `status = unsupported`.

### 5. Rule Filtering and Ambiguity Check
Each candidate expression is validated before it is kept:
- length must be 5-15 words
- the type label must match the content
- unsupported evidence is rejected
- spatial queries must use allowed landmarks
- jersey-number queries must have OCR support or very high visual confidence
- action queries must be supported by the action strip or motion evidence
- composite queries must combine at least two evidence sources

A lightweight query-conditioned ambiguity check then compares the target against competing tracks in the same sequence. Expressions that do not rank the target clearly enough are regenerated once and then dropped if they still fail.

### 6. Final Expression Selection
Each track keeps 2-3 validated expressions with distinct query types. Type selection is guided by the target distribution in `taxonomy.md`, but unsupported query types are never forced into the final annotation.

### 7. Human Audit Subset
A stratified audit subset is exported under `human_audit/`. The current workflow records:
- `accept`
- `edit`
- `reject`
- free-form notes

This first version uses human auditing for quality control and error discovery. It does not claim full double-annotation or inter-annotator agreement statistics.

## Constraints
- Expressions must rely only on visible evidence in the selected frames.
- The pipeline must not invent jersey numbers, colors, actions, or landmarks.
- If a query type is not supported by the evidence, it should be omitted rather than hallucinated.
