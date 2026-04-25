# Network AI Auditor Agent – Knowledge Inputs

## Purpose
Define exactly what knowledge sources the network AI auditor agent should read, how they should be prioritized, and how each source should be used.

This file exists to prevent vague retrieval behavior.
The agent should not read everything equally.
It should read the right source for the right purpose.

The agent is designed to be:
- knowledge-base first,
- standards-aware,
- uncertainty-aware,
- and externally augmentable only under controlled conditions.

That means internal documented knowledge always comes first.
Trusted external sources may be used only when needed and only in a clearly labeled way.

---

## Core Design Principle

The knowledge base is layered.

Different files serve different purposes:
- some files contain structured facts,
- some files contain narrative context,
- some files contain uncertainty boundaries,
- and some files contain external control expectations.

The agent should retrieve from these layers deliberately rather than treating the knowledge base as a flat document collection.

---

## Input Priority Model

The agent should use the following priority order when answering questions.

### Priority 1 — Structured Domain Model
These files should be the primary source for direct lookups and structured grounding.

Files:
- `knowledge/domains/network/model.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/index.yaml`

Use these first for:
- scope unit lookup
- entity lookup
- dependency lookup
- required flow lookup
- technical matrix lookup
- target intent summary lookup
- unnecessary access lookup
- open question lookup
- domain metadata lookup

These files are the best starting point because they are:
- structured,
- normalized,
- machine-readable,
- and designed for direct agent consumption.

---

## Priority 2 — Domain Markdown Files
These files provide supporting context, nuance, explanation, and traceability.

Files:
- `knowledge/domains/network/scope/scope_units.md`
- `knowledge/domains/network/scope/services.md`
- `knowledge/domains/network/scope/dependencies.md`
- `knowledge/domains/network/communication/required_flows.md`
- `knowledge/domains/network/communication/technical_matrix.md`
- `knowledge/domains/network/evidence/evidence_notes.md`
- `knowledge/domains/network/posture/unnecessary_access.md`
- `knowledge/domains/network/posture/target_intent.md`
- `knowledge/domains/network/uncertainty/open_questions.md`

Use these when the agent needs:
- explanation beyond the structured YAML,
- additional context,
- traceability,
- reasoning nuance,
- human-readable clarification,
- or supporting narrative around a structured fact.

Markdown should support reasoning, not replace structured grounding.

---

## Priority 3 — Standards Layer
This layer provides structured external expectations that the agent can use for comparison.

Files:
- `knowledge/standards/mappings/control_references.yaml`

Use this layer when the question involves:
- standards alignment,
- likely control misalignment,
- segmentation expectations,
- least-privilege expectations,
- controlled administrative access,
- boundary protection,
- controlled egress,
- or other audit-style comparison tasks.

Important:
This layer is not a complete framework library.
It is a lightweight and expandable structured reference layer.

The agent must understand:
- the listed controls are useful comparison inputs,
- the file may expand over time,
- and the absence of a control here does not mean the control is irrelevant.

---

## Priority 4 — Architecture and Rules Layer
These files provide interpretation rules, architecture rules, and knowledge model constraints.

Files:
- `knowledge/_meta/ARCHITECTURE.md`
- `knowledge/_meta/RULES.md`

Use these when the agent needs to understand:
- what a file is supposed to represent,
- what belongs in each layer,
- what the knowledge base stores,
- and what the knowledge base explicitly does not store.

This layer should shape agent behavior, not dominate question answering.

---

## Priority 5 — Trusted External Sources
These are not default knowledge sources.
They are optional augmentation sources used only when the question requires broader standards comparison or external best-practice context.

Examples of acceptable source categories:
- official framework documentation
- official standards publications
- official vendor hardening guidance
- recognized regulatory guidance
- authoritative security architecture guidance

These sources should be used only when:
- the user explicitly asks for broader external comparison,
- the structured standards layer is clearly insufficient for the question,
- or the answer would materially benefit from a trusted external reference.

These sources should not be used:
- as a substitute for the internal knowledge base,
- as a shortcut around missing internal facts,
- or as a reason to make strong claims from weak sources.

---

## Internal vs External Source Rule

When both internal and external sources are used, the agent must distinguish them clearly.

The answer should make clear:
- what is documented in the internal KB,
- what is inferred from internal documented material,
- and what comes from external trusted sources.

The agent must never blend external guidance into the internal model silently.

If a source is external, that must be visible in the reasoning and in the answer wording.

---

## Source Usage by Question Type

### 1. Direct Fact Questions
Examples:
- What is APP01?
- Which scope unit contains IAM01?
- What does DB01 depend on?

Primary source:
- `model.yaml`

Fallback / support:
- relevant scope or dependency markdown files

External sources:
- not needed

---

### 2. Required Communication Questions
Examples:
- What flows are required for APP02?
- Does IAM01 need to talk to DC01-CYBERAUDIT?
- What outbound path does DB01 use?

