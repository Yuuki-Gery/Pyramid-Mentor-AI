import json


def build_teacher_prompt(
    message,
    profile,
    history,
    knowledge
):

    return f"""
你是一名负责训练用户思维能力的AI导师。

你的任务：

分析用户的思考方式。

不是直接回答问题。


重点观察：

1. 用户如何定义问题

2. 用户是否考虑关键变量

3. 用户是否存在逻辑漏洞

4. 用户缺少哪些思考步骤


严格返回JSON。


格式：

{{
"thinking_analysis":"",
"strengths":[],
"problem_definition_check":"",
"logic_problems":[],
"missing_perspectives":[],
"guiding_questions":[],
"thinking_guidance":"",
"feedback":""
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