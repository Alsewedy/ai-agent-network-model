# Knowledge Base

## What This Is

A structured, AI-readable knowledge base designed to support an AI auditor agent.
The KB provides neutral environment facts, intended security posture, and external
control expectations. The AI auditor agent compares these inputs and generates
its own findings, gap analysis, and risk observations.

**The KB is a source of truth. The agent is the reasoning engine.**

## Structure

```
knowledge/
├── index.yaml                         ← KB overview (domains, dates, status)
│
├── _meta/                             ← Architecture rules (read-only reference)
│   ├── ARCHITECTURE.md                ← Knowledge categories and design principles
│   ├── CONFIDENCE_MODEL.md            ← Confidence levels for all facts
│   ├── RULES.md                       ← Rules every file must follow
│   └── DOMAIN_CHECKLIST.md            ← Step-by-step guide for adding a domain
│
├── shared/                            ← Cross-domain knowledge
│   ├── conventions/                   ← Naming, glossary, decisions
│   │   ├── naming_conventions.md
│   │   ├── glossary.md
│   │   └── architecture_decisions.md
│   ├── relationships/                 ← Cross-domain connections
│   │   ├── shared_entities.md
│   │   ├── cross_domain_flows.md
│   │   └── global_open_questions.md
│   └── security_principles.md         ← Environment-wide security principles
│
├── standards/                         ← External control expectations
│   └── mappings/
│       └── control_references.yaml    ← Lightweight control reference layer
│
├── domains/
│   ├── _template/                     ← Empty template (copy to start a domain)
│   │   ├── domain.yaml                ← Domain metadata
│   │   ├── scope/                     ← What exists (descriptive)
│   │   ├── communication/             ← What communicates (normative) [optional]
│   │   ├── posture/                   ← Current vs target (differential)
│   │   ├── evidence/                  ← How facts were confirmed [optional]
│   │   ├── uncertainty/               ← What is unresolved
│   │   └── model.yaml                 ← Machine-readable consolidation
│   │
│   └── .../                           ← Completed domains
```

## Key Separation

```
┌─────────────────────────────────────┐
│         KNOWLEDGE BASE              │
│                                     │
│  Environment facts (scope/)         │
│  Intended posture (posture/)        │
│  External expectations (standards/) │
│                                     │
│  → No verdicts                      │
│  → No findings                      │
│  → No pass/fail                     │
│  → No compliance conclusions        │
└──────────────┬──────────────────────┘
               │ input
               ▼
┌─────────────────────────────────────┐
│         AI AUDITOR AGENT            │
│                                     │
│  Compares facts vs expectations     │
│  Generates findings                 │
│  Identifies gaps                    │
│  Produces risk observations         │
│                                     │
│  → This is where verdicts live      │
└─────────────────────────────────────┘
```

## Design Principles

1. **Knowledge by type, not by file number.**
   Categories (scope, communication, posture, evidence, uncertainty)
   replace rigid numbered files.

2. **Domains are independent modules.**
   Adding a domain never changes existing domains.

3. **Shared knowledge is layered.**
   Conventions, relationships, and security principles are managed centrally.

4. **Not all categories are mandatory.**
   `communication/` and `evidence/` are optional.

5. **YAML captures structured facts; Markdown captures context.**
   Only queryable facts go in YAML.

6. **The KB never contains audit verdicts.**
   The AI auditor generates conclusions. The KB provides inputs.

7. **Standards are reference, not judgment.**
   Control references describe expectations, never results.
