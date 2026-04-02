"""
agent_v8.py – Hybrid YAML + RAG + LLM network reasoning agent.

Key changes from v7:
  1. Multi-intent: uses the retriever's full intent set instead of single classify_question
  2. Dynamic scaling: top_k and prompt max_chunks scale with intent complexity
  3. Dependency-aware zone context: pulls in asset descriptions for dependency targets
  4. Fixed alias map: separates services (Vault, Keycloak, Internal API) from hosts
  5. Flow metadata preserved in prompt: flow_assets reach the LLM
  6. Cached alias map: built once at startup
  7. Smart open_questions: zone-relevant filtering without full-fallback flooding
  8. Better prompt: passes intent set, explicit section order, tighter instructions
"""

import json
import re
from pathlib import Path
from functools import lru_cache
import yaml

from services.llm_client import real_llm_response
from rag.retrieve_chunks_v2 import retrieve_with_metadata


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge" / "network_domain"
YAML_FILE = KNOWLEDGE_DIR / "08_structured_network_model.yaml"


# ════════════════════════════════════════════════════════════════
#  Loading & Normalization
# ════════════════════════════════════════════════════════════════

def load_model():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected YAML root to be a dictionary, got: {type(data)}. "
            "Check 08_structured_network_model.yaml for formatting issues."
        )
    return data


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ════════════════════════════════════════════════════════════════
#  Entity Detection with Cached Alias Map
# ════════════════════════════════════════════════════════════════

def build_alias_map(model: dict) -> dict:
    """
    Build a mapping from normalized text → (kind, canonical_name).
    Kinds: "asset", "zone", "service"

    Service aliases resolve to the SERVICE name (e.g. "Vault"),
    not to the hosting asset. The agent can then look up which
    asset hosts a given service via the YAML assets list.
    """
    aliases = {}

    # ── Assets ──
    for asset in model.get("assets", []):
        name = asset["name"]
        aliases[normalize_text(name)] = ("asset", name)

    # Asset-specific aliases
    aliases["dc01"] = ("asset", "DC01-CYBERAUDIT")
    aliases["domain controller"] = ("asset", "DC01-CYBERAUDIT")
    aliases["laptop"] = ("asset", "Admin laptop")
    aliases["switch"] = ("asset", "Switch Management")
    aliases["proxy"] = ("asset", "PROXY01")

    # ── Services (NOT aliases for the host) ──
    aliases["vault"] = ("service", "Vault")
    aliases["keycloak"] = ("service", "Keycloak")
    aliases["internal api"] = ("service", "Internal API")
    aliases["mariadb"] = ("service", "MariaDB")

    # ── Zones ──
    for zone in model.get("zones", []):
        name = zone["name"]
        aliases[normalize_text(name)] = ("zone", name)

    # Zone-specific aliases
    aliases["lan"] = ("zone", "LAN / DATA")
    aliases["lan data"] = ("zone", "LAN / DATA")
    aliases["app zone"] = ("zone", "APP_ZONE")
    aliases["appzone"] = ("zone", "APP_ZONE")
    aliases["service zone"] = ("zone", "SERVICE_ZONE")
    aliases["servicezone"] = ("zone", "SERVICE_ZONE")
    aliases["dmz"] = ("zone", "DMZ_ZONE")
    aliases["dmz zone"] = ("zone", "DMZ_ZONE")
    aliases["management zone"] = ("zone", "MGMT")

    return aliases


def extract_entities(alias_map: dict, question: str):
    """
    Detect assets, zones, and services mentioned in the question.
    Uses word-boundary matching to prevent false positives
    (e.g. 'plan' should not match 'lan' alias).
    Sorted longest-first to avoid partial matches.
    """
    nq = normalize_text(question)
    found_assets = []
    found_zones = []
    found_services = []

    for alias in sorted(alias_map.keys(), key=len, reverse=True):
        if not alias:
            continue
        # Word-boundary match: alias must appear as a whole word/phrase
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, nq):
            kind, canonical = alias_map[alias]
            if kind == "asset" and canonical not in found_assets:
                found_assets.append(canonical)
            elif kind == "zone" and canonical not in found_zones:
                found_zones.append(canonical)
            elif kind == "service" and canonical not in found_services:
                found_services.append(canonical)

    return found_assets, found_zones, found_services


def find_host_for_service(model: dict, service_name: str) -> str | None:
    """Given a service name like 'Vault', find which asset hosts it."""
    sn = service_name.lower()
    for asset in model.get("assets", []):
        # Check hosted_components
        for comp in asset.get("hosted_components", []):
            if sn in comp.lower():
                return asset["name"]
        # Check services list
        for svc in asset.get("services", []):
            if sn in svc.lower():
                return asset["name"]
    return None


