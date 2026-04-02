from agents.agent_registry import ask_agent, list_agents, get_agent_definition


def ask_single_agent(agent_id: str, question: str):
    definition = get_agent_definition(agent_id)
    answer, prompt, context = ask_agent(agent_id, question)

    return {
        "question": question,
        "agent_id": agent_id,
        "agent_label": definition.label,
        "agent_description": definition.description,
        "answer": answer,
        "intents": context.get("intents", [context.get("intent", "unknown")]),
        "entities": context.get("entities", {}),
    }


def compare_agents(question: str, agent_ids: list[str] | None = None):
    selected_agent_ids = agent_ids or [agent["agent_id"] for agent in list_agents()]
    results = []

    for agent_id in selected_agent_ids:
        result = ask_single_agent(agent_id, question)
        results.append(result)

    return {
        "question": question,
        "results": results,
    }