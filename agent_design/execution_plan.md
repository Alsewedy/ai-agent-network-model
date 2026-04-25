# Network AI Auditor Agent – Execution Plan

## Purpose
Define a practical execution plan for building the first working version of the network AI auditor agent.

This file is not the reasoning logic itself.
It is the implementation-oriented plan that turns the documented agent design into a usable system.

The goal is to stay disciplined:
- build the right things,
- in the right order,
- with the current knowledge architecture,
- and without unnecessary complexity.

The execution model is:
- knowledge-base first,
- standards-aware,
- uncertainty-aware,
- and externally augmentable only under controlled conditions.

---

## Execution Goal

Build a first working network AI auditor agent that can:

- read the documented network knowledge base,
- retrieve structured facts correctly,
- explain relationships and communication paths,
- distinguish current state from intended posture,
- identify documented overly broad access,
- use the standards layer as structured comparison input,
- acknowledge uncertainty honestly,
- and optionally use trusted external guidance in a disciplined way when the question requires it.

The first version should be useful before it is elegant.

---

## Phase 1 — Load the Knowledge Base Correctly

### Objective
Make sure the agent reads the new knowledge architecture correctly and consistently.

### Required inputs
The execution plan should assume the agent reads from:

#### Structured sources
- `knowledge/index.yaml`
- `knowledge/domains/network/domain.yaml`
- `knowledge/domains/network/model.yaml`
- `knowledge/standards/mappings/control_references.yaml`

#### Supporting markdown sources
- `knowledge/domains/network/scope/scope_units.md`
- `knowledge/domains/network/scope/services.md`
- `knowledge/domains/network/scope/dependencies.md`
- `knowledge/domains/network/communication/required_flows.md`
- `knowledge/domains/network/communication/technical_matrix.md`
- `knowledge/domains/network/evidence/evidence_notes.md`
- `knowledge/domains/network/posture/unnecessary_access.md`
- `knowledge/domains/network/posture/target_intent.md`
- `knowledge/domains/network/uncertainty/open_questions.md`

#### Optional architecture/rules sources
- `knowledge/_meta/ARCHITECTURE.md`
- `knowledge/_meta/RULES.md`

### Output of this phase
A stable loader / reader layer that can access:
- structured facts,
- markdown context,
- standards references,
- and uncertainty boundaries.

---

## Phase 2 — Build a Retrieval Strategy

### Objective
Make retrieval deliberate rather than flat.

The agent should not read every file equally for every question.

### Retrieval rules
Implement the following order:

1. classify the question
2. retrieve from `model.yaml` first when possible
3. use `domain.yaml` and `index.yaml` for metadata / scope awareness
4. use markdown files only when context or explanation is needed
5. use `control_references.yaml` only when standards comparison is relevant
6. check `open_questions.md` before strong conclusions
7. consult trusted external sources only when explicitly justified

### Output of this phase
A retrieval strategy that maps:
- fact questions → structured model first
- technical questions → technical matrix + evidence
- posture questions → unnecessary access + target intent
- audit questions → model + posture + standards + uncertainty
- external best-practice questions → internal KB first, then trusted external augmentation if needed

---

## Phase 3 — Implement Reasoning Layers

### Objective
Make the agent reason in the correct sequence.

### Required reasoning steps
The execution logic should support this flow:

1. Identify question type
2. Retrieve current documented facts
3. Retrieve required operational state where relevant
4. Retrieve intended target posture where relevant
5. Retrieve external control expectations where relevant
6. Check uncertainty before strong conclusions
7. Decide whether trusted external guidance is justified
8. Produce a grounded answer

### Key rule
The system must never collapse:
- current state,
- intended state,
- documented external expectations,
- and optional external augmentation

into one undifferentiated answer.

These are separate reasoning layers and must remain separate.

### Output of this phase
An answer generation flow that can support:
- factual explanation
- posture comparison
- standards-aware comparison
- uncertainty-aware conclusions
- disciplined external augmentation

---

## Phase 4 — Implement Answer Construction

### Objective
Make the agent’s answers useful and consistent.

### Required answer shape
For most non-trivial questions, the answer construction should support:

1. direct answer
2. grounded explanation
3. intended posture context if relevant
4. standards context if relevant
5. uncertainty / confidence context if relevant
6. external guidance context if used
7. practical implication if helpful

### Important rule
The system must avoid:
- dumping raw file content
- copying markdown blocks blindly
- giving unsupported compliance verdicts
- sounding more certain than the documented model allows
- blending internal and external sources invisibly

### Output of this phase
Consistent audit-style answers rather than inconsistent ad hoc replies.

---

## Phase 5 — Add Standards-Aware Audit Reasoning

### Objective
Use the standards layer as structured comparison input.

### Inputs
- `target_intent.md`
- `model.yaml`
- `control_references.yaml`
- `unnecessary_access.md`
- `open_questions.md`

