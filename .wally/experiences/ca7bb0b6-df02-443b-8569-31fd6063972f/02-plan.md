# 02 · Plan（方案设计）

> **阶段任务**：在 Clarify 结论基础上，设计**原生** `GET /welcome` 路由、接口契约测试、启动与回滚方案；明确涉及文件与命令；仅产出方案文档，**不改源码、不新增路由、不运行实现、不提交**。
> **任务目标（用户授权）**：在当前仓库「现有 Web 服务」中增加原生 `GET /welcome` HTTP 路由，返回 JSON `message=welcome`。
> **分支 / 工作区**：`feature/wally-experience-ca7bb0b6`（平台创建，仓库独立副本；Git 提交由平台收尾）。`git branch --show-current` 实测为该分支，`git status --short` 仅 `?? .wally/`（前序阶段产物未提交），工作树无源码改动。
> **前序产物**：[00-overview.md](./00-overview.md)、[01-clarify.md](./01-clarify.md)。本阶段实地复核了 Clarify 的框架/路由/接口/测试结论（§二），并补齐启动链、mypy/ruff/sdist 边界、回滚所需事实。
> **阶段边界**：只写本文件；实施（03）、部署（04）、IT（05）、评审提交（06）由平台推进。

---

## 一、结论（先行）

1. **方案成立且无阻塞**：既有 FastAPI dashboard 上以 `@app.get("/welcome")` 注册一等路由即可满足目标，零新增运行依赖、零启动入口改动、零挂载改动、零配置/API/数据契约变更。
2. **改动最小**：1 个源文件新增 1 个带类型注解的函数（`adapters/dashboard/server.py` Routes 段）+ 1 个新契约测试文件（`tests/test_welcome.py`）。纯增量、纯只读端点。
3. **「原生」落地**：用既有框架自带装饰器在该 `app` 实例上注册；`create_app()`、`octop-memory dashboard` CLI、`TestClient(app)` 三者复用同一 `app`，路由自动被启动链与测试链同时覆盖（实测 §二.5）。
4. **验收条件明确可判定**（§十），启动/回滚方案完备（§七、§九），命令已固化（§八），可据以在 03 阶段「先写失败用例 → 再实现 → 再跑门禁」。

---

## 二、本阶段执行证据（实跑 / 实读）

| # | 动作 | 结果 |
|---|------|------|
| 1 | `git status --short` / `git branch --show-current` | `?? .wally/`；分支 `feature/wally-experience-ca7bb0b6`；无源码改动 |
| 2 | `python3 -c "import sys, fastapi..."` | `py 3.11.6`，`fastapi 0.115.0`（`[dashboard]` extra 可用） |
| 3 | `grep -rni welcome src tests` | 无命中 —— `/welcome` 当前确实缺失 |
| 4 | 实读 `server.py`（:1–50 / :240–299 / :660–712）、`test_dashboard_api.py`（:1–30 / :210–229 / :420–446）、`cli/dashboard.py`（:75–125）、`pyproject.toml`、`Makefile`、AGENTS.md | 见 §四、§五 |
| 5 | **实时探针** `TestClient(app)` | `app` = `fastapi.applications.FastAPI`；`create_app() is app` → `True`；route 对象 19 个（含 1 个 `/static` Mount 与 docs 默认路由），其中 15 个 GET 路径；**无 `/welcome`** |
| 6 | 探针 `GET /welcome` | `404`，体 `{"detail":"Not Found"}` —— 基线缺失，可作回滚对照 |
| 7 | 探针 `GET /api/defaults` | `200`，`Content-Type: application/json`，体 `{'db_path': '', 'namespace': ''}` —— 证实「返回 `dict` → 自动 JSON」的接口约定 |
| 8 | 基线测试实跑 `python3 -m pytest tests/test_dashboard_api.py -q` | `17 passed, 3 warnings in 0.94s`（warnings 为 langgraph/starlette 弃用告警；本仓无 `filterwarnings=error`，非致命） |
| 9 | `pyproject.toml:115–118` / `Makefile:106,111,113,124,129` / `pyproject.toml:153–168` | pytest `testpaths=["tests"]`；门禁 `make all = format lint typecheck test`；`ruff check/format src tests`、`mypy --strict src`；server 模块有 `disallow_untyped_decorators=false` 覆盖 |
| 10 | `pyproject.toml:97–113` sdist allowlist / `grep '"/tests'` | `tests/` **不在** sdist include 中 —— 新增测试文件**无需**改 allowlist |
| 11 | `pyproject.toml:77–79` / `cli/dashboard.py:80,125` | 控制台脚本 `octop-memory = ...cli:main`；dashboard 子命令导入 `app`（:80）→ `uvicorn.run(app, ...)`（:125） |

