import json
import re
import yaml
from pathlib import Path
from services.llm_client import real_llm_response


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge" / "network_domain"
YAML_FILE = KNOWLEDGE_DIR / "08_structured_network_model.yaml"

MARKDOWN_FILES = {
    "zones_assets": KNOWLEDGE_DIR / "01_zones_and_assets.md",
    "services": KNOWLEDGE_DIR / "02_services.md",
    "dependencies": KNOWLEDGE_DIR / "03_dependencies.md",
    "required_flows": KNOWLEDGE_DIR / "04_required_flows.md",
    "port_matrix": KNOWLEDGE_DIR / "04a_port_and_protocol_matrix.md",
    "evidence": KNOWLEDGE_DIR / "04b_evidence_notes.md",
    "blocked_flows": KNOWLEDGE_DIR / "05_blocked_or_unnecessary_flows.md",
    "open_questions": KNOWLEDGE_DIR / "06_open_questions_and_assumptions.md",
    "target_intent": KNOWLEDGE_DIR / "07_target_security_intent.md",
}


# ----------------------------
# Basic loading
# ----------------------------

def load_model():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(
            "08_structured_network_model.yaml was loaded as None. "
            "Check the file for invalid YAML formatting or extra text."
        )

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected YAML root to be a dictionary, but got: {type(data)}"
        )

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


def contains_normalized(haystack: str, needle: str) -> bool:
    return normalize_text(needle) in normalize_text(haystack)


def short_context_snippet(text: str, keyword: str, window: int = 500) -> str:
    if not text:
        return ""
    lower_text = text.lower()
    idx = lower_text.find(keyword.lower())
    if idx == -1:
        return ""
    start = max(0, idx - 120)
    end = min(len(text), idx + window)
    return text[start:end].strip()


def collect_keyword_snippets(text: str, keywords: list[str], max_snippets: int = 3, window: int = 500) -> list[str]:
    if not text:
        return []

    snippets = []
    seen = set()

    for keyword in keywords:
        if not keyword:
            continue
        norm_kw = keyword.lower()
        idx = text.lower().find(norm_kw)
        if idx == -1:
            continue

        start = max(0, idx - 120)
        end = min(len(text), idx + window)
        snippet = text[start:end].strip()

        key = snippet[:200]
        if key not in seen:
            seen.add(key)
            snippets.append(snippet)

        if len(snippets) >= max_snippets:
            break

    return snippets


# ----------------------------
# Model index helpers
# ----------------------------

def build_alias_map(model: dict):
    aliases = {}

    # Assets
    for asset in model.get("assets", []):
        name = asset["name"]
        aliases[normalize_text(name)] = ("asset", name)

        # simple extra aliases
        if name == "DC01-CYBERAUDIT":
            aliases["dc01"] = ("asset", name)
            aliases["domain controller"] = ("asset", name)

        if name == "Admin laptop":
            aliases["admin laptop"] = ("asset", name)
            aliases["laptop"] = ("asset", name)

        if name == "Switch Management":
            aliases["switch"] = ("asset", name)
            aliases["switch management"] = ("asset", name)

        if name == "PROXY01":
            aliases["proxy"] = ("asset", name)
            aliases["proxy01"] = ("asset", name)

        if name == "IAM01":
            aliases["iam"] = ("asset", name)
            aliases["keycloak"] = ("asset", name)
            aliases["internal api"] = ("asset", name)

        if name == "DB01":
            aliases["db"] = ("asset", name)
            aliases["db01"] = ("asset", name)
            aliases["vault"] = ("asset", name)

    # Zones
    for zone in model.get("zones", []):
        name = zone["name"]
        aliases[normalize_text(name)] = ("zone", name)

        if name == "LAN / DATA":
            aliases["lan"] = ("zone", name)
            aliases["data"] = ("zone", name)
            aliases["lan data"] = ("zone", name)

        if name == "APP_ZONE":
            aliases["app zone"] = ("zone", name)
            aliases["appzone"] = ("zone", name)

        if name == "SERVICE_ZONE":
            aliases["service zone"] = ("zone", name)
            aliases["servicezone"] = ("zone", name)

        if name == "DMZ_ZONE":
            aliases["dmz"] = ("zone", name)
            aliases["dmz zone"] = ("zone", name)

        if name == "MGMT":
            aliases["mgmt"] = ("zone", name)
            aliases["management zone"] = ("zone", name)

        if name == "ADMIN":
            aliases["admin"] = ("zone", name)

        if name == "EMPLOYEE":
            aliases["employee"] = ("zone", name)

        if name == "GUEST":
            aliases["guest"] = ("zone", name)

        if name == "WAN":
            aliases["wan"] = ("zone", name)

    return aliases


