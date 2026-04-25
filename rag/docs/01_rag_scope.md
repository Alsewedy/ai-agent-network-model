# RAG Scope

## Purpose
Define the role of RAG in the current knowledge architecture.

RAG is used to retrieve **supporting markdown context** for the agent.
It is not the primary source of truth for the environment.

The primary source of truth remains the structured knowledge in:
- `knowledge/index.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/domains/network/model.yaml`
- `knowledge/standards/mappings/control_references.yaml`

RAG exists to improve explanation, nuance, traceability, and contextual recall from markdown documentation.

---

## Core Principle

The knowledge architecture is intentionally split into two layers:

### 1. Structured Knowledge Layer
This layer is used for:
- direct fact lookup
- entity placement
- dependency lookup
- required communication lookup
- technical matrix lookup
- unnecessary access lookup
- target intent lookup
- open question lookup
- standards reference lookup

This layer is authoritative.

### 2. Markdown Retrieval Layer
This layer is used for:
- human-readable explanation
- contextual detail
- narrative clarification
- section-level supporting evidence
- richer wording around already documented facts

This layer is supportive, not authoritative.

---

## What RAG Should Include

RAG should include markdown files from the documented network domain only.

Current source set:
- `knowledge/domains/network/scope/scope_units.md`
- `knowledge/domains/network/scope/services.md`
- `knowledge/domains/network/scope/dependencies.md`
- `knowledge/domains/network/communication/required_flows.md`
- `knowledge/domains/network/communication/technical_matrix.md`
- `knowledge/domains/network/evidence/evidence_notes.md`
- `knowledge/domains/network/posture/unnecessary_access.md`
- `knowledge/domains/network/posture/target_intent.md`
- `knowledge/domains/network/uncertainty/open_questions.md`

These files are suitable for chunking because they contain:
- headings
- explanations
- flow descriptions
- rationale
- uncertainty wording
- supporting narrative

---

## What RAG Should NOT Include

RAG should not include the following structured files:

- `knowledge/index.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/domains/network/model.yaml`
- `knowledge/standards/mappings/control_references.yaml`

These files should remain outside RAG because they are:
- already structured
- easy to query directly
- better used through structured retrieval
- not improved by being turned into free-text chunks

---

## Why Structured Files Stay Outside RAG

The project intentionally avoids flattening everything into one retrieval system.

If structured YAML is pushed into RAG:
- direct fact lookup becomes less reliable
- ambiguity increases
- exact fields become harder to control
- fact vs context separation becomes weaker

Keeping structured data outside RAG preserves:
- precision
- controllability
- architectural clarity
- cleaner reasoning

---

## Role of RAG in Agent Reasoning

RAG should be used after structured retrieval, not before it.

The expected order is:

1. read structured facts
2. identify relevant markdown context
3. retrieve supporting chunks
4. use chunks to enrich explanation
5. keep structured facts as the final authority

This means:
- RAG can support the answer,
- but RAG should not override structured knowledge.

---

## RAG and Audit Reasoning

RAG is especially useful for questions that need:
- explanation of why a flow exists
- extra context around broad access
- narrative detail around target posture
- open question wording
- evidence-style reasoning support

Examples:
- Why does this access appear broader than intended?
- What does the posture narrative say about this segment?
- What uncertainty is documented here?
- What wording supports this concern?

These are exactly the kinds of questions where chunk retrieval adds value.

---

## RAG and Standards

The standards layer is not currently part of RAG.

`control_references.yaml` is intentionally handled as structured comparison input rather than free-text retrieval material.

This keeps standards usage:
- explicit
- structured
- limited
- and easier to reason about

RAG may later be extended with additional standards-related markdown only if a separate architecture decision is made.
That is not the current design.

---

## RAG Scope Boundary

The current RAG scope is limited to the `network` domain only.

It does not yet cover:
- identity domain knowledge
- application domain knowledge
- cloud domain knowledge
- multi-domain cross-retrieval
- generalized enterprise policy libraries

This is intentional.
The current goal is to make one domain work well before expanding.

---

## Final Scope Summary

RAG is used to retrieve markdown-based supporting context for the documented network domain.

It is not:
- the source of truth,
- a replacement for structured YAML,
- or a general-purpose search layer over the whole project.

It is:
- a supporting retrieval layer,
- focused on markdown context,
- designed to strengthen explanation and reasoning around structured facts.