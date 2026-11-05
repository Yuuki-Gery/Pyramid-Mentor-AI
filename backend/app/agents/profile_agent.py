from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResponse
from app.prompts.profile_prompt import build_profile_prompt


class ProfileAgent(BaseAgent):

    name = "profile"


    async def run(
        self,
        message: str,
        context: dict = None
    ):

        context = context or {}


        prompt = build_profile_prompt(
            message,
            context.get(
                "profile",
                {}
            ),
            context.get(
                "history",
                []
            ),
            context.get(
                "knowledge",
                ""
            )
        )


        response = await self.llm.chat(
            [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        data = self.clean_json(
            response
        )


        data = self.fill_json(
            data,
            {
                "background": "",

                "skills": [],

                "interests": [],

                "goal": "",

                "resources": []
            }
        )


        return AgentResponse(

            agent="profile",

            summary=data.get(
                "background",
                ""
            ),

            analysis=data,

            key_points=data.get(
                "skills",
                []
            )

        )