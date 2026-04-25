from dataclasses import dataclass
from typing import Callable

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
            "A conservative structured-first baseline agent for the new knowledge "
            "architecture. It relies primarily on model.yaml and other structured "
            "domain knowledge, with no RAG retrieval layer."
        ),
        strengths=[
            "Simple baseline reference",
            "Strong structured grounding",
            "Low retrieval complexity",
            "Conservative answer behavior",
        ],
        limitations=[
            "No dedicated RAG retrieval layer",
            "Less contextual richness than v7 and v8",
            "Weaker orchestration than v8",
        ],
        load_runtime=_load_v6_runtime,
        answer=_answer_v6,
    ),
    "v7": AgentDefinition(
        agent_id="v7",
        label="v7 – Hybrid Structured + RAG Agent",
        description=(
            "A hybrid agent for the new knowledge architecture that keeps structured "
            "facts as the primary source of truth while using retrieved RAG chunks "
            "as supporting context."
        ),
        strengths=[
            "Structured-first grounding",
            "Dedicated RAG retrieval layer",
            "Richer supporting context than v6",
            "Good middle-ground complexity",
        ],
        limitations=[
            "Less refined orchestration than v8",
            "Still simpler than the advanced multi-intent agent",
        ],
        load_runtime=_load_v7_runtime,
        answer=_answer_v7,
    ),
    "v8": AgentDefinition(
        agent_id="v8",
        label="v8 – Advanced Hybrid Orchestration Agent",
        description=(
            "The most advanced version for the new knowledge architecture. It uses "
            "multi-intent reasoning, dynamic retrieval scaling, richer entity and "
            "service handling, stronger orchestration, and better context assembly."
        ),
        strengths=[
            "Multi-intent reasoning",
            "Dynamic retrieval scaling",
            "Better service/entity handling",
            "Richer orchestration and context assembly",
            "Best support for complex audit-style questions",
        ],
        limitations=[
            "More complex than v6 and v7",
            "Heavier prompt/context construction",
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