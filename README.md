# RagForge

An end-to-end Retrieval-Augmented Generation system built over J.R.R. Tolkien's *Lord of the Rings* trilogy, evaluating how RAG design choices affect grounded question answering on long narrative text.

**Live app:** [ragforge-app.streamlit.app](https://ragforge-app.streamlit.app)

![RagForge app screenshot](https://github.com/user-attachments/assets/1504214a-c013-454e-a14f-6daccd919773)

## Architecture

- **Frontend:** Streamlit (this repo)
- **Backend:** AWS Lambda + API Gateway (serverless)
- **Corpus storage:** Amazon S3
- **Retrieval:** Pinecone vector DB with hybrid dense–BM25 search (α = 0.8)
- **Embeddings:** Amazon Titan Embed Text v2 (1,024-dim)
- **Generation:** Amazon Nova Pro (Simple) / Claude Opus 4.6 (Advanced), both via Amazon Bedrock

## Evaluation

Both generators were evaluated on a held-out set of 251 questions (88% factoid, 12% multi-hop), with answers graded by an LLM-as-judge against the source passages. Keyword-match accuracy is reported alongside judge accuracy to show how much string-matching overstates true correctness.

Parameters held constant across the model comparison:

- Chunk size: 200 tokens
- Retrieved passages: K = 20
- Hybrid weighting: α = 0.8 (dense-leaning)
- Generation temperature: 0.0

## Key Results

| Metric | Nova Pro | Opus 4.6 |
|--------|----------|----------|
| Keyword Accuracy | 79.3% | 90.4% |
| Judge Accuracy | 74.5% | 87.6% |
| Judge Accuracy (multi-hop) | 77.4% | 96.8% |
| Hit Rate | 89.6% | 89.6% |

With retrieval held constant at an 89.6% hit rate, the generator was the dominant bottleneck rather than retrieval tuning. Opus 4.6 beat Nova Pro by 13.1 points on overall judge accuracy and by 19.4 points on multi-hop questions, over identical retrieved context. Keyword scoring overstated accuracy by roughly 5 points for Nova Pro and 3 points for Opus, which is why judge accuracy is treated as the primary metric.

## Local Development

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your API Gateway URL
streamlit run app.py
```

## Author

Jonathan Lindahl — MS in Data Science, DePaul University (2026)
Capstone project, presented at the 2026 Jarvis Innovation Showcase.
