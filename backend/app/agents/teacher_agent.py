from app.agents.base_agent import BaseAgent
from app.core.logging import logger

from app.schemas.agent import AgentResponse

from app.prompts.teacher_prompt import build_teacher_prompt



class TeacherAgent(BaseAgent):

    name = "teacher"


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


        prompt = build_teacher_prompt(
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
                    "thinking_analysis":"",
                    "problem_definition_check":"",
                    "logic_problems":[],
                    "guiding_questions":[],
                    "thinking_guidance":"",
                    "feedback":""
                }
            )


            return AgentResponse(

                agent="teacher",

                summary=data.get(
                    "thinking_analysis",
                    ""
                ),

                analysis=data,

                questions=data.get(
                    "guiding_questions",
                    []
                ),

                recommendations=[

                    data.get(
                        "thinking_guidance",
                        ""
                    )

                ]

            )


        except Exception:
            logger.exception("Teacher agent response parse failed")


            return AgentResponse(

                agent="teacher",

                summary=response,

                analysis={
                    "raw_response": response
                }

            )