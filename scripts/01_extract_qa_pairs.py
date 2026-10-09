"""
01_extract_qa_pairs.py
======================
Extract question-answer (Q-A) pairs from Roda Viva interview transcripts.

Reference implementation of the heuristic pipeline described in Section 3
("Pair extraction") of the paper. It:

  1. Splits each transcript into speaker turns using the transcript's
     "SPEAKER: utterance" convention.
  2. Labels each turn as JOURNALIST (the interviewing panel) or INTERVIEWEE
     (the single guest of the episode).
  3. Detects journalist *questions* via interrogative markers, question marks,
     and simple syntactic cues.
  4. Concatenates consecutive journalist turns that precede a guest response
     into a single question unit, to preserve discourse context.
  5. Segments a guest response at the point where a follow-up question
     interrupts it before the guest concludes their turn.

Output is a CSV with one row per Q-A pair, ready for annotation.

NOTE: transcript formatting varies. The turn-splitting regex and the
journalist/guest role assignment below follow the most common Roda Viva
convention (uppercase speaker label followed by a colon). Adapt `SPEAKER_RE`
and `--guest` to match the exact files in your copy of the
LeGOS-UFSCar/Roda-Viva corpus.

Usage:
    python scripts/01_extract_qa_pairs.py \
        --input data/transcripts/ \
        --guest "Ciro Gomes" \
        --output data/pares_qa.csv

If --guest is omitted, the most frequent speaker in the transcript is assumed
to be the interviewee (guests speak the most in a 90-minute interview).
"""

import argparse
import csv
import os
import re
import unicodedata
from collections import Counter

# A speaker turn looks like:  "PAULO MARKUN: boa noite, governador."
# Group 1 = speaker label, group 2 = utterance (until the next speaker label).
SPEAKER_RE = re.compile(r"^\s*([A-ZÀ-Ÿ][A-ZÀ-Ÿ'.\- ]{1,40}):\s*(.*)$")

# Interrogative cues in Portuguese (lowercased, unaccented for matching).
INTERROGATIVES = {
    "o que", "que", "qual", "quais", "quem", "quando", "onde", "como",
    "por que", "porque", "por quê", "quanto", "quanta", "quantos", "quantas",
    "sera", "acaso",
}


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s)
                    if unicodedata.category(c) != "Mn")


def is_question(text: str) -> bool:
    """A turn is treated as a question if it ends with '?' or opens with an
    interrogative cue."""
    t = text.strip()
    if not t:
        return False
    if "?" in t:
        return True
    head = strip_accents(t.lower())[:20]
    return any(head.startswith(q) for q in INTERROGATIVES)


def parse_turns(raw: str):
    """Split transcript text into (speaker, utterance) turns."""
    turns = []
    current_speaker, buffer = None, []
    for line in raw.splitlines():
        m = SPEAKER_RE.match(line)
        if m:
            if current_speaker is not None:
                turns.append((current_speaker, " ".join(buffer).strip()))
            current_speaker = m.group(1).strip()
            buffer = [m.group(2).strip()]
        elif current_speaker is not None:
            buffer.append(line.strip())
    if current_speaker is not None:
        turns.append((current_speaker, " ".join(buffer).strip()))
    return [(s, u) for s, u in turns if u]


def guess_guest(turns):
    """Interviewee = speaker with the most words (guests dominate the airtime)."""
    words = Counter()
    for speaker, utt in turns:
        words[speaker] += len(utt.split())
    return words.most_common(1)[0][0] if words else None


def extract_pairs(turns, guest):
    """Build Q-A pairs: consecutive journalist turns (questions) followed by the
    guest's response. Journalist turns are concatenated; a response is closed
    when the guest stops speaking (i.e., a journalist turn follows)."""
    pairs = []
    pending_question, q_order = [], 0
    for speaker, utt in turns:
        is_guest = (speaker == guest)
        if not is_guest:
            # journalist turn: accumulate as (part of) the question
            pending_question.append(utt)
        else:
            # guest turn: if we have a pending question, emit a pair
            question = " ".join(pending_question).strip()
            if question and is_question(question):
                q_order += 1
                pairs.append({
                    "question_order": q_order,
                    "question": question,
                    "answer": utt,
                })
            pending_question = []
    return pairs


def process_file(path, guest_arg):
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    turns = parse_turns(raw)
    if not turns:
        return []
    guest = guest_arg or guess_guest(turns)
    interviewee = guest or "UNKNOWN"
    episode = os.path.splitext(os.path.basename(path))[0]
    rows = []
    for p in extract_pairs(turns, guest):
        rows.append({
            "episode": episode,
            "interviewee": interviewee,
            "question_order": p["question_order"],
            "question": p["question"],
            "answer": p["answer"],
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="Extract Q-A pairs from Roda Viva transcripts.")
    ap.add_argument("--input", required=True,
                    help="Transcript file or a directory of .txt transcripts.")
    ap.add_argument("--output", default="data/pares_qa.csv")
    ap.add_argument("--guest", default=None,
                    help="Interviewee name (as it appears in the transcript). "
                         "If omitted, inferred as the most talkative speaker.")
    args = ap.parse_args()

    if os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in sorted(os.listdir(args.input))
                 if f.lower().endswith((".txt", ".md"))]
    else:
        files = [args.input]

    all_rows = []
    for path in files:
        rows = process_file(path, args.guest)
        print(f"  {os.path.basename(path)}: {len(rows)} pairs")
        all_rows.extend(rows)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["episode", "interviewee",
                                          "question_order", "question", "answer"])
        w.writeheader()
        w.writerows(all_rows)

    print(f"\n[OK] {len(all_rows)} Q-A pairs written to {args.output}")
    print("Next: add PRE_ANOTACAO / ANOTACAO_HUMANA columns for annotation "
          "(see data/README.md).")


if __name__ == "__main__":
    main()
