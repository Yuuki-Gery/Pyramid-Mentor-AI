# Pyramid Mentor AI

> 以金字塔思维为核心的 AI Mentor：不是直接给答案，而是帮助用户看清问题、结构化拆解、形成行动，并持续记录成长。

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

**English summary:** Pyramid Mentor AI is an AI mentoring system built around the Pyramid Principle. It combines SCQA problem framing, MECE/logic-tree analysis, multi-agent collaboration, RAG over a private knowledge base, user profiling, growth tracking, and pluggable LLM providers in a FastAPI + Redis + Chroma + SQLite application.

---

## 1. 项目简介

普通聊天机器人通常直接回答“你应该怎么做”。Pyramid Mentor AI 更关注三件事：

1. **先理解问题**：区分表面问题、真实目标、限制条件和缺失信息。
2. **再组织思考**：用 SCQA、MECE 和逻辑树把问题拆成可以讨论的结构。
3. **最后落到行动**：综合专家视角与用户画像，给出可执行的下一步，并留下成长记录。

项目名称中的 **Pyramid** 指的是金字塔思维体系，而不是简单的多 Agent 拼接。Multi-Agent 是承载这套方法论的工程结构：问题诊断、金字塔分析、思维教练、领域专家和最终导师各自负责不同层次的思考，再由 Final Agent 汇总成面向用户的回复。

这是一个面向学习与作品展示的项目，当前定位是**可运行的 AI 应用原型**，不是已经完成商业化打磨的生产系统。

---

## 2. 核心功能

| 功能 | 实现说明 |
| --- | --- |
| SCQA 问题分析 | `PyramidAgent` 通过结构化 Prompt 输出 Situation / Complication / Question / Answer 分析 |
| 金字塔结构化思考 | 在 SCQA 基础上生成 MECE 分解、逻辑树和结构化行动建议 |
| Multi-Agent 协作 | `ProblemAgent`、`PyramidAgent`、`TeacherAgent` 并行分析，`FinalMentorAgent` 汇总；专家 Agent 按关键词选择 |
| RAG 知识检索 | BGE 中文 embedding + Chroma 向量库；`BaseAgent.safe_retrieval()` 为分析提供知识上下文 |
| 用户成长记录 | Redis 成长记忆（里程碑、目标、决策、思维模式）+ SQLite 成长记录与报告接口 |
| 用户画像 | `ProfileAgent` 提取背景、技能、兴趣、目标和资源，`ProfileMergeAgent` 合并长期画像 |
| 专家系统 | 创业、职业、学习、商业分析、成长五个领域导师 |
| 多模型支持 | Agnes、OpenAI / OpenAI-compatible、DeepSeek；通过 `LLM_PROVIDER` 切换 |
| 用户认证 | JWT 注册、登录、当前用户信息与画像更新 |
| 额度管理 | 用户额度查询、模型分级与消耗接口（尚未接入聊天主流程） |

> 说明：核心分析能力依赖真实 LLM API。仓库不包含任何真实 API Key。

---

## 3. 技术栈

- **后端**：Python 3.11、FastAPI、Pydantic
- **LLM 编排**：LangChain、langchain-openai
- **RAG**：ChromaDB、sentence-transformers（`BAAI/bge-small-zh-v1.5`）、pypdf
- **会话与缓存**：Redis
- **数据库**：SQLAlchemy 2.x Async、SQLite（`aiosqlite`）
- **认证**：JWT（python-jose）、passlib + bcrypt
- **日志**：Loguru
- **部署**：Docker、Docker Compose
- **前端**：原生 HTML / CSS / JavaScript 单页应用（由 FastAPI 静态挂载）

> 前端不是 React / Next.js 项目，仓库中也没有 Node 构建流程。

---

## 4. 系统架构

```text
Browser (HTML / CSS / JS)
        │
        ├── GET  /frontend/            静态页面
        ├── POST /api/chat             主对话接口
        ├── GET  /health               健康检查
        └── ...                        auth / growth / quota / growth-memory
        │
        ▼
FastAPI (app.main)
        │
        ▼
MentorOrchestrator
        │
        ▼
MentorService
        ├── MemoryManager ─────────── Redis（历史 / 画像 / 成长记忆）
        ├── ProfileManager ────────── ProfileAgent → ProfileMergeAgent
        ├── 并行分析
        │     ├── ProblemAgent
        │     ├── PyramidAgent
        │     ├── TeacherAgent
        │     └── ExpertSelector → 领域专家 Agent
        └── FinalMentorAgent ──────── LLM Provider
        │
        ▼
AgentManager
        ├── LLM Factory（Agnes / OpenAI / DeepSeek）
        ├── Retriever（Chroma + BGE）
        └── Agents / Prompts
        │
        ▼
SQLite（用户、成长记录、对话表结构）
```

### 数据存储

| 存储 | 内容 |
| --- | --- |
| Redis | 会话历史 `memory:{session_id}`、会话画像 `profile:{session_id}`、成长记忆 |
| SQLite | 用户、额度、成长记录，以及已定义但尚未被聊天流程写入的 conversation/messages 表 |
| Chroma | 金字塔原理与可选 SCQA 资料的向量知识库 |

