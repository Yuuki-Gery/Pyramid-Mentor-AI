from app.agents.expert_base import ExpertAgent


class LearningAgent(ExpertAgent):
    """学习导师 — 帮助用户高效学习、构建知识体系"""

    def __init__(self, llm, retriever=None):
        super().__init__(llm, retriever)
        self.expertise = "学习导师"
        self.expertise_keywords = [
            "学习", "知识", "读书", "课程", "考试", "自学",
            "学习方法", "记忆力", "理解", "知识体系", "学习计划",
            "技能提升", "学什么", "怎么学", "学习路线",
            "study", "learning", "skill", "knowledge"
        ]

    def _build_expert_prompt(self, message, context, rag_context, profile=None):
        base = super()._build_expert_prompt(message, context, rag_context, profile)
        return base + f"""

【学习导师特别关注】
- 根据用户目标推荐最佳学习路径
- 帮助构建系统化的知识体系而非碎片化学习
- 运用金字塔原理中的归类分组和逻辑递进来组织学习内容
- 关注学习中的刻意练习和反馈循环
- 帮助用户建立"输入→思考→输出"的完整学习闭环
"""