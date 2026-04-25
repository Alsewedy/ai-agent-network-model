"""
build_chunks.py – Chunk builder for the new network knowledge architecture.

Design rules:
  1. Build chunks from markdown files only.
  2. Structured YAML files remain direct structured inputs and are NOT chunked.
  3. Use model.yaml to derive entity and scope-unit awareness.
  4. Preserve flow directionality metadata for communication-related chunks.
  5. Preserve confidence-tag hints from evidence / technical content.
  6. Skip low-value filler sections that dilute retrieval quality.
"""

import json
import re
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_DIR = PROJECT_ROOT / "rag"
OUTPUT_FILE = RAG_DIR / "chunks.json"

KNOWLEDGE_ROOT = PROJECT_ROOT / "knowledge"
NETWORK_DOMAIN_DIR = KNOWLEDGE_ROOT / "domains" / "network"
MODEL_FILE = NETWORK_DOMAIN_DIR / "model.yaml"

SOURCE_FILES = [
    ("scope/scope_units.md", "scope_units"),
    ("scope/services.md", "services"),
    ("scope/dependencies.md", "dependencies"),
    ("communication/required_flows.md", "required_flows"),
    ("communication/technical_matrix.md", "technical_matrix"),
    ("evidence/evidence_notes.md", "evidence_notes"),
    ("posture/unnecessary_access.md", "unnecessary_access"),
    ("posture/target_intent.md", "target_intent"),
    ("uncertainty/open_questions.md", "open_questions"),
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
    "standard_default": [
        "standard default",
        "standard default declared by owner",
        "owner-declared",
        "owner declared",
    ],
    "open_question": [
        "open question",
        "open questions",
        "unresolved",
        "not fully confirmed",
        "needs confirmation",
        "assumption",
    ],
}

FLOW_TITLE_PATTERN = re.compile(
    r"Flow:\s*(.+?)\s*(?:->|→)\s*(.+?)(?:\s*\(.*\))?$",
    re.IGNORECASE,
)

ACCESS_TITLE_PATTERN = re.compile(
    r"^\s*(.+?)\s*(?:->|→)\s*(.+?)(?:\s*\(.*\))?$",
    re.IGNORECASE,
)

FILLER_SECTION_TITLES = {
    "document introduction",
    "purpose",
    "notes",
    "modeling rule",
    "network scope units",
    "network services",
    "network dependencies",
    "network required flows",
    "network technical matrix",
    "network evidence notes",
    "network unnecessary access",
    "network target intent",
    "network open questions",
    "per-scope-unit intent",
    "cross-cutting intent",
    "confirmed facts",
    "assumptions",
    "open questions",
}

KEEP_PURPOSE_FOR_CHUNK_TYPES = {
    "open_questions",
    "target_intent",
}

FLOW_LIKE_CHUNK_TYPES = {
    "required_flows",
    "technical_matrix",
    "unnecessary_access",
}

MIN_CHUNK_WORDS = 18
MIN_WORD_EXEMPT_TYPES = {
    "required_flows",
    "technical_matrix",
    "unnecessary_access",
    "open_questions",
    "target_intent",
}


# ──────────────────────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────────────────────

def load_model():
    with open(MODEL_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected model.yaml root to be a dictionary, got: {type(data)}"
        )

    return data


# ──────────────────────────────────────────────────────────────
# Normalization
# ──────────────────────────────────────────────────────────────

