# 源码实现状态与历史差异

最新源码核对见 [2026-11-13 增量](project-update-2026-11-13.md)；本页保留 11-07 固定快照，新增及变化以增量中注明的证据为准。

核对日 2026-11-07；唯一源码版本 `a1d1b14b74377eada25c04adcd7f66be4c24a363`。本次只做静态核对；看到测试文件不表示本次执行过测试，看到路由不表示已部署。业务规则继续由 [业务规则](rules.md) 定义，以下用于解释实现。

## 套餐升级已有后端接线

- GET `/api/v1/subscription/upgrade/quote?planVersionId=N` 返回报价；不能升级时可能仍 HTTP 200，必须看 `allowed`/`blockedReason`。
- POST `/api/v1/subscription/upgrade`，body 为目标 `planVersionId`，强制 Idempotency-Key；从个人钱包可用余额扣差价，与套餐增额在同一数据库事务中完成。
- 代码校验价格差与总额度差均为正、订阅有效、目标版本发布以及当前周期存在；通过周期和订阅版本 CAS 防并发覆盖，账本升级键及 grant 记录支持重放。
- 不修改原 startsAt/endsAt；已有测试文件覆盖升级后可读、余额不足无部分入账、幂等、并发只发一次和账本平衡。本次未重跑这些测试。
- 业务失败码包括 not_an_upgrade、expired、no_subscription、plan_version_invalid、cycle_missing；余额不足及并发冲突按服务端返回分别处理。

**计算精度要按实际报价**：设计文档称直接以大整数对毫秒比例折算；当前后端先将毫秒剩余比例向下取到百万分比 remainingPpm，再对差价和额度向下取整到 nanoUSD；共享前端公式则直接对完整毫秒比例做 BigInt 计算。两者存在精度口径差异，不应承诺预览与最终金额逐 nanoUSD 完全相同。核账以服务端 quote/实际 transaction 为准；不要把这处实现差异改写成新的业务政策。

例如恰剩 8/28 周期，后端 remainingPpm 为 285714，$79 差价对应 22,571,406,000 nanoUSD；直接按精确比例取整为 22,571,428,571 nanoUSD。这是静态公式推导，非本次实测收费。设计文档开头仍写“后端待做”，后文和当前源码已出现实现，不能只引用旧状态行。


依据：[backend/internal/handler/product_subscription_upgrade.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/product_subscription_upgrade.go)、[backend/internal/repository/sqlite/subscription_upgrade.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/repository/sqlite/subscription_upgrade.go)、[backend/internal/domain/subscription_upgrade.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/domain/subscription_upgrade.go)、[backend/internal/repository/sqlite/subscription_upgrade_test.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/repository/sqlite/subscription_upgrade_test.go)、[packages/api-client/src/subscription-upgrade.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/packages/api-client/src/subscription-upgrade.ts)、[docs/design/2026-11-06-plan-upgrade-proration.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/design/2026-11-06-plan-upgrade-proration.md)。

## 积分：数值一致，适用范围仍有缺口

- 当前 `DefaultPointsConfig`：每 $0.20 消费得 1 积分，即每 $1 得 5 积分；100 积分换 $1。兑换档位和启用状态仍应从当前配置读取。
- 1 积分 = 1,000,000 micropoints；有规则版本/小额余数累积、退款修正、批次过期逻辑。代码以每笔获得时间起算 180 天，提醒提前 7 天；不是按自然月统一清零，也不是严格的日历 6 个月。
- 当前 settlement eligibility 函数只认可个人钱包出资、非组织代付；不能根据业务“余额和订阅适用”就宣称套餐/团队消费都发积分。
- 用户确认的邀请人充值奖励、被邀请人首充奖励和 7–15 天冻结仍是业务方案，本次没有核实其完整执行链，不能宣称这几项已上线。
- `docs/api/06-commerce.md` 仍有旧“每 $1 得 1 积分、10 分换 $1、无过期任务”说明，与当前 domain/lot 源码不符；读者应以当前代码和实际配置核对。


依据：[backend/internal/domain/points.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/domain/points.go)、[backend/internal/repository/sqlite/points_settlement.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/repository/sqlite/points_settlement.go)、[backend/internal/repository/sqlite/points_lots.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/repository/sqlite/points_lots.go)、[docs/api/06-commerce.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/06-commerce.md)。

## 特殊价与用户折扣的进展

- 分组价格覆盖 DTO/保存路径已有 resolution、generationMode、timeRules、contextTiers；时间规则校验与相关测试文件存在。因此 11-04 的“完全未适配”应标作历史反馈，最新状态是源码支持字段，完整 UI/结算仍待验收。
- 用户管理已有 `pricingMultiplierOverride`：10000 表示 1.0 倍，0 清除个人覆盖、回归分组倍率；仓库有替换分组倍率及代理成本分组例外的测试。它是**用户个人倍率**，不能擅自解释成任意“用户×每个分组”独立价格矩阵。
- 分组成员可选、仅管理员指派、绑定路由项目是不同字段。按当前管理端与用户更新契约操作，不猜造新接口。
- 源码有取消/自动续费相关通用订阅接口，不代表产品政策变成自动续费；继续执行一次性购买规则。


依据：[backend/internal/handler/admin_pricing_group_overrides.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/admin_pricing_group_overrides.go)、[backend/internal/handler/admin_pricing_group_overrides_time_rules_test.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/admin_pricing_group_overrides_time_rules_test.go)、[backend/internal/handler/admin_users.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/handler/admin_users.go)、[backend/internal/repository/sqlite/user_multiplier_override_test.go](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/backend/internal/repository/sqlite/user_multiplier_override_test.go)、[docs/api/05-api-keys.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/05-api-keys.md)、[docs/api/06-commerce.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/docs/api/06-commerce.md)。

## 桌面和能力声明

轻客户端已含 local-agent 工具循环及本机文件/命令能力；完整桌面是另一套 Agent/任务引擎。升级旧“只做配置”的客服口径时必须先核对用户安装包、目录对应产品及构建日期，不能把源码新增能力当作所有旧包都有。

媒体能力声明以厂商资料为基础；单个中继忽略比例/尺寸不能证明模型本身不支持。渠道探测要检查交付图像/视频的实际尺寸和可播放性，HTTP 200/succeeded 不是参数生效证明。

源码文档存在过时状态、合并冲突残留和设计/实现不同步；抽取新知识时优先查实际入口、实现、测试契约，不直接整篇复制。


依据：[apione-desktop/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/apione-desktop/README.md)、[apione-desktop/ui/src/features/local-agent/loop.ts](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/apione-desktop/ui/src/features/local-agent/loop.ts)、[desktop/README.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/desktop/README.md)、[desktop/docs/20-release-readiness.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/desktop/docs/20-release-readiness.md)、[AGENTS.md](https://github.com/UltimateJob/AIGatewaySystem/blob/a1d1b14b74377eada25c04adcd7f66be4c24a363/AGENTS.md)。