> 环境快照为当前事实；解释器/依赖由平台管理。探针中出现的 `LangChainPendingDeprecationWarning` 为依赖库告警，与本次改动无关，后续阶段按平台环境如实记录 skip/失败，不谎报通过。

---

## 三、方案总体

- **主改动**：`src/octop_memory/adapters/dashboard/server.py` Routes 段新增一条原生 `GET /welcome`，返回 `{"message": "welcome"}`。
- **测试**：新增 `tests/test_welcome.py` 契约测试（沿用 `importorskip` + `TestClient(app)` + `status_code`/`res.json()` 约定）。
- **不动**：`cli/dashboard.py` 启动逻辑、`bridge/`（stdio JSON-RPC，非 HTTP）、任何存储/召回/提升管线、公共 API、数据格式、配置默认值、`pyproject.toml` 依赖。
- **属性**：0 新增依赖；0 配置/数据契约变更；不涉及 SQL/schema/事务/FTS/生命周期 → SQLite/PostgreSQL 双后端门禁（`AGENTS.md:137–141`）**不适用**。

---

## 四、涉及文件（具体 + 行号 + 改动类型）

| 文件 | 行号 | 改动类型 | 说明 |
|------|------|----------|------|
| `src/octop_memory/adapters/dashboard/server.py` | `:243–245` Routes 段起点，建议插在 `index()`（`:248–254`）之后、`@app.get("/api/connect")`（`:257`）之前 | **新增** 1 个路由函数 | 唯一 HTTP Web 服务实例 `app`（`:39`）；既有「返回 dict 的 GET」范例 `get_defaults()`（`:668–677`）在风格与 mypy 兼容性上可直接参照 |
| `src/octop_memory/adapters/dashboard/server.py` | `:39–50` | 只读、不改 | `app` 定义、CORS 中间件（对 `/welcome` 同样生效）、`/static` 挂载（无冲突） |
| `src/octop_memory/adapters/dashboard/server.py` | `:710–712` | 只读、不改 | `create_app()` 返回同一 `app`，是「现有服务」的可导入承载点 |
| `src/octop_memory/adapters/cli/dashboard.py` | `:80,:125` | 只读、不改 | 启动链：导入 `app` → `uvicorn.run(app, host, port)`；路由注册在 import 期完成，无需改启动逻辑 |
| `tests/test_dashboard_api.py` | `:15,17,19,219–220,424–447` | 只读、不改 | 既有测试约定来源：`importorskip` 守卫、`TestClient(app)` 夹具、`status_code`+`res.json()` 断言；新测试沿用之 |
| `tests/test_welcome.py` | 新建 | **新增** 契约测试 | 独立文件，隔离、最小 diff；`testpaths=["tests"]` 自动发现，无需注册 |
| `pyproject.toml` | `:115–118, 153–168` | 只读、不改 | pytest 配置；`mypy strict` 对 server 模块的 `disallow_untyped_decorators=false` 覆盖（`:166–168`）保证带类型注解的路由函数兼容 |
| `Makefile` | `:106,111,113,124,129` | 只读、不改 | 门禁命令来源 |
| `AGENTS.md`（仓库级 + 工作区级） | `:63,118–119,130,137–141,158–167` | 只读约束 | 聚焦最小改动、不改公共 API/配置默认值/生产依赖、双后端门禁（本例不适用）、`make all` 门禁 |

