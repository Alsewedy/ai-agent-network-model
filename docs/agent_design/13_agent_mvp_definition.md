# Phase 2 – Agent MVP Definition

## Purpose
This document defines the first Minimum Viable Product (MVP) for the network AI agent.

The goal of this MVP is not to create a full enterprise AI security system.
The goal is to build a first practical, trustworthy, and usable AI layer that can read the documented network model and answer useful network-focused questions.

This MVP should prove that the network knowledge base can be consumed by an AI agent in a reliable way.

---

## 1. MVP Scope

The first MVP is limited to the network domain only.

It should work with the current documented network knowledge base, including:
- zones
- assets
- services
- dependencies
- required flows
- port and protocol matrix
- blocked or unnecessary flows
- open questions
- target security intent

The MVP should not yet attempt to handle:
- full Active Directory modeling
- deep IAM design beyond what is already documented
- GPO structure
- full application source code reasoning
- full firewall syntax generation
- automatic remediation

---

## 2. MVP Goal

The first MVP should be able to answer useful questions about the network model in a grounded and trustworthy way.

The goal is to prove that the AI agent can:
- retrieve facts,
- reason about dependencies,
- compare current and target state,
- identify broad access that should not remain,
- and handle uncertainty honestly.

---

## 3. What the MVP Must Be Able to Do

### Capability 1 – Asset and Zone Lookup
The agent should be able to answer questions such as:
- What systems are in APP_ZONE?
- Where is IAM01 located?
- What is in LAN / DATA?

### Capability 2 – Service Lookup
The agent should be able to answer questions such as:
- What services are hosted on DB01?
- Does IAM01 host the Internal API?
- What does APP01 provide?

### Capability 3 – Dependency Lookup
The agent should be able to answer questions such as:
- What does APP01 depend on?
- Which systems rely on Vault?
- What depends on DB01?

### Capability 4 – Required Flow Lookup
The agent should be able to answer questions such as:
- What communication must remain open for APP02?
- What does IAM01 need to reach?
- What does APP01 need for normal operation?

### Capability 5 – Port and Protocol Lookup
The agent should be able to answer questions such as:
- What port does APP01 use to reach the Internal API?
- What protocol is used between APP02 and DB01?
- What port does the proxy use?

### Capability 6 – Current vs Target Comparison
The agent should be able to answer questions such as:
- Is broad APP_ZONE access aligned with the target security intent?
- What currently allowed paths should not remain in the final design?

### Capability 7 – Uncertainty-Aware Answering
The agent should be able to answer questions such as:
- What parts of the model are still unresolved?
- Which values are standard defaults declared by the owner?
- Which parts are fully confirmed?

### Capability 8 – Basic Recommendation Output
The agent should be able to give simple model-based recommendations such as:
- APP_ZONE access should be narrowed to confirmed dependencies only
- DMZ broad trust should not remain
- Admin laptop access should be reduced from any-to-any to approved management-only paths

---

## 4. What the MVP Does Not Need to Do Yet

The first MVP does not need to:
- generate final firewall rules automatically
- build a full graph engine
- perform packet analysis directly
- update the model automatically
- parse raw configuration files dynamically
- reason over undocumented AD internals
- answer questions outside the network knowledge base

If the user asks beyond documented scope, the agent should say that the current MVP does not yet support that level of answer.

---

## 5. Data Sources for the MVP

The MVP should use a hybrid model:

### Primary structured source
- `knowledge/network_domain/08_structured_network_model.yaml`

### Supporting context sources
- `knowledge/network_domain/01_zones_and_assets.md`
- `knowledge/network_domain/02_services.md`
- `knowledge/network_domain/03_dependencies.md`
- `knowledge/network_domain/04_required_flows.md`
- `knowledge/network_domain/04a_port_and_protocol_matrix.md`
- `knowledge/network_domain/04b_evidence_notes.md`
- `knowledge/network_domain/05_blocked_or_unnecessary_flows.md`
- `knowledge/network_domain/06_open_questions_and_assumptions.md`
- `knowledge/network_domain/07_target_security_intent.md`
- `docs/agent_design/09_agent_input_design.md`
- `docs/agent_design/10_agent_test_questions.md`
- `docs/agent_design/11_agent_answer_style.md`
- `docs/agent_design/12_agent_logic_v1.md`

---

## 6. Expected Answer Quality

The MVP should produce answers that are:

- grounded in the model
- concise but useful
- explicit about certainty
- aware of current vs target distinction
- practical for architecture review and hardening decisions

The MVP should not sound like:
- a generic chatbot
- an overconfident assistant
- or a system that treats assumptions as facts

---

## 7. Success Criteria

The MVP should be considered successful if it can answer the first core test questions correctly and reliably.

Minimum success means:
- correct fact retrieval
- correct dependency retrieval
- correct flow retrieval
- correct port/protocol retrieval where documented
- correct distinction between broad current access and target intended posture
- honest handling of unresolved items

---

## 8. Failure Conditions

The MVP should be considered weak or unreliable if it:
- invents missing technical details
- confuses current state with target state
- ignores open questions
- gives generic best-practice answers not grounded in the model
- fails simple dependency or port lookup questions

---

## 9. Practical Definition of MVP Completion

The MVP can be considered complete when:

1. the network knowledge base is readable by the agent,
2. the agent can answer the first official test questions,
3. the answers follow the defined answer style,
4. the logic remains grounded in the documented model,
5. and the agent is useful for basic network hardening and architecture review questions.

---

## 10. Next Step After MVP

Once the MVP is stable, the next stage can include:
- expanding to Active Directory as a new knowledge module
- improving hardening recommendations
- comparing multiple domains together
- adding richer structured querying
- or later introducing graph-style modeling if needed

---

## Notes
- The purpose of the MVP is proof of usefulness, not maximum complexity.
- A smaller grounded agent is better than a larger unreliable one.
- The first success target is a trustworthy network-aware assistant.