from app.agents.expert_base import ExpertAgent


class CareerAgent(ExpertAgent):
    """职业导师 — 帮助用户规划职业发展、转型、提升"""

    def __init__(self, llm, retriever=None):
        super().__init__(llm, retriever)
        self.expertise = "职业导师"
        self.expertise_keywords = [
            "职业", "工作", "跳槽", "面试", "升职", "加薪",
            "职业规划", "职业发展", "转行", "简历", "offer",
            "职场", "晋升", "团队管理", "找工作", "裸辞",
            "career", "job", "promotion"
        ]

    def _build_expert_prompt(self, message, context, rag_context, profile=None):
        base = super()._build_expert_prompt(message, context, rag_context, profile)
        return base + f"""

【职业导师特别关注】
- 分析用户的职业技能和优势，找到核心竞争力
- 评估职业转型的可行性和最佳路径
- 关注市场趋势与职业方向的匹配度
- 帮助制定短期和长期职业发展计划
"""