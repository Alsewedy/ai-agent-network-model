# Chunking Strategy

## Purpose
Define how markdown knowledge is converted into retrievable chunks.

The chunking strategy is designed for the current domain-based knowledge architecture.
It aims to preserve:
- semantic meaning
- section boundaries
- flow directionality
- entity awareness
- scope-unit awareness
- confidence hints
- and retrieval usefulness

The goal is not to maximize chunk count.
The goal is to produce chunks that are useful for agent reasoning.

---

## Source Material

Chunks are built only from markdown files inside the current network domain.

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

Each of these files is treated as a markdown source, not as structured YAML.

---

## Files Excluded from Chunking

The chunk builder does not chunk:
- `knowledge/index.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/domains/network/model.yaml`
- `knowledge/standards/mappings/control_references.yaml`

These remain outside chunking because they are better handled through direct structured loading.

---

## Basic Chunking Method

The chunk builder follows this process:

1. read each markdown source file
2. split the file into sections using markdown headings
3. treat each section as a semantic unit
4. split very large sections into smaller sub-chunks when necessary
5. attach metadata to every chunk
6. save all chunks to `rag/chunks.json`

The result is a chunk set that is:
- heading-aware
- semantically grouped
- and enriched with retrieval metadata

---

## Section-Based Chunking

Markdown headings are treated as the first semantic boundary.

Example:
- a section under `## Flow: APP01 -> DB01`
should remain intact as long as it is not excessively large.

This preserves:
- section intent
- flow identity
- local context
- and better retrieval relevance

It also makes debugging easier because retrieved chunks still map clearly to meaningful section titles.

---

## Large Section Splitting

If a section becomes too large, it is split into smaller chunks.

The current strategy:
- keeps small and medium sections intact
- splits only larger sections
- tries to split along paragraph/block boundaries
- appends `(Part N)` to the derived chunk title when needed

This avoids:
- overly large prompt payloads
- weak retrieval precision
- and chunks that mix too many unrelated ideas

---

## Chunk Types

Each chunk is assigned a chunk type based on its source file.

Current chunk types:
- `scope_units`
- `services`
- `dependencies`
- `required_flows`
- `technical_matrix`
- `evidence_notes`
- `unnecessary_access`
- `target_intent`
- `open_questions`

Chunk type is important because retrieval logic uses it to:
- reward relevant chunk categories
- apply quotas
- reduce filler
- and support intent-aware selection

---

## Metadata Stored Per Chunk

Each chunk includes at least the following metadata:

- `chunk_id`
- `source_file`
- `section_title`
- `chunk_type`
- `entities`
- `scope_units`
- `confidence_tags`
- `flow_source`
- `flow_destination`
- `flow_entities`
- `flow_scope_units`
- `text`

This metadata allows retrieval to go beyond raw keyword overlap.

---

## Entity Extraction

Chunking includes entity-aware extraction.

Entities are detected using the current `model.yaml` as the reference source.

This means chunk metadata is aligned with the current documented environment rather than relying only on fixed hardcoded names.

Entity metadata is used to:
- help identify which chunks relate to which systems
- support focus expansion
- support dependency-aware retrieval
- and improve flow coverage logic

---

## Scope-Unit Extraction

Chunking also extracts scope-unit references.

This is important because the new knowledge architecture is built around scope units rather than the old flat zone model.

Scope-unit metadata helps retrieval answer questions such as:
- what matters for APP_ZONE?
- what is relevant to MGMT_SEGMENT?
- which chunks support WAN-related reasoning?

---

## Confidence Tag Extraction

Chunking extracts confidence hints from text.

Examples of confidence-related signals:
- confirmed
- owner_confirmed
- standard_default
- open_question

These are not final verdicts.
They are retrieval hints and reasoning hints.

They help the agent understand whether a chunk is describing:
- a confirmed fact
- an owner-declared item
- a standard default
- or unresolved uncertainty

---

## Flow Metadata Extraction

For communication-related files, the chunker attempts to preserve flow directionality.

This is especially important for:
- `required_flows`
- `technical_matrix`
- `unnecessary_access`

When section titles follow a directional pattern such as:
- `Flow: APP01 -> DB01`

the chunker extracts:
- `flow_source`
- `flow_destination`
- `flow_entities`
- `flow_scope_units`

This is critical because retrieval later uses these fields for:
- connectivity scoring
- pair coverage
- and flow-aware ranking

---

## Why Flow Metadata Matters

A plain text chunk is often not enough for network reasoning.

For example, the question:
- “What must remain open for APP01?”
is much easier to answer when the retriever knows:
- which chunks are actual communication paths
- which entities participate in those paths
- and which pairs are already covered in the result set

That is why flow metadata is preserved at chunk-build time instead of being guessed later.

---

## Why Chunking Uses Markdown Only

Chunking intentionally uses markdown only.

This keeps a clean separation:

### Structured inputs
Used directly by agents:
- exact facts
- exact fields
- exact relationships

### Chunked inputs
Used by RAG:
- explanation
- narrative support
- section-level context
- wording and nuance

This separation is one of the core architectural decisions in the project.

---

## Chunking Philosophy

The chunking strategy prefers:
- semantic chunks over arbitrary windows
- section meaning over token-count obsession
- retrieval usefulness over chunk volume
- metadata richness over bare text fragments

The system is designed for reasoning quality, not just search.

---

## Output File

All built chunks are written to:

- `rag/chunks.json`

This file is the retrieval corpus used by:
- `retrieve_chunks.py`
- `retrieve_chunks_v2.py`

If the chunking logic changes, or if the markdown knowledge changes, this file should be rebuilt.

---

## When Rebuild Is Required

Rebuild `chunks.json` when:
- `build_chunks.py` changes
- markdown source files inside `knowledge/domains/network/...` change
- chunk metadata rules change
- chunk type mapping changes

Rebuild is not required when only:
- the web UI changes
- API routes change
- agent prompt wording changes
- structured YAML changes without changing chunked markdown sources

---

## Final Strategy Summary

The chunking strategy is:

- markdown-only
- heading-aware
- section-based
- metadata-rich
- flow-aware
- entity-aware
- scope-unit-aware
- and aligned with the new domain-based knowledge architecture

Its purpose is to make RAG useful for explanation and reasoning without replacing structured knowledge.