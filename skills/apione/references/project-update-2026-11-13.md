# 项目增量：2026-11-13

固定来源：AIGatewaySystem `main`，commit `4ba12289142f12c78eaf4c6fbcbd2481436e3878`；对比上一源码快照 `a1d1b14b74377eada25c04adcd7f66be4c24a363`。本次仅静态核对 diff、文档和实现，不运行产品测试、迁移、付费请求或部署。下文引用原项目的本地验收报告时，只转述其限定条件，不冒充本次实测或生产证明。

目录：推广归因 → 路由/缓存 → 内容提取 → 媒体/价格 → 登录/团队 → 套餐 → 客户端分发 → 发布要求。

## 推广来源与运营统计

管理端已有“推广来源”页面及链接生成、用户来源卡片；会员端有本人分享统计接线。

- UTM/source 是渠道或活动标记；`ref` 只承载有效会员邀请码，两者可以共存，不能拿渠道名充当邀请码。推广归因本身不新设邀请返利政策。
- 首次来源按可观测证据固定；注册前最后一次有效非直接触达另外记录，后续登录不能补造最初来源。
- UV 是可观测浏览器去重数，不是自然人数；跨设备、隐私限制、清缓存和多标签竞争会影响计数，不能用 IP/指纹强行推算唯一用户。
- 管理漏斗按 UTC 半开区间内首次访问者分组，观察其随后 30 天注册、首次成功使用和首次已确认付款；未满窗口显示观察未完成。查询区间最多 90 天，分母缺失时不显示假转化率。
- 会员页近 90 天访问浏览器数与正式邀请关系累计账号数不是同一批次；不能相除得“新增获客转化率”。充值/订阅确认毛额也不是扣除退款拒付后的净收入。
- `MAXX_ACQUISITION_ENABLED=false` 关闭新匿名采集与注册归因，不应阻断登录/支付/推理；已有统计不自动删。匿名事件及无活动访客的保留期为 90 天，不能回填已清理的历史访问。
- 只采必要来源字段，不保存完整查询 URL，不在参数里放身份、令牌或付款信息；表不可用时可显示未知来源，不能因此断言注册失败。


依据：[docs/acquisition.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/acquisition.md)、[backend/internal/handler/product_acquisition.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_acquisition.go)、[backend/internal/handler/admin_acquisition.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/admin_acquisition.go)、[backend/web/src/pages/users/user-acquisition-card.tsx](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/web/src/pages/users/user-acquisition-card.tsx)。

## 自动路由、会话亲和和缓存观察

`health_priority` 已有自适应分配：同一 provider 的多条路由只占一份新会话份额，结合新鲜健康、首字 P95 和有界缓存收益。未知不是失败；配置顺序、手动权重与自动模式不能混作同一算法。

| 策略 | 新会话选择语义 |
|---|---|
| health_priority | 合格 provider 内稳定加权，健康/速度/缓存证据影响偏好 |
| priority | Position 和原健康等级重排，不靠缓存收益改变顺序 |
| weighted_random | 按路由权重，缓存收益只做有界概率调整 |
| sticky_priority | Position 与自身软绑定 |
| custom_weight | 管理员 provider 手动权重，零权重排除，健康/缓存不改手动概率 |

未保存全局/项目策略时，内置自动默认开启 conversation 亲和、1800 秒 TTL；已有保存策略不被更新覆盖。绑定要有稳定 token/session，按租户、项目、协议客户端、模型及配置代次隔离，成功后续期。升级粘性命名空间可能短时影响缓存；不要为此清空 Redis、恢复软删除路由或放宽分组隔离。

有限恢复不等于无费用重试：普通文本结果不明时只有在适配器执行事实、输出状态及预算允许下有限恢复；已输出、取消、工具副作用等情况不透明重放。图像/视频不自动继承文本兜底，不能仅凭 429/5xx 判定上游未执行，也不承诺跨请求 exactly-once。

管理端新增 `/api/admin/requests/routing-observability`：默认 24 小时、最长 7 天，按当前租户和项目/provider/精确模型筛选；有样本上限、截断和未知标记，不是资金审计账本。可信完整 usage 才能计算 token 加权缓存率，缺失不显示 0%。轨迹的非最终尝试目录价估算不是额外用户扣款、Provider 成本或节省金额。

**模型广场字段单位不同**：`trafficCacheHitRate` 是 24h 会员流量，范围 0–100，优先展示；`cacheHitRate` 是探测的 0–1 比例，无流量时才作探测兜底并标明来源。两者均缺失时为未知，不能重复 ×100 或把探测说成客户实用命中。


