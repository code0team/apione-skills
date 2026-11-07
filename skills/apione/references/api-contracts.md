# 接入契约与恢复

2026-11-07 静态核对，源码 SHA 同 [项目功能](project-features.md)。下面路径是接口相对路径，不含服务器地址或凭据。接入当前部署前核对其 commit 和配置。

## 身份与响应

| 平面 | 路径 | 凭据与解析 |
|---|---|---|
| 用户产品 | `/api/v1/*` | 用户登录 access token；通常 `{data, requestId}` |
| 推理网关 | `/v1/chat/completions`、`/v1/responses`、`/v1/messages`、`/v1beta/models/*` | 推理 API Key，保持原协议 JSON/SSE |
| 管理 | `/api/admin/*` | 管理员身份，不交给浏览器普通用户持有 |
| 渲染/OCR 内部任务 | `/internal/artifact-tasks/*`、`/internal/ocr-tasks/*` | 独立 Worker 凭据，不能公网开放 |

例外：连接器成功响应不包 `data`；MCP 是 JSON-RPC；204 没有响应体；文件下载按 Content-Type/Content-Disposition 读二进制。不要做所有请求统一 `response.json()` 的包装。

错误通常是 `{error:{code,message,requestId}}`，依 `code` 分流并保留请求 ID。401 共享一次 refresh；402 不反复重试扣费；409 重读资源及原操作状态；429 按 Retry-After 退避。金额 nanoUSD 用十进制整数字符串，1 USD = 1,000,000,000 nanoUSD；前端不转浮点结算。积分 micropoint 与 nanoUSD 是两种单位。


依据：[docs/api/00-conventions.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/00-conventions.md)、[docs/api/08-connectors-mcp.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/08-connectors-mcp.md)、[backend/docs/backend-feature-manual.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/backend-feature-manual.md)。

## API Key、分组和模型发现

- Key 明文仅创建/轮换时返回，支持权限 scope、模型白名单、分组、项目、有效期、启停和轮换。模型列表至少需要 `models:read`；能推理不自动等于能列模型。
- 第三方模型发现用 `/v1/models` 或 Gemini `/v1beta/models`；用户网站完整能力/价格目录用 `/api/v1/models`。前者不应被当作完整能力清单。
- Key 自己绑定档位，未知/失效档位不能静默掉到更便宜或全局线路。`keyDefaultId`/`apiDefaultId` 等由目录返回，不硬编码历史分组 ID。
- 登录会话可以按单请求带 `X-Maxx-Pricing-Group` 选择允许的分组；不带默认 Web 通道。API Key 带这个头会得到 403 `pricing_group_header_not_allowed`，不能用它覆盖 Key 档位。代码能力存在不代表产品界面已开放选项。
- 可在 Authorization Bearer、x-api-key 或 x-goog-api-key 传同一推理凭据。**同一个 Key 同时出现在多个头允许；不同 Key 并存拒绝**。旧“看到两个头就判冲突”口径已不适用。
- 默认并发文档为每用户的产品入口与 API Key 入口分别计数，同一入口增加 Key 不增加额度；实际限额看后台。这是单进程计数，不是多实例全局额度。

`/models` 按能力和可用供给呈现；WebChat 基础资格应匹配同路由、同 Provider、同上游模型的 text、streaming、usage 证据，工具/搜索另验。HTTP 200、静态模型名或纯文本成功均不能替代完整资格；人工停用不能被自动探测重新打开。


依据：[docs/api/02-models.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/02-models.md)、[docs/api/05-api-keys.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/05-api-keys.md)、[backend/internal/handler/token_auth.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/token_auth.go)、[backend/internal/handler/product_v1.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/product_v1.go)。

## 三种恢复身份各有用途

| 请求 | 首次调用/恢复身份 | 超时后怎么处理 |
|---|---|---|
| 持久 WebChat | `clientTurnId`；返回 turn 后订阅 `/api/v1/chat/turns/{id}/events` | 同一个 turn 携 Last-Event-ID 重连，不再创建新的收费 turn |
| 原生推理流 | `X-Maxx-Request-ID`，恢复保留 Key、URL、body 与事件游标 | 同 ID 恢复；`stream_outcome_unknown`/`stream_request_failed` 先核对账本与输出，再决定新调用 |
| 非流式资金 mutation、媒体任务 | 接口要求的 `Idempotency-Key` | 原 key 与原 body 重试/查询；409 不换 key 猛试 |

原生推理流携 Idempotency-Key 会被拒为 `idempotency_mode_unsupported`，不能将非流式幂等头和流恢复头混用。`X-Client-Request-ID` 是排障相关头，也不是上述幂等身份。

WebChat 显式 `Accept: application/json` 才按异步 JSON/202 接收提交结果，再订阅 SSE；否则可能直接是 SSE。`routing.status` 不带可续传 id，仅用于等待展示，不能推进游标或作为回答。只有 turn 的完成/停止/失败是终态；用户主动停止需调用 stop，关闭 SSE 不等于取消后端任务。receipt/账本决定最终费用。


依据：[docs/api/03-chat.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/03-chat.md)、[docs/api/05-api-keys.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/05-api-keys.md)。

## 图片、视频与 Artifact

- 媒体模型目录分别 `/api/v1/images/models`、`/api/v1/videos/models`；按返回 `params`/capabilities 与价格渲染控件，不按模型名称猜。
- 持久媒体创建入口 `/api/v1/images/generations/idempotency/v1`、`/api/v1/videos/generations/idempotency/v1`。两个入口都要求 **32 位小写十六进制** Idempotency-Key，不能直接用带连字符 UUID。
- 网络断开先恢复同 operation；视频创建后按 job ID 查询，轮询不能重新发创建请求。失败、结果未知与无法下载分别处理；结果归档失败不代表上游未生成或未收费。
- 文件沙箱导入走 preflight，再 import；草稿 PATCH 用 expectedVersion；render 使用稳定幂等身份。job 完成后按实际 artifactId 下载，不构造不存在的链接。
- `GET /api/v1/records` 为跨来源统一时间线，用不透明 nextCursor 原样翻页；各详情和专项列表保留各自接口与游标，不跨接口复用。


依据：[backend/internal/handler/product_images.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/product_images.go)、[backend/internal/handler/product_videos.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/product_videos.go)、[docs/api/04-generation.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/04-generation.md)、[docs/api/07-workspace-team.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/07-workspace-team.md)、[docs/api/03-chat.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/03-chat.md)。
