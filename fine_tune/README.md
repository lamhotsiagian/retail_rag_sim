# Fine-tuning (Optional)

This project includes `prepare_finetune_jsonl.py` to generate a tiny `train.jsonl`.

Typical workflow:
1) Create/expand `train.jsonl`
2) Upload JSONL to your fine-tuning provider
3) Set `OPENAI_MODEL=<your_fine_tuned_model_id>` in `.env`

Tip: keep your fine-tune domain **sanitized** (no proprietary policies, no trademarks).
