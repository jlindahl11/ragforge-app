# RagForge

A retrieval-augmented generation (RAG) system built over the complete text of J.R.R. Tolkien's *Lord of the Rings* trilogy, evaluating how RAG design choices affect grounded question answering on long narrative text.

[**Live Demo**](https://ragforge.streamlit.app) · [**Paper (PDF)**](link-to-paper)

## What This Is

RagForge is my MS Data Science capstone project at DePaul University. The system chunks \~576,000 words into 3,417 retrievable passages, embeds them with Amazon Titan v2, stores them in Pinecone, and retrieves evidence using hybrid dense–BM25 search before generating answers with Amazon Nova Pro or Claude Opus 4.6.

A curated dataset of 1,000 questions (749 training, 251 held-out test) was used for systematic evaluation across retrieval and generation parameters.

## Key Findings

* **Generator capability > retrieval tuning.** On identical retrieval (same chunks, same 89.6% hit rate), Opus 4.6 achieved 87.6% judge accuracy vs. Nova Pro's 74.5% — a 13.1-point gap that exceeds all retrieval tuning gains combined.
* **Keyword scoring inflates accuracy by 3–5 points** relative to LLM-judge evaluation.
* **Query expansion and calibrated abstention both failed** to improve performance on literary text, despite being recommended by the literature.

## Architecture

```
User Question
    │
    ├── Embed (Amazon Titan v2, 1024-dim)
    │
    ├── Retrieve (hybrid dense + BM25, α=0.8, K=20)
    │
    ├── Detect question type (factoid vs multi-hop)
    │   └── Decompose multi-hop → 2-3 sub-questions (Llama 3.2 3B)
    │
    └── Generate answer with citations
        ├── Nova Pro (fast)
        └── Opus 4.6 (advanced)
```

Both models use identical retrieval: \~200-token chunks, K=20, hybrid search (α=0.8).

## Held-Out Test Results (n=251)

|Metric|Nova Pro|Opus 4.6|Δ|
|-|-|-|-|
|Keyword Accuracy|79.3%|90.4%|+11.1%|
|Judge Accuracy|74.5%|87.6%|+13.1%|
|Judge Multi-hop|77.4%|96.8%|+19.4%|
|Hit Rate|89.6%|89.6%|same|

## Running Locally

```bash
git clone https://github.com/jlindahl11/ragforge-app.git
cd ragforge-app
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:

```toml
API_URL = "your-api-gateway-url"
```

```bash
streamlit run app.py
```

## Infrastructure

* **Frontend:** Streamlit (deployed on Streamlit Community Cloud)
* **Backend:** AWS Lambda + API Gateway
* **Vector DB:** Pinecone
* **Embeddings:** Amazon Titan Embed Text v2
* **Models:** Amazon Nova Pro, Claude Opus 4.6 (via AWS Bedrock)
* **Evaluation:** SageMaker notebooks (ml.t3.medium)

## Project Structure

```
ragforge-app/
├── app.py                  # Streamlit frontend
├── requirements.txt
├── .streamlit/
│   ├── config.toml         # Streamlit theme
│   └── secrets.toml.example
├── .gitignore
└── README.md
```

## Author

**Jonathan Lindahl** — DePaul University, College of Computing and Digital Media
MS in Data Science Capstone, 2026
Advisor: Professor David Hubbard

