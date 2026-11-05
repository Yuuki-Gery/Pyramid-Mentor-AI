from app.llm.manager import get_llm

from app.agents.problem_agent import ProblemAgent
from app.agents.pyramid_agent import PyramidAgent
from app.agents.teacher_agent import TeacherAgent
from app.agents.final_agent import FinalMentorAgent
from app.agents.profile_agent import ProfileAgent
from app.agents.profile_merge_agent import ProfileMergeAgent

from app.rag.retriever import retriever


class AgentManager:

    def __init__(self):

        llm = get_llm()

        self.agents = {
            "problem": ProblemAgent(llm, retriever),
            "pyramid": PyramidAgent(llm, retriever),
            "teacher": TeacherAgent(llm, retriever),
            "final": FinalMentorAgent(llm, retriever),
            "profile": ProfileAgent(llm, retriever),
            "profile_merge": ProfileMergeAgent(llm, retriever),
        }

        # 专家 Agent 系统
        from app.agents.expert_selector import create_default_experts, ExpertSelector
        self.experts = create_default_experts(llm, retriever)
        self.expert_selector = ExpertSelector(self.experts)

    async def run(self, agent_name: str, message: str, context: dict = None):
        agent = self.agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        return await agent.run(message, context)

    async def run_expert(self, message: str, context: dict = None):
        """自动选择并运行最合适的专家 Agent"""
        expert, domain = self.expert_selector.select(message, context)
        if expert is None:
            return {"domain": "general", "analysis": None}
        result = await expert.run(message, context)
        result["domain"] = domain
        return result