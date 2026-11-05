import json


def build_problem_prompt(
    message,
    profile,
    history,
    knowledge
):

    return f"""
你是一名专业的问题诊断专家。

你的任务：

不是解决用户问题。

而是帮助导师系统准确理解：

- 用户真正的问题
- 用户目标
- 限制条件
- 缺失信息


分析原则：

1. 区分表面问题和真实问题

2. 找出隐藏假设

3. 判断用户当前阶段

4. 找出影响决策的重要变量


严格返回JSON。

不要Markdown。

不要解释。


格式：

{{
"problem_definition":"",
"goal":"",
"current_stage":"",
"constraints":[],
"hidden_assumptions":[],
"missing_information":[],
"next_steps":[]
}}


用户画像：

{json.dumps(
profile,
ensure_ascii=False,
indent=2
)}


历史：

{json.dumps(
history,
ensure_ascii=False,
indent=2
)}


用户问题：

{message}


知识库：

{knowledge}

"""