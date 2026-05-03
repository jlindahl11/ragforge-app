# RagForge

An end-to-end Retrieval-Augmented Generation system built over J.R.R. Tolkien's *Lord of the Rings* trilogy, evaluating how RAG design choices affect grounded question answering on long narrative text.

**Live app:** [ragforge.streamlit.app](https://ragforge.streamlit.app)

## Architecture

- **Frontend:** Streamlit (this repo)
- **Backend:** AWS Lambda + API Gateway
- **Retrieval:** Pinecone vector DB with hybrid dense–BM25 search
- **Embeddings:** Amazon Titan Embed Text v2 (1,024-dim)
- **Generation:** Amazon Nova Pro (Simple) / Claude Opus 4.6 (Advanced)

## Key Results

| Metric | Nova Pro | Opus 4.6 |
|--------|----------|----------|
| Judge Accuracy | 74.5% | 87.6% |
| Multi-hop Accuracy | 77.4% | 96.8% |
| Hit Rate | 89.6% | 89.6% |

Generator capability was a larger bottleneck than retrieval tuning — Opus outperformed Nova Pro by 13.1 points on identical retrieval.

## Local Development

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your API Gateway URL
streamlit run app.py
```

## Author

Jonathan Lindahl — DePaul University — MS Data Science Capstone 2026
