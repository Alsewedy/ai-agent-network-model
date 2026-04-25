"""
retrieve_chunks_v2.py – Advanced connectivity-aware retriever for the new network knowledge architecture.

Key design goals:
  1. Use model.yaml from the new knowledge structure.
  2. Build focus from detected entities and scope units.
  3. Expand from scope units to their entities, then to dependency targets.
  4. Score chunks using entity connectivity, scope relevance, and intent-aware weighting.
  5. Return both retrieved chunks and metadata (intents + focus) for advanced agents.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.json"
MODEL_FILE = PROJECT_ROOT / "knowledge" / "domains" / "network" / "model.yaml"


INTENT_KEYWORDS = {
    "transition_plan": [
        "transition plan", "least privilege transition plan", "least-privilege transition plan",
        "hardening plan", "tighten", "final design", "final intended design",
    ],
    "required_flows": [
        "required flow", "required flows", "required communication",
        "must remain open", "must remain", "keep working", "allow list",
    ],
    "technical_details": [
        "port", "ports", "protocol", "protocols", "endpoint", "technical",
    ],
    "overly_broad_access": [
        "broad access", "too open", "overly broad", "unnecessary access",
        "should not remain broad", "broader than intended",
    ],
    "target_posture": [
        "target posture", "intended posture", "target intent", "final design", "intended",
    ],
    "uncertainty": [
        "unresolved", "open question", "open questions", "not fully confirmed",
        "uncertain", "needs confirmation", "assumption", "blocker",
    ],
    "dependencies": [
        "depend", "dependencies", "depends on", "rely on",
    ],
    "standards_comparison": [
        "standard", "standards", "policy", "least privilege",
        "segmentation", "boundary protection", "control expectations",
    ],
    "external_guidance": [
        "best practice", "external guidance", "outside my kb", "not in my files",
    ],
}

LOW_VALUE_TYPES = {"scope_units", "services", "evidence_notes"}
FILLER_TITLE_PATTERNS = [
    "document introduction", "purpose", "modeling rule", "notes",
]


# ──────────────────────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────────────────────

def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model():
    with open(MODEL_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Expected model.yaml root to be a dictionary, got: {type(data)}")

    return data


# ──────────────────────────────────────────────────────────────
# Normalization
# ──────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("→", " ")
    text = text.replace("->", " ")
    text = text.replace("/", " / ")
    text = re.sub(r"[^a-z0-9\s/_-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> set[str]:
    return set(normalize(text).split())


# ──────────────────────────────────────────────────────────────
# Model-aware aliases / detection
# ──────────────────────────────────────────────────────────────

def build_entity_aliases(model: dict) -> dict[str, str]:
    aliases = {}

    for entity in model.get("entities", []):
        name = entity.get("name")
        if not name:
            continue

        aliases[normalize(name)] = name

        if name == "DC01-CYBERAUDIT":
            aliases["dc01"] = name
            aliases["domain controller"] = name

        if name == "Admin laptop":
            aliases["laptop"] = name
            aliases["admin laptop"] = name

        if name == "Switch Management":
            aliases["switch"] = name
            aliases["switch management"] = name

        if name == "PROXY01":
            aliases["proxy"] = name
            aliases["proxy01"] = name

        if name == "IAM01":
            aliases["iam"] = name
            aliases["iam01"] = name

        if name == "DB01":
            aliases["db"] = name
            aliases["db01"] = name

    aliases["vault"] = "Vault"
    aliases["internal api"] = "Internal API"
    aliases["keycloak"] = "Keycloak"
    aliases["mariadb"] = "MariaDB"
    aliases["dns"] = "DNS"
    aliases["ntp"] = "NTP"

    return aliases


def build_scope_unit_aliases(model: dict) -> dict[str, str]:
    aliases = {}

    for unit in model.get("scope_units", []):
        name = unit.get("name")
        if not name:
            continue

        aliases[normalize(name)] = name

        if name == "LAN":
            aliases["lan"] = name
        if name == "APP_ZONE":
            aliases["app zone"] = name
            aliases["appzone"] = name
        if name == "SERVICE_ZONE":
            aliases["service zone"] = name
            aliases["servicezone"] = name
        if name == "DMZ_ZONE":
            aliases["dmz"] = name
            aliases["dmz zone"] = name
        if name == "MGMT_SEGMENT":
            aliases["mgmt"] = name
            aliases["management segment"] = name
        if name == "ADMIN_SEGMENT":
            aliases["admin segment"] = name
        if name == "EMPLOYEE_SEGMENT":
            aliases["employee segment"] = name
        if name == "GUEST_SEGMENT":
            aliases["guest segment"] = name
        if name == "WAN":
            aliases["wan"] = name

    return aliases


def detect_entities_and_scope_units(model: dict, question: str):
    q = normalize(question)
    entity_aliases = build_entity_aliases(model)
    scope_aliases = build_scope_unit_aliases(model)

    entities = []
    scope_units = []

    for alias, canonical in sorted(entity_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, q) and canonical not in entities:
            entities.append(canonical)

    for alias, canonical in sorted(scope_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, q) and canonical not in scope_units:
            scope_units.append(canonical)

    return entities, scope_units


def expand_from_scope_units(model: dict, entities: list[str], scope_units: list[str]) -> list[str]:
    expanded = list(entities)

    for unit in model.get("scope_units", []):
        if unit.get("name") in scope_units:
            for entity_name in unit.get("entities", []) or []:
                if entity_name not in expanded:
                    expanded.append(entity_name)

    return expanded


def expand_from_dependencies(model: dict, entities: list[str]) -> list[str]:
    dep_entities = []

    for dep_entry in model.get("dependencies", []):
        if dep_entry.get("entity") in entities:
            for dep in dep_entry.get("depends_on", []):
                if dep not in entities and dep not in dep_entities:
                    dep_entities.append(dep)

    return dep_entities


def build_focus_set(model: dict, question: str) -> dict:
    direct_entities, scope_units = detect_entities_and_scope_units(model, question)
    scope_expanded_entities = expand_from_scope_units(model, direct_entities, scope_units)
    dep_entities = expand_from_dependencies(model, scope_expanded_entities)

    all_entities = list(scope_expanded_entities)
    for entity_name in dep_entities:
        if entity_name not in all_entities:
            all_entities.append(entity_name)

    return {
        "direct_entities": direct_entities,
        "scope_expanded_entities": scope_expanded_entities,
        "dep_entities": dep_entities,
        "all_entities": all_entities,
        "scope_units": scope_units,
    }


# ──────────────────────────────────────────────────────────────
# Intent detection
# ──────────────────────────────────────────────────────────────

def detect_intents(question: str) -> set[str]:
    q = normalize(question)
    found = set()

    for intent, patterns in INTENT_KEYWORDS.items():
        for pattern in patterns:
            if normalize(pattern) in q:
                found.add(intent)
                break

    if "transition_plan" in found:
        found.update({
            "required_flows",
            "technical_details",
            "overly_broad_access",
            "target_posture",
            "uncertainty",
        })

    if "required_flows" in found:
        found.add("technical_details")

    return found


# ──────────────────────────────────────────────────────────────
# Flow connectivity helpers
# ──────────────────────────────────────────────────────────────

def chunk_touches_entities(chunk: dict, entity_set: set[str]) -> set[str]:
    flow_entities = chunk.get("flow_entities", [])
    if flow_entities:
        return set(flow_entities) & entity_set

    return set(chunk.get("entities", [])) & entity_set


def chunk_touches_scope_units(chunk: dict, scope_unit_set: set[str]) -> set[str]:
    flow_scope_units = chunk.get("flow_scope_units", [])
    if flow_scope_units:
        return set(flow_scope_units) & scope_unit_set

    return set(chunk.get("scope_units", [])) & scope_unit_set


def chunk_flow_pair(chunk: dict) -> tuple[str, str] | None:
    src = chunk.get("flow_source")
    dst = chunk.get("flow_destination")
    if src and dst:
        s = src.get("raw", "")
        d = dst.get("raw", "")
        if s and d:
            return (normalize(s), normalize(d))
    return None


# ──────────────────────────────────────────────────────────────
# Dynamic scaling
# ──────────────────────────────────────────────────────────────

def compute_rag_params(intents: set[str]) -> dict:
    if "transition_plan" in intents:
        return {"top_k": 20, "max_chunks": 14}
    if "standards_comparison" in intents or "overly_broad_access" in intents:
        return {"top_k": 14, "max_chunks": 10}
    if "technical_details" in intents or "required_flows" in intents:
        return {"top_k": 12, "max_chunks": 10}
    return {"top_k": 10, "max_chunks": 8}


# ──────────────────────────────────────────────────────────────
# Scoring
# ──────────────────────────────────────────────────────────────

def score_chunk(question: str, chunk: dict, focus: dict, intents: set[str]) -> dict:
    breakdown = defaultdict(int)
    q_tokens = tokenize(question)

    chunk_type = chunk.get("chunk_type", "general")
    section_title = normalize(chunk.get("section_title", ""))
    chunk_text_norm = normalize(chunk.get("text", ""))

    focus_entity_set = set(focus["all_entities"])
    focus_scope_set = set(focus["scope_units"])
    scope_expanded_entity_set = set(focus["scope_expanded_entities"])

    # 1) token overlap
    chunk_tokens = tokenize(chunk.get("text", ""))
    overlap = len(q_tokens & chunk_tokens)
    breakdown["token_overlap"] = overlap * 1

    # 2) title match
    title_hits = sum(1 for t in q_tokens if len(t) > 2 and t in section_title)
    breakdown["title_match"] = title_hits * 3

    # 3) entity connectivity
    touching_entities = chunk_touches_entities(chunk, focus_entity_set)
    touching_scope_entities = chunk_touches_entities(chunk, scope_expanded_entity_set)
    touching_scope_units = chunk_touches_scope_units(chunk, focus_scope_set)

    if touching_entities:
        breakdown["entity_connectivity"] = len(touching_entities) * 12

    if len(touching_scope_entities) >= 1 and len(touching_entities) >= 2:
        breakdown["cross_entity_flow"] = 15

    # 4) scope-unit relevance
    if touching_scope_units:
        breakdown["scope_unit_match"] = len(touching_scope_units) * 10

    # 5) intent-type alignment
    intent_type_map = {
        "technical_matrix": {"technical_details", "required_flows", "transition_plan"},
        "required_flows": {"required_flows", "transition_plan"},
        "unnecessary_access": {"overly_broad_access", "transition_plan"},
        "target_intent": {"target_posture", "standards_comparison", "transition_plan"},
        "open_questions": {"uncertainty", "transition_plan"},
        "dependencies": {"dependencies"},
    }

    for ctype, relevant_intents in intent_type_map.items():
        if chunk_type == ctype and (intents & relevant_intents):
            breakdown["intent_type_match"] = 20
            break

    # 6) communication-heavy bonuses
    if chunk_type == "technical_matrix":
        if touching_scope_entities:
            breakdown["tm_scope_entity"] = 18

        is_infra = any(kw in section_title for kw in ["dns", "time", "ntp"])
        if touching_scope_entities and not is_infra:
            breakdown["tm_service_flow"] = 10

        conf_tags = [normalize(t) for t in chunk.get("confidence_tags", [])]
        if any("owner" in t or "default" in t for t in conf_tags):
            if intents & {"transition_plan", "required_flows"}:
                breakdown["tm_owner_default_penalty"] = -8

    if chunk_type == "required_flows":
        if touching_scope_entities and intents & {"transition_plan", "required_flows"}:
            breakdown["rf_scope_relevance"] = 12

    if chunk_type == "unnecessary_access":
        if touching_scope_entities or touching_scope_units:
            if intents & {"transition_plan", "overly_broad_access"}:
                breakdown["ua_focus_relevance"] = 14

        if "target state" in chunk_text_norm or "should remain broad" in chunk_text_norm:
            if "transition_plan" in intents:
                breakdown["ua_target_state"] = 8

    # 7) open questions relevance
    if chunk_type == "open_questions" and "uncertainty" in intents:
        oq_signals = [
            "open question", "unresolved", "assumption",
            "not fully confirmed", "needs confirmation", "blocker"
        ]
        if any(signal in chunk_text_norm for signal in oq_signals):
            breakdown["oq_signal"] = 12
            if touching_scope_entities or touching_scope_units:
                breakdown["oq_focus_relevance"] = 10
        else:
            breakdown["oq_no_signal_penalty"] = -15

    # 8) target intent relevance
    if chunk_type == "target_intent":
        ti_signals = ["target intent", "final design", "least privilege", "restricted"]
        if any(signal in section_title or signal in chunk_text_norm for signal in ti_signals):
            breakdown["ti_signal"] = 8
        if touching_scope_units:
            breakdown["ti_scope_match"] = 12

    # 9) filler penalties
    is_filler_title = any(pattern in section_title for pattern in FILLER_TITLE_PATTERNS)
    if is_filler_title:
        breakdown["filler_title_penalty"] = -20

    if chunk_type in LOW_VALUE_TYPES and intents & {
        "transition_plan", "required_flows", "technical_details", "uncertainty"
    }:
        breakdown["low_value_type_penalty"] = -12

    total = max(sum(breakdown.values()), 0)
    return {"total": total, "breakdown": dict(breakdown)}


# ──────────────────────────────────────────────────────────────
# Dynamic quotas / selection
# ──────────────────────────────────────────────────────────────

def compute_dynamic_quotas(intents: set[str], n_relevant_flows: int) -> dict:
    minimums = {
        "technical_matrix": 2,
        "required_flows": 2,
        "unnecessary_access": 1,
        "target_intent": 1,
        "open_questions": 0,
        "dependencies": 0,
    }

    maximums = {
        "technical_matrix": 4,
        "required_flows": 3,
        "unnecessary_access": 2,
        "target_intent": 2,
        "open_questions": 1,
        "dependencies": 1,
    }

    if "transition_plan" in intents:
        maximums["technical_matrix"] = max(12, n_relevant_flows)
        maximums["required_flows"] = 5
        maximums["unnecessary_access"] = 4
        maximums["target_intent"] = 3
        minimums["unnecessary_access"] = 2
        minimums["target_intent"] = 1

    if "uncertainty" in intents:
        minimums["open_questions"] = 2
        maximums["open_questions"] = 4

    if "required_flows" in intents and "transition_plan" not in intents:
        maximums["technical_matrix"] = max(8, n_relevant_flows)
        maximums["required_flows"] = 4

    if "dependencies" in intents:
        minimums["dependencies"] = 1
        maximums["dependencies"] = 3

    return {"minimums": minimums, "maximums": maximums}


def select_with_coverage(
    scored_chunks: list[tuple[int, dict, dict]],
    intents: set[str],
    focus: dict,
    top_k: int = 10,
) -> list[tuple[int, dict]]:
    focus_set = set(focus["all_entities"])
    n_relevant_flows = sum(
        1 for _, chunk, _ in scored_chunks
        if chunk.get("chunk_type") in ("technical_matrix", "required_flows")
        and chunk_touches_entities(chunk, focus_set)
    )

    quotas = compute_dynamic_quotas(intents, n_relevant_flows)
    minimums = quotas["minimums"]
    maximums = quotas["maximums"]

    selected = []
    used_ids = set()
    type_counts = defaultdict(int)
    covered_pairs_by_type = defaultdict(set)

    def can_add(chunk):
        chunk_id = chunk["chunk_id"]
        chunk_type = chunk.get("chunk_type", "general")

        if chunk_id in used_ids:
            return False

        if type_counts[chunk_type] >= maximums.get(chunk_type, top_k):
            return False

        return True

    def do_add(score, chunk):
        chunk_id = chunk["chunk_id"]
        chunk_type = chunk.get("chunk_type", "general")

        selected.append((score, chunk))
        used_ids.add(chunk_id)
        type_counts[chunk_type] += 1

        pair = chunk_flow_pair(chunk)
        if pair:
            covered_pairs_by_type[chunk_type].add(pair)

    if intents & {"transition_plan", "required_flows"}:
        min_order = ["technical_matrix", "required_flows", "unnecessary_access", "target_intent", "open_questions", "dependencies"]
    else:
        min_order = list(minimums.keys())

    # Pass 1: minimums
    for chunk_type in min_order:
        min_count = minimums.get(chunk_type, 0)
        if min_count <= 0:
            continue

        count = 0
        for score, chunk, _ in scored_chunks:
            if count >= min_count:
                break

            if chunk.get("chunk_type") == chunk_type and can_add(chunk):
                do_add(score, chunk)
                count += 1

    # Pass 2: expand technical_matrix coverage first
    if intents & {"transition_plan", "required_flows", "technical_details"}:
        for score, chunk, _ in scored_chunks:
            if len(selected) >= top_k:
                break

            if chunk.get("chunk_type") != "technical_matrix":
                continue
            if not can_add(chunk):
                continue

            pair = chunk_flow_pair(chunk)
            if pair and pair not in covered_pairs_by_type.get("technical_matrix", set()):
                if chunk_touches_entities(chunk, focus_set):
                    do_add(score, chunk)

    # Pass 3: expand required_flows coverage second
    if intents & {"transition_plan", "required_flows"}:
        for score, chunk, _ in scored_chunks:
            if len(selected) >= top_k:
                break

            if chunk.get("chunk_type") != "required_flows":
                continue
            if not can_add(chunk):
                continue

            pair = chunk_flow_pair(chunk)
            if pair and pair not in covered_pairs_by_type.get("technical_matrix", set()):
                if chunk_touches_entities(chunk, focus_set):
                    do_add(score, chunk)

    # Pass 4: fill by score
    for score, chunk, _ in scored_chunks:
        if len(selected) >= top_k:
            break

        if can_add(chunk):
            do_add(score, chunk)

    selected.sort(key=lambda x: x[0], reverse=True)
    return selected[:top_k]


# ──────────────────────────────────────────────────────────────
# Main retrieval pipelines
# ──────────────────────────────────────────────────────────────

def retrieve_top_chunks(question: str, top_k: int = 10, debug: bool = False):
    chunks = load_chunks()
    model = load_model()

    intents = detect_intents(question)
    focus = build_focus_set(model, question)

    scored = []
    for chunk in chunks:
        result = score_chunk(question, chunk, focus, intents)
        if result["total"] > 0:
            scored.append((result["total"], chunk, result["breakdown"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = select_with_coverage(scored, intents, focus, top_k=top_k)

    if debug:
        print(f"Intents: {intents}")
        print(
            f"Focus: scope_units={focus['scope_units']}, "
            f"scope_expanded_entities={focus['scope_expanded_entities']}, "
            f"dep_entities={focus['dep_entities']}"
        )
        print(f"Scored chunks: {len(scored)}")

    return results


def retrieve_with_metadata(question: str, top_k: int = 10):
    chunks = load_chunks()
    model = load_model()

    intents = detect_intents(question)
    focus = build_focus_set(model, question)

    # Let internal dynamic policy raise top_k when needed, but never lower caller intent.
    rag_params = compute_rag_params(intents)
    effective_top_k = max(top_k, rag_params["top_k"])

    scored = []
    for chunk in chunks:
        result = score_chunk(question, chunk, focus, intents)
        if result["total"] > 0:
            scored.append((result["total"], chunk, result["breakdown"]))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = select_with_coverage(scored, intents, focus, top_k=effective_top_k)

    return {
        "chunks": results,
        "intents": intents,
        "focus": focus,
    }


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def main():
    print("RAG Retriever v2 (advanced, new knowledge architecture)")
    print("Type a question, or 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        results = retrieve_top_chunks(question, top_k=15, debug=True)

        if not results:
            print("\nNo relevant chunks found.\n")
            continue

        print(f"\nTop retrieved chunks ({len(results)}):\n")
        for i, (score, chunk) in enumerate(results, start=1):
            print(f"[{i}] score={score}")
            print(f"    chunk_id: {chunk['chunk_id']}")
            print(f"    source_file: {chunk['source_file']}")
            print(f"    section_title: {chunk['section_title']}")
            print(f"    chunk_type: {chunk['chunk_type']}")
            print(f"    entities: {chunk.get('entities', [])}")
            print(f"    scope_units: {chunk.get('scope_units', [])}")
            print(f"    flow_entities: {chunk.get('flow_entities', [])}")
            print(f"    flow_scope_units: {chunk.get('flow_scope_units', [])}")
            print(f"    text preview: {chunk['text'][:300]}")
            print("-" * 60)


if __name__ == "__main__":
    main()