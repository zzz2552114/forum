# Forum（论坛系统）后端 + 前端

简体中文说明 — 本仓库实现了一个基于 FastAPI 的论坛后端及一个基于 Vue 的前端（位于 `frontend/`）。后端包含认证、帖子、评论、实时聊天、AI 提及提醒、热度同步等功能；前端使用 Vue 3 + Vite + Element Plus 开发。

---

## 项目概览

- 名称（后端配置）：`Forum Backend`
- API 前缀：`/api/v1`
- 健康检查：`GET /health`
- OpenAPI（JSON）：`/api/v1/openapi.json`
- 主要技术栈：
  - 后端：Python、FastAPI、Tortoise ORM、Aerich、uvicorn
  - 前端：Vue 3、TypeScript、Vite、Pinia、Element Plus
  - 其他：Redis、WebSocket（实时聊天）、AI 通知模块
- 仓库语言构成（近似）：Vue 42.5%、Python 41.4%、TypeScript 15.8%

仓库最后更新时间：2026-05-14（注意：仓库当前未指定许可证）。

---

## 目录结构（摘要）

- `main.py` - FastAPI 应用入口，包含生命周期管理、路由挂载和异常处理。
- `app/` - 后端源码（路由、模型、数据库连接、迁移、实时聊天、AI 提及等模块）。
- `frontend/` - 前端项目（Vue + Vite），包含 `package.json` 和开发脚本。
- `requirements.txt` - Python 依赖。
- `tests/` - 后端单元/集成测试（pytest）。
- `todo/` - 待办或笔记目录（项目内部用）。

---

## 快速开始（开发环境）

1. 克隆仓库
```bash
git clone https://github.com/zzz2552114/forum.git
cd forum
```

2. 后端（Python）依赖
- 建议使用虚拟环境（venv / conda / poetry 等）
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. 配置环境变量
在项目根目录创建 `.env`，示例：
```
# 数据库（MySQL）连接字符串（示例）
MYSQL_URL=mysql+asyncmy://user:password@127.0.0.1:3306/forum_db

# 安全配置
SECRET_KEY=changethissecretkeyinproduction!!!
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 超级管理员（初始化脚本会使用）
SUPER_ROOT_USERNAME=super_root
SUPER_ROOT_EMAIL=root@localhost
SUPER_ROOT_PASSWORD=root123456

# CORS 白名单（可选）
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```
（请根据生产环境修改 `SECRET_KEY`、数据库 URL、密码等敏感配置）

4. 数据库迁移 / 初始化
- 项目使用 Tortoise ORM + Aerich 进行迁移（仓库中含迁移工具依赖）。
- 一般流程（请根据仓库内的 `app/db/migrations`、`aerich` 配置调整）：
```bash
# 初始化 aerich（只需首次）
aerich init
aerich init-db

# 生成并应用迁移
aerich migrate
aerich upgrade
```
注意：具体命令和配置文件（tortoise config/aerich.ini）可能在 `app/db` 目录中，请查看对应实现并按需修改。

5. 运行后端（开发模式）
```bash
# 在项目根目录
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
启动后可访问：
- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/api/v1/openapi.json
- 健康检查: http://127.0.0.1:8000/health

6. 运行前端（开发）
```bash
cd frontend
npm install        # 或 pnpm/yarn
npm run dev
```
默认 Vite 开发服务器通常在 `http://localhost:5173`（或按 Vite 输出为准）。后端默认允许常见本地端口（配置中有 `BACKEND_CORS_ORIGINS`，包含 3000/8080/5173）。

---

## 主要功能说明（后端）

- 认证（JWT）与用户管理
- 帖子、评论、标签、空间（spaces）、资源上传、文件管理
- 帖子行为（点赞/收藏/举报等）
- 搜索接口（可能是全文或关键字搜索）
- 实时聊天（WebSocket 路由：realtime chat）
- AI 提及提醒（WebSocket 路由：ai-mention）
- 后台任务：热度同步（启动时会创建后台守护任务来同步热度/热分）
- 统一响应格式：成功/错误/分页（参见 `app/core/responses.py`）

---

## 测试

- 后端测试（pytest）
```bash
pytest
```
- 前端测试（Vitest）
```bash
cd frontend
npm run test
```

---

## 部署建议

- 使用生产级 ASGI 服务器（例如 uvicorn + gunicorn / uvicorn workers）或使用容器化部署（Docker）。
- 为生产环境准备：
  - 安全的 SECRET_KEY
  - 受管的 MySQL 实例（或托管数据库）
  - Redis（如需会话或消息队列）
  - 配置日志与监控（仓库中依赖 Sentry 等）
- 考虑将前后端分别构建部署：
  - 前端：`npm run build`，将生成的静态文件部署到静态站点服务或 CDN。
  - 后端：使用环境变量配置并在启动前执行数据库迁移/初始化脚本。

---

## 开发者提示 / 已知点

- 后端生命周期中会执行 `migrate_user_roles_and_trust()` 和 `init_super_root()`，确保在首次启动前数据库可用以完成初始化。
- 后端启动会创建一个后台任务 `sync_all_hot_scores_task()`，启动或关闭时需注意任务管理。
- 如果遇到依赖兼容问题，请参考 `requirements.txt` 中的精确版本。

---

## 贡献与联系方式

欢迎 PR 与 issue。如果你想贡献：
1. Fork 仓库并新建分支（feature/xxx 或 fix/xxx）。
2. 提交与功能或 bug 对应的修改和测试。
3. 发起 Pull Request 并在说明中描述变更点。

若需要联系仓库作者，可通过 GitHub 用户主页：
https://github.com/zzz2552114

---

## 致谢

本项目结合了 FastAPI、Tortoise ORM、Aerich、Vue 3 等现代工具与生态，便于快速构建高性能异步后端与响应式前端界面。希望本说明能帮助你快速上手并参与贡献