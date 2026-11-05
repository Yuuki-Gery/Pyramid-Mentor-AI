from fastapi import APIRouter, Depends
from app.agents.agent_manager import AgentManager

router = APIRouter(prefix="/api/expert", tags=["专家系统测试"])


# 共享的 agent_manager 实例（由 main.py 注入）
agent_manager: AgentManager = None


def get_agent_manager():
    if agent_manager is None:
        from app.agents.agent_manager import AgentManager
        return AgentManager()
    return agent_manager


@router.get("/domains")
async def list_expert_domains():
    """列出所有可用的专家领域"""
    manager = get_agent_manager()
    return {
        "domains": [
            {"name": "entrepreneur", "label": "创业导师"},
            {"name": "career", "label": "职业导师"},
            {"name": "learning", "label": "学习导师"},
            {"name": "business", "label": "商业分析导师"},
            {"name": "growth", "label": "成长导师"},
        ],
        "total": 5,
    }


@router.post("/select")
async def select_expert(message: str):
    """测试专家选择 - 根据消息匹配合适的专家"""
    manager = get_agent_manager()
    expert, domain = manager.expert_selector.select(message)
    if expert is None:
        return {
            "selected_domain": "general",
            "message": "未匹配到特定专家，将使用默认处理",
        }
    return {
        "selected_domain": domain,
        "expertise": expert.expertise,
        "match_score": expert.should_handle(message),
    }


@router.post("/chat")
async def chat_with_expert(message: str):
    """直接与匹配的专家对话（测试用）"""
    manager = get_agent_manager()
    expert, domain = manager.expert_selector.select(message)
    if expert is None:
        return {
            "domain": "general",
            "analysis": "未匹配到特定专家领域",
            "note": "请尝试使用更具体的问题描述",
        }
    result = await expert.run(message, {"history": []})
    return {
        "domain": domain,
        "analysis": result.get("analysis", ""),
    }