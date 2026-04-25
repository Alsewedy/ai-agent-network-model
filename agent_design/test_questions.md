# Network AI Auditor Agent – Test Questions

## Purpose
Define the main question types the network AI auditor agent should be tested against.

These questions are not random examples.
They are designed to verify that the agent can:
- retrieve structured facts correctly,
- explain relationships clearly,
- distinguish current state from intended posture,
- reason about overly broad access,
- use standards references appropriately,
- handle uncertainty honestly,
- and use trusted external guidance carefully when needed.

The goal is not only to test whether the agent can answer.
The goal is to test whether it can answer in the right way.

---

## Test Group 1 — Direct Fact Retrieval

These questions verify that the agent can read structured knowledge correctly.

### Questions
- What scope unit contains IAM01?
- What systems are currently documented in LAN?
- What services are provided by DB01?
- Which systems are currently documented in APP_ZONE?
- Does GUEST_SEGMENT currently contain any active documented entities?
- What is the documented purpose of PROXY01?
- What are the currently documented entities in MGMT_SEGMENT?

### What a good answer should demonstrate
- correct use of `model.yaml`
- no invented entities
- clear distinction between documented and undocumented
- concise fact-based answers

---

## Test Group 2 — Dependency Reasoning

These questions verify that the agent can explain system relationships.

### Questions
- What does APP01 depend on?
- Why does IAM01 depend on DC01-CYBERAUDIT?
- Does APP02 depend on PROXY01?
- Which systems currently depend on DC01-CYBERAUDIT?
- Which systems currently rely on Vault on DB01?
- What role does PROXY01 play in the dependency model?
- How is DB01 positioned in relation to the application systems?

### What a good answer should demonstrate
- correct use of dependencies
- correct explanation of service-on-host relationships
- no invented dependency chains
- ability to explain why the dependency matters

---

## Test Group 3 — Required Communication Flows

These questions verify that the agent can reason about operational communication.

### Questions
- What communication is required for APP01 to function?
- Does IAM01 require communication with DB01?
- What outbound communication is documented for DB01?
- Does APP02 require communication with IAM01?
- Is DC01-CYBERAUDIT documented as using PROXY01?
- Which systems currently use PROXY01 for outbound Internet access?
- What communication is documented between APP01 and IAM01?

### What a good answer should demonstrate
- correct use of required flows
- clear distinction between required flow and broad access
- ability to explain required purpose without over-expanding
- correct relationship between dependencies and communication

---

## Test Group 4 — Technical Detail Retrieval

These questions verify that the agent can retrieve exact technical details.

### Questions
- What port does APP01 use to communicate with DB01?
- What protocol is documented for IAM01 to DC01-CYBERAUDIT LDAP federation?
- What port is used for Vault access from APP02?
- What does the technical matrix document for APP01 to the Internal API on IAM01?
- What port does PROXY01 use for outbound proxy access?
- What technical details are documented for DNS communication to DC01-CYBERAUDIT?
- Is the local APP01 reverse proxy flow documented in the technical matrix?

### What a good answer should demonstrate
- correct use of `technical_matrix.md`
- correct confidence interpretation
- no mixing of flow purpose with technical details
- no invented ports, protocols, or directions

---

## Test Group 5 — Evidence and Confidence Reasoning

These questions verify that the agent can connect facts to evidence and confidence levels.

### Questions
- How do we know APP01 talks to the Internal API on IAM01?
- What evidence supports the current documented Vault address?
- Why is LDAP federation marked differently from directly observed DNS?
- Which technical entries are based on standard defaults rather than direct observation?
- What is owner-confirmed versus directly observed in the current model?
- What supports the statement that the Admin laptop currently has broad access?
- What supports the statement that APP01 uses Nginx on HTTPS?

### What a good answer should demonstrate
- correct use of `evidence_notes.md`
- correct distinction between:
  - confirmed
  - owner_confirmed
  - standard_default
- ability to explain traceability clearly

---

## Test Group 6 — Current vs Intended Posture

These questions verify that the agent can distinguish current state from intended state.

### Questions
- What is the intended posture of APP_ZONE?
- What is the intended posture of WAN?
- What is the current context of MGMT_SEGMENT?
- What is the intended target for administrative access?
- What is the intended posture of GUEST_SEGMENT?
- How does the current state of APP_ZONE differ from its intended posture?
- What is the difference between the current state of ADMIN_SEGMENT and its target posture?

### What a good answer should demonstrate
- correct use of `target_intent.md`
- explicit distinction between current context and target posture
- no confusion between implemented state and intended direction
- clear use of scope-unit-specific intent

---

## Test Group 7 — Overly Broad Access and Hardening Questions

These questions verify that the agent can identify access documented as broader than necessary.

### Questions
- What access is currently documented as broader than necessary?
- Is APP_ZONE currently broader than intended?
- Should broad LAN to APP_ZONE access remain in the final design?
- Why is broad SERVICE_ZONE to LAN a concern?
- What is the target state for Admin laptop access?
- What is the documented concern with DMZ_ZONE broad internal reachability?
- What broad access should not remain in the final design for APP01?

### What a good answer should demonstrate
- correct use of `unnecessary_access.md`
- correct use of `target_intent.md`
- ability to explain why the access is broader than intended
- clear distinction between operational need and excessive reachability

---

## Test Group 8 — Uncertainty and Open Questions

These questions verify that the agent can handle unresolved knowledge honestly.

