"""
agent_v8.py – Advanced Hybrid Orchestration Agent for the new knowledge architecture.

Key properties:
  1. Multi-intent reasoning
  2. Dynamic retrieval scaling
  3. Structured facts as primary source of truth
  4. Local markdown / RAG knowledge as part of the local KB
  5. Standards-aware comparison support
  6. Uncertainty-aware reasoning support
  7. Optional external-guidance behavior with explicit mode separation
  8. Unified context shape across agents
"""

import json
import re
from pathlib import Path

import yaml

from services.llm_client import real_llm_response
from rag.retrieve_chunks_v2 import retrieve_with_metadata


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
NETWORK_DOMAIN_DIR = KNOWLEDGE_ROOT / "domains" / "network"

INDEX_FILE = KNOWLEDGE_ROOT / "index.yaml"
DOMAIN_FILE = NETWORK_DOMAIN_DIR / "domain.yaml"
MODEL_FILE = NETWORK_DOMAIN_DIR / "model.yaml"
CONTROL_REFERENCES_FILE = KNOWLEDGE_ROOT / "standards" / "mappings" / "control_references.yaml"


# ════════════════════════════════════════════════════════════════
#  Loading
# ════════════════════════════════════════════════════════════════

def _load_yaml_file(file_path: Path):
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data


def load_model():
    model = _load_yaml_file(MODEL_FILE)

    if model is None:
        raise ValueError(
            "model.yaml was loaded as None. "
            "Check the file for invalid YAML formatting or extra text."
        )

    if not isinstance(model, dict):
        raise ValueError(
            f"Expected YAML root to be a dictionary, but got: {type(model)}"
        )

    return model


def load_domain():
    data = _load_yaml_file(DOMAIN_FILE)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected domain.yaml root to be a dictionary, but got: {type(data)}")
    return data


def load_index():
    data = _load_yaml_file(INDEX_FILE)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected index.yaml root to be a dictionary, but got: {type(data)}")
    return data


def load_control_references():
    data = _load_yaml_file(CONTROL_REFERENCES_FILE)
    if data is None:
        return {"controls": []}
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected control_references.yaml root to be a dictionary, but got: {type(data)}"
        )
    data.setdefault("controls", [])
    return data


