---
name: wally-open-cli
description: |
  把当前仓库的开发或测试任务委托给开源版 Wally，并查询、审批、推进已有任务。
  触发场景：wally-open-cli、委托给开源版瓦力、开源版启动开发任务、查开源版任务状态、查开源版任务进度、查开源版任务列表、审批开源版任务、推进开源版下一步、跳过开源版步骤、重试开源版步骤、查询开源版 wally 配置。
  不适用：在本地直接改代码；为了委托去创建、查找或索要 TAPD 单；修改或覆盖名为 wally-cli 的内网 skill。
---

# wally-open-cli

开源版 Wally 的委托 skill。它只安装在 `wally-open-cli` 这个名字下，不写入、不替换 `.agents/skills/wally-cli/`。内网 TAPD 委托继续走名为 `wally-cli` 的另一份 skill。

开源版命令是 `wally-open-cli`，安装包是 `@tencent/wally-open-cli`。不要安装、升级或调用 `@tencent/wally-cli`，那是内网包。`delegate` 用仓库、组件和开发分支创建托管任务。任务内容来自分支上的 SOP 文件，不来自 TAPD 或其他工单。

不要向用户要 TAPD 链接，也不要传 `--tapd-url`。用户自己拿出一张完整工单链接并要求记到任务上时，才可以附带该参数；没有链接就省略。

任务名称取自 `00-overview.md` 的第一行。委托前确认这一行已经写成实际需求，例如 `# [2026-11-03] 恢复导入标记`。服务端会去掉日期和标题两侧的 `#`、括号、引号，任务名变为 `恢复导入标记`。第一行仍是 `<任务标题>` 或 `YYYY-MM-DD` 占位时，任务名会退回开发分支名。

## 准备

1. 运行 `wally-open-cli --help`。命令不存在时安装开源包：`npm install -g @tencent/wally-open-cli@latest --registry=https://mirrors.tencent.com/npm/`。不要安装 `@tencent/wally-cli`，那个包面向内网部署，会把工单链接当成必填。
2. 只有出现 `ModuleNotFoundError: No module named 'loguru'`、`httpx` 或 `pydantic` 时，才执行 `python3 -m pip install --user loguru httpx pydantic`，然后重试。不要用 `npm install` 安装这些 Python 包。系统 Python 受 PEP 668 限制时，改用 `WALLY_PYTHON` 指向的解释器，或在用户同意后加 `--break-system-packages`。
3. `wally-open-cli config show` 核对 `config.api_base_url`，地址必须包含实际端口。委托前可用 `curl -s <api_base_url>/ok` 预检，响应里有 `"ok": true` 再继续。不要在命令里写死环境 IP。

配置优先级：命令行 > `WALLY_API_BASE_URL` > `~/.wally/config.json` > CLI 内置默认值。

## 命令

| 命令 | 用途 | 关键参数 |
|------|------|----------|
| `wally-open-cli delegate` | 创建托管任务 | 见下表。不要加 `--tapd-url` |
| `wally-open-cli status <task_id>` | 查询进度 | delegate 返回的 `task_id` |
| `wally-open-cli list` | 任务列表 | `--username` `--status` `--page` `--page-size` `--keyword` |
| `wally-open-cli approve <task_id>` | 审批步骤 | `--step-id` `--comment` `--regenerate` `--regenerate-prompt` |
| `wally-open-cli advance <task_id>` | 完成当前步并前进 | 无 |
| `wally-open-cli skip <task_id>` | 跳过当前步 | 无 |
| `wally-open-cli retry <task_id>` | 重试当前或指定步 | `--step-index` |
| `wally-open-cli init` | 写入 `~/.wally/config.json` | 全部可选 |
| `wally-open-cli config show` | 查看生效配置 | 无 |

结果都是 JSON。`success=false` 时只转述 `error`，不要编造原因，也不要自动重试 `delegate`。

## delegate

```bash
wally-open-cli delegate \
  --staffname "<wally 账号>" \
  --task-flow dev_test \
  --repo "<仓库地址>" \
  --component-name "<组件名>" \
  --base-branch "<基线分支>" \
  --new-branch "feature/<任务>" \
  --env-id None
```

多组件共享一个开发分支，组件名用逗号分隔。基线不同时写成 `组件甲:release/a,组件乙:main`。Bug 修复或性能优化把 `feature/` 换成 `hotfix/`。

