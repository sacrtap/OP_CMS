# 项目上下文: OP_CMS

**项目名称：** OP_CMS  
**项目描述：** BMAD 驱动的数据库迁移项目 (PostgreSQL 16 → MySQL 8.0+)  
**生成日期：** 2026-02-24  
**最后更新：** 2026-02-25  
**BMAD 版本：** 6.0.3  
**测试状态：** 100% 通过率 (后端 179/179, 前端 32/32)

---

## 1. 技术栈和版本

### 前端技术栈
- **框架：** Vue 3.4.19 (Composition API)
- **UI 库：** Arco Design 2.57.0
- **构建工具：** Vite 5.1.0
- **状态管理：** Pinia 2.1.7
- **路由：** Vue Router 4.2.5
- **HTTP 客户端：** Axios 1.6.7
- **TypeScript：** 5.3.3
- **Node.js 版本：** 20.x+
- **包管理：** Bun (bun.lockb present)

### 后端技术栈
- **框架：** Sanic 23.6.0 + sanic-ext 23.6.0
- **Python 版本：** 3.9+
- **数据库：** MySQL 8.0+ (迁移自 PostgreSQL 16)
- **ORM：** SQLAlchemy 2.0.0+ / Tortoise ORM
- **MySQL 驱动：** PyMySQL 1.1.0+
- **API 文档：** Swagger/OpenAPI (sanic-ext)
- **任务队列：** Celery 5.3.0+ + Flower 2.0.0+
- **缓存：** Redis 5.0.0+
- **数据验证：** Pydantic 2.0.0+
- **Excel 处理：** openpyxl 3.1.0+ + pandas 2.0.0+

### DevOps 技术栈
- **容器化：** Docker 24.x + Docker Compose
- **CI/CD：** GitHub Actions / GitLab CI
- **监控：** Prometheus + Grafana
- **日志：** ELK Stack (Elasticsearch, Logstash, Kibana)

---

## 2. 语言特定规则

### Python 规则
- **代码风格：** PEP 8
- **类型提示：** 严格使用 type hints
- **文档字符串：** Google style docstrings
- **异步编程：** async/await for I/O operations
- **依赖管理：** pip + requirements.txt / pyproject.toml

### JavaScript/TypeScript 规则
- **代码风格：** StandardJS / Airbnb Style Guide
- **TypeScript：** 严格模式 (strict: true)
- **Vue 3 规则：** Composition API 优先
- **包管理：** Bun (preferred) / npm
- **构建配置：** Vite + TypeScript

---

## 3. 框架特定规则

### Vue 3 规则
- **组件命名：** PascalCase (MyComponent.vue)
- **文件命名：** kebab-case (my-component.vue)
- **Composition API：** 使用 `<script setup lang="ts">` 语法糖
- **状态管理：** Pinia stores in `src/stores/`
- **路由：** Lazy loading for routes
- **样式：** Scoped CSS + CSS Modules
- **TypeScript：** 严格模式，所有组件使用 TypeScript
- **UI 组件库：** 使用 Arco Design 组件 (@arco-design/web-vue)
- **主题定制：** 使用 Arco Design 主题配置系统

### Sanic 规则
- **蓝图：** 使用 Blueprint for modular routing
- **异步视图：** Always async def for request handlers
- **异常处理：** Custom exception handlers with sanic-ext
- **中间件：** Request/response interceptors (@app.middleware)
- **配置管理：** Environment variables + config.py
- **CORS：** 使用 sanic-ext 的 CORS 中间件
- **类型提示：** 所有路由和服务函数使用类型提示

---

## 4. 测试规则

### 单元测试
- **前端：** Vitest 1.2.2 + @vue/test-utils 2.4.6 + happy-dom/jsdom
- **后端：** pytest + pytest-asyncio + coverage
- **测试覆盖率：** 最低 70% (pytest --cov-fail-under=70)
- **测试命名：** `test_<function>_<condition>_<expected>.py`
- **测试报告：** HTML (htmlcov/) + terminal missing lines
- **当前状态：** 100% 通过率 (后端 179/179, 前端 32/32)

