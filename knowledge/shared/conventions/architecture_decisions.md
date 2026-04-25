# Architecture Decisions

Environment-wide design decisions that affect multiple domains.
Document each decision once here so all domains share the same understanding.

---

<!-- Copy this block for each decision -->

## Decision: [SHORT_TITLE]

**Date:** [when decided]
**Status:** [active / superseded / under_review]
**Scope:** [which domains or components are affected]

**Context:** [what situation led to this decision]

**Decision:** [what was decided]

**Reasoning:** [why this option was chosen over alternatives]

**Consequences:** [what this means for the affected domains]

---

<!--
  EXAMPLE (remove when filling in real data):

  ## Decision: Centralized Outbound Proxy

  **Date:** 2024
  **Status:** active
  **Scope:** All domains — network, identity, application

  **Context:** Internal systems need Internet access for updates, package downloads, and external API calls.

  **Decision:** All outbound Internet access is routed through PROXY01 in the DMZ.

  **Reasoning:** Centralizing egress provides a single enforcement point for logging, filtering, and policy control. Direct Internet access from internal zones increases attack surface.

  **Consequences:** Every domain that documents outbound communication must reference PROXY01 as the egress path. No direct Internet access from internal zones.
-->
