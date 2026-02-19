from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("DUMMY_API_BASE_URL", "http://localhost:8001")

def call_api(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = BASE_URL.rstrip("/") + "/" + path.lstrip("/")
    with httpx.Client(timeout=10.0) as client:
        r = client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()
