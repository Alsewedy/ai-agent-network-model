import yaml
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
YAML_FILE = BASE_DIR / "08_structured_network_model.yaml"


def load_model():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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


def answer_question(model, question: str):
    q = question.strip().lower()

    if q == "what does app01 depend on?":
        deps = get_dependencies(model, "APP01")
        return (
            "APP01 depends on:\n- "
            + "\n- ".join(deps)
            + "\n\nCertainty: confirmed in the current model."
        )

    if q == "what communication must remain open for app02?":
        flows = get_required_flows_for_source(model, "APP02")
        if not flows:
            return "No required flows found for APP02."
        lines = []
        for flow in flows:
            lines.append(
                f"- {flow['source']} -> {flow['destination']}: {flow['purpose']}"
            )
        return (
            "Required communication for APP02:\n"
            + "\n".join(lines)
            + "\n\nCertainty: based on documented required flows."
        )

    if q == "what exact port and protocol does app01 use to reach the internal api?":
        item = get_port_protocol(model, "APP01", "Internal API on IAM01")
        if not item:
            return "No exact port/protocol entry found."
        return (
            f"APP01 reaches the Internal API on IAM01 using {item['protocol']} on port {item['port']}.\n"
            f"Purpose: {item['purpose']}\n"
            f"Certainty: {item['status']}."
        )

    if q == "is broad app_zone access aligned with the target security intent?":
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

    if q == "what parts of the network model are still unresolved or not fully confirmed?":
        questions = list_open_questions(model)
        if not questions:
            return "No open questions recorded."
        return (
            "Open questions in the current network model:\n- "
            + "\n- ".join(questions)
            + "\n\nCertainty: these are explicitly recorded as open questions."
        )

    return (
        "Question not supported in v1.\n\n"
        "Try one of these exact questions:\n"
        "- What does APP01 depend on?\n"
        "- What communication must remain open for APP02?\n"
        "- What exact port and protocol does APP01 use to reach the Internal API?\n"
        "- Is broad APP_ZONE access aligned with the target security intent?\n"
        "- What parts of the network model are still unresolved or not fully confirmed?"
    )


def main():
    model = load_model()
    print("Network AI Agent v1")
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