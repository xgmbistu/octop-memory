# 知识库读取、增量写入与验收

本规则随任务绑定的 SOP 版本加载；知识内容读取当前工作树。所有路径均相对仓库根目录，元数据中的文档路径相对 `.wally/docs/`。

## 统一入口与权威来源

先读 `.wally/docs/INDEX.md`，按任务意图和源码路径定位相关页，再读正文及源码核实。`.wally/docs/.wiki-meta.json` 的 `fileToDocs` 是影响分析提示，不是完整性证明。索引/元数据缺失、映射遗漏或文档过期时，查项目 Profile 的实际文档路径及源码，记录缺口；不能把骨架、文件存在或索引已加载当成正文已读。

- 架构：`.wally/docs/overview/system-architecture.md`、`architecture/`；业务：`business/`；上下游：`integrations/index.md` 及其子页。
- 契约：`contracts/`；运维知识：`operations/`。以上由 `wally-codewiki` Mode B 维护。
- 项目已有 API/SQL 权威文档沿用原路径；SOP 专用执行规范为 `.wally/docs/apis/`、`sqls/`、`unittest/`、`integration_test/`、`devops/` 或 Profile 明确配置的现有路径。codewiki 对相同事实引用这些文档，不复制维护第二份。
- 不新建旧的 `.wally/docs/architecture.md`、`relationship/` 或 `README.md` 总导航。已有旧路径只作迁移线索，确认实际权威页后在 INDEX 中路由；保留人工定制。

## 按阶段读取与写入

1. Clarify / Plan：读相关业务、架构、契约、上下游与测试规范；在阶段文档记录实际读过的路径、相关结论、源码核验及缺口。Plan 列出预计受影响的知识页。
2. Implement：根据实际任务 diff 重新计算影响页，使用 `fileToDocs` 并检查调用方、下游、配置、测试和新增/删除/重命名文件；同步更新正文、源码锚点、关联页、INDEX 与元数据。用 `wally-codewiki` Mode B 维护知识页，SOP 执行规范更新其原权威文件。不要只改任务记录或只追加更新日志。记录“源码变化 → 文档路径 → 更新/无需更新及依据 → 校验结果”。
3. Deploy / IT：读取 Profile 绑定的部署、单测/集成测试执行规范及相关 `operations/`、`integrations/` 页；环境或运行行为的新事实回写原权威页。后续代码变更重新执行 Docs 影响评估。
4. Review / Commit：以最终任务 diff 对照上述对应关系复查；验证路径、链接、源码锚点和 INDEX/元数据一致性，以及文档是否反映最终行为。修复后复验。缺失、过期或未验证须明确报告，不能将 Docs 标成通过。

## 增量范围与完成条件

任务变更范围和 wiki 基线范围分别检查，取并集；不可仅运行默认 `git diff`。包括基线到 HEAD 的已提交变化、暂存区、工作区，以及未忽略的未跟踪源码；删除/重命名检查旧、新路径。未纳入 Git 的敏感文件不进入知识库。缺失基线/映射时扩大源码检查范围，不能据此判断无需更新。

保留 `origin: human` 或 `status: verified` 页，不自动覆盖；列出漂移和建议修订，未解决漂移保留为未通过/未验证。仅在对应范围验证成功后更新元数据；工作树未提交时保留已提交基线，记录实际检查范围，不把 HEAD 冒充包含未提交内容的新基线。部分更新不能推进全库基线。知识库缺失时明确补建范围；不能伪造通过。
