# 03 · Implement + UT + Docs（实现 + 单测 + 文档）

> **阶段任务**：在现有 Web 服务内增加原生 `GET /welcome` 路由，返回 JSON `message=welcome`；更新 README 接口说明；编写并**实际运行**契约测试；产出 `runtime.json` 供平台后续验证；仅执行本阶段（不改启动逻辑、不部署、不提交）。
> **任务目标（用户授权）**：在当前仓库「现有 Web 服务」中增加**原生** `GET /welcome` HTTP 路由，返回 JSON `message=welcome`。
> **分支 / 工作区**：`feature/wally-experience-ca7bb0b6`（平台创建，仓库独立副本；Git 提交由平台收尾）。`git branch --show-current` 实测为该分支。
> **前序产物**：[00-overview.md](./00-overview.md)、[01-clarify.md](./01-clarify.md)、[02-plan.md](./02-plan.md)。本阶段沿用 Clarify 的框架/路由/接口/测试结论与 Plan 的落地方案（§五 路由、§六 契约测试、§八 验证命令）。
> **阶段边界**：只改源码 / 测试 / README / runtime.json / 本阶段文档；部署（04）、IT（05）、评审提交（06）由平台推进。

---

## 一、验收结论（先行）

**Implement 阶段已完成，功能验收条件全部满足，无阻塞。**

- 在既有 FastAPI dashboard（`src/octop_memory/adapters/dashboard/server.py` 的 `app`）上以框架自带 `@app.get("/welcome")` 注册了一等路由，返回 `{"message": "welcome"}` —— 零新增运行依赖、零启动入口 / 挂载 / 配置 / 公共 API / 数据契约改动。
- **TDD 实跑**：先写契约测试 → 基线红（`404 != 200`）→ 实现 → 绿。最终 `python3 -m pytest tests/test_welcome.py tests/test_dashboard_api.py -q` = **18 passed**（17 既有回归 + 1 新增契约）。
- **真实 HTTP 冒烟**：按 `runtime.json` 的 `serve` 命令起进程，`GET /welcome` → `200 | application/json | {"message":"welcome"}`，既有 `/api/defaults` 仍 `200`。
- `runtime.json` 已按格式 `{"test": [...], "serve": [...]}` 产出，`serve` 通过 `{port}` 接收临时端口。
- README（EN/CN 双语、对齐）已补充「Dashboard HTTP 接口」小节记录 `/welcome`。
- 变更相关静态检查全绿：`ruff check src tests`、`ruff format --check src tests`、以及**隔离的 `mypy --strict`**（真实 override，1 file，Success）。
- 唯一未绿项：仓库全量门禁 `make all` 的 `typecheck` 与 2 个架构边界用例，因**运行环境 Python 3.11.6 < 项目要求 3.12**、无法解析仓库**既有**的 PEP 695 语法文件而失败。经核实为前序/环境限制，与本变更无关（§六、§八，已给出复现命令与隔离验证）。

---

## 二、实际分析（聚焦启动入口 / 路由 / 测试约定）