def extract_entities(model: dict, question: str):
    aliases = build_alias_map(model)
    nq = normalize_text(question)

    found_assets = []
    found_zones = []

    # longest aliases first to reduce partial collisions
    for alias in sorted(aliases.keys(), key=len, reverse=True):
        if alias and alias in nq:
            kind, canonical = aliases[alias]
            if kind == "asset" and canonical not in found_assets:
                found_assets.append(canonical)
            elif kind == "zone" and canonical not in found_zones:
                found_zones.append(canonical)

    return found_assets, found_zones


# ----------------------------
# Structured retrieval helpers
# ----------------------------

def find_asset(model: dict, asset_name: str):
    for asset in model.get("assets", []):
        if asset.get("name") == asset_name:
            return asset
    return None


def find_zone(model: dict, zone_name: str):
    for zone in model.get("zones", []):
        if zone.get("name") == zone_name:
            return zone
    return None


def get_assets_in_zone(model: dict, zone_name: str):
    return [a for a in model.get("assets", []) if a.get("zone") == zone_name]


def get_dependencies(model: dict, asset_name: str):
    for item in model.get("dependencies", []):
        if item.get("asset") == asset_name:
            return item.get("depends_on", [])
    return []


def get_reverse_dependencies(model: dict, target_name: str):
    results = []
    norm_target = normalize_text(target_name)

    for item in model.get("dependencies", []):
        asset = item.get("asset")
        depends_on = item.get("depends_on", [])
        for dep in depends_on:
            if norm_target in normalize_text(dep):
                results.append({
                    "asset": asset,
                    "depends_on_entry": dep,
                })
    return results


def entry_mentions_asset(entry: dict, asset_name: str):
    name = normalize_text(asset_name)
    source = normalize_text(entry.get("source", ""))
    destination = normalize_text(entry.get("destination", ""))
    service = normalize_text(entry.get("service", ""))
    purpose = normalize_text(entry.get("purpose", ""))
    flow = normalize_text(entry.get("flow", ""))

    return (
        name in source
        or name in destination
        or name in service
        or name in purpose
        or name in flow
    )


def entry_mentions_zone(entry: dict, zone_name: str):
    name = normalize_text(zone_name)
    combined = " ".join([
        normalize_text(str(entry.get("source", ""))),
        normalize_text(str(entry.get("destination", ""))),
        normalize_text(str(entry.get("purpose", ""))),
        normalize_text(str(entry.get("flow", ""))),
    ])
    return name in combined


def get_required_flows_for_asset(model: dict, asset_name: str):
    return [f for f in model.get("required_flows", []) if entry_mentions_asset(f, asset_name)]


def get_port_matrix_for_asset(model: dict, asset_name: str):
    return [p for p in model.get("port_protocol_matrix", []) if entry_mentions_asset(p, asset_name)]


def get_blocked_flows_for_asset(model: dict, asset_name: str):
    return [b for b in model.get("blocked_or_unnecessary_flows", []) if entry_mentions_asset(b, asset_name)]


def get_blocked_flows_for_zone(model: dict, zone_name: str):
    return [b for b in model.get("blocked_or_unnecessary_flows", []) if entry_mentions_zone(b, zone_name)]


