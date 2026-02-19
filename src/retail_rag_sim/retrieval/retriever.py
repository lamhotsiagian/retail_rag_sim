from __future__ import annotations

import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

from retail_rag_sim.llms.factory import get_embeddings

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
TOP_K_RETRIEVE = int(os.getenv("TOP_K_RETRIEVE", "10"))
COLLECTION = "retail_kb"


class HybridRetriever:
    """
    Lightweight hybrid retriever (BM25 + Vector) that does NOT depend on `langchain.retrievers`.

    Uses Reciprocal Rank Fusion (RRF) with weights to merge results:
      score += weight / (k0 + rank)
    """

    def __init__(self, bm25: BM25Retriever, vector_retriever, weights: Tuple[float, float] = (0.4, 0.6),
                 top_k: int = TOP_K_RETRIEVE, k0: int = 60):
        self.bm25 = bm25
        self.vector = vector_retriever
        self.weights = weights
        self.top_k = top_k
        self.k0 = k0

    def invoke(self, query: str) -> List[Document]:
        bm_docs = self.bm25.invoke(query) if hasattr(self.bm25, "invoke") else self.bm25.get_relevant_documents(query)
        vec_docs = self.vector.invoke(query)

        scores: Dict[str, float] = {}
        docs_map: Dict[str, Document] = {}

        def _key(d: Document) -> str:
            # stable-ish key for dedupe
            src = (d.metadata or {}).get("source", "unknown")
            return f"{src}::{hash(d.page_content)}"

        # RRF scoring
        for w, docs in zip(self.weights, [bm_docs, vec_docs]):
            for rank, d in enumerate(docs, start=1):
                k = _key(d)
                docs_map[k] = d
                scores[k] = scores.get(k, 0.0) + float(w) / float(self.k0 + rank)

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [docs_map[k] for k, _ in ranked[: self.top_k]]


def build_hybrid_retriever() -> HybridRetriever:
    embeddings = get_embeddings()
    vs = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vector_retriever = vs.as_retriever(search_kwargs={"k": TOP_K_RETRIEVE})

    # Build BM25 corpus from stored chunks (simple demo approach)
    all_docs = vs.get(include=["documents", "metadatas"])
    docs: List[Document] = []
    for txt, md in zip(all_docs.get("documents", []), all_docs.get("metadatas", [])):
        docs.append(Document(page_content=txt, metadata=md or {}))

    bm25 = BM25Retriever.from_documents(docs)
    bm25.k = TOP_K_RETRIEVE

    return HybridRetriever(bm25=bm25, vector_retriever=vector_retriever)


def format_citations(docs: List[Document]) -> List[dict]:
    cites = []
    for i, d in enumerate(docs, start=1):
        src = (d.metadata or {}).get("source", "unknown")
        excerpt = d.page_content[:220].replace("\n", " ") + "..."
        cites.append({"id": i, "source": src, "excerpt": excerpt})
    return cites
