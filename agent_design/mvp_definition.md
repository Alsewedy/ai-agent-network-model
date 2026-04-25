# Network AI Auditor Agent – MVP Definition

## Purpose
Define the minimum viable version of the network AI auditor agent.

This file exists to keep the project focused.
It defines what the first real version of the agent should do, what it should not do yet, and what counts as success.

The goal of the MVP is not to build a complete autonomous auditor.
The goal is to build a grounded, useful, reasoning-oriented network auditor agent that works well on the documented network domain.

This MVP is:
- knowledge-base first,
- standards-aware,
- uncertainty-aware,
- and externally augmentable only under controlled conditions.

---

## Core MVP Goal

The MVP should be able to:

- read the documented network knowledge base,
- answer direct questions about the documented network model,
- explain dependencies, required communication, and technical details,
- distinguish current state from intended target posture,
- identify access documented as broader than necessary,
- compare current facts against lightweight structured external expectations,
- explicitly acknowledge uncertainty where the model is unresolved,
- and, when explicitly needed, use trusted external guidance without becoming random or speculative.

This is the minimum useful version.

---

## What the MVP Must Be Able to Do

### 1. Structured Fact Retrieval
The MVP must retrieve facts correctly from:
- `knowledge/domains/network/model.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/index.yaml`

Examples:
- identify scope unit membership
- identify services per entity
- identify dependencies
- identify required flows
- identify documented technical details
- identify open questions
- identify known overly broad access

This is the baseline capability.

---

### 2. Relationship Explanation
The MVP must explain how documented systems relate to each other.

Examples:
- how APP01 relates to IAM01 and DB01
- how IAM01 depends on DC01-CYBERAUDIT
- how outbound access is structured through PROXY01
- how administrative access is currently described

This means the MVP is not just a YAML lookup tool.
It must be able to explain relationships in plain language.

---

### 3. Current vs Intended Posture Reasoning
The MVP must distinguish between:
- what is currently documented,
- what is operationally required,
- and what is intended in the final design.

Examples:
- current broad access exists, but should not remain broad
- a segment exists in the architecture, but its final policy is unresolved
- administrative access is currently broad, but intended posture is narrower

This is one of the most important parts of the MVP.

---

### 4. Overly Broad Access Reasoning
The MVP must be able to identify access that the knowledge base already documents as broader than necessary.

Examples:
- broad LAN to APP_ZONE access
- broad APP_ZONE to SERVICE_ZONE access
- broad DMZ reachability
- broad Admin laptop access

The MVP should explain:
- what is broad,
- why it matters,
- and what the documented target direction says instead.

---

### 5. Technical Detail Support
The MVP must be able to answer technical questions using the documented technical matrix.

Examples:
- what port APP01 uses for DB access
- what protocol is used for proxy paths
- what is documented for LDAP federation
- what is directly observed versus owner-confirmed or standard default

This allows the MVP to support both architecture-level and low-level reasoning.

---

### 6. Standards-Aware Comparison
The MVP must be able to use:
- `knowledge/standards/mappings/control_references.yaml`

as structured comparison guidance.

This means the MVP should be able to answer questions like:
- what looks broader than the listed least-privilege expectations?
- what seems weak from a segmentation perspective?
- what parts of the documented model are relevant to controlled egress?
- what areas appear directionally inconsistent with the documented control references?

The MVP should do this carefully.
It is not a full compliance engine.

---

### 7. Uncertainty-Aware Reasoning
The MVP must be able to say:
- what is unresolved,
- what cannot be judged confidently yet,
- and why stronger conclusions are limited.

Examples:
- MGMT_SEGMENT policy is unresolved
- EMPLOYEE_SEGMENT and GUEST_SEGMENT exist architecturally but are not yet actively modeled
- WAN future exposure is still an open question

This is required because the project explicitly avoids silent assumptions.

---

