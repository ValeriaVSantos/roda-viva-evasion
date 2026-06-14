"""
metodo1_similaridade.py
=======================
Método 1: Similaridade semântica entre pergunta e resposta.

Usa sentence-transformers com modelo multilíngue para calcular
cosseno entre embeddings de pergunta e resposta.
Threshold determina RESPONDE / PARCIAL / ESQUIVA.

Instalar dependências:
    pip install sentence-transformers scikit-learn openpyxl pandas

Uso:
    python Scripts/metodo1_similaridade.py \
        --input pares_qa_anotacao.csv \
        --output resultados_similaridade.csv
"""

import argparse
import csv
from pathlib import Path


# ── Thresholds (calibrados no gold standard) ──────────────────────────────────
# Similaridade alta  → resposta on-topic  → RESPONDE
# Similaridade média → parcialmente relacionada → PARCIAL
# Similaridade baixa → desvio → ESQUIVA
THRESH_RESPONDE = 0.45   # cosseno >= 0.45 → RESPONDE
THRESH_PARCIAL  = 0.25   # 0.25 <= cosseno < 0.45 → PARCIAL
                         # cosseno < 0.25 → ESQUIVA


def carregar_gold(caminho: str):
    """Lê CSV e retorna apenas pares com ANOTACAO_HUMANA preenchida."""
    pares = []
    with open(caminho, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label = row.get("ANOTACAO_HUMANA", "").strip().upper()
            if label in ("RESPONDE", "PARCIAL", "ESQUIVA"):
                pares.append({
                    "entrevistado": row["ENTREVISTADO"],
                    "pergunta": row["PERGUNTA"],
                    "resposta": row["RESPOSTA"],
                    "gold": label,
                    "pre_anotacao": row.get("PRE_ANOTACAO", ""),
                })
    return pares


def classificar_por_cosseno(score: float) -> str:
    if score >= THRESH_RESPONDE:
        return "RESPONDE"
    elif score >= THRESH_PARCIAL:
        return "PARCIAL"
    else:
        return "ESQUIVA"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default="pares_qa_anotacao.csv")
    parser.add_argument("--output", default="resultados_similaridade.csv")
    parser.add_argument("--modelo", default="paraphrase-multilingual-MiniLM-L12-v2",
                        help="Nome do modelo sentence-transformers")
    args = parser.parse_args()

    # ── Carregar gold standard ────────────────────────────────────────────────
    pares = carregar_gold(args.input)
    print(f"Pares com anotação humana: {len(pares)}")

    # ── Embeddings ────────────────────────────────────────────────────────────
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.metrics import classification_report, cohen_kappa_score
    import numpy as np

    print(f"Carregando modelo: {args.modelo}")
    model = SentenceTransformer(args.modelo)

    perguntas  = [p["pergunta"] for p in pares]
    respostas  = [p["resposta"] for p in pares]

    print("Gerando embeddings...")
    emb_perg = model.encode(perguntas,  batch_size=32, show_progress_bar=True)
    emb_resp = model.encode(respostas,  batch_size=32, show_progress_bar=True)

    scores = [
        cosine_similarity([ep], [er])[0][0]
        for ep, er in zip(emb_perg, emb_resp)
    ]

    predicoes = [classificar_por_cosseno(s) for s in scores]

    # ── Salvar resultados ─────────────────────────────────────────────────────
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ENTREVISTADO","PERGUNTA","RESPOSTA",
                         "GOLD","PRE_ANOTACAO","SIM_COSSENO","METODO1_SIM"])
        for par, score, pred in zip(pares, scores, predicoes):
            writer.writerow([
                par["entrevistado"],
                par["pergunta"][:120],
                par["resposta"][:120],
                par["gold"],
                par["pre_anotacao"],
                f"{score:.4f}",
                pred,
            ])
    print(f"\n[OK] Resultado salvo em: {args.output}")

    # ── Avaliação ─────────────────────────────────────────────────────────────
    gold = [p["gold"] for p in pares]
    print("\n── Método 1: Similaridade Semântica ──────────────────────────────")
    print(classification_report(gold, predicoes,
                                 labels=["RESPONDE","PARCIAL","ESQUIVA"],
                                 digits=3))
    kappa = cohen_kappa_score(gold, predicoes)
    print(f"Cohen's Kappa: {kappa:.3f}")

    # Distribuição de scores por classe (para ajuste de thresholds)
    from collections import defaultdict
    scores_por_classe = defaultdict(list)
    for g, s in zip(gold, scores):
        scores_por_classe[g].append(s)
    print("\nScore médio por classe (gold):")
    for cls in ["RESPONDE","PARCIAL","ESQUIVA"]:
        vals = scores_por_classe[cls]
        if vals:
            print(f"  {cls}: média={np.mean(vals):.3f}  min={np.min(vals):.3f}  max={np.max(vals):.3f}")


if __name__ == "__main__":
    main()
