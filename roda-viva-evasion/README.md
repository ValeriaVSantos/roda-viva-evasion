# Can LLMs Detect Political Evasion? A Benchmark for Brazilian Portuguese Interviews

Code and data for the paper submitted to ICNLSP 2026.

## Overview

This repository contains the annotation pipeline, automatic methods, and evaluation scripts for detecting political evasion in Brazilian Portuguese political interviews from the *Roda Viva* program.

We annotate 276 question-answer pairs across three categories:
- **RESPONDS** – politician directly addresses the question
- **PARTIAL** – politician addresses the topic but avoids key aspects
- **EVADES** – politician redirects or uses rhetorical strategies to avoid the question

## Results

| Method | Macro F1 | Cohen's κ |
|---|---|---|
| Cosine Similarity | 0.347 | 0.053 |
| NLI (mDeBERTa) | 0.217 | -0.032 |
| Claude Haiku zero-shot | 0.257 | 0.055 |
| **Claude Haiku few-shot** | **0.372** | **0.146** |
| Claude Sonnet few-shot | 0.388 | 0.126 |

## Repository Structure

```
roda-viva-evasion/
├── data/
│   └── README.md              # Data format and access instructions
├── scripts/
│   ├── 01_extract_qa_pairs.py     # Q-A pair extraction pipeline
│   ├── 02_method1_similarity.py   # Cosine similarity baseline
│   ├── 03_method2_nli.py          # NLI zero-shot (mDeBERTa)
│   ├── 04_method3_llm.py          # LLM zero-shot and few-shot (Claude API)
│   └── 05_evaluate.py             # Evaluation and comparison table
├── paper/
│   ├── main.tex                   # LaTeX source (ACL format)
│   └── references.bib             # Bibliography
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

For Method 3 (LLM), set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### 1. Extract Q-A pairs
```bash
python scripts/01_extract_qa_pairs.py \
    --input data/transcripts/ \
    --output data/pares_qa.csv
```

### 2. Run automatic methods
```bash
# Method 1: Cosine similarity
python scripts/02_method1_similarity.py \
    --input data/pares_qa_anotacao.csv \
    --output results/resultados_similaridade.csv

# Method 2: NLI
python scripts/03_method2_nli.py \
    --input data/pares_qa_anotacao.csv \
    --output results/resultados_nli.csv

# Method 3: LLM (zero-shot and few-shot)
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

The source transcripts come from the [Roda Viva corpus](https://github.com/LeGOS-UFSCar/Roda-Viva) (LeGOS-UFSCar). Our annotated Q-A pairs (`pares_qa_anotacao.csv`) are available upon request due to copyright restrictions on the original transcripts.

The annotation file follows this format:

| Column | Description |
|---|---|
| `ENTREVISTADO` | Politician name |
| `PERGUNTA` | Journalist question |
| `RESPOSTA` | Politician response |
| `PRE_ANOTACAO` | Heuristic pre-annotation |
| `ANOTACAO_HUMANA` | Gold standard label (RESPONDE/PARCIAL/ESQUIVA) |

## Citation

```bibtex
@inproceedings{anonymous2026evasion,
  title     = {Can {LLM}s Detect Political Evasion? {A} Benchmark for {B}razilian {P}ortuguese Interviews},
  author    = {Anonymous},
  booktitle = {Proceedings of the 9th International Conference on Natural Language and Speech Processing (ICNLSP)},
  year      = {2026}
}
```

## Requirements

See `requirements.txt` for full dependencies.

## License

Code: MIT License  
Data: See `data/README.md`
