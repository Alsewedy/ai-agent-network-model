import json
import re
from pathlib import Path

import yaml

from services.llm_client import real_llm_response


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
NETWORK_DOMAIN_DIR = KNOWLEDGE_ROOT / "domains" / "network"

INDEX_FILE = KNOWLEDGE_ROOT / "index.yaml"
DOMAIN_FILE = NETWORK_DOMAIN_DIR / "domain.yaml"
MODEL_FILE = NETWORK_DOMAIN_DIR / "model.yaml"
CONTROL_REFERENCES_FILE = KNOWLEDGE_ROOT / "standards" / "mappings" / "control_references.yaml"

MARKDOWN_FILES = {
    "scope_units": NETWORK_DOMAIN_DIR / "scope" / "scope_units.md",
    "services": NETWORK_DOMAIN_DIR / "scope" / "services.md",
    "dependencies": NETWORK_DOMAIN_DIR / "scope" / "dependencies.md",
    "required_flows": NETWORK_DOMAIN_DIR / "communication" / "required_flows.md",
    "technical_matrix": NETWORK_DOMAIN_DIR / "communication" / "technical_matrix.md",
    "evidence_notes": NETWORK_DOMAIN_DIR / "evidence" / "evidence_notes.md",
    "unnecessary_access": NETWORK_DOMAIN_DIR / "posture" / "unnecessary_access.md",
    "target_intent": NETWORK_DOMAIN_DIR / "posture" / "target_intent.md",
    "open_questions": NETWORK_DOMAIN_DIR / "uncertainty" / "open_questions.md",
}


# ----------------------------
# Basic loading
# ----------------------------

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


def load_markdown_text(file_path: Path) -> str:
    if not file_path.exists():
        return ""
    return file_path.read_text(encoding="utf-8")


MARKDOWN_CACHE = {k: load_markdown_text(v) for k, v in MARKDOWN_FILES.items()}


# ----------------------------
# Normalization / matching
# ----------------------------

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def short_context_snippet(text: str, keyword: str, window: int = 600) -> str:
    if not text or not keyword:
        return ""

    lower_text = text.lower()
    idx = lower_text.find(keyword.lower())
    if idx == -1:
        return ""

    start = max(0, idx - 140)
    end = min(len(text), idx + window)
    return text[start:end].strip()


def collect_keyword_snippets(
    text: str,
    keywords: list[str],
    max_snippets: int = 3,
    window: int = 600
) -> list[str]:
    if not text:
        return []

    snippets = []
    seen = set()

    for keyword in keywords:
        if not keyword:
            continue

        snippet = short_context_snippet(text, keyword, window=window)
        if not snippet:
            continue

        key = snippet[:220]
        if key in seen:
            continue

        seen.add(key)
        snippets.append(snippet)

        if len(snippets) >= max_snippets:
            break

    return snippets


# ----------------------------
# Model helpers
# ----------------------------

def build_alias_map(model: dict):
    aliases = {}

    # Scope units
    for unit in model.get("scope_units", []):
        name = unit.get("name")
        if not name:
            continue

        aliases[normalize_text(name)] = ("scope_unit", name)

        if name == "LAN":
            aliases["lan"] = ("scope_unit", name)

        if name == "APP_ZONE":
            aliases["app zone"] = ("scope_unit", name)
            aliases["appzone"] = ("scope_unit", name)

        if name == "SERVICE_ZONE":
            aliases["service zone"] = ("scope_unit", name)
            aliases["servicezone"] = ("scope_unit", name)

        if name == "DMZ_ZONE":
            aliases["dmz"] = ("scope_unit", name)
            aliases["dmz zone"] = ("scope_unit", name)

        if name == "MGMT_SEGMENT":
            aliases["mgmt"] = ("scope_unit", name)
            aliases["management segment"] = ("scope_unit", name)

        if name == "ADMIN_SEGMENT":
            aliases["admin segment"] = ("scope_unit", name)

        if name == "EMPLOYEE_SEGMENT":
            aliases["employee segment"] = ("scope_unit", name)

        if name == "GUEST_SEGMENT":
            aliases["guest segment"] = ("scope_unit", name)

        if name == "WAN":
            aliases["wan"] = ("scope_unit", name)

    # Entities
    for entity in model.get("entities", []):
        name = entity.get("name")
        if not name:
            continue

        aliases[normalize_text(name)] = ("entity", name)

        if name == "DC01-CYBERAUDIT":
            aliases["dc01"] = ("entity", name)
            aliases["domain controller"] = ("entity", name)

        if name == "Admin laptop":
            aliases["admin laptop"] = ("entity", name)
            aliases["laptop"] = ("entity", name)

        if name == "Switch Management":
            aliases["switch"] = ("entity", name)
            aliases["switch management"] = ("entity", name)

        if name == "PROXY01":
            aliases["proxy"] = ("entity", name)
            aliases["proxy01"] = ("entity", name)

        if name == "IAM01":
            aliases["iam"] = ("entity", name)
            aliases["iam01"] = ("entity", name)

        if name == "DB01":
            aliases["db"] = ("entity", name)
            aliases["db01"] = ("entity", name)

    # Services
    for entity in model.get("entities", []):
        for service in entity.get("services", []):
            if not service:
                continue
            aliases[normalize_text(service)] = ("service", service)

    # Common service aliases
    aliases["vault"] = ("service", "Vault")
    aliases["keycloak"] = ("service", "Keycloak IAM")
    aliases["internal api"] = ("service", "Internal API")
    aliases["mariadb"] = ("service", "MariaDB database services")
    aliases["dns"] = ("service", "Internal DNS")
    aliases["time"] = ("service", "Time service")
    aliases["ntp"] = ("service", "Time / NTP")

    return aliases


