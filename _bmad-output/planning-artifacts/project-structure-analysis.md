## Project Structure & Boundaries

### Complete Project Directory Structure

```
OP_CMS/
├── frontend/                      # Vue 3 前端应用
│   ├── src/
│   │   ├── api/                  # API 调用模块
│   │   │   ├── customer.js       # 客户管理 API
│   │   │   ├── settlement.js     # 结算管理 API
│   │   │   ├── analysis.js       # 画像分析 API
│   │   │   └── auth.js          # 认证 API
│   │   │
│   │   ├── components/          # 公共组件
│   │   │   ├── common/          # 通用组件
│   │   │   │   ├── DataTable.vue
│   │   │   │   ├── SearchForm.vue
│   │   │   │   └── Pagination.vue
│   │   │   └── business/        # 业务组件
│   │   │       ├── CustomerCard.vue
│   │   │       └── BillingTable.vue
│   │   │
│   │   ├── views/               # 页面视图
│   │   │   ├── customer/        # 客户管理页面
│   │   │   │   ├── List.vue
│   │   │   │   ├── Detail.vue
│   │   │   │   └── Import.vue
│   │   │   ├── settlement/      # 结算管理页面
│   │   │   │   ├── Billing.vue
│   │   │   │   └── Tracking.vue
│   │   │   ├── analysis/        # 数据分析页面
│   │   │   │   └── Dashboard.vue
│   │   │   └── auth/           # 认证页面
│   │   │       └── Login.vue
│   │   │
│   │   ├── router/              # 路由配置
│   │   │   └── index.js
│   │   │
│   │   ├── stores/              # Pinia 状态管理
│   │   │   ├── user.js
│   │   │   └── app.js
│   │   │
│   │   ├── styles/              # 全局样式
│   │   │   └── index.less
│   │   │
│   │   ├── utils/               # 工具函数
│   │   │   ├── request.js       # Axios 封装
│   │   │   └── auth.js          # 认证工具
│   │   │
│   │   ├── main.js              # 应用入口
│   │   ├── App.vue              # 根组件
│   │   └── settings.js          # 全局配置
│   │
│   ├── public/                  # 静态资源
│   ├── package.json            # 项目依赖
│   ├── vite.config.js          # Vite 配置
│   ├── tsconfig.json          # TypeScript 配置
│   └── index.html             # HTML 入口
│
├── backend/                     # Python Sanic 后端服务
│   ├── app/
│   │   ├── main.py             # Sanic 应用入口
│   │   ├── config.py          # 配置管理
│   │   ├── extensions.py      # 扩展初始化
│   │   │
│   │   ├── api/                # API 路由层
│   │   │   ├── v1/
│   │   │   │   ├── customer.py     # 客户管理 API
│   │   │   │   ├── settlement.py   # 结算管理 API
│   │   │   │   ├── billing.py      # 账单管理 API
│   │   │   │   ├── analysis.py     # 画像分析 API
│   │   │   │   └── auth.py         # 认证 API
│   │   │   └── deps.py          # API 依赖注入
│   │   │
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── customer_service.py
│   │   │   ├── settlement_service.py
│   │   │   ├── billing_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── external_api.py     # 外部系统 API 调用
│   │   │
│   │   ├── models/             # 数据模型层 (Tortoise ORM)
│   │   │   ├── customer.py
│   │   │   ├── settlement.py
│   │   │   ├── billing.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/            # Pydantic 数据验证
│   │   │   ├── customer.py
│   │   │   ├── settlement.py
│   │   │   └── billing.py
│   │   │
│   │   ├── tasks/              # Celery 异步任务
│   │   │   ├── celery_app.py
│   │   │   ├── daily_usage_task.py  # 每日用量采集
│   │   │   └── monthly_billing_task.py  # 月度账单生成
│   │   │
│   │   ├── utils/              # 工具函数
│   │   │   ├── jwt.py          # JWT 认证工具
│   │   │   ├── excel.py        # Excel 导入导出
│   │   │   └── validators.py   # 数据验证工具
│   │   │
│   │   └── middleware/         # 中间件
│   │       ├── auth.py         # 认证中间件
│   │       └── logging.py      # 日志中间件
│   │
│   ├── tests/                  # 测试文件
│   │   ├── conftest.py
│   │   ├── test_customer.py
│   │   └── test_settlement.py
│   │
│   ├── requirements.txt       # 生产依赖
│   ├── requirements-dev.txt   # 开发依赖
│   ├── Dockerfile             # Docker 镜像配置
│   └── docker-compose.yml     # Docker 编排配置
│
├── deploy/                     # 部署配置
│   ├── docker/                 # Docker 部署配置
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.backend
│   │   └── docker-compose.yml  # Docker Compose 配置
│
├── docs/                      # 项目文档
│   ├── user-manual.md        # 用户手册
│   ├── api-documentation.md  # API 文档
│   └── deployment-guide.md   # 部署指南
│
├── .gitignore                 # Git 忽略文件
└── README.md                 # 项目说明
```

