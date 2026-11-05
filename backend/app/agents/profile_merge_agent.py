from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResponse
from app.prompts.profile_merge_prompt import build_profile_merge_prompt


class ProfileMergeAgent(BaseAgent):

    name = "profile_merge"


    async def run(
        self,
        message: str,
        context: dict = None
    ):

        context = context or {}


        prompt = build_profile_merge_prompt(

            context.get(
                "old_profile",
                {}
            ),

            context.get(
                "new_profile",
                {}
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

            agent="profile_merge",

            summary=data.get(
                "background",
                ""
            ),

            analysis=data

        )