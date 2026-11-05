from app.agents.base_agent import BaseAgent
from app.core.logging import logger

from app.schemas.agent import AgentResponse

from app.prompts.problem_prompt import build_problem_prompt



class ProblemAgent(BaseAgent):

    name = "problem"


    async def run(
        self,
        message: str,
        context: dict = None
    ):

        context = context or {}


        profile = context.get(
            "profile",
            {}
        )


        history = context.get(
            "history",
            []
        )


        knowledge = self.safe_retrieval(
            message,
            k=3
        )


        prompt = build_problem_prompt(
            message,
            profile,
            history,
            knowledge
        )


        response = await self.safe_llm_call(
            prompt
        )


        try:

            data = self.clean_json(
                response
            )


            data = self.fill_json(
                data,
                {
                    "problem_definition":"",
                    "goal":"",
                    "constraints":[],
                    "missing_information":[],
                    "next_steps":[]
                }
            )


            return AgentResponse(

                agent="problem",

                summary=data.get(
                    "problem_definition",
                    ""
                ),

                analysis=data,

                key_points=data.get(
                    "next_steps",
                    []
                ),

                questions=data.get(
                    "missing_information",
                    []
                )

            )


        except Exception:
            logger.exception("Problem agent response parse failed")


            return AgentResponse(

                agent="problem",

                summary=response,

                analysis={
                    "raw_response": response
                }

            )