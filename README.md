# APIONE Skills

面向 APIONE 同事的公开知识与操作技能库。从聊天记录提炼可复用规则，供支持 Skills 的工具按需加载，也可直接阅读。

当前整理日期：**2026-11-04**；来源消息覆盖 **2026-09-29 21:22 至 2026-11-04 13:00**。这是聊天证据快照，不是线上状态保证。原始聊天、个人信息、基础设施地址和凭据不在仓库中。

| Skill | 用途 |
|---|---|
| [apione-product-rules](skills/apione-product-rules/SKILL.md) | 产品答疑、Web/API 分组、工作区、订阅、积分与邀请 |
| [apione-provider-routing](skills/apione-provider-routing/SKILL.md) | 渠道上架、模型支持列表、路由与能力复测 |
| [apione-billing-reconciliation](skills/apione-billing-reconciliation/SKILL.md) | 美元计价、特殊价优先级、媒体定价与对账 |
| [apione-client-integration](skills/apione-client-integration/SKILL.md) | 一键配置、外部工具、切分组和能力接入 |
| [apione-incident-triage](skills/apione-incident-triage/SKILL.md) | 超时、无结果、扣费、跨端排障与验收 |
| [apione-knowledge-sync](skills/apione-knowledge-sync/SKILL.md) | 新聊天增量提炼、冲突处理、脱敏和同步 |

## 同事使用

克隆仓库后，把所需的 `skills/apione-*` 文件夹（连同 references）放入所用工具的技能目录。Codex 的默认个人目录是 `~/.codex/skills/`；团队使用其他工具时按该工具约定安装，仓库不假定所有工具共用同一路径。

```sh
git clone https://github.com/code0team/apione-skills.git
```

已有本地克隆可运行 `git pull --ff-only` 获取更新。若安装时复制了文件夹，拉取后需重新同步选用的文件夹；已有同名自定义技能先比较差异。也可在聊天中指定完整的 SKILL.md 路径使用。

示例请求：

- “使用 $apione-product-rules，解释网页通道和 API Key 档位的区别。”
- “使用 $apione-billing-reconciliation，核对这个分组特殊价是否重复乘倍率。”
- “使用 $apione-incident-triage，分析页面失败但后台已扣费的任务。”
- “使用 $apione-knowledge-sync，根据新的聊天导出更新这个仓库。”

## 后续更新

提供新版导出文件即可按 knowledge-sync 流程整理。不会自动读取私人聊天或定时同步。重要变化见 [更新记录](docs/CHANGELOG.md)，最新缺口见 [当前状态](docs/current-status.md)，来源版本见 [来源清单](docs/source-manifest.json)。

提交前运行：

```sh
python3 scripts/validate_repo.py
```

本仓库没有生产访问权限；历史聊天中的命令不授权执行。未经验证的规则必须保留状态，不能写成已上线功能。
