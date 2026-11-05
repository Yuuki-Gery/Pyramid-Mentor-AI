from app.agents.expert_base import ExpertAgent


class EntrepreneurAgent(ExpertAgent):
    """创业导师 — 帮助创业者分析商业模式、市场机会、产品验证"""

    def __init__(self, llm, retriever=None):
        super().__init__(llm, retriever)
        self.expertise = "创业导师"
        self.expertise_keywords = [
            "创业", "商业模式", "融资", "产品", "市场", "创业想法",
            "startup", "business", "产品验证", "MVP", "增长",
            "商业计划", "bp", "融资", "合伙人"
        ]

    def _build_expert_prompt(self, message, context, rag_context, profile=None):
        base = super()._build_expert_prompt(message, context, rag_context, profile)
        return base + f"""

【创业导师特别关注】
- 评估创业想法的可行性和市场空间
- 分析商业模式的关键假设和风险
- 关注最小可行产品（MVP）的验证路径
- 考虑资源配置和优先级排序
"""