| 核对项 | 结论（与 01/02 一致，本阶段实读复核） |
|--------|--------------------------------------|
| 仓库 / 框架 | `octop-memory` v1.0.5；核心依赖为空，Web 框架为 **FastAPI**（可选 `[dashboard]` extra，`pyproject.toml:49-53`）。当前环境 `fastapi 0.115.0`、`uvicorn 0.54.0`、`pytest 8.2.2`、`httpx 0.28.1` 已具备。 |
| 「现有 Web 服务」 | `app = FastAPI(title="octop-memory Dashboard", version="1.0.0")`（`server.py:39`），路由用 `@app.get / @app.patch / @app.delete` 原生注册（`server.py` Routes 段）。**无需新建服务**。 |
| `app.py` 字面 | 仓库无 `app.py`；等价物为 `adapters/dashboard/server.py` 的 `app` 实例与路由表（Clarify §一.3 已裁决）。`bridge/server.py` 为 stdio JSON-RPC，非 HTTP，排除。 |
| 启动入口 | `octop-memory dashboard`（`pyproject.toml:78`）→ `cli/dashboard.py:80` 导入 `app` → `:125` `uvicorn.run(app, host, port)`。`create_app()`（`server.py:712`）与测试复用同一 `app`（本阶段实测 `create_app() is app → True`）。路由在 import 期注册，启动链 / 测试链天然覆盖。 |
| 路由落点 | `server.py` Routes 段，紧随 `index()`（`:248-254`）之后、`@app.get("/api/connect")` 之前。既有「返回 dict 的 GET」范例 `get_defaults() -> dict[str, Any]`（`:668-677`，本阶段后移至 `:674`）风格可直接参照。 |
| 接口约定 | 返回 `dict` → FastAPI 自动 `HTTP 200` + `application/json` + JSON 体（实测）。故 `{"message": "welcome"}`。 |
| 「原生」释义 | 用既有框架自带装饰器在该 `app` 上注册一等路由；不引入新框架/依赖、不改挂载、不手写 path 分派、不另起 stdlib `http.server`。 |
| 测试约定 | `pytest.importorskip("fastapi")` 守卫 + `from octop_memory.adapters.dashboard.server import app` + `TestClient(app)` 夹具 + `res.status_code`/`res.json()` 断言（`tests/test_dashboard_api.py:15,17,19,219-220,424-447`）。pytest 配置 `pyproject.toml:115-118`，`testpaths=["tests"]`、`pythonpath=["src", "plugins/hermes"]`。 |
| 双后端门禁 | 本路由为纯只读、无 SQL/schema/事务/FTS/生命周期 → SQLite/PostgreSQL 双后端门禁（AGENTS.md:137-141）**不适用**；不改公共 API/配置默认值/生产依赖（AGENTS.md:130）。 |

---

## 三、涉及文件（改动清单）

| 文件 | 改动 | 说明 |
|------|------|------|
| `src/octop_memory/adapters/dashboard/server.py` | **修改**：Routes 段新增 1 个函数（`:257-260`，见 §四） | 唯一 HTTP Web 服务实例 `app`（`:39`）；既有用例、CORS（`:41-46`）、`/static` 挂载（`:48-50`）、`create_app()`（`:710-712`）均只读不改 |
| `tests/test_welcome.py` | **新增**：契约测试（独立文件，ruff 已格式化） | 沿用 `importorskip` + `TestClient(app)` + `status_code`/`res.json()` 约定；`testpaths` 自动发现，无需改 `pyproject.toml` / sdist allowlist（tests 不在其中） |
| `README.md` | **修改**：在 `:142` dashboard 说明后新增「Dashboard HTTP endpoints」小节 | 记录 `/welcome` 及既有 `/`、`/api/*` 接口，说明启动方式与只读语义 |
| `README_CN.md` | **修改**：在 `:140` 对应位置新增「Dashboard HTTP 接口」小节 | 与 EN 版技术契约、命令、示例对齐（AGENTS.md 文档语言要求） |
| `.wally/.../runtime.json` | **新增**：平台验证入口 | 见 §六 |
| `.wally/.../03-implement.md` | **新增**：本阶段文档 | 本文件 |
| `pyproject.toml` / `Makefile` / `cli/dashboard.py` / `bridge/` / 存储 / 管线 | **未改动** | `git diff -- pyproject.toml` 为空 → 零新增依赖；无启动/挂载/配置/API 改动 |

> 交付核对（`git diff --name-only`）：`README.md`、`README_CN.md`、`src/octop_memory/adapters/dashboard/server.py`；未跟踪新文件 `tests/test_welcome.py`。`.wally/` 为阶段产物目录。

---

## 四、实现（原生路由）

落点 `src/octop_memory/adapters/dashboard/server.py`，紧随 `index()` 之后：

```python
@app.get("/welcome")
def welcome() -> dict[str, str]:
    """Return a simple welcome message."""
    return {"message": "welcome"}
```

