# 01 · Clarify（需求澄清）

> **阶段任务**：核对现有 Web 框架、启动入口、路由位置、接口约定与测试约定，明确改动范围与验收条件；仅产出澄清文档，不改动源码、不新增路由、不提交。
> **任务目标（用户授权）**：在当前仓库「现有 Web 服务」中增加**原生** `GET /welcome` HTTP 路由，返回 JSON `message=welcome`。
> **分支 / 工作区**：`feature/wally-experience-ca7bb0b6`（平台创建，仓库独立副本；Git 提交由平台收尾）。`baseline-sha = 396e9c9`，工作树干净。
> **前序产物**：本阶段开始时 `.wally/experiences/ca7bb0b6-df02-443b-8569-31fd6063972f/` 为空目录；父目录 `*.log` 仅含 git SHA 与分支切换记录，未见预置的前序阶段文档或测试结果文件。故本阶段结论与「实际测试结果」均来自本次实地核对（含基线测试实跑，见 §二）。

---

## 一、结论（先行）

1. **仓库身份**：当前仓库是 `octop-memory` v1.0.5（`pyproject.toml:6,7`），`requires-python >=3.12`（`pyproject.toml:11`），核心运行依赖为空（`pyproject.toml:24`）。它是一个可复用记忆**库**，但源码内确实带有一个「本地可视化 dashboard」Web 服务。
2. **「现有 Web 服务」前提成立**：仓库内存在基于 **FastAPI** 的 HTTP 服务 —— `app = FastAPI(title="octop-memory Dashboard", version="1.0.0")`（`src/octop_memory/adapters/dashboard/server.py:39`），路由以原生装饰器 `@app.get / @app.patch / @app.delete` 注册（`server.py:248–701`），启动入口是 `octop-memory dashboard` CLI → `uvicorn.run(app, ...)`（`src/octop_memory/adapters/cli/dashboard.py:29,80,125`）。与「库内无 Web 服务」的其它体验不同，**本任务无需新建服务，只需在既有 FastAPI app 上扩展一条路由**。
3. **`app.py` 字面文件不存在**：`git ls-files` 中仅有 `adapters/bridge/server.py` 与 `adapters/dashboard/server.py` 两个 `server.py`，无 `app.py / wsgi.py / asgi.py / routes.py`。任务中的「优先阅读 app.py」应映射到 `adapters/dashboard/server.py` 内的 `app` 实例与路由表；`bridge/server.py` 是 **stdio JSON-RPC**（`bridge/server.py:1,144`），非 HTTP，不在本次范围。
4. **接口约定已实测确认**：路由返回 Python `dict` 即得到 `HTTP 200` + `Content-Type: application/json` + JSON 体（实测 `GET /api/defaults` → `200`，`application/json`，`{"db_path":"","namespace":""}`）。故 `/welcome` 可返回 `{"message": "welcome"}`。全仓 `src/`、`tests/` 中 `grep -rn welcome` 为空，`GET /welcome` 基线为 `404 {"detail":"Not Found"}` —— 路由当前缺失。
5. **「原生」释义（据现状裁决）**：目标是「现有 FastAPI 服务」，因此「原生路由」= 用该框架自带装饰器在该 `app` 上注册一等路由（`@app.get("/welcome")`），不引入新框架/新运行依赖、不改挂载方式、不用手写 path 分派或 stdlib `http.server` 另起服务。
6. **验收条件明确且可判定**，无阻塞；澄清阶段只核对、不实施（§八）。

---

## 二、执行证据（本阶段实跑 / 实读）

