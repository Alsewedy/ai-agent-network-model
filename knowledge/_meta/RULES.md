# Knowledge Rules

These rules apply to every file in every domain.

## 1. No Silent Assumptions
Unconfirmed facts go in `uncertainty/`. Never state assumptions as facts elsewhere.

## 2. Current State ≠ Final Design
Currently allowed ≠ permanently intended. Always distinguish:
observed → required → target.

## 3. YAML for Lookups, Markdown for Context
YAML holds structured facts the agent queries directly.
Markdown holds narrative, reasoning, and explanation for RAG retrieval.
Not every markdown section needs a YAML entry. Only structured, queryable
facts belong in YAML. Explanatory and analytical content stays markdown-only.

## 4. YAML Is Primary, Not Exhaustive
Structured YAML is the primary organized representation of domain knowledge,
but it is not assumed to contain every useful or important detail.

Important supporting knowledge may also exist in markdown, including:
- evidence
- uncertainty
- intended direction
- implementation context
- traceability
- reasoning support

Absence from YAML must not be treated as proof that a fact, dependency,
restriction, uncertainty, or design consideration does not exist elsewhere
in the documented local knowledge base.

## 5. Local Knowledge Base First, External Guidance Second
The AI agent must reason from the full documented local knowledge base first.

The local knowledge base includes:
- structured YAML
- domain markdown
- documented internal control references

External guidance may be used only when:
- the user explicitly asks for it
- a relevant standard or control is not documented locally
- the local knowledge base does not fully resolve the evaluative question

Absence from YAML alone is never sufficient reason to use external guidance.

## 6. Naming Must Be Exact
Entity names, scope unit names, and service names must be identical
across all files within a domain and in shared/ references.
See `shared/conventions/naming_conventions.md` for the standard.

## 7. Cross-Domain Facts Use Shared Files
Entities, flows, or questions spanning domains belong in `shared/`.
Domain files reference by name only, never duplicate definitions.

## 8. Confidence Is Mandatory for Technical Facts
Every port, protocol, endpoint, or dependency status must carry
a confidence level from `_meta/CONFIDENCE_MODEL.md`.

## 9. Domains Are Self-Contained
Adding a domain must never require modifying another domain's files.
Cross-domain connections are managed through `shared/relationships/`.

## 10. Optional Categories Are Truly Optional
If `communication/` or `evidence/` does not apply to a domain, do not
create empty placeholder files. Skip the folder entirely.

## 11. Evaluative Claims Must Be Grounded in Environment Evidence
When the AI agent evaluates a condition against an internal or external
expectation, the conclusion must be tied to documented environment evidence.

The agent must not produce evaluative claims based only on abstract standards
language. It should connect the claim to documented local facts, flows,
technical details, evidence notes, target intent, or uncertainty records.

## 12. Risk Owner Must Be Explicit or Fallback to Domain Owner
If a narrower owner is documented for a specific entity, service, scope unit,
or relationship, the AI agent should use that owner.

If no narrower owner is documented, the agent should fall back to the
domain owner defined in `domain.yaml`.

This supports practical remediation ownership without inventing unsupported
organizational structure.

## 13. No Verdict Language in the Knowledge Base

**No file in the knowledge base may contain audit conclusions, compliance
judgments, or verdict language about the current environment.**

This includes, but is not limited to:
- compliant / non-compliant
- pass / fail
- finding / gap / deficiency
- risk level (high / medium / low)
- any equivalent direct judgment about the environment's current state

This rule applies to:
- `standards/` — control references describe **expectations**, not results
- `posture/target_intent` — describes **intended direction**, not achieved status
- `posture/unnecessary_access` — describes **what should change**, not audit findings

**Why this rule exists:**
The knowledge base is a neutral source of truth. The AI auditor agent
is the reasoning engine that compares facts against expectations and
produces findings. If the KB already contains verdicts, the agent
becomes a reader instead of a reasoner. The separation between
documenting expectations and generating conclusions must be preserved.