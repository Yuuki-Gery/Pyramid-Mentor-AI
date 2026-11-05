# 知识库说明

## 1. 组成

RAG 链路由以下模块组成：

| 文件 | 作用 |
| --- | --- |
| `app/rag/loader.py` | 加载 PDF / TXT 并附加 `source`、`category`、`chapter` 元数据 |
| `app/rag/splitter.py` | `RecursiveCharacterTextSplitter`，chunk 500 / overlap 50 |
| `app/rag/embedding.py` | 懒加载 `BAAI/bge-small-zh-v1.5` |
| `app/rag/knowledge.py` | 生成向量并写入 Chroma，使用内容哈希 ID + `upsert` |
| `app/rag/chroma_client.py` | Chroma HTTP 客户端，延迟连接 |
| `app/rag/retriever.py` | 查询 Chroma，返回 `content` + `metadata` |

内置语料：`backend/app/rag/knowledge_data/pyramid_principle.txt`。

## 2. 初始化

开发环境启动后调用：

```bash
curl -X POST http://127.0.0.1:8000/knowledge-load-pyramid
```

如果本地有 `docs/scqa.pdf`：

```bash
curl -X POST http://127.0.0.1:8000/knowledge-load-all
```

接口只在 `ENABLE_DEBUG_ENDPOINTS=true` 且非生产环境注册。生产部署时，应先在开发环境完成灌库，再让生产实例连接同一 Chroma 数据卷。

## 3. 关于 SCQA PDF

仓库**默认不分发** `docs/scqa.pdf`：

- PDF 元数据包含生成机器的本地路径；
- 无法确认该文件的公开分发授权；
- 文件内容属于第三方方法论资料时，需要使用者自行确认版权。

本地文件被 `.gitignore` 排除，不会被提交，但保留在开发目录中。知识库加载代码没有删除：只要你在本地放入一份**有权使用**的 `docs/scqa.pdf`，`/knowledge-load` 仍然可用。

## 4. 添加自己的语料

1. 将 TXT 或 PDF 放入你有权使用的目录。
2. 在 `backend/app/api/knowledge_test.py` 中调整路径，或新增一个开发用加载函数。
3. 调用 `document_loader.load_text()` / `load_pdf()`，再交给 `text_splitter.split()` 和 `knowledge_base.add_documents()`。
4. 建议在 metadata 中写清 `source`、`category`、`chapter`，便于后续展示引用来源。

请勿上传未经授权的教材、付费课程、内部文档或包含个人信息的资料。

## 5. 常见问题

**首次调用检索很慢？**

embedding 模型在第一次检索时才会下载和加载，属于预期行为。可提前预热，或在镜像中预置 Hugging Face 缓存。

**知识库接口返回 503？**

先检查 `http://127.0.0.1:8000/rag-health` 和 Chroma 日志。Chroma 不可用时检索会失败，但主聊天链路会通过 `safe_retrieval()` 降级为空知识。

**重复灌库会报 ID 冲突吗？**

不会。当前实现使用文本 + source 的 SHA-256 作为确定性 ID，并通过 `upsert` 写入。