### 8. Controlled External Augmentation
The MVP may use trusted external guidance only when:
- the user explicitly asks for broader standards or best-practice comparison,
- or the question clearly requires external context beyond the lightweight internal standards layer.

When this happens, the MVP must:
- reason from the internal KB first,
- identify what is already documented internally,
- use only trusted external sources,
- clearly label what comes from outside the KB,
- and avoid treating external guidance as if it were internal fact.

This is optional augmentation, not the default operating mode.

---

## What the MVP Must NOT Do

The MVP must not:

- invent undocumented systems, flows, or policies
- assume that current access equals intended access
- assume that intended posture is already implemented
- treat missing control references as proof of irrelevance
- act like a full compliance automation platform
- produce unsupported pass/fail compliance judgments
- convert open questions into facts
- confuse documentation gaps with real security gaps
- answer outside the documented network domain as if that knowledge already exists
- browse external material casually and present it as reliable without discipline

These limits are part of a good MVP, not weaknesses.

---

## MVP Scope Boundaries

The MVP is scoped to:
- the `network` domain only
- the currently documented knowledge base
- the current layered architecture of:
  - structured facts,
  - markdown context,
  - uncertainty,
  - standards references,
  - and optional trusted external augmentation

The MVP is not yet scoped to:
- multi-domain reasoning across identity, applications, or cloud domains
- autonomous remediation
- full policy synthesis
- full framework coverage
- graph databases
- automatic control expansion
- dynamic evidence ingestion
- continuous monitoring
- unrestricted external policy crawling

Those can come later if justified.

---

## What Counts as MVP Success

The MVP is successful if it can consistently do the following:

1. answer direct factual questions correctly
2. explain dependencies and communication clearly
3. distinguish current state from target posture
4. identify documented overly broad access
5. use standards references as comparison guidance
6. acknowledge uncertainty honestly
7. produce useful audit-style reasoning without inventing conclusions
8. use trusted external guidance carefully when explicitly needed

If it can do those eight things reliably, the MVP is already valuable.

---

## What Does NOT Need to Exist Yet

The MVP does not require:

- a complete framework library
- a full control catalog
- multi-agent orchestration
- a separate standards reasoning engine
- graph-based relationship storage
- automated finding persistence
- scoring systems
- maturity dashboards
- remediation generation pipelines
- multi-domain cross-correlation
- unrestricted web-scale standards discovery

These may become useful later, but they are not part of the first useful version.

---

## Expected User Experience of the MVP

A good MVP should let the user ask questions such as:

- What does APP01 depend on?
- Which access is currently broader than intended?
- What is the target posture of ADMIN_SEGMENT?
- What technical details are documented for IAM01 to DC01-CYBERAUDIT?
- What seems directionally weak from a least-privilege perspective?
- What cannot yet be judged confidently because the model is unresolved?
- What additional trusted external guidance may be relevant here even if it is not yet documented in the KB?

And the agent should answer:
- clearly,
- correctly,
- with grounding,
- with standards context when relevant,
- with explicit uncertainty where needed,
- and with clear separation between internal and external sourcing.

---

## MVP Philosophy

The MVP should be:
- small enough to build well,
- disciplined enough to stay honest,
- and useful enough to demonstrate real audit reasoning value.

It should not try to impress by pretending to be larger than it is.

It should prove a few things well:
- that a documented network knowledge base can support grounded, standards-aware, uncertainty-aware AI audit reasoning,
- and that external augmentation can be added carefully without turning the agent into a random web searcher.

---

## Final MVP Summary

The MVP is not:
- a generic chatbot,
- a document summarizer,
- a full compliance platform,
- or an unrestricted external standards crawler.

The MVP is:
- a grounded network AI auditor,
- operating on a structured knowledge base,
- able to explain the environment,
- compare current state to intended state,
- compare current state to documented external expectations,
- speak honestly about uncertainty,
- and carefully incorporate trusted external guidance only when justified.

That is the correct MVP target.