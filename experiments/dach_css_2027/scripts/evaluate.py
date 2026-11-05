"""Reproduce historical paired-prompt metrics using only Python's standard library."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

LABELS = ("RESPONDE", "PARCIAL", "ESQUIVA")
HUMANS = ("annotator_1", "annotator_2", "annotator_3")
CONDITIONS = {"simple": "qwen_simple_label", "guided_historical": "qwen_guided_label"}
ROOT = Path(__file__).resolve().parents[1]


def normalise(value):
    return str(value or "").strip().upper()


def human_reference(row):
    votes = [normalise(row.get(column)) for column in HUMANS]
    votes = [vote for vote in votes if vote in LABELS]
    counts = Counter(votes)
    majority = next((label for label, count in counts.items() if count >= 2), None)
    return majority, len(votes), len(votes) == 3 and len(counts) == 1


def classification_metrics(reference, predicted):
    if len(reference) != len(predicted) or not reference:
        raise ValueError("Reference and predictions must have equal, nonzero length.")
    matrix = [[0 for _ in LABELS] for _ in LABELS]
    for actual, prediction in zip(reference, predicted):
        if actual not in LABELS or prediction not in LABELS:
            raise ValueError("Unexpected classification label.")
        matrix[LABELS.index(actual)][LABELS.index(prediction)] += 1
    total = len(reference)
    support = [sum(row) for row in matrix]
    predicted_counts = [sum(row[j] for row in matrix) for j in range(3)]
    accuracy = sum(matrix[j][j] for j in range(3)) / total
    chance = sum(a * b for a, b in zip(support, predicted_counts)) / total**2
    per_class = {}
    for j, label in enumerate(LABELS):
        true_positive = matrix[j][j]
        precision = true_positive / predicted_counts[j] if predicted_counts[j] else 0.0
        recall = true_positive / support[j] if support[j] else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = dict(precision=precision, recall=recall, f1=f1,
                                support=support[j], predicted_count=predicted_counts[j])
    return dict(n=total, accuracy=accuracy,
                cohen_kappa=(accuracy - chance) / (1 - chance) if chance < 1 else None,
                macro_f1=sum(row["f1"] for row in per_class.values()) / 3,
                label_order=list(LABELS), confusion_matrix=matrix, per_class=per_class)


def build_report(rows, input_sha256):
    if len({row["item_id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate item_id: records must remain uniquely identified.")
    paired = []
    coverage = Counter()
    unanimity = 0
    for row in rows:
        majority, n_votes, unanimous = human_reference(row)
        coverage[n_votes] += 1
        unanimity += unanimous
        if majority and all(normalise(row.get(column)) in LABELS for column in CONDITIONS.values()):
            paired.append(dict(row, human_majority=majority, n_human_votes=n_votes))
    report = {
        "input_sha256": input_sha256,
        "labels": list(LABELS),
        "reference_policy": "At least two matching valid human votes; no forced tie-breaking.",
        "prediction_policy": "Use identical items with valid labels in both Qwen columns.",
        "historical_guided_prompt_variant": "Unknown per item: two variants occur in source Colab.",
        "corpus": dict(n=len(rows), n_interviews=len({(r["interviewee"], r["interview_date"]) for r in rows}),
                       human_vote_coverage={str(k): v for k, v in sorted(coverage.items())},
                       triple_unanimous=unanimity,
                       triple_unanimity_rate=unanimity / coverage[3] if coverage[3] else None),
        "subsets": {},
    }
    subsets = {
        "paired_available_majority": paired,
        "paired_triple_votes": [row for row in paired if row["n_human_votes"] == 3],
        "paired_excluding_aecio": [row for row in paired if row["interviewee"] != "Aécio Neves"],
    }
    for name, subset in subsets.items():
        if not subset:
            continue
        report["subsets"][name] = dict(
            n=len(subset),
            human_vote_coverage=dict(Counter(str(r["n_human_votes"]) for r in subset)),
            interview_coverage=dict(sorted(Counter(r["interviewee"] for r in subset).items())),
            conditions={condition: classification_metrics(
                [r["human_majority"] for r in subset],
                [normalise(r[column]) for r in subset])
                for condition, column in CONDITIONS.items()},
        )
    return report, paired


def markdown_summary(report):
    lines = ["# Historical Qwen paired-prompt comparison", "",
             "These descriptive results reproduce stored predictions. They do not rerun the API.", "",
             "| Reference subset | Condition | N | Cohen kappa | Macro-F1 | Accuracy |",
             "|---|---|---:|---:|---:|---:|"]
    for subset_name, subset in report["subsets"].items():
        for condition, metrics in subset["conditions"].items():
            kappa = metrics["cohen_kappa"]
            kappa_text = f"{kappa:.6f}" if kappa is not None else "undefined"
            lines.append(f"| {subset_name} | {condition} | {metrics['n']} | {kappa_text} | "
                         f"{metrics['macro_f1']:.6f} | {metrics['accuracy']:.6f} |")
    lines += ["", "## Interpretation", "",
              "The paired 248-item analysis includes nine items with two concordant human votes. "
              "The 239-item sensitivity analysis requires all three human votes.", "",
              "The source Colab contains guided prompts with and without examples. Historical rows "
              "do not record which variant produced each prediction. Therefore guided_historical "
              "is a stored pipeline result, not a certified single-prompt run. See docs/provenance.md.", "",
              "RESPONDE includes explicit ignorance/refusal under the codebook. Labels do not "
              "establish factual truth, intent, or substantive disclosure.", "",
              "No causal claim of eliminated length bias or generalisation to all politicians is made.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/labels_snapshot.csv")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    report, paired = build_report(rows, hashlib.sha256(args.input.read_bytes()).hexdigest())
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / "summary.md").write_text(markdown_summary(report), encoding="utf-8")
    columns = ["item_id", "source_row", "interviewee", "interview_date", "n_human_votes",
               "human_majority", "qwen_simple_label", "qwen_guided_label"]
    with (args.out_dir / "paired_items.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(paired)
    print(markdown_summary(report))


if __name__ == "__main__":
    main()