### Architectural Boundaries

**API Boundaries:**
- **前端 API 边界：** 前端通过 axios 与后端 API 通信，API 端点前缀为 `/api/v1`
- **后端 API 边界：** Sanic 服务器暴露 RESTful API，支持 HTTP 方法 GET/POST/PUT/DELETE
- **外部 API 边界：** 通过适配器模式与企业 ERP 系统和三方用量数据 API 集成

**Component Boundaries:**
- **前端组件边界：** 使用 Vue 3 组件，通过 props/events 通信，遵循单向数据流原则
- **业务组件边界：** 按功能模块划分（客户管理、结算管理等），组件间通过路由和状态管理通信
- **通用组件边界：** DataTable、SearchForm、Pagination 等通用组件可在各业务模块复用

**Service Boundaries:**
- **后端服务边界：** 业务逻辑按领域划分（客户服务、结算服务等），通过接口通信
- **外部服务边界：** 与 ERP 系统、邮件服务、短信服务集成，使用适配器模式解耦
- **异步任务边界：** Celery 任务队列处理定时任务和异步操作

**Data Boundaries:**
- **MySQL 边界：** 存储核心业务数据（客户信息、价格配置、结算记录等），使用 Tortoise ORM 访问
- **Redis 边界：** 缓存客户基础信息、价格配置和会话数据，使用 Redis 客户端访问
- **文件存储边界：** 导入/导出的 Excel/PDF 文件存储在云存储服务（如 AWS S3）
- **外部数据边界：** 通过 API 从第三方系统获取用量数据，使用适配器模式处理

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
- **客户管理（Epic）：** `/frontend/src/views/customer/` - 客户列表、详情、导入页面
- **结算管理（Epic）：** `/frontend/src/views/settlement/` - 账单生成、结算跟踪页面
- **数据分析（Epic）：** `/frontend/src/views/analysis/` - 管理看板、客户分层页面
- **用户权限（Epic）：** `/backend/app/api/v1/auth.py` - 认证 API，`/backend/app/middleware/auth.py` - 权限中间件
- **数据导入（Epic）：** `/frontend/src/views/customer/Import.vue` - 数据导入页面，`/backend/app/utils/excel.py` - 解析工具
- **系统管理（Epic）：** `/backend/app/config.py` - 系统配置，`/backend/app/middleware/logging.py` - 日志管理

**Cross-Cutting Concerns:**
- **认证与授权：** `/backend/app/middleware/auth.py` - 权限控制，`/frontend/src/utils/auth.js` - 前端认证
- **操作审计：** `/backend/app/middleware/logging.py` - 操作日志，数据库审计字段
- **数据验证：** `/backend/app/utils/validators.py` - 后端验证，前端表单验证
- **错误处理：** 前端操作反馈，后端异常处理
- **缓存策略：** `/backend/app/extensions.py` - Redis 配置，`/backend/app/utils/cache.py` - 缓存工具

