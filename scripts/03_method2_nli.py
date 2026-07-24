"""
metodo2_nli.py
==============
Método 2: Inferência Textual (NLI) para detecção de esquiva.

Instalar:
    pip install transformers torch scikit-learn

Modelo recomendado (multilíngue, ~300MB):
    MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7

Uso:
    python metodo2_nli.py --input pares_qa_anotacao.csv --output resultados_nli.csv
"""

import argparse, csv, re

def carregar_gold(caminho):
    pares = []
    with open(caminho, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            label = row.get("ANOTACAO_HUMANA","").strip().upper()
            if label in ("RESPONDE","PARCIAL","ESQUIVA"):
                pares.append({
                    "entrevistado": row["ENTREVISTADO"],
                    "pergunta": row["PERGUNTA"],
                    "resposta": row["RESPOSTA"],
                    "gold": label,
                    "pre_anotacao": row.get("PRE_ANOTACAO",""),
                })
    return pares

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default="pares_qa_anotacao.csv")
    parser.add_argument("--output", default="resultados_nli.csv")
    parser.add_argument("--modelo", default="MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7")
    args = parser.parse_args()

    from transformers import pipeline
    from sklearn.metrics import classification_report, cohen_kappa_score

    pares = carregar_gold(args.input)
    print(f"Pares com anotação humana: {len(pares)}")

    print(f"Carregando modelo: {args.modelo}")
    clf = pipeline("zero-shot-classification", model=args.modelo, device=-1)

    candidate_labels = ["responde à pergunta", "responde parcialmente", "esquiva da pergunta"]
    predicoes = []

    print("Classificando...")
    for i, par in enumerate(pares):
        if i % 20 == 0:
            print(f"  {i}/{len(pares)}")
        res = clf(
            par["resposta"][:512],
            candidate_labels,
            hypothesis_template="O político {}.",
            multi_label=False,
        )
        top = res["labels"][0]
        if "esquiva" in top:
            pred = "ESQUIVA"
        elif "parcialmente" in top:
            pred = "PARCIAL"
        else:
            pred = "RESPONDE"
        predicoes.append(pred)

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ENTREVISTADO","PERGUNTA","RESPOSTA","GOLD","PRE_ANOTACAO","METODO2_NLI"])
        for par, pred in zip(pares, predicoes):
            w.writerow([par["entrevistado"], par["pergunta"][:120],
                        par["resposta"][:120], par["gold"],
                        par["pre_anotacao"], pred])
    print(f"\n[OK] Salvo: {args.output}")

    gold = [p["gold"] for p in pares]
    print("\n── Método 2: NLI ──────────────────────────────────────────────────")
    print(classification_report(gold, predicoes,
                                 labels=["RESPONDE","PARCIAL","ESQUIVA"], digits=3))
    print(f"Cohen's Kappa: {cohen_kappa_score(gold, predicoes):.3f}")

if __name__ == "__main__":
    main()