设计要点：
- **原生**：框架自带 `@app.get` 注册在既有 `app`；本阶段实测 `create_app() is app → True`、`app.routes` 中 `/welcome` 为 `APIRoute(methods={'GET'}, endpoint=welcome, return=dict[str, str])`，`APIRoute` 总数由 14 → 15（+1，即本路由）。
- **接口**：返回 `dict` → 自动 `200` + `application/json`，精确体 `{"message": "welcome"}`。
- **类型**：`-> dict[str, str]` 兼容 `mypy --strict`；本模块有 `disallow_untyped_decorators=false` 覆盖（`pyproject.toml:166-168`），隔离 strict 检查通过（§五.6）。
- **无副作用**：不访问 `app.state`、不读 DB、无参数、无 `HTTPException`。

---

## 五、执行证据（真实命令 + 结果）

环境快照：`python3 = 3.11.6`（Python 3.12 语法在此运行环境无法解析，见 §八）；`PYTHONPATH` 由平台注入（含仓库根、`src`、site-packages），未覆盖。

| # | 命令 | 结果 |
|---|------|------|
| 1 | `python3 -m pytest tests/test_welcome.py -q`（**先写测试，TDD 红**） | `1 failed`：`assert 404 == 200` —— 基线 `/welcome` 缺失，红态证据 |
| 2 | 在 `server.py` 新增 `@app.get("/welcome")`（§四） | 实现完成 |
| 3 | `python3 -m pytest tests/test_welcome.py tests/test_dashboard_api.py -q`（**= runtime.json 的 `test` 命令**） | **18 passed, 3 warnings in 0.99s**（17 既有 `test_dashboard_api.py` 回归 + 1 新增契约）；最终复跑仍 `18 passed` |
| 4 | `python3 -m ruff check src tests` | `All checks passed!` |
| 5 | `python3 -m ruff format --check src tests` | `205 files already formatted`（新增测试文件已按 ruff 0.15.9 格式化：docstring 后补空行） |
| 6 | `python3 -m mypy --config-file /tmp/mypy_welcome.ini src/octop_memory/adapters/dashboard/server.py`（隔离 strict，沿用真实 `disallow_untyped_decorators=false` override，skip imports 以绕开 3.11 解析限制） | **`Success: no issues found in 1 source file`** —— 含新增 `welcome()` 的严格类型检查通过 |
| 7 | `python3 -m pytest tests/test_agent_docs.py tests/test_architecture_boundaries.py -q` | `54 passed, 2 failed`；2 个失败均为 `SyntaxError`（3.11 `ast.parse` 无法解析既有 PEP 695 文件 `checkpoint_retention.py:11` 等）—— 前序/环境限制，见 §八 |
| 8 | **真实 HTTP 冒烟**：按 `serve` 命令起 `uvicorn ...:app --host 127.0.0.1 --port 17861`，`urllib` 请求 | `GET /welcome -> 200 \| application/json \| {"message":"welcome"}`；断言 `status==200`、`content-type` 前缀、`body=={"message":"welcome"}`、`["message"]=="welcome"` 全 PASS；`GET /api/defaults -> 200 {"db_path":"","namespace":""}`（既有行为未破坏）；服务 `terminate` 退出码 `-15` |
| 9 | `make all`（全量门禁） | `format`：`205 files left unchanged`；`lint`：`All checks passed!` + `205 files already formatted`；`typecheck`：`mypy --strict src` → `pipeline/recall/timeout.py:53: error: Expected '('  [syntax]`，`Error 2` 中止（未执行到 `test`）—— 见 §八 |
| 10 | `git diff --name-only` / `git diff -- pyproject.toml` / 路由探针 / `runtime.json` 校验 | 仅 §三 列出的文件被改；`pyproject.toml` 无 diff（零新增依赖）；`create_app() is app` = True；`/welcome` 为原生 GET 路由；`runtime.json` 合法且 `serve` 含 `{port}` |

