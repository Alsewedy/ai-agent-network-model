"""
build_chunks.py – Enhanced chunking with flow directionality metadata.

Changes from v1:
  1. Extracts flow_source and flow_destination from section titles
     (e.g. "Flow: APP01 -> DB01" → source=APP01, destination=DB01)
  2. Resolves compound destinations to primary asset
     (e.g. "Vault on DB01" → destination_asset=DB01, destination_service=Vault)
  3. Adds a `flow_assets` field: deduplicated list of primary assets involved
     in the flow, making connectivity-graph construction trivial at retrieval time.
  4. All other chunking logic is unchanged from v1.
"""

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_DIR = PROJECT_ROOT / "rag"
OUTPUT_FILE = RAG_DIR / "chunks.json"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge" / "network_domain"

SOURCE_FILES = [
    "01_zones_and_assets.md",
    "02_services.md",
    "03_dependencies.md",
    "04_required_flows.md",
    "04a_port_and_protocol_matrix.md",
    "04b_evidence_notes.md",
    "05_blocked_or_unnecessary_flows.md",
    "06_open_questions_and_assumptions.md",
    "07_target_security_intent.md",
]

KNOWN_ASSETS = [
    "APP01",
    "APP02",
    "IAM01",
    "DB01",
    "DC01-CYBERAUDIT",
    "PROXY01",
    "Firewall01",
    "ESXi",
    "Switch Management",
    "Admin laptop",
    "Vault",
    "Internal API",
    "Keycloak",
]

KNOWN_ZONES = [
    "WAN",
    "LAN / DATA",
    "APP_ZONE",
    "DMZ_ZONE",
    "SERVICE_ZONE",
    "MGMT",
    "ADMIN",
    "EMPLOYEE",
    "GUEST",
]

# Maps service-on-host descriptions to (primary_asset, service_name)
# Used to resolve "Vault on DB01" → asset=DB01, service=Vault
HOST_SERVICE_PATTERNS = [
    (r"(?i)vault\s+on\s+(DB01|IAM01|APP01|APP02)", "Vault"),
    (r"(?i)internal\s+api\s+on\s+(IAM01)", "Internal API"),
    (r"(?i)keycloak\s+on\s+(IAM01)", "Keycloak"),
    (r"(?i)nginx\s+on\s+(APP01|APP02)", "Nginx"),
    (r"(?i)local\s+(?:node\.?js\s+)?portal\s+process\s+on\s+(APP01)", "Portal"),
]

CONFIDENCE_PATTERNS = {
    "confirmed": [
        "confirmed",
        "confirmed fact",
        "confirmed facts",
    ],
    "owner_confirmed": [
        "owner-confirmed",
        "owner confirmed",
        "owner_confirmed",
    ],
    "standard_default_declared_by_owner": [
        "standard default declared by owner",
        "owner-declared",
        "owner declared",
    ],
    "open_question": [
        "open question",
        "open questions",
        "unresolved",
        "not fully confirmed",
    ],
}

FLOW_TITLE_PATTERN = re.compile(r"Flow:\s*(.+?)\s*->\s*(.+?)(?:\s*\(.*\))?$")


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_chunk_type(source_file: str, section_title: str) -> str:
    file_map = {
        "01_zones_and_assets.md": "zones_assets",
        "02_services.md": "services",
        "03_dependencies.md": "dependencies",
        "04_required_flows.md": "flows",
        "04a_port_and_protocol_matrix.md": "port_matrix",
        "04b_evidence_notes.md": "evidence",
        "05_blocked_or_unnecessary_flows.md": "blocked_flows",
        "06_open_questions_and_assumptions.md": "open_questions",
        "07_target_security_intent.md": "target_intent",
    }
    return file_map.get(source_file, "general")


def extract_entities(text: str) -> list[str]:
    found = []
    lower = text.lower()
    for asset in KNOWN_ASSETS:
        if asset.lower() in lower and asset not in found:
            found.append(asset)
    return found


def extract_zones(text: str) -> list[str]:
    found = []
    lower = text.lower()
    for zone in KNOWN_ZONES:
        if zone.lower() in lower and zone not in found:
            found.append(zone)
    return found


def extract_confidence_tags(text: str) -> list[str]:
    found = []
    lower = normalize_text(text)
    for tag, patterns in CONFIDENCE_PATTERNS.items():
        for pattern in patterns:
            if normalize_text(pattern) in lower:
                found.append(tag)
                break
    return found


