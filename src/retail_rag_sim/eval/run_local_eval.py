from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

from retail_rag_sim.agents.graph import chat
from retail_rag_sim.eval.metrics import citation_presence, grounded_numeric_claims, escalation_when_low_confidence

DATA = Path("data/eval_examples.jsonl")

def main():
    examples = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    scores = {"citation_presence": [], "grounded_numeric_claims": [], "escalation_when_low_confidence": []}

    for ex in examples:
        out = chat(ex["input"])
        scores["citation_presence"].append(citation_presence(out))
        scores["grounded_numeric_claims"].append(grounded_numeric_claims(out))
        scores["escalation_when_low_confidence"].append(escalation_when_low_confidence(out))

    print("Local Eval Summary")
    for k, v in scores.items():
        print(f"- {k}: {mean(v):.2f}  (n={len(v)})")

if __name__ == "__main__":
    main()
