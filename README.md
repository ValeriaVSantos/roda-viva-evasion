# Speech Disfluencies and LLM Confidence

[![ACL Anthology](https://img.shields.io/badge/ACL%20Anthology-2026.codi--1.5-5b2c6f)](https://aclanthology.org/2026.codi-1.5/)
[![DOI](https://img.shields.io/badge/DOI-10.18653%2Fv1%2F2026.codi--1.5-blue)](https://doi.org/10.18653/v1/2026.codi-1.5)
[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE)

Reproducibility materials for:

> Valeria Santos. 2026. **Speech Disfluencies and LLM Confidence: Length Bias and Pragmatic Insensitivity in Brazilian Portuguese.** CODI-CRAC 2026, ACL. Pages 24-28.

## Why this matters

Confidence estimates can look precise while responding to superficial properties of an input. This study tests whether a language model responds to pragmatic uncertainty markers in spontaneous Brazilian Portuguese or primarily to surface features such as turn length.

The central finding is **surface-feature dominance**: after controlling for turn length, disfluency and hedge effects move in the human-expected direction but remain much smaller than the length effect.

## Study design

- **Data:** 344 turns from three interviews in the Roda Viva corpus
- **Contrast:** faithful Conversation Analysis transcripts versus sanitized transcripts
- **Model:** Meta-Llama-3.1-8B-Instruct with 4-bit quantization
- **Reference signal:** a deductive proxy of epistemic commitment based on pragmatic markers
- **Analysis:** binned divergence measures, Spearman correlations, Wilcoxon test, and multivariate OLS regression

ECE and OE are used here as **divergence measures between model confidence and a discourse-pragmatic proxy**. They are not presented as classical factual-correctness calibration metrics.

## Main results

| Result | Faithful layer | Sanitized layer |
|---|---:|---:|
| ECE-style divergence | 41.95 | 41.14 |
| Overconfidence error | 4.29 | 3.31 |
| Spearman correlation | -0.49 | -0.43 |

The paired difference was significant in the reported Wilcoxon test (`W = 10988.50`, `p = 0.0023`). In the multivariate model, turn length was the only significant predictor (`beta_std = +14.47`, `p < 0.001`); oral disfluency markers and lexical hedges were not significant.

See the [published paper](https://aclanthology.org/2026.codi-1.5/) for the full interpretation and limitations.

## Repository structure

```text
.
├── data/                 # Benchmark and source-derived research data
├── docs/                 # Annotation and discourse-topic notes
├── notebooks/            # Exploratory analyses and model audit notebooks
├── results/              # Reported outputs and figures
├── src/
│   └── ece_calibration_pipeline.py
├── tests/                # Tests for the reusable metric code
├── CITATION.cff
└── requirements.txt
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/ece_calibration_pipeline.py \
  --input "results/reported_confidence_scores.csv" \
  --output "results/reliability_diagram_reproduced.png"
python -m unittest discover -s tests -v
```

The notebooks document the exploratory model-inference workflow. Re-running Llama inference requires access to the model weights and hardware compatible with the quantized setup described in the paper.

The command above uses the complete 344-turn result table. The shorter 95-turn CSV and Colab-oriented scripts are retained only as pilot-stage provenance.

## Annotation proxy

The epistemic-commitment proxy starts at 100 and applies hierarchical deductions:

| Category | Example | Deduction |
|---|---|---:|
| Epistemic hedge | “maybe”, “I think” | -15 |
| Reformulation / false start | abandoned construction | -10 |
| Filled pause | “uh”, “um” | -5 |
| Lengthening | prolonged vowel | -5 |
| Repetition | repeated word or connective | -5 |

This proxy is theory-driven and was annotated by one researcher. It should not be interpreted as a direct measurement of a speaker's internal mental state.

## Data and ethics

The study uses interviews with public figures from the [Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva). The repository contains research derivatives used for the audit. Users should consult the upstream corpus terms before redistributing transcript content.

## Limitations

- The benchmark contains 344 turns from one interview genre.
- The experiment uses one autoregressive model.
- The reference proxy was developed deductively and annotated by one researcher.
- The regression explains approximately 29% of the confidence variance.
- The results do not establish factual correctness or a general psychological measure of certainty.

## Citation

```bibtex
@inproceedings{santos-2026-speech,
  title     = {Speech Disfluencies and {LLM} Confidence: Length Bias and Pragmatic Insensitivity in {B}razilian {P}ortuguese},
  author    = {Santos, Valeria},
  booktitle = {Proceedings of the 2nd Joint Workshop on Computational Approaches to Discourse, Context and Document-Level Inferences and Computational Models of Reference, Anaphora and Coreference (CODI-CRAC 2026)},
  pages     = {24--28},
  year      = {2026},
  publisher = {Association for Computational Linguistics},
  url       = {https://aclanthology.org/2026.codi-1.5/},
  doi       = {10.18653/v1/2026.codi-1.5}
}
```

## Author

**Valeria Vieira dos Santos**<br>
Federal University of Sao Carlos (UFSCar), Brazil<br>
[ORCID](https://orcid.org/0009-0006-0023-6736) · [Website](https://valeriavsantos.com) · [LinkedIn](https://www.linkedin.com/in/valeriavieira-/)

## License

Code is released under the [MIT License](LICENSE). Source-derived linguistic data may be subject to the terms of the upstream Roda Viva corpus.