| # | 动作 | 结果 |
|---|------|------|
| 1 | `git status --short` / `git branch --show-current` / `cat baseline-sha` | 分支 `feature/wally-experience-ca7bb0b6`，工作树干净，基线 `396e9c9`（`Merge pull request #51 ... release/1.0.5`） |
| 2 | `git ls-files \| grep -iE "(^\|/)(app\|wsgi\|asgi\|routes?\|server\|main)\.py$"` | 仅 `src/octop_memory/adapters/bridge/server.py`、`src/octop_memory/adapters/dashboard/server.py`；**无 `app.py`** |
| 3 | 全仓 `Grep Flask\|FastAPI\|uvicorn\|@app.get\|BaseHTTPRequestHandler\|APIRouter...` | 命中集中在 `adapters/dashboard/server.py`、`adapters/cli/dashboard.py`、`tests/test_dashboard_api.py`、`pyproject.toml`、`uv.lock`；确认 Web 框架为 FastAPI（可选 extra） |
| 4 | `grep -rn -i welcome src tests` | 无命中（无既有 `/welcome` 或同名逻辑） |
| 5 | 读 `server.py`（全 712 行）、`cli/dashboard.py`、`bridge/server.py`、`test_dashboard_api.py`、`pyproject.toml`、`Makefile`、README/README_CN 相关段、AGENTS.md | 见 §三、§四 |
| 6 | **实时探针**（`fastapi.testclient.TestClient(app)`，平台 `PYTHONPATH` 已含 `src`+site-packages） | `app` 类型 `fastapi.applications.FastAPI`，title `octop-memory Dashboard` v`1.0.0`；列出 18 条路由（含 `/`、`/api/*`、`/static`、docs 等），**无 `/welcome`** |
| 7 | 同上探针：`GET /welcome` | `404`，体 `{"detail":"Not Found"}` —— 基线缺失 |
| 8 | 同上探针：`GET /api/defaults` | `200`，`Content-Type: application/json`，体 `{'db_path': '', 'namespace': ''}` —— JSON 约定实测 |
| 9 | **基线测试实跑**：`python3 -m pytest tests/test_dashboard_api.py -q` | `17 passed, 3 warnings in 1.01s`（warnings 为 pytest/starlette/langgraph 弃用告警，非致命；本仓无 `filterwarnings=error`） |
| 10 | 运行环境探针 | `python3` = `3.11.6`（低于 `>=3.12`）；无 `uv`、无 `.venv`；已装 `fastapi 0.115.0 / pytest 8.2.2 / httpx 0.28.1`。平台 `PYTHONPATH` 已含仓库根、`src` 与 site-packages，**勿覆盖**（覆盖会丢失 fastapi） |

> 环境快照为当前事实记录；解释器/依赖由平台管理，后续阶段以平台配置为准。

---

## 三、关键文件清单（含行号）

| 文件 | 角色 / 本阶段结论 |
|------|-------------------|
| `src/octop_memory/adapters/dashboard/server.py:39` | `app = FastAPI(...)` —— **唯一 HTTP Web 服务实例**，路由落点 |
| `server.py:41–46` | CORS 中间件（`allow_origins/methods/headers=["*"]`），对 `/welcome` 同样生效 |
| `server.py:48–50` | `/static` 静态挂载（与新增路由无冲突） |
| `server.py:243–701` | **Routes 段**：`@app.get("/")`、`/api/connect`、`/api/stats`、`/api/*`、`/api/defaults`、`/api/namespaces` 及写接口；新增 `/welcome` 应放此处 |
| `server.py:257–290 / :669–677` | 返回 `dict[str, Any]` 的既有 GET 路由范例（FastAPI 自动 JSON 序列化） |
| `server.py:710–712` | `create_app() -> FastAPI` 工厂，返回同一 `app`；「现有服务」的可导入承载点 |
| `src/octop_memory/adapters/cli/dashboard.py:29,80,125` | 启动入口：`octop-memory dashboard` → 导入 `app` → `uvicorn.run(app, host=127.0.0.1, port)` |
| `src/octop_memory/adapters/bridge/server.py:1,144` | stdio JSON-RPC 桥（**非 HTTP**），排除出范围 |
| `tests/test_dashboard_api.py:15,17,19` | 既有测试约定：`pytest.importorskip("fastapi")` + `fastapi.testclient.TestClient` + `from ...server import app` |
| `tests/test_dashboard_api.py:219–220` | `client` 夹具 = `TestClient(app)` |
| `tests/test_dashboard_api.py:424–447` | `TestDefaults` —— 既有 `res.status_code == 200` + `res.json()` 断言风格 |
| `pyproject.toml:6,7,11,24` | 项目身份 / `>=3.12` / 核心依赖为空 |
| `pyproject.toml:49–53` | `[dashboard]` 可选 extra = `click / fastapi>=0.110 / uvicorn[standard]>=0.29` —— **fastapi 非核心依赖** |
| `pyproject.toml:77–79` | 控制台脚本（无独立 web server 脚本） |
| `pyproject.toml:87–92` | wheel **排除** `adapters/dashboard/` 与 `cli/dashboard.py` —— dashboard 为源码 checkout 专属 |
| `pyproject.toml:115–118` | `[tool.pytest.ini_options]`：`testpaths=["tests"]`、`pythonpath=["src","plugins/hermes"]`、`asyncio_mode="auto"` |
| `pyproject.toml:153–168` | mypy `--strict`，含 `octop_memory.adapters.dashboard.server` 的 `disallow_untyped_decorators=false` 覆盖 —— 新增带类型注解的路由函数兼容 |
| `Makefile:106,127–129` | `all: format lint typecheck test`（ship bar）/ `test: pytest --cov=octop_memory --cov-report=term-missing` |
| `README.md:142` / `README_CN.md:140` | dashboard 仅源码 checkout + `[dashboard]` 依赖可用，模块未进 wheel |
| `AGENTS.md:21,38` | `adapters/` 为 CLI/JSON-RPC/源码 dashboard；HTTP/CLI 等归上层产品 |
| `AGENTS.md:63,130` | 改动聚焦、最小验证；「不擅自改公共 API / 数据格式 / 配置默认值 / 生产依赖」 |
| `AGENTS.md:118–119` | 架构约束；「source dashboard 的直接 SQLite 访问是既有例外，不是新 adapter 模板」 |
| `AGENTS.md:137–141` | SQLite/PostgreSQL 双后端门禁（schema/SQL/事务/生命周期变更时）—— **本路由不触及** |
| `AGENTS.md:158–167` | `make install-hooks` / `make all` 为验证门禁；文档检查用 `test_agent_docs.py` / `test_architecture_boundaries.py` |