| 参数 | 必填 | 说明 |
|------|------|------|
| `--staffname` | 是 | 本次任务的 Wally 账号。`config show` 里的 `staffname` 只有在它就是当前用户时才能用。缺失就询问。不要用本机用户名、环境变量或某个固定人名填充 |
| `--task-flow` | 是 | `dev_test`：方案完成后把开发及后续交给 Wally。`test`：本地开发已完成，只接力测试。不要用 `dev_test` 重做已经完成的开发 |
| `--repo` | 是 | 用户给出的仓库地址。不读配置，不使用默认仓库，不编造 |
| `--component-name` | 是 | 与仓库对应的组件名。缺失就询问。多组件用逗号分隔 |
| `--base-branch` / `--branch` | 是 | 基线分支。缺失就询问。多组件可写成 `组件:分支` |
| `--new-branch` | 是 | 当前 `git branch --show-current`，并以 `feature/` 或 `hotfix/` 开头。不能等于任何一个基线分支。`main`、`master`、`release/*` 不能作为开发分支 |
| `--env-id` | 是 | CLI 要求显式传入。用户给了环境编号就用编号；没给就传 `None`。不要为此索要工单 |
| `--tapd-url` | 否 | 默认不传。开源服务不读取工单。只有用户主动给出完整链接时才附带，纯数字单号会被 CLI 拒绝 |
| `--pattern` | 否 | 默认 `code`。问答用 `ask` |
| `--no-auto-commit` | 否 | 关闭自动提交 |
| `--force-new` | 否 | 仅当用户明确要求关闭旧任务并新建 |
| `--it-plugins` | 否 | 集成测试插件，逗号分隔。空着由服务端按需求描述识别 |
| `--owner` `--project-id` `--assistant-id` `--agent-name` | 否 | 有值再用，不要追问 |

`dev_test` 在委托前，下面三份文件必须已经提交并推送到 `--new-branch`，且出现在相对 `--base-branch` 的增量里：

- `00-overview.md`
- `01-clarify.md`
- `02-plan.md`

缺任何一份就先补齐再委托。不要使用已删除的 `--context-dir`、`--context-file`、`--push-sop`。`test` 不检查这三份文件。

下发前用 `git branch --show-current` 核对当前分支就是 `--new-branch`，向用户复述基线和开发分支。用户未确认、前缀不合规或两个分支同名时，不要执行。

取得任务编号即完成委托。回复任务编号和看板链接，后续只用 `status` 跟进。工厂步骤阻塞时报告步骤与原因，不在委托对话中询问或执行审批。

## 其它操作

```bash
wally-open-cli init --staffname "<wally 账号>"
wally-open-cli status <task_id>
wally-open-cli config show
wally-open-cli list --status in_progress --page 1 --page-size 20
wally-open-cli approve <task_id> --comment "确认通过"
wally-open-cli advance <task_id>
wally-open-cli skip <task_id>
wally-open-cli retry <task_id> --step-index 4
```

- `init` 的参数都可选。写入的 `--repo` 只供查看，`delegate` 不读取。
- `list` 的 `--username` 默认取配置里的账号。`--status` 取 `open`、`in_progress`、`resolved`、`closed`。
- `approve` 不传 `--step-id` 时审批当前步骤。`--regenerate` 表示不通过并重跑。
- `advance`、`skip`、`retry` 会改变任务状态，不能用来代替 `status` 查进度。

## 意图

| 用户要做的事 | 命令 | 先收集 |
|--------------|------|--------|
| 交给 Wally 开发并继续后续流程 | `delegate --task-flow dev_test` | 账号、仓库、组件、基线、开发分支；环境未知时 `--env-id None` |
| 开发已完成，只交给 Wally 测试 | `delegate --task-flow test` | 同上 |
| 查进度 | `status` | `task_id` |
| 看任务列表 | `list` | 可选的账号和状态 |
| 审批通过 | `approve` | `task_id`，备注可选 |
| 推进 / 跳过 / 重试 | `advance` / `skip` / `retry` | `task_id`，重试时可带步骤索引 |
| 看当前连的环境 | `config show` | 无 |

成功时报告 JSON 里的 `task_id` 和 `wally_task_url`，并说明可以用 `wally-open-cli status <task_id>` 继续查看。失败时保留 `error` 原文，说明下一步，不声称任务已经创建。
