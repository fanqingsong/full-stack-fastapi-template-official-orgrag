# 项目分析文档

## 项目概述

这是一个基于 [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) 的全栈应用项目，在此基础上添加了组织管理和工作流编排功能。

---

## 项目功能

### 核心功能（官方模板）
- **用户认证系统**：JWT 身份验证、安全密码哈希、基于邮件的密码恢复
- **管理后台**：响应式仪表板界面，支持深色模式
- **API 文档**：自动生成的交互式 API 文档（Swagger UI）
- **邮件功能**：开发环境使用 Mailcatcher 进行本地邮件测试

### 定制功能
- **组织管理功能**（Organization Management）
  - 业务单元（Business Units）
  - 职能部门（Functions）
- **Airflow 工作流编排**：集成了 Apache Airflow 用于任务调度

---

## 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | ≥0.114.2 | Python Web 框架 |
| SQLModel | ≥0.0.21 | ORM（基于 SQLAlchemy + Pydantic） |
| PostgreSQL | - | 关系型数据库 |
| Pydantic | >2.0 | 数据验证和设置管理 |
| Alembic | ≥1.12.1 | 数据库迁移工具 |
| PyJWT | ≥2.8.0 | JWT 令牌认证 |
| pwdlib | ≥0.3.0 | 密码哈希（支持 Argon2/Bcrypt） |
| Redis | ≥5.0.0 | 缓存/消息队列 |
| MinIO | ≥7.2.0 | 对象存储（S3 兼容） |
| Sentry SDK | ≥1.40.6 | 错误监控和性能追踪 |
| Pytest | ≥7.4.3 | 单元测试框架 |
| Python | ≥3.10 | 运行时环境 |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| React | ^19.1.1 | UI 框架 |
| TypeScript | ^5.9.3 | 类型安全 |
| Vite | ^7.3.0 | 构建工具和开发服务器 |
| TanStack Router | ^1.157.3 | 路由管理 |
| TanStack Query | ^5.90.12 | 服务端状态管理/数据获取 |
| Tailwind CSS | ^4.1.17 | 原子化 CSS 框架 |
| shadcn/ui + Radix UI | - | 无样式 UI 组件库 |
| React Hook Form | ^7.68.0 | 表单状态管理 |
| Zod | ^4.3.6 | Schema 验证 |
| Cypress | ^14.3.2 | 端到端测试 |
| Biome | ^2.3.12 | 前端代码格式化和检查 |
| Axios | 1.13.2 | HTTP 客户端 |
| next-themes | ^0.4.6 | 主题切换（深色模式） |

### 基础设施与运维
| 技术 | 用途 |
|------|------|
| Docker Compose | 容器编排和多环境配置 |
| Traefik | 反向代理、负载均衡、自动 HTTPS |
| Apache Airflow | 工作流调度和任务编排 |
| GitHub Actions | CI/CD 自动化 |
| Ruff | Python 代码检查和格式化 |
| MailHog/Mailcatcher | 开发环境邮件测试 |

---

## 项目结构

```
.
├── backend/                # FastAPI 后端应用
│   ├── app/               # 应用主代码目录
│   ├── tests/             # 后端测试
│   ├── alembic.ini        # 数据库迁移配置
│   ├── pyproject.toml     # Python 项目配置
│   └── Dockerfile         # 后端容器构建
│
├── frontend/              # React 前端应用
│   ├── src/               # 前端源代码
│   ├── package.json       # Node.js 依赖配置
│   └── vite.config.ts     # Vite 构建配置
│
├── airflow/               # Apache Airflow 配置
│   ├── dags/              # DAG 工作流定义
│   ├── plugins/           # Airflow 插件
│   └── docker-compose.yaml # Airflow 容器编排
│
├── hooks/                 # Git 钩子脚本
├── scripts/               # 项目实用脚本
├── services/              # 额外服务配置
│
├── compose.yml            # Docker Compose 主配置
├── compose.dev.yml        # 开发环境配置
├── compose.prod.yml       # 生产环境配置
├── compose.staging.yml    # 预发布环境配置
├── compose.airflow.yml    # Airflow 服务配置
└── compose.kong.yml       # Kong API 网关配置
```

---

## 环境配置

项目包含多环境配置文件：
- `.env` - 基础配置
- `.env.dev` - 开发环境
- `.env.staging` - 预发布环境
- `.env.prod` - 生产环境

### 关键配置项
| 配置项 | 说明 |
|--------|------|
| `SECRET_KEY` | 应用密钥（必须修改） |
| `FIRST_SUPERUSER_PASSWORD` | 初始管理员密码（必须修改） |
| `POSTGRES_PASSWORD` | 数据库密码（必须修改） |
| `smtp_*` | 邮件服务配置 |

---

## 开发命令速查

### 后端开发
```bash
cd backend
# 启动开发服务器
uvicorn app.main:app --reload
# 运行测试
pytest
# 代码检查
ruff check
```

### 前端开发
```bash
cd frontend
# 启动开发服务器
bun run dev
# 构建生产版本
bun run build
# 生成 API 客户端
bun run generate-client
# 运行 E2E 测试
bun run test
```

### Docker Compose
```bash
# 启动所有服务
docker compose -f compose.yml -f compose.dev.yml up
# 生产环境
docker compose -f compose.yml -f compose.prod.yml up
```

---

## 相关文档

- [backend/README.md](../backend/README.md) - 后端开发文档
- [frontend/README.md](../frontend/README.md) - 前端开发文档
- [deployment.md](../deployment.md) - 部署指南
- [development.md](../development.md) - 开发指南
- [release-notes.md](../release-notes.md) - 版本更新日志

---

## 项目仓库

- 基于模板：[fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template)
- 当前分支：master
- 许可证：MIT License