依据：[backend/docs/adaptive-routing.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/docs/adaptive-routing.md)、[backend/docs/routing-observability.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/docs/routing-observability.md)、[backend/internal/router/router.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/router/router.go)、[backend/internal/handler/admin_routing_observability.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/admin_routing_observability.go)、[backend/internal/handler/product_square.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_square.go)、[docs/api/02-models.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/api/02-models.md)。

## 内容拆解与提取：仍有明确未完成项

已有 `/api/v1/chat/content-sources` 准备/读取私有来源，资料交给用户所选模型及现有 plan→turn→SSE 链路。来源准备本身不调用模型；不能偷偷固定第二个“分析模型”。粘贴文本必须标为用户提供，不能算平台自动提取成功。刷新追问需恢复同 owner/会话来源，切账号/新会话不能带上旧素材。

较早基础版报告证明了模拟模型环境的来源、引用、收费接线及跨账号拒绝，未证明真实模型分析质量。更新后的内容提取设计仍明确：三平台稳定读取、图片 OCR/视觉、视频受控解码到转写接线、会员异步入口以及真实多模型六项效果尚未完成；社交首页入口沿主线隐藏，实际线上是否隐藏需另验。用户看到真实效果并明确批准之前，不据源码 reader 存在就恢复入口或对外承诺。

可选 AIDATA 仅补小红书/公众号正文读取，默认关闭：`MAXX_CONTENT_SOURCE_AIDATA_ENABLED` 与对应服务端 API key 分开配置，只填 key 不会开启；cache_mode=auto 也可能产生供应商费用。规范作品身份与短链处理有边界，公开读取失败不意味着可无条件付费重试。

抖音 reader/下载器存在不等于字幕、音轨、画面已理解。本地转写 CLI 是操作员工具，输入要求 16 kHz 单声道 PCM16 WAV，工具/模型需事先提供并验证；不是会员直接上传任意远程视频就转写的接口。音频结果标注 audio_only/unverified_asr，不将描述文字或标题当视频口播。


依据：[docs/design/content-extraction-engine.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/design/content-extraction-engine.md)、[docs/reports/2026-11-08-content-remix.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/reports/2026-11-08-content-remix.md)、[backend/internal/handler/product_content_sources.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_content_sources.go)、[backend/internal/service/content_source.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/service/content_source.go)、[backend/internal/config/vars_content_sources.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/config/vars_content_sources.go)。

## 媒体兼容、文件生命周期和报价

- 已有 `/api/v1/media/preparations` 私有准备任务及原文件/兼容 MP4 读取，服务不可用返回 media_preparation_unavailable。依赖转换工具及存储接线，上传成功不代表已可播放、已作为生成参考或处理完成。
- Apple 媒体上传、MOV/HEVC 兼容、参考素材过期恢复及身份切换有前后端代码/测试。原项目有本地 Web/macOS 及模拟环境报告，本次不将其升级成生产或跨平台通用保证。
- 请求结束、关闭页面、附件 TTL、来源索引和上游请求审计副本是不同生命周期；不能承诺删除一个附件会清除全系统所有副本。

图片 `startingPrice.basis` 的 UI 口径：

| basis | 字段 | 界面显示 |
|---|---|---|
| image | perImageNanoUsd | 按张价格 |
| request | perRequestNanoUsd | 按次价格 |
| image_tokens | imageOutputPriceMicro | “按量计费”，解释实际按出图用量结算，不换算为固定每张价 |

`imageOutputPriceMicro` 是 microUSD/百万 token，不能直接当 nanoUSD/张。缺报价时显示暂无报价，不显示假 $0；价格面板与实际账本仍分别核对。


依据：[backend/internal/handler/product_media_preparation.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_media_preparation.go)、[backend/internal/service/media_preparation.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/service/media_preparation.go)、[backend/internal/core/media_preparation.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/core/media_preparation.go)、[frontend/src/lib/apple-media-upload.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/frontend/src/lib/apple-media-upload.ts)、[frontend/src/lib/generation-reference-recovery.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/frontend/src/lib/generation-reference-recovery.ts)、[docs/api/04-generation.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/api/04-generation.md)、[docs/reports/2026-11-08-full-e2e-completion.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/reports/2026-11-08-full-e2e-completion.md)。

## 登录、团队与用户可见状态

