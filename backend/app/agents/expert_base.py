from typing import Optional

from app.agents.base_agent import BaseAgent
from app.core.logging import logger
from app.rag.retriever import KnowledgeRetriever


class ExpertAgent(BaseAgent):
    """专家 Agent 基类，所有专家继承此类"""

    def __init__(self, llm, retriever: KnowledgeRetriever = None):
        super().__init__(llm, retriever)
        self.expertise = ""
        self.expertise_keywords = []

    def should_handle(self, message: str, context: dict = None) -> float:
        """判断是否应该由该专家处理，返回匹配分数 0-1"""
        message_lower = message.lower()
        keywords_found = sum(
            1 for kw in self.expertise_keywords
            if kw.lower() in message_lower
        )
        if len(self.expertise_keywords) == 0:
            return 0.0
        return min(keywords_found / len(self.expertise_keywords) * 1.5, 1.0)

    async def run(self, message: str, context: dict = None, profile: dict = None) -> Optional[dict]:
        """专家运行，会注入专业领域知识"""
        context = context or {}
        profile = profile or context.get("profile")
        rag_context = ""
        if self.retriever:
            try:
                docs = self.retriever.search(message, k=3)
                rag_context = "\n".join([d.get("content", "") for d in docs])
            except Exception:
                logger.exception("Expert RAG retrieval failed for {}", self.name)

        prompt = self._build_expert_prompt(message, context, rag_context, profile)
        response = await self.llm.chat([{"role": "user", "content": prompt}])
        return self._parse_response(response)

    def _build_expert_prompt(self, message: str, context: dict, rag_context: str, profile: dict = None) -> str:
        """构建专家提示词，子类可覆盖"""
        profile_str = ""
        if profile:
            profile_str = f"""
用户画像：
- 背景：{profile.get('background', '未知')}
- 技能：{', '.join(profile.get('skills', [])[:5])}
- 兴趣：{', '.join(profile.get('interests', [])[:5])}
- 当前目标：{profile.get('goal', '未知')}
"""

        return f"""你是一位【{self.expertise}】领域的专业导师。

你的任务是基于金字塔原理，帮助用户分析问题并提供专业建议。

{profile_str}

用户问题：{message}

参考知识：
{rag_context}

历史对话：
{context.get('history', []) if context else []}

请按照以下结构回答：
1. **问题定义** — 用一句话重新定义用户的核心问题
2. **专业分析** — 基于你的专业领域，拆解问题的关键要素
3. **金字塔结构** — 用金字塔结构组织你的分析（结论先行，论点分层）
4. **行动建议** — 给出具体、可执行的下一步行动
5. **核心判断** — 对用户的处境做出一个核心判断

请以专业、温暖但直接的方式回答。"""

    def _parse_response(self, response: str) -> dict:
        """解析响应，子类可覆盖"""
        return {
            "analysis": response,
            "expertise": self.expertise,
        }
