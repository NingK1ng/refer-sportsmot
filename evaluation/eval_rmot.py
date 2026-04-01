"""
Refer-SportsMOT RMOT evaluation for the anonymous supplementary package.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Refer-SportsMOT predictions")
    parser.add_argument("--gt", required=True, help="Path to benchmark annotation JSON")
    parser.add_argument("--pred", required=True, help="Path to prediction JSON")
    parser.add_argument("--sportsmot-root", required=True, help="Path to official SportsMOT dataset root")
    parser.add_argument("--soccernet-root", required=True, help="Path to official SoccerNet-Tracking root")
    parser.add_argument("--output", default=None)
    return parser.parse_args()


def compute_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    inter = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    union = w1 * h1 + w2 * h2 - inter
    return inter / max(union, 1e-6)


def parse_source_gt(sequence_record: dict, dataset_bases: Dict[str, Path]) -> Dict[int, Dict[int, Tuple[int, int, int, int]]]:
    base = dataset_bases[sequence_record["source_dataset"]]
    gt_path = base / sequence_record["source_split"] / sequence_record["sequence_id"] / "gt" / "gt.txt"
    frames = defaultdict(dict)
    with gt_path.open() as handle:
        for line in handle:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 6:
                continue
            frame_id = int(parts[0])
            track_id = int(parts[1])
            bbox = tuple(int(float(v)) for v in parts[2:6])
            frames[frame_id][track_id] = bbox
    return frames


def gt_track_frames(sequence_record: dict, target_track_id: int, dataset_bases: Dict[str, Path]):
    source_gt = parse_source_gt(sequence_record, dataset_bases)
    result = {}
    for frame_id, tracks in source_gt.items():
        if target_track_id in tracks:
            result[frame_id] = [(target_track_id, tracks[target_track_id])]
    return result


def pred_track_frames(prediction: dict):
    frames = defaultdict(list)
    for row in prediction.get("trajectory", []):
        bbox = tuple(int(v) for v in row["bbox"])
        frames[int(row["frame_id"])].append((int(row.get("track_id", -1)), bbox))
    return dict(frames)


def compute_hota_per_expression(gt_tracks, pred_tracks, iou_threshold=0.5):
    det_tp = det_fn = det_fp = ass_correct = ass_total = 0
    all_frames = sorted(set(gt_tracks.keys()) | set(pred_tracks.keys()))
    for frame in all_frames:
        gt_boxes = gt_tracks.get(frame, [])
        pred_boxes = pred_tracks.get(frame, [])
        matched_gt = set()
        matched_pred = set()
        for pred_index, (pred_tid, pred_box) in enumerate(pred_boxes):
            best_iou = 0.0
            best_gt_index = -1
            for gt_index, (gt_tid, gt_box) in enumerate(gt_boxes):
                if gt_index in matched_gt:
                    continue
                iou = compute_iou(pred_box, gt_box)
                if iou > best_iou:
                    best_iou = iou
                    best_gt_index = gt_index
            if best_iou >= iou_threshold and best_gt_index >= 0:
                matched_gt.add(best_gt_index)
                matched_pred.add(pred_index)
                det_tp += 1
                gt_tid = gt_boxes[best_gt_index][0]
                if pred_tid == gt_tid:
                    ass_correct += 1
                ass_total += 1
            else:
                det_fp += 1
        det_fn += len(gt_boxes) - len(matched_gt)

    det_a = det_tp / max(det_tp + det_fn + det_fp, 1)
    ass_a = ass_correct / max(ass_total, 1)
    hota = math.sqrt(det_a * ass_a)
    return {
        "HOTA": round(hota * 100, 1),
        "DetA": round(det_a * 100, 1),
        "AssA": round(ass_a * 100, 1),
    }


def compute_r_prec(annotation: dict, prediction: dict, gt_tracks: dict) -> float:
    rep_frame = annotation["rep_frame_id"]
    pred_rows = [row for row in prediction.get("trajectory", []) if int(row["frame_id"]) == rep_frame]
    gt_rows = gt_tracks.get(rep_frame, [])
    if not pred_rows or not gt_rows:
        return 0.0
    pred_row = pred_rows[0]
    gt_tid, gt_box = gt_rows[0]
    pred_tid = int(pred_row.get("track_id", -1))
    pred_box = pred_row["bbox"]
    return 100.0 if pred_tid == gt_tid and compute_iou(pred_box, gt_box) >= 0.5 else 0.0


def prediction_index(pred_data: dict):
    index = {}
    for seq in pred_data.get("sequences", []):
        seq_id = seq["sequence_id"]
        for pred in seq.get("predictions", []):
            index[(seq_id, pred["expression_id"])] = pred
    return index


def evaluate(gt_path: Path, pred_path: Path, dataset_bases: Dict[str, Path]) -> dict:
    gt_data = json.loads(Path(gt_path).read_text())
    pred_data = json.loads(Path(pred_path).read_text())
    pred_index = prediction_index(pred_data)

    results_by_type = defaultdict(list)
    all_results = []

    for sequence_record in gt_data["sequences"]:
        for annotation in sequence_record["annotations"]:
            gt_tracks = gt_track_frames(sequence_record, annotation["target_track_id"], dataset_bases)
            for expr in annotation["expressions"]:
                prediction = pred_index.get((sequence_record["sequence_id"], expr["id"]), {"trajectory": []})
                pred_tracks = pred_track_frames(prediction)
                metrics = compute_hota_per_expression(gt_tracks, pred_tracks)
                metrics["R-Prec"] = round(compute_r_prec(annotation, prediction, gt_tracks), 1)
                metrics["type"] = expr["type"]
                results_by_type[expr["type"]].append(metrics)
                all_results.append(metrics)

    type_averages = {}
    for qtype, rows in results_by_type.items():
        type_averages[qtype] = {
            "HOTA": round(float(np.mean([row["HOTA"] for row in rows])), 1),
            "DetA": round(float(np.mean([row["DetA"] for row in rows])), 1),
            "AssA": round(float(np.mean([row["AssA"] for row in rows])), 1),
            "R-Prec": round(float(np.mean([row["R-Prec"] for row in rows])), 1),
            "count": len(rows),
        }

    overall = {
        metric: round(float(np.mean([entry[metric] for entry in type_averages.values()])), 1)
        for metric in ["HOTA", "DetA", "AssA", "R-Prec"]
    }
    return {
        "overall": overall,
        "per_type": type_averages,
        "n_expressions": len(all_results),
        "n_sequences": len(gt_data["sequences"]),
    }


def main() -> None:
    args = parse_args()
    dataset_bases = {
        "sportsmot": Path(args.sportsmot_root),
        "soccernet": Path(args.soccernet_root),
    }
    results = evaluate(Path(args.gt), Path(args.pred), dataset_bases)
    print("\n" + "=" * 52)
    print("Refer-SportsMOT RMOT Evaluation Results")
    print("=" * 52)
    print(f"Expressions: {results['n_expressions']}")
    print(f"Sequences: {results['n_sequences']}")
    print(
        f"Overall: HOTA={results['overall']['HOTA']}, DetA={results['overall']['DetA']}, "
        f"AssA={results['overall']['AssA']}, R-Prec={results['overall']['R-Prec']}"
    )
    print("\nPer Query Type:")
    for qtype, metrics in sorted(results["per_type"].items()):
        print(
            f"  {qtype:15s}: HOTA={metrics['HOTA']:5.1f}, DetA={metrics['DetA']:5.1f}, "
            f"AssA={metrics['AssA']:5.1f}, R-Prec={metrics['R-Prec']:5.1f} (n={metrics['count']})"
        )
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2))
        print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
