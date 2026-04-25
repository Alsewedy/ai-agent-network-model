# Retrieval Strategy

## Purpose
Define how the RAG retriever selects chunks from `rag/chunks.json` for a given question.

This document explains the retrieval logic conceptually.
It does not describe the full agent pipeline.
It only describes the markdown retrieval layer.

The retrieval system is designed to support:
- network reasoning
- hardening questions
- flow-related questions
- uncertainty-related questions
- and posture comparison questions

while remaining aligned with the new domain-based knowledge architecture.

---

## Core Retrieval Principle

The retriever is not intended to answer the question by itself.

Its role is to:
- identify the most relevant markdown chunks
- provide contextual support
- improve explanation quality
- and give the agent richer narrative material

The final answer should still be grounded by structured knowledge outside RAG.

This means retrieval is:
- supportive
- context-oriented
- and intentionally secondary to structured facts

---

## Retrieval Inputs

The retriever works from two main inputs:

### 1. `rag/chunks.json`
This contains all markdown chunks plus their metadata.

### 2. `knowledge/domains/network/model.yaml`
This is used to:
- detect valid entities
- detect valid scope units
- expand scope-unit focus into entities
- expand dependency-related focus
- and keep retrieval aligned with the documented environment

The retriever does not use:
- `domain.yaml`
- `index.yaml`
- `control_references.yaml`

as retrieval corpora.

---

## Retrieval Output

The retriever returns a ranked list of chunks.

Depending on the version:

### Baseline retriever
Returns:
- top retrieved chunks only

### Advanced retriever
Returns:
- top retrieved chunks
- detected intents
- computed focus set

This allows more advanced agents to reuse retrieval metadata rather than recomputing it.

---

## Question Understanding

The first step is question understanding.

The retriever performs lightweight intent detection from the user question.

Examples of supported intent families:
- transition / hardening questions
- required flow questions
- technical detail questions
- overly broad access questions
- target posture questions
- uncertainty questions
- dependency questions
- standards-aware questions
- external-guidance-style questions

The retriever is not doing final reasoning here.
It is only identifying what kinds of chunks are likely to matter.

---

## Focus Set Construction

After intent detection, the retriever builds a focus set.

This is one of the most important parts of the retrieval strategy.

The focus set is built from:

### 1. Directly mentioned entities
Examples:
- APP01
- IAM01
- DB01

### 2. Directly mentioned scope units
Examples:
- APP_ZONE
- MGMT_SEGMENT
- WAN

### 3. Scope-unit expansion
If a scope unit is mentioned, retrieval expands it into the entities currently documented inside that scope unit.

### 4. Dependency expansion
If focus entities are known, retrieval also expands to their dependency targets.

This gives the retriever a richer and more realistic idea of what the question is actually about.

---

## Why Focus Expansion Matters

A user may ask about:
- APP_ZONE
- or a least-privilege transition plan
- or a management segment concern

But the most useful chunks are often not the ones that mention only the scope unit name.
They are often the chunks describing:
- the specific entities inside it
- the required flows for those entities
- the technical matrix for those flows
- the broad access that should not remain
- and the unresolved blockers affecting that scope unit

That is why simple keyword retrieval is not enough.

---

## Chunk Metadata Used in Retrieval

Retrieval relies heavily on metadata stored during chunk building.

Important metadata includes:
- `chunk_type`
- `entities`
- `scope_units`
- `confidence_tags`
- `flow_source`
- `flow_destination`
- `flow_entities`
- `flow_scope_units`

This metadata allows retrieval to reason about:
- connectivity
- relevance to focus entities
- relevance to focus scope units
- chunk type suitability
- and uncertainty signals

---

## Scoring Strategy

Each chunk is scored using a combination of signals.

Typical signals include:

### 1. Token overlap
Simple lexical overlap between the question and the chunk text.

This is low-weight and mainly used as a tiebreaker.

### 2. Section title relevance
If question terms appear in the section title, the chunk gets a boost.

This matters because section titles often carry strong semantic meaning.

### 3. Entity connectivity
Chunks are rewarded when they touch entities in the current focus set.

This is one of the most important signals for communication-heavy retrieval.

### 4. Scope-unit relevance
Chunks are rewarded when they reference focus scope units directly.