### Required behavior
The agent should be able to answer questions like:
- What appears broader than the documented least-privilege expectations?
- What seems weak from a segmentation perspective?
- Which documented paths are most relevant to controlled egress expectations?
- What cannot be judged strongly yet because the policy is unresolved?

### Important rule
The agent must not behave as if:
- `control_references.yaml` is exhaustive,
- or as if control presence automatically means failure,
- or as if absent controls are irrelevant.

It should use this layer for guided comparison only.

### Output of this phase
A standards-aware but still honest and limited auditor agent.

---

## Phase 6 — Add Uncertainty Gate

### Objective
Prevent false certainty.

### Required uncertainty checks
Before making a strong statement, the system should check:

- whether the relevant fact is confirmed
- whether it is only owner-confirmed
- whether it relies on a standard default
- whether an open question materially affects the issue
- whether the issue is a documentation gap or a likely security concern

### Important behavior
When uncertainty changes the strength of the answer, the agent must say so explicitly.

Examples:
- cannot be judged confidently yet
- this appears concerning, but the final policy is unresolved
- the relationship is documented, but some technical details rely on accepted defaults

### Output of this phase
A more trustworthy agent that does not overstate conclusions.

---

## Phase 7 — Add Controlled External Augmentation

### Objective
Allow the agent to use trusted external guidance without becoming random or unreliable.

### When external augmentation is allowed
External guidance may be used only when:
- the user explicitly asks for broader standards or best-practice comparison,
- the internal standards layer is clearly insufficient for the question,
- or the question specifically requires outside authoritative guidance.

### Source quality rule
The system should prefer:
- official standards documentation
- official framework documentation
- official vendor hardening guidance
- authoritative regulatory guidance
- other clearly recognized primary or authoritative sources

The system should avoid:
- weak blog posts
- low-authority commentary
- unclear summaries
- random secondary claims used as if they were standards

### Required behavior
When external guidance is used, the system must:
1. reason from the internal KB first
2. clearly identify the external source as external
3. distinguish internal documented facts from outside guidance
4. avoid overclaiming from one source alone
5. remain conservative in judgment wording

### Output of this phase
An agent that can expand beyond the internal KB when necessary without becoming unreliable.

---

## Phase 8 — Test Against Real Question Types

### Objective
Validate behavior using realistic questions from the documented environment.

### Minimum test categories
- direct fact retrieval
- dependency reasoning
- required communication reasoning
- technical detail lookup
- evidence and confidence reasoning
- current vs intended posture reasoning
- overly broad access reasoning
- uncertainty-aware questions
- standards-aware audit questions
- integrated architecture review questions
- external best-practice comparison questions

### Success condition
The agent should:
- stay grounded,
- avoid inventing facts,
- separate current and intended state,
- use standards carefully,
- acknowledge uncertainty where appropriate,
- and clearly distinguish internal from external reasoning when external guidance is used

### Failure condition
The agent is not ready if it:
- invents undocumented logic
- ignores open questions
- gives binary compliance verdicts too easily
- confuses broad current access with approved final design
- or uses weak external material to produce strong conclusions

---

## Suggested Build Order

The recommended implementation order is:

### Step 1
Get knowledge loading working correctly

### Step 2
Implement question classification

### Step 3
Implement structured retrieval from `model.yaml`

### Step 4
Add markdown context retrieval

### Step 5
Add standards-aware comparison

### Step 6
Add uncertainty checks

### Step 7
Add controlled external augmentation

### Step 8
Tune answer construction

### Step 9
Run realistic test questions and refine

This order keeps the build stable and avoids premature complexity.

---

## What Not to Build Yet

To keep execution disciplined, do not build these yet unless they become necessary:

- graph database storage
- dynamic framework ingestion
- automated finding persistence
- scoring engines
- policy synthesis engines
- remediation generation pipelines
- multi-domain orchestration
- cross-domain graph reasoning
- full framework catalogs
- autonomous compliance scoring
- unrestricted external crawling

These may be useful later, but they are not required for the first good version.

---

## MVP Implementation Standard

The first working version is good enough if it can reliably do the following:

- answer network-domain questions correctly
- explain why systems communicate
- identify where access is broader than intended
- compare current state against target intent
- compare current state against documented external expectations
- state what remains unresolved
- and carefully use trusted external guidance only when justified

That is the build target.

---

## Final Execution Summary

Build the agent in this order:

1. load the new knowledge structure correctly
2. retrieve facts from structured sources first
3. use markdown as supporting context
4. compare current state to intended posture
5. compare current state to structured external expectations
6. gate strong conclusions through uncertainty checks
7. augment with trusted external guidance only when justified
8. generate grounded audit-style answers with clear internal/external separation

If those steps work well, the first version of the network AI auditor agent will already be useful.