### Questions
- What is still unresolved in the network model?
- Can MGMT_SEGMENT be judged confidently yet?
- Is the final Admin laptop restriction model already defined?
- Do we know the final policy for EMPLOYEE_SEGMENT?
- Do we know the final policy for GUEST_SEGMENT?
- Is WAN exposure fully settled?
- What currently limits stronger conclusions about final least-privilege posture?

### What a good answer should demonstrate
- correct use of `open_questions.md`
- no false certainty
- clear explanation of what is known versus unresolved
- ability to say why uncertainty matters

---

## Test Group 9 — Standards-Aware Audit Questions

These questions verify that the agent can compare the documented environment against structured external expectations without pretending to be a full compliance engine.

### Questions
- What currently appears inconsistent with the documented least-privilege expectations?
- Which areas seem directionally weak from a segmentation perspective?
- What documented access patterns appear broader than the listed control expectations?
- Which parts of the current model are most relevant to controlled egress expectations?
- Does the documented administrative access model appear tighter or broader than intended?
- Which parts of the design are most relevant to boundary protection reasoning?
- What sensitive service paths should be reviewed from an audit perspective?

### What a good answer should demonstrate
- correct use of `control_references.yaml`
- correct use of `target_intent.md`
- correct use of `unnecessary_access.md`
- careful language
- no unsupported pass/fail verdicts
- standards-aware reasoning rather than standards name-dropping

---

## Test Group 10 — Integrated Audit Reasoning

These questions verify that the agent can combine facts, posture, uncertainty, and standards context in a mature way.

### Questions
- If you were reviewing this network as an auditor, what would you examine first?
- What are the strongest documented signs that the environment is still in a build-phase posture?
- Which areas are operationally functional but not yet hardened?
- What looks like a meaningful architecture concern versus merely incomplete documentation?
- What is the clearest example of current state differing from target intended state?
- Which part of the documented model is most ready for least-privilege refinement?
- Where should a human reviewer ask follow-up questions before making stronger audit judgments?

### What a good answer should demonstrate
- multi-file reasoning
- current vs intended separation
- uncertainty-aware thinking
- standards-aware interpretation
- useful audit-style prioritization
- grounded, non-dramatic analysis

---

## Test Group 11 — Internal vs External Reasoning Separation

These questions verify that the agent can clearly separate:
- what is documented internally,
- what is inferred from internal documentation,
- and what comes from external trusted guidance.

### Questions
- Based only on my documented KB, what are the strongest current concerns?
- What does my KB already document about controlled egress?
- What does my KB already document about administrative access restriction?
- What part of your answer is grounded in my files versus inferred from them?
- Are you using anything external in this answer, or only my documented knowledge?

### What a good answer should demonstrate
- clear separation between internal and external sources
- no hidden external assumptions
- ability to answer using KB only when requested
- precise explanation of what is explicitly documented versus interpreted

---

## Test Group 12 — Trusted External Guidance Questions

These questions verify that the agent can use external trusted guidance carefully when explicitly needed.

### Questions
- What additional external best-practice concerns might matter here even if they are not yet in my KB?
- Are there trusted external expectations relevant to MGMT_SEGMENT even though its final policy is unresolved internally?
- What official or well-recognized guidance would likely matter for broad Admin laptop access?
- Does trusted external guidance suggest tighter expectations for DMZ behavior than what is currently implemented?
- What externally recognized guidance is most relevant to WAN-facing exposure decisions?
- If my KB does not mention a control, does that mean it is irrelevant?
- What additional trusted guidance may be relevant to segmentation even if it is not yet listed in `control_references.yaml`?

### What a good answer should demonstrate
- internal KB reasoning first
- careful use of trusted external sources only when justified
- no random external claims
- explicit labeling of external guidance as external
- no pretending that external guidance is already part of the internal KB

---

## Test Group 13 — External Source Discipline Questions

These questions verify that the agent does not become careless when external information is involved.

### Questions
- How do you decide whether an external source is trustworthy enough to use here?
- Can you answer this question using only my internal KB and no external guidance?
- What would prevent you from making a strong compliance claim here?
- Why should a missing control in my internal standards file not be treated as irrelevant?
- What parts of this issue are internal facts versus external comparison context?

### What a good answer should demonstrate
- conservative standards for external augmentation
- no false certainty
- awareness of source quality
- discipline in separating internal facts from external context

---

## Minimum Success Criteria

The agent should be considered minimally successful if it can:

1. answer direct lookup questions correctly,
2. explain dependencies and required flows clearly,
3. distinguish current state from intended posture,
4. identify access documented as broader than necessary,
5. use standards references as comparison guidance,
6. explicitly acknowledge unresolved uncertainty when it matters,
7. clearly separate internal from external reasoning,
8. and use trusted external guidance carefully when justified.

---

## Failure Indicators

The agent is not behaving correctly if it:

- invents undocumented facts
- confuses current state with intended state
- treats broad current access as if it were already approved long-term design
- ignores uncertainty
- gives absolute compliance verdicts without strong grounding
- fails to distinguish required flows from overly broad access
- uses external guidance without labeling it clearly
- uses weak external material to produce strong claims
- or silently blends external content into the internal documented model

---

## Final Testing Principle

A strong test answer is not only technically correct.
It is also:

- grounded,
- honest,
- comparative,
- standards-aware when relevant,
- careful about uncertainty,
- and explicit about internal versus external sourcing.

That is the standard this agent should be tested against.