---

## 五、原生 `/welcome` 路由设计

**落点**：`server.py` Routes 段，建议紧随 `index()`（`:254` 后）插入，作为顶层一等路由；装饰器在模块 import 期注册，置于 Routes 段内任一位置效果一致。

**实现（供 03 阶段照此落地）**：

```python
@app.get("/welcome")
def welcome() -> dict[str, str]:
    """Return a simple welcome message."""
    return {"message": "welcome"}
```

设计要点：
- **原生**：使用框架自带 `@app.get` 在既有 `app` 上注册；不新建服务、不引入新框架/依赖、不改 `uvicorn.run`/挂载方式、不手写 path 分派、不动 `create_app()`。
- **接口约定**：返回 `dict` → FastAPI 自动 `HTTP 200` + `Content-Type: application/json` + JSON 体（§二.7 实测 `/api/defaults` 验证该约定）；精确体 `{"message": "welcome"}`。
- **类型注解**：`-> dict[str, str]`，与 `get_defaults() -> dict[str, Any]`（`:669`）一致，兼容 `mypy --strict`；`disallow_untyped_decorators=false`（`pyproject.toml:166–168`）覆盖未注解的 `@app.get` 装饰器。
- **无副作用**：不访问 `app.state`、不读 DB、无参数/查询、无 `HTTPException`。
- 函数命名 `welcome`，全仓 `grep welcome` 无同名冲突（§二.3）。

---

## 六、接口契约与契约测试设计

**契约（任务 + 实测推定）**

| 项 | 约定 |
|----|------|
| 方法 / 路径 | `GET /welcome` |
| 状态码 | `200` |
| Content-Type | `application/json` |
| 响应体 | 精确 `{"message": "welcome"}`（字段 `message`，值 `welcome`） |
| 副作用 | 无；只读端点 |

**契约测试（新建 `tests/test_welcome.py`，供 03 阶段先写）**

```python
"""Contract tests for the native GET /welcome route."""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="dashboard extra not installed")

from fastapi.testclient import TestClient

from octop_memory.adapters.dashboard.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestWelcome:
    def test_welcome_returns_message(self, client: TestClient) -> None:
        res = client.get("/welcome")
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("application/json")
        assert res.json() == {"message": "welcome"}
        assert res.json()["message"] == "welcome"
```

设计要点：
- 沿用既有约定：`pytest.importorskip("fastapi")`（`test_dashboard_api.py:15`，dashboard 为可选 extra）、`from ...server import app`（`:19`）、`TestClient(app)` 夹具（`:219–220`）、`res.status_code` + `res.json()` 断言（`:424–447` `TestDefaults`）。
- **为何独立文件而非并入 `test_dashboard_api.py`**：该文件 447 行、以命名空间隔离为组织线索；新增独立契约测试 diff 最小、隔离性好、便于单独 `pytest tests/test_welcome.py -q` 运行，且不触碰既有用例。两者等价，03 阶段若选择并入现有文件亦符合约定。
- **TDD 顺序**：先提交测试 → 基线 `GET /welcome` 为 `404`（§二.6）→ 测试失败（红）→ 实现 §五 路由 → 测试通过（绿）。
- `ruff check/format src tests`（`Makefile:111,113`）覆盖 `tests/`；该文件需保持 ruff 干净（line-length 120）。测试文件不在 `mypy --strict src` 的 `files=["src/octop_memory"]` 范围内，不受 mypy 约束。
- `tests/` 不在 sdist allowlist（§二.10），新增文件无需改 `pyproject.toml`。

---

## 七、启动方案（本阶段不执行，供 03/04/05 阶段）

