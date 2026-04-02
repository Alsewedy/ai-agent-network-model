from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    agent_id: str


class AskResponse(BaseModel):
    question: str
    agent_id: str
    agent_label: str
    agent_description: str
    answer: str
    intents: list[str]
    entities: dict


class CompareRequest(BaseModel):
    question: str
    agent_ids: list[str] | None = None


class CompareItem(BaseModel):
    agent_id: str
    agent_label: str
    agent_description: str
    answer: str
    intents: list[str]
    entities: dict


class CompareResponse(BaseModel):
    question: str
    results: list[CompareItem]