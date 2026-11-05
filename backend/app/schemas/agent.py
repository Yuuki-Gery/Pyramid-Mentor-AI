from pydantic import BaseModel
from typing import Any, Dict, List


class AgentResponse(BaseModel):

    agent: str

    summary: str = ""

    analysis: Dict[str, Any] = {}

    key_points: List[str] = []

    questions: List[str] = []

    recommendations: List[str] = []