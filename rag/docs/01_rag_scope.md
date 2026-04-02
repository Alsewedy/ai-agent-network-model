# Phase 4 – RAG Scope

## Purpose
This document defines which files are included in the first Hybrid YAML + RAG implementation.

The goal is to use RAG only for environment knowledge retrieval, not for agent-planning documents.

---

## Files included in RAG
- `knowledge/network_domain/01_zones_and_assets.md`
- `knowledge/network_domain/02_services.md`
- `knowledge/network_domain/03_dependencies.md`
- `knowledge/network_domain/04_required_flows.md`
- `knowledge/network_domain/04a_port_and_protocol_matrix.md`
- `knowledge/network_domain/04b_evidence_notes.md`
- `knowledge/network_domain/05_blocked_or_unnecessary_flows.md`
- `knowledge/network_domain/06_open_questions_and_assumptions.md`
- `knowledge/network_domain/07_target_security_intent.md`

---

## Files excluded from RAG for now
- `knowledge/network_domain/08_structured_network_model.yaml`
- `docs/agent_design/09_agent_input_design.md`
- `docs/agent_design/10_agent_test_questions.md`
- `docs/agent_design/11_agent_answer_style.md`
- `docs/agent_design/12_agent_logic_v1.md`
- `docs/agent_design/13_agent_mvp_definition.md`
- `docs/agent_design/14_agent_execution_plan.md`

---

## Reasoning
The included files describe the documented network environment itself.

The excluded files are:
- structured source-of-truth files,
- or project/planning files about how the agent should work.

The first RAG layer should retrieve environment knowledge only.