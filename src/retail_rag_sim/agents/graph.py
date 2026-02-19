from __future__ import annotations

import json
import os
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

from retail_rag_sim.agents.prompts import SYSTEM_BRAND_TONE, PLANNER_INSTRUCTIONS, VERIFIER_INSTRUCTIONS
from retail_rag_sim.llms.factory import get_chat_model
from retail_rag_sim.retrieval.retriever import build_hybrid_retriever, format_citations
from retail_rag_sim.retrieval.reranker import rerank
from retail_rag_sim.tools.db import run_select
from retail_rag_sim.tools.api import call_api
from retail_rag_sim.tools.email import send_gmail_smtp

load_dotenv()

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.55"))

# -------------------------
# Tools (tool calling)
# -------------------------
@tool
def retrieve_kb(query: str) -> Dict[str, Any]:
    """Retrieve KB snippets with citations."""
    retr = build_hybrid_retriever()
    docs = retr.invoke(query)
    ranked = rerank(query, docs)
    top_docs = [d for d, _ in ranked]
    return {"citations": format_citations(top_docs)}

@tool
def db_select(sql: str) -> Dict[str, Any]:
    """Run SELECT query against DB (guardrail: SELECT only)."""
    return {"rows": run_select(sql)}

@tool
def store_hours(store_id: str) -> Dict[str, Any]:
    """Get store hours from dummy API."""
    return call_api("/store_hours", {"store_id": store_id})

@tool
def inventory_lookup(store_id: str, sku: str) -> Dict[str, Any]:
    """Get inventory from dummy API."""
    return call_api("/inventory", {"store_id": store_id, "sku": sku})

@tool
def appointment_slots(store_id: str, service: str) -> Dict[str, Any]:
    """Get appointment slots from dummy API."""
    return call_api("/appointment_slots", {"store_id": store_id, "service": service})

@tool
def send_email(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email via Gmail SMTP."""
    return {"status": send_gmail_smtp(to_email, subject, body)}

TOOLS = [retrieve_kb, db_select, store_hours, inventory_lookup, appointment_slots, send_email]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}

# -------------------------
# State
# -------------------------
class AgentState(TypedDict):
    user_input: str
    messages: List[Any]
    plan: Dict[str, Any]
    citations: List[dict]
    tool_outputs: List[dict]
    final_answer: str
    confidence: float
    recommended_action: str


def planner_node(state: AgentState) -> AgentState:
    llm = get_chat_model()
    prompt = [
        SystemMessage(content=SYSTEM_BRAND_TONE),
        SystemMessage(content=PLANNER_INSTRUCTIONS),
        HumanMessage(content=state["user_input"]),
    ]
    raw = llm.invoke(prompt).content
    try:
        plan = json.loads(raw)
    except Exception:
        plan = {"intent": "other", "needs_retrieval": True, "needs_db": False, "needs_api": False,
                "needs_email": False, "sensitivity": "medium", "sql_hint": None}

    state["plan"] = plan
    state["messages"] = [SystemMessage(content=SYSTEM_BRAND_TONE), HumanMessage(content=state["user_input"])]
    state["citations"] = []
    state["tool_outputs"] = []
    state["final_answer"] = ""
    state["confidence"] = 0.0
    state["recommended_action"] = "answer"
    return state


def executor_node(state: AgentState) -> AgentState:
    llm = get_chat_model()
    llm_tools = llm.bind_tools(TOOLS)

    messages = state["messages"]
    tool_outputs: List[dict] = []

    for _ in range(6):
        resp = llm_tools.invoke(messages)
        messages.append(resp)

        if not getattr(resp, "tool_calls", None):
            state["final_answer"] = resp.content
            break

        for tc in resp.tool_calls:
            name = tc.get("name")
            args = tc.get("args") or {}
            tool_obj = TOOLS_BY_NAME.get(name)
            out = tool_obj.invoke(args) if tool_obj else {"error": f"Unknown tool {name}"}
            tool_outputs.append({"tool": name, "args": args, "output": out})
            messages.append(ToolMessage(content=json.dumps(out, ensure_ascii=False), tool_call_id=tc.get("id", "")))

    for t in tool_outputs:
        if t["tool"] == "retrieve_kb":
            state["citations"] = t["output"].get("citations", [])

    state["tool_outputs"] = tool_outputs
    state["messages"] = messages
    return state


def verifier_node(state: AgentState) -> AgentState:
    llm = get_chat_model()
    payload = {
        "draft_answer": state.get("final_answer", ""),
        "citations": state.get("citations", []),
        "tool_outputs": state.get("tool_outputs", []),
    }
    prompt = [SystemMessage(content=VERIFIER_INSTRUCTIONS), HumanMessage(content=json.dumps(payload, ensure_ascii=False))]
    raw = llm.invoke(prompt).content

    try:
        verdict = json.loads(raw)
    except Exception:
        verdict = {"grounded": False, "issues": ["verifier_parse_error"], "confidence": 0.3, "recommended_action": "ask_clarify"}

    state["confidence"] = float(verdict.get("confidence", 0.4))
    state["recommended_action"] = verdict.get("recommended_action", "answer")

    if state["confidence"] < CONFIDENCE_THRESHOLD and state["recommended_action"] == "answer":
        state["recommended_action"] = "ask_clarify"

    answer = state.get("final_answer", "")
    if state.get("citations"):
        answer += "\n\nSources (sanitized):\n" + "\n".join([f"- [{c['id']}] {c['source']}" for c in state["citations"]])

    answer = answer.strip() + f"\n\nConfidence: {state['confidence']:.2f} | Next: {state['recommended_action']}"
    state["final_answer"] = answer
    return state


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("planner", planner_node)
    g.add_node("executor", executor_node)
    g.add_node("verifier", verifier_node)

    g.add_edge(START, "planner")
    g.add_edge("planner", "executor")
    g.add_edge("executor", "verifier")
    g.add_edge("verifier", END)
    return g.compile()

GRAPH = build_graph()

def chat(user_input: str) -> Dict[str, Any]:
    state: AgentState = {
        "user_input": user_input.strip(),
        "messages": [],
        "plan": {},
        "citations": [],
        "tool_outputs": [],
        "final_answer": "",
        "confidence": 0.0,
        "recommended_action": "answer",
    }
    out = GRAPH.invoke(state)
    return {
        "answer": out["final_answer"],
        "plan": out.get("plan", {}),
        "citations": out.get("citations", []),
        "tool_outputs": out.get("tool_outputs", []),
        "confidence": out.get("confidence", 0.0),
        "recommended_action": out.get("recommended_action", "answer"),
    }
