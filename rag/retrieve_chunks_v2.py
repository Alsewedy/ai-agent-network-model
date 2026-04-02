"""
retrieve_chunks_v2.py – Connectivity-aware RAG retriever for network hardening questions.

Key design changes from v1:
  1. ENTITY-GRAPH EXPANSION: When a zone is mentioned, expand to all assets in
     that zone, then use flow_assets metadata to find all flow chunks touching
     those assets.
  2. CONNECTIVITY SCORING: Flow chunks are scored by how many focus assets they
     connect, with bonus for covering asset pairs not yet in the result set.
  3. DYNAMIC QUOTAS: For complex intents such as transition_plan, port_matrix
     and flow quotas scale with the number of relevant flows.
  4. COVERAGE-AWARE SELECTION: The selector tracks which asset pairs are already
     covered and prioritizes chunks that add new coverage.
  5. OPEN QUESTION RELEVANCE: For unresolved intents, open_questions chunks are
     scored by textual overlap with the question's zone and asset focus.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "rag" / "chunks.json"
YAML_FILE = PROJECT_ROOT / "knowledge" / "network_domain" / "08_structured_network_model.yaml"


KNOWN_ASSETS = [
    "APP01", "APP02", "IAM01", "DB01", "DC01-CYBERAUDIT",
    "PROXY01", "Firewall01", "ESXi", "Switch Management",
    "Admin laptop", "Vault", "Internal API", "Keycloak",
]

KNOWN_ZONES = [
    "WAN", "LAN / DATA", "APP_ZONE", "DMZ_ZONE",
    "SERVICE_ZONE", "MGMT", "ADMIN", "EMPLOYEE", "GUEST",
]

# Intents and their trigger phrases
INTENT_KEYWORDS = {
    "transition_plan": [
        "transition plan", "least-privilege transition plan",
        "final least-privilege transition plan", "hardening plan",
        "tighten", "final design", "final intended design",
    ],
    "allow_list": [
        "allow list", "least privilege allow list", "least privilege",
        "must remain open", "keep open", "required access",
    ],
    "ports_protocols": ["port", "ports", "protocol", "protocols"],
    "blocked": [
        "broad access", "broad trust", "remove", "should be removed",
        "should not remain", "blocked",
    ],
    "unresolved": [
        "unresolved", "open question", "open questions",
        "not fully confirmed", "needs confirmation",
        "block final firewall hardening", "block final enforcement",
        "still needs confirmation", "blocker", "blockers",
    ],
    "target_intent": [
        "target intent", "target security intent",
        "aligned", "final intended design",
    ],
    "dependencies": [
        "depend", "dependencies", "rely on", "depends on",
    ],
    "required_flows": [
        "required flow", "required flows", "must remain",
        "normal operation", "keep working",
        "must remain for", "flows that must remain",
    ],
    "local_only": [
        "local-only", "local only", "host-internal", "host internal",
        "not inter-host", "inter-host firewall rules", "local portal process",
    ],
    "owner_declared": [
        "owner-declared", "owner declared",
        "owner-confirmed", "owner confirmed", "defaults",
    ],
}

# Chunk types that are considered low-value filler for complex queries
LOW_VALUE_TYPES = {"zones_assets", "services", "evidence"}

# Section titles that indicate filler content
FILLER_TITLE_PATTERNS = [
    "document introduction", "purpose", "main assets by zone", "notes",
]


# ─── Normalization ───────────────────────────────────────────────

def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("->", " ")
    text = text.replace("/", " / ")
    text = re.sub(r"[^a-z0-9\s/_-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> set[str]:
    return set(normalize(text).split())


# ─── Loading ─────────────────────────────────────────────────────

def load_chunks():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─── Intent detection ────────────────────────────────────────────

def detect_intents(question: str) -> set[str]:
    q = normalize(question)
    found = set()
    for intent, patterns in INTENT_KEYWORDS.items():
        for p in patterns:
            if normalize(p) in q:
                found.add(intent)
                break

    # Derived expansions
    if "transition_plan" in found:
        found.update({
            "allow_list", "blocked", "target_intent",
            "required_flows", "unresolved", "ports_protocols",
        })
    if "allow_list" in found:
        found.update({"ports_protocols", "required_flows"})
    return found


# ─── Entity/zone detection and expansion ─────────────────────────

def detect_assets_and_zones(question: str):
    q = normalize(question)
    assets = [a for a in KNOWN_ASSETS if normalize(a) in q]
    zones = [z for z in KNOWN_ZONES if normalize(z) in q]
    return assets, zones


def expand_from_zones(model: dict, assets: list[str], zones: list[str]):
    """Expand zone mentions into their member assets."""
    expanded_assets = list(assets)
    for zone in model.get("zones", []):
        if zone.get("name") in zones:
            for asset_name in zone.get("assets", []):
                if asset_name not in expanded_assets:
                    expanded_assets.append(asset_name)
    return expanded_assets


def expand_from_dependencies(model: dict, assets: list[str]) -> list[str]:
    """
    For each focus asset, find what it depends on from the YAML dependency graph.
    Returns: list of additional assets that are dependency targets.
    """
    dep_assets = []
    for dep_entry in model.get("dependencies", []):
        if dep_entry.get("asset") in assets:
            for d in dep_entry.get("depends_on", []):
                name = d.get("name", d) if isinstance(d, dict) else d
                if name not in assets and name not in dep_assets:
                    dep_assets.append(name)
    return dep_assets


def build_focus_set(model: dict, question: str) -> dict:
    """
    Build a complete focus set from the question.
    Returns: {
        "direct_assets": [...],     # explicitly mentioned
        "zone_assets": [...],       # expanded from zones
        "dep_assets": [...],        # dependency targets
        "all_assets": [...],        # union
        "zones": [...],
    }
    """
    direct_assets, zones = detect_assets_and_zones(question)
    zone_assets = expand_from_zones(model, direct_assets, zones)
    # zone_assets already includes direct_assets
    dep_assets = expand_from_dependencies(model, zone_assets)

    all_assets = list(zone_assets)
    for a in dep_assets:
        if a not in all_assets:
            all_assets.append(a)

    return {
        "direct_assets": direct_assets,
        "zone_assets": zone_assets,
        "dep_assets": dep_assets,
        "all_assets": all_assets,
        "zones": zones,
    }


# ─── Flow-graph connectivity ────────────────────────────────────

def chunk_touches_assets(chunk: dict, asset_set: set[str]) -> set[str]:
    """
    Return which focus assets this chunk's flow_assets overlap with.
    Uses flow_assets metadata if it exists in the chunk data.
    Falls back to entity matching if flow_assets is empty.
    """
    flow_assets = chunk.get("flow_assets", [])
    if flow_assets:
        return set(flow_assets) & asset_set

    # Fallback: entity matching
    return set(chunk.get("entities", [])) & asset_set


def chunk_flow_pair(chunk: dict) -> tuple[str, str] | None:
    """
    Extract a (source, destination) pair for coverage tracking.
    Returns a normalized tuple or None.
    """
    src = chunk.get("flow_source")
    dst = chunk.get("flow_destination")
    if src and dst:
        s = src.get("raw", "")
        d = dst.get("raw", "")
        if s and d:
            return (normalize(s), normalize(d))
    return None


# ─── Scoring ─────────────────────────────────────────────────────

def score_chunk(
    question: str,
    chunk: dict,
    focus: dict,
    intents: set[str],
) -> dict:
    """
    Score a chunk and return a breakdown dict for debuggability.
    Returns: {"total": int, "breakdown": {category: points}}
    """
    breakdown = defaultdict(int)
    q_norm = normalize(question)
    q_tokens = tokenize(question)

    chunk_type = chunk.get("chunk_type", "general")
    section_title = normalize(chunk.get("section_title", ""))
    chunk_text_norm = normalize(chunk.get("text", ""))
    entities = set(chunk.get("entities", []))
    zones = set(chunk.get("zones", []))

    focus_asset_set = set(focus["all_assets"])
    zone_asset_set = set(focus["zone_assets"])

    # ── 1. TOKEN OVERLAP (low weight, tiebreaker) ──
    chunk_tokens = tokenize(chunk.get("text", ""))
    overlap = len(q_tokens & chunk_tokens)
    breakdown["token_overlap"] = overlap * 1

    # ── 2. TITLE MATCH ──
    title_hits = sum(1 for t in q_tokens if t in section_title and len(t) > 2)
    breakdown["title_match"] = title_hits * 3

    # ── 3. ENTITY CONNECTIVITY (the core improvement) ──
    # How many focus assets does this chunk connect to?
    touching = chunk_touches_assets(chunk, focus_asset_set)
    zone_touching = chunk_touches_assets(chunk, zone_asset_set)

    if touching:
        breakdown["entity_connectivity"] = len(touching) * 12

    # Bonus: chunk connects a zone-level focus asset (APP01/APP02) to a dep target
    if len(zone_touching) >= 1 and len(touching) >= 2:
        breakdown["cross_zone_flow"] = 15

    # ── 4. ZONE MATCH ──
    zone_hits = set(focus["zones"]) & zones
    if zone_hits:
        breakdown["zone_match"] = len(zone_hits) * 10

    # ── 5. INTENT-TO-TYPE ALIGNMENT ──
    intent_type_map = {
        "port_matrix":    {"ports_protocols", "allow_list", "transition_plan", "required_flows"},
        "flows":          {"required_flows", "allow_list", "transition_plan"},
        "blocked_flows":  {"blocked", "transition_plan"},
        "target_intent":  {"target_intent", "transition_plan"},
        "open_questions": {"unresolved"},
        "dependencies":   {"dependencies"},
    }
    for ctype, relevant_intents in intent_type_map.items():
        if chunk_type == ctype and (intents & relevant_intents):
            breakdown["intent_type_match"] = 20
            break

    # ── 6. FLOW-SPECIFIC BONUSES ──
    if chunk_type == "port_matrix":
        # Core application flow: any chunk whose flow touches a zone asset
        if zone_touching:
            breakdown["pm_zone_asset"] = 18

        # Service flow (not DNS/NTP infrastructure)
        is_infra = any(kw in section_title for kw in ["dns", "time", "ntp"])
        if zone_touching and not is_infra:
            breakdown["pm_service_flow"] = 10

        # Owner-default penalty for transition plans
        conf_tags = [normalize(t) for t in chunk.get("confidence_tags", [])]
        if any("owner" in t or "default" in t for t in conf_tags):
            if intents & {"transition_plan", "allow_list"}:
                breakdown["pm_owner_default_penalty"] = -8

    if chunk_type == "flows":
        if zone_touching and intents & {"transition_plan", "allow_list", "required_flows"}:
            breakdown["flow_zone_relevance"] = 12

    if chunk_type == "blocked_flows":
        if zone_touching and intents & {"transition_plan", "blocked"}:
            breakdown["blocked_zone_relevance"] = 14
        if "target state" in chunk_text_norm or "should remain broad" in chunk_text_norm:
            if "transition_plan" in intents:
                breakdown["blocked_target_state"] = 8

    # ── 7. OPEN QUESTIONS RELEVANCE ──
    if chunk_type == "open_questions":
        if "unresolved" in intents:
            # Reward chunks that actually contain open question content
            oq_signals = ["open question", "unresolved", "assumption",
                          "not fully confirmed", "block", "needs confirmation"]
            if any(s in chunk_text_norm for s in oq_signals):
                breakdown["oq_signal"] = 12

                # Extra: does this open question mention focus zones/assets?
                if zone_touching or (set(focus["zones"]) & zones):
                    breakdown["oq_focus_relevance"] = 10
            else:
                # Confirmed facts section inside open_questions file → low value
                breakdown["oq_no_signal_penalty"] = -15

    # ── 8. TARGET INTENT RELEVANCE ──
    if chunk_type == "target_intent":
        ti_signals = ["target intent", "final model", "final design",
                      "least privilege", "restricted"]
        if any(s in section_title or s in chunk_text_norm for s in ti_signals):
            breakdown["ti_signal"] = 8
        # Does target intent chunk mention focus zones?
        if set(focus["zones"]) & zones:
            breakdown["ti_zone_match"] = 12

    # ── 9. FILLER PENALTIES ──
    is_filler_title = any(p in section_title for p in FILLER_TITLE_PATTERNS)
    if is_filler_title:
        breakdown["filler_title_penalty"] = -20

    if chunk_type in LOW_VALUE_TYPES and intents & {
        "transition_plan", "allow_list", "ports_protocols", "unresolved"
    }:
        breakdown["low_value_type_penalty"] = -12

    total = max(sum(breakdown.values()), 0)
    return {"total": total, "breakdown": dict(breakdown)}


# ─── Coverage-aware selection ────────────────────────────────────

def compute_dynamic_quotas(intents: set[str], n_relevant_flows: int) -> dict:
    """
    Compute per-type quotas that scale with the question's complexity.

    For transition_plan questions, the port_matrix quota scales with
    the number of relevant flows instead of staying at a small fixed cap.
    """
    # Base minimums: ensure at least this many per type if available
    minimums = {
        "port_matrix": 2,
        "flows": 2,
        "blocked_flows": 1,
        "target_intent": 1,
        "open_questions": 0,
        "dependencies": 0,
    }

    # Maximums: hard caps per type (out of top_k)
    maximums = {
        "port_matrix": 4,
        "flows": 3,
        "blocked_flows": 2,
        "target_intent": 2,
        "open_questions": 1,
        "dependencies": 1,
    }

    if "transition_plan" in intents:
        # Scale port_matrix to cover most relevant flows
        maximums["port_matrix"] = max(12, n_relevant_flows)
        maximums["flows"] = 5
        maximums["blocked_flows"] = 4
        maximums["target_intent"] = 3
        minimums["blocked_flows"] = 2
        minimums["target_intent"] = 1

    if "unresolved" in intents:
        minimums["open_questions"] = 2
        maximums["open_questions"] = 4

    if "allow_list" in intents and "transition_plan" not in intents:
        maximums["port_matrix"] = max(8, n_relevant_flows)
        maximums["flows"] = 4

    if "dependencies" in intents:
        minimums["dependencies"] = 1
        maximums["dependencies"] = 3

    if "required_flows" in intents and "transition_plan" not in intents:
        maximums["flows"] = 5

    return {"minimums": minimums, "maximums": maximums}


def select_with_coverage(
    scored_chunks: list[tuple[int, dict, dict]],
    intents: set[str],
    focus: dict,
    top_k: int = 10,
) -> list[tuple[int, dict]]:
    """
    Coverage-aware selection that ensures:
    1. Minimum representation of each relevant chunk type
    2. Maximizes asset-pair coverage for flow chunks
    3. For transition_plan, port_matrix is primary (has exact port/protocol),
       flows is secondary (has semantic reasoning)
    4. Respects per-type caps to maintain diversity

    scored_chunks: list of (score, chunk, score_breakdown)
    """
    focus_set = set(focus["all_assets"])
    n_relevant_flows = sum(
        1 for _, c, _ in scored_chunks
        if c.get("chunk_type") in ("port_matrix", "flows")
        and chunk_touches_assets(c, focus_set)
    )

    quotas = compute_dynamic_quotas(intents, n_relevant_flows)
    minimums = quotas["minimums"]
    maximums = quotas["maximums"]

    selected = []
    used_ids = set()
    type_counts = defaultdict(int)
    covered_pairs_by_type = defaultdict(set)  # per-type pair tracking
    covered_pairs_global = set()

    def can_add(chunk):
        cid = chunk["chunk_id"]
        if cid in used_ids:
            return False
        ctype = chunk.get("chunk_type", "general")
        if type_counts[ctype] >= maximums.get(ctype, top_k):
            return False
        return True

    def do_add(score, chunk):
        cid = chunk["chunk_id"]
        ctype = chunk.get("chunk_type", "general")
        selected.append((score, chunk))
        used_ids.add(cid)
        type_counts[ctype] += 1
        pair = chunk_flow_pair(chunk)
        if pair:
            covered_pairs_by_type[ctype].add(pair)
            covered_pairs_global.add(pair)
        return True

    # For transition_plan: port_matrix first (exact details), then flows (reasoning),
    # then blocked_flows, target_intent. Otherwise: natural order.
    if intents & {"transition_plan", "allow_list"}:
        min_order = ["port_matrix", "flows", "blocked_flows", "target_intent",
                     "open_questions", "dependencies"]
    else:
        min_order = list(minimums.keys())

    # ── Pass 1: Satisfy minimums in priority order ──
    for ctype in min_order:
        min_count = minimums.get(ctype, 0)
        if min_count <= 0:
            continue
        count = 0
        for score, chunk, _ in scored_chunks:
            if count >= min_count:
                break
            if chunk.get("chunk_type") == ctype and can_add(chunk):
                do_add(score, chunk)
                count += 1

    # ── Pass 2: Coverage expansion for port_matrix (highest priority) ──
    # Add port_matrix chunks that cover NEW asset-pairs.
    if intents & {"transition_plan", "allow_list", "required_flows", "ports_protocols"}:
        for score, chunk, _ in scored_chunks:
            if len(selected) >= top_k:
                break
            ctype = chunk.get("chunk_type", "general")
            if ctype != "port_matrix":
                continue
            if not can_add(chunk):
                continue
            pair = chunk_flow_pair(chunk)
            # Add if this pair isn't yet covered by ANY port_matrix chunk
            if pair and pair not in covered_pairs_by_type.get("port_matrix", set()):
                if chunk_touches_assets(chunk, focus_set):
                    do_add(score, chunk)

    # ── Pass 3: Coverage expansion for flows (secondary) ──
    if intents & {"transition_plan", "allow_list", "required_flows"}:
        for score, chunk, _ in scored_chunks:
            if len(selected) >= top_k:
                break
            ctype = chunk.get("chunk_type", "general")
            if ctype != "flows":
                continue
            if not can_add(chunk):
                continue
            pair = chunk_flow_pair(chunk)
            # Add if this route isn't covered by port_matrix already
            if pair and pair not in covered_pairs_by_type.get("port_matrix", set()):
                if chunk_touches_assets(chunk, focus_set):
                    do_add(score, chunk)

    # ── Pass 4: Fill remaining slots by score ──
    for score, chunk, _ in scored_chunks:
        if len(selected) >= top_k:
            break
        if can_add(chunk):
            do_add(score, chunk)

    # Sort final list by score descending
    selected.sort(key=lambda x: x[0], reverse=True)
    return selected[:top_k]


# ─── Main retrieval pipeline ────────────────────────────────────

def retrieve_top_chunks(question: str, top_k: int = 10, debug: bool = False):
    """
    Main entry point.
    Returns: list of (score, chunk) tuples.
    If debug=True, also prints scoring breakdowns.
    """
    chunks = load_chunks()
    model = load_model()

    intents = detect_intents(question)
    focus = build_focus_set(model, question)

    # Score all chunks
    scored = []
    for chunk in chunks:
        result = score_chunk(question, chunk, focus, intents)
        if result["total"] > 0:
            scored.append((result["total"], chunk, result["breakdown"]))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    if debug:
        print(f"Intents: {intents}")
        print(f"Focus: zones={focus['zones']}, zone_assets={focus['zone_assets']}, "
              f"dep_assets={focus['dep_assets']}")
        print(f"Scored chunks: {len(scored)}")
        print()

    # Select with coverage awareness
    results = select_with_coverage(scored, intents, focus, top_k=top_k)

    if debug:
        # Also show what was scored but not selected
        selected_ids = {c["chunk_id"] for _, c in results}
        missed_important = [
            (s, c, b) for s, c, b in scored[:50]
            if c["chunk_id"] not in selected_ids
            and c["chunk_type"] in ("port_matrix", "flows", "blocked_flows", "open_questions")
        ]
        if missed_important:
            print(f"\n--- Scored but not selected (top flow-relevant) ---")
            for s, c, b in missed_important[:10]:
                print(f"  score={s:3d} | {c['chunk_type']:15s} | {c['chunk_id']} | "
                      f"{c['section_title'][:55]}")

    return results


def retrieve_with_metadata(question: str, top_k: int = 10):
    """
    Extended entry point that returns retrieval results along with
    the detected intents and focus set, so the calling agent can
    reuse them instead of re-computing.

    Returns: {
        "chunks": list of (score, chunk),
        "intents": set[str],
        "focus": dict,
    }
    """
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

    return {
        "chunks": results,
        "intents": intents,
        "focus": focus,
    }


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    print("RAG Retriever v2 (connectivity-aware)")
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
            print(f"    entities: {chunk['entities']}")
            print(f"    flow_assets: {chunk.get('flow_assets', [])}")
            print(f"    zones: {chunk['zones']}")
            print(f"    text preview: {chunk['text'][:300]}")
            print("-" * 60)


if __name__ == "__main__":
    main()