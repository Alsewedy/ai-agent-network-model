# Knowledge Architecture

## Knowledge Categories

Every domain organizes knowledge into up to five categories.
Three are required. Two are optional depending on domain nature.

| Category | Folder | Required | What It Answers |
|----------|--------|----------|-----------------|
| Scope | `scope/` | Always | What exists? What does it do? What depends on what? |
| Communication | `communication/` | When applicable | What communicates with what? What are the exact details? |
| Posture | `posture/` | Always | What should change? What is the target state? |
| Evidence | `evidence/` | When useful | How was each fact confirmed? |
| Uncertainty | `uncertainty/` | Always | What is not yet resolved? What are the assumptions? |

Additionally, one cross-domain layer exists outside individual domains:

| Layer | Location | Purpose |
|-------|----------|---------|
| Standards | `standards/mappings/` | External control expectations the AI auditor compares against |

---

### Scope (`scope/`)

**Required: Always**

Defines what exists within this domain. Pure description.

Files:
- `scope_units.md` — organizational structure and entity listing per unit
- `services.md` — what each entity provides, including hosted components
- `dependencies.md` — what relies on what

Entities are defined within `scope_units.md` (as members of each unit) and
described in `services.md` (with type, services, purpose). There is no
separate entities file because this would duplicate what these two already cover.

---

### Communication (`communication/`)

**Required: When the domain involves entity-to-entity communication.**

Skip this category entirely if the domain does not involve direct communication
flows (e.g., a compliance-only or policy-only domain).

Files:
- `required_flows.md` — what communication is needed and why
- `technical_matrix.md` — exact technical details with confidence tags

---

### Posture (`posture/`)

**Required: Always**

Defines the gap between current state and intended state.

Files:
- `unnecessary_access.md` — what is too broad and should be restricted
- `target_intent.md` — what the final design should look like, including
  `intended_alignment` references to external controls where applicable

**Important:** Posture files describe direction and intention. They do NOT
contain audit verdicts, compliance conclusions, or pass/fail judgments.
See Rule 9 in `_meta/RULES.md`.

---

### Evidence (`evidence/`)

**Required: When traceability matters.**

For simpler domains, inline confidence tags may be sufficient.

Files:
- `evidence_notes.md` — traceability records linking facts to sources

---

### Uncertainty (`uncertainty/`)

**Required: Always**

Files:
- `open_questions.md` — confirmed baselines, assumptions, and unresolved questions

---

### Model (`model.yaml`)

**Required: Always**

Machine-readable consolidation of structured facts.
Only facts the agent needs for direct lookup go here.
Narrative, reasoning, and explanation stay in Markdown.

---

### Domain Metadata (`domain.yaml`)

**Required: Always**

Lightweight metadata about the domain: name, last updated, owner,
open questions count, standards mapping status.

---

## Standards Layer (`standards/`)

The standards layer sits outside individual domains. It provides structured external control expectations that the AI auditor agent uses as comparison input when reasoning about the environment.

**This layer contains expectations only — never verdicts.**

It is also intentionally lightweight and expandable.
It is **not** intended to be a complete catalog of all possible controls, frameworks, or requirements.
Instead, it contains a structured starter set of relevant control references for the currently documented environment.

This means:
- the listed controls help guide structured comparison,
- the layer may expand over time,
- and the absence of a control here does **not** mean that the control is irrelevant.

File:
- `standards/mappings/control_references.yaml` — framework, control ID, title, plain-English expectation, relevant domains, relevant scope units, typical evidence types, and optional applicability notes.

The AI auditor's reasoning flow:
1. Read environment facts from domain knowledge
2. Read intended posture from `posture/target_intent.md`
3. Read structured external expectations from `standards/mappings/`
4. Compare and generate findings, gaps, and observations

Steps 1–3 are knowledge base inputs. Step 4 is agent output — never stored in the KB.

---

## What Goes in YAML vs What Stays in Markdown

| YAML | Markdown Only |
|------|---------------|
| Entities with names, types, scope units | Narrative reasoning about why entities exist |
| Dependencies as source→target pairs | Detailed dependency reasoning |
| Flows with ports, protocols, confidence | Hardening notes and architectural commentary |
| Unnecessary access as structured list | Detailed reasoning about why access is unnecessary |
| Open questions as a flat list | Assumptions with status and impact analysis |
| Target intent as per-unit summaries | Full narrative security direction |
| Intended alignment as structured references | Contextual notes about control applicability |
| Confidence tags on technical facts | Evidence traceability records |

**Rule:** If the agent needs it for filtering, matching, or comparing → YAML.
If it provides reasoning, context, or explanation → Markdown only.
