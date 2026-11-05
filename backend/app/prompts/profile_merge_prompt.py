import json


def build_profile_merge_prompt(
    old_profile,
    new_profile,
    *args
):

    return f"""
你是一名用户长期记忆管理专家。


你的任务：

合并旧用户画像和最新用户信息。


规则：

1. 保留旧信息中长期有效内容

2. 添加新的有效信息

3. 删除重复内容

4. 不删除仍然有效的信息

5. 不保存短期状态

6. 不虚构用户资料


目标：

生成准确、稳定、长期可使用的用户画像。


严格返回JSON。


格式：

{{
"background":"",
"skills":[],
"interests":[],
"goal":"",
"resources":[]
}}


旧Profile：

{json.dumps(
old_profile,
ensure_ascii=False,
indent=2
)}


新Profile：

{json.dumps(
new_profile,
ensure_ascii=False,
indent=2
)}

"""