### 5. Intent-to-type alignment
Certain chunk types are more relevant for certain question types.

Examples:
- `technical_matrix` for technical / required communication questions
- `required_flows` for operational flow questions
- `unnecessary_access` for broad-access concerns
- `target_intent` for posture questions
- `open_questions` for uncertainty questions
- `dependencies` for dependency questions

### 6. Flow-specific relevance
Flow-like chunks are rewarded more strongly when they connect focus entities.

### 7. Uncertainty relevance
Open-question chunks are rewarded when the question explicitly concerns uncertainty and the chunk contains real unresolved signals.

### 8. Filler penalties
Low-value chunk types and generic sections can be penalized for complex questions.

---

## Why Retrieval Is Not Pure Similarity Search

The retriever does not rely on text similarity alone.

This is intentional.

A pure text-based retriever tends to:
- miss critical communication chunks
- over-retrieve generic prose
- under-retrieve exact technical flows
- and fail on zone-to-entity expansion

The current design is more like:
- metadata-aware retrieval
- plus connectivity-aware ranking
- plus intent-aware chunk selection

This makes it better suited for architecture and hardening questions.

---

## Dynamic Quotas

The retriever does not treat all chunk types equally for every question.

Instead, it uses dynamic quotas.

For example:
- transition questions need more `technical_matrix` and `required_flows`
- broad-access questions need `unnecessary_access`
- uncertainty questions need `open_questions`

This prevents the top results from being dominated by only one category.

It also helps ensure that complex questions retrieve:
- exact technical material
- contextual flow material
- hardening context
- and unresolved blockers

all in the same result set.

---

## Coverage-Aware Selection

After scoring, the retriever does not simply take the top N chunks by score.

It also tries to improve coverage.

For flow-like chunks, it tracks which communication pairs are already represented.
Then it prefers chunks that add new pair coverage.

This is especially important for:
- least-privilege transition questions
- allow-list questions
- communication path questions

because a good answer often requires:
- multiple distinct flows
- not just repeated chunks about one flow

---

## Priority Order for Complex Questions

For more complex hardening-style questions, retrieval should generally prefer this pattern:

1. `technical_matrix`
2. `required_flows`
3. `unnecessary_access`
4. `target_intent`
5. `open_questions`
6. `dependencies`

This order reflects the idea that:
- exact technical communication matters most,
- then operational flow intent,
- then broad-access concerns,
- then target posture,
- then unresolved blockers,
- then supporting dependency context.

---

## Baseline vs Advanced Retriever

The project keeps two retriever versions.

### Baseline retriever
- simpler orchestration
- returns top chunks only
- intended for the simpler hybrid agent

### Advanced retriever
- same general retrieval philosophy
- richer metadata return
- exposes intents and focus
- intended for the advanced orchestration agent

The advanced retriever does not change the overall retrieval philosophy.
It makes the metadata more reusable by the calling agent.

---

## Retrieval and Uncertainty

The retriever does not resolve uncertainty.
It only helps surface the right uncertainty-related chunks.

For example:
- if a question is about unresolved policy
- or not-fully-confirmed configuration
- or blockers to hardening

the retriever should increase the visibility of `open_questions` chunks that genuinely match the focus.

This supports the agent’s later reasoning step without pretending that retrieval itself solved the issue.

---

## Retrieval and Standards

The current retriever does not retrieve the standards layer as chunks.

This is intentional.

Standards references are better handled directly as structured inputs.
They are not part of the markdown retrieval corpus.

This keeps retrieval focused on:
- contextual markdown support
while standards remain:
- explicit structured comparison inputs

---

## Retrieval Boundaries

The retriever currently operates only on:
- the `network` domain markdown corpus

It does not yet support:
- multi-domain retrieval
- cross-domain graph traversal
- generalized enterprise documentation search
- standards-library retrieval
- external web retrieval

Those are future expansion possibilities, not current behavior.

---

## Final Retrieval Summary

The retrieval strategy is:

- markdown-only
- metadata-aware
- entity-aware
- scope-unit-aware
- connectivity-aware
- intent-aware
- quota-aware
- and coverage-aware

Its purpose is to return the best supporting chunks for the agent,
not to replace structured retrieval or generate final conclusions by itself.