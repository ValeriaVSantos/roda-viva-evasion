"""Offline checks for reference construction, saved metrics and new-run safeguards."""
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluation = load_module("dach_evaluation", ROOT / "scripts/evaluate.py")
runner = load_module("dach_runner", ROOT / "scripts/run_qwen.py")


class ReproductionChecks(unittest.TestCase):
    def test_majority_requires_two_matching_valid_votes(self):
        self.assertEqual(evaluation.human_reference(dict(annotator_1="responde", annotator_2=" RESPONDE ", annotator_3="")), ("RESPONDE", 2, False))
        self.assertEqual(evaluation.human_reference(dict(annotator_1="RESPONDE", annotator_2="PARCIAL", annotator_3="ESQUIVA")), (None, 3, False))
        self.assertEqual(evaluation.human_reference(dict(annotator_1="ERRO", annotator_2="ESQUIVA", annotator_3="")), (None, 1, False))

    def test_metric_convention_and_confusion_orientation(self):
        result = evaluation.classification_metrics(["RESPONDE", "PARCIAL", "ESQUIVA"], ["RESPONDE", "RESPONDE", "ESQUIVA"])
        self.assertEqual(result["confusion_matrix"], [[1, 0, 0], [1, 0, 0], [0, 0, 1]])
        self.assertAlmostEqual(result["cohen_kappa"], 0.5)
        self.assertAlmostEqual(result["macro_f1"], 5 / 9)

    def test_paired_intersection_excludes_failure_for_both_conditions(self):
        base = dict(interviewee="example", interview_date="01/01/2000", source_row="2",
                    annotator_1="RESPONDE", annotator_2="RESPONDE", annotator_3="RESPONDE",
                    qwen_simple_label="RESPONDE", qwen_guided_label="RESPONDE")
        report, paired = evaluation.build_report([dict(base, item_id="a"), dict(base, item_id="b", qwen_simple_label="ERRO")], "test")
        self.assertEqual([row["item_id"] for row in paired], ["a"])
        self.assertEqual(report["subsets"]["paired_available_majority"]["n"], 1)

    def test_saved_snapshot_reproduces_both_reference_policies(self):
        with (ROOT / "data/labels_snapshot.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        report, _ = evaluation.build_report(rows, "test")
        self.assertEqual(report["corpus"]["n"], 694)
        self.assertEqual(report["corpus"]["human_vote_coverage"]["3"], 455)
        self.assertEqual(report["corpus"]["triple_unanimous"], 322)
        paired = report["subsets"]["paired_available_majority"]
        strict = report["subsets"]["paired_triple_votes"]
        self.assertEqual(paired["n"], 248)
        self.assertEqual(strict["n"], 239)
        self.assertAlmostEqual(paired["conditions"]["simple"]["macro_f1"], 0.30528852323724115)
        self.assertAlmostEqual(paired["conditions"]["guided_historical"]["macro_f1"], 0.5840502345026177)
        self.assertAlmostEqual(strict["conditions"]["simple"]["cohen_kappa"], 0.09736551215917463)
        self.assertAlmostEqual(strict["conditions"]["guided_historical"]["macro_f1"], 0.5309480150130581)
        self.assertEqual(paired["conditions"]["simple"]["per_class"]["ESQUIVA"]["predicted_count"], 149)

    def test_snapshot_has_no_transcript_or_explanation_columns(self):
        with (ROOT / "data/labels_snapshot.csv").open(encoding="utf-8", newline="") as handle:
            columns = set(csv.DictReader(handle).fieldnames)
        self.assertFalse(columns & {"PERGUNTA", "RESPOSTA", "COMENTARIO", "QWEN_JUSTIFICATIVA"})

    def test_new_runner_validation_and_user_message(self):
        self.assertEqual(runner.validate_response('{"rotulo":"PARCIAL"}', "simple")["rotulo"], "PARCIAL")
        with self.assertRaises(ValueError):
            runner.validate_response('{"rotulo":"ERRO"}', "simple")
        with self.assertRaises(ValueError):
            runner.validate_response('{"rotulo":"RESPONDE"}', "guided_with_examples")
        messages = runner.messages_for("simple", "instructions", "question", "response")
        self.assertEqual(messages[1]["content"], 'PERGUNTA: "question"\nRESPOSTA: "response"')

    def test_new_runner_rejects_configuration_change(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps({"configuration": {"model": "original"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                runner.require_matching_manifest(manifest, {"model": "changed"})

    def test_new_runner_is_offline_by_default(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "private.csv"
            with source.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["ENTREVISTADO", "DATA", "ORDEM_PERGUNTA", "ORDEM_RESPOSTA", "PERGUNTA", "RESPOSTA"])
                writer.writeheader()
                writer.writerow(dict(ENTREVISTADO="test", DATA="01/01/2000", ORDEM_PERGUNTA="1", ORDEM_RESPOSTA="1", PERGUNTA="Test question?", RESPOSTA="Test response."))
            output = Path(directory) / "not_created"
            result = subprocess.run([sys.executable, str(ROOT / "scripts/run_qwen.py"), "--input", str(source), "--output", str(output), "--conditions", "simple", "guided_with_examples"], text=True, capture_output=True, check=True)
            self.assertIn('"dry_run": true', result.stdout)
            self.assertIn('"maximum_requests": 2', result.stdout)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
