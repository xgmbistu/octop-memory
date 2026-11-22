# AGENTS.md

Shared working agreement for coding agents. Start with the [README](README.md),
[documentation index](docs/README.md), and [CONTRIBUTING](CONTRIBUTING.md).
Engineering knowledge lives in `docs/agent/`; host setup lives in the
[integration guide](docs/integrations.md). Follow the clarification, implementation,
validation, and documentation loop below.
This file governs repository contributions. Hosts own the memory instructions,
workspace templates, and file-access policies used by their running agents.

## Project overview

`octop-memory` is an independently usable and releasable memory library, called at runtime
by Octop, octop-harness, and other hosts. Maintain it as a reusable memory foundation;
users need neither an Octop deployment nor adjacent repository checkouts.
This repository owns evidence-capture rules, fact extraction, recall, storage, and migration.
Upper layers own agent-turn wiring, execution scheduling, and product interfaces.
The core uses the standard library and SQLite; PostgreSQL, vector indexes, and LLMs use optional backends/interfaces.

- Public entry points: `Memory` (`core.py`) and `MemoryService` (`service.py`); shared orchestration is in `application/`.
- Business pipelines live in `pipeline/`, persistence in `storage/`, and CLI/JSON-RPC adapters in `adapters/`.
- `plugins/<host>/` adapts external hosts, currently OpenClaw and Hermes. New adapters reuse shared business logic.
- Find implementation and validation entry points in [PROJECT_MAP](docs/agent/PROJECT_MAP.md)
  and [TEST_MATRIX](docs/agent/TEST_MATRIX.md). Package paths above are relative to `src/octop_memory/`.

## Repository ownership and collaboration

Dependencies flow **Octop → octop-harness → octop-memory**; Octop's memory-management API also calls octop-memory directly.
Production code here must not depend on the other two repositories. Identify the owner of a behavior before editing;
a problem appearing in Octop's UI does not justify copying memory algorithms or agent-turn logic into Octop.

| Change | Primary repository | Check related consumers |
|---|---|---|
| Extraction results, promotion/conflict rules, recall sources/ranking, evidence, data contracts | octop-memory | Check Harness consumers and Octop's management API when public interfaces/results change. Algorithm fixes with unchanged interfaces need no duplicate implementations upstream. |
| Capture/extraction timing, prompt injection/replay, memory-tool binding, background review/maintenance, instance lifecycle | octop-harness | Reuse memory APIs; involve Octop for product switches, persisted settings, or status display. |
| Auxiliary-model selection, retries, timeouts, and configuration forwarding for Octop agents | octop-harness | Octop owns configuration UI/storage/mapping; memory owns the generic LLM protocol and algorithm budgets. Fix host calls rather than hiding failures with prompt changes. |
| Session loading of USER.md/MEMORY.md, agent write protection, runtime memory instructions | octop-harness | Octop owns user editing, owner permissions, and file saving; memory owns semantic reconciliation, conflict candidates, and recall suppression. |
| User memory settings, HTTP/CLI, permissions, memory/review UI, proactive-reminder product flows | Octop | Apply settings through Harness configuration/public memory APIs. Put new algorithms or generic turn behavior in the owning library. |
| Schema, SQL, namespaces, checkpoint encoding, migrations, generic space maintenance | octop-memory | Check Harness resource reuse/closure and Octop statistics, backup/restore, thread cleanup, and online-pause coordination. |
| OpenClaw/Hermes hooks, tool schemas, installation configuration | This repository's `plugins/<host>/` | Reuse this repository's Runtime; external hosts need no changes to octop-harness or Octop. |

