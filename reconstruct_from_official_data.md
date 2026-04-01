# Reconstruction Notes

Refer-SportsMOT is derived only from the official training partitions of the source benchmarks:

- SportsMOT: `train` and `val`
- SoccerNet-Tracking: `train`

No official benchmark test sequence is used in this package.

## To Reconstruct the Benchmark Context

1. Download the official SportsMOT and SoccerNet-Tracking datasets from their official sources.
2. Place the datasets in any local directory structure of your choice.
3. Use `metadata/refer_split_manifest.json` to recover the sequence-level `refer-train`, `refer-val`, and `refer-test` partitions.
4. Use `metadata/sequence_manifest_public.json` to recover the benchmark sequence list and sport metadata.
5. Use `annotations/refer_*.json` as the benchmark labels.

## Notes

- This anonymous package omits raw media and local evidence crops.
- The evaluation script therefore requires explicit dataset-root arguments.
- The package is intended for anonymous review and protocol inspection rather than as a final public release archive.
