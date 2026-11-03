<h1 align="center">Judy Ndungu</h1>
<p align="center"><b>AI evaluation & data quality</b> · I build tools that measure whether human and model judgments can be trusted — and AI apps that cite their sources.</p>

<p align="center">
  <a href="mailto:YOUR_EMAIL"><img src="https://img.shields.io/badge/Email-222?style=flat&logo=gmail&logoColor=white" alt="Email"></a>
  <a href="https://www.linkedin.com/in/YOUR_LINKEDIN"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
  <img src="https://img.shields.io/badge/Based%20in-Nairobi%2C%20Kenya-555?style=flat" alt="Nairobi, Kenya">
</p>

---

### About

I work in AI output evaluation and quality assurance — scoring model responses, auditing other evaluators' work, and writing evidence-based rationales. My projects turn that work into software: rubric pipelines, agreement metrics, bias checks and annotation audits, plus AI tools that refuse to make things up.

**Focus areas:** inter-rater agreement · LLM-as-a-judge reliability · annotation QA · rubric design · grounded generation

---

### 🧪 AI evaluation

| Project | What it does | Stack |
|---|---|---|
| **[RubricOps](https://github.com/judie-paul/rubricops)** | Evaluation review platform: versioned rubrics, two independent scores per task, sampled reviewer audits, adjudication, and a dashboard for Cohen's kappa, exact agreement and overturn rate. | TypeScript · Next.js · PostgreSQL · Prisma · Playwright |
| **[JudgeCheck](https://github.com/judie-paul/judgecheck)** | How far can LLM judges be trusted? Measures agreement, position bias and verbosity bias against ~3,300 MT-Bench expert votes across direct, rationale and rubric prompting. 92 tests, CI on Python 3.11/3.12. | Python · Streamlit · Ollama · OpenAI/Anthropic SDKs |
| **[LabelLint](https://github.com/judie-paul/labellint)** | Offline-first annotation audit pipeline that flags duplicate rationales, rating/rationale contradictions, speed and agreement anomalies — with evidence for each flag. F1 ≈ 0.82–0.84 on seeded synthetic data; 97% test coverage. | Python · FastAPI · Typer · React |
| **[PatchBench](https://github.com/judie-paul/patchbench)** | SWE-bench-style runner that checks whether a proposed code patch actually fixes an issue without breaking anything, by running the repo's own tests in an isolated Docker container. *(In progress)* | Python · Docker · FastAPI · Celery |

### 📚 Grounded AI apps

| Project | What it does | Stack |
|---|---|---|
| **[Revision Tool](https://github.com/judie-paul/reference-based-revision-tool)** | Answers past exam questions from your own uploaded notes first, and labels every answer as document-based, supplemented, external or not answered. Every cited quote is checked against the source pages. | Go · SQLite · Anthropic/OpenAI · Tavily |
| **[CiteWise AI](https://github.com/judie-paul/citewise-ai)** | Finds real academic references for an essay topic or uploaded essay via Crossref and OpenAlex, removes duplicates, and formats APA 7 or Harvard citations. Never invents publications, authors or DOIs. | Go · Crossref · OpenAlex · OpenAI |
| **[GitHub → Resume](https://github.com/judie-paul/github-resume-generator)** | Turns a public GitHub profile into an editable, ATS-friendly resume with PDF export. AI output is validated as structured JSON before display; works without an API key. | Go (standard library) · Claude API |

### 🛠️ Web apps

| Project | What it does | Stack |
|---|---|---|
| **[Shoebox](https://github.com/judie-paul/shoebox)** | Single-vendor shoe store shipped as one executable: catalog with filters, size/colour stock, cart, checkout and a vendor dashboard. | Go · SQLite · html/template |
| **[School Management System](https://github.com/judie-paul/school-management-system)** | Self-contained web app for managing students, exam results and fees, with separate staff and parent access. | Go |
| **[Contractor Application](https://github.com/judie-paul/contractor-application)** | Airtable-based contractor application pipeline. | Python · Airtable |

<sub>Metrics come from each repo's own README; LabelLint figures are on synthetic data.</sub>

---

### Toolkit

**Languages:** Python · Go · TypeScript · SQL
**Data & ML:** NumPy · Hugging Face datasets · evaluation metrics (precision/recall/F1, Cohen's kappa)
**AI:** Anthropic & OpenAI APIs · Ollama · structured output validation · citation verification
**Web & APIs:** FastAPI · Next.js · React · Streamlit · Go net/http
**Infra & quality:** PostgreSQL · SQLite · Prisma · Docker · GitHub Actions · pytest · Playwright

---

### How I build

- **Honest metrics** — every number states its data source and caveats.
- **No made-up sources** — AI output is checked against real documents and real records.
- **Reproducible** — seeded data, pinned datasets, one-command setup with Docker, `make` or a single binary.
- **Reviewer-first** — tools show the evidence behind a flag, not just a score.

<p align="center"><sub>Open to roles in AI evaluation, data quality and analytics.</sub></p>
