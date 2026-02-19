from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_chroma import Chroma

from retail_rag_sim.llms.factory import get_embeddings

load_dotenv()

DOCS_DIR = os.getenv("DOCS_DIR", "./data/docs")
CHROMA_DIR = os.getenv("CHROMA_DIR", "./data/chroma")
COLLECTION = "retail_kb"

def main():
    loader = DirectoryLoader(
        DOCS_DIR,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
    )
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120)
    chunks = splitter.split_documents(docs)

    embeddings = get_embeddings()
    Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    vs = Chroma(
        collection_name=COLLECTION,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vs.add_documents(chunks)
    print(f"Indexed {len(chunks)} chunks into Chroma at {CHROMA_DIR}")

if __name__ == "__main__":
    main()
