# Can LLMs Detect Political Evasion? A Benchmark for Brazilian Portuguese Interviews

Code and data for the paper submitted to **ICNLSP 2026**.

> **Note (anonymous review):** this paper is under double-blind review. Author
> identity is withheld throughout this repository. If you are reading this during
> the review period, please keep the repository access anonymous.

## Overview

This repository contains the automatic methods and evaluation scripts for
detecting political evasion in Brazilian Portuguese political interviews from the
*Roda Viva* program.

We release a corpus of **276 question–answer pairs** across three categories,
annotated by a single expert linguist (see *Limitations* in the paper):

- **RESPONDS** – politician directly addresses the question
- **PARTIAL** – politician addresses the topic but avoids key aspects
- **EVADES** – politician redirects or uses rhetorical strategies to avoid the question

Label distribution: RESPONDS = 154 (55.8%), PARTIAL = 100 (36.2%), EVADES = 22 (8.0%).

## Results

| Method | Macro F1 | Cohen's κ |
|---|---|---|
| Cosine Similarity | 0.347 | 0.053 |
| NLI (mDeBERTa) | 0.217 | -0.032 |
| Claude Haiku zero-shot | 0.257 | 0.055 |
| **Claude Haiku few-shot** | **0.372** | **0.146** |
| Claude Sonnet few-shot | 0.388 | 0.126 |

All methods yield low agreement with human annotation (best κ = 0.146), and every
LLM method over-predicts EVADES. Running the scripts regenerates these numbers.

## Repository Structure

```
roda-viva-evasion/
├── data/
│   └── README.md              # Data format, distribution, and access (upon request)
├── scripts/
│   ├── 01_extract_qa_pairs.py     # Q-A pair extraction from transcripts
│   ├── 02_method1_similarity.py   # Cosine similarity baseline
│   ├── 03_method2_nli.py          # NLI zero-shot (mDeBERTa)
│   ├── 04_method3_llm.py          # LLM zero-shot / few-shot (Claude API)
│   └── 05_evaluate.py             # Evaluation and comparison table
├── paper/
│   ├── main.tex                   # LaTeX source (ACL format)
│   └── references.bib             # Bibliography
├── CITATION.cff
├── LICENSE
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

For Method 3 (LLM), set your Anthropic API key (never commit it):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### 1. Q–A pair extraction

Question–answer pairs are extracted from the *Roda Viva* transcripts with the
heuristic pipeline described in §3 of the paper (speaker-turn detection, then
journalist-question identification via interrogative markers, syntactic cues, and
punctuation; consecutive journalist turns are concatenated to preserve context):

```bash
python scripts/01_extract_qa_pairs.py \
    --input data/transcripts/ \
    --output data/pares_qa.csv
```

The pairs are then annotated (RESPONDE / PARCIAL / ESQUIVA). The annotated file
(`pares_qa_anotacao.csv`) is available on request (see **Data** below), as the
source transcripts are under copyright.

### 2. Run the automatic methods

```bash
# Method 1: Cosine similarity
python scripts/02_method1_similarity.py \
    --input data/pares_qa_anotacao.csv \
    --output results/resultados_similaridade.csv

# Method 2: NLI
python scripts/03_method2_nli.py \
    --input data/pares_qa_anotacao.csv \
    --output results/resultados_nli.csv

# Method 3: LLM (zero-shot / few-shot)
python scripts/04_method3_llm.py \
    --input data/pares_qa_anotacao.csv \
    --output results/resultados_llm.csv \
    --mode fewshot
```

### 3. Evaluate all methods

```bash
python scripts/05_evaluate.py \
    --sim results/resultados_similaridade.csv \
    --nli results/resultados_nli.csv \
    --llm results/resultados_llm.csv \
    --output results/tabela_resultados.xlsx
```

## Data

The source transcripts come from the
[Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva) (LeGOS-UFSCar).
Our annotated Q–A pairs (`pares_qa_anotacao.csv`, 276 pairs) are **available upon
request** due to copyright restrictions on the original transcripts. See
`data/README.md` for the schema and label distribution.

The annotation file follows this format:

| Column | Description |
|---|---|
| `ENTREVISTADO` | Politician name |
| `PERGUNTA` | Journalist question |
| `RESPOSTA` | Politician response |
| `PRE_ANOTACAO` | Heuristic pre-annotation |
| `ANOTACAO_HUMANA` | Gold standard label (RESPONDE/PARCIAL/ESQUIVA) |

## Ethics

*Roda Viva* is a public-television program and the transcripts are public. The data
concerns **public figures speaking in a public, professional context**. Annotation
reflects a linguistic judgment about discourse structure — whether an answer
addresses the question — not a claim about any individual's honesty or intent.

## Citation

```bibtex
@inproceedings{anonymous2026evasion,
  title     = {Can {LLM}s Detect Political Evasion? {A} Benchmark for {B}razilian {P}ortuguese Interviews},
  author    = {Anonymous},
  booktitle = {Proceedings of the 9th International Conference on Natural Language and Speech Processing (ICNLSP)},
  year      = {2026}
}
```

## License

- **Code:** MIT (see `LICENSE`).
- **Data:** CC BY 4.0 (see `data/README.md`).
