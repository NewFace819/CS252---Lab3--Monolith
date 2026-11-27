"""Streamlit chat UI.   Run:  streamlit run ui/app.py      (the API must be running on port 8000)

The UI never imports assistant_core: it only talks to the backend through the HTTP API.
"""

import os
import sys
import uuid
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so "import ui..." works under streamlit

from ui.api_client import AssistantClient
from ui.logic import EXAMPLES, WELCOME, format_sources, status_note, validate_input

st.set_page_config(page_title="FIT Study Assistant", page_icon="🎓")
AVATARS = {"assistant": "🎓", "user": "🧑‍🎓"}  # replace the stock robot/face icons
client = AssistantClient(os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000"))

# ---- session state: remembered between reruns of this script ----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = uuid.uuid4().hex[:12]
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]
if "rated" not in st.session_state:
    st.session_state.rated = set()

st.title("🎓 FIT Study Assistant")
if len(st.session_state.messages) == 1:
    st.info("Ask one question per message. Send unrelated topics as separate messages.")
    st.caption(
        "For thesis eligibility, ask about accumulated credits (e.g. 118 credits). "
        "For tuition, ask about credits taken this semester (e.g. 18 credits)."
    )
if not client.healthy():
    st.error("The assistant backend is not reachable. Start it with: uvicorn assistant_api.main:create_app --factory")

with st.sidebar:
    st.subheader("Try an example")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state.pending = ex
    st.caption("This is an AI assistant. Check important decisions with the Training Office.")

# ---- history -------------------------------------------------------------------
for i, m in enumerate(st.session_state.messages):
    with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
        st.markdown(m["content"])
        if m.get("source_details"):
            for source in m["source_details"]:
                with st.expander(f"{source['id']} — {source['title']}"):
                    st.text(source["title"])
        elif m.get("sources"):
            st.caption(m["sources"])
        if m.get("note"):
            st.info(m["note"])
        rid = m.get("request_id")
        if rid and rid not in st.session_state.rated:
            slot = st.empty()  # replaced after a saved vote, so the buttons disappear in the same run
            c1, c2, _ = slot.container().columns([2, 2.4, 4])
            vote = None
            if c1.button("👍 Helpful", key=f"up{i}", help="Helpful answer"):
                vote = (1, "Thanks for your feedback!")
            if c2.button("👎 Not helpful", key=f"down{i}", help="Not helpful — we will review it"):
                vote = (-1, "Thanks — we will look at this answer.")
            if vote:
                rating, thanks = vote
                if client.send_feedback(rid, rating):  # only a saved vote counts
                    st.session_state.rated.add(rid)
                    st.toast(thanks)
                    slot.caption("✓ Feedback recorded — thanks!")
                else:  # keep the buttons so the user can try again
                    st.warning("Your feedback could not be saved. Check that the assistant is running and try again.")
        elif rid:
            st.caption("✓ Feedback recorded — thanks!")

# ---- new question ----------------------------------------------------------------
question = st.chat_input("Ask one question about fees, offices or the handbook…") or st.session_state.pop(
    "pending", None
)
if question:
    problem = validate_input(question)
    if problem:
        st.warning(problem)
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.spinner("Thinking…"):
            result = client.ask(question, st.session_state.session_id)
        if result.ok:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.answer,
                    "sources": format_sources(result.sources),
                    "source_details": result.sources,
                    "note": status_note(result),
                    "request_id": result.request_id,
                }
            )
        else:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {result.error}"})
        st.rerun()
