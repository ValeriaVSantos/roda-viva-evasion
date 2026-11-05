# Historical Qwen paired-prompt comparison

These descriptive results reproduce stored predictions. They do not rerun the API.

| Reference subset | Condition | N | Cohen kappa | Macro-F1 | Accuracy |
|---|---|---:|---:|---:|---:|
| paired_available_majority | simple | 248 | 0.115865 | 0.305289 | 0.330645 |
| paired_available_majority | guided_historical | 248 | 0.415413 | 0.584050 | 0.685484 |
| paired_triple_votes | simple | 239 | 0.097366 | 0.284360 | 0.313808 |
| paired_triple_votes | guided_historical | 239 | 0.380111 | 0.530948 | 0.682008 |
| paired_excluding_aecio | simple | 210 | 0.107286 | 0.286597 | 0.319048 |
| paired_excluding_aecio | guided_historical | 210 | 0.445167 | 0.595587 | 0.700000 |

## Interpretation

The paired 248-item analysis includes nine items with two concordant human votes. The 239-item sensitivity analysis requires all three human votes.

The source Colab contains guided prompts with and without examples. Historical rows do not record which variant produced each prediction. Therefore guided_historical is a stored pipeline result, not a certified single-prompt run. See docs/provenance.md.

RESPONDE includes explicit ignorance/refusal under the codebook. Labels do not establish factual truth, intent, or substantive disclosure.

No causal claim of eliminated length bias or generalisation to all politicians is made.
