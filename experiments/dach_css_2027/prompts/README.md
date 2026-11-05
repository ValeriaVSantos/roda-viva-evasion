# Exact prompt texts from the supplied Colab

The `.txt` files preserve the Python string values extracted from the source notebook, not rewritten or translated prompts:

| File | Original notebook cell (zero-based) | Python name |
|---|---:|---|
| `guided_with_examples.txt` | 0 | `SYSTEM_PROMPT` |
| `guided_without_examples.txt` | 1 | `SYSTEM_PROMPT` |
| `simple.txt` | 3 | `SYSTEM_PROMPT_SIMPLES` |

The guided user-message template is `Analise o par abaixo:\nPERGUNTA: "{question}"\nRESPOSTA: "{response}"`. The simple user-message template omits the opening `Analise o par abaixo:`. Both use model `qwen/qwen3.8-27b`, `temperature=0.0`, and `response_format={"type":"json_object"}` in the source notebook.

The guided prompts request four JSON fields (`objetivo_central`, `mesmo_tema`, `aborda_ponto_especifico`, `rotulo`); the simple prompt requests only `rotulo`. Thus the two conditions differ in instructions, examples where present, and requested output structure. The code does not isolate the effect of any one component.

The source notebook resumes guided annotation with a different `SYSTEM_PROMPT` while keeping the same result column. The CSV has no per-item prompt hash. Do not certify the historical guided column as uniformly few-shot or uniformly zero-shot. Both variants remain explicit choices for future runs, with per-run hashes recorded by `scripts/run_qwen.py`.

The first guided prompt includes examples adapted from Aécio's interview, as reported by the author. The evaluation exports an exclusion-of-Aécio sensitivity analysis. This is not proof of zero contamination.
