import asyncio

from app.core.logging import logger
from app.services.memory_manager import memory_manager
from app.services.profile_manager import ProfileManager


class MentorService:

    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.profile_manager = ProfileManager(agent_manager)

    CASUAL_KEYWORDS = [
        "你好", "您好", "嗨", "hi", "hello", "hey",
        "在吗", "在么", "早上好", "下午好", "晚上好",
        "你好呀", "哈喽", "hi there",
        "谢谢", "感谢", "thanks", "thank you",
        "好的", "知道了", "明白", "ok", "okay",
        "再见", "bye", "拜拜", "回头见",
        "你是谁", "你能做什么", "介绍一下你自己",
        "测试", "test",
    ]

    def _is_casual(self, message: str) -> bool:
        msg = message.strip()
        if len(msg) <= 6:
            return True
        msg_lower = msg.lower()
        for kw in self.CASUAL_KEYWORDS:
            if kw in msg_lower:
                return True
        return False

    async def _get_casual_response(self, message: str, history: list, profile: dict) -> str:
        prompt = f"""你是金字塔导师AI。用户发了一条简短消息，请用自然、友好、人类的方式回复。

用户消息: {message}

要求:
- 像朋友一样自然回应
- 如果用户打招呼，就友好回应
- 如果用户问你是谁，简单介绍你是金字塔导师AI
- 如果用户说谢谢，客气回应
- 不要结构化分析
- 不要输出JSON
- 简短自然，20-50字
"""
        try:
            resp = await asyncio.wait_for(
                self.agent_manager.run("final", message, {
                    "profile": profile, "history": history,
                    "casual_mode": True, "custom_prompt": prompt
                }),
                timeout=10.0
            )
            if resp and hasattr(resp, "analysis") and resp.analysis:
                return resp.analysis.get("mentor_response", "") or resp.summary
        except Exception:
            logger.exception("Casual response failed")
        return "你好呀！我是金字塔导师AI，有什么我可以帮你的吗？😊"

    def trim_history(self, history, limit=10):
        if not history:
            return []
        return history[-limit:]

    def trim_profile(self, profile):
        if not profile:
            return {}
        return {
            "background": profile.get("background", ""),
            "skills": profile.get("skills", [])[:10],
            "interests": profile.get("interests", [])[:10],
            "goal": profile.get("goal", ""),
            "resources": profile.get("resources", [])[:10]
        }

    async def safe_run(self, agent_name, message, context=None):
        try:
            return await asyncio.wait_for(
                self.agent_manager.run(agent_name, message, context), timeout=20.0
            )
        except asyncio.TimeoutError:
            logger.warning("{} timed out", agent_name)
            return None
        except Exception:
            logger.exception("{} failed", agent_name)
            return None

    async def process(self, message: str, session_id: str):
        try:
            return await asyncio.wait_for(
                self._process_impl(message, session_id), timeout=60.0
            )
        except asyncio.TimeoutError:
            return {
                "profile": {}, "mentor_response": "抱歉，请求超时了。请稍后重试。",
                "expert": {"domain": "general", "analysis": None}, "is_casual": False,
            }

    async def _process_impl(self, message: str, session_id: str):
        # Get history
        try:
            history = await asyncio.wait_for(
                asyncio.to_thread(memory_manager.get_history, session_id), timeout=5.0
            )
        except Exception:
            history = []
        history = self.trim_history(history)

        # Save user message
        try:
            await asyncio.wait_for(
                asyncio.to_thread(memory_manager.save_message, session_id, "user", message), timeout=3.0
            )
        except Exception:
            pass

        # Get profile
        try:
            profile = await asyncio.wait_for(
                self.profile_manager.update_profile(session_id, message), timeout=25.0
            )
        except Exception:
            profile = {}
        profile = self.trim_profile(profile)

        # Check if casual
        is_casual = self._is_casual(message)
        if is_casual:
            mentor_text = await self._get_casual_response(message, history, profile)
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(memory_manager.save_message, session_id, "assistant", mentor_text), timeout=3.0
                )
            except Exception:
                pass
            return {
                "profile": profile, "mentor_response": mentor_text,
                "expert": {"domain": "general", "analysis": None}, "is_casual": True,
            }

        # Full pipeline for real problems
        context = {"profile": profile, "history": history}
        problem_task = self.safe_run("problem", message, context)
        pyramid_task = self.safe_run("pyramid", message, context)
        teacher_task = self.safe_run("teacher", message, context)
        expert_task = self.safe_run_expert(message, context)

        try:
            problem, pyramid, teacher, expert_result = await asyncio.wait_for(
                asyncio.gather(problem_task, pyramid_task, teacher_task, expert_task), timeout=40.0
            )
        except asyncio.TimeoutError:
            problem = pyramid = teacher = None
            expert_result = {"domain": "general", "analysis": None}

        final_context = {
            "profile": profile, "history": history,
            "problem": problem.model_dump() if problem else {},
            "pyramid": pyramid.model_dump() if pyramid else {},
            "teacher": teacher.model_dump() if teacher else {},
            "expert": expert_result if expert_result else {"domain": "general", "analysis": None},
            "casual_mode": False,
        }

        try:
            final = await asyncio.wait_for(
                self.safe_run_final("final", message, final_context), timeout=15.0
            )
        except Exception:
            final = None

        if final:
            mentor_text = final.analysis.get("mentor_response", "")
        else:
            mentor_text = "当前导师服务暂时不可用，请稍后再试。"

        try:
            await asyncio.wait_for(
                asyncio.to_thread(memory_manager.save_message, session_id, "assistant", mentor_text), timeout=3.0
            )
        except Exception:
            pass

        return {
            "profile": profile, "mentor_response": mentor_text,
            "expert": expert_result, "is_casual": False,
        }

    async def safe_run_expert(self, message, context):
        try:
            return await asyncio.wait_for(
                self.agent_manager.run_expert(message, context), timeout=20.0
            )
        except asyncio.TimeoutError:
            return {"domain": "general", "analysis": None}
        except Exception:
            return {"domain": "general", "analysis": None}

    async def safe_run_final(self, agent_name, message, context):
        try:
            return await asyncio.wait_for(
                self.agent_manager.run(agent_name, message, context), timeout=15.0
            )
        except Exception:
            return None
