from app.agents.expert_base import ExpertAgent


class GrowthAgent(ExpertAgent):
    """成长导师 — 帮助用户规划个人成长、习惯养成、目标达成"""

    def __init__(self, llm, retriever=None):
        super().__init__(llm, retriever)
        self.expertise = "成长导师"
        self.expertise_keywords = [
            "成长", "习惯", "目标", "自律", "时间管理",
            "拖延", "效率", "自我提升", "个人发展",
            "人生", "方向", "迷茫", "焦虑", "心态",
            "读书", "运动", "健康", "情绪", "幸福感",
            "growth", "habit", "goal", "self-improvement"
        ]

    def _build_expert_prompt(self, message, context, rag_context, profile=None):
        base = super()._build_expert_prompt(message, context, rag_context, profile)
        return base + f"""

【成长导师特别关注】
- 帮助用户建立可持续的习惯系统而非追求短期改变
- 关注内在动机和价值观的梳理
- 用金字塔原理将大目标逐层分解为可执行的小行动
- 帮助用户建立反馈和反思机制
- 关注成长过程中的心态调整和持续动力维持
"""