---

## 5. 一次典型请求的流程

以 `POST /api/chat` 为例：

1. `ChatRequest` 校验消息与 `session_id`；未提供时生成 UUID。
2. `MentorService` 从 Redis 读取最近对话，并保存用户消息。
3. `ProfileManager` 调用画像 Agent，增量提取并合并用户背景、技能、目标等信息。
4. 如果是短消息/问候，进入闲聊分支，由 Final Agent 生成自然回复。
5. 如果是真实问题：
   - `ProblemAgent` 做问题诊断；
   - `PyramidAgent` 做 SCQA / MECE / 逻辑树分析；
   - `TeacherAgent` 分析思考方式与盲区；
   - `ExpertSelector` 按关键词选择领域专家并生成专业分析。
6. 各 Agent 结果与画像、历史一起交给 `FinalMentorAgent`，生成最终导师回复。
7. 回复写入 Redis 会话历史，并返回 `session_id`、`mentor_response`、`is_casual`。

> Agent 调用设置了超时与降级处理；单个分析 Agent 失败不会让整个请求直接崩溃。

---

## 6. 项目截图

> 截图待补充。建议在 `docs/screenshots/` 放置真实运行截图，不要使用伪造的产品界面。

预留位置：

- `docs/screenshots/chat.png` — 主对话页
- `docs/screenshots/pyramid.png` — 金字塔分析页
- `docs/screenshots/growth.png` — 成长追踪页

---

## 7. 环境要求

- Python **3.11**（与 Dockerfile 一致）
- Docker **24+** 与 Docker Compose v2（推荐启动方式）
- Redis 7（Docker Compose 已包含）
- ChromaDB（Docker Compose 已包含）
- 至少一个真实 LLM API Key（Agnes / OpenAI-compatible / DeepSeek）
- 首次运行 embedding 模型时需要访问 Hugging Face（或提前配置本地模型缓存）

---

## 8. 环境配置

```bash
cp backend/.env.example backend/.env
```

然后编辑 `backend/.env`。最小配置示例：

```dotenv
ENVIRONMENT=development
LLM_PROVIDER=agnes
AGNES_API_KEY=your_api_key_here
AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
DEFAULT_MODEL=agnes-2.0-flash

REDIS_HOST=redis
CHROMA_HOST=chromadb

JWT_SECRET_KEY=
CORS_ALLOW_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

### 关键配置说明

| 配置 | 说明 |
| --- | --- |
| `LLM_PROVIDER` | `agnes` / `openai` / `deepseek` |
| `DEFAULT_MODEL` | 必须与所选供应商支持的模型名一致 |
| `AGNES_API_KEY` / `OPENAI_API_KEY` / `DEEPSEEK_API_KEY` | 按供应商填写对应 Key，不要提交到 Git |
| `REDIS_HOST` / `CHROMA_HOST` | Docker Compose 内使用服务名；本机直连使用 `127.0.0.1` |
| `JWT_SECRET_KEY` | 生产环境必填，至少 32 个随机字符；开发环境留空会使用明确标记的本地占位密钥 |
| `CORS_ALLOW_ORIGINS` | 逗号分隔的明确来源；由于启用了 credentials，禁止使用 `*` |
| `ENABLE_DEBUG_ENDPOINTS` | 本地调试/知识灌库接口开关；生产环境强制关闭 |

生成 JWT 密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 9. 启动方式

### 方式一：Docker Compose（推荐）

```bash
docker compose up -d --build
```

Dockerfile 会先安装 CPU 版 PyTorch，避免把数 GB 的 CUDA 依赖带进镜像；本项目实际验证的镜像约 2.7 GB。

检查服务：

```bash
docker compose ps
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/llm-health
```

访问：

- 前端：<http://127.0.0.1:8000/frontend/>
- Swagger：<http://127.0.0.1:8000/docs>
- 根路径：<http://127.0.0.1:8000/>
- Chroma 宿主机端口：`127.0.0.1:8001`
- Redis 宿主机端口：`127.0.0.1:6379`

首次启动后，将内置金字塔知识灌入 Chroma：

```bash
curl -X POST http://127.0.0.1:8000/knowledge-load-pyramid
```

如果本地拥有可合法使用的 `docs/scqa.pdf`，可执行：

```bash
curl -X POST http://127.0.0.1:8000/knowledge-load-all
```

停止服务：

```bash
docker compose down
```

如需同时清除 Redis / Chroma 数据卷，请确认后再执行 `docker compose down -v`。

### 方式二：本机运行

先启动 Redis 与 Chroma，并确保 `backend/.env` 中：

```dotenv
REDIS_HOST=127.0.0.1
CHROMA_HOST=127.0.0.1
```

然后：

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 10. 测试方式

测试不依赖真实 LLM、Redis 或 Chroma，外部能力均使用 Mock/隔离。

```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

当前共 30 项测试，覆盖：