def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("→", " ")
    text = text.replace("->", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def first_n_words(text: str, n: int) -> str:
    words = text.split()
    if len(words) <= n:
        return text
    return " ".join(words[:n])


def remove_low_value_lines_for_extraction(text: str, chunk_type: str) -> str:
    """
    Remove lines that often inject noisy entities/services into extraction
    without representing the primary subject of the chunk.
    """
    if chunk_type not in {"services", "evidence_notes"}:
        return text

    drop_prefixes = (
        "related entry:",
        "related entries:",
        "location:",
        "method:",
        "reference:",
        "references:",
    )

    kept_lines = []
    for line in text.splitlines():
        stripped = line.strip().lower()
        if any(stripped.startswith(prefix) for prefix in drop_prefixes):
            continue
        kept_lines.append(line)

    return "\n".join(kept_lines).strip()


# ──────────────────────────────────────────────────────────────
# Knowledge-derived lookup helpers
# ──────────────────────────────────────────────────────────────

def build_entity_aliases(model: dict) -> dict[str, str]:
    aliases = {}

    for entity in model.get("entities", []):
        name = entity.get("name")
        if not name:
            continue

        aliases[normalize_text(name)] = name

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

        aliases[normalize_text(name)] = name

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


# ──────────────────────────────────────────────────────────────
# Chunk typing
# ──────────────────────────────────────────────────────────────

def detect_chunk_type(source_file: str) -> str:
    file_map = {
        "scope/scope_units.md": "scope_units",
        "scope/services.md": "services",
        "scope/dependencies.md": "dependencies",
        "communication/required_flows.md": "required_flows",
        "communication/technical_matrix.md": "technical_matrix",
        "evidence/evidence_notes.md": "evidence_notes",
        "posture/unnecessary_access.md": "unnecessary_access",
        "posture/target_intent.md": "target_intent",
        "uncertainty/open_questions.md": "open_questions",
    }
    return file_map.get(source_file, "general")


# ──────────────────────────────────────────────────────────────
# Extraction
# ──────────────────────────────────────────────────────────────

def extract_entities(text: str, entity_aliases: dict[str, str]) -> list[str]:
    found = []
    lower = normalize_text(text)

    for alias, canonical in sorted(entity_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, lower) and canonical not in found:
            found.append(canonical)

    return found


def extract_scope_units(text: str, scope_aliases: dict[str, str]) -> list[str]:
    found = []
    lower = normalize_text(text)

    for alias, canonical in sorted(scope_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, lower) and canonical not in found:
            found.append(canonical)

    return found


def extract_confidence_tags(text: str) -> list[str]:
    found = []
    lower = normalize_text(text)

    for tag, patterns in CONFIDENCE_PATTERNS.items():
        for pattern in patterns:
            if normalize_text(pattern) in lower:
                if tag not in found:
                    found.append(tag)
                break

    return found


def resolve_endpoint(raw: str, entity_aliases: dict[str, str], scope_aliases: dict[str, str]) -> dict:
    raw = raw.strip()

    result = {
        "raw": raw,
        "entities": [],
        "service": None,
        "scope_units": [],
        "is_scope_unit": False,
    }

    raw_lower = normalize_text(raw)

    if "client" in raw_lower or "browser" in raw_lower:
        result["entities"] = ["Client"]
        return result

    if "any destination" in raw_lower:
        result["entities"] = ["Any"]
        return result

    for alias, canonical in scope_aliases.items():
        if raw_lower == alias:
            result["is_scope_unit"] = True
            result["scope_units"] = [canonical]
            return result

    for alias, canonical in sorted(scope_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, raw_lower) and canonical not in result["scope_units"]:
            result["scope_units"].append(canonical)

    for alias, canonical in sorted(entity_aliases.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r"(?:^|\s)" + re.escape(alias) + r"(?:\s|$)"
        if re.search(pattern, raw_lower):
            if canonical not in result["entities"]:
                result["entities"].append(canonical)

    if "target systems" in raw_lower and not result["entities"] and not result["scope_units"]:
        result["entities"] = ["Any"]
        return result

    service_on_host_patterns = [
        (r"(?i)vault\s+on\s+(.+)$", "Vault"),
        (r"(?i)internal\s+api\s+on\s+(.+)$", "Internal API"),
        (r"(?i)keycloak\s+on\s+(.+)$", "Keycloak"),
        (r"(?i)nginx\s+on\s+(.+)$", "Nginx"),
        (r"(?i)local\s+(?:node\.?js\s+)?portal\s+process\s+on\s+(.+)$", "Portal"),
    ]

    for pattern, service_name in service_on_host_patterns:
        match = re.search(pattern, raw)
        if match:
            host_raw = normalize_text(match.group(1).strip())
            for alias, canonical in entity_aliases.items():
                if alias == host_raw and canonical not in result["entities"]:
                    result["entities"].append(canonical)
                    result["service"] = service_name
                    return result

    return result


def extract_flow_metadata(
    section_title: str,
    chunk_type: str,
    entity_aliases: dict[str, str],
    scope_aliases: dict[str, str],
) -> dict:
    match = FLOW_TITLE_PATTERN.match(section_title)

    if not match and chunk_type == "unnecessary_access":
        match = ACCESS_TITLE_PATTERN.match(section_title)

    if not match:
        return {
            "flow_source": None,
            "flow_destination": None,
            "flow_entities": [],
            "flow_scope_units": [],
        }

    source = resolve_endpoint(match.group(1), entity_aliases, scope_aliases)
    destination = resolve_endpoint(match.group(2), entity_aliases, scope_aliases)

    flow_entities = []
    flow_scope_units = []

    for endpoint in (source, destination):
        for entity in endpoint.get("entities", []):
            if entity not in ("Client", "Any") and entity not in flow_entities:
                flow_entities.append(entity)

        for scope_unit in endpoint.get("scope_units", []):
            if scope_unit not in flow_scope_units:
                flow_scope_units.append(scope_unit)

    return {
        "flow_source": source,
        "flow_destination": destination,
        "flow_entities": flow_entities,
        "flow_scope_units": flow_scope_units,
    }


def merge_unique(primary: list[str], secondary: list[str]) -> list[str]:
    merged = []
    for item in primary + secondary:
        if item not in merged:
            merged.append(item)
    return merged


def build_extraction_text(
    section_title: str,
    section_text: str,
    chunk_type: str,
) -> tuple[str, str]:
    title_text = section_title.strip()
    clean_body = remove_low_value_lines_for_extraction(section_text, chunk_type)

    if chunk_type in FLOW_LIKE_CHUNK_TYPES:
        body_text = first_n_words(clean_body, 80)
    else:
        body_text = first_n_words(clean_body, 160)

    return title_text, body_text


def extract_chunk_entities_and_scope_units(
    section_title: str,
    section_text: str,
    chunk_type: str,
    entity_aliases: dict[str, str],
    scope_aliases: dict[str, str],
    flow_meta: dict,
) -> tuple[list[str], list[str]]:
    title_text, body_text = build_extraction_text(section_title, section_text, chunk_type)

    title_entities = extract_entities(title_text, entity_aliases)
    title_scope_units = extract_scope_units(title_text, scope_aliases)

    body_entities = extract_entities(body_text, entity_aliases)
    body_scope_units = extract_scope_units(body_text, scope_aliases)

    entities = merge_unique(
        flow_meta.get("flow_entities", []),
        merge_unique(title_entities, body_entities),
    )
    scope_units = merge_unique(
        flow_meta.get("flow_scope_units", []),
        merge_unique(title_scope_units, body_scope_units),
    )

    return entities, scope_units


# ──────────────────────────────────────────────────────────────
# Markdown section splitting
# ──────────────────────────────────────────────────────────────

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

    return [(title, body) for title, body in sections if body.strip()]


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


def should_skip_section(section_title: str, chunk_type: str, section_text: str) -> bool:
    title = normalize_text(section_title)
    word_count = len(section_text.split())

    if title in FILLER_SECTION_TITLES and chunk_type not in KEEP_PURPOSE_FOR_CHUNK_TYPES:
        return True

    if title.startswith("network ") and chunk_type not in KEEP_PURPOSE_FOR_CHUNK_TYPES:
        return True

    if (
        word_count < MIN_CHUNK_WORDS
        and chunk_type not in MIN_WORD_EXEMPT_TYPES
        and not FLOW_TITLE_PATTERN.match(section_title)
        and not ACCESS_TITLE_PATTERN.match(section_title)
    ):
        return True

    return False


# ──────────────────────────────────────────────────────────────
# Build
# ──────────────────────────────────────────────────────────────

def build_chunks():
    model = load_model()
    entity_aliases = build_entity_aliases(model)
    scope_aliases = build_scope_unit_aliases(model)

    all_chunks = []
    chunk_counter = 1

    for relative_path, _source_type in SOURCE_FILES:
        source_path = NETWORK_DOMAIN_DIR / relative_path
        if not source_path.exists():
            print(f"Warning: file not found: {relative_path}")
            continue

        text = source_path.read_text(encoding="utf-8")
        sections = split_markdown_into_sections(text)
        chunk_type = detect_chunk_type(relative_path)

        for section_title, section_body in sections:
            if should_skip_section(section_title, chunk_type, section_body):
                continue

            semantic_chunks = maybe_split_large_section(section_title, section_body)

            for final_title, final_text in semantic_chunks:
                if should_skip_section(final_title, chunk_type, final_text):
                    continue

                flow_meta = {
                    "flow_source": None,
                    "flow_destination": None,
                    "flow_entities": [],
                    "flow_scope_units": [],
                }

                if chunk_type in FLOW_LIKE_CHUNK_TYPES:
                    flow_meta = extract_flow_metadata(
                        final_title,
                        chunk_type,
                        entity_aliases,
                        scope_aliases,
                    )

                entities, scope_units = extract_chunk_entities_and_scope_units(
                    final_title,
                    final_text,
                    chunk_type,
                    entity_aliases,
                    scope_aliases,
                    flow_meta,
                )

                full_text_for_confidence = f"{final_title}\n{final_text}"

                chunk = {
                    "chunk_id": f"chunk_{chunk_counter:04d}",
                    "source_file": relative_path,
                    "section_title": final_title,
                    "chunk_type": chunk_type,
                    "entities": entities,
                    "scope_units": scope_units,
                    "confidence_tags": extract_confidence_tags(full_text_for_confidence),
                    "flow_source": flow_meta["flow_source"],
                    "flow_destination": flow_meta["flow_destination"],
                    "flow_entities": flow_meta["flow_entities"],
                    "flow_scope_units": flow_meta["flow_scope_units"],
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

    flow_count = sum(1 for c in chunks if c["flow_entities"] or c["flow_scope_units"])
    print(f"Chunks with flow metadata: {flow_count}")


if __name__ == "__main__":
    main()