# ════════════════════════════════════════════════════════════════
#  Normalization
# ════════════════════════════════════════════════════════════════

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("→", " ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ════════════════════════════════════════════════════════════════
#  Alias Map / Entity Detection
# ════════════════════════════════════════════════════════════════

def build_alias_map(model: dict) -> dict:
    aliases = {}

    # ── Scope units ──
    for unit in model.get("scope_units", []):
        name = unit.get("name")
        if not name:
            continue

        aliases[normalize_text(name)] = ("scope_unit", name)

    aliases["lan"] = ("scope_unit", "LAN")
    aliases["app zone"] = ("scope_unit", "APP_ZONE")
    aliases["appzone"] = ("scope_unit", "APP_ZONE")
    aliases["service zone"] = ("scope_unit", "SERVICE_ZONE")
    aliases["servicezone"] = ("scope_unit", "SERVICE_ZONE")
    aliases["dmz"] = ("scope_unit", "DMZ_ZONE")
    aliases["dmz zone"] = ("scope_unit", "DMZ_ZONE")
    aliases["mgmt"] = ("scope_unit", "MGMT_SEGMENT")
    aliases["management segment"] = ("scope_unit", "MGMT_SEGMENT")
    aliases["admin segment"] = ("scope_unit", "ADMIN_SEGMENT")
    aliases["employee segment"] = ("scope_unit", "EMPLOYEE_SEGMENT")
    aliases["guest segment"] = ("scope_unit", "GUEST_SEGMENT")
    aliases["wan"] = ("scope_unit", "WAN")

    # ── Entities ──
    for entity in model.get("entities", []):
        name = entity.get("name")
        if not name:
            continue

        aliases[normalize_text(name)] = ("entity", name)

    aliases["dc01"] = ("entity", "DC01-CYBERAUDIT")
    aliases["domain controller"] = ("entity", "DC01-CYBERAUDIT")
    aliases["laptop"] = ("entity", "Admin laptop")
    aliases["admin laptop"] = ("entity", "Admin laptop")
    aliases["switch"] = ("entity", "Switch Management")
    aliases["switch management"] = ("entity", "Switch Management")
    aliases["proxy"] = ("entity", "PROXY01")
    aliases["proxy01"] = ("entity", "PROXY01")
    aliases["iam"] = ("entity", "IAM01")
    aliases["iam01"] = ("entity", "IAM01")
    aliases["db"] = ("entity", "DB01")
    aliases["db01"] = ("entity", "DB01")

    # ── Services ──
    for entity in model.get("entities", []):
        for service in entity.get("services", []):
            if not service:
                continue
            aliases[normalize_text(service)] = ("service", service)

    aliases["vault"] = ("service", "Vault")
    aliases["keycloak"] = ("service", "Keycloak IAM")
    aliases["internal api"] = ("service", "Internal API")
    aliases["mariadb"] = ("service", "MariaDB database services")
    aliases["dns"] = ("service", "Internal DNS")
    aliases["time"] = ("service", "Time service")
    aliases["ntp"] = ("service", "Time / NTP")

    return aliases


def extract_entities(alias_map: dict, question: str):
    nq = normalize_text(question)

    found_entities = []
    found_scope_units = []
    found_services = []

    for alias in sorted(alias_map.keys(), key=len, reverse=True):
        if not alias:
            continue

        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if not re.search(pattern, nq):
            continue

        kind, canonical = alias_map[alias]

        if kind == "entity" and canonical not in found_entities:
            found_entities.append(canonical)
        elif kind == "scope_unit" and canonical not in found_scope_units:
            found_scope_units.append(canonical)
        elif kind == "service" and canonical not in found_services:
            found_services.append(canonical)

    return found_entities, found_scope_units, found_services


def find_host_for_service(model: dict, service_name: str) -> str | None:
    target = normalize_text(service_name)

    for entity in model.get("entities", []):
        for service in entity.get("services", []):
            if target in normalize_text(service):
                return entity.get("name")

    return None


# ════════════════════════════════════════════════════════════════
#  Model Helpers
# ════════════════════════════════════════════════════════════════

def find_entity(model: dict, entity_name: str):
    for entity in model.get("entities", []):
        if entity.get("name") == entity_name:
            return entity
    return None


def find_scope_unit(model: dict, scope_unit_name: str):
    for unit in model.get("scope_units", []):
        if unit.get("name") == scope_unit_name:
            return unit
    return None


def get_entities_in_scope_unit(model: dict, scope_unit_name: str):
    names = []

    for unit in model.get("scope_units", []):
        if unit.get("name") == scope_unit_name:
            names = unit.get("entities", []) or []
            break

    results = []
    for entity in model.get("entities", []):
        if entity.get("name") in names:
            results.append(entity)

    return results


def get_dependencies(model: dict, entity_name: str):
    for item in model.get("dependencies", []):
        if item.get("entity") == entity_name:
            return item.get("depends_on", [])
    return []


def get_reverse_dependencies(model: dict, target_name: str):
    results = []
    norm_target = normalize_text(target_name)

    for item in model.get("dependencies", []):
        entity = item.get("entity")
        depends_on = item.get("depends_on", [])
        for dep in depends_on:
            if norm_target in normalize_text(dep):
                results.append({
                    "entity": entity,
                    "depends_on_entry": dep,
                })

    return results


def _entry_mentions_name(entry: dict, name: str):
    norm_name = normalize_text(name)
    joined = " ".join(
        normalize_text(str(v))
        for v in entry.values()
        if isinstance(v, (str, int, float, bool))
    )
    return norm_name in joined


def get_required_flows_for_name(model: dict, name: str):
    return [f for f in model.get("required_flows", []) if _entry_mentions_name(f, name)]


def get_technical_matrix_for_name(model: dict, name: str):
    return [t for t in model.get("technical_matrix", []) if _entry_mentions_name(t, name)]


def get_unnecessary_access_for_name(model: dict, name: str):
    return [u for u in model.get("unnecessary_access", []) if _entry_mentions_name(u, name)]


def get_target_intent_for_scope_unit(model: dict, scope_unit_name: str):
    target = model.get("target_intent", {})
    return {
        "general": target.get("general", []),
        "scope_unit_target": target.get("per_scope_unit", {}).get(scope_unit_name, ""),
        "intended_alignment": [
            item for item in target.get("intended_alignment", [])
            if item.get("scope_unit") in {scope_unit_name, "general"}
        ],
    }


def get_open_questions(model: dict):
    return model.get("open_questions", [])


def get_open_questions_for_name(model: dict, name: str):
    items = model.get("open_questions", [])
    norm_name = normalize_text(name)
    return [q for q in items if norm_name in normalize_text(q)]


def get_relevant_control_references(
    control_references: dict,
    scope_units: list[str] | None = None,
    domains: list[str] | None = None,
):
    scope_units = scope_units or []
    domains = domains or ["network"]

    results = []

    for control in control_references.get("controls", []):
        relevant_domains = control.get("relevant_domains", [])
        relevant_scope_units = control.get("relevant_scope_units", [])

        domain_match = any(d in relevant_domains for d in domains)
        scope_match = not scope_units or any(su in relevant_scope_units for su in scope_units)

        if domain_match and scope_match:
            results.append(control)

    return results


def infer_risk_owner(
    domain_data: dict,
    entities: list[str],
    scope_units: list[str],
    services: list[str],
) -> dict:
    domain_root = domain_data.get("domain", {})

    domain_owner = domain_root.get("owner", "Unknown")
    domain_name = domain_root.get("name", "Unknown")

    matched_from = "domain_owner_fallback"

    if "IAM01" in entities or any(normalize_text(s) in {"keycloak iam", "internal api"} for s in services):
        return {
            "owner": domain_owner,
            "basis": "IAM-related issue; no narrower owner documented, so domain owner is used as fallback.",
            "matched_from": matched_from,
            "domain": domain_name,
        }

    if "MGMT_SEGMENT" in scope_units or "ADMIN_SEGMENT" in scope_units:
        return {
            "owner": domain_owner,
            "basis": "Management / privileged-access issue; no narrower owner documented, so domain owner is used as fallback.",
            "matched_from": matched_from,
            "domain": domain_name,
        }

    if "WAN" in scope_units or "DMZ_ZONE" in scope_units or "PROXY01" in entities:
        return {
            "owner": domain_owner,
            "basis": "Boundary / egress / DMZ-related issue; no narrower owner documented, so domain owner is used as fallback.",
            "matched_from": matched_from,
            "domain": domain_name,
        }

    return {
        "owner": domain_owner,
        "basis": "No narrower owner is documented for this issue, so the domain owner is used as the default risk owner.",
        "matched_from": matched_from,
        "domain": domain_name,
    }


# ════════════════════════════════════════════════════════════════
#  Intent Logic / Answer Modes
# ════════════════════════════════════════════════════════════════

def classify_question(question: str, entities: list[str], scope_units: list[str], services: list[str]) -> list[str]:
    q = normalize_text(question)
    intents = []

    if "transition plan" in q or "least privilege transition plan" in q:
        intents.append("transition_plan")

    if "allow list" in q or "must remain open" in q or "keep working" in q:
        intents.append("required_flows")

    if "depend" in q or "dependency" in q or "rely on" in q:
        intents.append("dependencies")

    if "port" in q or "protocol" in q or "endpoint" in q:
        intents.append("technical_details")

    if "inventory" in q or "list all" in q or "enumerate" in q:
        intents.append("inventory")

    if "broad" in q or "too open" in q or "overly broad" in q or "unnecessary access" in q:
        intents.append("overly_broad_access")

    if "intended posture" in q or "target posture" in q or "final design" in q or "intended" in q:
        intents.append("target_posture")

    if "unresolved" in q or "open question" in q or "uncertain" in q or "not fully confirmed" in q:
        intents.append("uncertainty")

    if "standard" in q or "policy" in q or "least privilege" in q or "segmentation" in q or "boundary protection" in q:
        intents.append("standards_comparison")

    if (
        "best practice" in q
        or "external guidance" in q
        or "outside my kb" in q
        or "not in my files" in q
        or "from the internet" in q
        or "official guidance" in q
        or "vendor guidance" in q
        or "trusted external" in q
    ):
        intents.append("external_guidance")

    if "owner of the risk" in q or "risk owner" in q or "who owns" in q:
        intents.append("risk_owner")

    if not intents:
        if entities or scope_units or services:
            intents.append("entity_general")
        else:
            intents.append("general_network_question")

    deduped = []
    for item in intents:
        if item not in deduped:
            deduped.append(item)

    return deduped


def should_include_standards_section(question: str, intents: list[str]) -> bool:
    q = normalize_text(question)

    explicit_policy_request = any(
        phrase in q for phrase in [
            "what policies",
            "which policy",
            "which policies",
            "what standard",
            "which standard",
            "which standards",
            "what control",
            "which control",
            "which controls",
            "what does it violate",
            "what does this violate",
            "why does it violate",
            "what conflicts",
            "what does it conflict with",
            "why is it misaligned",
            "is it aligned",
            "is it compliant",
            "is it non compliant",
            "compare against",
        ]
    )

    evaluative_intents = {
        "standards_comparison",
        "target_posture",
        "overly_broad_access",
        "external_guidance",
    }

    return explicit_policy_request or any(intent in evaluative_intents for intent in intents)


def determine_answer_mode(question: str, intents: list[str], control_reference_count: int) -> dict:
    q = normalize_text(question)

    explicit_verify = (
        "verify" in q
        or "confirm externally" in q
        or "validate externally" in q
        or "are you sure" in q
    )

    external_requested = "external_guidance" in intents
    local_standards_missing = control_reference_count == 0 and "standards_comparison" in intents

    if explicit_verify:
        mode = "external_verification"
    elif external_requested or local_standards_missing:
        mode = "internal_plus_external"
    else:
        mode = "internal_only"

    return {
        "mode": mode,
        "external_guidance_requested": external_requested,
        "explicit_external_verification": explicit_verify,
        "local_standards_missing": local_standards_missing,
        "needs_audit_style_structure": True,
    }


# ════════════════════════════════════════════════════════════════
#  RAG Integration
# ════════════════════════════════════════════════════════════════

def format_rag_chunks(chunks: list[tuple[int, dict]], max_chunks: int) -> list[dict]:
    formatted = []

    for score, chunk in chunks[:max_chunks]:
        entry = {
            "chunk_id": chunk.get("chunk_id"),
            "source_file": chunk.get("source_file"),
            "section_title": chunk.get("section_title"),
            "chunk_type": chunk.get("chunk_type"),
            "entities": chunk.get("entities", []),
            "scope_units": chunk.get("scope_units", []),
            "confidence_tags": chunk.get("confidence_tags", []),
            "flow_entities": chunk.get("flow_entities", []),
            "flow_scope_units": chunk.get("flow_scope_units", []),
            "text": chunk.get("text", "")[:1600],
            "score": score,
        }

        flow_source = chunk.get("flow_source")
        flow_destination = chunk.get("flow_destination")
        if flow_source and flow_destination:
            entry["flow_direction"] = f"{flow_source.get('raw', '?')} -> {flow_destination.get('raw', '?')}"

        formatted.append(entry)

    return formatted


# ════════════════════════════════════════════════════════════════
#  Context Builders
# ════════════════════════════════════════════════════════════════

def build_entity_context(model: dict, entity_name: str):
    entity = find_entity(model, entity_name)
    scope_unit_name = entity.get("scope_unit") if entity else None

    return {
        "entity": entity,
        "scope_unit": find_scope_unit(model, scope_unit_name) if scope_unit_name else None,
        "dependencies": get_dependencies(model, entity_name),
        "reverse_dependencies": get_reverse_dependencies(model, entity_name),
        "required_flows": get_required_flows_for_name(model, entity_name),
        "technical_matrix": get_technical_matrix_for_name(model, entity_name),
        "unnecessary_access": get_unnecessary_access_for_name(model, entity_name),
        "target_intent": get_target_intent_for_scope_unit(model, scope_unit_name) if scope_unit_name else {},
        "open_questions": get_open_questions_for_name(model, entity_name),
    }


def build_scope_unit_context(model: dict, scope_unit_name: str, include_dependency_targets: bool = False):
    scope_unit = find_scope_unit(model, scope_unit_name)
    entities = get_entities_in_scope_unit(model, scope_unit_name)
    entity_names = [e.get("name") for e in entities]

    required_flows = []
    technical_matrix = []
    unnecessary_access = []
    dependency_target_names = set()

    for entity_name in entity_names:
        required_flows.extend(get_required_flows_for_name(model, entity_name))
        technical_matrix.extend(get_technical_matrix_for_name(model, entity_name))
        unnecessary_access.extend(get_unnecessary_access_for_name(model, entity_name))

        for dep in get_dependencies(model, entity_name):
            dependency_target_names.add(dep)

    unnecessary_access.extend(get_unnecessary_access_for_name(model, scope_unit_name))

    result = {
        "scope_unit": scope_unit,
        "entities_in_scope_unit": entities,
        "required_flows": required_flows,
        "technical_matrix": technical_matrix,
        "unnecessary_access": unnecessary_access,
        "target_intent": get_target_intent_for_scope_unit(model, scope_unit_name),
        "open_questions": get_open_questions_for_name(model, scope_unit_name),
    }

    if include_dependency_targets:
        dependency_target_entities = []

        for dep_name in dependency_target_names:
            entity = find_entity(model, dep_name)
            if not entity:
                match = re.search(r"on\s+(.+)$", dep_name)
                if match:
                    entity = find_entity(model, match.group(1).strip())

            if entity and entity not in dependency_target_entities and entity.get("name") not in entity_names:
                dependency_target_entities.append(entity)

        result["dependency_target_entities"] = dependency_target_entities

    return result


def build_service_context(model: dict, service_name: str):
    matching_entities = []

    for entity in model.get("entities", []):
        services = entity.get("services", [])
        if any(normalize_text(service_name) in normalize_text(s) for s in services):
            matching_entities.append(entity)

    return {
        "service_name": service_name,
        "hosting_entities": matching_entities,
        "required_flows": get_required_flows_for_name(model, service_name),
        "technical_matrix": get_technical_matrix_for_name(model, service_name),
    }


def build_global_context(model: dict, domain_data: dict, index_data: dict, control_references: dict):
    return {
        "domain": model.get("domain", {}),
        "domain_metadata": domain_data,
        "scope_units": model.get("scope_units", []),
        "entities": model.get("entities", []),
        "dependencies": model.get("dependencies", []),
        "unnecessary_access": model.get("unnecessary_access", []),
        "target_intent": model.get("target_intent", {}),
        "open_questions": model.get("open_questions", []),
        "required_flows": model.get("required_flows", []),
        "technical_matrix": model.get("technical_matrix", []),
        "control_references": get_relevant_control_references(control_references, domains=["network"]),
        "index_metadata": index_data,
    }


def build_context(model: dict, alias_map: dict, question: str):
    domain_data = load_domain()
    domain_root = domain_data.get("domain", {})
    index_data = load_index()
    control_references = load_control_references()

    entities, scope_units, services = extract_entities(alias_map, question)

    service_hosts = {}
    for service in services:
        host = find_host_for_service(model, service)
        if host:
            service_hosts[service] = host
            if host not in entities:
                entities.append(host)

    relevant_scope_units = scope_units.copy()

    for entity_name in entities:
        entity = find_entity(model, entity_name)
        if entity and entity.get("scope_unit") and entity["scope_unit"] not in relevant_scope_units:
            relevant_scope_units.append(entity["scope_unit"])

    relevant_controls = get_relevant_control_references(
        control_references=control_references,
        scope_units=relevant_scope_units,
        domains=["network"],
    )

    intents = classify_question(question, entities, scope_units, services)
    answer_mode = determine_answer_mode(question, intents, len(relevant_controls))
    include_standards_section = should_include_standards_section(question, intents)

    rag_result = retrieve_with_metadata(question, top_k=10)
    rag_chunks = format_rag_chunks(rag_result.get("chunks", []), max_chunks=14)

    risk_owner = infer_risk_owner(
        domain_data=domain_data,
        entities=entities,
        scope_units=relevant_scope_units,
        services=services,
    )

    context = {
        "question": question,
        "intents": intents,
        "entities": {
            "entities": entities,
            "scope_units": scope_units,
            "services": services,
            "service_hosts": service_hosts,
        },
        "focus": {
            "retriever_intents": sorted(list(rag_result.get("intents", set()))),
            "retriever_focus": rag_result.get("focus", {}),
        },
        "structured_facts": {},
        "rag_chunks": rag_chunks,
        "control_references": {
            "relevant_controls": relevant_controls
        },
        "answer_mode": answer_mode,
        "response_style": {
            "include_standards_section": include_standards_section,
            "include_external_section": answer_mode["mode"] in {"internal_plus_external", "external_verification"},
            "inventory_style": "inventory" in intents or "technical_details" in intents,
        },
        "domain_metadata": {
            "name": domain_root.get("name"),
            "description": domain_root.get("description"),
            "owner": domain_root.get("owner"),
        },
        "risk_owner": risk_owner,
        "external_guidance_policy": {
            "enabled": answer_mode["mode"] in {"internal_plus_external", "external_verification"},
            "must_keep_internal_primary": True,
            "must_check_full_local_kb_first": True,
            "must_label_external_separately": True,
            "local_kb_components": [
                "structured yaml facts",
                "markdown-derived RAG context",
                "documented control references",
            ],
            "trusted_source_priority": [
                "official standards bodies",
                "official vendor documentation",
                "government cybersecurity guidance",
                "widely recognized security foundations",
            ],
            "avoid_source_types": [
                "random blogs",
                "marketing pages",
                "forums",
                "low-authority commentary",
            ],
        },
    }

    include_dependency_targets = "transition_plan" in intents or "dependencies" in intents

    if entities:
        context["structured_facts"]["entities_context"] = {
            name: build_entity_context(model, name)
            for name in entities
        }

    if scope_units:
        context["structured_facts"]["scope_units_context"] = {
            name: build_scope_unit_context(
                model,
                name,
                include_dependency_targets=include_dependency_targets,
            )
            for name in scope_units
        }

    if services:
        context["structured_facts"]["services_context"] = {
            name: build_service_context(model, name)
            for name in services
        }

    if not entities and not scope_units and not services:
        context["structured_facts"]["global_context"] = build_global_context(
            model=model,
            domain_data=domain_data,
            index_data=index_data,
            control_references=control_references,
        )

    return context


# ════════════════════════════════════════════════════════════════
#  Prompt Building
# ════════════════════════════════════════════════════════════════

def build_prompt(context: dict) -> str:
    include_standards_section = context["response_style"]["include_standards_section"]
    include_external_section = context["response_style"]["include_external_section"]
    inventory_style = context["response_style"]["inventory_style"]

    standards_instruction = ""
    if include_standards_section:
        standards_instruction = """
- Relevant documented control expectations
- Why this conflicts / may conflict / may not conflict"""

    external_instruction = ""
    if include_external_section:
        external_instruction = """
- External trusted guidance"""

    section_rules_extra = ""
    if include_standards_section:
        section_rules_extra += """
- "Relevant documented control expectations" = only from the documented internal control references when available
- "Why this conflicts / may conflict / may not conflict" = explicit reasoning that connects environment evidence to the relevant standard or expectation"""

    if include_external_section:
        section_rules_extra += """
- "External trusted guidance" = include ONLY when answer_mode requires external reasoning or local standards are missing"""

    answer_mode_extra = ""
    if not include_standards_section:
        answer_mode_extra = """
- Do NOT include standards, control, policy, compliance, or conflict sections unless the user explicitly asked for them or the question is evaluative by nature.
- For inventory, enumeration, listing, extraction, and technical-detail questions, focus on:
  - direct answer
  - structured inventory/table
  - environment evidence
  - unresolved uncertainty where needed
"""

    inventory_extra = ""
    if inventory_style:
        inventory_extra = """
L) Inventory-style response rule:
- For inventory / listing / extraction questions, prefer:
  - a direct answer
  - a clean table or structured list
  - source/evidence traceability
  - confidence / unresolved distinction
- Do not expand into policy analysis unless explicitly requested.
"""

    return f"""You are an AI auditor for a documented environment.

You must answer with strong grounding, disciplined reasoning, and explicit separation between knowledge layers.

════════════════════════════════════════════
CORE RULES
════════════════════════════════════════════

1. Structured facts are the PRIMARY organized source of truth.
2. Retrieved RAG chunks are also part of the LOCAL documented knowledge base.
3. Local documented knowledge includes:
   - structured YAML facts
   - markdown-derived RAG context
   - documented internal control references
4. Do NOT treat absence from YAML alone as proof that the information does not exist in the local knowledge base.
5. Use documented internal control references first when evaluating against standards.
6. If a relevant standard or control is not documented locally, you may use trusted external guidance when answer_mode allows it.
7. Do NOT invent:
   - protocols
   - ports
   - management paths
   - dependencies
   - flows
   - standards mappings
   - final-state rules
   - owners not supported by context
8. Do NOT treat current broad access as automatically justified.
9. Do NOT confuse:
   - current documented state
   - required operational state
   - target intended state
   - unresolved uncertainty
   - internal documented control expectations
   - external trusted guidance
10. If external guidance is used, it must:
   - be clearly labeled as external
   - be kept separate from internal KB facts
   - never override internal KB facts
   - use trusted sources only
11. If the provided context is insufficient, say so clearly.

════════════════════════════════════════════
QUESTION
════════════════════════════════════════════

{context["question"]}

════════════════════════════════════════════
ANSWER MODE
════════════════════════════════════════════

{json.dumps(context["answer_mode"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
RESPONSE STYLE
════════════════════════════════════════════

{json.dumps(context["response_style"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
DOMAIN METADATA
════════════════════════════════════════════

{json.dumps(context["domain_metadata"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
RISK OWNER DEFAULT
════════════════════════════════════════════

{json.dumps(context["risk_owner"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
EXTERNAL GUIDANCE POLICY
════════════════════════════════════════════

{json.dumps(context["external_guidance_policy"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
DETECTED INTENTS
════════════════════════════════════════════

{json.dumps(context["intents"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
DETECTED ENTITIES
════════════════════════════════════════════

{json.dumps(context["entities"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
RETRIEVER FOCUS
════════════════════════════════════════════

{json.dumps(context["focus"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
STRUCTURED FACTS
════════════════════════════════════════════

{json.dumps(context["structured_facts"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
DOCUMENTED CONTROL REFERENCES
════════════════════════════════════════════

{json.dumps(context["control_references"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
RETRIEVED RAG CHUNKS
════════════════════════════════════════════

{json.dumps(context["rag_chunks"], indent=2, ensure_ascii=False)}

════════════════════════════════════════════
REQUIRED ANSWER METHOD
════════════════════════════════════════════

You must produce an answer using the following discipline:

A) Start with a direct answer.

B) Then separate the answer into clearly labeled sections when relevant:

- Current documented state
- Environment evidence
- Required operational state
- Target intended state{standards_instruction}{external_instruction}
- Unresolved uncertainty
- Risk owner
- Bottom line / auditor conclusion

C) Use these section rules carefully:

- "Current documented state" = what is explicitly documented now
- "Environment evidence" = concrete supporting evidence from the local environment knowledge base
- "Required operational state" = what appears necessary for normal operation
- "Target intended state" = what the target posture says should exist later{section_rules_extra}
- "Unresolved uncertainty" = what is still missing or not fully confirmed
- "Risk owner" = who should own remediation of the issue; use narrower owner only if documented, otherwise use the provided domain owner fallback
- "Bottom line / auditor conclusion" = concise internal conclusion grounded in local evidence

D) LOCAL-FIRST RULES:

- Always check the full local documented knowledge base before treating a point as absent.
- Do NOT move to external guidance merely because a detail is absent from YAML alone.
- If the issue is evaluative and local control references are present, use them first.
- If the issue is evaluative and local control references are missing or insufficient, you may use trusted external standards or guidance when answer_mode allows it.{answer_mode_extra}

E) STRICT INTERNAL / EXTERNAL SEPARATION RULES:

- Do NOT place external citations, external claims, or externally-supported statements inside:
  - Current documented state
  - Environment evidence
  - Required operational state
  - Target intended state
  - Unresolved uncertainty
  - Risk owner
  - Bottom line / auditor conclusion"""

    + ("""
  - Relevant documented control expectations
  - Why this conflicts / may conflict / may not conflict""" if include_standards_section else "") + (
"""
- Those sections must be grounded only in:
  - structured facts
  - retrieved internal RAG context
  - documented internal control references
  - documented domain metadata
""" if include_standards_section else """
- Those sections must be grounded only in:
  - structured facts
  - retrieved internal RAG context
  - documented domain metadata
"""
    ) + ("""
- External sources may appear ONLY inside:
  - External trusted guidance
""" if include_external_section else "") + """

- In the "Bottom line / auditor conclusion" section, summarize the internal conclusion only.
  Do NOT attach external citations there.

F) Answer mode rules:

- If mode = "internal_only":
  - answer from local documented knowledge only
  - do not add external guidance
- If mode = "internal_plus_external":
  - answer from internal documented knowledge first
  - then add a separate external trusted guidance section
  - use external guidance especially when local standards are missing or insufficient
  - make clear that external guidance is not part of the internal KB
- If mode = "external_verification":
  - start from internal documented facts
  - then explicitly check whether trusted external guidance generally supports or cautions against the same pattern
  - never claim external guidance proves internal implementation details
""" + ("""
G) Standards evaluation rules:

- Use documented internal control references first.
- If they do not exist or do not cover the question sufficiently, external trusted standards may be used when answer_mode allows it.
- Do not imply compliance has been achieved unless the context unusually supports that conclusion.
- Prefer careful phrases such as:
  - "appears misaligned"
  - "likely inconsistent with"
  - "not yet supported as aligned"
  - "insufficient evidence to confirm alignment"
""" if include_standards_section else "") + """

H) Evidence rule:

- Evaluative claims must cite environment evidence from the local KB.
- Do not give standards-based criticism without connecting it to a documented local condition.

I) Risk owner rule:

- If a narrower owner is not documented, use the domain owner fallback provided in the context.
- If ownership is uncertain, say so clearly and then provide the most defensible fallback owner.

J) Citation rule:

- Internal sections should not contain web citations.
- External web citations should appear only in the "External trusted guidance" section.

K) Quality target:
- practical
- precise
- non-generic
- audit-oriented
- well-structured
- grounded
{inventory_extra}
Now answer the question.
"""


# ════════════════════════════════════════════════════════════════
#  Main Answer Path
# ════════════════════════════════════════════════════════════════

def answer_question(model: dict, alias_map: dict, question: str):
    context = build_context(model, alias_map, question)
    prompt = build_prompt(context)

    allow_web_search = context["answer_mode"]["mode"] in {
        "internal_plus_external",
        "external_verification",
    }

    answer = real_llm_response(prompt, allow_web_search=allow_web_search)
    return answer, prompt, context


def main():
    model = load_model()
    alias_map = build_alias_map(model)

    print("Network AI Agent v8 (advanced hybrid orchestration, new knowledge architecture)")
    print("Type a question, or type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            answer, prompt, context = answer_question(model, alias_map, question)

            print("\nAgent:")
            print(answer)
            print("\n" + "-" * 60 + "\n")

            show_debug = input("Show debug info? (y/n): ").strip().lower()
            if show_debug == "y":
                print("\n--- INTENTS ---")
                print(context["intents"])

                print("\n--- ANSWER MODE ---")
                print(json.dumps(context["answer_mode"], indent=2, ensure_ascii=False))

                print("\n--- RESPONSE STYLE ---")
                print(json.dumps(context["response_style"], indent=2, ensure_ascii=False))

                print("\n--- RISK OWNER ---")
                print(json.dumps(context["risk_owner"], indent=2, ensure_ascii=False))

                print("\n--- ENTITIES ---")
                print(json.dumps(context["entities"], indent=2, ensure_ascii=False))

                print("\n--- FOCUS ---")
                print(json.dumps(context["focus"], indent=2, ensure_ascii=False))

                print(f"\n--- RAG CHUNKS ({len(context['rag_chunks'])}) ---")
                for chunk in context["rag_chunks"]:
                    chunk_id = chunk.get("chunk_id")
                    chunk_type = chunk.get("chunk_type", "")
                    section_title = chunk.get("section_title", "")
                    print(f"  {chunk_id}: {chunk_type:20s} | {section_title[:60]}")

                print("\n--- STRUCTURED FACTS KEYS ---")
                for key in context["structured_facts"]:
                    value = context["structured_facts"][key]
                    if isinstance(value, dict):
                        print(f"  {key}: {{ {', '.join(value.keys())} }}")
                    else:
                        print(f"  {key}: {type(value).__name__}")

                print("\n" + "=" * 60 + "\n")

                show_prompt = input("Show full prompt? (y/n): ").strip().lower()
                if show_prompt == "y":
                    print("\n--- FULL PROMPT ---")
                    print(prompt)
                    print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print(f"\nAgent Error: {e}")
            print("-" * 60 + "\n")


if __name__ == "__main__":
    main()