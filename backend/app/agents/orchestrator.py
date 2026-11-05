from app.agents.agent_manager import AgentManager
from app.services.mentor_service import MentorService


class MentorOrchestrator:

    def __init__(self):
        self.manager = AgentManager()
        self.service = MentorService(self.manager)

    async def run(self, message: str, session_id: str):
        return await self.service.process(message, session_id)
