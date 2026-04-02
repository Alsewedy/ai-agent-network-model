# Phase 2 – Agent Logic v1

## Purpose
This document defines the first practical reasoning workflow for the network AI agent.

It explains:
- how the agent should process a user question,
- which source it should consult first,
- when it should use YAML,
- when it should use markdown context,
- how it should handle uncertainty,
- and how it should produce a grounded answer.

The purpose of this logic is not to create a perfect agent immediately.
It is to create a first usable, trustworthy, network-aware assistant.

---

## 1. Core Logic Principle

The agent should not answer directly from general model knowledge alone.

Instead, it should answer by using the documented network model in this order:

1. structured facts first
2. supporting context second
3. uncertainty handling before recommendation
4. practical answer last

---

## 2. Primary Source Order

### First source
- `knowledge/network_domain/08_structured_network_model.yaml`

This should be used first for:
- assets
- zones
- services
- dependencies
- required flows
- blocked flows
- port and protocol data
- open questions
- target intent
- certainty labels

### Second source
- markdown files

These should be used when:
- the question needs explanation
- the answer needs architectural reasoning
- the agent needs current vs target comparison context
- the YAML alone is too compact for a good answer

---

## 3. Question Classification

The first version of the agent should classify the question into one of these categories:

### Type 1 – Asset / Zone Question
Examples:
- What systems are in APP_ZONE?
- Where is IAM01 located?

### Type 2 – Service Question
Examples:
- What services are hosted on DB01?
- Does IAM01 host the Internal API?

### Type 3 – Dependency Question
Examples:
- What does APP01 depend on?
- Which systems rely on Vault?

### Type 4 – Required Flow Question
Examples:
- What communication must remain open for APP02?
- What does IAM01 need to reach?

### Type 5 – Port / Protocol Question
Examples:
- What port does APP01 use to reach the Internal API?
- What protocol is used for DB access?

### Type 6 – Current vs Target Comparison Question
Examples:
- Is broad APP_ZONE access aligned with the target security intent?
- Which current permissions should not remain in the final design?

### Type 7 – Uncertainty / Model Gap Question
Examples:
- What is still unresolved in the network model?
- Which values are owner-declared defaults?

### Type 8 – Recommendation Question
Examples:
- What should be tightened first in APP_ZONE?
- What should remain open for least privilege?

---

## 4. Reasoning Workflow

For each question, the agent should follow this reasoning path:

### Step 1 – Identify question type
The agent should determine what kind of question is being asked.

### Step 2 – Read YAML first
The agent should retrieve the relevant structured sections from:
- zones
- assets
- dependencies
- required_flows
- port_protocol_matrix
- blocked_or_unnecessary_flows
- open_questions
- target_security_intent
- metadata

### Step 3 – Decide whether markdown context is needed
The agent should use markdown context if:
- the question needs explanation rather than only facts
- the question involves current vs target comparison
- the question requires security interpretation
- the answer would be too shallow without supporting reasoning

### Step 4 – Check certainty level
Before finalizing the answer, the agent should identify whether the relevant information is:
- confirmed
- owner_confirmed
- standard_default_declared_by_owner
- open_question

### Step 5 – Build answer
The answer should include:
- direct answer
- concise reasoning
- certainty handling
- practical implication when relevant

---

## 5. YAML Preference Rules

The agent should prefer YAML when the question is asking for:

- exact asset placement
- service presence
- dependency listing
- required flows
- port/protocol details
- open questions
- certainty level

The YAML is the preferred source for:
- precise retrieval
- structured answers
- fact grounding

---

## 6. Markdown Preference Rules

The agent should also consult markdown when the question is asking for:

- why something exists
- whether broad access is justified
- how current state differs from target intent
- what the broader architectural meaning is
- how a recommendation should be explained

The markdown files are the preferred source for:
- reasoning depth
- explanation
- architecture context
- security interpretation

---

## 7. Uncertainty Rules

If the relevant information is unresolved, the agent must not convert it into a confirmed fact.

The agent should instead:

- answer with the confirmed part only
- identify the unresolved part explicitly
- state that it remains open or owner-declared
- avoid pretending that the model is more complete than it is

Example:
- "The model confirms that IAM01 depends on DC01 for DNS, LDAP-related federation, and time-related services. However, some communication values are still treated as standard defaults declared by the owner rather than directly observed packet-level evidence."

---

## 8. Recommendation Rules

If the user asks for a recommendation, the agent should:

1. identify the current state
2. identify the required state
3. identify the target intent
4. identify uncertainty
5. produce a scoped recommendation

The agent should avoid:
- generic best-practice answers detached from the model
- absolute claims when the model still contains open questions

---

## 9. Comparison Rules

If the question compares current and target state, the agent should explicitly separate:

- currently allowed communication
- operationally required communication
- target least-privilege communication

This separation is one of the core design goals of the network knowledge base.

---

## 10. First Operational Goal

The first version of the agent should be able to do these five things reliably:

1. retrieve asset/service/dependency facts
2. retrieve required flows
3. retrieve exact ports and protocols where documented
4. compare current broad access with target security intent
5. identify open questions and uncertainty honestly

If the agent can do these five things well, then the first network AI layer is already useful.

---

## 11. Out-of-Scope Behavior

The first version of the agent should not pretend to know details that are not yet documented, such as:

- full Active Directory structure
- full GPO design
- exact future management policy for all zones
- undocumented application internals
- undocumented firewall rule syntax

If asked about such things, the agent should say that the current model does not yet support a final answer.

---

## Notes
- This logic applies only to the network domain in the current phase.
- The purpose is reliability first, not complexity first.
- The future agent can become more advanced later, but v1 should remain simple, grounded, and trustworthy.