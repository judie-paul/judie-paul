<img width="100%" src="assets/hero.svg?v=1" alt="Judy Ndungu: a human model card for AI evaluation and data quality" />

<div align="center">

<!-- BADGE:START --><a href="https://github.com/judie-paul?tab=repositories"><img src="https://img.shields.io/badge/projects-11_public-5b3fa0?style=flat-square&labelColor=0f0b1e" /></a><!-- BADGE:END -->
<img src="https://img.shields.io/badge/status-open_to_work-e879f9?style=flat-square&labelColor=0f0b1e" />
<img src="https://img.shields.io/badge/card-updated_daily-a78bfa?style=flat-square&labelColor=0f0b1e" />

</div>

> [!NOTE]
> Every AI model ships with a **model card**: what it is, what it's for, how it was evaluated, and where it falls short.
> Judy evaluates AI for a living, so here is hers.

<img width="100%" src="assets/divider.svg?v=lav" />

## 📇 Model details

| | |
|:--|:--|
| **Developed by** | Judy Ndungu |
| **Model type** | Human · AI evaluator who also builds the tools |
| **Specialisation** | AI output evaluation · inter-rater agreement · LLM-as-a-judge reliability · annotation QA · grounded generation |
| **Languages** | Python · Go · TypeScript · SQL |
| **Release** | `judy.v2026`, with <!-- COUNT:START -->11<!-- COUNT:END --> public checkpoints |
| **License** | 🟢 Open to work |

## 🎯 Intended use

- ✅ Roles in **AI evaluation, data quality and analytics**
- ✅ Designing rubrics, and measuring whether raters (human or model) actually agree
- ✅ Building AI tools that show their sources and survive their own tests

**Out-of-scope use**

- ❌ Inventing citations, DOIs or metrics (`citewise-ai` refuses to)
- ❌ Shipping code that hasn't been tested
- ❌ Vibes-based evaluation

<img width="100%" src="assets/divider.svg?v=lav" />

## 📊 Benchmark highlights

<img width="100%" src="assets/metrics.svg?v=1" alt="About 3,300 MT-Bench expert votes, 92 tests, 97% coverage, 5 pipeline checkpoints, 10 public projects" />

## 🧪 Evaluation protocol

<img width="100%" src="assets/trust-pipeline.svg?v=1" alt="Animated trust pipeline: an AI answer is checked by each of Judy's tools before it is stamped trusted" />

| Checkpoint | Result | Evidence |
|:--|:--:|:--|
| Measures rater agreement | ✅ | Cohen's kappa, exact agreement and overturn rate across independent scorers in `rubricops` |
| Knows when an AI judge is biased | ✅ | Position and verbosity bias against ~3,300 MT-Bench expert votes in `judgecheck` |
| Audits training labels | ✅ | Flags contradictions, duplicate rationales and speed anomalies, with evidence for each, in `labellint` |
| Doesn't let AI invent sources | ✅ | Every quote checked against its source page in `reference-based-revision-tool`; only real Crossref/OpenAlex records in `citewise-ai` |
| Tests before shipping | ✅ | 92 tests + CI in `judgecheck` · 97% coverage in `labellint` · Playwright browser tests in `rubricops` |
| Sandboxed patch evaluation | 🔄 | `patchbench` runs a repo's own tests in isolated Docker containers (in progress) |

<img width="100%" src="assets/divider.svg?v=lav" />

## 📦 Released checkpoints

<!-- PROJECTS:START -->
**🧪 AI evaluation & data quality**

<p align="center">
  <a href="https://github.com/judie-paul/rubricops"><img src="assets/cards/rubricops.svg?v=2a715bf" width="49%" alt="RubricOps" /></a>
  <a href="https://github.com/judie-paul/judgecheck"><img src="assets/cards/judgecheck.svg?v=4e5dbd4" width="49%" alt="JudgeCheck" /></a>
  <a href="https://github.com/judie-paul/labellint"><img src="assets/cards/labellint.svg?v=676412a" width="49%" alt="LabelLint" /></a>
  <a href="https://github.com/judie-paul/patchbench"><img src="assets/cards/patchbench.svg?v=029b56c" width="49%" alt="PatchBench" /></a>