> 另：工作区级 `/data/workspace/wally-open/AGENTS.md` 同样适用 —— 可执行验证放在 `tests/`、修改后运行相关测试、不把测试日志/本机会话记录作为源码提交、新增运行依赖先说明理由、不硬编码内部平台地址、SQL 参数化。

---

## 四、框架 / 启动入口 / 路由位置 / 接口约定核对

- **框架**：FastAPI（可选 `[dashboard]` extra，`pyproject.toml:49–53`）；`adapters/dashboard/server.py` 顶部 `try: from fastapi import ...` 缺失时抛 `ImportError` 提示安装 extra（`server.py:20–28`）。仓库核心依赖为空，**新增 `/welcome` 不需要也不应新增任何运行依赖**。
- **启动入口**：`octop-memory dashboard`（`cli/dashboard.py:29`）→ 导入 `app`（`:80`）→ `uvicorn.run(app, host=127.0.0.1, port=…)`（`:125`，默认 7860 起探测空闲端口）。`create_app()`（`server.py:710`）与测试均复用同一 `app` 实例 —— 在该 `app` 上注册路由即可被 CLI 启动与 `TestClient` 同时覆盖。
- **路由位置**：`server.py` 的 Routes 段（`:243–701`），以 `@app.get` 等装饰器原生注册。既有 `GET` 路由均返回 `dict`/`FileResponse`；无 `/welcome`，无同名常量。
- **接口约定（据任务 + 实测）**：
  - 方法 `GET`，路径 `/welcome`；
  - 成功 `HTTP 200`，`Content-Type: application/json`（由「返回 dict」自动获得，实测 §二.8）；
  - 体精确为 `{"message": "welcome"}`（字段 `message`，值 `welcome`）；
  - 「原生」= 既有 FastAPI `app` 上的一等路由 `@app.get("/welcome")`，不新建服务、不引入框架、不改挂载、不手写分派。
  - 实现形态建议：`@app.get("/welcome")` → `def welcome() -> dict[str, str]: return {"message": "welcome"}`（与 `:669` `get_defaults` 风格一致，带类型注解以兼容 strict mypy）。

---

## 五、测试约定与验收条件

**测试约定（来自仓库，后续实现/验证阶段须遵守）**
- 框架 pytest；配置 `pyproject.toml:115–118`；测试目录 `tests/`，配置 `pythonpath=["src","plugins/hermes"]`。
- 既有 Web 测试范式：`tests/test_dashboard_api.py` 用 `pytest.importorskip("fastapi")` 守卫 + `TestClient(app)` 夹具（`:15,17,19,219`），`res.status_code` + `res.json()` 断言。新测试应沿用同一 `app` 与 `TestClient` 方式，并保留 `importorskip` 守卫（dashboard 为可选 extra）。
- 针对性用例：`pytest tests/test_dashboard_api.py -q`（或新建 `tests/test_welcome.py`）；随后全量门禁 `make all`（`Makefile:106` = format+lint+strict mypy+pytest，`AGENTS.md:162`）。当前环境基线 `17 passed` 已验证测试链可用（§二.9）。
- 工作区 AGENTS.md：可执行验证放 `tests/`，改后跑相关测试，不提交测试日志；新增运行依赖须先说明理由（本次为 0 新增）。
- **SQLite/PostgreSQL 双后端门禁（`AGENTS.md:137–141`）不适用**：`/welcome` 为纯只读 HTTP 端点，不涉及 SQL、schema、事务、FTS、持久化编排或生命周期。
- 文档/grep 边界检查（`tests/test_agent_docs.py`、`test_architecture_boundaries.py`，`AGENTS.md:167`）在路由改动下应仍通过；本变更不改变公共 API/数据契约/配置默认值（`AGENTS.md:130`）。