**启动链（无需改动）**：
`octop-memory dashboard`（`pyproject.toml:78` → `cli:main`；`cli/dashboard.py:29`）→ 导入 `app`（`:80`）→ `uvicorn.run(app, host=127.0.0.1, port)`（`:125`，默认自 7860 探测空闲端口）。路由在 `server.py` import 期由装饰器注册到同一 `app`，因此 CLI 启动、`create_app()`、`TestClient(app)` 三者天然覆盖该路由。

**验证方式**：
- **主验证（进程内，测试用例依赖）**：`TestClient(app).get("/welcome")` —— 与启动共用同一 `app` 实例，确定性强，§六 契约测试即采用此方式。
- **真实 HTTP 冒烟（可选，04/05 阶段；需环境装有 `uvicorn`/`[dashboard]` extra）**：
  ```bash
  uvicorn octop_memory.adapters.dashboard.server:app --host 127.0.0.1 --port 7860
  curl -i http://127.0.0.1:7860/welcome
  ```
  或经 CLI：`octop-memory dashboard --no-browser`，再 `curl` 其输出 URL 拼 `/welcome`。
- **约束**：dashboard 被 wheel 排除（`pyproject.toml:87–92`）、仅源码 checkout + `[dashboard]` extra 可用（README:142）；当前环境 `fastapi 0.115.0` 已具备（§二.2）。无新启动入口、无新端口/挂载配置。

---

## 八、验证命令（供 03 实现阶段 / 05 IT 阶段执行；本阶段不执行实现）

```bash
# 1) 针对性契约测试（先红后绿）
python3 -m pytest tests/test_welcome.py -q

# 2) 回归既有 dashboard 用例（基线 17 passed，§二.8）
python3 -m pytest tests/test_dashboard_api.py -q

# 3) 变更文件静态检查（mypy 仅 src；ruff 覆盖 src+tests）
python3 -m mypy --strict src/octop_memory/adapters/dashboard/server.py
python3 -m ruff check src tests && python3 -m ruff format --check src tests

# 4) 全量质量门禁（AGENTS.md:158–167 / Makefile:106）
make install-hooks   # 每个 clone 仅一次，绝不绕过失败门禁
make all             # format + lint + typecheck + pytest

# 5) 文档/架构边界检查（路由改动不改变公共 API/数据契约，预期仍通过）
python3 -m pytest tests/test_agent_docs.py tests/test_architecture_boundaries.py -q
```

环境注意：当前 `python3 = 3.11.6` 低于 `requires-python >=3.12`；`ruff target py312`、`mypy python_version=3.12` 对解释器敏感。针对性 pytest 在 3.11 下实跑通过（§二.8）；`make all` 以平台环境为准，若因环境导致 skip/失败，如实记录复现命令，不谎报通过（`AGENTS.md:171`）。`PYTHONPATH` 已含仓库根/`src`/site-packages，勿覆盖（覆盖会丢失 fastapi）。

---

## 九、回滚方案

- **改动性质**：纯增量、隔离 —— 仅 `server.py` 新增一个函数块 + `tests/test_welcome.py` 一个新文件；不触及 `app.state`、CORS、`/static` 挂载、CLI、bridge、存储/管线，无 schema/迁移/数据/配置写入。
- **回滚操作**（任一即可，由平台按收尾方式裁定）：
  1. 平台已提交时：`git revert <该阶段 commit>`；或
  2. 未提交/源码层：删除 `server.py` 中 `@app.get("/welcome")` 的 `welcome()` 函数块，并删除 `tests/test_welcome.py`。
- **回滚后行为**：`GET /welcome` 恢复为基线 `404 {"detail":"Not Found"}`（§二.6 已实测），既有 `test_dashboard_api.py` 的 17 个用例与 `make all` 不受影响 —— 因本次未修改任何既有代码/配置/依赖/数据契约。
- **数据/下游风险**：0。无持久化状态、无公共接口结果变更、无配置默认值变更，无 Harness/Octop 等上层消费者需要联动（对照 `AGENTS.md` 仓库协作表，本改动属「源码 checkout 专属的 dashboard 轻量新增」，非公共 API/数据契约变更）。