def get_target_intent_for_zone(model: dict, zone_name: str):
    target = model.get("target_security_intent", {})
    zone_intent = target.get("zone_intent", {}).get(zone_name, "")
    return {
        "zone_intent": zone_intent,
        "general": target.get("general", []),
        "identity_intent": target.get("identity_intent", []),
        "database_and_secret_intent": target.get("database_and_secret_intent", []),
        "proxy_and_egress_intent": target.get("proxy_and_egress_intent", []),
        "administrative_access_intent": target.get("administrative_access_intent", []),
    }


def get_open_questions(model: dict):
    return model.get("open_questions", [])


def get_open_questions_for_zone(zone_name: str, model: dict):
    questions = model.get("open_questions", [])
    zn = normalize_text(zone_name)
    filtered = []

    for q in questions:
        qn = normalize_text(q)
        if zn in qn:
            filtered.append(q)

    # if none matched directly, return all because some are global blockers
    return filtered if filtered else questions


# ----------------------------
# Question classification
# ----------------------------

def classify_question(question: str, assets: list[str], zones: list[str]) -> str:
    q = normalize_text(question)

    if "transition plan" in q or "final least privilege transition plan" in q:
        return "transition_plan"

    if "allow list" in q or "least privilege allow list" in q:
        return "allow_list"

    if "must remain open" in q or "keep working" in q or "what network access must remain open" in q:
        return "required_access"

    if "depend" in q or "dependencies" in q or "rely on" in q:
        return "dependencies"

    if "what services" in q or "services hosted" in q or "what does" in q and "provide" in q:
        return "services"

    if "port" in q or "protocol" in q:
        return "ports_protocols"

    if "aligned" in q or "target security intent" in q or "current build phase" in q or "final intended design" in q:
        return "comparison"

    if "unresolved" in q or "open questions" in q or "not fully confirmed" in q or "owner declared" in q:
        return "uncertainty"

    if assets or zones:
        return "entity_general"

    return "general_network_question"


# ----------------------------
# Context building
# ----------------------------

def build_asset_context(model: dict, asset_name: str):
    asset = find_asset(model, asset_name)
    zone_name = asset.get("zone") if asset else None

    context = {
        "asset": asset,
        "zone": find_zone(model, zone_name) if zone_name else None,
        "dependencies": get_dependencies(model, asset_name),
        "reverse_dependencies": get_reverse_dependencies(model, asset_name),
        "required_flows": get_required_flows_for_asset(model, asset_name),
        "port_protocol_matrix": get_port_matrix_for_asset(model, asset_name),
        "blocked_flows": get_blocked_flows_for_asset(model, asset_name),
        "zone_target_intent": get_target_intent_for_zone(model, zone_name) if zone_name else {},
        "open_questions": get_open_questions(model),
    }

    keywords = [asset_name]
    if zone_name:
        keywords.append(zone_name)

    context["supporting_context"] = {}
    for key, text in MARKDOWN_CACHE.items():
        snippets = collect_keyword_snippets(text, keywords, max_snippets=2)
        if snippets:
            context["supporting_context"][key] = snippets

    return context


def build_zone_context(model: dict, zone_name: str):
    zone = find_zone(model, zone_name)
    assets = get_assets_in_zone(model, zone_name)

    asset_names = [a["name"] for a in assets]

    zone_required_flows = []
    zone_port_matrix = []

    for asset_name in asset_names:
        zone_required_flows.extend(get_required_flows_for_asset(model, asset_name))
        zone_port_matrix.extend(get_port_matrix_for_asset(model, asset_name))

    context = {
        "zone": zone,
        "assets_in_zone": assets,
        "required_flows_for_zone_assets": zone_required_flows,
        "port_protocol_matrix_for_zone_assets": zone_port_matrix,
        "blocked_flows_for_zone": get_blocked_flows_for_zone(model, zone_name),
        "target_intent_for_zone": get_target_intent_for_zone(model, zone_name),
        "open_questions": get_open_questions_for_zone(zone_name, model),
    }

    keywords = [zone_name] + asset_names

    context["supporting_context"] = {}
    for key, text in MARKDOWN_CACHE.items():
        snippets = collect_keyword_snippets(text, keywords, max_snippets=3)
        if snippets:
            context["supporting_context"][key] = snippets

    return context


