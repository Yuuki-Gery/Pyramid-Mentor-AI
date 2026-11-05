from typing import List, Optional, Tuple
from app.agents.expert_base import ExpertAgent
from app.agents.entrepreneur_agent import EntrepreneurAgent
from app.agents.career_agent import CareerAgent
from app.agents.learning_agent import LearningAgent
from app.agents.business_agent import BusinessAgent
from app.agents.growth_agent import GrowthAgent


# 默认领域（当不匹配任何专家时）
GENERAL_DOMAIN = "general"


def create_default_experts(llm, retriever=None) -> List[ExpertAgent]:
    """创建所有专家实例"""
    return [
        EntrepreneurAgent(llm, retriever),
        CareerAgent(llm, retriever),
        LearningAgent(llm, retriever),
        BusinessAgent(llm, retriever),
        GrowthAgent(llm, retriever),
    ]


class ExpertSelector:
    """专家选择器 — 根据用户问题自动匹配合适的专家"""

    def __init__(self, experts: List[ExpertAgent]):
        self.experts = experts

    def select(self, message: str, context: dict = None) -> Tuple[ExpertAgent, str]:
        """
        根据用户消息选择最合适的专家
        返回: (选中的专家, 领域名称)
        """
        scores = []
        for expert in self.experts:
            score = expert.should_handle(message, context)
            scores.append((expert, score))

        # 按分数排序，取最高分
        scores.sort(key=lambda x: x[1], reverse=True)
        best_expert, best_score = scores[0]

        # 如果最高分太低，返回 None（使用默认处理）
        if best_score < 0.3:
            return None, GENERAL_DOMAIN

        return best_expert, best_expert.expertise

    def get_domain_for_message(self, message: str) -> str:
        """仅判断领域，不返回专家实例"""
        message_lower = message.lower()

        domain_scores = {
            "创业": 0,
            "职业": 0,
            "学习": 0,
            "商业": 0,
            "成长": 0,
        }

        # 创业关键词
        startup_kw = ["创业", "融资", "商业计划", "startup", "mvp", "产品验证", "合伙人"]
        domain_scores["创业"] = sum(1 for kw in startup_kw if kw in message_lower)

        # 职业关键词
        career_kw = ["工作", "跳槽", "面试", "职业", "offer", "简历", "升职", "职场"]
        domain_scores["职业"] = sum(1 for kw in career_kw if kw in message_lower)

        # 学习关键词
        learn_kw = ["学习", "读书", "课程", "知识", "技能", "自学", "考试"]
        domain_scores["学习"] = sum(1 for kw in learn_kw if kw in message_lower)

        # 商业关键词
        biz_kw = ["商业", "业务", "利润", "成本", "战略", "市场", "管理", "决策"]
        domain_scores["商业"] = sum(1 for kw in biz_kw if kw in message_lower)

        # 成长关键词
        growth_kw = ["成长", "习惯", "目标", "自律", "迷茫", "焦虑", "拖延", "时间管理"]
        domain_scores["成长"] = sum(1 for kw in growth_kw if kw in message_lower)

        best_domain = max(domain_scores, key=domain_scores.get)
        if domain_scores[best_domain] == 0:
            return GENERAL_DOMAIN

        return best_domain