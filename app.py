import streamlit as st
import requests
import time

API_URL = st.secrets.get("API_URL", "")

st.set_page_config(page_title="RagForge", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { color: #e0d8c8; }
    header[data-testid="stHeader"] { background: transparent; }
    footer { display: none; }
    .block-container { max-width: 760px; padding-top: 2rem; }
    .title-block { text-align: center; padding-top: 12vh; padding-bottom: 2.5rem; }
    .title-block h1 { font-size: 3.6rem; font-weight: 300; letter-spacing: 0.03em; margin-bottom: 0.5rem; }
    .title-block p { color: #888; font-size: 1.1rem; }
    .stTextInput label { display: none !important; }
    .stTextInput input { font-size: 1.1rem !important; }
    .stSelectbox label { display: none !important; }
    .stSelectbox > div > div { min-width: 130px !important; }
    .answer-box {
        background: #1a1a2e; border: 1px solid #2a2a3e; border-radius: 12px;
        padding: 2rem; margin: 1.5rem 0; line-height: 1.85; font-size: 1.05rem;
    }
    .metrics-row {
        display: flex; gap: 1.5rem; flex-wrap: wrap; color: #888;
        font-size: 0.82rem; margin-top: 0.8rem; padding-top: 0.8rem;
        border-top: 1px solid #2a2a3e;
    }
    .metrics-row span { color: #bbb; }
    .streamlit-expanderHeader { color: #888 !important; font-size: 0.85rem !important; }
    .streamlit-expanderContent { background: #0f0f18 !important; }
    .stCaption { color: #555 !important; }
    section[data-testid="stSidebar"] { background: #0e0e16; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-block">
    <h1>RagForge</h1>
    <p>Retrieval-Augmented Generation over the Lord of the Rings corpus</p>
</div>
""", unsafe_allow_html=True)

model_map = {"Nova Pro (fast)": "nova_pro", "Opus 4.6 (advanced)": "opus"}

col_q, col_m = st.columns([5, 1])
with col_q:
    question = st.text_input("query", placeholder="Ask anything about Lord of the Rings...", label_visibility="collapsed")
with col_m:
    model_label = st.selectbox("model", list(model_map.keys()), index=0, label_visibility="collapsed")

model_choice = model_map[model_label]

if question:
    if not API_URL:
        st.error("API_URL not configured. Add it to .streamlit/secrets.toml")
        st.stop()

    with st.spinner("Searching the texts of Middle-earth..."):
        start = time.time()
        try:
            resp = requests.post(API_URL, json={"question": question, "model": model_choice}, timeout=300)
            elapsed = time.time() - start
            data = resp.json()
        except Exception as e:
            st.error(f"Request failed: {str(e)}")
            st.stop()

    answer = data.get("answer", "No answer returned.")
    is_mh = data.get("is_multi_hop", False)
    q_type = "Multi-hop" if is_mh else "Factoid"
    num_sources = len(data.get("sources", []))
    config_str = "~200-tok | K=20 | hybrid α=0.8"

    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="metrics-row">'
        f'<div>Model: <span>{model_label}</span></div>'
        f'<div>Type: <span>{q_type}</span></div>'
        f'<div>Passages: <span>{num_sources}</span></div>'
        f'<div>Config: <span>{config_str}</span></div>'
        f'<div>Latency: <span>{elapsed:.1f}s</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if data.get("query_rewrites"):
        with st.expander(f"Sub-questions ({len(data['query_rewrites'])} generated)"):
            for i, rw in enumerate(data["query_rewrites"], 1):
                st.markdown(f"**{i}.** {rw}")

    if data.get("sources"):
        with st.expander(f"Sources ({num_sources} passages)"):
            for s in data["sources"]:
                score_val = s.get('score', 0)
                score_str = f"RRF: {score_val:.4f}"
                chapter = s.get('chapter', '')
                st.markdown(
                    f"**[{s['citation']}]** {s.get('book', '?')} — {chapter} — "
                    f"{score_str} — `{s.get('chunk_id', '')}`"
                )

with st.sidebar:
    st.markdown("## About RagForge")
    st.markdown(
        "A capstone research project evaluating **retrieval strategies** "
        "in Retrieval-Augmented Generation systems over the Lord of the Rings trilogy."
    )
    st.markdown("---")

    st.markdown("## Pipeline")
    st.markdown(
        "1. **Embed** question (Amazon Titan v2)\n"
        "2. **Retrieve** passages (hybrid dense + BM25, α=0.8)\n"
        "3. **Detect** question type (factoid vs multi-hop)\n"
        "4. **Decompose** multi-hop into sub-questions\n"
        "5. **Generate** answer with citations\n"
    )
    st.markdown("---")

    st.markdown("## Final Results (held-out test, n=251)")
    st.markdown(
        "**Nova Pro** — 79.3% keyword / 74.5% judge\n\n"
        "**Opus 4.6** — 90.4% keyword / 87.6% judge\n\n"
        "Both: ~200-tok chunks, K=20, hybrid α=0.8\n"
    )
    st.markdown("---")

    st.markdown("## Key Findings")
    st.markdown(
        "- Opus outperforms Nova Pro by +13% judge accuracy on identical retrieval\n"
        "- Hybrid retrieval (α=0.8) outperforms pure dense\n"
        "- Keyword scoring inflates accuracy by ~3-5%\n"
        "- Generation quality is a larger bottleneck than retrieval design\n"
        "- 3,417 chunks across all 3 books\n"
    )
    st.markdown("---")

    st.markdown("## Try These")
    st.markdown("**Factoid:** Who is Frodo's gardener?")
    st.markdown("**Factoid:** What is the name of Gandalf's sword?")
    st.markdown("**Multi-hop:** How was the One Ring destroyed?")
    st.markdown("**Multi-hop:** What happened to Saruman after Isengard?")
    st.markdown("---")
    st.markdown("*Jonathan Lindahl — DePaul University — 2026*")
