# 架构说明

## 1. 设计目标

Pyramid Mentor AI 的核心不是“让多个 Agent 依次说话”，而是把金字塔思维的几个步骤拆成可独立失败、可替换的分析单元：

```text
理解问题 → 结构化拆解 → 检查思考方式 → 引入领域视角 → 汇总成导师回复
```

Agent 之间不直接调用，统一由 `AgentManager` 管理、由 `MentorService` 编排。这样可以单独替换模型、Prompt、检索器或某个专家，而不影响 API 层。

## 2. 分层

| 层 | 主要模块 | 职责 |
| --- | --- | --- |
| 接入层 | `app/api/*` | HTTP 路由、请求校验、鉴权、错误转换 |
| 编排层 | `MentorOrchestrator`、`MentorService` | 闲聊/深度模式判定、并行 Agent、超时与降级 |
| Agent 层 | `app/agents/*` | 问题诊断、金字塔分析、教学反馈、画像、领域专家 |
| 能力层 | `app/llm/*`、`app/rag/*`、`app/memory/*` | 模型调用、向量检索、Redis 持久化 |
| 基础层 | `app/core/*`、`app/database/*`、`app/models/*` | 配置、日志、SQLAlchemy、ORM |

前端是原生单页 `frontend/index.html`，由 FastAPI 在 `/frontend` 静态挂载；它只消费后端接口，不参与构建后端。

## 3. 对话主链路

```text
POST /api/chat
  └─ ChatRequest 校验
      └─ MentorOrchestrator.run(message, session_id)
          └─ MentorService.process()
              ├─ MemoryManager.get_history()          Redis
              ├─ MemoryManager.save_message(user)
              ├─ ProfileManager.update_profile()
              │   ├─ ProfileAgent.run()
              │   └─ ProfileMergeAgent.run()
              ├─ _is_casual() ?
              │   ├─ 是 → FinalMentorAgent（闲聊 Prompt）
              │   └─ 否 → asyncio.gather:
              │            ProblemAgent
              │            PyramidAgent
              │            TeacherAgent
              │            ExpertSelector.run_expert()
              ├─ FinalMentorAgent（综合各分析结果）
              └─ MemoryManager.save_message(assistant)
```

### 超时与降级

- 单 Agent：`MentorService.safe_run()` 20 秒超时，失败返回 `None`。
- 并行分析：整体 40 秒超时；失败时 Final Agent 仍可基于画像和历史生成回复。
- 主流程：60 秒超时，返回用户可读的降级文案。
- 闲聊：10 秒超时，失败使用本地兜底文案。
- Redis 读写失败：`MemoryManager` 记日志并返回空历史/跳过写入，不阻断主流程。

## 4. Agent 职责

| Agent | 职责 | 主要输出 |
| --- | --- | --- |
| `ProblemAgent` | 区分表面问题与真实问题 | 问题定义、目标、约束、缺失信息 |
| `PyramidAgent` | SCQA、MECE、逻辑树、行动路径 | 结构化分析文本 |
| `TeacherAgent` | 检查用户思考方式 | 逻辑问题、盲区、引导问题 |
| `FinalMentorAgent` | 综合分析与用户画像 | 面向用户的导师回复 |
| `ProfileAgent` | 提取长期有效信息 | background / skills / interests / goal / resources |
| `ProfileMergeAgent` | 合并旧画像与新画像 | 稳定长期画像 |
| `ExpertAgent` 子类 | 领域专业分析 | 创业、职业、学习、商业、成长建议 |

`ExpertSelector` 以关键词命中比例打分，最高分低于 0.3 时使用 general 分支。

## 5. 数据流

### Redis

- `memory:{session_id}`：最近对话，TTL 24 小时。
- `profile:{session_id}`：会话级画像，TTL 30 天。
- `growth:{user_id}:*`：里程碑、目标、决策、思维模式与汇总。

### SQLite

- `users`：账号、密码哈希、画像字段、额度、模型等级。
- `growth_records`：成长记录。
- `conversations` / `messages`：已定义 ORM 结构，聊天主流程目前尚未写入。

数据库表在 FastAPI lifespan 启动阶段通过 `Base.metadata.create_all` 创建。

### Chroma

- Collection：`pyramid_knowledge`
- Embedding：`BAAI/bge-small-zh-v1.5`
- 写入：`KnowledgeBase.add_documents()`，以内容哈希生成确定性 ID 并 `upsert`，重复灌库不会产生重复 ID。
- 查询：`KnowledgeRetriever.search()` 返回 `[{"content": str, "metadata": dict}]`。

## 6. 模型接入

`app/llm/manager.py` 根据 `LLM_PROVIDER` 返回：

- `AgnesClient`
- `OpenAIClient`
- `DeepSeekClient`

三个客户端都实现 `BaseLLM.chat()`。客户端在第一次调用时才创建 LangChain `ChatOpenAI` 实例，因此没有 API Key 时 Web 服务仍可启动，`/llm-health` 会报告 `not_configured`，聊天接口会走降级路径。

## 7. 安全边界

- JWT 密钥：开发环境有明确标记的占位值；生产环境缺失、过短或使用占位值时启动失败。
- CORS：只接受显式来源列表；由于启用了 credentials，拒绝 `*`。
- 调试接口：`ENABLE_DEBUG_ENDPOINTS` 控制，且生产环境强制关闭。
- 日志：不打印 API Key、密码或完整请求内容；API 层返回内部异常的通用文案。
- 容器：Redis / Chroma 仅绑定宿主机 `127.0.0.1`，`.dockerignore` 阻止凭证进入镜像。

## 8. 当前架构限制

详见根 README 的“当前限制”。最需要优先处理的是：聊天接口仍是匿名的、额度未在主链路扣减、画像以 session 而不是账号为键、结构化分析结果尚未返回给前端渲染。
