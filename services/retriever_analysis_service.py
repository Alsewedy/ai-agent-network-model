from collections import Counter
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_DIR = PROJECT_ROOT / "rag"

if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))


def rebuild_chunks():
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "rag" / "build_chunks.py")],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    if result.returncode != 0:
        raise RuntimeError(
            "build_chunks.py failed.\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )


def import_retriever_modules():
    for module_name in [
        "retrieve_chunks",
        "retrieve_chunks_v2",
    ]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    import retrieve_chunks as v1_module
    import retrieve_chunks_v2 as v2_module

    return v1_module, v2_module


def normalize_focus(focus: dict) -> dict:
    return {
        "scope_units": focus.get("scope_units", []),
        "direct_entities": focus.get("direct_entities", []),
        "scope_expanded_entities": focus.get("scope_expanded_entities", []),
        "dep_entities": focus.get("dep_entities", []),
        "all_entities": focus.get("all_entities", []),
    }


def build_summary_flags(results: list[tuple[int, dict]]) -> dict:
    types = [chunk.get("chunk_type", "general") for _, chunk in results]
    type_counts = dict(Counter(types).most_common())

    low_value_types = {"scope_units", "services", "evidence_notes"}
    low_value_count = sum(1 for t in types if t in low_value_types)

    return {
        "result_count": len(results),
        "type_counts": type_counts,
        "low_value_count": low_value_count,
        "has_technical_matrix": type_counts.get("technical_matrix", 0) > 0,
        "has_required_flows": type_counts.get("required_flows", 0) > 0,
        "has_unnecessary_access": type_counts.get("unnecessary_access", 0) > 0,
        "has_open_questions": type_counts.get("open_questions", 0) > 0,
        "has_target_intent": type_counts.get("target_intent", 0) > 0,
        "has_dependencies": type_counts.get("dependencies", 0) > 0,
    }


def serialize_results(results: list[tuple[int, dict]]) -> list[dict]:
    serialized = []

    for rank, (score, chunk) in enumerate(results, start=1):
        serialized.append({
            "rank": rank,
            "score": score,
            "chunk_id": chunk.get("chunk_id"),
            "chunk_type": chunk.get("chunk_type"),
            "source_file": chunk.get("source_file"),
            "section_title": chunk.get("section_title"),
            "entities": chunk.get("entities", []),
            "scope_units": chunk.get("scope_units", []),
            "flow_entities": chunk.get("flow_entities", []),
            "flow_scope_units": chunk.get("flow_scope_units", []),
            "confidence_tags": chunk.get("confidence_tags", []),
            "text_preview": chunk.get("text", "")[:500],
        })

    return serialized


def analyze_with_v1(v1_module, question: str, top_k: int):
    model = v1_module.load_model()
    intents = sorted(list(v1_module.detect_intents(question)))
    focus = v1_module.build_focus_set(model, question)
    results = v1_module.retrieve_top_chunks(question, top_k=top_k)

    return {
        "version_label": "Retriever v1",
        "intents": intents,
        "focus": normalize_focus(focus),
        "summary": build_summary_flags(results),
        "results": serialize_results(results),
    }


def analyze_with_v2(v2_module, question: str, top_k: int):
    payload = v2_module.retrieve_with_metadata(question, top_k=top_k)
    results = payload.get("chunks", [])
    intents = sorted(list(payload.get("intents", set())))
    focus = payload.get("focus", {})

    return {
        "version_label": "Retriever v2",
        "intents": intents,
        "focus": normalize_focus(focus),
        "summary": build_summary_flags(results),
        "results": serialize_results(results),
    }


def build_diagnostics(question: str, analyses: list[dict]) -> list[dict]:
    diagnostics = []
    normalized_question = question.lower()

    for item in analyses:
        version = item["version_label"]
        summary = item["summary"]
        notes = []

        if "transition plan" in normalized_question or "least-privilege" in normalized_question:
            if not summary["has_technical_matrix"]:
                notes.append("No technical_matrix chunks were retrieved for a transition-style question.")
            if not summary["has_unnecessary_access"]:
                notes.append("No unnecessary_access chunks were retrieved for a transition-style question.")
            if not summary["has_target_intent"]:
                notes.append("No target_intent chunks were retrieved for a transition-style question.")

        if "unresolved" in normalized_question or "not fully confirmed" in normalized_question:
            if not summary["has_open_questions"]:
                notes.append("No open_questions chunks were retrieved for an uncertainty-style question.")

        if "depend" in normalized_question:
            if not summary["has_dependencies"]:
                notes.append("No dependencies chunks were retrieved for a dependency-style question.")

        if summary["low_value_count"] > 0:
            notes.append(f"{summary['low_value_count']} low-value chunks appeared in the top results.")

        if not item["results"]:
            notes.append("No chunks were retrieved.")

        diagnostics.append({
            "version_label": version,
            "notes": notes,
        })

    return diagnostics


def analyze_retrieval(question: str, top_k: int = 10):
    rebuild_chunks()
    v1_module, v2_module = import_retriever_modules()

    v1 = analyze_with_v1(v1_module, question, top_k)
    v2 = analyze_with_v2(v2_module, question, top_k)

    return {
        "question": question,
        "top_k": top_k,
        "analyses": [v1, v2],
        "diagnostics": build_diagnostics(question, [v1, v2]),
    }