- Google One Tap 已有 AuthGate 统一提示和 `/api/v1/auth/google/one-tap`。需要 registration-policy 下发 Client ID；未配置、强制邀请码、用户本标签页已关闭或 Google 不展示时，不弹框是可能的正常状态。原跳转登录按钮仍保留。
- 浏览器只提交 credential，身份验证由后端校验签名、受众和已验证邮箱；不能从前端解码内容直接建立登录态。登录/退出、刷新与并发请求需核对身份 epoch，避免旧账号响应回填新账号历史。
- 团队加入链接已有预览与接受路由；预览不等于加入，接受必须登录并由服务端校验链接/角色。团队余额、个人余额与项目权限保持原有隔离。
- 用户支持入口提供群组/支持素材读取，不等于开放任意联系消息发送；不要把产品内支持 API 误认为当前 AI 可自行联系同事或客户。


依据：[docs/google-one-tap.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/google-one-tap.md)、[backend/internal/handler/product_google_oauth.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_google_oauth.go)、[frontend/src/components/app/AuthGate.tsx](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/frontend/src/components/app/AuthGate.tsx)、[frontend/src/lib/maxx-auth.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/frontend/src/lib/maxx-auth.ts)、[backend/internal/handler/product_organization_join_links.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_organization_join_links.go)、[backend/internal/handler/product_support.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/handler/product_support.go)。

## 套餐升级的实现变化

业务套餐价格/28 天政策不由源码自动改写。后端升级现在使用与实际扣减一致的 cycle_key 周期解析，避免重叠旧周期导致报价/升级 409；排查时比较当前版本、实际计费周期及 upgrade grant，不能直接删旧周期或手调额度。

已有在线升级支付界面逻辑复用“充值入钱包→再执行钱包升级”，不是一笔新的直接套餐扣款用途。可能看到充值和升级两条账单；最低充值约束可能让支付金额高于差价，多余金额留在钱包，需说明差价、支付额与留存额，不能说多余全是升级费。完成升级按支付单 ID 生成稳定幂等键；前端展示/支付四舍五入不能替代服务端真实报价。

此前记录的后端 ppm 与前端 BigInt 比例精度差异仍可见，积分 domain/eligibility 的关键文件本次与上版没有变化；不能因更新项目就关闭这些待验收项。源码的通用续订/自动续费函数也不能取代一次性购买政策。


依据：[backend/internal/repository/sqlite/subscription_upgrade.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/repository/sqlite/subscription_upgrade.go)、[backend/internal/domain/subscription_upgrade.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/domain/subscription_upgrade.go)、[frontend/src/lib/upgrade-payment.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/frontend/src/lib/upgrade-payment.ts)、[backend/internal/domain/points.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/domain/points.go)、[backend/internal/repository/sqlite/points_settlement.go](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/backend/internal/repository/sqlite/points_settlement.go)。

## 桌面 UX、CLI 和更新分发

完整桌面有按会话保留未发送草稿及草稿提示点。npm CLI 包装器、下载校验、manifest 验签和平台产物选择已有文件；签名校验失败不能当“已是最新版”。

发行文档记录过签名清单/CLI 产物连通验证，但同一文档仍明确：示例通道当时放的是 CLI 二进制，不是 GUI 安装包；npm 正式 publish、GUI 包、其他发行渠道和真机清单有待办。不能仅根据 npm 包目录、发行计划开头或 v1.1.1 验收清单标题宣称已正式发布/三平台验收通过。本次未联网验证下载、安装包或生产更新源。


依据：[desktop/docs/22-ux-improvements.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/desktop/docs/22-ux-improvements.md)、[desktop/docs/24-distribution-plan.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/desktop/docs/24-distribution-plan.md)、[desktop/docs/25-device-acceptance-checklist.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/desktop/docs/25-device-acceptance-checklist.md)、[desktop/npm/cli/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/desktop/npm/cli/README.md)。

## 发布前必须知道

推广归因涉及后端/数据库、管理静态资源和会员前端三个产物。`scripts/release-acquisition.sh` 的 plan、preflight、execute 不能混称“只读”；子服务各自持锁，组合发布不是跨服务原子事务，出现版本差异时可能是部分成功，不能为了修复自己这一批而回滚别人的更新。核对固定 commit、备份事实回执、运行身份和会员端 release 标记；未知或旧快照不当作成功证据。

本技能更新只发布知识，不更新或部署 AIGatewaySystem 本身的业务代码、鉴权、计费、路由和生产配置。


依据：[docs/acquisition-release.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/acquisition-release.md)、[scripts/release-acquisition.sh](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/scripts/release-acquisition.sh)、[docs/deployment.md](https://github.com/UltimateJob/AIGatewaySystem/blob/4ba12289142f12c78eaf4c6fbcbd2481436e3878/docs/deployment.md)。
