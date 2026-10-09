# Political Evasion Detection in Brazilian Portuguese

[![Project status: active extension](https://img.shields.io/badge/status-active%20extension-5b2c6f)](#current-status)
[![License: MIT](https://img.shields.io/badge/code%20license-MIT-green.svg)](LICENSE)

An evaluation benchmark for testing whether language models can distinguish direct answers, partial answers, and evasive answers in Brazilian Portuguese political interviews.

## Why this matters

Detecting political evasion is not ordinary topic classification. A system must compare the communicative goal of a journalist's question with what the interviewee addresses, partially addresses, or leaves unanswered. The task therefore tests discourse understanding rather than keyword overlap alone.

## Current status

This repository contains two research stages:

1. **Original benchmark:** 276 question-answer pairs labeled by one expert annotator and evaluated with five automatic methods.
2. **Multi-annotator extension:** 694 question-answer pairs with partially overlapping judgments from three human annotators. Of these, 455 have all three human labels and 681 have at least two. Agreement analysis and adjudication are in progress.

The original paper was not accepted for publication. It is retained as a transparent record of the initial experiment, not presented as a peer-reviewed publication. The multi-annotator extension is intended to address the original study's main annotation limitation.

## Labels

- **RESPONDE / RESPONDS:** directly addresses the central communicative goal.
- **PARCIAL / PARTIAL:** addresses the topic but leaves a key part unanswered or introduces substantial digression.
- **ESQUIVA / EVADES:** redirects to another topic, answers a different question, or uses a rhetorical strategy that avoids the central point.

The decision protocol is documented in [docs/annotation_guidelines.md](docs/annotation_guidelines.md).

## Initial benchmark results

These results use the original 276-item, single-annotator benchmark. They must not be interpreted as results from the multi-annotator extension.

| Method | Macro F1 | Cohen's kappa |
|---|---:|---:|
| Cosine similarity | 0.347 | 0.053 |
| NLI (mDeBERTa) | 0.217 | -0.032 |
| Claude Haiku zero-shot | 0.257 | 0.055 |
| Claude Haiku few-shot | 0.372 | **0.146** |
| Claude Sonnet few-shot | **0.388** | 0.126 |

All tested approaches showed low agreement with the original human labels. The LLM prompting conditions over-predicted `EVADES`, while the NLI formulation largely collapsed into `PARTIAL`. These are exploratory findings that will be re-evaluated against the adjudicated multi-annotator gold set.

## Multi-annotator extension

The agreement pipeline:

- accepts missing ratings;
- reports annotation coverage and label distributions;
- computes nominal Krippendorff's alpha across available ratings;
- computes pairwise Cohen's kappa and observed agreement;
- computes Fleiss' kappa on items with all three ratings;
- assigns a provisional majority label when at least two annotators agree;
- flags ties and insufficiently annotated items for adjudication;
- exports labels and identifiers without redistributing transcript text.

Run it with:

```bash
python scripts/06_annotation_agreement.py \
  --input /path/to/guia_anotacao.xlsx \
  --output-data data/annotations_labels_only.csv \
  --output-summary results/annotation_agreement.json
```

The source workbook is intentionally excluded from this public repository because it contains full interview text.

### Preliminary agreement results

| Measure | Items | Value |
|---|---:|---:|
| Krippendorff's alpha (nominal, available ratings) | 681 | 0.712 |
| Fleiss' kappa (complete three-annotator subset) | 455 | 0.607 |
| Cohen's kappa, annotators A-B | 455 | 0.539 |
| Cohen's kappa, annotators A-C | 464 | 0.569 |
| Cohen's kappa, annotators B-C | 672 | 0.822 |

These are non-adjudicated results from the current workbook. The difference between annotator pairs is itself a quality-control finding and will guide targeted adjudication.

## Repository structure

```text
.
├── data/
│   ├── README.md
│   └── annotations_labels_only.csv
├── docs/
│   └── annotation_guidelines.md
├── paper/                 # Initial, non-peer-reviewed manuscript
├── results/
│   └── annotation_agreement.json
├── scripts/
│   ├── 01_extract_qa_pairs.py
│   ├── 02_method1_similarity.py
│   ├── 03_method2_nli.py
│   ├── 04_method3_llm.py
│   ├── 05_evaluate.py
│   └── 06_annotation_agreement.py
├── tests/
└── CITATION.cff
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The LLM experiments require an Anthropic API key. Never commit keys or `.env` files.

## Data access and licensing

The transcripts originate from the [LeGOS-UFSCar Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva). This repository does not redistribute the full question and response text in the multi-annotator file. It publishes only source identifiers, anonymized annotator labels, coverage fields, and provisional consensus status.

Code is MIT licensed. A separate license for the annotation layer should be assigned only after confirming compatibility with the upstream corpus terms.

## Ethics and interpretation

The labels describe the relationship between a public interview question and its response. They are not claims about a person's honesty, intent, character, or factual accuracy. Models trained on political discourse may also reproduce stereotypes about politicians; the original experiments therefore require replication against the multi-annotator gold set.

## Research roadmap

- [x] Build the original 276-item benchmark.
- [x] Evaluate similarity, NLI, and prompted-LLM baselines.
- [x] Collect an expanded annotation workbook with three annotator columns.
- [x] Add reproducible coverage and agreement analysis.
- [ ] Complete missing annotations or define a documented partial-coverage policy.
- [ ] Adjudicate unresolved and high-disagreement cases.
- [ ] Freeze a versioned gold set.
- [ ] Split data by interview or speaker to reduce leakage.
- [ ] Re-run all baselines against the new gold set.
- [ ] Publish a dataset card and versioned research release.

## Citation

Until a revised study is published, cite the repository rather than the rejected manuscript:

```bibtex
@software{santos2026political_evasion,
  author = {Valeria Vieira dos Santos},
  title  = {Political Evasion Detection in Brazilian Portuguese},
  year   = {2026},
  url    = {https://github.com/ValeriaVSantos/roda-viva-evasion}
}
```

## Author

**Valeria Vieira dos Santos**<br>
Federal University of Sao Carlos (UFSCar), Brazil<br>
[ORCID](https://orcid.org/0009-0006-0023-6736) · [Website](https://valeriavsantos.com) · [LinkedIn](https://www.linkedin.com/in/valeriavieira-/)
