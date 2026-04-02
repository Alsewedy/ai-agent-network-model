from fastapi import APIRouter, Body

from agents.agent_registry import list_agents
from models.schemas import (
    AskRequest,
    AskResponse,
    CompareRequest,
    CompareResponse,
    CompareItem,
)
from services.agent_service import ask_single_agent, compare_agents
from services.retriever_analysis_service import analyze_retrieval

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/agents")
def get_agents():
    return {"agents": list_agents()}


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = ask_single_agent(request.agent_id, request.question)
    return AskResponse(**result)


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest):
    result = compare_agents(request.question, request.agent_ids)
    return CompareResponse(
        question=result["question"],
        results=[CompareItem(**item) for item in result["results"]],
    )


@router.post("/analyze-retrieval")
def analyze_retrieval_route(
    payload: dict = Body(...)
):
    question = str(payload.get("question", "")).strip()
    top_k = int(payload.get("top_k", 10))

    if not question:
        return {
            "error": "Question is required."
        }

    return analyze_retrieval(question=question, top_k=top_k)