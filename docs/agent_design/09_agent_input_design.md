# Phase 2 – Agent Input Design

## Purpose
This document defines how the first version of the AI agent will consume the current network knowledge base.

It clarifies:
- which files the agent should read,
- which file acts as the main structured source of truth,
- what role the markdown files still play,
- and what the first practical use cases of the agent will be.

---

## 1. Primary Source of Truth
The main structured source of truth for the first version of the AI agent is:

- `knowledge/network_domain/08_structured_network_model.yaml`

This file should be treated as the primary machine-readable network model.

---

## 2. Supporting Context Files
The markdown files remain important as supporting context and explanation layers.

They provide:
- reasoning,
- architectural explanation,
- current vs target distinctions,
- open questions,
- and security intent.

The supporting files are:

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

## 3. Agent Reading Strategy
The first version of the AI agent should use a hybrid reading model:

- YAML first for structured facts
- Markdown second for explanation and deeper reasoning context

This means:
- if the answer needs a direct fact, the agent should check YAML first
- if the answer needs interpretation, uncertainty handling, or architectural explanation, the agent should also use the markdown files

---

## 4. First Agent Scope
The first version of the AI agent is limited to the network domain only.

It should not yet attempt to answer questions about:
- full Active Directory design details
- GPOs
- IAM policy internals beyond what is already documented
- application source code beyond what has already been abstracted into the network model

---

## 5. First Practical Use Cases
The first version of the agent should support these use cases:

### Use Case 1 – Dependency Lookup
Example:
- What does APP01 depend on?
- Which systems rely on Vault?

### Use Case 2 – Required Flow Lookup
Example:
- What communication must remain open for APP02?
- What does IAM01 need to reach?

### Use Case 3 – Port and Protocol Lookup
Example:
- What port does APP01 use to reach the Internal API?
- What protocol does APP02 use to reach DB01?

### Use Case 4 – Current vs Target Comparison
Example:
- Is broad APP_ZONE access aligned with the target security intent?
- Which currently allowed paths should not remain in the final design?

### Use Case 5 – Uncertainty-Aware Answering
Example:
- What parts of the network model are still unresolved?
- Which values are confirmed vs owner-declared defaults?

---

## 6. Agent Output Style
The first version of the AI agent should aim to produce answers that are:

- clear
- grounded in the documented model
- explicit about certainty level
- and useful for hardening or architectural review

The agent should avoid treating:
- current broad firewall access
as
- final intended security design

---

## 7. Current Goal of Phase 2
The goal of this phase is not to build a perfect AI system immediately.

The goal is to prove that the documented network knowledge base can be used reliably by an AI agent for:
- retrieval,
- reasoning,
- comparison,
- and useful output generation.

---

## Notes
- The current focus is the network domain only.
- Expansion to Active Directory, IAM depth, or other domains will happen later as separate knowledge modules.
- The first AI layer should remain simple, reliable, and grounded.