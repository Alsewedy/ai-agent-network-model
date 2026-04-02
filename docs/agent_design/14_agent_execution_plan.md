# Phase 2 – Agent Execution Plan

## Purpose
This document defines the first practical execution plan for building the network AI agent MVP.

The goal is to move from:
- documented knowledge,
- structured YAML,
- answer style,
- reasoning logic,
- and MVP scope

into:
- a real first implementation that can be tested.

This plan is intentionally simple.
The priority is to build a first working and trustworthy prototype, not a complex system.

---

## 1. Execution Goal

The goal of the first execution phase is to build a simple prototype that can:

- read the current network knowledge base,
- answer the first official test questions,
- use the YAML as the primary structured source,
- use markdown as supporting context if needed,
- and produce grounded answers with certainty awareness.

---

## 2. First Implementation Style

The first implementation should be a simple prototype, not a full production system.

Recommended style:
- a Python-based prototype
- local file reading
- YAML-first logic
- markdown-supported reasoning
- manual testing against the official test questions

The first version does not need:
- a web interface
- a database
- a graph engine
- automatic updates
- or production deployment

---

## 3. Phase 2 Execution Steps

### Step 1 – Confirm file set
Ensure the network knowledge base files are present and stable.

Expected files:
- `knowledge/network_domain/08_structured_network_model.yaml`
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
- `docs/agent_design/13_agent_mvp_definition.md`

**Output of Step 1:**  
Stable knowledge base ready for agent consumption.

---

### Step 2 – Build YAML loader
Create a simple loader that reads:
- `knowledge/network_domain/08_structured_network_model.yaml`

The loader should allow the prototype to access:
- zones
- assets
- dependencies
- required flows
- port/protocol matrix
- blocked/unnecessary flows
- open questions
- target intent
- certainty-related metadata

**Output of Step 2:**  
Structured model is available inside the prototype.

---

### Step 3 – Build first query handlers
Implement the first simple handlers for:

- asset / zone lookup
- service lookup
- dependency lookup
- required flow lookup
- port / protocol lookup
- open question lookup
- current vs target comparison

The first version does not need complex NLP routing.
Simple classification or explicit command-style handling is enough.

**Output of Step 3:**  
Prototype can answer core network questions from structured data.

---

### Step 4 – Add answer formatting rules
Implement output formatting based on:
- `docs/agent_design/11_agent_answer_style.md`

The prototype should:
- answer directly
- explain briefly
- indicate certainty level
- distinguish current vs target where relevant
- avoid unsupported claims

**Output of Step 4:**  
Prototype produces trustworthy and consistent answers.

---

### Step 5 – Test against official test questions
Run the prototype against:
- `docs/agent_design/10_agent_test_questions.md`

Check whether the prototype can:
- retrieve correct facts
- retrieve correct dependencies
- retrieve required flows correctly
- retrieve exact ports/protocols where documented
- distinguish current broad access from target security intent
- identify open questions honestly

**Output of Step 5:**  
Initial evaluation of whether the MVP is actually useful.

---

### Step 6 – Record gaps and improve
After testing, record:
- wrong answers
- weak answers
- missing facts
- overconfident answers
- unclear areas in the knowledge base

Then improve either:
- the YAML
- the markdown context
- or the prototype logic

**Output of Step 6:**  
A stronger second iteration of the MVP.

---

## 4. Minimum Success Criteria

The first prototype should be considered successful if it can do these things reliably:

1. answer the official dependency question correctly
2. answer the official required flow question correctly
3. answer the official port/protocol question correctly
4. compare broad current access against target intent correctly
5. identify unresolved parts of the model honestly

---

## 5. Things to Avoid in the First Implementation

The first prototype should avoid:

- pretending to know undocumented details
- using broad generic cybersecurity advice instead of model-based reasoning
- confusing current build-phase access with final intended design
- answering outside the documented network scope
- overengineering the prototype too early

---

## 6. Recommended First Technical Direction

Recommended first technical direction:

- Python script
- load YAML
- optionally load markdown
- simple question classifier
- structured answer generation
- manual testing using the official test questions

This is enough for the first MVP.

---

## 7. After This Plan

Once this execution plan is accepted, the next step is not more planning.

The next step is:
- build the first prototype

The first implementation should focus on usefulness, trustworthiness, and grounded reasoning rather than complexity.

---

## Notes
- This is the final planning layer before implementation.
- The purpose is to create momentum toward a real working agent.
- A smaller working prototype is better than a larger unfinished design.