> 命令 3 即 `runtime.json` 的 `test` 命令，命令 8 使用 `runtime.json` 的 `serve` 命令（将 `{port}` 替换为临时端口 17861）。二者均**实际执行并通过**。

---

## 六、runtime.json（平台验证入口）

写入 `.wally/experiences/ca7bb0b6-df02-443b-8569-31fd6063972f/runtime.json`：

```json
{
  "test": ["python3", "-m", "pytest", "tests/test_welcome.py", "tests/test_dashboard_api.py", "-q"],
  "serve": ["python3", "-m", "uvicorn", "octop_memory.adapters.dashboard.server:app", "--host", "127.0.0.1", "--port", "{port}"]
}
```

- 格式符合 `{"test": ["命令", "参数"...], "serve": ["命令", "参数"...]}`；`test` 覆盖新增契约用例 + 既有 dashboard 回归，`serve` 通过 `{port}` 接收临时端口。
- `serve` 选 `python3 -m uvicorn ...:app`（而非 `octop-memory dashboard`）：显式 `--port {port}` 便于平台注入端口，且直接复用既有 `app` 实例（Plan §七 已推荐此真实 HTTP 冒烟方式）。已实测 `python3 -m uvicorn --version` 可用并以命令 8 验证起服与响应。
- 运行前提：需 `[dashboard]` extra（fastapi/uvicorn）+ `PYTHONPATH` 含 `src`；当前平台环境已满足。

---

## 七、验收条件对照（Plan §十 / 任务）

| # | 条件 | 证据 | 结果 |
|---|------|------|------|
| 1 | `GET /welcome` 返回 `HTTP 200` | 命令 3 契约断言 `status_code==200`；命令 8 真实 HTTP `200` | ✅ |
| 2 | 响应体 JSON 精确 `{"message": "welcome"}` | 命令 3 `res.json()=={"message":"welcome"}`；命令 8 实测体一致 | ✅ |
| 3 | `Content-Type: application/json` | 命令 3 `res.headers["content-type"]` 前缀；命令 8 实测 | ✅ |
| 4 | 路由**原生**（既有 `app` 上 `@app.get`，无新框架/依赖/入口/挂载改动） | §四；命令 10 `create_app() is app`、APIRoute(GET)；`git diff -- pyproject.toml` 为空 | ✅ |
| 5 | `tests/` 有自动化测试，沿用 `TestClient(app)` + `importorskip` | `tests/test_welcome.py`；命令 1 红 / 命令 3 绿 | ✅ |
| 6 | 不破坏既有行为：既有 dashboard 用例全绿、门禁（或针对性用例 + 变更文件 lint/mypy）通过 | 命令 3 `18 passed`（含 17 回归）；命令 4/5 ruff 全绿；命令 6 隔离 strict mypy Success；命令 8 真实 HTTP `/api/defaults` 仍 200。`make all` 的 typecheck 因环境受阻（§八） | ✅（相关检查）/ ⚠️ 全量门禁见 §八 |
| 7 | 验证环境装有 `fastapi` | 环境探针 `fastapi 0.115.0` | ✅ |
| 8 | README 接口说明更新 | §三 README.md / README_CN.md 双语文案 | ✅ |
| 9 | 产出 `runtime.json` 供平台验证 | §六、命令 10 校验 | ✅ |

---

## 八、环境限制 / 风险（如实记录，非本变更引入，不阻塞本阶段）

