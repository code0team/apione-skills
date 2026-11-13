# 配置与运行必备条件

最新源码核对见 [2026-11-13 增量](project-update-2026-11-13.md)；本页保留 11-07 固定快照，新增及变化以增量中注明的证据为准。

2026-11-07 源码静态摘要；不是当前生产配置，也不是执行部署的授权。不要把源仓库中的机器专用脚本参数直接复制到别的环境。

## 启动前确认

- 源码快照的 backend/go.mod 指定 Go 1.26.0，仓库 Node 要求 ≥22.12.0，包管理器 pnpm 10.7.0；实际构建按该 commit 的声明，不用系统默认版本碰运气。
- 使用独立开发数据目录/测试数据库，不让本地进程写生产库。后端管理 UI 是构建产物的一部分，只有 Go 编译不代表所有前端文件都已发布。
- 数据库、文件存储、Worker 和上游 Provider 是不同依赖；健康检查不能替代真实请求、渲染/下载和账务验收。

## 关键配置类别

| 配置名 | 必须理解的用途 |
|---|---|
| MAXX_ADMIN_PASSWORD | 管理身份保护，部署 Secret 注入 |
| MAXX_DATA_DIR、MAXX_DSN | 文件/数据库落点，备份与恢复必须一起考虑 |
| MAXX_CORS_ALLOW_ORIGINS | 浏览器来源白名单；优先同源反代 |
| MAXX_REQUEST_IDEMPOTENCY_SECRET | 持久请求幂等编码密钥，源码要求 32 字节的十六进制表示；需安全保管，不能随意更换 |
| MAXX_OFFICE_AGENT_V1 | 办公能力，关闭不等于删除已有草稿 |
| MAXX_SMART_CONTEXT_V1 | 上下文整理；依赖辅助模型供给/价格 |
| MAXX_WORKSPACE_MEMORY_V1、MAXX_USER_MEMORY_V1 | 文件工作区与个人记忆，范围不同 |
| MAXX_WORKSPACE_SOURCE_SEARCH_RETRIEVAL_V1 | 来源检索 |
| MAXX_WORKSPACE_DOCUMENT_REDUCTION_V2 | off/shadow/allowlist/all，逐步放量；shadow 不应产生真实付费 Provider 工作 |
| MAXX_WORKSPACE_OCR_V1 | OCR 接线，需额外 OCR Worker |
| MAXX_ARTIFACT_WORKER_TOKEN、MAXX_OCR_WORKER_TOKEN | 两种 Worker 独立凭据，不能复用用户 token |
| MAXX_ARTIFACT_WORKER_CAPACITY | Worker 准入容量，需匹配运行资源与并行数 |
| MAXX_PUBLIC_BASE_URL、MAXX_CONNECTOR_FRONTEND_ORIGIN | OAuth 回调 HTTPS 基址和唯一可信前端 origin |
| MAXX_CONNECTOR_ENCRYPTION_KEY | 后端第三方凭据加密密钥，需持久保存和备份 |

只公开配置名，不记录值。Compose 的 env 文件被读取不代表所有变量进入容器，确认显式映射；排查时也不要打印完整带秘密的配置。新增配置变量需查配置注册表，不能仅在 shell 设一个未被读取的名字。


依据：[backend/go.mod](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/go.mod)、[package.json](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/package.json)、[backend/docs/configuration.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/configuration.md)、[backend/internal/requestidempotency/operation.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/requestidempotency/operation.go)、[backend/docs/backend-feature-manual.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/backend-feature-manual.md)。

## Office/OCR 的额外条件

Artifact Worker 必须有健康心跳、兼容的渲染 profile、正确 token 和容量；固定 LibreOffice/Poppler/字体清单，版本漂移不能假装可渲染。内部任务接口仅供隔离 Worker 使用。

OCR 的环境 false 不一定覆盖数据库开启值；关闭要同时核对环境和数据库开关。扫描 PDF 需兼容 OCR Worker，不应以空文本替代失败。导入预检可能明确返回 worker_unavailable、office_agent_disabled、quota_exceeded，应提示实际原因。


依据：[backend/docs/artifact-worker.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/artifact-worker.md)、[backend/docs/office-capabilities.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/office-capabilities.md)、[docs/api/07-workspace-team.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/07-workspace-team.md)。

## 发布与账务不变量

1. 合并与部署分开确认，固定完整 commit；检查运行中 `X-Maxx-Commit` 和 `/readyz`，不能只凭人类版本号。
2. 源项目已有发布脚本、部署锁、祖先关系/降级检查和回滚约束。获得本次部署授权后按目标仓库当前手册和脚本执行，不能手工复制旧二进制冒充新 commit。
3. 网站 standalone 发布需要完整静态资源；后端内存缓存的管理 UI 也可能需随进程重启生效。只传一半产物会产生旧页面或按需 chunk 白屏。
4. 模型价格、账本实际收费、Provider 成本及平台利润是不同事实。以请求冻结价格/usage/原账本关联核账，不能用当前报价覆盖历史金额。
5. 备份应包括数据库、上传/Artifact 文件、持久密钥和版本信息，验证可恢复后再承诺恢复目标。不要运行会修改现有库的演练脚本。

首次输出等待预算与整条流总超时分开；代理不缓冲 SSE。供应商满载、用户并发超限、资格缺失与上游故障分别记录，不对所有 503/422 用同一个重试策略。探测会消耗真实上游预算，批量刷新前确认预算和授权。


依据：[docs/deployment.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/deployment.md)、[AGENTS.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/AGENTS.md)、[backend/docs/backend-feature-manual.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/backend-feature-manual.md)、[docs/api/05-api-keys.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/05-api-keys.md)、[docs/api/03-chat.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/03-chat.md)。
