"""
metodo3_llm_zeroshot.py
========================
Método 3: LLM zero-shot (Claude claude-haiku-4-5-20251001) para detecção de esquiva.

Instalar:
    pip install anthropic scikit-learn

Configurar API key:
    export ANTHROPIC_API_KEY="sk-ant-..."

Uso:
    python metodo3_llm_zeroshot.py --input pares_qa_anotacao.csv --output resultados_llm.csv
"""

import argparse, csv, os, time

PROMPT_SISTEMA = """Você é um anotador especialista em análise do discurso político.
Sua tarefa é classificar pares pergunta-resposta de entrevistas políticas brasileiras.

Classifique a resposta do político em UMA das três categorias:

RESPONDE – O político responde diretamente à pergunta, abordando o tema central.
PARCIAL  – O político aborda parcialmente o tema, mas evita aspectos centrais da pergunta ou adiciona digressões que desviam sem abandonar completamente o tópico.
ESQUIVA  – O político evita a pergunta, muda de assunto, responde a outra pergunta implícita ou usa estratégias retóricas para não responder ao ponto central.

Responda APENAS com uma das palavras: RESPONDE, PARCIAL ou ESQUIVA.
Não inclua explicações nem pontuação adicional."""

PROMPT_USUARIO = """PERGUNTA DO JORNALISTA:
{pergunta}

RESPOSTA DO POLÍTICO ({entrevistado}):
{resposta}

Classificação:"""


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


def classificar_par(client, par, modelo="claude-haiku-4-5-20251001"):
    """Chama a API do Claude e retorna a classificação."""
    mensagem = client.messages.create(
        model=modelo,
        max_tokens=10,
        system=PROMPT_SISTEMA,
        messages=[{
            "role": "user",
            "content": PROMPT_USUARIO.format(
                pergunta=par["pergunta"][:800],
                resposta=par["resposta"][:1200],
                entrevistado=par["entrevistado"],
            )
        }]
    )
    resposta = mensagem.content[0].text.strip().upper()
    # Normalizar variações
    if resposta.startswith("RESPONDE"):
        return "RESPONDE"
    elif resposta.startswith("PARCIAL"):
        return "PARCIAL"
    elif resposta.startswith("ESQUIVA"):
        return "ESQUIVA"
    else:
        return "PARCIAL"  # fallback


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",   default="pares_qa_anotacao.csv")
    parser.add_argument("--output",  default="resultados_llm.csv")
    parser.add_argument("--modelo",  default="claude-haiku-4-5-20251001")
    parser.add_argument("--delay",   type=float, default=0.5,
                        help="Segundos entre chamadas (evitar rate limit)")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Defina a variável ANTHROPIC_API_KEY")

    import anthropic
    from sklearn.metrics import classification_report, cohen_kappa_score

    client = anthropic.Anthropic(api_key=api_key)
    pares  = carregar_gold(args.input)
    print(f"Pares com anotação humana: {len(pares)}")
    print(f"Modelo: {args.modelo}")
    print(f"Custo estimado: ~{len(pares) * 0.0004:.2f} USD (Haiku)")

    predicoes = []
    erros = 0

    for i, par in enumerate(pares):
        if i % 10 == 0:
            print(f"  {i}/{len(pares)}...")
        try:
            pred = classificar_par(client, par, args.modelo)
            predicoes.append(pred)
        except Exception as e:
            print(f"  [ERRO] par {i}: {e}")
            predicoes.append("PARCIAL")  # fallback
            erros += 1
        time.sleep(args.delay)

    # Salvar
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ENTREVISTADO","PERGUNTA","RESPOSTA","GOLD","PRE_ANOTACAO","METODO3_LLM"])
        for par, pred in zip(pares, predicoes):
            w.writerow([par["entrevistado"], par["pergunta"][:120],
                        par["resposta"][:120], par["gold"],
                        par["pre_anotacao"], pred])
    print(f"\n[OK] Salvo: {args.output}  (erros: {erros})")

    gold = [p["gold"] for p in pares]
    print("\n── Método 3: LLM Zero-shot ────────────────────────────────────────")
    print(classification_report(gold, predicoes,
                                 labels=["RESPONDE","PARCIAL","ESQUIVA"], digits=3))
    print(f"Cohen's Kappa: {cohen_kappa_score(gold, predicoes):.3f}")

if __name__ == "__main__":
    main()
