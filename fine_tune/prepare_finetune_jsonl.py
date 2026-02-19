from __future__ import annotations

import json
from pathlib import Path

OUT = Path("fine_tune/train.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

EXAMPLES = [
  {
    "messages": [
      {"role": "system", "content": "You are a cautious retail customer service assistant. Use policies; cite sources."},
      {"role": "user", "content": "What is the return window for pickup orders?"},
      {"role": "assistant", "content": "The standard return window is 14 days from the pickup date. (Returns & Exchanges policy)"},
    ]
  },
  {
    "messages": [
      {"role": "system", "content": "You are a cautious retail customer service assistant. Use policies; cite sources."},
      {"role": "user", "content": "Can I designate someone else to pick up my order?"},
      {"role": "assistant", "content": "Yes—an alternate pickup person can be designated, but identity verification is required. (Pickup & Reservation policy)"},
    ]
  }
]

def main():
    with OUT.open("w", encoding="utf-8") as f:
        for ex in EXAMPLES:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"Wrote {len(EXAMPLES)} examples to {OUT}")

if __name__ == "__main__":
    main()
