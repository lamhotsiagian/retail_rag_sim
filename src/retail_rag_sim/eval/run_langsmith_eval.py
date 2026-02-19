from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
import os
from langsmith import evaluate

from retail_rag_sim.agents.graph import chat
from retail_rag_sim.eval.metrics import citation_presence, grounded_numeric_claims, escalation_when_low_confidence
from retail_rag_sim.ops.observability import log_mlflow, log_wandb

load_dotenv()

DATA = Path("data/eval_examples.jsonl")

def target(example: Dict[str, Any]) -> Dict[str, Any]:
    return chat(example["input"])

def main():
    if not os.getenv('LANGSMITH_API_KEY'):
        raise SystemExit('LANGSMITH_API_KEY not set. Use: python -m retail_rag_sim.eval.run_local_eval')

    examples = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    results = evaluate(
        target,
        data=examples,
        evaluators=[citation_presence, grounded_numeric_claims, escalation_when_low_confidence],
        experiment_prefix="retail-rag-sim",
    )
    print(results)

    # Optional: log a tiny summary to MLflow/W&B if configured
    try:
        summary = {
            'n_examples': float(len(examples)),
        }
        log_mlflow(summary, params={'experiment_prefix': 'retail-rag-sim'})
        log_wandb(summary, config={'experiment_prefix': 'retail-rag-sim'})
    except Exception:
        pass


if __name__ == "__main__":
    main()