# ════════════════════════════════════════════════════════════════
#  YAML Context Builders
# ════════════════════════════════════════════════════════════════

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
        for dep in item.get("depends_on", []):
            if norm_target in normalize_text(dep):
                results.append({
                    "asset": item.get("asset"),
                    "depends_on_entry": dep,
                })
    return results


def entry_mentions(entry: dict, name: str) -> bool:
    """Check if a YAML flow/blocked entry mentions a given name."""
    norm = normalize_text(name)
    fields = ["source", "destination", "service", "purpose", "flow"]
    return any(norm in normalize_text(str(entry.get(f, ""))) for f in fields)


def get_required_flows(model: dict, name: str):
    return [f for f in model.get("required_flows", []) if entry_mentions(f, name)]


def get_port_matrix(model: dict, name: str):
    return [p for p in model.get("port_protocol_matrix", []) if entry_mentions(p, name)]


def get_blocked_flows(model: dict, name: str):
    return [b for b in model.get("blocked_or_unnecessary_flows", []) if entry_mentions(b, name)]


def get_target_intent(model: dict, zone_name: str) -> dict:
    target = model.get("target_security_intent", {})
    return {
        "zone_intent": target.get("zone_intent", {}).get(zone_name, ""),
        "general": target.get("general", []),
        "identity_intent": target.get("identity_intent", []),
        "database_and_secret_intent": target.get("database_and_secret_intent", []),
        "proxy_and_egress_intent": target.get("proxy_and_egress_intent", []),
        "administrative_access_intent": target.get("administrative_access_intent", []),
    }


def get_open_questions(model: dict, zone_name: str | None = None) -> list:
    """
    Return open questions. If zone_name is provided, filter to relevant ones.
    Unlike v7, does NOT fall back to returning ALL questions if none match.
    """
    questions = model.get("open_questions", [])
    if not zone_name:
        return questions

    zn = normalize_text(zone_name)
    filtered = [q for q in questions if zn in normalize_text(q)]
    return filtered  # may be empty — that's fine


def build_asset_context(model: dict, asset_name: str) -> dict:
    asset = find_asset(model, asset_name)
    zone_name = asset.get("zone") if asset else None

    return {
        "asset": asset,
        "zone": find_zone(model, zone_name) if zone_name else None,
        "dependencies": get_dependencies(model, asset_name),
        "reverse_dependencies": get_reverse_dependencies(model, asset_name),
        "required_flows": get_required_flows(model, asset_name),
        "port_protocol_matrix": get_port_matrix(model, asset_name),
        "blocked_flows": get_blocked_flows(model, asset_name),
        "zone_target_intent": get_target_intent(model, zone_name) if zone_name else {},
        "open_questions": get_open_questions(model),
    }


def build_zone_context(model: dict, zone_name: str, include_dep_targets: bool = False) -> dict:
    """
    Build zone context. When include_dep_targets=True (used for transition_plan),
    also includes asset descriptions for dependency targets outside the zone,
    so the LLM understands what IAM01, DB01, etc. are.
    """
    zone = find_zone(model, zone_name)
    assets = get_assets_in_zone(model, zone_name)
    asset_names = [a["name"] for a in assets]

    zone_required_flows = []
    zone_port_matrix = []
    dep_target_names = set()

    for asset_name in asset_names:
        zone_required_flows.extend(get_required_flows(model, asset_name))
        zone_port_matrix.extend(get_port_matrix(model, asset_name))
        for dep in get_dependencies(model, asset_name):
            dep_target_names.add(dep)

    result = {
        "zone": zone,
        "assets_in_zone": assets,
        "required_flows": zone_required_flows,
        "port_protocol_matrix": zone_port_matrix,
        "blocked_flows": get_blocked_flows(model, zone_name),
        "target_intent": get_target_intent(model, zone_name),
        "open_questions": get_open_questions(model, zone_name),
    }

    # Include dependency target descriptions
    if include_dep_targets:
        dep_target_assets = []
        for dep_name in dep_target_names:
            # dep_name might be "Vault on DB01" — try exact match first, then partial
            asset = find_asset(model, dep_name)
            if not asset:
                # Try extracting host from "Service on Host" pattern
                m = re.search(r"on\s+(\S+)", dep_name)
                if m:
                    asset = find_asset(model, m.group(1))
            if asset and asset["name"] not in asset_names:
                if asset not in dep_target_assets:
                    dep_target_assets.append(asset)
        result["dependency_target_assets"] = dep_target_assets

    return result


def build_global_context(model: dict) -> dict:
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


# ════════════════════════════════════════════════════════════════
#  Dynamic Scaling
# ════════════════════════════════════════════════════════════════

