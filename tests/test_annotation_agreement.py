import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "06_annotation_agreement.py"
SPEC = importlib.util.spec_from_file_location("annotation_agreement", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class AgreementTests(unittest.TestCase):
    def test_normalizes_portuguese_and_english_labels(self):
        self.assertEqual(MODULE.normalize_label("responde"), "RESPONDE")
        self.assertEqual(MODULE.normalize_label("EVADES"), "ESQUIVA")

    def test_majority_consensus(self):
        label, status = MODULE.provisional_consensus(["RESPONDE", "PARCIAL", "RESPONDE"])
        self.assertEqual(label, "RESPONDE")
        self.assertEqual(status, "MAJORITY_2_OF_3")

    def test_two_available_matching_labels_are_not_called_three_way_majority(self):
        label, status = MODULE.provisional_consensus(["PARCIAL", "PARCIAL"])
        self.assertEqual(label, "PARCIAL")
        self.assertEqual(status, "AGREEMENT_2_OF_2")

    def test_all_different_requires_adjudication(self):
        label, status = MODULE.provisional_consensus(["RESPONDE", "PARCIAL", "ESQUIVA"])
        self.assertIsNone(label)
        self.assertEqual(status, "ADJUDICATION_REQUIRED")

    def test_perfect_pairwise_agreement(self):
        kappa, agreement, count = MODULE.cohen_kappa(["RESPONDE", "PARCIAL"], ["RESPONDE", "PARCIAL"])
        self.assertAlmostEqual(kappa, 1.0)
        self.assertAlmostEqual(agreement, 1.0)
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
