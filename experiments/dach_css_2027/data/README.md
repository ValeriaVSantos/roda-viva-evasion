# Labels-only snapshot

`labels_snapshot.csv` preserves all 694 rows from the CSV supplied on 5 November 2026, without redistributing `PERGUNTA`, `RESPOSTA`, `JORNALISTA(S)`, `COMENTARIO`, or model explanations.

Columns:

- `item_id`: `rv_` plus the first 20 hex characters of SHA-256 over the JSON list of original interviewee, date, question-order and response-order strings, using UTF-8 and `ensure_ascii=False`.
- `source_row`: original spreadsheet-style row number, with header in row 1. This is not a physical CSV line number because text fields can contain newlines.
- `interviewee`, `interview_date`, `question_order`, `answer_order`: original source identifiers.
- `annotator_1`, `annotator_2`, `annotator_3`: labels mapped from `ANOTACAO_HUMANA`, `Anotacao 2`, `Anotador 3`.
- `qwen_simple_label`: `QWEN_SIMPLES_ROTULO`.
- `qwen_guided_label`: historical `QWEN_ROTULO`. Exact guided prompt variant is unknown per item.

Labels are normalised by trimming spaces and uppercasing. Empty cells remain empty. `ERRO` is retained as an execution-status value and excluded from classification evaluation; it is not recoded as ESQUIVA. The snapshot retains individual votes and does not replace them with adjudicated labels.

The source checksum and provenance are recorded in `../docs/source_manifest.json`. This file supports recomputing metrics from stored labels; rerunning a language model additionally requires the private interview text and an explicitly chosen prompt variant.