### 集成测试
- **E2E：** Playwright / Cypress
- **API 测试：** pytest + httpx
- ** Database：** pytest fixtures with test database

### 测试策略
- **TDD：** Test-Driven Development for critical features
- **红 - 绿 - 重构：** Red (write failing test) → Green (make it pass) → Refactor
- **测试标记：** pytest markers (unit, integration, slow, auth, customer, pricing)
- **Mock 使用：** 对 Session、外部 API 使用 Mock，对 openpyxl 使用真实对象
- **测试隔离：** 使用独立测试数据库，避免测试间污染

---

## 5. 代码质量和风格规则

### 静态代码分析
- **前端：** ESLint 8.56.0 + Prettier + vue-tsc 1.8.27
- **后端：** Ruff + Black
- **类型检查：** TypeScript compiler (tsc), MyPy (Python)
- **配置文件：** eslint.config.js, tsconfig.json, pytest.ini

### 代码规范
- **函数长度：** Max 50 lines
- **文件长度：** Max 500 lines
- **复杂度：** Cyclomatic complexity < 10
- **命名规范：** CamelCase for classes, snake_case for functions/variables

### 文档要求
- **API 文档：** OpenAPI/Swagger for all endpoints
- **代码注释：** Required for complex logic
- **README：** Project setup, configuration, and usage

---

## 6. 开发工作流规则

