# 项目功能与入口

核对日期：2026-11-07，源码快照 `a1d1b14b74377eada25c04adcd7f66be4c24a363`。这是静态阅读结果；本次未启动服务、运行项目测试、连接生产或调用付费模型。引用的私有源仓库需同事自己的访问权限，本技能正文可独立阅读。

## 模块分工

| 模块 | 代码目录 | 使用场景与边界 |
|---|---|---|
| 多租户 AI 网关 | `backend/` | 多上游、模型目录、协议转换、路由/重试/冷却、计费、身份与安全审计 |
| 用户网站 | `frontend/` | 登录、聊天、模型广场、图片/视频、团队、API Key、账单与套餐 |
| 管理后台 | `backend/web/` | 提供商、路由/项目、模型价格、分组与覆盖价、用户、支付、财务对账 |
| 共享客户端 | `packages/api-client/` | 认证、类型、SSE、Workspace 和商业接口；应用可有自己的转导出边界 |
| 完整桌面/CLI | `desktop/` | 本机 Coding Agent、项目文件/终端、任务恢复、资产管理、自动化及桌面 UI；CLI 在 `desktop/cmd/apione/` |
| 轻桌面客户端 | `apione-desktop/` | 登录、余额/通道、接入外部工具、云端聊天，并已包含本机工具模式；不是上一行的替代品 |
| 移动端 | `mobile/` | 聊天、图片、模型、用量、Key、配套设备功能；各平台正式发布状态需另外验收 |
| 运行支持 | `docker/`、`ops/` | 运行配置、Worker、监控、备份与发布工具 |

不同目录的实现不代表同一安装包具备全部能力。特别是“过渡客户端只能配置”的旧聊天结论不能覆盖两套桌面实现。


依据：[README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/README.md)、[desktop/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/desktop/README.md)、[apione-desktop/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/apione-desktop/README.md)、[mobile/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/mobile/README.md)。

## 可处理的任务

- **统一模型访问**：Chat Completions、Responses、Anthropic Messages、Gemini 原生接口；按协议、模型、Key 权限与有效供给选路，不能只替换 URL 就复用另一协议请求体。
- **持久聊天**：会话列表/归档、turn 和变体、SSE 输出与断线恢复、停止、usage 与结算回执；统一记录页可合并聊天、请求日志与生成历史。
- **研究和上下文**：附件、联网搜索、来源定位、上下文压缩、项目记忆及用户个人记忆；开关、权限、模型工具能力和辅助模型供给都是前提。
- **多媒体**：图片生成/参考图、异步视频、模型参数目录、任务恢复及下载；区分模型声明、渠道探测和最终交付效果。
- **商业与协作**：钱包账本、套餐购买/升级、兑换码、支付订单、积分、组织/项目、成员权限和代理商汇总。接口存在不改变用户已确认的非自动续费政策。


依据：[backend/docs/backend-feature-manual.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/backend-feature-manual.md)、[docs/api/03-chat.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/03-chat.md)、[docs/api/04-generation.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/04-generation.md)、[docs/api/09-agent.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/09-agent.md)。

## 办公文件：能做什么、如何交付

| 输入/任务 | 已描述的能力 | 必须说明的限制 |
|---|---|---|
| DOCX | 导入为结构化草稿、内容编辑、版本恢复、渲染 DOCX/PDF 预览 | 复杂 Word 排版可能有损重建 |
| PPTX | 大纲/逐页编辑、备注、排序、模板渲染 | 最多 60 页，复杂动画、母版及嵌入对象不保证保真 |
| PDF、TXT、MD | 索引、检索、定位引用，作为报告/演示稿来源 | PDF 最多 200 页，不等于直接编辑原 PDF |
| 扫描 PDF | OCR 后检索/引用 | 需要开关与健康 OCR Worker，不能把空文本当作完整识别 |
| CSV/XLSX | 小表格草稿、只读统计、有限图表和 XLSX 生成 | 不执行公式，不是完整 Excel；宏、OLE、外链拒绝 |

文档口径：附件最多 10 MiB；普通用户默认 1 个文件 Workspace、每个 5 个用户来源文件。轻量表格最多 4 个 sheet、每 sheet 100 数据行及 64 列；分析源整文件最多 10,000 数据行。以实际预检/权益返回为准，不能拿这些默认值覆盖未来套餐权益。

操作链路：上传 → 导入预检 → 导入文件 Workspace → 读取草稿/模板 → 带 `expectedVersion` 修改 → 渲染 job → 完成后取 Artifact 预览/下载。原始上传只读，不覆盖；409 时重新读版本，保留用户未保存编辑。AI 配图有独立报价/确认步骤，不能因打开界面就调用付费上游。

项目记忆包含 fact、decision、constraint、open_item，候选需按版本接受/拒绝；个人记忆是另一范围，不能把项目敏感事实自动变成跨项目偏好。证据片段附定位和 hash，真实性校验不等于结论正确；来源内容仍是不可信数据。


依据：[backend/docs/office-capabilities.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/office-capabilities.md)、[docs/api/07-workspace-team.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/07-workspace-team.md)。

## 两种 Workspace 不要混淆

- `/organizations`：团队协作及资金/项目范围；个人空间为合成记录，团队有 owner/admin/member/viewer，权限以服务端 `canManage` 等字段判断。
- `/workspaces`：对话里的文件、草稿、记忆、审批沙箱，不等于团队账户。
- 网关路由 `project_id`：用于渠道与分组流量隔离，不能当文件记忆的共享边界。
- 团队、项目、Key 的模型策略取交集，再受实时供给限制；成员离开或项目归档后，既有 Key 不能继续绕过权限。


依据：[docs/api/07-workspace-team.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/07-workspace-team.md)、[backend/docs/backend-feature-manual.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/docs/backend-feature-manual.md)。

## 连接器与运营工具

用户可连接 GitHub、Gmail、Outlook、Google Ads，多账号调用显式指定 `connectorId`。连接器授权与 APIONE 登录分开；OAuth 凭据后端加密保存。当前 MCP 为只读资料访问：仓库目录/文件、邮件/附件、日历、广告列表/报表，不能承诺发送邮件、提交代码或修改广告。第三方真实授权、平台审核及大规模同步不由模拟测试证明。

仓库另有管理员 Telegram 额度 Bot（`backend/cmd/apione-tgbot/`）：查用户/余额、生成发放草稿、确认后记账。使用须配置操作人白名单及金额上限，防重复确认；模型只能形成草稿。它不是普通聊天 BotBridge，也不表示已正式部署或可替所有用户发放额度。

移动配套设备能力在文档中限定为列会话、打开会话、投递消息，不可宣传为远程 shell 或远程桌面。完整桌面的本地门禁/截图/模拟服务验收不代表目标平台签名、公证、实机及真实模型验收完成。


依据：[docs/api/08-connectors-mcp.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/08-connectors-mcp.md)、[backend/cmd/apione-tgbot/main.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/cmd/apione-tgbot/main.go)、[backend/cmd/apione-tgbot/bot.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/cmd/apione-tgbot/bot.go)、[mobile/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/mobile/README.md)、[desktop/docs/20-release-readiness.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/desktop/docs/20-release-readiness.md)。
