import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
YAML_FILE = BASE_DIR / "08_structured_network_model.yaml"


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


def normalize_question(text: str) -> str:
    return " ".join(text.strip().lower().split())


def find_asset(model, asset_name: str):
    for asset in model.get("assets", []):
        if asset.get("name", "").lower() == asset_name.lower():
            return asset
    return None


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


def answer_app01_dependencies(model):
    deps = get_dependencies(model, "APP01")
    return (
        "APP01 depends on:\n- "
        + "\n- ".join(deps)
        + "\n\nCertainty: confirmed in the current model."
    )


def answer_app02_required_flows(model):
    flows = get_required_flows_for_source(model, "APP02")
    if not flows:
        return "No required flows found for APP02."

    lines = []
    for flow in flows:
        lines.append(f"- {flow['source']} -> {flow['destination']}: {flow['purpose']}")

    return (
        "Required communication for APP02:\n"
        + "\n".join(lines)
        + "\n\nCertainty: based on documented required flows."
    )


def answer_app01_internal_api_port(model):
    item = get_port_protocol(model, "APP01", "Internal API on IAM01")
    if not item:
        return "No exact port/protocol entry found."

    return (
        f"APP01 reaches the Internal API on IAM01 using {item['protocol']} on port {item['port']}.\n"
        f"Purpose: {item['purpose']}\n"
        f"Certainty: {item['status']}."
    )


def answer_app_zone_comparison(model):
    findings, zone_intent, general_intent = compare_app_zone_target(model)

    answer = "No, broad APP_ZONE access is not aligned with the target security intent.\n\n"
    answer += "Why:\n"
    answer += f"- Target APP_ZONE intent: {zone_intent}\n"

    if general_intent:
        answer += "- General security intent:\n"
        for item in general_intent:
            answer += f"  - {item}\n"

    if findings:
        answer += "- Current broad access that should not remain:\n"
        for f in findings:
            answer += f"  - {f}\n"

    answer += "\nCertainty: based on blocked/unnecessary flows and target security intent."
    return answer


def answer_open_questions(model):
    questions = list_open_questions(model)
    if not questions:
        return "No open questions recorded."

    return (
        "Open questions in the current network model:\n- "
        + "\n- ".join(questions)
        + "\n\nCertainty: these are explicitly recorded as open questions."
    )


def classify_question(q: str) -> str | None:
    # APP01 dependencies
    if "app01" in q and (
        "depend" in q
        or "dependencies" in q
        or "rely on" in q
        or "depends on" in q
    ):
        return "app01_dependencies"

    # APP02 required communication
    if "app02" in q and (
        "communication must remain open" in q
        or "must remain open" in q
        or "required communication" in q
        or "required flows" in q
        or "needs to reach" in q
        or "needs access to" in q
    ):
        return "app02_required_flows"

    # APP01 -> Internal API port/protocol
    if "app01" in q and "internal api" in q and (
        "port" in q
        or "protocol" in q
        or "reach" in q
        or "use" in q
        or "uses" in q
    ):
        return "app01_internal_api_port"

    # APP_ZONE comparison
    if "app_zone" in q and (
        "aligned" in q
        or "target security intent" in q
        or "broad access" in q
        or "target intent" in q
    ):
        return "app_zone_comparison"

    # open questions / unresolved
    if (
        "unresolved" in q
        or "not fully confirmed" in q
        or "open questions" in q
        or "still unresolved" in q
        or "not confirmed" in q
    ):
        return "open_questions"

    return None


def answer_question(model, question: str):
    q = normalize_question(question)
    intent = classify_question(q)

    if intent == "app01_dependencies":
        return answer_app01_dependencies(model)

    if intent == "app02_required_flows":
        return answer_app02_required_flows(model)

    if intent == "app01_internal_api_port":
        return answer_app01_internal_api_port(model)

    if intent == "app_zone_comparison":
        return answer_app_zone_comparison(model)

    if intent == "open_questions":
        return answer_open_questions(model)

    return (
        "This question is outside the current network-agent scope, or its wording is not supported yet.\n\n"
        "Examples of supported questions:\n"
        "- What does APP01 depend on?\n"
        "- List APP01 dependencies\n"
        "- What communication must remain open for APP02?\n"
        "- What are the required flows for APP02?\n"
        "- What exact port and protocol does APP01 use to reach the Internal API?\n"
        "- Is broad APP_ZONE access aligned with the target security intent?\n"
        "- What parts of the network model are still unresolved or not fully confirmed?"
    )


def main():
    model = load_model()
    print("Network AI Agent v2")
    print("Type a question, or type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        answer = answer_question(model, question)
        print("\nAgent:")
        print(answer)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()