from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

def get_chat_model():
    """
    OpenAI-only chat model factory.
    """
    from langchain_openai import ChatOpenAI
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    return ChatOpenAI(model=model, temperature=0.0)

def get_embeddings():
    """
    OpenAI-only embeddings.
    """
    from langchain_openai import OpenAIEmbeddings
    embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=embed_model)
