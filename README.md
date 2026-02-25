# Customer Service RAG — **OpenAI-only**
A **ready-to-run** RAG simulation with:
- **LangChain tool calling** (OpenAI)
- **LangGraph A2A** (Planner → Executor → Verifier)
- **Hybrid retrieval** (BM25 + Chroma vector search) + **cross-encoder re-ranking**
- **Citations + confidence scoring** (hallucination reduction)
- **SQL tool** (SQLite) + **Dummy API tools** (FastAPI)
- **Email notification** (Gmail SMTP)
- **Evaluation**: local offline metrics + optional **LangSmith** (if configured)
- **Deployable**: Docker + docker-compose + GitHub Actions CI

<img width="2255" height="1302" alt="image" src="https://github.com/user-attachments/assets/b420849b-57da-49fb-8fc0-54bf884d61cc" />


---

## Repository layout
```
retail_rag_sim/
  src/retail_rag_sim/        # python package
  data/docs/                 # markdown KB docs
  data/seed.sql              # demo retail DB seed
  api/dummy_api.py           # dummy tools API (FastAPI)
  ui/app.py                  # Streamlit UI
  tests/                     # basic tests
  docker/                    # Dockerfile + docker-compose
```

---


> Note: This repo intentionally avoids the `langchain` meta-package to reduce breakage from packaging changes. It uses `langchain-core`, `langchain-community`, and `langchain-openai`.

## Prerequisites
- Python **3.10+**
- An **OpenAI API key** (this project is OpenAI-only)

---

## 1) Local run (no cloud required)

### 1.1 Create venv + install deps
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

### 1.2 Install the local package (recommended)
```bash
pip install -e .
```

### 1.3 (Optional) If you prefer PYTHONPATH instead
```bash
export PYTHONPATH=./src     # Windows (PowerShell): $env:PYTHONPATH="./src"
```

### 1.4 Configure environment
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 1.5 Seed the demo SQLite DB
```bash
python -m retail_rag_sim.tools.seed_db
```

### 1.6 Build the vector index (RAG ingest)
```bash
python -m retail_rag_sim.retrieval.ingest
```

### 1.7 Start dummy tool API (FastAPI)
```bash
uvicorn api.dummy_api:app --reload --port 8001
```

### 1.8 Start UI (Streamlit)
In a new terminal (same venv + PYTHONPATH):
```bash
streamlit run ui/app.py
```

Open: http://localhost:8501

---

## 2) What to ask (example prompts)
- “What is the return window for in-store pickup?”
- “Can I designate someone else to pick up my order?”
- “How much tax did I pay on order R-10002 and what was the total?”
- “What are store hours for ST-CHI-01?”
- “What appointment slots are available for ST-CHI-01 repair service?”

---

## 3) Hallucination reduction techniques implemented
- **Grounding**: answers must rely on retrieved snippets + tool outputs
- **Hybrid retrieval**: BM25 + vector search
- **Re-ranking**: cross-encoder ranks top candidates
- **Citations**: sources listed in output
- **Confidence scoring**: verifier agent returns a confidence score and next action recommendation

---

## 4) Evaluation

### 4.1 Offline local eval (no LangSmith required)
Run:
```bash
python -m retail_rag_sim.eval.run_local_eval
```

This prints a simple metric summary over `data/eval_examples.jsonl`.

### 4.2 Optional: LangSmith evaluation (requires LANGSMITH_API_KEY)
If you want LangSmith:
1) Set in `.env`:
```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=retail-rag-sim
```
2) Run:
```bash
python -m retail_rag_sim.eval.run_langsmith_eval
```

---

## 5) Email notifications (Gmail SMTP)
This is optional. Gmail typically requires an **App Password**.
Set in `.env`:
```
GMAIL_SMTP_USER=you@gmail.com
GMAIL_SMTP_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

The agent can call the `send_email` tool when prompted (e.g., “Email me a pickup checklist”).

---

## 6) Docker (local deployment)
From the repo root:

### 6.1 Build & run with docker-compose
```bash
cd docker
docker compose -f docker-compose.yml up --build
```

Services:
- Dummy API: http://localhost:8001
- UI: http://localhost:8501

> For Docker usage, pass environment variables via an `.env` file or `docker compose` environment settings.

---

## 7) CI/CD
GitHub Actions workflow:
- installs deps
- seeds DB
- runs tests
- runs ruff lint

File: `.github/workflows/ci.yml`

---

## Troubleshooting
- **Import errors**: ensure `PYTHONPATH=./src`
- **OpenAI auth**: ensure `OPENAI_API_KEY` is set
- **Vector ingest slow**: first run downloads reranker model weights
- **LangSmith errors**: run local eval if you don’t set `LANGSMITH_API_KEY`

---

## Customize quickly
- Add/replace KB docs in `data/docs/*.md`
- Add new tools in `src/retail_rag_sim/tools/` and register in `agents/graph.py`
- Extend DB schema + tool queries (still SELECT-only for governance)
