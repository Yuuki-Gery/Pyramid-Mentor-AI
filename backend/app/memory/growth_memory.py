"""
高级成长记忆系统
记录用户的成长轨迹、目标变化、决策历史
基于Redis实现持久化
"""
import json
import time
from typing import Optional
from app.memory.redis_client import redis_client


class GrowthMemory:
    """成长记忆：记录用户的思维成长历程"""

    def __init__(self):
        self.redis = redis_client

    # ========= 成长轨迹 =========

    def _growth_key(self, user_id: str) -> str:
        return f"growth:{user_id}:trajectory"

    def add_milestone(self, user_id: str, milestone: dict) -> list:
        """
        记录一个成长里程碑
        milestone = {
            "type": "认知突破|技能提升|思维转变",
            "title": "里程碑标题",
            "description": "详细描述",
            "timestamp": "ISO时间戳"
        }
        """
        key = self._growth_key(user_id)
        milestones = self.get_milestones(user_id)
        milestones.append(milestone)
        # 只保留最近50条
        if len(milestones) > 50:
            milestones = milestones[-50:]
        self.redis.set(key, json.dumps(milestones, ensure_ascii=False))
        return milestones

    def get_milestones(self, user_id: str) -> list:
        data = self.redis.get(self._growth_key(user_id))
        if not data:
            return []
        return json.loads(data)

    # ========= 目标变化历史 =========

    def _goal_key(self, user_id: str) -> str:
        return f"growth:{user_id}:goals"

    def add_goal(self, user_id: str, goal: dict) -> list:
        """
        记录用户的目标/问题
        goal = {
            "goal": "目标描述",
            "context": "背景",
            "status": "进行中|已完成|已放弃",
            "timestamp": "ISO时间戳"
        }
        """
        key = self._goal_key(user_id)
        goals = self.get_goals(user_id)
        goals.append(goal)
        self.redis.set(key, json.dumps(goals, ensure_ascii=False))
        return goals

    def get_goals(self, user_id: str) -> list:
        data = self.redis.get(self._goal_key(user_id))
        if not data:
            return []
        return json.loads(data)

    def update_goal_status(self, user_id: str, goal_idx: int, status: str):
        """更新某个目标的状态"""
        goals = self.get_goals(user_id)
        if 0 <= goal_idx < len(goals):
            goals[goal_idx]["status"] = status
            self.redis.set(self._goal_key(user_id), json.dumps(goals, ensure_ascii=False))

    # ========= 决策历史 =========

    def _decision_key(self, user_id: str) -> str:
        return f"growth:{user_id}:decisions"

    def add_decision(self, user_id: str, decision: dict) -> list:
        """
        记录用户的重大决策
        decision = {
            "topic": "决策主题",
            "options": ["选项1", "选项2"],
            "choice": "最终选择",
            "reason": "理由",
            "outcome": "结果(待评估)",
            "timestamp": "ISO时间戳"
        }
        """
        key = self._decision_key(user_id)
        decisions = self.get_decisions(user_id)
        decisions.append(decision)
        self.redis.set(key, json.dumps(decisions, ensure_ascii=False))
        return decisions

    def get_decisions(self, user_id: str) -> list:
        data = self.redis.get(self._decision_key(user_id))
        if not data:
            return []
        return json.loads(data)

    # ========= 思维模式档案 =========

    def _pattern_key(self, user_id: str) -> str:
        return f"growth:{user_id}:patterns"

    def update_thinking_pattern(self, user_id: str, pattern: dict):
        """
        更新用户思维模式分析
        pattern = {
            "strengths": ["结构化思维", "逻辑分析"],
            "weaknesses": ["容易发散", "忽略细节"],
            "preferred_style": "演绎/归纳/混合",
            "improvement_areas": ["MECE应用", "结论先行"],
            "last_analysis": "ISO时间戳"
        }
        """
        key = self._pattern_key(user_id)
        existing = self.get_thinking_pattern(user_id) or {}
        existing.update(pattern)
        self.redis.set(key, json.dumps(existing, ensure_ascii=False))

    def get_thinking_pattern(self, user_id: str) -> Optional[dict]:
        data = self.redis.get(self._pattern_key(user_id))
        if not data:
            return None
        return json.loads(data)

    # ========= 综合成长报告 =========

    def generate_growth_summary(self, user_id: str) -> dict:
        """生成用户的综合成长报告"""
        milestones = self.get_milestones(user_id)
        goals = self.get_goals(user_id)
        decisions = self.get_decisions(user_id)
        pattern = self.get_thinking_pattern(user_id)

        # 统计
        active_goals = [g for g in goals if g.get("status") == "进行中"]
        completed_goals = [g for g in goals if g.get("status") == "已完成"]

        return {
            "milestones_count": len(milestones),
            "recent_milestones": milestones[-5:],
            "active_goals_count": len(active_goals),
            "completed_goals_count": len(completed_goals),
            "active_goals": active_goals[-3:],
            "decisions_count": len(decisions),
            "recent_decisions": decisions[-3:],
            "thinking_pattern": pattern,
            "summary": self._generate_summary_text(milestones, goals, pattern),
        }

    def _generate_summary_text(self, milestones: list, goals: list, pattern: Optional[dict]) -> str:
        """生成成长摘要文本"""
        parts = []
        if pattern:
            strengths = pattern.get("strengths", [])
            weaknesses = pattern.get("weaknesses", [])
            if strengths:
                parts.append(f"思维优势：{'、'.join(strengths)}")
            if weaknesses:
                parts.append(f"待改进：{'、'.join(weaknesses)}")

        completed = [g for g in goals if g.get("status") == "已完成"]
        if completed:
            parts.append(f"已完成目标：{len(completed)}个")

        if milestones:
            latest = milestones[-1]
            parts.append(f"最近成长：{latest.get('title', '')}")

        return "；".join(parts) if parts else "暂无足够的成长数据"


growth_memory = GrowthMemory()