Do not confuse the two `MemoryRuntime` classes: this package's `application.runtime.MemoryRuntime`
is host-neutral orchestration; `octop_harness.memory.runtime.MemoryRuntime` adapts assembly and lifecycle to agents.
See the [repository integration map](docs/agent/PROJECT_MAP.md#repository-integration-map) for files and call chains.

For work spanning repositories:

1. State the primary repository, affected consumers, API/configuration/data compatibility, and acceptance criteria
   in the Issue/PR. Read the other repository's AGENTS before editing it.
2. Trace real consumers when public fields, RPC results, configuration, or persistent formats change;
   library unit tests alone are insufficient. Audit Octop's existing direct table readers, but do not use
   those management paths as a template for new business logic that bypasses library APIs.
3. Use [validation across repositories](docs/agent/TEST_MATRIX.md#validation-across-repositories).
   Record the versions/source revisions actually loaded. A green library suite, a green old installation,
   or skipped PostgreSQL/host cases cannot establish cross-repository acceptance.
4. Link related PRs and state dependency order. To consume new interfaces, release the lower-level library first,
   then update Harness/Octop dependency declarations and lockfiles and verify the consumer loads the new version.
   Local source integration does not mean released users have the fix. UI-only work needs no unrelated library edits.

## Working practices

- Check `git status --short` and relevant diffs first; preserve existing user changes.
- For nontrivial work, state the goal, files, expected behavior, minimal validation, and risks. Stage large work and keep scope focused.
- Update affected code, tests, configuration, and documentation together. Avoid unrelated refactors and per-task document proliferation.
- Communicate in the requester's language; preserve code identifiers, CLI flags, environment variables, and error messages verbatim.
- Use English PR titles by default unless the requester explicitly asks for another language.
- Use generic placeholders and temporary databases. Never commit personal paths, runtime records, credentials, memory exports, or real databases.

## Documentation language

Maintain `AGENTS.md`, `CONTRIBUTING.md`, and `docs/agent/` in English as the engineering source of truth.
Keep the README and integration guide available in English and Chinese, with reciprocal language links;
keep their technical contracts, commands, and examples aligned. The documentation index is in English and links both user-facing languages.

## Engineering documentation workflow

**Scope:** `docs/agent/` records business logic, architecture, public APIs, data contracts, recall/write behavior,
and related bugs, requirements, design tradeoffs, and unresolved risks.
Routine banner, layout, wording, link, Python/dependency/lockfile, build/CI, and personal-tool maintenance belongs
in the affected files and necessary README/CONTRIBUTING/CHANGELOG updates; do not create HANDOFF entries or ADRs for it.
If such maintenance changes runtime behavior or data contracts, document that code impact rather than a maintenance diary.
The following requirements apply according to actual impact, not file count or whether source files changed.

1. **Check in:** inspect relevant code, diffs, and recent related commits against
   [HANDOFF](docs/agent/HANDOFF.md) and [PROJECT_MAP](docs/agent/PROJECT_MAP.md).
   Check recall sources/order, public APIs, configuration, prompts, and validation commands.
   Judge freshness from implementation, not dates or commit counts. Correct drift; record out-of-scope gaps in
   [KNOWN_RISKS](docs/agent/KNOWN_RISKS.md).
2. **Clarify in text:** use the existing Issue/PR or HANDOFF to describe actual/expected behavior and a minimal
   reproduction, or the user scenario, scope, exclusions, and verifiable acceptance criteria.
   List assumptions and unresolved questions. Resolve questions affecting scope, compatibility, or data safety;
   continue already-authorized work without asking for the same permission again.
3. **Implement and validate:** complete the smallest verifiable loop and run relevant tests and the full gate.
   Apply the mandatory recall/write and backend rules below when affected.
4. **Update knowledge:** for nontrivial code work, update HANDOFF with current status, key files, actual validation,
   risks, and next steps. Update PROJECT_MAP for modules/call chains/runtime configuration;
   [DECISIONS](docs/agent/DECISIONS.md) for important tradeoffs;
   [TEST_MATRIX](docs/agent/TEST_MATRIX.md) for validation changes; KNOWN_RISKS for code-related gaps;
   [GLOSSARY](docs/agent/GLOSSARY.md) for terms; and check [README_AUDIT](docs/agent/README_AUDIT.md)
   when public behavior changes.
5. **Sync GitHub Wiki:** whenever `docs/` changes issue descriptions, status, known risks, or development plans,
   update the corresponding pages in this repository's [GitHub Wiki](https://github.com/TencentCloud/octop-memory/wiki)
   in the same work session. Keep affected English/Chinese pages aligned, cite the source Issue/PR/revision,
   and distinguish proposed, merged, and released behavior. Check the actual PR state before publishing;
   a validated PR is not a released fix. If Wiki access prevents synchronization, report the exact pending pages.

Each document owns its facts. HANDOFF keeps active work and unresolved items; move merged tasks out of active work,
retaining only useful history links and follow-up boundaries. Put durable knowledge in the map, decisions, tests, or risks.
Merged code is not evidence of fresh validation in the current environment.
Keep stable ADR numbers and supersession relationships, check statuses against implementation, and avoid dated activity logs.
Correct documentation drift in the relevant knowledge files without recording documentation cleanup as a new code task.
Updating only HANDOFF while omitting affected maps or test guidance is incomplete.

## Architecture constraints

- `Memory` is the public storage API. Shared host operations in `MemoryService`/`Bridge` reuse `application.MemoryRuntime`.
  `MemoryService.recall()` calls the prompt pipeline directly; verify tool-search and prompt-recall configuration/sources separately.
- pipeline/storage/domain must not depend on adapters; storage must not depend on pipeline; service must not depend on bridge.
- New hosts use shared application logic. The source dashboard's direct SQLite access is an existing exception, not a new-adapter template.
- `AtomCard` is the canonical fact; tree leaves reference atoms. Chroma/Qdrant are optional indexes, not relational backends.
- Runtime incremental extraction commits candidates and the durable cursor in one transaction, then advances in-memory progress.
  Never mark success before candidates persist, or equate that commit with successful promotion/page/Episode stages.
  Check lower-level extractor failure semantics separately.
- Automatic page regeneration passes and atomically checks the snapshot's `mutation_version`; failed guards must not fall back
  to unconditional writes. Preserve legacy public low-level page calls without version conditions; all page writers maintain revision semantics.
- `MemoryService.save()` stores the fact and notifies a nonblocking scheduler. Hosts run synchronous `review_new_memory()` in the background.
  Current manual files govern reconciliation; the actual chat snapshot governs recall deduplication. Keep those inputs distinct.
- Verify host configuration forwarding, hook scheduling, and actual execution separately. A configured model does not prove extraction ran;
  do not assume profiles have identical semantics across hosts.
- Do not change public APIs, data formats, configuration defaults, or production dependencies without task authorization.

Detailed contracts are in [PROJECT_MAP](docs/agent/PROJECT_MAP.md); host capabilities and limits are in the
[integration guide](docs/integrations.md) and [KNOWN_RISKS](docs/agent/KNOWN_RISKS.md).

## SQLite and PostgreSQL gate

Both are supported production memory backends. Changes to public reads/writes, persistence orchestration,
backend contracts, schema, SQL, transactions, FTS, or lifecycle must:

1. Maintain both implementations and validate the same behavior assertions, preferably in `tests/test_backend_parity.py`.
2. Use a real dedicated PostgreSQL database through `TEST_POSTGRES_DSN`; confirm relevant PG cases did not skip.
3. Explicitly reject the other backend for deliberately backend-specific capabilities, documenting the reason in KNOWN_RISKS.
4. Keep backend-specific SQL in `storage/backends/`. Existing capability gaps do not justify new silent divergence.

## Sensitive recall and write paths

| Area | Explain the effect on |
|---|---|
| `core.py`, `storage/backends/` | Public writes, transactions, schema, indexes, namespaces |
| `pipeline/extractor/`, `pipeline/promotion/`, `pipeline/episode/` | What becomes a Candidate, AtomCard, or Episode |
| `pipeline/recall/`, `pipeline/page/` | Sources, ranking, raw policy, deduplication, budgets, page content |
| `application/runtime.py`, `application/path_projection.py`, `application/host_files.py` | Tool search, readable paths, host files |
| `adapters/bridge/handlers.py`, host hooks | Host capture/extraction and memory_search/memory_get behavior |

Mark behavior changes with `⚠️ Recall/write path change`, naming the affected sources/layers and validation commands.
For documentation/build-list edits, state that behavior is unchanged; do not describe documentation cleanup as a runtime change.

## Validation and delivery

```bash
make install-hooks    # Once per clone; never bypass a failed gate.
make all              # Format + lint + strict mypy + pytest.
```

Run focused tests before the full gate for code changes. Documentation-only work needs relevant documentation checks;
the full gate still runs before a commit.
Use `tests/test_agent_docs.py` and `tests/test_architecture_boundaries.py` for documentation checks.
When adding/moving files or changing headings, update navigation, local links, and heading anchors;
check public-document coverage, directory contracts, and the sdist allowlist.
Find the first failure's cause, make the smallest in-scope fix, and rerun.
If the environment or an existing issue prevents validation, report failures/skips and reproduction commands without claiming success.
Before delivery, confirm acceptance and alignment with code. For work within the engineering-documentation scope,
record actual validation and unresolved items in HANDOFF. Never label an unvalidated state as accepted.
Summarize changes, validation, and remaining limits; no fixed multi-section handoff response is required.

Without explicit user authorization, do not push, rewrite Git history, delete large directories, deploy production, or change secrets.
See [TEST_MATRIX](docs/agent/TEST_MATRIX.md) for backend/environment commands and
[CONTRIBUTING](CONTRIBUTING.md) for branching and release checks (`develop` integration and the `/publish` skill).


<!-- wally-init:entry:start -->
## 先判断是否属于开发任务

- 必须走开发 SOP：实现功能、修复缺陷、重构、性能优化，以及改变程序行为的接口、数据结构、配置、脚本、Agent 规则/Skill 等修改。开发需求中的方案、契约和配套文档也属于该任务；不能因为改动少或暂时只写文档而豁免。用户明确要求开始/继续 SOP 时按任务上下文执行。
- 直接处理、不创建 SOP 任务：问题咨询、原理解释、只读分析/独立审阅、状态查询、与开发无关的对话，以及纯文档措辞整理，以及暂存/提交已有改动（git add / git commit）。先核对实际请求和 diff；提交操作本身不要求新建 SOP 任务，不因已有改动包含代码而倒补六阶段产物；仍须遵守已有开发任务的交付门禁、项目提交规范与用户授权。
- 是否进入 SOP 取决于当前请求的工作性质，不取决于问句形式、文件扩展名、改动行数或当前分支是否已有任务。咨询过程中用户转而要求开发修改时，再进入开发 SOP；混有代码、运行配置、规则或行为变更时不套用纯文档豁免。已有开发任务的代码交付也不能通过改称“只做提交”绕过适用门禁；工具 Hook 对 Git 操作中立放行不代表门禁已完成或已获得 Commit/Push 授权。

## 开发任务的 SOP 启动检查

确认属于开发任务后，任务简单、改动少、只加一个页面都不是跳过 SOP 的理由。读取本入口不代表已完成任务路由；在探索实现方案、编辑业务文件或执行变更命令前，必须完成：

1. 读取 `.wally/core/entry.md`，运行 `git branch --show-current`，按分支定位任务；无任务则先读 `.wally/profiles/project.md`，用 `.wally/scripts/create_task.py` 创建任务。不要猜测任务目录或套用其他任务。
2. 运行 `python3 .wally/scripts/sop_context.py`，读取它实际输出的任务 overview、版本规则、项目配置和当前阶段。输出缺文件、多任务匹配或其他错误时先修复；不能绕过并继续实现。
3. 在首次工作说明中报告真实的分支、任务目录、规则版本和当前阶段；无任务时如实说明需要创建。不得未读取就声称已读取。
4. 进入每个阶段前读取对应阶段文件与所需绑定规则，填写 Clarify 和 Plan 后再实现。压缩上下文、恢复会话、切换分支及委派子 Agent 后重新定位；委派时明确传入任务目录、规则版本和阶段，子 Agent 也执行本检查。

5. 知识库先读 `.wally/docs/INDEX.md`，按任务绑定版本的 `core/knowledge.md` 读取、更新和验收相关页。索引缺失时回查 Profile 的实际文档路径与源码，并记录缺口。

## 阶段与完成条件

仅用于已确认属于开发工作的新任务；咨询与轻量文档操作不激活本流程，已有开发任务始终以其绑定版本为准，本概览不能替代历史任务契约。

- 01 Clarify：目标、范围、成功判据、关键约束、未决业务问题。先读本规则版本中的 `clarify.md`；已有用户输入可直接整理与校验，不重复访谈。
- 02 Plan：影响范围、调用链/状态机、数据及协议兼容性、UT 和 IT 设计、风险与回滚。
- 03 Implement + UT + Docs：Red → Green → Refactor → 增量覆盖率 → Docs → 增量 CR。适用门禁未通过不得 Deploy。
- 04 Deploy：环境、基线、部署范围、生效验证、回滚。热更前保留缺陷基线。
- 05 IT：按 Plan 执行，核验逐用例结果与总体门禁，完成缺陷 A/B。
- 06 Review + Commit：复核变更后的证据、时间记录和遗留风险，完成外部系统/资源处置及提交准备，再按授权执行 Git。

新任务始终保留 01–06 六阶段。 显式标记 `readiness: pending` 的方法即使有 guide/command 也不完整，标记 BLOCKED 并按 `gaps` 向用户询问补齐，不能自动跳过；只有 ready 方法（或未带 readiness 的旧配置）按下述 command/guide 规则判断，ready 不等于执行通过。每次进入 Deploy/IT 前读取本任务 `execution.json`：对应 command 与 guide 都为空时自动跳过，不准备环境、不调用工具；使用创建任务时已生成的 SKIPPED 记录与零耗时行。配置了任一方法则按客户实际命令/指南执行，缺环境、权限、工具或执行失败均不得伪装成未配置而跳过。跳过不是通过，必须在 Review 说明未完成部署/集成验证；其他适用门禁继续执行。历史任务按自己的绑定版本恢复，不因新规则改写。

在开始 Implement、Deploy、IT 的实际操作前，分别运行 `python3 .wally/scripts/sop_context.py --checkpoint implement`、`--checkpoint deploy`、`--checkpoint it`。Clarify/Plan 未记录完成或仍为空模板，以及用户准备执行未配置方法的 Deploy/IT 时，必须先展示缺失项、拟执行操作和影响，等待用户确认后才继续。默认自动跳过未配置的 Deploy/IT 不需要确认；确认例外也不提供执行方法，仍须取得真实命令/指南，不能猜测。

检查点退出码 3 表示等待确认。使用提问工具或对话清楚展示原因与 `CONFIRM SOP <编号>`；用户需在聊天中明确发送该文本，输入 Hook 才会记录确认。Agent 不得自行发送确认、修改 `.wally/local/sop-confirmations.json`、伪造产物或反复重试。拒绝、无回复、无效或过期编号均不视为确认。同任务/阶段且相关材料未变时不重复询问；分支、任务、阶段、绑定规则或相关材料变化后重新检查。缺少输入 Hook 的环境只能保留等待状态或先补齐前置材料，不能声称自动确认。

确认允许带缺项继续当前阶段，须在 overview 记录实际用户授权、缺失证据和未验证范围；不自动勾选前置阶段，不把 SKIPPED/未验证改为通过，不免除其他适用验收。质量要求由阶段检查与 Review 持续核验。普通工具操作不因 SOP 白名单或上下文错误被强制拒绝；Shell/MCP 不做全面拦截，阶段检查点由 Agent 主动调用，已有客户端权限和用户授权继续生效。

Hook 负责加载上下文，并仅对已识别业务编辑触发上述两类确认；普通 Shell、Git、date 等不做 SOP 白名单拦截。实现/部署/IT 前必须主动运行对应 `--checkpoint`，等待明确用户确认或补齐前置条件后继续。确认只允许带已披露缺项继续，不能把未验证阶段记为完成。Hook 未启用、不支持或未受信任时保留指令约束，不声称强制覆盖。已有客户端权限、用户约束与授权边界继续生效。
<!-- wally-init:entry:end -->
