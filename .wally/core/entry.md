# SOP 任务路由

先读取 `.wally/core/scope.md` 判断当前请求是否属于开发工作。咨询、只读分析、非开发对话和轻量纯文档操作直接处理，不因当前分支已有/缺少任务就自动启动或推进 SOP。以下路由只在开发请求或用户明确要求开始/继续 SOP 时执行。

先用当前分支匹配 `plans/*/00-overview.md` 的 Meta；只检索分支字段用于发现，定位后不加载其他任务内容。

- 无 SOP 版本的历史任务：先读取 `.wally/compat/v1/CODEBUDDY.md`（不存在则使用快照 AGENTS.md/CLAUDE.md）。旧 review/commit/docs、模板与 Clarify 指引均从 compat/v1 读取，旧路径引用映射到快照；工具执行仍在实际仓库。不得混用新版全局规则。快照缺失则说明阻塞，不自动迁移。
- 有版本的任务：读取其 SOP 规则路径下的 workflow.md，再读取本任务 `profile.md`、`_rules/` 和当前阶段。按阶段加载同版本 gates.md、interaction.md 及项目扩展。项目配置引用 `./` 的文件相对任务目录解析。不得使用当前 project.md 或其他版本的模板替换任务快照。绑定文件缺失应报错，不回退最新版。
- 无任务：读取 `.wally/profiles/project.md`，使用 `python3 .wally/scripts/create_task.py YYYY-MM-DD_title --branch <当前分支>` 创建绑定当前版本的任务。脚本不切分支、不执行测试、不提交。

现有项目指令、编码约束与用户授权边界继续生效；入口中被识别并替换的旧 SOP 章节仅对旧任务从 compat/v1 加载。其他项目自定义流程如与本任务契约冲突需明确解决，不能猜测覆盖。