def build_global_context(model: dict):
    return {
        "zones": model.get("zones", []),
        "assets": model.get("assets", []),
        "dependencies": model.get("dependencies", []),
        "required_flows": model.get("required_flows", []),
        "port_protocol_matrix": model.get("port_protocol_matrix", []),
        "blocked_or_unnecessary_flows": model.get("blocked_or_unnecessary_flows", []),
        "open_questions": model.get("open_questions", []),
        "target_security_intent": model.get("target_security_intent", {}),
    }


def build_context(model: dict, question: str):
    assets, zones = extract_entities(model, question)
    intent = classify_question(question, assets, zones)

    context = {
        "question": question,
        "intent": intent,
        "entities": {
            "assets": assets,
            "zones": zones,
        },
        "structured_facts": {},
        "supporting_context": {},
    }

    # Global special case for APP_ZONE-like transition plans with multiple assets
    if intent == "transition_plan" and zones:
        zone_name = zones[0]
        zone_ctx = build_zone_context(model, zone_name)
        context["structured_facts"]["zone_context"] = zone_ctx

    elif assets and not zones:
        # one or multiple assets mentioned
        context["structured_facts"]["assets_context"] = {
            asset_name: build_asset_context(model, asset_name)
            for asset_name in assets
        }

    elif zones and not assets:
        # one or multiple zones mentioned
        context["structured_facts"]["zones_context"] = {
            zone_name: build_zone_context(model, zone_name)
            for zone_name in zones
        }

    elif assets and zones:
        # mixed question: include both
        context["structured_facts"]["assets_context"] = {
            asset_name: build_asset_context(model, asset_name)
            for asset_name in assets
        }
        context["structured_facts"]["zones_context"] = {
            zone_name: build_zone_context(model, zone_name)
            for zone_name in zones
        }

    else:
        context["structured_facts"]["global_context"] = build_global_context(model)

    return context


# ----------------------------
# Prompt
# ----------------------------

def build_prompt(context: dict) -> str:
    return f"""
You are a network-aware AI assistant for a documented homelab environment.

Your job:
- answer only using the provided context
- do not invent facts
- clearly distinguish:
  - confirmed facts
  - owner-confirmed facts
  - standard defaults declared by the owner
  - unresolved / open questions
- keep the answer practical, structured, and concise
- if the provided context is insufficient, say so clearly

Question:
{context['question']}

Intent:
{context['intent']}

Detected Entities:
{json.dumps(context['entities'], indent=2, ensure_ascii=False)}

Structured Facts:
{json.dumps(context['structured_facts'], indent=2, ensure_ascii=False)}

Answer rules:
1. Start with a direct answer.
2. For allow-list or transition-plan questions:
   - use port_protocol_matrix first
   - then use required_flows
   - then use target_security_intent
3. Clearly separate:
   - flows that must remain
   - broad trust that should be removed
   - local-only host-internal flows
   - owner-declared defaults
   - unresolved blockers
4. If the question mentions multiple assets or a zone with multiple assets, treat them separately.
5. If a port/protocol is documented, do not say it is undocumented.
6. If something is only owner-declared or owner-confirmed, say that clearly.
7. If something is local-only and not an inter-host firewall rule, say that clearly.
8. Do not use general cybersecurity assumptions beyond the provided context.
9. If the question is broader than the current documented model supports, state the limitation clearly.
""".strip()


# ----------------------------
# Main answer path
# ----------------------------

def answer_question(model, question: str):
    context = build_context(model, question)
    prompt = build_prompt(context)
    answer = real_llm_response(prompt)
    return answer, prompt, context


def main():
    model = load_model()
    print("Network AI Agent v6 (generalized, OpenAI-connected)")
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