def extract_entities(model: dict, question: str):
    aliases = build_alias_map(model)
    nq = normalize_text(question)

    found_entities = []
    found_scope_units = []
    found_services = []

    for alias in sorted(aliases.keys(), key=len, reverse=True):
        if not alias:
            continue

        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if not re.search(pattern, nq):
            continue

        kind, canonical = aliases[alias]

        if kind == "entity" and canonical not in found_entities:
            found_entities.append(canonical)
        elif kind == "scope_unit" and canonical not in found_scope_units:
            found_scope_units.append(canonical)
        elif kind == "service" and canonical not in found_services:
            found_services.append(canonical)

    return found_entities, found_scope_units, found_services


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
    matches = [q for q in items if norm_name in normalize_text(q)]
    return matches if matches else []


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


# ----------------------------
# Question classification
# ----------------------------

def classify_question(question: str, entities: list[str], scope_units: list[str], services: list[str]) -> list[str]:
    q = normalize_text(question)
    intents = []

    if "depend" in q or "dependency" in q or "rely on" in q:
        intents.append("dependencies")

    if "port" in q or "protocol" in q or "endpoint" in q:
        intents.append("technical_details")

    if "required flow" in q or "required communication" in q or "must remain open" in q or "keep working" in q:
        intents.append("required_flows")

    if "broad" in q or "too open" in q or "overly broad" in q or "unnecessary access" in q or "should remain broad" in q:
        intents.append("overly_broad_access")

    if "intended posture" in q or "target posture" in q or "final design" in q or "intended" in q:
        intents.append("target_posture")

    if "unresolved" in q or "open question" in q or "uncertain" in q or "not fully confirmed" in q:
        intents.append("uncertainty")

    if "standard" in q or "policy" in q or "least privilege" in q or "segmentation" in q or "boundary protection" in q:
        intents.append("standards_comparison")

    if "best practice" in q or "external guidance" in q or "outside my kb" in q or "not in my files" in q:
        intents.append("external_guidance")

    if not intents:
        if entities or scope_units or services:
            intents.append("entity_general")
        else:
            intents.append("general_network_question")

    # preserve order, deduplicate
    deduped = []
    for item in intents:
        if item not in deduped:
            deduped.append(item)

    return deduped


# ----------------------------
# Context building
# ----------------------------

def build_entity_context(model: dict, entity_name: str):
    entity = find_entity(model, entity_name)
    scope_unit_name = entity.get("scope_unit") if entity else None

    keywords = [entity_name]
    if scope_unit_name:
        keywords.append(scope_unit_name)

    supporting_context = {}
    for key, text in MARKDOWN_CACHE.items():
        snippets = collect_keyword_snippets(text, keywords, max_snippets=2)
        if snippets:
            supporting_context[key] = snippets

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
        "supporting_context": supporting_context,
    }


def build_scope_unit_context(model: dict, scope_unit_name: str):
    scope_unit = find_scope_unit(model, scope_unit_name)
    entities = get_entities_in_scope_unit(model, scope_unit_name)
    entity_names = [e.get("name") for e in entities]

    required_flows = []
    technical_matrix = []
    unnecessary_access = []

    for entity_name in entity_names:
        required_flows.extend(get_required_flows_for_name(model, entity_name))
        technical_matrix.extend(get_technical_matrix_for_name(model, entity_name))
        unnecessary_access.extend(get_unnecessary_access_for_name(model, entity_name))

    # scope-unit-level unnecessary access
    unnecessary_access.extend(get_unnecessary_access_for_name(model, scope_unit_name))

    keywords = [scope_unit_name] + entity_names

    supporting_context = {}
    for key, text in MARKDOWN_CACHE.items():
        snippets = collect_keyword_snippets(text, keywords, max_snippets=3)
        if snippets:
            supporting_context[key] = snippets

    return {
        "scope_unit": scope_unit,
        "entities_in_scope_unit": entities,
        "required_flows": required_flows,
        "technical_matrix": technical_matrix,
        "unnecessary_access": unnecessary_access,
        "target_intent": get_target_intent_for_scope_unit(model, scope_unit_name),
        "open_questions": get_open_questions_for_name(model, scope_unit_name),
        "supporting_context": supporting_context,
    }


