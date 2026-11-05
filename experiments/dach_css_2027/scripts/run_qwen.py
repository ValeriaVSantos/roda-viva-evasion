"""Future, versioned Groq runs. Dry-run by default; --execute makes API calls."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
LABELS = {"RESPONDE", "PARCIAL", "ESQUIVA"}
CONDITIONS = {"simple": "simple.txt", "guided_with_examples": "guided_with_examples.txt",
              "guided_without_examples": "guided_without_examples.txt"}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def item_id(row):
    fields = [row[name] for name in ("ENTREVISTADO", "DATA", "ORDEM_PERGUNTA", "ORDEM_RESPOSTA")]
    return "rv_" + hashlib.sha256(json.dumps(fields, ensure_ascii=False).encode()).hexdigest()[:20]


def messages_for(condition, prompt, question, response):
    pair = f'PERGUNTA: "{question}"\nRESPOSTA: "{response}"'
    user = pair if condition == "simple" else "Analise o par abaixo:\n" + pair
    return [{"role": "system", "content": prompt}, {"role": "user", "content": user}]


def validate_response(text, condition):
    data = json.loads(text)
    if not isinstance(data, dict) or data.get("rotulo") not in LABELS:
        raise ValueError("Missing or invalid rotulo.")
    if condition != "simple":
        if not isinstance(data.get("mesmo_tema"), bool):
            raise ValueError("Guided response requires boolean mesmo_tema.")
        if not all(isinstance(data.get(key), str) for key in ["objetivo_central", "aborda_ponto_especifico"]):
            raise ValueError("Guided response lacks explanatory fields.")
    return data


def require_matching_manifest(path, configuration):
    if path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        if previous["configuration"] != configuration:
            raise ValueError("Run directory belongs to a different configuration. Choose a new --output directory.")
        return previous
    manifest = {"started_at_utc": timestamp(), "configuration": configuration,
                "python_version": platform.python_version(),
                "groq_sdk_version": importlib.metadata.version("groq")}
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Private CSV containing question and response text.")
    parser.add_argument("--output", type=Path, required=True, help="Use a private_runs subdirectory, not public results.")
    parser.add_argument("--conditions", nargs="+", required=True, choices=CONDITIONS)
    parser.add_argument("--model", default="qwen/qwen3.8-27b", help="Historical identifier; confirm provider availability.")
    parser.add_argument("--items", type=Path, help="CSV with item_id column to freeze the evaluated sample.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum rows in this run; 0 selects all input rows.")
    parser.add_argument("--pause", type=float, default=1.5)
    parser.add_argument("--execute", action="store_true", help="Actually call Groq; requires GROQ_API_KEY.")
    args = parser.parse_args()
    if args.limit < 0 or args.pause < 0:
        parser.error("--limit and --pause cannot be negative.")
    with args.input.open(encoding="utf-8-sig", newline="") as handle:
        records = list(csv.DictReader(handle))
    required = {"ENTREVISTADO", "DATA", "ORDEM_PERGUNTA", "ORDEM_RESPOSTA", "PERGUNTA", "RESPOSTA"}
    if not records or not required.issubset(records[0]):
        parser.error("Input CSV is empty or missing the original identity/question/response columns.")
    allowed = None
    if args.items:
        with args.items.open(encoding="utf-8-sig", newline="") as handle:
            allowed = {row["item_id"] for row in csv.DictReader(handle)}
    selected = []
    for row in records:
        identifier = item_id(row)
        if allowed is None or identifier in allowed:
            if not row["PERGUNTA"].strip() or not row["RESPOSTA"].strip():
                parser.error("Selected record has an empty question or response.")
            selected.append((identifier, row))
    if len({identifier for identifier, _ in selected}) != len(selected):
        parser.error("Duplicate item identifiers in input.")
    if allowed is not None and allowed != {identifier for identifier, _ in selected}:
        parser.error("The item list does not match the available input records.")
    if args.limit:
        selected = selected[:args.limit]
    if not selected:
        parser.error("No records selected.")
    conditions = list(dict.fromkeys(args.conditions))
    prompts = {name: (ROOT / "prompts" / CONDITIONS[name]).read_text(encoding="utf-8") for name in conditions}
    configuration = {"input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
                     "item_ids": [identifier for identifier, _ in selected],
                     "conditions": conditions, "model": args.model, "temperature": 0.0,
                     "response_format": {"type": "json_object"}, "pause_seconds": args.pause,
                     "prompt_sha256": {name: hashlib.sha256(text.encode()).hexdigest() for name, text in prompts.items()},
                     "user_message_templates": {"simple": 'PERGUNTA: "{question}"\nRESPOSTA: "{response}"',
                                                "guided": 'Analise o par abaixo:\nPERGUNTA: "{question}"\nRESPOSTA: "{response}"'}}
    print(json.dumps({"dry_run": not args.execute, "selected_rows": len(selected), "conditions": conditions,
                      "maximum_requests": len(selected) * len(conditions), "model": args.model}, indent=2))
    if not args.execute:
        print("No API call made. Add --execute only when ready to use your Groq quota.")
        return
    if not os.environ.get("GROQ_API_KEY"):
        parser.error("Set GROQ_API_KEY as an environment variable; do not put it in a notebook cell or commit it.")
    try:
        from groq import Groq
    except ImportError:
        parser.error("Install optional dependency: pip install -r requirements-inference.txt")
    args.output.mkdir(parents=True, exist_ok=True)
    require_matching_manifest(args.output / "manifest.json", configuration)
    output_file = args.output / "predictions.jsonl"
    completed = set()
    if output_file.exists():
        for line in output_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                saved = json.loads(line)
                if saved.get("status") == "ok":
                    completed.add((saved["item_id"], saved["condition"]))
    client = Groq(max_retries=0)
    for identifier, row in selected:
        for condition in conditions:
            if (identifier, condition) in completed:
                continue
            entry = {"item_id": identifier, "condition": condition, "timestamp_utc": timestamp()}
            try:
                completion = client.chat.completions.create(
                    model=args.model, temperature=0.0, response_format={"type": "json_object"},
                    messages=messages_for(condition, prompts[condition], row["PERGUNTA"], row["RESPOSTA"]))
                text = completion.choices[0].message.content or ""
                entry.update(status="ok", parsed=validate_response(text, condition), raw_response=text,
                             provider_model=completion.model,
                             finish_reason=completion.choices[0].finish_reason,
                             usage=completion.usage.model_dump() if completion.usage else None)
            except Exception as error:
                # Do not print exception bodies, which can include submitted text or provider credentials.
                entry.update(status="error", error_type=type(error).__name__)
                with output_file.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
                print("Run stopped after an API/format error; progress was saved. Error type:", type(error).__name__)
                return 1
            with output_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(identifier, condition, entry["parsed"]["rotulo"])
            time.sleep(args.pause)
    return 0


if __name__ == "__main__":
    sys.exit(main())
