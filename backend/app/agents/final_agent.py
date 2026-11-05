from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResponse
from app.prompts.final_prompt import build_final_prompt


class FinalMentorAgent(BaseAgent):

    name = "final"

    async def run(self, message: str, context: dict = None):
        context = context or {}
        profile = context.get("profile", {})
        history = context.get("history", [])
        casual_mode = context.get("casual_mode", False)
        custom_prompt = context.get("custom_prompt", None)
        analyses = {
            key: context.get(key)
            for key in ("problem", "pyramid", "teacher", "expert")
            if context.get(key)
        }

        prompt = build_final_prompt(
            message,
            profile,
            history,
            casual_mode,
            custom_prompt,
            analyses,
        )
        response = await self.llm.chat([{"role": "user", "content": prompt}])

        parsed = self.clean_json(response)
        if not parsed:
            parsed = {}
        parsed = self.fill_json(parsed, {"mentor_response": response})
        mentor_response = parsed.get("mentor_response", response)

        nested = self.clean_json(mentor_response)
        if nested and "mentor_response" in nested:
            mentor_response = nested["mentor_response"]

        return AgentResponse(
            agent="final",
            summary=mentor_response[:200],
            analysis={"mentor_response": mentor_response},
            recommendations=["根据用户情况持续提供行动建议"]
        )
