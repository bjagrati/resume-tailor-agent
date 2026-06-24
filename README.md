# resume-tailor-agent

An AI-powered résumé tailoring tool that takes your résumé and a job description, and returns honest, per-bullet recommendations — without inventing experience you don't have.

Built with the Anthropic API, Pydantic, and FastAPI. Hallucination-resistant by design.

---

## What It Does

You upload (or paste) your résumé, paste a job description, and click Analyze. About 30-45 seconds later, you get:

- **Alignment score** (1-10) with honest 2-3 sentence assessment
- **Per-skill match** — every required and nice-to-have skill, marked present/absent with cited evidence from your résumé
- **Biggest gaps** — what's missing from your résumé that the JD demands
- **Missing ATS keywords** — specific terms an applicant tracking system would scan for
- **Per-bullet recommendations** — for each bullet on your résumé: keep, rewrite (with concrete rewrite), or drop, with reasoning
- **Suggested summary** — tailored to the role using only facts already on your résumé
- **Skills to add** — items you demonstrate in bullets but didn't put in your Skills section

### The "no lying" guarantee

The system is engineered to refuse fabrication. Rewrites must be traceable back to the original bullet's actual content. The system prompt enforces:

- No inventing technologies, methodologies, or metrics not in the original
- No quietly changing words that constrain meaning ("junior engineers" stays "junior engineers")
- No inventing career arcs ("Flask, foundation for FastAPI" is forbidden)
- When in doubt → keep the original

This is unusual for résumé tailoring tools. Most LLM-based tools eagerly fabricate to "make you look good." This one explicitly doesn't.

---

## Architecture

[Browser UI]  ─►  [FastAPI]  ─►  [Service layer]  ─►  4× Anthropic Claude API calls

│

├─► parse_job_description()  → JobAnalysis

├─► parse_resume()           → Resume

├─► analyze_gap()            → GapAnalysis

└─► generate_recommendations() → TailoringRecommendations

Each LLM call uses **Anthropic's tool use feature** with a Pydantic-generated JSON schema, guaranteeing structured output.

### Components

| Path | Role |
|------|------|
| `src/core/models.py` | Pydantic models defining every structured shape |
| `src/core/llm.py` | Reusable `structured_call()` — sends any Pydantic model to Claude, returns a validated instance |
| `src/core/comparator.py` | Compares parsed résumé to parsed JD, returns gap analysis |
| `src/core/tailor.py` | Generates per-bullet rewrite recommendations with strict anti-hallucination prompt |
| `src/core/service.py` | Orchestrates the 4-step pipeline |
| `src/interfaces/web/api.py` | FastAPI endpoints |
| `src/interfaces/web/static/` | HTML/CSS/JS frontend |

---

## Tech Stack

- **Python 3.12**
- **Anthropic Claude API** (`claude-sonnet-4-6`) — LLM provider
- **Pydantic v2** — structured output schema + validation
- **FastAPI + Uvicorn** — REST API
- **PyMuPDF** — PDF text extraction
- **python-dotenv** — secrets management
- **Plain HTML/CSS/JS** — frontend (no framework)

---

## Setup

### Prerequisites

- Python 3.10+ (3.12 recommended)
- An Anthropic API key (get one at https://console.anthropic.com — small free credit available, $5 prepaid is more than enough)

### Install

```bash
git clone https://github.com/bjagrati/resume-tailor-agent.git
cd resume-tailor-agent

python3.12 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root with your API key:
ANTHROPIC_API_KEY=sk-ant-your-key-here

The `.env` file is gitignored and will never be committed.

### Run

```bash
uvicorn src.interfaces.web.api:app --reload --port 8001
```

Then open:
- **http://localhost:8001/ui/** — the web UI
- **http://localhost:8001/docs** — auto-generated API documentation

---

## Cost

Each full résumé analysis makes 4 Claude API calls. Typical cost: **about $0.05 per analysis** (using Claude Sonnet 4.6). A $5 prepaid credit covers 80-100 analyses, more than enough for an entire job search.

---

## What I Learned Building This

This project was about applying real AI engineering patterns:

- **Structured output via tool use** — the production-grade alternative to "prompt and pray for valid JSON"
- **Schema design as prompt engineering** — Pydantic field descriptions directly shape model behavior
- **The hallucination iteration loop** — building, observing outputs critically, identifying fabrication failure modes, and tightening the prompt with concrete forbidden examples
- **Multi-step LLM pipelines** — decomposing one task into four focused calls produces dramatically better results than one mega-prompt
- **Hexagonal architecture** — core engine usable from any interface (CLI, web, etc.)

---

## Roadmap

- [ ] Multi-version résumé output — let users pick which rewrites to accept and download the final résumé
- [ ] Local LLM support (Ollama) for offline / private use
- [ ] Cover letter generator using the same structured-output pattern
- [ ] Deployment to a public URL (Render, Railway, or Fly.io)
- [ ] Evaluation harness — test set of résumé/JD pairs with expected scores

---

## License

MIT

---

## Author

Built by Jagrati Bhardwaj while job hunting. The motivation was simple: I needed this tool, and I wanted to learn the production AI engineering stack while building it.