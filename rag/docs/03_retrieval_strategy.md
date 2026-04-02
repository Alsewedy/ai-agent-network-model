# Phase 4 – Retrieval Strategy

## Purpose
This document defines how the first RAG retrieval step should work for the network agent.

The goal is to retrieve the most relevant chunks from `rag/chunks.json` for a user question, then combine them with structured YAML facts before sending the prompt to the LLM.

---

## 1. Retrieval Goal
The first retrieval layer should:
- read the chunk collection from `rag/chunks.json`
- score chunks against the user question
- return the most relevant chunks
- preserve useful metadata such as source file, section title, entities, zones, and confidence tags

---

## 2. Retrieval Style
The first implementation should use:
- simple keyword-based retrieval
- metadata-aware scoring
- no embeddings yet

This keeps the first RAG layer simple and inspectable.

---

## 3. What Should Influence Ranking
Chunk relevance should increase when the chunk matches:

- asset names mentioned in the question
- zone names mentioned in the question
- important keywords such as:
  - allow list
  - least privilege
  - required flows
  - port
  - protocol
  - unresolved
  - target intent
  - blocked
  - hardening

Chunks should also get value from:
- matching section titles
- matching chunk_type
- matching confidence tags when relevant

---

## 4. Output of Retrieval
The retriever should return:
- top relevant chunks
- chunk metadata
- chunk text

These will later be used as:
- supporting RAG context in the final prompt

---

## 5. First Scope
The first retriever does not need:
- embeddings
- vector databases
- semantic search
- re-ranking models

The first goal is only:
- correct, useful, inspectable retrieval

---

## Notes
- YAML will remain the structured source of truth.
- RAG retrieval is an additional context layer, not a replacement for YAML.
- The first retrieval implementation should prioritize clarity and debuggability.