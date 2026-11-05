from app.prompts.final_prompt import build_final_prompt


def test_final_prompt_includes_multi_agent_analyses():
    prompt = build_final_prompt(
        message="我想转行",
        profile={"goal": "转行"},
        history=[],
        analyses={
            "pyramid": {"scqa": "情境、冲突、问题"},
            "expert": {"domain": "career", "analysis": "先验证可迁移能力"},
        },
    )

    assert "问题诊断 / 金字塔分析" in prompt
    assert "情境、冲突、问题" in prompt
    assert "先验证可迁移能力" in prompt


def test_custom_casual_prompt_takes_precedence():
    prompt = build_final_prompt(
        "你好",
        {},
        [],
        casual_mode=True,
        custom_prompt="只有这段自定义提示",
    )
    assert prompt == "只有这段自定义提示"
