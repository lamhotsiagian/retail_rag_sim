import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from retail_rag_sim.agents.graph import chat

st.set_page_config(page_title="Retail RAG Concierge (Sanitized)", layout="wide")
st.title("Customer Service RAG")
st.caption("LangChain + LangGraph A2A + Hybrid Retrieval + Tool Calling + LangSmith-ready")

if "history" not in st.session_state:
    st.session_state.history = []
if "last_debug" not in st.session_state:
    st.session_state.last_debug = None

user_msg = st.chat_input("Ask about returns, pickup, store hours, orders, appointments...")

if user_msg:
    st.session_state.history.append(("user", user_msg))
    out = chat(user_msg)
    st.session_state.history.append(("assistant", out["answer"]))
    st.session_state.last_debug = out

col1, col2 = st.columns([2, 1])

with col1:
    for role, msg in st.session_state.history:
        with st.chat_message(role):
            st.write(msg)

with col2:
    st.subheader("Debug / Observability")
    if st.session_state.last_debug:
        st.json({
            "plan": st.session_state.last_debug.get("plan"),
            "confidence": st.session_state.last_debug.get("confidence"),
            "recommended_action": st.session_state.last_debug.get("recommended_action"),
            "citations": st.session_state.last_debug.get("citations"),
        })
        with st.expander("Tool outputs"):
            st.write(st.session_state.last_debug.get("tool_outputs", []))
    else:
        st.info("Send a message to see plan, tools, and citations.")