**验收条件（功能，明确且可判定）**
1. `GET /welcome` 返回 `HTTP 200`；
2. 响应体为 JSON，且 `message == "welcome"`（精确体 `{"message": "welcome"}`）；
3. `Content-Type` 为 `application/json`；
4. 路由是**原生**的：在既有 `FastAPI app` 上用 `@app.get` 注册，无新框架/新运行依赖/新启动入口/挂载改动；
5. `tests/` 内有自动化测试覆盖该路由（沿用 `TestClient(app)` + `importorskip` 约定）；
6. 不破坏既有行为：既有 dashboard 用例全绿，质量门禁 `make all` 通过（或至少：针对性用例 + 变更文件的 lint/mypy 通过）；
7. 验证环境需装有 `fastapi`（`[dashboard]` extra），否则 `importorskip` 会跳过测试 —— 当前环境 `fastapi 0.115.0` 已具备。

---

## 六、改动范围（供后续阶段参考，本阶段不执行）

- **主改动**：在 `src/octop_memory/adapters/dashboard/server.py` 的 Routes 段（`:243+`）新增一条原生 `GET /welcome` 路由，返回 `{"message": "welcome"}`。单函数、带类型注解、无 DB 访问、无新依赖。
- **测试**：在 `tests/` 新增用例（建议 `tests/test_welcome.py` 独立文件，或并入 `tests/test_dashboard_api.py`），以 `pytest.importorskip("fastapi")` + `TestClient(app)` 断言 §五.1–3。
- **不改动**：`cli/dashboard.py` 启动逻辑、`bridge/`、任何存储/召回/提升管线、公共 API、数据格式、配置默认值、`pyproject.toml` 依赖。
- **可选（非功能验收必需）**：README/CHANGELOG 仅在该路由被当作对外可文档化行为时再提；dashboard 为源码专属且被 wheel 排除，文档影响面小。工程文档（`docs/agent/*`）按 `AGENTS.md` §95–99 由后续阶段按实际影响判断，本变更属轻量新增，预计无需 ADR。
- **验证命令**：`python3 -m pytest tests/test_welcome.py -q`（或 `tests/test_dashboard_api.py`）→ `make all`；结果写回后续阶段文档。

---

## 七、待确认 / 风险（均非阻塞）

1. **`app.py` 字面缺失**：任务提示的「app.py」在本仓库无对应文件，等价物为 `adapters/dashboard/server.py` 中的 `app` 实例与路由表。已在 §一.3 明确映射，不影响实施。
2. **`[dashboard]` 可选 extra + wheel 排除**（`pyproject.toml:49–53,87–92`；README:142）：路由只在「源码 checkout + 装了 fastapi」的环境可见/可测。验证阶段须确认 fastapi 已安装（当前 `0.115.0` 已具备），否则相关测试会被 `importorskip` 跳过而非失败。
3. **解释器版本**：当前 `python3 = 3.11.6` 低于 `requires-python >=3.12`；针对性测试在 3.11 下实跑通过，但 `make all` 中的 `mypy --strict`（`target py312`）、`ruff`（`py312`）对解释器敏感。运行环境由平台管理，后续阶段以平台环境为准，必要时记录 skip/失败而不谎报通过（`AGENTS.md:171`）。
4. **「原生」释义**：按「现有 FastAPI 服务」前提取「框架自带 `@app.get` 原生路由」；若平台另指「新建 stdlib `http.server` 服务」，则与「**现有** Web 服务中**增加**路由」冲突 —— 本阶段据仓库现状采用前者，作为假设记录，若有异议由平台裁决。
5. **前序产物缺失**：阶段目录与父目录日志中未见预置的前序文档/测试结果（§二 头部）。澄清所需信息已全部通过本次实地核对获得，故不阻塞本阶段，亦不触发「停止并记失败」。

---

## 八、验收结论 / 阶段边界

**Clarify 阶段已完成。** 框架（FastAPI，可选 `[dashboard]` extra）、启动入口（`octop-memory dashboard` → `uvicorn.run(app)`）、路由位置（`server.py` Routes 段）、接口约定（`dict` → `200 application/json`）、测试约定（`test_dashboard_api.py` 的 `TestClient(app)` + `importorskip`）与验收条件（§五）均已实地核对，证据见 §二、关键文件见 §三。

- **任务前提成立**：本仓库确有「现有 Web 服务」（FastAPI dashboard），与「库内无 Web 服务」的情形不同；无需新建服务，只需在既有 `app` 上扩展一条原生 `@app.get("/welcome")` 路由。功能验收条件明确、可判定、可据以在后续阶段先写失败用例再实现。
- **无阻塞**：未遇工具/读取层面障碍；`app.py` 字面缺失、可选 extra、解释器版本等均已作为非阻塞风险在 §七 记录并给出处置。
- **严格阶段边界**：本阶段仅写入本文件（`.wally/experiences/ca7bb0b6-df02-443b-8569-31fd6063972f/01-clarify.md`）；**未改动任何源码、未新增 `/welcome` 路由、未运行任何实现性改动、未执行 Git 提交**。§二 的探针与基线测试为只读核对，用于产出「执行证据 / 实际测试结果」；Git 提交由平台收尾。