- `BaseAgent.clean_json()`：普通 JSON、Markdown 包裹、前后多余文本、非法 JSON、空输入；
- Retriever：正常结果、空结果、缺失 metadata、Chroma 异常、空 query；
- Chat API：正常请求、必填校验、session_id 生成、异常降级；
- 配置：环境变量读取、生产环境 JWT 强制校验、CORS 解析与通配符拒绝；
- 认证：bcrypt 哈希/校验、JWT 编解码；
- 专家 Agent：确认使用 `chat()` 接口并注入画像；
- Final Prompt：确认多 Agent 分析结果确实进入最终回复上下文。

---

## 11. 项目目录结构

```text
Pyramid-Mentor-AI/
├── backend/
│   ├── app/
│   │   ├── api/               # health、chat、auth、growth、quota 等路由
│   │   ├── agents/            # 核心 Agent、专家 Agent、选择器、编排器
│   │   ├── core/              # Settings、统一日志
│   │   ├── database/          # 异步 SQLAlchemy 引擎与建表
│   │   ├── llm/               # Agnes / OpenAI / DeepSeek 客户端与工厂
│   │   ├── memory/            # Redis 会话、画像、成长记忆
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── prompts/           # 独立 Prompt 模板
│   │   ├── rag/               # Chroma、embedding、加载、切分、检索
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── services/          # 认证、成长、额度、画像、导师主流程
│   │   └── main.py            # FastAPI 入口、CORS、路由注册
│   ├── tests/                 # pytest 自动化测试
│   ├── .env.example           # 环境变量模板（无真实凭证）
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── docs/
│   ├── ARCHITECTURE.md        # 更详细的架构说明
│   ├── KNOWLEDGE_BASE.md      # 知识库与语料说明
│   ├── screenshots/           # 真实截图占位
│   └── scqa.pdf               # 本地文件，默认被 .gitignore 排除
├── frontend/
│   └── index.html             # 原生单页前端
├── docker-compose.yml
└── README.md
```

---

## 12. 当前限制

这些是当前版本真实存在的边界，不应在展示时省略：

1. **前端未接入 JWT**：聊天与成长记忆页面使用匿名 session；注册/登录 API 已实现，但前端尚未调用。
2. **画像以 session 为键**：`profile:{session_id}` 不是账号级长期画像；清除浏览器会话后会重新开始。
3. **成长记忆使用匿名 ID**：`/api/growth-memory/*` 当前固定使用 `anonymous_dev_user`，不适合直接作为多用户生产服务。
4. **额度尚未在聊天中强制扣减**：额度 API 已实现，但 `/api/chat` 未调用 `quota_service.consume_quota()`。
5. **聊天历史只在 Redis**：`conversations` / `messages` ORM 表结构存在，但主聊天流程尚未写入 SQL。
6. **知识库需要手动灌入**：没有自动索引任务；首次使用需调用开发接口。
7. **SCQA PDF 不随仓库分发**：因其元数据含本机路径、公开分发授权未确认，默认只保留本地文件；RAG 加载能力仍在。
8. **专家选择基于关键词**：不是语义路由，复杂问题可能匹配不到专家。
9. **前端金字塔面板数据有限**：`/api/chat` 目前只返回最终文本等基础字段，没有返回完整结构化分析对象。
10. **没有真实 LLM 的自动化测试**：测试只验证本地逻辑和 Mock 路径；真实模型效果需要提供 API Key 后人工验证。
11. **仓库尚未声明开源许可证**：如需允许他人复用代码，请在发布前补充合适的 LICENSE。

---

## 13. 后续规划

- 将 JWT 用户身份接入聊天、画像和成长记忆，替换匿名 session。
- 在聊天主流程中执行额度校验与扣减。
- 把会话与消息持久化到 SQL，并提供历史会话接口。
- 将 SCQA/MECE/逻辑树输出为前端可直接渲染的结构化 JSON。
- 增加流式输出、请求限流和更细粒度的可观测性。
- 为真实 LLM 增加端到端评估集与回归测试。
- 增加知识库版本管理、增量索引与引用来源展示。

以上为规划，不代表当前已经实现。

---

## 14. 安全说明

- `.env`、数据库文件、日志和本地缓存均在 `.gitignore` 中排除。
- Docker 构建使用 `.dockerignore`，不会把 `.env`、SQLite 或测试缓存打进镜像。
- 生产环境缺少有效 `JWT_SECRET_KEY` 时应用会拒绝启动。
- CORS 不使用 `*` + credentials 的危险组合，来源必须显式配置。
- 调试/测试接口在 `ENVIRONMENT=production` 时强制关闭。
- 仓库中没有任何真实 API Key；如你在别处暴露过 Key，请立即撤销并重新生成。

---

## 15. 文档

- [架构说明](docs/ARCHITECTURE.md)
- [知识库说明](docs/KNOWLEDGE_BASE.md)
- [安全说明](SECURITY.md)
- [截图占位说明](docs/screenshots/README.md)

---

如果这个项目对你有帮助，欢迎通过 Issue 讨论金字塔思维、Agent 协作和 RAG 工程实践。
