from app.agents.expert_base import ExpertAgent


class BusinessAgent(ExpertAgent):
    """商业分析导师 — 帮助用户分析商业问题、决策优化"""

    def __init__(self, llm, retriever=None):
        super().__init__(llm, retriever)
        self.expertise = "商业分析导师"
        self.expertise_keywords = [
            "商业", "业务", "公司", "利润", "成本", "收入",
            "战略", "竞争", "市场分析", "投资", "回报率",
            "管理", "组织", "流程", "效率", "增长策略",
            "business", "strategy", "market", "investment", "ROI",
            "决策", "数据分析", "指标", "KPI", "OKR"
        ]

    def _build_expert_prompt(self, message, context, rag_context, profile=None):
        base = super()._build_expert_prompt(message, context, rag_context, profile)
        return base + f"""

【商业分析导师特别关注】
- 用 MECE 原则（相互独立，完全穷尽）拆解商业问题
- 关注数据驱动的决策而非直觉判断
- 分析投入产出比和关键杠杆点
- 帮助构建可验证的商业假设和实验框架
"""