1. **`make all` 的 `typecheck` 失败**：`mypy --strict src` → `src/octop_memory/pipeline/recall/timeout.py:53: error: Expected '('  [syntax]`。该文件 `:53` 为 `def with_deadline[T](`（PEP 695 泛型函数，Python 3.12+ 语法），**前序已存在于 HEAD、本阶段未修改**（`git diff -- timeout.py` 为空，`git cat-file` 证实）。根因：运行解释器 `3.11.6` 低于 `requires-python >=3.12`（`pyproject.toml:11`），mypy 在 3.11 runtime 下无法解析 3.12 语法。Plan §七.3 / §十一.3 / §八 已预判此风险。复现：`python3 -m mypy --strict src`（结果同上）、`python3 -m mypy --strict src/octop_memory/adapters/dashboard/server.py`（报 `postgres_checkpoint_retention.py:42` 的 `type _Cursor = ...`）。**证明与本变更无关**：命令 6 用真实 override 对 `server.py` 单独做隔离 strict 检查 → `Success`；且全仓 `ruff check/format` 全绿。`format`/`lint` 两步均已通过。
2. **2 个架构边界用例失败**：`test_engine_layers_do_not_import_adapters`、`test_storage_does_not_import_pipeline` 报 `SyntaxError`。`tests/test_architecture_boundaries.py:13` 用 `ast.parse` 解析 `src/octop_memory/**/*.py`（`:24` rglob），3.11 的 `ast` 无法解析仓库既有 4 处 PEP 695 `type X =` 别名（`checkpoint_retention.py:11`、`postgres_checkpoint_retention.py:42`、`postgres_pool.py:27-28`）。这些文件均前序存在、未修改；本阶段新增文件在 `tests/` 与 `server.py`（无 `type` 别名），不在解析失败集合内。结果 `54 passed, 2 failed`，失败为环境/前序限制。在 Python 3.12 环境下该门禁预期恢复。
3. **解释器版本**：`python3 3.11.6 < 3.12`。针对性 pytest 在 3.11 下实跑通过（fastapi/httpx 均兼容），契约逻辑与 py3.12 语法无关。运行环境由平台管理；若平台以 3.12 执行 `make all`，typecheck 与 2 个架构用例应通过。本阶段不谎报全量门禁通过。
4. **dashboard 可选 extra + wheel 排除**（`pyproject.toml:49-53,87-92`）：路由仅在「源码 checkout + 装 fastapi」环境可见/可测；当前环境已具备。未装时 `importorskip` 跳过而非失败。
5. **warnings**：契约/回归测试的 3 条 warning 为 `asyncio_mode` 未知配置、`starlette`、`langgraph` 弃用告警，非致命（本仓无 `filterwarnings=error`），与基线一致。

> 依据 AGENTS.md：环境与既有问题阻碍验证时，如实记录失败/skip 与复现命令，不冒充通过。上述均为前序/环境限制，本变更相关验证（命令 1/3/4/5/6/8/10）全部通过。

---

## 九、阶段边界 / 交付

- **本阶段已做**：新增原生 `GET /welcome` 路由；新增并通过契约测试 `tests/test_welcome.py`；更新 README.md / README_CN.md 接口说明；产出 `runtime.json`；实跑 TDD 红→绿、回归、ruff、隔离 strict mypy、真实 HTTP 冒烟、文档/架构边界用例、全量 `make all`（如实记录 typecheck 环境失败）；写本阶段文档。
- **本阶段未做（由平台后续阶段推进）**：部署（04）、集成测试 IT（05）、评审与 Git 提交（06）。未改 `cli/dashboard.py` 启动逻辑、`bridge/`、存储/管线、公共 API/数据契约/配置默认值/生产依赖；未新增任何运行依赖；未执行任何 Git 提交或历史改写。
- **回滚**（若需）：删除 `server.py` 中 `@app.get("/welcome")` 的 `welcome()` 函数块、删除 `tests/test_welcome.py`、回退 README 两处小节、`runtime.json`；`GET /welcome` 恢复为基线 `404`（命令 1 已证实），既有 17 用例与其余文件不受影响（Plan §九）。
- **交付物清单**：`src/octop_memory/adapters/dashboard/server.py`、`tests/test_welcome.py`、`README.md`、`README_CN.md`、`.wally/experiences/.../runtime.json`、`.wally/experiences/.../03-implement.md`。

**结论：03 Implement + UT + Docs 阶段验收通过（无阻塞），可交平台推进后续阶段。**