def compute_rag_params(intents: set[str]) -> dict:
    """
    Determine top_k and max_chunks_for_prompt based on intent complexity.
    Complex multi-aspect questions get more context; simple lookups stay lean.
    """
    if "transition_plan" in intents:
        return {"top_k": 20, "max_chunks": 16}
    if "allow_list" in intents:
        return {"top_k": 15, "max_chunks": 12}
    if intents & {"required_flows", "blocked", "unresolved"}:
        return {"top_k": 12, "max_chunks": 10}
    return {"top_k": 10, "max_chunks": 8}


# ════════════════════════════════════════════════════════════════
#  RAG Integration
# ════════════════════════════════════════════════════════════════

def format_rag_chunks(chunks: list[tuple[int, dict]], max_chunks: int) -> list[dict]:
    """
    Format and trim RAG chunks for prompt inclusion.
    Preserves flow_assets metadata so the LLM can reason about connectivity.
    """
    formatted = []
    for score, chunk in chunks[:max_chunks]:
        entry = {
            "chunk_id": chunk.get("chunk_id"),
            "source_file": chunk.get("source_file"),
            "section_title": chunk.get("section_title"),
            "chunk_type": chunk.get("chunk_type"),
            "entities": chunk.get("entities", []),
            "zones": chunk.get("zones", []),
            "confidence_tags": chunk.get("confidence_tags", []),
            "text": chunk.get("text", "")[:1500],
        }
        # Include flow metadata when present
        flow_assets = chunk.get("flow_assets", [])
        if flow_assets:
            entry["flow_assets"] = flow_assets
        flow_src = chunk.get("flow_source")
        flow_dst = chunk.get("flow_destination")
        if flow_src and flow_dst:
            entry["flow_direction"] = f"{flow_src.get('raw', '?')} -> {flow_dst.get('raw', '?')}"

        formatted.append(entry)
    return formatted


# ════════════════════════════════════════════════════════════════
#  Context Assembly
# ════════════════════════════════════════════════════════════════

def build_context(model: dict, alias_map: dict, question: str) -> dict:
    """
    Build the full context for a question:
      1. Detect entities
      2. Retrieve RAG chunks (with intents + focus from retriever)
      3. Build YAML structured facts based on entity scope
      4. Assemble everything into a context dict
    """
    assets, zones, services = extract_entities(alias_map, question)

    # Resolve services to their hosting assets for YAML lookups
    service_hosts = {}
    for svc in services:
        host = find_host_for_service(model, svc)
        if host:
            service_hosts[svc] = host
            if host not in assets:
                assets.append(host)

    # Get RAG results WITH metadata (intents + focus)
    rag_params_preliminary = compute_rag_params(set())  # initial estimate
    rag_result = retrieve_with_metadata(question, top_k=15)
    intents = rag_result["intents"]
    focus = rag_result["focus"]

    # Now recompute with actual intents for proper scaling
    rag_params = compute_rag_params(intents)
    if rag_params["top_k"] > 15:
        rag_result = retrieve_with_metadata(question, top_k=rag_params["top_k"])

    rag_chunks = format_rag_chunks(
        rag_result["chunks"],
        max_chunks=rag_params["max_chunks"],
    )

    # ── Build structured YAML facts ──
    structured_facts = {}
    is_complex = bool(intents & {"transition_plan", "allow_list"})

    if "transition_plan" in intents and zones:
        # Full zone context with dependency target descriptions
        zone_name = zones[0]
        structured_facts["zone_context"] = build_zone_context(
            model, zone_name, include_dep_targets=True
        )
        # Also include blocked flows that mention the zone by name
        zone_blocked = get_blocked_flows(model, zone_name)
        # And blocked flows for each asset in the zone
        for asset_name in focus.get("zone_assets", []):
            zone_blocked.extend(get_blocked_flows(model, asset_name))
        # Deduplicate
        seen = set()
        deduped = []
        for b in zone_blocked:
            key = json.dumps(b, sort_keys=True)
            if key not in seen:
                seen.add(key)
                deduped.append(b)
        structured_facts["zone_context"]["blocked_flows"] = deduped

    elif assets and zones:
        structured_facts["assets_context"] = {
            name: build_asset_context(model, name) for name in assets
        }
        structured_facts["zones_context"] = {
            name: build_zone_context(model, name, include_dep_targets=is_complex)
            for name in zones
        }

    elif assets:
        structured_facts["assets_context"] = {
            name: build_asset_context(model, name) for name in assets
        }

    elif zones:
        structured_facts["zones_context"] = {
            name: build_zone_context(model, name, include_dep_targets=is_complex)
            for name in zones
        }

    else:
        structured_facts["global_context"] = build_global_context(model)

    return {
        "question": question,
        "intents": sorted(intents),
        "entities": {
            "assets": assets,
            "zones": zones,
            "services": services,
            "service_hosts": service_hosts,
        },
        "focus": {
            "zone_assets": focus.get("zone_assets", []),
            "dep_assets": focus.get("dep_assets", []),
        },
        "structured_facts": structured_facts,
        "rag_chunks": rag_chunks,
    }


