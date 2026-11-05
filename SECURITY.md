# Security Policy

## 凭证

- 不要提交 `backend/.env`、API Key、JWT 密钥、数据库或日志。
- 如果怀疑密钥泄露，请立即在供应商控制台撤销并重新生成；仅从 Git 工作区删除文件并不能清除历史提交中的密钥。
- 生产环境必须设置至少 32 个随机字符的 `JWT_SECRET_KEY`，应用会在缺失或使用开发占位值时拒绝启动。

## 部署基线

- CORS 仅配置明确的前端来源，禁止 `*` + credentials。
- 生产环境自动关闭 `/llm-test`、`/agent-test`、`/rag-test`、`/knowledge-load*` 和 `/api/expert/*` 调试接口。
- Redis 与 Chroma 的宿主机端口默认只绑定 `127.0.0.1`。
- `.dockerignore` 阻止 `.env`、SQLite、日志和测试缓存进入镜像。

## 当前已知边界

聊天接口目前没有接入 JWT 和请求限流；成长记忆使用匿名 ID。这些是项目限制，不应将当前版本直接作为多用户生产服务暴露到公网。

## 报告问题

如果你发现安全问题，请通过仓库 Issue 私下联系维护者，不要公开贴出可利用细节或真实凭证。
