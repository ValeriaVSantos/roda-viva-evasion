# Provenance and historical limitations

## Sources inspected on 5 November 2026

- Repository: https://github.com/ValeriaVSantos/roda-viva-evasion
- Repository HEAD inspected: `95058f859183b649f9218dfc5e15f1f73a75e25b`.
- Colab: https://colab.research.google.com/drive/14HXEOpc6J1oOmvvmCBsOS7KdyAM081t1
- Colab title: `Evasao Politica_gemini`; Google Drive modified time: `2026-11-05T17:01:08.811Z`.
- Predictions source: the author-supplied `resultados_anotacao_llms (1).csv`.

Original source bytes were kept outside the public upload directory. SHA-256 hashes and extraction steps are recorded in `source_manifest.json`. The labels-only release removes full interview text, annotator comments, and model explanations. Notebook outputs and stored credentials were removed before preparing the public archive copy.

## What was observed in the source notebook

| Cell, zero-based | Recorded execution count | Role |
|---:|---:|---|
| 0 | 1 | Guided prompt with three examples; begins annotation and writes checkpoints. |
| 1 | 2 | Resume cell; defines a guided prompt without the examples; skips valid existing labels and writes to the same columns. |
| 2 | 4 | Evaluates stored guided results against available human majority. |
| 3 | 6 | Runs the simple Qwen prompt on rows with a valid guided label. |
| 4 | 8 | Compares stored simple and guided predictions on the available paired subset. |

Execution counts and retained outputs support this execution history, but do not map each CSV result to a particular guided prompt. A checkpoint can combine existing labels from one condition and resumed labels from another. There are no per-item prompt identifiers in the source CSV. The public archive intentionally clears outputs and execution state; the observed counts are documented here rather than represented as newly executed results.

Consequently, the comparison reliably reproduces **historical stored pipeline predictions**, while attribution to one exact guided prompt remains unresolved. If the author has a prior CSV checkpoint or API logs, a future provenance update may resolve the mapping. It must not be guessed from the final labels.

The prompt text is preserved exactly, including possible tensions between refusal rules and examples. No silent correction was made to historical experimental instructions. New experiments should use explicit variant names, separate output directories and recorded hashes.

## Reproduced findings

- 694 rows and 11 interview/date combinations.
- 455 rows with three valid human votes; 322 unanimous.
- 248 paired model items with an available majority: 239 triple-annotated plus nine with two concordant human labels.
- Available-majority comparison: simple kappa 0.115865 / macro-F1 0.305289; historical guided kappa 0.415413 / macro-F1 0.584050.
- Triple-vote sensitivity: simple kappa 0.097366 / macro-F1 0.284360; historical guided kappa 0.380111 / macro-F1 0.530948.
- Simple prompt predicts ESQUIVA for 149/248 items, compared with 20 human-reference ESQUIVA labels.
- Precision for RESPONDE is 0.877193 in the simple condition and 0.853147 in historical guided. It does not increase.

The 248 items come from five substantially represented interviews and two items from José Dirceu. They are not a representative sample of all 11 interviews. The dates cover one interview in 1989 and ten in 2004–2007, not continuous decades of observations.

## Code provenance

`01_original_colab_sanitized.ipynb` preserves the five original code cells, with credential assignments replaced by removal comments and all outputs/execution metadata cleared. It retains original code quirks as an archival record, including a faulty progress-count expression in the resume cell. It is not the recommended new-run workflow.

`evaluate.py`, `run_qwen.py`, the analysis notebook and regression checks were prepared with AI assistance during repository organisation. Evaluation results were checked against the supplied CSV. No new paid or free model inference was run during this packaging step. The future runner's offline behaviour and response validation were tested; live Groq availability is not certified by those checks.

## Interpretation boundaries

The result is preliminary and descriptive. It does not establish a general effect across models, isolate decision trees versus examples, demonstrate the absence of length bias, or prove absence of training/evaluation contamination. Explicit refusals and ignorance can receive RESPONDE under the guide. The study measures annotations under that protocol rather than factual correctness or a politician's intent.

The researcher should retain the original private notebook and source CSV as historical evidence. For new runs, store exact prompt, model/provider identifier, input checksum, selected IDs, time, output and processing status. Keep credentials outside source files and keep raw API output private.