</p>


**📚 Grounded AI apps**

<p align="center">
  <a href="https://github.com/judie-paul/reference-based-revision-tool"><img src="assets/cards/reference-based-revision-tool.svg?v=3212785" width="32.6%" alt="Revision Tool" /></a>
  <a href="https://github.com/judie-paul/citewise-ai"><img src="assets/cards/citewise-ai.svg?v=38c63b1" width="32.6%" alt="CiteWise AI" /></a>
  <a href="https://github.com/judie-paul/github-resume-generator"><img src="assets/cards/github-resume-generator.svg?v=c104701" width="32.6%" alt="GitHub → Resume" /></a>
</p>


**🛠️ Web apps**

<p align="center">
  <a href="https://github.com/judie-paul/shoebox"><img src="assets/cards/shoebox.svg?v=feabd69" width="49%" alt="Shoebox" /></a>
  <a href="https://github.com/judie-paul/school-management-system"><img src="assets/cards/school-management-system.svg?v=0dbc916" width="49%" alt="School Management" /></a>
  <a href="https://github.com/judie-paul/contractor-application"><img src="assets/cards/contractor-application.svg?v=71496d1" width="49%" alt="Contractor Application" /></a>
  <a href="https://github.com/judie-paul/kanban"><img src="assets/cards/kanban.svg?v=d6d6f40" width="49%" alt="kanban" /></a>
</p>
<!-- PROJECTS:END -->

<img width="100%" src="assets/divider.svg?v=lav" />

## 🏋️ Training activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/judie-paul/judie-paul/output/training-dark.svg">
  <img src="https://raw.githubusercontent.com/judie-paul/judie-paul/output/training.svg" width="100%" alt="Training run: cumulative contributions with daily activity, total, active days and streaks">
</picture>

<details>
  <summary>Full contribution calendar</summary>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/judie-paul/judie-paul/output/calendar-dark.svg">
    <img src="https://raw.githubusercontent.com/judie-paul/judie-paul/output/calendar.svg" width="100%" alt="This year's contribution calendar">
  </picture>
</details>

## 🧰 Architecture

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,go,ts,fastapi,nextjs,react,postgres,sqlite,prisma,docker,githubactions,git,linux,vscode&perline=14" />
</p>

## ⚠️ Known limitations

An honest model card lists what isn't finished yet.

- 🔄 **PatchBench is in progress.** Sandboxed patch evaluation is the current focus.
- ⏳ **JudgeCheck's model-judge study is still running.** Results get published when they're real, not before.
- 🧪 **LabelLint's scores come from synthetic data**, and its README says so.

<img width="100%" src="assets/divider.svg?v=lav" />

## 📎 Citation

If this model is useful to you, please cite it. Better still, get in touch:

```bibtex
@person{ndungu2026judy,
  name   = {Judy Ndungu},
  focus  = {AI evaluation, data quality, analytics},
  github = {github.com/judie-paul},
  email  = {judyjudith119@gmail.com},
  status = {open to work}
}
```

<div align="center">

<a href="mailto:judyjudith119@gmail.com"><img src="https://img.shields.io/badge/Email-0f0b1e?style=for-the-badge&logo=gmail&logoColor=C4A7FF" /></a>
<a href="https://github.com/judie-paul"><img src="https://img.shields.io/badge/GitHub-0f0b1e?style=for-the-badge&logo=github&logoColor=white" /></a>
<!-- LINKEDIN: replace YOUR_LINKEDIN, then delete this comment's opening and closing markers to show it.
<a href="https://linkedin.com/in/YOUR_LINKEDIN"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
-->

</div>

<img width="100%" src="assets/footer.svg?v=1" alt="End of model card" />
