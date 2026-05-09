import streamlit as st
import requests
import time

API_URL = st.secrets.get("API_URL", "https://u6uox3h9mi.execute-api.us-east-2.amazonaws.com/default/ragforge-query")

st.set_page_config(
    page_title="RagForge",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { color: #e0d8c8; }
    header[data-testid="stHeader"] { background: transparent; }
    footer { display: none; }
    .block-container { max-width: 760px; padding-top: 2rem; }

    .title-block {
        text-align: center;
        padding-top: 18vh;
        padding-bottom: 2.5rem;
    }
    .title-block h1 {
        font-size: 3.6rem;
        font-weight: 300;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }
    .title-block p {
        color: #888;
        font-size: 1.1rem;
    }

    /* Search input */
    .stTextInput label { display: none !important; }
    .stTextInput input { font-size: 1.1rem !important; }

    /* Dropdown */
    .stSelectbox label { display: none !important; }
    .stSelectbox > div > div { min-width: 130px !important; }

    /* Answer */
    .answer-box {
        background: #1a1a2e;
        border: 1px solid #2a2a3e;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        line-height: 1.85;
        font-size: 1.05rem;
    }

    /* Metrics */
    .metrics-row {
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        color: #888;
        font-size: 0.82rem;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #2a2a3e;
    }
    .metrics-row span { color: #bbb; }

    .streamlit-expanderHeader { color: #888 !important; font-size: 0.85rem !important; }
    .streamlit-expanderContent { background: #0f0f18 !important; }
    .stCaption { color: #555 !important; }
    section[data-testid="stSidebar"] { background: #0e0e16; }
</style>
""", unsafe_allow_html=True)

# ---- Title ----
st.markdown("""
<div class="title-block">
    <h1>RagForge</h1>
    <p>Retrieval-Augmented Generation over the Lord of the Rings corpus</p>
</div>
""", unsafe_allow_html=True)

# ---- Search bar + model dropdown ----
tier_map = {"Nova Pro": "fast", "Opus 4.6": "powerful"}

col_q, col_m = st.columns([5, 1])
with col_q:
    question = st.text_input(
        "query",
        placeholder="Ask anything about Lord of the Rings...",
        label_visibility="collapsed",
    )
with col_m:
    tier_label = st.selectbox(
        "model",
        list(tier_map.keys()),
        index=0,
        label_visibility="collapsed",
    )

tier = tier_map[tier_label]

# ---- Query ----
if question:
    with st.spinner("Searching..."):
        start = time.time()
        try:
            resp = requests.post(
                API_URL,
                json={"question": question, "tier": tier},
                timeout=120,
            )
            elapsed = time.time() - start
            data = resp.json()
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
            st.stop()

    answer = data.get("answer", "No answer returned.")
    model_name = data.get("model", "?")
    chunks_used = data.get("chunks_used", "?")
    is_mh = data.get("is_multi_hop", False)
    config_label = data.get("config", "?")
    q_type = "Multi-hop" if is_mh else "Factoid"

    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="metrics-row">'
        f'<div>Model: <span>{model_name}</span></div>'
        f'<div>Type: <span>{q_type}</span></div>'
        f'<div>Passages: <span>{chunks_used}</span></div>'
        f'<div>Config: <span>{config_label}</span></div>'
        f'<div>Latency: <span>{elapsed:.1f}s</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if data.get("query_rewrites"):
        with st.expander("Query rewrites"):
            for rw in data["query_rewrites"]:
                st.markdown(f"- {rw}")

    if data.get("sources"):
        with st.expander(f"Sources ({len(data['sources'])} passages)"):
            for s in data["sources"]:
                score = f"RRF: {s['score']:.4f}" if s.get("score") else ""
                chapter = f", {s['chapter']}" if s.get("chapter") else ""
                chunk_id = s.get("chunk_id", "")
                st.markdown(
                    f"**[{s['citation']}]** {s.get('book', '?')}{chapter} "
                    f"— {score} — `{chunk_id}`"
                )

    if tier != "powerful":
        st.caption("Switch to Opus 4.6 for richer multi-hop answers.")

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## About RagForge")
    st.markdown(
        "An end-to-end RAG system evaluating how retrieval and generation "
        "parameters affect grounded question answering on long narrative text."
    )
    st.markdown("---")
    st.markdown("## Try these questions")
    st.markdown(
        "- Who is Frodo's gardener?\n"
        "- What is the sword that was broken?\n"
        "- How was the One Ring destroyed?\n"
        "- How does Aragorn become king?\n"
        "- What happened to Boromir?\n"
        "- Who is Gollum?"
    )
    st.markdown("---")
    st.markdown("## Model details")
    st.markdown(
        "**Nova Pro** — Amazon Nova Pro\n"
        "~200-token chunks, K=20, hybrid \u03b1=0.8\n\n"
        "**Opus 4.6** — Claude Opus 4.6\n"
        "~200-token chunks, K=20, hybrid \u03b1=0.8\n\n"
        "*Same retrieval, different generator — "
        "matching the paper's held-out test design.*"
    )
    st.markdown("---")
    st.caption("Jonathan Lindahl — DePaul University — MS Data Science Capstone 2026")
