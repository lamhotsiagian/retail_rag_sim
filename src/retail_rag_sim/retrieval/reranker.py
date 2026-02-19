from __future__ import annotations

import os
from typing import List, Tuple
from dotenv import load_dotenv

from langchain_core.documents import Document

load_dotenv()

RERANK_MODEL = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", "5"))

_model = None
_disabled_reason = None

def _get_model():
    """
    Try to load a Sentence-Transformers CrossEncoder.
    If the environment lacks the heavy deps (torch, etc.), we fall back gracefully
    (no rerank) so the app still runs.
    """
    global _model, _disabled_reason
    if _model is not None or _disabled_reason is not None:
        return _model

    try:
        from sentence_transformers import CrossEncoder
        _model = CrossEncoder(RERANK_MODEL)
        return _model
    except Exception as e:
        _disabled_reason = str(e)
        return None

def rerank(query: str, docs: List[Document], top_k: int = TOP_K_RERANK) -> List[Tuple[Document, float]]:
    """
    Returns list of (Document, score), highest first.
    Fallback: if reranker unavailable, keep original order with score=0.0.
    """
    if not docs:
        return []
    model = _get_model()
    if model is None:
        return [(d, 0.0) for d in docs[:top_k]]

    pairs = [(query, d.page_content) for d in docs]
    scores = model.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: float(x[1]), reverse=True)
    return ranked[:top_k]
