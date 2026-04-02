# Phase 4 – Chunking Strategy

## Purpose
This document defines how the first RAG layer should chunk the network knowledge files.

The goal is to preserve meaning, structure, and retrievability.

The chunking strategy should support:
- environment-aware retrieval,
- zone-level and asset-level questions,
- current vs target comparisons,
- and hardening-oriented reasoning.

---

## 1. Chunking Principle

The first RAG implementation should use:

- **section-based chunking**
- not arbitrary fixed-size chunking

This means each chunk should correspond to:
- a meaningful heading,
- subsection,
- or logically complete block of knowledge

The goal is to keep each chunk semantically coherent.

---

## 2. Why Section-Based Chunking

The knowledge files are already structured using headings and subheadings.

This makes section-based chunking a better fit than naive token-based splitting because it preserves:
- architectural meaning
- asset/service relationships
- flow definitions
- and current vs target distinctions

This is especially important for complex questions such as:
- least-privilege transition plans
- broad trust removal
- owner-declared vs confirmed distinctions
- and unresolved blockers

---

## 3. Files to Chunk

The following files should be chunked for the first RAG layer:

- `knowledge/network_domain/01_zones_and_assets.md`
- `knowledge/network_domain/02_services.md`
- `knowledge/network_domain/03_dependencies.md`
- `knowledge/network_domain/04_required_flows.md`
- `knowledge/network_domain/04a_port_and_protocol_matrix.md`
- `knowledge/network_domain/04b_evidence_notes.md`
- `knowledge/network_domain/05_blocked_or_unnecessary_flows.md`
- `knowledge/network_domain/06_open_questions_and_assumptions.md`
- `knowledge/network_domain/07_target_security_intent.md`

---

## 4. Chunk Unit

Each chunk should ideally represent one of the following:

- one zone section
- one asset section
- one flow section
- one port/protocol section
- one blocked-flow section
- one open-question section
- one target-intent section
- or one compact explanatory block if a section is too large

---

## 5. Chunk Size Guidance

Chunks should be:
- large enough to preserve meaning
- small enough to remain retrieval-friendly

The first implementation should prefer:
- one heading/subheading block per chunk
- with optional splitting only if a section becomes too long

A rough target is:
- approximately 150 to 600 words per chunk
- but semantic coherence is more important than strict size

---

## 6. Metadata for Each Chunk

Each chunk should store metadata to improve retrieval and later prompt assembly.

Recommended metadata:

- `chunk_id`
- `source_file`
- `section_title`
- `chunk_type`
- `entities`
- `zones`
- `assets`
- `confidence_tags`
- `text`

---

## 7. Metadata Meaning

### chunk_id
A unique identifier for the chunk

### source_file
Which markdown file the chunk came from

### section_title
The heading or subheading title associated with the chunk

### chunk_type
A category such as:
- zones
- assets
- services
- dependencies
- flows
- port_matrix
- evidence
- blocked_flows
- open_questions
- target_intent

### entities
Named assets or systems mentioned in the chunk, such as:
- APP01
- APP02
- IAM01
- DB01
- DC01-CYBERAUDIT
- PROXY01

### zones
Zone names mentioned in the chunk, such as:
- APP_ZONE
- LAN / DATA
- SERVICE_ZONE
- DMZ_ZONE

### confidence_tags
Useful labels when present, such as:
- confirmed
- owner_confirmed
- standard_default_declared_by_owner
- open_question

### text
The actual chunk content

---

## 8. Entity Extraction Goal

The chunking stage should try to extract lightweight entity metadata.

This does not need to be perfect.
It only needs to help retrieval become more relevant for questions like:
- What must remain open for APP02?
- What broad trust should be removed from APP_ZONE?
- What depends on DB01?
- What is still unresolved about LAN / DATA hardening?

---

## 9. Special Handling

### Port and Protocol Matrix
For `knowledge/network_domain/04a_port_and_protocol_matrix.md`, each flow block should ideally become its own chunk.

### Required Flows
For `knowledge/network_domain/04_required_flows.md`, each flow block should ideally become its own chunk.

### Blocked or Unnecessary Flows
For `knowledge/network_domain/05_blocked_or_unnecessary_flows.md`, each blocked-flow statement or grouped section can become a chunk.

### Open Questions
For `knowledge/network_domain/06_open_questions_and_assumptions.md`, each question or grouped question section can become a chunk.

### Target Security Intent
For `knowledge/network_domain/07_target_security_intent.md`, each major intent subsection can become its own chunk.

---

## 10. Output of Chunking Phase

The output of the chunking phase should be a structured collection of chunks, for example in JSON format.

Each chunk should include:
- metadata
- and text

This chunk collection will later be used for:
- retrieval
- prompt-building
- and Hybrid YAML + RAG answering

---

## Notes
- The first chunking implementation should prioritize clarity over cleverness.
- Simple, stable, and inspectable chunking is better than highly complex chunking.
- Retrieval quality will depend heavily on chunk quality, so semantic structure should be preserved as much as possible.