### Git 工作流
- **分支策略：** Git Flow (main, develop, feature/*, hotfix/*)
- **提交消息：** Conventional Commits format
- **PR 要求：** Required reviews, passing tests, updated documentation

### 开发流程
- **代码审查：** PR must be reviewed by at least 2 team members
- **CI/CD：** All tests must pass before merge
- **版本控制：** Semantic Versioning (MAJOR.MINOR.PATCH)

### 任务管理
- **Story 跟踪：** BMAD stories in `_bmad-output/implementation-artifacts/stories/`
- **Sprint 状态：** JSON YAML in `sprint-status.yaml`
- **任务状态：** backlog → ready-for-dev → in-progress → review → done

---

## 7. 关键避免规则

### 禁止操作
- ❌ Never commit `.env` files or secrets
- ❌ Never use hardcoded credentials
- ❌ Never skip tests for production code
- ❌ Never merge broken builds
- ❌ Never force push to main/master branches

### 最佳实践避免
- ⚠️ Avoid global state in Vue components
- ⚠️ Avoid N+1 queries in database operations
- ⚠️ Avoid blocking I/O in async functions
- ⚠️ Avoid deep nesting in Vue templates
- ⚠️ Avoid large commit with multiple features

### 性能考虑
- ⚠️ Use Vue 3 reactivity system properly
- ⚠️ Implement pagination for large datasets
- ⚠️ Use Redis for caching frequent queries
- ⚠️ Implement server-side rendering for SEO-critical pages

---

## 8. 项目结构规则

### 目录结构
```
OP_CMS/
├── frontend/                # Vue 3 frontend application
│   ├── src/
│   │   ├── assets/         # Static assets
│   │   ├── components/     # Reusable components
│   │   ├── views/          # Page components
│   │   ├── stores/         # Pinia stores
│   │   ├── router/         # Vue Router configuration
│   │   ├── services/       # API service layers
│   │   └── App.vue
│   ├── tests/             # Frontend tests
│   ├── vite.config.ts
│   └── package.json
│
├── backend/               # Sanic backend application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Background tasks
│   │   └── main.py
│   ├── tests/           # Backend tests
│   ├── requirements.txt
│   └── dockerfile
│
├── docs/                 # Project documentation
│   ├── api/             # API documentation
│   ├── architecture/    # Architecture diagrams
│   └── project-context.md
│
├── _bmad/               # BMAD framework
│   ├── bmm/            # Core module
│   ├── _bmad-output/   # Generated artifacts
│   └── config.yaml
│
├── docker/              # Docker configuration
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── docker-compose.yml
│
└── config/             # Environment configurations
    ├── .env.example
    └── config.py

```

### 命名约定
- **文件命名：** kebab-case for Vue components, snake_case for Python modules
- **类命名：** PascalCase for both Vue components and Python classes
- **常量命名：** UPPER_SNAKE_CASE
- **变量命名：** camelCase for JavaScript, snake_case for Python

---

## 9. 架构设计原则

### 前端架构
- **组件化：** Small, reusable components
- **状态管理：** Centralized state with Pinia
- **响应式设计：** Mobile-first approach
- **性能优化：** Code splitting, lazy loading, image optimization

### 后端架构
- **分层架构：** API → Service → Model → Database
- **异步处理：** Background tasks for long-running operations
- **API 设计：** RESTful principles with proper HTTP status codes
- **数据库设计：** Normalized tables with proper indexes

### 部署架构
- **容器化：** Docker Compose for local development
- **环境隔离：** Development, staging, production environments
- **健康检查：** API endpoints for service health monitoring
- **日志管理：** Structured logging with proper log levels

---

## 10. 数据库设计规则

### MySQL 8.0+ 规则
- **字符集：** utf8mb4 for full Unicode support
- **引擎：** InnoDB for ACID compliance
- **索引：** Index on foreign keys and frequently queried columns
- **事务：** Use transactions for data consistency
- **数据迁移：** Alembic / Tortoise ORM migrations
- **SQL 语法：** 避免 PostgreSQL 特有语法 (RETURNING, ON CONFLICT, etc.)
- **迁移注意：** MySQL 不支持部分 PostgreSQL 功能 (JSONB 操作符，数组类型等)

### PostgreSQL 到 MySQL 迁移要点
- **迁移工具：** 自定义迁移脚本 + 手动验证
- **类型映射：** JSONB → JSON, ARRAY → JSON/逗号分隔，SERIAL → AUTO_INCREMENT
- **语法变更：** 替换 PostgreSQL 特有函数和语法
- **测试验证：** 所有查询和测试需在 MySQL 环境验证

### 数据模型命名
- **表名：** snake_case plural (customers, pricing_configs)
- **字段名：** snake_case (customer_id, created_at)
- **主键：** id (UUID or auto-increment)
- **外键：** <table_name>_id

---

## 11. API 设计规则

### RESTful 端点
- **资源命名：** Plural nouns (GET /api/v1/customers)
- **HTTP 方法：** GET (read), POST (create), PUT (update), DELETE (delete)
- **状态码：** 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- **版本控制：** /api/v1/ path versioning

### 请求/响应格式
- **请求体：** JSON format with proper content-type header
- **错误响应：** Consistent error structure with code, message, details
- **分页：**?page=1&limit=10 with meta information
- **排序：**?sort=created_at&order=desc

---

## 12. 安全性规则

### 前端安全
- **XSS 防护：** Vue's built-in escaping + sanitization
- **CSRF 防护：** Token-based authentication
- **敏感数据：** Never expose API keys or secrets in frontend code

### 后端安全
- **身份验证：** JWT or session-based authentication
- **授权：** Role-based access control (RBAC)
- **输入验证：** Sanitize and validate all user inputs
- **SQL 注入：** Use parameterized queries / ORM
- **速率限制：** Implement rate limiting for API endpoints

---

## 13. 性能优化规则

### 前端性能
- **代码分割：** Lazy load routes and components
- **图片优化：** WebP format + responsive images
- **缓存策略：** Service workers for PWA features
- **虚拟滚动：** For large lists and tables

### 后端性能
- **数据库优化：** Index optimization, query optimization
- **缓存策略：** Redis for session and data caching
- **异步处理：** Background tasks for heavy operations
- **连接池：** Database connection pooling

---

## 14. 监控和日志规则

### 日志级别
- **DEBUG：** Detailed information for debugging
- **INFO：** General application events
- **WARNING：** Non-critical issues
- **ERROR：** Error events that need attention
- **CRITICAL：** Critical errors requiring immediate action

### 监控指标
- **API 性能：** Response time, error rate
- **数据库性能：** Query time, connection pool usage
- **系统资源：** CPU, memory, disk usage
- **业务指标：** User actions, conversion rates

---

## 15. 依赖管理规则

### 前端依赖
- **生产依赖：** npm install --save
- **开发依赖：** npm install --save-dev
- **版本管理：** Caret range (^) for minor updates
- **锁定文件：** package-lock.json or bun.lockb

### 后端依赖
- **生产依赖：** pip install
- **开发依赖：** pip install -r requirements-dev.txt
- **版本管理：** Exact version pinning
- **锁定文件：** requirements.txt or poetry.lock

---

## 16. 文档规则

### API 文档
- **OpenAPI 规范：** YAML/JSON format
- **端点文档：** Description, request/response examples, error cases
- **认证说明：** Authentication requirements and examples
- **测试 API：** Interactive API documentation

### 代码文档
- **函数文档：** Docstrings for all public functions
- **类文档：** Class description and method summaries
- **配置文档：** Environment variables and configuration options
- **架构文档：** System architecture and data flow diagrams

---

## 17. 数据迁移规则

### 迁移脚本
- **版本控制：** Each migration has a unique version number
- **可逆性：** Upsert and downsert operations
- **数据备份：** Backup before major migrations
- **测试迁移：** Test migrations in staging environment
- **幂等性：** Migration scripts must be idempotent

### PostgreSQL → MySQL 迁移规则
- **语法检查：** 替换所有 PostgreSQL 特有语法
- **类型映射：** 
  - JSONB → JSON (MySQL 8.0+ supports JSON)
  - ARRAY → JSON or comma-separated string
  - SERIAL → AUTO_INCREMENT
  - TIMESTAMPTZ → DATETIME with timezone handling in app
- **函数替换：**
  - NOW() → CURRENT_TIMESTAMP
  - RETURNING clause → separate SELECT after INSERT
  - ON CONFLICT → INSERT ... ON DUPLICATE KEY UPDATE
- **索引迁移：** 验证所有索引在 MySQL 下有效
- **查询测试：** 所有自定义查询需在 MySQL 环境测试

### 迁移工具
- ** Database：** Alembic or Tortoise ORM migrations
- **脚本执行：** Migration scripts must be idempotent
- **错误处理：** Rollback on migration failures

---

## 18. 持续集成/持续部署规则

### CI/CD 流程
- **构建触发：** Push to feature_branch and PR to develop/main
- **自动化测试：** Run all unit, integration, and E2E tests
- **代码审查：** Required reviews before merge
- **部署触发：** Merge to main triggers production deployment

### 部署策略
- **蓝绿部署：** Zero-downtime deployments
- **回滚计划：** Automated rollback on deployment failure
- **健康检查：** Verify service health after deployment

---

## 19. 配置管理规则

### 环境变量
- **开发环境：** .env.development
- **生产环境：** .env.production
- **安全存储：** Use secrets management for sensitive data
- **配置验证：** Validate all required environment variables

### 配置文件
- **版本控制：** .env.example in version control
- **环境隔离：** Different configurations for each environment
- **配置热更新：** Support for runtime configuration changes

---

## 20. 国际化和本地化规则

### 多语言支持
- **前端翻译：** vue-i18n for translations
- **后端国际化：**gettext or Babel for translations
- **语言检测：** Browser locale or user preference
- **默认语言：** English (en-US) as fallback

---

**文档维护：** Last updated 2026-02-25  
**版本：** v1.1  
**由 BMAD generate-project-context workflow 更新  
**测试状态：** 100% 通过率 (后端 179/179, 前端 32/32)
