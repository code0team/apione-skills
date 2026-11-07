# APIONE Skills

面向 APIONE 同事的公开知识与操作技能库。从聊天记录提炼可复用规则，供支持 Skills 的工具按需加载，也可直接阅读。

当前整理日期：**2026-11-07**；套餐及升级规则包含 11 月 5 日用户直接确认的更新；原群聊来源消息覆盖 **2026-09-29 21:22 至 2026-11-04 13:00**。另纳入 11 月 7 日固定 commit 的项目源码静态核对。这些是知识证据快照，不是线上状态保证。原始聊天、个人信息、基础设施地址和凭据不在仓库中。

统一入口：[APIONE skill](skills/apione/SKILL.md)。仅需安装一个 `apione`，包含产品规则、渠道路由、计费对账、客户端接入、排障验收及知识更新参考资料，按问题读取；新增 [项目功能](skills/apione/references/project-features.md)、[接入契约](skills/apione/references/api-contracts.md)、[实现状态](skills/apione/references/implementation-status.md)、[配置与运行](skills/apione/references/operations.md)。

## 同事使用

克隆仓库后，把 `skills/apione` 文件夹（连同 references）放入所用工具的技能目录。Codex 的默认个人目录是 `~/.codex/skills/`；团队使用其他工具时按该工具约定安装，仓库不假定所有工具共用同一路径。

```sh
git clone https://github.com/code0team/apione-skills.git
```

已有本地克隆可运行 `git pull --ff-only` 获取更新。若安装时复制了文件夹，拉取后需重新同步 `apione` 文件夹；已有同名自定义技能先比较差异。也可在聊天中指定完整的 SKILL.md 路径使用。

示例请求：

- “使用 $apione，解释网页通道和 API Key 档位的区别。”
- “使用 $apione，核对这个分组特殊价是否重复乘倍率。”
- “使用 $apione，分析页面失败但后台已扣费的任务。”
- “使用 $apione，根据新的聊天导出更新这个仓库。”

如果之前安装过六个 `apione-*` 技能，请先安装新的 `apione`，验证可用后移除旧六个技能文件夹，避免重复加载；自行修改过的内容先保留备份。

## 后续更新

提供新版导出文件即可按 `apione` 内的知识更新流程整理。不会自动读取私人聊天或定时同步。重要变化见 [更新记录](docs/CHANGELOG.md)，最新缺口见 [当前状态](docs/current-status.md)，来源版本见 [来源清单](docs/source-manifest.json)。

提交前运行：

```sh
python3 scripts/validate_repo.py
```

本仓库没有生产访问权限；历史聊天中的命令不授权执行。未经验证的规则必须保留状态，不能写成已上线功能。
