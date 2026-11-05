from app.agents.base_agent import BaseAgent
from app.schemas.agent import AgentResponse
from app.prompts.pyramid_prompt import build_pyramid_prompt


class PyramidAgent(BaseAgent):

    name = "pyramid"

    async def run(
        self,
        message: str,
        context: dict = None
    ):
        context = context or {}

        profile = context.get("profile", {})
        knowledge = self.safe_retrieval(message, k=3)

        # 检测是否需要深度分析
        needs_deep_analysis = any(kw in message for kw in [
            "分析", "解决", "问题", "怎么办", "如何", "决策",
            "选择", "比较", "评估", "规划", "转型", "创业"
        ])

        prompt = build_pyramid_prompt(message, profile, knowledge)
        response = await self.safe_llm_call(prompt)

        # 提取关键部分用于摘要
        summary = response[:300] if len(response) > 300 else response

        # 从回复中提取SCQA部分
        scqa_section = ""
        mece_section = ""
        tree_section = ""

        if "【SCQA完整分析】" in response:
            parts = response.split("【")
            for part in parts:
                if part.startswith("SCQA完整分析"):
                    scqa_section = "【" + part.split("【MECE分解】")[0] if "【MECE分解】" in part else "【" + part
                elif part.startswith("MECE分解"):
                    mece_section = "【" + part.split("【逻辑树分析】")[0] if "【逻辑树分析】" in part else "【" + part
                elif part.startswith("逻辑树分析"):
                    tree_section = "【" + part.split("【结构化解决方案】")[0] if "【结构化解决方案】" in part else "【" + part

        return AgentResponse(
            agent="pyramid",
            summary=summary,
            analysis={
                "structure": response,
                "scqa": scqa_section,
                "mece": mece_section,
                "tree": tree_section,
                "has_deep_analysis": needs_deep_analysis,
            },
            key_points=[
                "SCQA分析",
                "MECE拆解",
                "逻辑树",
                "结构化解决方案",
                "思维引导",
            ]
        )
