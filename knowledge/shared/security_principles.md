# Security Principles

Environment-wide security principles that guide decisions across all domains.
These are not domain-specific rules — they are foundational principles that
every domain's posture and target intent should align with.

---

<!-- Copy this block for each principle -->

## Principle: [SHORT_TITLE]

**Statement:** [the principle in one clear sentence]

**Implication:** [what this means in practice for domain documentation]

---

<!--
  EXAMPLES (remove when filling in real data):

  ## Principle: Least Privilege by Default
  **Statement:** Every entity should have only the minimum access required for its confirmed operational purpose.
  **Implication:** Broad access documented in any domain must be flagged in posture/unnecessary_access.md with a target state that narrows it to specific, justified paths.

  ## Principle: No Implicit Trust
  **Statement:** Zone membership or network adjacency does not imply trust.
  **Implication:** Every inter-scope-unit flow must be explicitly documented and justified. "They are in the same zone" is not sufficient justification.

  ## Principle: Confirmed Before Trusted
  **Statement:** Facts used for security decisions must be confirmed, not assumed.
  **Implication:** Every technical fact must carry a confidence tag. Untagged facts are treated as open_question by the AI agent.
-->
