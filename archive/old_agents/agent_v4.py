import os
import json
import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
YAML_FILE = BASE_DIR / "08_structured_network_model.yaml"

MARKDOWN_FILES = {
    "services": BASE_DIR / "02_services.md",
    "dependencies": BASE_DIR / "03_dependencies.md",
    "required_flows": BASE_DIR / "04_required_flows.md",
    "blocked_flows": BASE_DIR / "05_blocked_or_unnecessary_flows.md",
    "open_questions": BASE_DIR / "06_open_questions_and_assumptions.md",
    "target_intent": BASE_DIR / "07_target_security_intent.md",
}


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


def normalize_question(text: str) -> str:
    return " ".join(text.strip().lower().split())


def get_dependencies(model, asset_name: str):
    for item in model.get("dependencies", []):
        if item.get("asset", "").lower() == asset_name.lower():
            return item.get("depends_on", [])
    return []


def get_required_flows_for_source(model, asset_name: str):
    results = []
    for flow in model.get("required_flows", []):
        if flow.get("source", "").lower() == asset_name.lower():
            results.append(flow)
    return results


def get_port_protocol(model, source: str, destination: str):
    for item in model.get("port_protocol_matrix", []):
        if (
            item.get("source", "").lower() == source.lower()
            and item.get("destination", "").lower() == destination.lower()
        ):
            return item
    return None


def compare_app_zone_target(model):
    blocked = model.get("blocked_or_unnecessary_flows", [])
    target = model.get("target_security_intent", {})
    findings = []

    for item in blocked:
        flow = item.get("flow", "")
        if "APP_ZONE" in flow:
            findings.append(flow)

    zone_intent = target.get("zone_intent", {}).get("APP_ZONE", "")
    general_intent = target.get("general", [])

    return findings, zone_intent, general_intent


def list_open_questions(model):
    return model.get("open_questions", [])


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


def classify_question(q: str) -> str | None:
    if "app01" in q and (
        "depend" in q or "dependencies" in q or "rely on" in q
    ):
        return "app01_dependencies"

    if "app02" in q and (
        "communication must remain open" in q
        or "must remain open" in q
        or "required communication" in q
        or "required flows" in q
        or "needs to reach" in q
        or "needs access to" in q
    ):
        return "app02_required_flows"

    if "app01" in q and "internal api" in q and (
        "port" in q or "protocol" in q or "reach" in q or "use" in q or "uses" in q
    ):
        return "app01_internal_api_port"

    if "app_zone" in q and (
        "aligned" in q
        or "target security intent" in q
        or "broad access" in q
        or "target intent" in q
    ):
        return "app_zone_comparison"

    if (
        "unresolved" in q
        or "not fully confirmed" in q
        or "open questions" in q
        or "still unresolved" in q
        or "not confirmed" in q
    ):
        return "open_questions"

    return "general_network_question"


def build_context(model, question: str, intent: str) -> dict:
    context = {
        "intent": intent,
        "question": question,
        "structured_facts": {},
        "supporting_context": {},
    }

    if intent == "app01_dependencies":
        context["structured_facts"]["dependencies"] = get_dependencies(model, "APP01")
        context["supporting_context"]["dependencies_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["dependencies"]),
            "## Asset: APP01"
        )

    elif intent == "app02_required_flows":
        context["structured_facts"]["required_flows"] = get_required_flows_for_source(model, "APP02")
        context["supporting_context"]["required_flows_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["required_flows"]),
            "## Flow: APP02"
        )

    elif intent == "app01_internal_api_port":
        context["structured_facts"]["port_protocol"] = get_port_protocol(
            model, "APP01", "Internal API on IAM01"
        )
        context["supporting_context"]["required_flows_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["required_flows"]),
            "## Flow: APP01 -> Internal API on IAM01"
        )

    elif intent == "app_zone_comparison":
        findings, zone_intent, general_intent = compare_app_zone_target(model)
        context["structured_facts"]["broad_findings"] = findings
        context["structured_facts"]["zone_intent"] = zone_intent
        context["structured_facts"]["general_intent"] = general_intent
        context["supporting_context"]["target_intent_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["target_intent"]),
            "### APP_ZONE"
        )
        context["supporting_context"]["blocked_flows_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["blocked_flows"]),
            "APP_ZONE"
        )

    elif intent == "open_questions":
        context["structured_facts"]["open_questions"] = list_open_questions(model)
        context["supporting_context"]["open_questions_md"] = short_context_snippet(
            load_markdown_text(MARKDOWN_FILES["open_questions"]),
            "## Open Questions"
        )

    else:
        # General network fallback
        context["structured_facts"]["zones"] = model.get("zones", [])
        context["structured_facts"]["assets"] = model.get("assets", [])
        context["structured_facts"]["dependencies"] = model.get("dependencies", [])
        context["structured_facts"]["required_flows"] = model.get("required_flows", [])
        context["structured_facts"]["open_questions"] = model.get("open_questions", [])

    return context


