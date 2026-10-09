# Data documentation

## Source

The interview material originates from the [LeGOS-UFSCar Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva), which contains transcripts from the Brazilian public-television interview program.

## Public annotation export

`annotations_labels_only.csv` contains no question or response text. It is a derived table for documenting annotation coverage and preparing adjudication.

| Column | Description |
|---|---|
| `item_id` | Repository-local stable identifier |
| `interviewee` | Public interview participant |
| `date` | Interview date from the source workbook |
| `question_order` | Source turn/order identifier for the question |
| `response_order` | Source turn/order identifier for the response |
| `annotator_a` | Anonymized first human label |
| `annotator_b` | Anonymized second human label |
| `annotator_c` | Anonymized third human label |
| `provisional_label` | Majority label when at least two ratings agree |
| `consensus_status` | Coverage-aware agreement or adjudication status |

The provisional label is not yet a frozen gold standard. Majority-disagreement cases still require review, and items with insufficient coverage require either additional annotation or an explicit exclusion policy.

Statuses distinguish `UNANIMOUS_3_OF_3`, `MAJORITY_2_OF_3`, and `AGREEMENT_2_OF_2`. This prevents two available matching ratings from being presented as a three-annotator majority.

## Coverage in the current workbook

- Total items: 694
- Three human ratings: 455
- Two human ratings: 226
- One human rating: 6
- No human rating: 7
- Items with at least two human ratings: 681

## Preliminary agreement

The reproducible analysis in `results/annotation_agreement.json` reports:

- nominal Krippendorff's alpha: 0.712 across 681 items with at least two labels;
- Fleiss' kappa: 0.607 across 455 items with all three labels;
- pairwise Cohen's kappa: 0.539, 0.569, and 0.822, depending on the annotator pair.

These values describe the current, non-adjudicated annotations. They should be recomputed after any label correction or additional annotation.

## Full text

The working spreadsheet contains full question and response text and is not included here. Reconstruct or inspect source turns through the upstream corpus and the identifiers in the public export, subject to the upstream terms.

## License

No separate open-data license has yet been assigned to the annotation export. Code remains covered by the repository's MIT License. Confirm the annotation license before creating a public dataset release.