def resolve_endpoint(raw: str) -> dict:
    """
    Resolve a flow endpoint string to structured metadata.
    Returns: {"raw": str, "assets": [str], "service": str|None, "is_zone": bool}

    Note: `assets` is a list because compound endpoints like "IAM01 / Internal API"
    reference multiple assets.
    """
    raw = raw.strip()
    result = {"raw": raw, "assets": [], "service": None, "is_zone": False}

    # Check for "service on host" pattern first
    for pattern, service_name in HOST_SERVICE_PATTERNS:
        m = re.search(pattern, raw)
        if m:
            host = m.group(1)
            # Find the matching known asset (case-insensitive)
            for asset in KNOWN_ASSETS:
                if host.lower() == asset.lower():
                    result["assets"].append(asset)
                    break
            result["service"] = service_name
            return result

    raw_lower = raw.lower().strip()

    # Special cases first
    if "client" in raw_lower or "browser" in raw_lower:
        result["assets"] = ["Client"]
        return result
    if "target systems" in raw_lower or "any destination" in raw_lower:
        result["assets"] = ["Any"]
        return result

    # Check for zone match (exact)
    for zone in KNOWN_ZONES:
        if raw_lower == zone.lower():
            result["is_zone"] = True
            result["assets"] = [zone]
            return result

    # Check for asset matches (supports compound like "IAM01 / Internal API")
    for asset in KNOWN_ASSETS:
        if asset.lower() in raw_lower and asset not in result["assets"]:
            result["assets"].append(asset)

    return result


def extract_flow_metadata(section_title: str) -> dict:
    """
    Parse flow directionality from section title.
    Returns: {"flow_source": {...}, "flow_destination": {...}, "flow_assets": [...]}
    """
    m = FLOW_TITLE_PATTERN.match(section_title)
    if not m:
        return {"flow_source": None, "flow_destination": None, "flow_assets": []}

    src = resolve_endpoint(m.group(1))
    dst = resolve_endpoint(m.group(2))

    # Build deduplicated list of primary assets involved
    flow_assets = []
    for endpoint in [src, dst]:
        for asset in endpoint.get("assets", []):
            if asset not in ("Client", "Any") and asset not in flow_assets:
                flow_assets.append(asset)

    return {
        "flow_source": src,
        "flow_destination": dst,
        "flow_assets": flow_assets,
    }


def split_markdown_into_sections(text: str):
    lines = text.splitlines()
    sections = []
    current_title = "Document Introduction"
    current_lines = []
    heading_pattern = re.compile(r"^(#{1,6})\s+(.*)$")

    for line in lines:
        match = heading_pattern.match(line.strip())
        if match:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
                current_lines = []
            current_title = match.group(2).strip()
            current_lines.append(line)
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    sections = [(title, body) for title, body in sections if body.strip()]
    return sections


def maybe_split_large_section(section_title: str, section_text: str):
    words = section_text.split()
    if len(words) <= 600:
        return [(section_title, section_text)]

    blocks = re.split(r"\n\s*\n", section_text.strip())
    chunks = []
    current = []
    current_word_count = 0
    part = 1

    for block in blocks:
        block_words = len(block.split())
        if current and current_word_count + block_words > 500:
            chunks.append((f"{section_title} (Part {part})", "\n\n".join(current).strip()))
            current = [block]
            current_word_count = block_words
            part += 1
        else:
            current.append(block)
            current_word_count += block_words

    if current:
        chunks.append((f"{section_title} (Part {part})", "\n\n".join(current).strip()))

    return chunks


def build_chunks():
    all_chunks = []
    chunk_counter = 1

    for source_name in SOURCE_FILES:
        source_path = KNOWLEDGE_DIR / source_name
        if not source_path.exists():
            print(f"Warning: file not found: {source_name}")
            continue

        text = source_path.read_text(encoding="utf-8")
        sections = split_markdown_into_sections(text)
        chunk_type_base = detect_chunk_type(source_name, "")

        for section_title, section_body in sections:
            semantic_chunks = maybe_split_large_section(section_title, section_body)

            for final_title, final_text in semantic_chunks:
                # Extract flow metadata for flow-like chunk types
                flow_meta = {"flow_source": None, "flow_destination": None, "flow_assets": []}
                if chunk_type_base in ("port_matrix", "flows", "blocked_flows"):
                    flow_meta = extract_flow_metadata(final_title)

                chunk = {
                    "chunk_id": f"chunk_{chunk_counter:04d}",
                    "source_file": source_name,
                    "section_title": final_title,
                    "chunk_type": detect_chunk_type(source_name, final_title),
                    "entities": extract_entities(final_text),
                    "zones": extract_zones(final_text),
                    "confidence_tags": extract_confidence_tags(final_text),
                    "flow_source": flow_meta["flow_source"],
                    "flow_destination": flow_meta["flow_destination"],
                    "flow_assets": flow_meta["flow_assets"],
                    "text": final_text,
                }
                all_chunks.append(chunk)
                chunk_counter += 1

    return all_chunks


def main():
    chunks = build_chunks()

    RAG_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Built {len(chunks)} chunks.")
    print(f"Saved to: {OUTPUT_FILE}")

    # Summary
    flow_count = sum(1 for c in chunks if c["flow_assets"])
    print(f"Chunks with flow_assets metadata: {flow_count}")


if __name__ == "__main__":
    main()
