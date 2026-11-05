from pydantic import BaseModel


class ProblemAnalysis(BaseModel):

    problem_definition: str

    goal: str

    constraints: list[str]

    missing_information: list[str]

    next_steps: list[str]