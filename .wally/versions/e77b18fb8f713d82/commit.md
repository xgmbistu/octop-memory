# Commit 规范

完成最终 Review、时间记录审计、适用外部系统/资源处置、message 和已启用的 Token 报告后，先保存 overview 的提交准备内容，再按授权 git add、commit、push。只显式暂存本任务文件；不把准备完成当作提交成功。
message 格式、关联单号、一个 MR 的 commit 数与 amend 规则以项目配置和下方项目自定义为准。没有项目格式时采用 `<type>(<scope>): <subject>`，type 可用 feat/fix/perf/refactor/docs/test/chore。
时间审计不齐或无证据时退回缺步重做，不得标“漏记”后继续提交。
不提交凭证、原始 token.json 或临时测试运行产物；用户要求暂不提交/推送时停在该边界。生成 Token 报告不授权任何额外 Git 操作。

## 项目自定义

引用项目已有提交规范和 CI 规则；升级保留本区。