def build_prompt(context: dict) -> str:
    return f"""
You are a network-aware AI assistant for a documented homelab environment.

Your job:
- answer only using the provided context
- do not invent facts
- clearly distinguish confirmed facts, owner-declared defaults, and open questions
- keep the answer practical and concise
- if the question goes beyond the provided context, say so clearly

Question:
{context['question']}

Intent:
{context['intent']}

Structured Facts:
{json.dumps(context['structured_facts'], indent=2, ensure_ascii=False)}

Supporting Context:
{json.dumps(context['supporting_context'], indent=2, ensure_ascii=False)}

Answer rules:
1. Start with a direct answer.
2. Then add a short supporting explanation.
3. Mention certainty level when relevant.
4. Do not assume undocumented details.
""".strip()


def fake_llm_response(context: dict) -> str:
    """
    Temporary fallback until a real LLM is connected.
    This keeps v4 testable without external API dependency.
    """
    intent = context["intent"]

    if intent == "app01_dependencies":
        deps = context["structured_facts"].get("dependencies", [])
        return (
            "Direct answer:\n"
            f"APP01 depends on: {', '.join(deps)}.\n\n"
            "Supporting explanation:\n"
            "These dependencies are taken from the structured network model and reflect the current documented architecture.\n\n"
            "Certainty:\n"
            "Confirmed in the current model."
        )

    if intent == "app02_required_flows":
        flows = context["structured_facts"].get("required_flows", [])
        lines = [f"- {f['source']} -> {f['destination']}: {f['purpose']}" for f in flows]
        return (
            "Direct answer:\n"
            "The communication that must remain open for APP02 is:\n"
            + "\n".join(lines)
            + "\n\nSupporting explanation:\n"
            "These are the documented required flows, not just broad currently allowed access.\n\n"
            "Certainty:\n"
            "Grounded in documented required flows."
        )

    if intent == "app01_internal_api_port":
        item = context["structured_facts"].get("port_protocol", {})
        if not item:
            return "No confirmed port/protocol entry was found for APP01 -> Internal API on IAM01."
        return (
            "Direct answer:\n"
            f"APP01 uses {item['protocol']} on port {item['port']} to reach the Internal API on IAM01.\n\n"
            f"Supporting explanation:\nPurpose: {item['purpose']}\n\n"
            f"Certainty:\n{item['status']}."
        )

    if intent == "app_zone_comparison":
        zone_intent = context["structured_facts"].get("zone_intent", "")
        findings = context["structured_facts"].get("broad_findings", [])
        return (
            "Direct answer:\n"
            "No, broad APP_ZONE access is not aligned with the target security intent.\n\n"
            "Supporting explanation:\n"
            f"- APP_ZONE target intent: {zone_intent}\n"
            + (
                "- Broad access patterns that should not remain:\n"
                + "\n".join([f"  - {x}" for x in findings])
                if findings else ""
            )
            + "\n\nCertainty:\nGrounded in blocked/unnecessary flows and target security intent."
        )

    if intent == "open_questions":
        questions = context["structured_facts"].get("open_questions", [])
        return (
            "Direct answer:\n"
            "The current model still contains unresolved items.\n\n"
            "Supporting explanation:\n"
            + "\n".join([f"- {q}" for q in questions])
            + "\n\nCertainty:\nThese are explicitly recorded as open questions."
        )

    return (
        "Direct answer:\n"
        "This question is outside the current supported network-agent scope for v4.\n\n"
        "Supporting explanation:\n"
        "The current v4 prototype can build structured context, but it is still limited to the first core network use cases.\n\n"
        "Certainty:\n"
        "Scope-limited by current implementation."
    )


def answer_question(model, question: str):
    q = normalize_question(question)
    intent = classify_question(q)
    context = build_context(model, question, intent)
    prompt = build_prompt(context)

    # Temporary fallback until real LLM is connected
    answer = fake_llm_response(context)

    return answer, prompt, context


def main():
    model = load_model()
    print("Network AI Agent v4 (LLM-ready)")
    print("Type a question, or type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer, prompt, context = answer_question(model, question)

        print("\nAgent:")
        print(answer)
        print("\n" + "-" * 60 + "\n")

        # Optional debug view
        show_debug = input("Show built prompt/context? (y/n): ").strip().lower()
        if show_debug == "y":
            print("\n--- BUILT CONTEXT ---")
            print(json.dumps(context, indent=2, ensure_ascii=False))
            print("\n--- BUILT PROMPT ---")
            print(prompt)
            print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()