def build_service_context(model: dict, service_name: str):
    matching_entities = []

    for entity in model.get("entities", []):
        services = entity.get("services", [])
        if any(normalize_text(service_name) in normalize_text(s) for s in services):
            matching_entities.append(entity)

    keywords = [service_name] + [e.get("name") for e in matching_entities]

    supporting_context = {}
    for key, text in MARKDOWN_CACHE.items():
        snippets = collect_keyword_snippets(text, keywords, max_snippets=2)
        if snippets:
            supporting_context[key] = snippets

    return {
        "service_name": service_name,
        "hosting_entities": matching_entities,
        "required_flows": get_required_flows_for_name(model, service_name),
        "technical_matrix": get_technical_matrix_for_name(model, service_name),
        "supporting_context": supporting_context,
    }


def build_global_context(model: dict, domain_data: dict, index_data: dict, control_references: dict):
    return {
        "domain": model.get("domain", {}),
        "domain_metadata": domain_data,
        "index_metadata": index_data,
        "scope_units": model.get("scope_units", []),
        "entities": model.get("entities", []),
        "dependencies": model.get("dependencies", []),
        "unnecessary_access": model.get("unnecessary_access", []),
        "target_intent": model.get("target_intent", {}),
        "open_questions": model.get("open_questions", []),
        "required_flows": model.get("required_flows", []),
        "technical_matrix": model.get("technical_matrix", []),
        "control_references": get_relevant_control_references(control_references, domains=["network"]),
    }


def build_context(model: dict, question: str):
    domain_data = load_domain()
    index_data = load_index()
    control_references = load_control_references()

    entities, scope_units, services = extract_entities(model, question)
    intents = classify_question(question, entities, scope_units, services)

    context = {
        "question": question,
        "intents": intents,
        "entities": {
            "entities": entities,
            "scope_units": scope_units,
            "services": services,
        },
        "structured_facts": {},
        "control_references": {},
    }

    if entities:
        context["structured_facts"]["entities_context"] = {
            name: build_entity_context(model, name)
            for name in entities
        }

    if scope_units:
        context["structured_facts"]["scope_units_context"] = {
            name: build_scope_unit_context(model, name)
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

    relevant_scope_units = scope_units.copy()

    for entity_name in entities:
        entity = find_entity(model, entity_name)
        if entity and entity.get("scope_unit") and entity["scope_unit"] not in relevant_scope_units:
            relevant_scope_units.append(entity["scope_unit"])

    context["control_references"] = {
        "relevant_controls": get_relevant_control_references(
            control_references=control_references,
            scope_units=relevant_scope_units,
            domains=["network"],
        )
    }

    return context


# ----------------------------
# Prompt
# ----------------------------

def build_prompt(context: dict) -> str:
    return f"""
You are a network AI auditor agent for a documented network knowledge base.

Your job:
- answer using the provided context only unless the question explicitly asks for broader external guidance
- treat structured facts as the primary source of truth
- use supporting markdown context only to add explanation and nuance
- use documented control references as structured comparison guidance
- clearly distinguish:
  - current documented state
  - required operational state
  - target intended state
  - unresolved uncertainty
  - documented internal standards expectations
  - optional external guidance only if explicitly requested
- do not invent facts
- do not pretend the KB already contains final audit verdicts
- if the provided context is insufficient, say so clearly

Question:
{context["question"]}

Detected Intents:
{json.dumps(context["intents"], indent=2, ensure_ascii=False)}

Detected Entities:
{json.dumps(context["entities"], indent=2, ensure_ascii=False)}

Structured Facts:
{json.dumps(context["structured_facts"], indent=2, ensure_ascii=False)}

Relevant Control References:
{json.dumps(context["control_references"], indent=2, ensure_ascii=False)}

Answer rules:
1. Start with a direct answer.
2. Use structured facts first.
3. If the question is evaluative, compare:
   - current documented state
   - required operational state
   - target intended state
4. If standards are relevant, use the documented control references as comparison guidance.
5. If uncertainty affects the answer, say so clearly.
6. Do not use final compliance language unless the context unusually supports it.
7. If the user asks for broader external best-practice comparison, clearly separate:
   - what is documented internally
   - what is inferred from internal documentation
   - what comes from external trusted guidance
8. Keep the answer practical, structured, and concise.
""".strip()


# ----------------------------
# Main answer path
# ----------------------------

def answer_question(model, question: str):
    context = build_context(model, question)
    prompt = build_prompt(context)
    answer = real_llm_response(prompt, allow_web_search=False)
    return answer, prompt, context


def main():
    model = load_model()
    print("Network AI Agent v6 (structured baseline, new knowledge architecture)")
    print("Type a question, or type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            answer, prompt, context = answer_question(model, question)

            print("\nAgent:")
            print(answer)
            print("\n" + "-" * 60 + "\n")

            show_debug = input("Show built prompt/context? (y/n): ").strip().lower()
            if show_debug == "y":
                print("\n--- BUILT CONTEXT ---")
                print(json.dumps(context, indent=2, ensure_ascii=False))
                print("\n--- BUILT PROMPT ---")
                print(prompt)
                print("\n" + "=" * 60 + "\n")

        except Exception as e:
            print("\nAgent Error:")
            print(str(e))
            print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()