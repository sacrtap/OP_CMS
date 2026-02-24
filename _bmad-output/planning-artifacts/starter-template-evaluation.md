## Starter Template Evaluation

### Primary Technology Domain

企业运营软件（房产行业客户管理与结算） based on project requirements analysis

### Starter Options Considered

**前端启动模板分析：**
1. **Vite Vue 3 官方模板** - 基础 Vue 3 + TypeScript 模板，提供最小化配置
2. **Arco Design Pro Vue** - 字节跳动开源的企业级管理系统模板，基于 Vue 3 + Arco Design，包含完整的权限管理、表单、表格等组件
3. **Vue Admin Plus** - 社区流行的 Vue 3 管理后台模板，支持多种 UI 框架

**后端启动模板分析：**
1. **Sanic 官方示例** - 官方提供的基础示例项目
2. **Sanic RESTful API 模板** - 社区开发的 RESTful API 模板，包含认证、数据库集成等
3. **Full Stack Python** - 包含 Sanic 的全栈模板项目

**部署模板分析：**
1. **Docker Compose 基础模板** - 简单的本地开发和测试部署
2. **Kubernetes 生产部署模板** - 完整的 Kubernetes 部署配置
3. **Helm Chart** - Kubernetes 应用包管理

### Selected Starter: Arco Design Pro Vue (Frontend) + Custom Sanic Backend Template (Backend)

**Rationale for Selection:**
- **前端选择 Arco Design Pro Vue**：该模板提供了企业级管理系统所需的完整功能，包括用户认证、权限管理、数据表格、表单、图表等，与项目需求高度匹配。它使用 Vue 3 + TypeScript + Pinia + Vue Router，与我们的技术栈完全一致。
- **后端选择自定义 Sanic 模板**：虽然没有官方的 Sanic 启动模板，但我们可以基于项目架构文档创建一个符合需求的模板，包含 Tortoise ORM、Celery、Redis 等组件。

**Initialization Command:**

```bash
# 前端初始化
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install @arco-design/web-vue pinia vue-router@4 axios

# 后端初始化（使用自定义模板）
mkdir backend && cd backend
pip install sanic tortoise-orm pydantic celery redis pyjwt openpyxl
mkdir -p app/{api,v1,services,models,schemas,tasks,utils,middleware} tests
touch requirements.txt requirements-dev.txt Dockerfile docker-compose.yml

# 创建基础文件结构
cat > app/main.py << 'EOF'
from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.log import logger
from app.api.v1 import customer, settlement, billing, analysis, auth
from app.middleware.auth import auth_middleware
from app.extensions import db, redis_client, celery_app

app = Sanic(__name__)

# Configuration
app.config.update({
    'DATABASE_URL': 'mysql://user:password@localhost:3306/op_cms',
    'REDIS_URL': 'redis://localhost:6379/0',
    'JWT_SECRET': 'your-secret-key'
})

# Extensions
db.init_app(app)
redis_client.init_app(app)
celery_app.init_app(app)

# Middleware
app.register_middleware(auth_middleware)

# Routes
app.blueprint(customer.bp)
app.blueprint(settlement.bp)
app.blueprint(billing.bp)
app.blueprint(analysis.bp)
app.blueprint(auth.bp)

# Error handling
@app.exception(NotFound)
async def not_found(request, exception):
    logger.warning(f"Route not found: {request.url}")
    return json({"error": "Not found"}, status=404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True)
EOF
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- **前端**：Vue 3 + TypeScript，使用 Vite 作为构建工具
- **后端**：Python 3.9+，使用 Sanic 框架

**Styling Solution:**
- **前端**：Arco Design Vue 2.x 组件库，支持主题定制和响应式设计
- **后端**：无特定样式要求，重点关注 API 设计和业务逻辑

**Build Tooling:**
- **前端**：Vite 4.x，支持极速热更新和优化构建
- **后端**：Python 原生打包，使用 Docker 容器化部署

**Testing Framework:**
- **前端**：Vitest + Vue Test Utils
- **后端**：Pytest + pytest-asyncio，支持异步测试

**Code Organization:**
- **前端**：
  - `src/api/` - API 调用模块
  - `src/components/` - 公共组件
  - `src/views/` - 页面视图
  - `src/router/` - 路由配置
  - `src/stores/` - Pinia 状态管理
  - `src/styles/` - 全局样式
  - `src/utils/` - 工具函数

- **后端**：
  - `app/api/v1/` - API 路由层
  - `app/services/` - 业务逻辑层
  - `app/models/` - 数据模型层 (Tortoise ORM)
  - `app/schemas/` - Pydantic 数据验证
  - `app/tasks/` - Celery 异步任务
  - `app/utils/` - 工具函数
  - `app/middleware/` - 中间件
  - `tests/` - 测试文件

**Development Experience:**
- **前端**：Vite 热更新、Vue DevTools、Arco Design 组件文档
- **后端**：Sanic 自动重载、Swagger API 文档、Docker 本地开发环境
- **部署**：Docker Compose 本地开发环境，Kubernetes 生产部署

**Note:** Project initialization using this command should be the first implementation story.