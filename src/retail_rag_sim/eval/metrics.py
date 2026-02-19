from __future__ import annotations

import re
from typing import Any, Dict

NUM_RE = re.compile(r"(?<!\w)(?:\$\s*)?\d+(?:\.\d+)?(?!\w)")

def citation_presence(output: Dict[str, Any]) -> float:
    answer = output.get("answer", "").lower()
    cites = output.get("citations", [])
    policyish = any(k in answer for k in ["return", "exchange", "pickup", "policy", "window"])
    if policyish and not cites:
        return 0.0
    return 1.0

def grounded_numeric_claims(output: Dict[str, Any]) -> float:
    answer = output.get("answer", "")
    nums = NUM_RE.findall(answer)
    if not nums:
        return 1.0
    tools = output.get("tool_outputs", [])
    has_structured = any(t.get("tool") in ["db_select", "inventory_lookup", "store_hours", "appointment_slots"] for t in tools)
    return 1.0 if has_structured else 0.0

def escalation_when_low_confidence(output: Dict[str, Any]) -> float:
    conf = float(output.get("confidence", 0.0))
    action = output.get("recommended_action", "answer")
    if conf < 0.4 and action == "answer":
        return 0.0
    return 1.0