Primary source:
- `model.yaml`
- `required_flows.md`
- `technical_matrix.md`

Support:
- `evidence_notes.md`
- `dependencies.md`

External sources:
- not needed unless the user explicitly asks for outside comparison

---

### 3. Technical Detail Questions
Examples:
- What port does APP01 use to talk to DB01?
- Is LDAP documented between IAM01 and DC01-CYBERAUDIT?
- What protocol is used for the proxy path?

Primary source:
- `technical_matrix.md`
- `model.yaml`

Support:
- `evidence_notes.md`

External sources:
- not needed

---

### 4. Overly Broad Access Questions
Examples:
- What access currently appears broader than necessary?
- Is APP_ZONE too open?
- Which paths should not remain broad?

Primary source:
- `unnecessary_access.md`
- `model.yaml`

Support:
- `required_flows.md`
- `target_intent.md`

External sources:
- only if the user asks for broader external best-practice comparison

---

### 5. Intended Posture Questions
Examples:
- What is the intended posture of SERVICE_ZONE?
- What should happen to ADMIN_SEGMENT in the final design?
- Is WAN supposed to remain blocked by default?

Primary source:
- `target_intent.md`
- `model.yaml`

Support:
- `unnecessary_access.md`
- `open_questions.md`

External sources:
- only if the user asks how this posture relates to external guidance

---

### 6. Standards-Aware Audit Questions
Examples:
- What seems inconsistent with the documented standards expectations?
- Which current access patterns appear misaligned with least privilege?
- Does the current design appear broader than the documented control expectations?

Primary source:
- `model.yaml`
- `target_intent.md`
- `control_references.yaml`

Support:
- `unnecessary_access.md`
- `required_flows.md`
- `technical_matrix.md`
- `open_questions.md`

External sources:
- permitted only when the user asks for broader external comparison or the documented control layer is clearly incomplete for the question

---

### 7. Uncertainty Questions
Examples:
- What is still unresolved in the network model?
- What cannot be judged confidently yet?
- Which parts of the architecture are still provisional?

Primary source:
- `open_questions.md`
- `model.yaml`

Support:
- `evidence_notes.md`
- `target_intent.md`

External sources:
- not needed

---

### 8. External Best-Practice Questions
Examples:
- What else might be missing even if it is not documented in my KB?
- Are there external best practices relevant here that are not yet listed internally?
- Does trusted external guidance suggest additional concerns?

Primary source:
- internal KB first

Support:
- `control_references.yaml`

External sources:
- yes, but only from trusted and clearly identified sources

The answer must distinguish:
- internal documented issues
- from externally suggested additional concerns

---

## Retrieval Rule

The agent should not retrieve all files by default.

Instead, it should:
1. classify the question,
2. determine which layer is most relevant,
3. read structured files first,
4. read markdown context only where needed,
5. consult standards only when comparison is relevant,
6. consult trusted external sources only when justified,
7. and consult uncertainty before making strong conclusions.

This keeps answers:
- grounded,
- efficient,
- and logically scoped.

---

## Structured-First Rule

If the needed fact exists clearly in `model.yaml`, the agent should use that as the primary grounding source.

Markdown files should be used to:
- confirm nuance,
- add explanation,
- provide context,
- or support a more careful answer.

The agent should avoid ignoring the structured model when the answer is already present there.

---

## Uncertainty Gate

Before making a strong architectural or audit-style statement, the agent should check whether uncertainty affects the answer.

Relevant sources:
- `open_questions.md`
- confidence tags in the technical matrix
- evidence notes where applicable

If the answer depends on unresolved information, the agent should say so clearly.

---

## Standards Usage Rule

When using `control_references.yaml`, the agent should:
- use it as structured expectation input,
- compare it against current documented facts and intended posture,
- and avoid treating it as exhaustive framework coverage.

The agent must not say:
- “this is fully compliant”
- “this is definitively non-compliant”
unless the documented evidence is unusually strong and the reasoning is fully grounded.

Safer default language is:
- appears inconsistent with
- likely broader than
- directionally aligned with
- may represent over-permission relative to
- cannot be judged confidently because

---

## External Source Discipline Rule

When using trusted external sources, the agent should:
- prefer official and authoritative sources,
- avoid weak secondary commentary where possible,
- make the source category clear,
- use external guidance to enrich comparison rather than replace internal grounding,
- and avoid overclaiming based on one external statement alone.

If source quality or relevance is uncertain, the agent should say so rather than forcing a conclusion.

---

## Final Input Summary

The agent should think about knowledge inputs like this:

- `model.yaml` = primary structured facts
- domain markdown files = context and nuance
- `control_references.yaml` = structured external expectations already documented in the KB
- `open_questions.md` = uncertainty boundaries
- `_meta` files = architecture rules and interpretation constraints
- trusted external sources = optional augmentation when explicitly justified

A strong answer usually comes from combining these layers deliberately rather than relying on only one file.