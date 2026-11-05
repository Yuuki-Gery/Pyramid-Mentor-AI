import json


def build_profile_prompt(
    message,
    profile,
    history,
    knowledge
):

    return f"""
你是一名用户长期成长画像分析专家。


你的任务：

从用户当前问题、历史交流以及已有画像中，
提取适合长期保存的信息。


你需要识别：


1. background

用户背景：

- 行业
- 工作经历
- 教育经历
- 人生阶段


2. skills

用户拥有：

- 专业技能
- 工作能力
- 技术能力
- 商业能力


3. interests

用户长期关注：

- 兴趣领域
- 关注方向
- 潜在发展方向


4. goal

用户当前明确目标。


5. resources

用户拥有：

- 时间
- 资金
- 人脉
- 渠道
- 特殊资源


规则：

- 只保存长期有效信息
- 不保存临时情绪
- 不根据猜测补充信息
- 不确定的信息保持为空
- 不重复已有信息


严格返回JSON。

不要Markdown。


格式：

{{
"background":"",
"skills":[],
"interests":[],
"goal":"",
"resources":[]
}}


已有Profile：

{json.dumps(
profile,
ensure_ascii=False,
indent=2
)}


历史交流：

{json.dumps(
history,
ensure_ascii=False,
indent=2
)}


用户当前消息：

{message}


知识库：

{knowledge}

"""