# ════════════════════════════════════════════════════════════════
#  Prompt Building
# ════════════════════════════════════════════════════════════════

def build_prompt(context: dict) -> str:
    """
    Build the final LLM prompt from assembled context.
    The prompt gives the LLM:
      - the full intent set (not just one label)
      - YAML facts as primary source
      - RAG chunks as supporting context with flow metadata
      - clear answer rules ordered by priority
    """

    intents_str = ", ".join(context["intents"])
    entities_str = json.dumps(context["entities"], indent=2, ensure_ascii=False)
    focus_str = json.dumps(context["focus"], indent=2, ensure_ascii=False)
    yaml_str = json.dumps(context["structured_facts"], indent=2, ensure_ascii=False)
    rag_str = json.dumps(context["rag_chunks"], indent=2, ensure_ascii=False)

    return f"""You are a network-aware AI assistant for a documented homelab environment.

═══ YOUR ROLE ═══
Answer ONLY using the provided context. Do not invent facts. Do not use general cybersecurity assumptions beyond the provided context. If the context is insufficient, say so clearly.

═══ QUESTION ═══
{context["question"]}

═══ DETECTED INTENTS ═══
{intents_str}

These are the aspects the question requires you to address. For transition_plan, you must cover: required flows (allow list), flows to be blocked, target intent alignment, AND unresolved blockers.

═══ DETECTED ENTITIES ═══
{entities_str}

═══ FOCUS SET (assets the question is about) ═══
{focus_str}

═══ STRUCTURED YAML FACTS (primary source of truth) ═══
{yaml_str}

═══ RETRIEVED RAG CHUNKS (supporting context) ═══
{rag_str}

═══ ANSWER RULES (in priority order) ═══

1. START with a direct answer to the question.

2. YAML facts are the primary source of truth. If YAML and a RAG chunk conflict, YAML wins.

3. For allow-list or transition-plan questions, organize your answer in this order:
   a. REQUIRED FLOWS that must remain — use exact port/protocol from port_protocol_matrix first
   b. BROAD TRUST that should be removed — from blocked_or_unnecessary_flows
   c. TARGET INTENT — what the final design should look like
   d. UNRESOLVED BLOCKERS — open questions that must be answered before enforcement
   e. LOCAL-ONLY FLOWS — host-internal flows that are not inter-host firewall rules

4. For each flow or fact, clearly indicate its certainty level:
   - "Confirmed" — observed or code-verified
   - "Owner-confirmed" — declared by the owner
   - "Standard default declared by owner" — accepted but not independently verified
   - "Open question" — not yet resolved

5. NEVER treat current broad firewall access as permanently justified.
   Current broad access ≠ final intended design.

6. If a port/protocol is documented in the YAML port_protocol_matrix, do NOT say it is undocumented.

7. If something is local-only (e.g. Nginx → local portal process on the same host), state that clearly — it does not need an inter-host firewall rule.

8. If multiple assets or zones are involved, address each one separately.

9. If the question is broader than the documented model supports, state the limitation.

10. Keep the answer practical, structured, and concise. Use clear section headings.
"""


# ════════════════════════════════════════════════════════════════
#  Main Answer Pipeline
# ════════════════════════════════════════════════════════════════

def answer_question(model: dict, alias_map: dict, question: str):
    """
    Full pipeline: question → context → prompt → LLM → answer.
    Returns: (answer, prompt, context)
    """
    context = build_context(model, alias_map, question)
    prompt = build_prompt(context)
    answer = real_llm_response(prompt)
    return answer, prompt, context


def main():
    model = load_model()
    alias_map = build_alias_map(model)

    print("Network AI Agent v8 (Hybrid YAML + RAG + LLM)")
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
                print("\n--- ENTITIES ---")
                print(json.dumps(context["entities"], indent=2, ensure_ascii=False))
                print("\n--- FOCUS ---")
                print(json.dumps(context["focus"], indent=2, ensure_ascii=False))
                print(f"\n--- RAG CHUNKS ({len(context['rag_chunks'])}) ---")
                for c in context["rag_chunks"]:
                    print(f"  {c['chunk_id']}: {c['chunk_type']:15s} | {c['section_title'][:50]}")
                print("\n--- STRUCTURED FACTS KEYS ---")
                for key in context["structured_facts"]:
                    val = context["structured_facts"][key]
                    if isinstance(val, dict):
                        print(f"  {key}: {{ {', '.join(val.keys())} }}")
                    else:
                        print(f"  {key}: {type(val).__name__}")
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