---

## 十、验收条件（明确、可判定）

| # | 条件 | 判定方式 |
|---|------|----------|
| 1 | `GET /welcome` 返回 `HTTP 200` | §六 契约测试 `res.status_code == 200` |
| 2 | 响应体 JSON，精确 `{"message": "welcome"}` | `res.json() == {"message": "welcome"}` 且 `["message"] == "welcome"` |
| 3 | `Content-Type: application/json` | `res.headers["content-type"].startswith("application/json")` |
| 4 | 路由**原生**（既有 `app` 上 `@app.get`，无新框架/依赖/入口/挂载改动） | 代码审查 §五；`create_app() is app` 复用（§二.5）；`pyproject.toml` 依赖 diff 为空 |
| 5 | `tests/` 有自动化测试覆盖，沿用 `TestClient(app)`+`importorskip` | §六 `tests/test_welcome.py` 存在并通过 |
| 6 | 不破坏既有行为：`test_dashboard_api.py` 全绿、`make all` 通过（或至少针对性用例 + 变更文件 lint/mypy 通过） | §八 命令 2/3/4 |
| 7 | 验证环境装有 `fastapi`（`[dashboard]` extra），否则 `importorskip` 会跳过 | §二.2 `fastapi 0.115.0` 已具备 |

---

## 十一、风险 / 边界 / 非目标

1. **`app.py` 字面缺失**：任务「优先阅读 app.py」映射为 `adapters/dashboard/server.py` 的 `app` 实例与路由表（Clarify §一.3 已裁决）；`bridge/server.py` 为 stdio JSON-RPC，排除。
2. **`[dashboard]` 可选 extra + wheel 排除**（`pyproject.toml:49–53,87–92`）：路由仅在源码 checkout + 装 fastapi 的环境可见/可测；未装时 `importorskip` 跳过而非失败。当前环境已具备。
3. **解释器版本 3.11.6 < 3.12**：针对性测试实跑通过，`make all` 的 mypy/ruff 以平台环境为准（§八）。
4. **路由计数**：本阶段实测 `len(app.routes)=19`（含 1 个 `/static` Mount 与 docs 默认路由），15 个 GET 路径 —— 与 Clarify 的「18 条」为计数口径差异，不影响方案。
5. **sdist allowlist**：`tests/` 不在 include 中（§二.10），新增测试文件无需改 allowlist，也无需改导航/链接锚点。
6. **文档**：本变更为轻量增量、不改公共 API/数据契约/配置默认值；按 `AGENTS.md` 工程文档工作流，预计无需 ADR/HANDOFF 大改。若 03 阶段决定将 `/welcome` 作为可文档化对外行为，再在 README/CHANGELOG 追加简短说明（非功能验收必需）。
7. **严格阶段边界（本阶段）**：仅写本 `02-plan.md`；**未改源码、未新增 `/welcome` 路由、未创建测试文件、未运行实现性改动、未执行 Git 提交**。§二 探针与基线测试均为只读核对，用于产出「执行证据 / 实际测试结果」。

---

## 十二、验收结论 / 阶段边界

**Plan 阶段已完成，方案可实施、无阻塞。** 原生路由设计（§五）、接口契约与契约测试（§六）、启动链（§七）、验证命令（§八）、回滚方案（§九）、涉及文件（§四）与验收条件（§十）均已明确并落到具体文件/行号/命令；关键结论经本阶段实地探针与基线测试复核（§二）。

- 改动聚焦为「1 源文件函数 + 1 测试文件」，零新增依赖、零配置/API/数据契约变更，不触发双后端门禁与文档/架构边界风险。
- 03 阶段可直接按 §六「先写失败用例（基线 404）→ 实现 §五 路由 → 跑 §八 门禁」落地；若 03/04/05 阶段出现阻塞，按 §十一 风险如实记录并停止，由平台记录失败。
- 本阶段唯一产物即本文件；Git 提交由平台收尾。