### Integration Points

**Internal Communication:**
- **前端到后端：** HTTP/REST API，使用 axios 发送请求
- **后端组件通信：** API 调用 → 业务逻辑 → 数据访问 → 数据库操作
- **异步任务通信：** Celery 任务队列，使用 Redis 作为 broker
- **状态管理：** Pinia 存储全局状态，组件间通过 store 通信

**External Integrations:**
- **ERP 系统集成：** 通过适配器模式与企业 ERP 系统同步客户信息和订单数据
- **邮件服务集成：** 使用 SMTP 发送报表通知和提醒
- **短信服务集成：** 使用短信 API 发送逾期提醒
- **云存储集成：** 使用 AWS S3 或阿里云 OSS 存储文件

**Data Flow:**
1. **客户信息管理流程：** 用户操作 → 前端表单 → API 请求 → 后端校验 → 数据库操作 → 返回结果
2. **Excel 数据导入流程：** 用户上传 → 前端上传 → 后端解析 → 数据校验 → 清洗转换 → 批量入库
3. **用量数据采集流程：** Celery 定时任务 → 调用外部 API → 数据解析 → 数据校验 → 更新客户用量
4. **账单生成流程：** Celery 定时任务 → 获取客户列表 → 读取定价规则 → 计算账单金额 → 生成账单记录
5. **收款核销流程：** 用户录入收款 → 后端校验 → 匹配待核销账单 → 用户确认 → 更新账单状态

### File Organization Patterns

**Configuration Files:**
- **前端配置：** `vite.config.js` - Vite 构建配置，`tsconfig.json` - TypeScript 配置
- **后端配置：** `config.py` - 环境变量和系统参数配置，`.env` - 环境变量文件
- **部署配置：** `docker-compose.yml` - 本地开发部署，`kubernetes/` - Kubernetes 生产部署
- **依赖配置：** `package.json` - 前端依赖，`requirements.txt` - 后端依赖

**Source Organization:**
- **前端代码：** 按功能模块组织，API、组件、视图、路由、状态管理分离
- **后端代码：** 分层架构，API 路由层、业务逻辑层、数据模型层、工具函数分离
- **公共代码：** 通用组件、工具函数、中间件可在项目内复用

**Test Organization:**
- **前端测试：** 在 `frontend/src/__tests__/` 目录下，使用 Vitest + Vue Test Utils
- **后端测试：** 在 `backend/tests/` 目录下，使用 Pytest + pytest-asyncio
- **测试类型：** 单元测试、集成测试、端到端测试

**Asset Organization:**
- **静态资源：** `frontend/public/` - 图片、字体等静态文件
- **文件存储：** 导入/导出的 Excel/PDF 文件存储在云存储服务
- **样式资源：** `frontend/src/styles/` - 全局样式，组件内联样式

### Development Workflow Integration

**Development Server Structure:**
- **前端开发：** 使用 Vite 开发服务器，支持热更新
- **后端开发：** 使用 Sanic 自动重载，支持开发模式
- **数据库开发：** 使用 Docker Compose 本地运行 MySQL 和 Redis
- **调试工具：** Vue DevTools、Chrome DevTools、Sanic 调试器

**Build Process Structure:**
- **前端构建：** Vite 打包，生成优化后的静态资源
- **后端打包：** Python 打包，使用 Docker 容器化
- **依赖管理：** npm install 管理前端依赖，pip install 管理后端依赖

**Deployment Structure:**
- **本地部署：** Docker Compose 启动所有服务
- **测试部署：** Docker Compose 测试环境
- **生产部署：** Docker Compose 生产环境，支持容器编排
- **CI/CD 集成：** GitHub Actions 自动构建、测试、部署