from dataclasses import dataclass
from typing import Callable, Any

from agents import agent_v6
from agents import agent_v7
from agents import agent_v8


@dataclass
class AgentDefinition:
    agent_id: str
    label: str
    description: str
    strengths: list[str]
    limitations: list[str]
    load_runtime: Callable[[], dict]
    answer: Callable[[dict, str], tuple[str, str, dict]]


def _load_v6_runtime() -> dict:
    model = agent_v6.load_model()
    return {
        "model": model,
        "alias_map": None,
    }


def _answer_v6(runtime: dict, question: str):
    return agent_v6.answer_question(runtime["model"], question)


def _load_v7_runtime() -> dict:
    model = agent_v7.load_model()
    return {
        "model": model,
        "alias_map": None,
    }


def _answer_v7(runtime: dict, question: str):
    return agent_v7.answer_question(runtime["model"], question)


def _load_v8_runtime() -> dict:
    model = agent_v8.load_model()
    alias_map = agent_v8.build_alias_map(model)
    return {
        "model": model,
        "alias_map": alias_map,
    }


def _answer_v8(runtime: dict, question: str):
    return agent_v8.answer_question(
        runtime["model"],
        runtime["alias_map"],
        question,
    )


AGENTS: dict[str, AgentDefinition] = {
    "v6": AgentDefinition(
        agent_id="v6",
        label="v6 – Structured Baseline Agent",
        description=(
            "A conservative YAML-first baseline agent that uses structured facts "
            "as the primary source of truth and simple Markdown snippets as "
            "supporting context."
        ),
        strengths=[
            "Simple baseline reference",
            "Strong YAML grounding",
            "Conservative answer behavior",
        ],
        limitations=[
            "Uses simple snippet extraction",
            "No dedicated RAG retrieval layer",
        ],
        load_runtime=_load_v6_runtime,
        answer=_answer_v6,
    ),
    "v7": AgentDefinition(
        agent_id="v7",
        label="v7 – Hybrid YAML + RAG Agent",
        description=(
            "A hybrid agent that keeps YAML as the primary source of truth while "
            "using retrieved RAG chunks instead of direct Markdown snippets for "
            "supporting context."
        ),
        strengths=[
            "Dedicated RAG retrieval layer",
            "Richer supporting context",
            "Better scalability than v6",
        ],
        limitations=[
            "Less refined than v8",
            "Still an earlier hybrid version",
        ],
        load_runtime=_load_v7_runtime,
        answer=_answer_v7,
    ),
    "v8": AgentDefinition(
        agent_id="v8",
        label="v8 – Advanced Hybrid Orchestration Agent",
        description=(
            "The current tuned version with multi-intent reasoning, dynamic "
            "retrieval scaling, improved entity handling, and a stronger prompt "
            "structure."
        ),
        strengths=[
            "Multi-intent reasoning",
            "Dynamic top-k scaling",
            "Better service/entity handling",
            "Improved prompt orchestration",
        ],
        limitations=[
            "More complex than earlier versions",
            "Still depends on file-based retrieval rather than full vector RAG",
        ],
        load_runtime=_load_v8_runtime,
        answer=_answer_v8,
    ),
}


_LOADED_RUNTIMES: dict[str, dict] = {}


def get_agent_definition(agent_id: str) -> AgentDefinition:
    if agent_id not in AGENTS:
        raise ValueError(f"Unknown agent_id: {agent_id}")
    return AGENTS[agent_id]


def get_agent_runtime(agent_id: str) -> dict:
    if agent_id not in _LOADED_RUNTIMES:
        definition = get_agent_definition(agent_id)
        _LOADED_RUNTIMES[agent_id] = definition.load_runtime()
    return _LOADED_RUNTIMES[agent_id]


def ask_agent(agent_id: str, question: str):
    definition = get_agent_definition(agent_id)
    runtime = get_agent_runtime(agent_id)
    return definition.answer(runtime, question)


def list_agents() -> list[dict]:
    return [
        {
            "agent_id": agent.agent_id,
            "label": agent.label,
            "description": agent.description,
            "strengths": agent.strengths,
            "limitations": agent.limitations,
        }
        for agent in AGENTS.values()
    ]