---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9]
inputDocuments: ["prd.md"]
workflowType: "architecture"
lastStep: 9
status: "complete"
completedAt: "2026-02-25"
project: OP_CMS
document_type: Architecture Design Document
version: 1.6.0
status: Draft - High-Level Design
created: 2026-02-24
updated: 2026-02-25
author: BMAD Architect Agent
phase: Phase 3 - Architecture Validation & Review
---

# 客户信息管理与运营系统 - 架构设计文档

## 文档信息

| 项目 | 值 |
|------|-----|
| **项目名称** | 客户信息管理与运营系统 |
| **文档类型** | 架构设计文档 |
| **版本号** | 1.1.0 |
| **状态** | 草稿 - Phase 2 详细设计 (数据库) |
| **创建日期** | 2026-02-24 |
| **更新日期** | 2026-02-24 |
| **技术栈** | Vue 3 + Arco Design | Python 3.9+ + Sanic | MySQL 8.0+ |

---

## 修订历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| 1.0.0 | 2026-02-24 | BMAD Architect | 初始版本 - 高层次架构设计 |
| 1.1.0 | 2026-02-24 | BMAD Architect | Phase 2 详细设计 - 数据库 ER 图和表结构（支持三种结算模式） |
| 1.2.0 | 2026-02-24 | BMAD Architect | Phase 2 详细设计 - API 接口设计（24 个核心接口） |

---

## 目录

1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [技术栈选型](#技术栈选型)
4. [项目结构](#项目结构)
5. [数据流设计](#数据流设计)
6. [关键技术决策](#关键技术决策)
7. [实施路线图](#实施路线图)

---

## 项目概述

### 系统定位

**客户运营中台** - 连接上游客户接入系统和下游结算/财务系统，以**结算管理为核心**的统一运营平台（内部员工使用）

### 业务目标

1. **客户信息管理** - 统一管理平台，1320 条客户数据系统化
2. **账号治理** - 规范化账号体系，状态流转自动化
3. **结算管理** - 多维度结算体系，保障收入准确性
4. **画像管理** - 客户消费行为分析，数据驱动决策
5. **客户分析** - 用量趋势、流失预警、信用评分

### 核心需求优先级

| 优先级 | 模块 | 核心功能 |
|--------|------|----------|
| **P0-1** | 客户信息管理 | 客户档案（18 字段）、Excel 导入、数据清洗、账号状态、负责人分配 |
| **P0-2** | 结算管理 | 定价配置（单层/多层）、账单生成、结算状态跟踪、收款核销 |
| **P1** | 自动化 | 用量 API 采集、定时账单、逾期提醒、状态自动流转 |
| **P2** | 画像分析 | 客户分层、用量趋势、流失预警、信用评分、管理看板 |
| **P3** | 体验优化 | 用量可视化、高级筛选、批量操作、自定义报表 |

### 关键决策

- ✅ 系统定位：内部运营工具（非客户自助）
- ✅ 用量采集：调用三方系统 API，每日定时获取
- ✅ 支付系统：暂不对接（人工收款核销）
- ✅ 客户基础信息维护：第一优先级

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        客户信息管理与运营系统                            │
│                          技术架构设计 (High-Level)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    Frontend Layer (Vue 3)                     │      │
│  │                                                               │      │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │      │
│  │  │ 客户信息管理  │  │  结算管理    │  │  画像分析    │       │      │
│  │  │              │  │              │  │              │       │      │
│  │  │ • 客户列表   │  │ • 账单生成   │  │ • 客户分层   │       │      │
│  │  │ • 客户详情   │  │ • 结算跟踪   │  │ • 用量趋势   │       │      │
│  │  │ • 数据导入   │  │ • 收款核销   │  │ • 流失预警   │       │      │
│  │  │ • 批量操作   │  │ • 报表导出   │  │ • 管理看板   │       │      │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │      │
│  │                                                               │      │
│  │              UI Framework: Arco Design Vue                    │      │
│  │              State: Pinia | Router: Vue Router                │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                              │                                           │
│                              │ HTTP/REST API                             │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                Backend Layer (Python 3.9+ + Sanic)            │      │
│  │                                                               │      │
│  │  ┌──────────────────────────────────────────────────────┐   │      │
│  │  │                  API Gateway Layer                    │   │      │
│  │  │  • 认证鉴权 (JWT)  • 请求校验  • 限流  • 日志        │   │      │
│  │  └──────────────────────────────────────────────────────┘   │      │
│  │                                                               │      │
│  │  ┌──────────────────┐  ┌──────────────────┐                │      │
│  │  │   Business Layer │  │    Task Queue    │                │      │
│  │  │                  │  │                  │                │      │
│  │  │ • 客户服务       │  │ • Celery Workers │                │      │
│  │  │ • 结算服务       │  │ • 定时任务调度   │                │      │
│  │  │ • 账单服务       │  │ • 异步任务处理   │                │      │
│  │  │ • 报表服务       │  │                  │                │      │
│  │  │ • 画像服务       │  │                  │                │      │
│  │  └──────────────────┘  └──────────────────┘                │      │
│  │                                                               │      │
│  │  ┌──────────────────────────────────────────────────────┐   │      │
│  │  │                 Data Access Layer                     │   │      │
│  │  │  • ORM: Tortoise ORM  • 连接池  • 缓存策略           │   │      │
│  │  └──────────────────────────────────────────────────────┘   │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                              │                                           │
│                              │                                           │
│            ┌─────────────────┼─────────────────┐                        │
│            │                 │                 │                        │
│            ▼                 ▼                 ▼                        │
│     ┌────────────┐   ┌────────────┐   ┌────────────┐                  │
│     │   MySQL    │   │   Redis    │   │  外部系统   │                  │
│     │            │   │            │   │            │                  │
│     │ • 业务数据 │   │ • 缓存     │   │ • 用量 API │                  │
│     │ • 结算记录 │   │ • 会话     │   │ • 客户接入 │                  │
│     │ • 画像数据 │   │ • 任务队列 │   │   系统     │                  │
│     └────────────┘   └────────────┘   └────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 架构分层说明

| 层级 | 职责 | 技术组件 |
|------|------|----------|
| **前端层** | 用户界面、交互逻辑、状态管理 | Vue 3, Arco Design, Pinia, Vue Router |
| **API 网关层** | 认证鉴权、请求校验、限流、日志 | Sanic Middleware, JWT |
| **业务逻辑层** | 核心业务规则、流程编排 | Sanic Services |
| **任务队列层** | 异步任务、定时调度 | Celery + Redis |
| **数据访问层** | 数据库操作、缓存策略 | Tortoise ORM, Redis |
| **数据存储层** | 持久化存储、缓存、外部集成 | MySQL 8.0+, Redis 7.0+, External APIs |

---

## 技术栈选型

### 前端技术栈

| 技术组件 | 选型 | 版本号 | 选型理由 |
|----------|------|--------|----------|
| **框架** | Vue 3 | 3.3+ | 组合式 API、性能优秀、学习曲线平缓 |
| **UI 组件库** | Arco Design Vue | 2.x | 字节开源，设计精美，60+ 组件，支持主题定制 |
| **状态管理** | Pinia | 2.x | Vue 3 官方推荐，比 Vuex 更简洁，TypeScript 友好 |
| **路由** | Vue Router | 4.x | Vue 3 配套路由，支持动态路由、路由守卫 |
| **HTTP 客户端** | Axios | 1.x | 成熟稳定，支持拦截器、请求取消、自动转换 JSON |
| **构建工具** | Vite | 4.x | 极速冷启动，HMR 热更新，开箱即用 |

### 后端技术栈

| 技术组件 | 选型 | 版本号 | 选型理由 |
|----------|------|--------|----------|
| **框架** | Sanic | 23.x | 异步高性能，支持 WebSocket，类 Flask 语法 |
| **Python 版本** | Python | 3.9+ | 异步语法原生支持，类型提示增强 |
| **ORM** | Tortoise ORM | 0.20+ | 异步 ORM，Django-like 语法，支持 MySQL 8.0+，自动迁移 |
| **数据验证** | Pydantic | 2.x | 高性能数据验证，类型提示，自动文档生成 |
| **任务队列** | Celery | 5.3+ | 分布式任务队列，支持定时任务，Redis Broker |
| **缓存** | Redis | 7.0+ | 高性能 KV 存储，缓存/会话/任务队列/分布式锁 |
| **数据库** | MySQL | 8.0+ | 项目技术栈要求，支持 JSON/窗口函数/CTE |
| **API 文档** | Sanic-OpenAPI | 3.x | 自动生成 Swagger/OpenAPI 文档 |
| **认证** | PyJWT | 2.x | JWT Token 生成验证，支持刷新 Token |

### 开发运维工具

| 技术组件 | 选型 | 用途 |
|----------|------|------|
| **容器化** | Docker + Docker Compose | 本地开发环境、生产部署 |
| **测试框架** | Pytest + pytest-asyncio | 单元测试、集成测试 |
| **代码质量** | Black + Flake8 + MyPy | 代码格式化、静态检查、类型检查 |
| **CI/CD** | GitHub Actions / GitLab CI | 自动化构建、测试、部署 |

---

## 项目结构

### 后端项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Sanic 应用入口
│   ├── config.py                # 配置管理 (开发/测试/生产)
│   ├── extensions.py            # 扩展初始化 (DB, Redis, Celery)
│   │
│   ├── api/                     # API 路由层
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── customer.py      # 客户管理 API
│   │   │   ├── settlement.py    # 结算管理 API
│   │   │   ├── billing.py       # 账单管理 API
│   │   │   ├── analysis.py      # 画像分析 API
│   │   │   └── auth.py          # 认证 API
│   │   └── deps.py              # API 依赖注入
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── settlement_service.py
│   │   ├── billing_service.py
│   │   ├── analysis_service.py
│   │   └── external_api.py      # 外部系统 API 调用
│   │
│   ├── models/                  # 数据模型层 (Tortoise ORM)
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── settlement.py
│   │   ├── billing.py
│   │   └── user.py
│   │
│   ├── schemas/                 # Pydantic 数据验证
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── settlement.py
│   │   └── billing.py
│   │
│   ├── tasks/                   # Celery 任务
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── daily_usage_task.py  # 每日用量采集
│   │   └── monthly_billing_task.py  # 月度账单生成
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   ├── excel.py             # Excel 导入导出
│   │   └── validators.py
│   │
│   └── middleware/              # 中间件
│       ├── __init__.py
│       ├── auth.py
│       └── logging.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_customer.py
│   └── test_settlement.py
│
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── docker-compose.yml
```

### 前端项目结构

```
frontend/
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── settings.js              # 全局配置
│   │
│   ├── api/                     # API 调用
│   │   ├── customer.js
│   │   ├── settlement.js
│   │   └── analysis.js
│   │
│   ├── components/              # 公共组件
│   │   ├── common/              # 通用组件
│   │   │   ├── DataTable.vue
│   │   │   ├── SearchForm.vue
│   │   │   └── Pagination.vue
│   │   └── business/            # 业务组件
│   │       ├── CustomerCard.vue
│   │       └── BillingTable.vue
│   │
│   ├── views/                   # 页面视图
│   │   ├── customer/
│   │   │   ├── List.vue         # 客户列表
│   │   │   ├── Detail.vue       # 客户详情
│   │   │   └── Import.vue       # 数据导入
│   │   ├── settlement/
│   │   │   ├── Billing.vue      # 账单生成
│   │   │   └── Tracking.vue     # 结算跟踪
│   │   └── analysis/
│   │       └── Dashboard.vue    # 管理看板
│   │
│   ├── router/                  # 路由配置
│   │   └── index.js
│   │
│   ├── stores/                  # Pinia 状态管理
│   │   ├── user.js
│   │   └── app.js
│   │
│   ├── styles/                  # 全局样式
│   │   └── index.less
│   │
│   └── utils/                   # 工具函数
│       ├── request.js           # Axios 封装
│       └── auth.js
│
├── public/
├── package.json
├── vite.config.js
└── index.html
```

---

## 数据流设计

### 核心业务流程

#### 1. 客户信息管理流程

```
用户操作 → 前端表单 → API 请求 → 后端校验 → 数据库操作 → 返回结果
   │                                                               │
   └────────────────── 操作日志记录 ◀──────────────────────────────┘
```

**详细步骤：**

1. 用户在前端填写客户信息（18 个字段）
2. 前端表单验证（必填字段、格式校验）
3. 发送 POST/PUT 请求到后端 API
4. 后端进行业务规则校验（如：公司名称唯一性）
5. Tortoise ORM 执行数据库操作
6. 记录操作审计日志
7. 返回操作结果到前端

---

#### 2. Excel 数据导入流程

```
用户上传 Excel → 前端上传 → 后端解析 → 数据校验 → 清洗转换 → 批量入库
                                     │
                                     ▼
                              生成导入报告（成功/失败明细）
```

**详细步骤：**

1. 用户上传 Excel 文件（.xlsx 格式）
2. 后端使用 openpyxl 解析 Excel
3. 数据校验：
   - 必填字段检查
   - 格式校验（日期、数值）
   - 重复检测（公司 ID/名称）
4. 数据清洗：
   - 格式标准化（日期格式统一）
   - 缺失值处理
   - 字典值映射（行业类型、客户等级）
5. 批量插入数据库（事务处理）
6. 生成导入报告（成功条数、失败明细及原因）

---

#### 3. 用量数据采集流程（每日定时）

```
Celery 定时任务 → 调用外部 API → 数据解析 → 数据校验 → 更新客户用量
                      │                                     │
                      ▼                                     ▼
               调用失败重试机制                      异常数据标记人工处理
```

**详细步骤：**

1. Celery 定时任务每日凌晨 2 点触发
2. 调用三方系统 API 获取用量数据
3. 解析 API 响应（JSON 格式）
4. 数据校验：
   - 客户 ID 匹配
   - 用量值合理性检查
   - 日期范围校验
5. 更新客户当月用量数据
6. 记录采集日志（成功/失败）
7. 失败任务进入重试队列（最多 3 次）

---

#### 4. 账单生成流程（月度）

```
Celery 定时任务 → 获取客户列表 → 读取定价规则 → 计算账单金额 → 生成账单记录
                      │              │              │
                      ▼              ▼              ▼
               筛选活跃客户     单层/多层定价    用量 × 单价
                                                        │
                                                        ▼
                                                 发送逾期提醒通知
```

**详细步骤：**

1. Celery 定时任务每月 1 号凌晨触发
2. 获取所有活跃客户列表
3. 读取每个客户的定价规则（单层/多层）
4. 获取客户当月用量数据
5. 计算账单金额：
   - 单层定价：结算金额 = 用量 × 单价
   - 多层定价：结算金额 = Σ(各阶梯用量 × 对应单价)
6. 批量生成账单记录（状态：未结算）
7. 生成基础报表（应收总额、客户分布）

---

#### 5. 收款核销流程

```
用户录入收款 → 后端校验 → 匹配待核销账单 → 用户确认 → 更新账单状态
                              │
                              ▼
                       支持部分核销、合并核销
```

**详细步骤：**

1. 用户在前端录入收款记录（金额、日期、付款方式）
2. 系统自动匹配待核销账单（按客户 + 金额模糊匹配）
3. 用户确认核销对应关系
4. 更新账单状态（未结算 → 已结算）
5. 记录收款流水（防重复）
6. 支持核销撤销（审计日志记录）

---

## 关键技术决策

### ADR-001: ORM 选型 - Tortoise ORM

**决策日期:** 2026-02-24  
**状态:** 已采纳

**背景:** 需要异步 ORM 框架，支持 MySQL 8.0+，与 Sanic 框架集成

**选项对比:**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Tortoise ORM** | 异步、Django-like语法、自动迁移、MySQL原生支持 | 社区规模较小 |
| SQLAlchemy 2.0 | 功能强大、生态成熟 | 异步支持不够原生、学习曲线陡 |
| Peewee | 轻量级、简单易用 | 异步支持有限 |

**决策:** 选择 **Tortoise ORM**

**理由:**
1. 原生异步支持，与 Sanic 框架完美匹配
2. Django-like 语法，团队学习成本低
3. 支持自动迁移（Alembic-like）
4. MySQL 8.0+ 原生支持

---

### ADR-002: 任务队列 - Celery + Redis

**决策日期:** 2026-02-24  
**状态:** 已采纳

**背景:** 需要支持定时任务（每日用量采集、月度账单生成）和异步任务处理

**选项对比:**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Celery + Redis** | 成熟稳定、功能全面、定时任务支持好 | 配置相对复杂 |
| RQ (Redis Queue) | 轻量级、简单易用 | 功能较少、定时任务支持弱 |
| ARQ | 异步原生、轻量级 | 生态较小、文档不完善 |

**决策:** 选择 **Celery 5.3+ + Redis**

**理由:**
1. 工业级任务队列，稳定性有保障
2. 完善的定时任务支持（Celery Beat）
3. Redis Broker 配置简单，性能优秀
4. 支持任务重试、任务链、任务分组等高级特性

---

### ADR-003: 认证方案 - JWT Token

**决策日期:** 2026-02-24  
**状态:** 已采纳

**背景:** 内部运营系统，需要无状态认证，支持权限控制

**选项对比:**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **JWT Token** | 无状态、支持横向扩展、权限灵活 | Token 撤销复杂 |
| Session-Cookie | 实现简单、易于撤销 | 服务器存储压力、不支持横向扩展 |
| OAuth 2.0 | 标准化、支持第三方 | 实现复杂、过度设计 |

**决策:** 选择 **JWT (PyJWT 2.x)**

**理由:**
1. 无状态认证，适合分布式部署
2. Access Token + Refresh Token 双 Token 机制
3. 支持 RBAC 权限控制
4. 与 Sanic 中间件集成简单

**实现方案:**
- Access Token: 有效期 2 小时
- Refresh Token: 有效期 7 天
- Token 存储在请求头：`Authorization: Bearer <token>`
- 权限控制通过中间件实现

---

### ADR-004: 外部 API 集成 - 适配器模式

**决策日期:** 2026-02-24  
**状态:** 已采纳

**背景:** 用量数据采集需调用三方系统 API，当前无 API 文档，未来可能对接多个数据源

**决策:** 采用 **适配器模式 (Adapter Pattern)** 设计外部 API 集成层

**设计要点:**
1. 定义统一的 `ExternalDataSource` 接口
2. 为每个三方系统实现独立适配器
3. 配置化数据源切换
4. 统一错误处理和重试机制

**代码结构:**
```python
# services/external_api.py

class ExternalDataSource(ABC):
    @abstractmethod
    async def fetch_usage(self, customer_id: str, month: str) -> dict:
        pass

class VendorAAdapter(ExternalDataSource):
    async def fetch_usage(self, customer_id: str, month: str) -> dict:
        # 实现 Vendor A 的 API 调用逻辑
        pass

class VendorBAdapter(ExternalDataSource):
    async def fetch_usage(self, customer_id: str, month: str) -> dict:
        # 实现 Vendor B 的 API 调用逻辑
        pass
```

**优势:**
1. 未来新增数据源无需修改核心业务逻辑
2. 便于单元测试（Mock 适配器）
3. 支持运行时数据源切换

---

### ADR-005: 数据库设计 - 审计字段

**决策日期:** 2026-02-24  
**状态:** 已采纳

**背景:** 需要追踪数据变更历史，满足审计要求

**决策:** 所有业务表统一添加审计字段

**审计字段规范:**
```sql
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- 创建时间
updated_at      TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
created_by      VARCHAR(50)                             -- 创建人
updated_by      VARCHAR(50)                             -- 更新人
is_deleted      TINYINT DEFAULT 0                       -- 软删除标记
deleted_at      TIMESTAMP NULL                          -- 删除时间
```

**实现方式:**
- Tortoise ORM 使用 mixin 类统一继承
- 后端中间件自动填充 `updated_by` 字段
- 软删除通过查询条件自动过滤

---

## 实施路线图

### Phase 1: MVP (8-10 周) - 客户信息维护 + 核心结算能力

**技术目标:**
- [ ] 完成项目脚手架搭建
- [ ] 实现数据库设计和迁移
- [ ] 客户信息管理模块（增删改查、Excel 导入）
- [ ] 结算管理模块（定价配置、账单生成、收款核销）
- [ ] 基础权限控制

**里程碑:**
1. Week 2: 技术选型确认、项目脚手架
2. Week 4: 数据库设计完成、核心模型实现
3. Week 6: 客户信息管理模块完成
4. Week 8: 结算管理模块完成
5. Week 10: 集成测试、数据迁移、上线准备

---

### Phase 2: 自动化 (4-6 周) - 提升效率

**技术目标:**
- [ ] 外部 API 适配器实现
- [ ] Celery 定时任务（每日用量采集）
- [ ] 月度账单自动生成
- [ ] 逾期自动提醒
- [ ] 账号状态自动流转

**里程碑:**
1. Week 2: 外部 API 对接完成
2. Week 4: 定时任务实现
3. Week 6: 自动化流程测试、上线

---

### Phase 3: 数据驱动 (4-6 周) - 画像分析

**技术目标:**
- [ ] 客户分层看板
- [ ] 用量趋势分析
- [ ] 流失预警算法
- [ ] 信用评分模型
- [ ] 管理者驾驶舱

---

### Phase 4: 体验优化 (2-4 周)

**技术目标:**
- [ ] 用量可视化（ECharts）
- [ ] 高级筛选和搜索
- [ ] 批量操作优化
- [ ] 自定义报表导出

---

## 风险与缓解

| 风险 | 影响程度 | 概率 | 缓解措施 |
|------|----------|------|----------|
| 外部 API 无文档 | 🔴 高 | 🔴 高 | 预留 2 周沟通时间，设计可配置适配器 |
| 数据迁移质量 | 🔴 高 | 🟡 中 | 提前启动数据清洗，双轨运行验证 |
| 团队 Sanic 经验不足 | 🟡 中 | 🟡 中 | 安排技术培训，引入外部专家支持 |
| 需求范围蔓延 | 🟡 中 | 🟡 中 | 严格遵循优先级，Phase 1 聚焦 MVP |

---

## 下一步行动

### 待完成设计（Phase 2 详细设计）

- [ ] 数据库 ER 图和完整表结构设计
- [ ] API 接口定义（OpenAPI 规范）
- [ ] 前端组件架构设计
- [ ] 部署架构方案（Docker + Docker Compose）
- [ ] 监控和日志方案

### 立即行动

1. **项目初始化** - 使用所选启动模板创建项目结构
2. **确认技术选型** - 本架构文档评审通过
3. **外部 API 沟通** - 获取用量数据 API 文档
4. **数据清洗启动** - 对 1320 条 Excel 数据进行预处理
5. **项目立项** - 确定团队成员和时间表

---

## Project Structure Analysis Results

### Technical Architecture Overview

**Frontend:**
Vue 3 + TypeScript + Pinia + Vue Router + Arco Design Vue + Vite

**Backend:**
Python 3.9+ + Sanic + Tortoise ORM + MySQL 8.0+ + Redis + Celery

**Deployment:**
Docker + Docker Compose + GitHub Actions CI/CD

### Key Project Structure Features

- **前后端分离架构：** 前端使用 Vue 3 + TypeScript，后端使用 Python Sanic，通过 RESTful API 通信
- **模块化设计：** 按业务功能划分（客户管理、结算管理、数据分析等），代码结构清晰
- **分层架构：** 后端采用 API 路由层 → 业务逻辑层 → 数据模型层的分层设计
- **异步任务处理：** 使用 Celery + Redis 处理定时任务和异步操作
- **容器化部署：** 支持 Docker 本地开发和 Docker Compose 生产部署
- **全面的测试覆盖：** 前端使用 Vitest + Vue Test Utils，后端使用 Pytest + pytest-asyncio

### Architecture Boundaries

**API Boundaries:**
- 前端通过 axios 与后端 API 通信，API 端点前缀为 `/api/v1`
- Sanic 服务器暴露 RESTful API，支持 HTTP 方法 GET/POST/PUT/DELETE
- 通过适配器模式与企业 ERP 系统和三方用量数据 API 集成

**Component Boundaries:**
- 前端使用 Vue 3 组件，通过 props/events 通信，遵循单向数据流原则
- 业务组件按功能模块划分，组件间通过路由和状态管理通信
- DataTable、SearchForm、Pagination 等通用组件可在各业务模块复用

**Service Boundaries:**
- 后端业务逻辑按领域划分（客户服务、结算服务等），通过接口通信
- 与 ERP 系统、邮件服务、短信服务集成，使用适配器模式解耦
- Celery 任务队列处理定时任务和异步操作

**Data Boundaries:**
- MySQL 存储核心业务数据（客户信息、价格配置、结算记录等），使用 Tortoise ORM 访问
- Redis 缓存客户基础信息、价格配置和会话数据
- 导入/导出的 Excel/PDF 文件存储在云存储服务（如 AWS S3）
- 通过 API 从第三方系统获取用量数据，使用适配器模式处理

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
- 前端到后端：HTTP/REST API，使用 axios 发送请求
- 后端组件通信：API 调用 → 业务逻辑 → 数据访问 → 数据库操作
- 异步任务通信：Celery 任务队列，使用 Redis 作为 broker
- 状态管理：Pinia 存储全局状态，组件间通过 store 通信

**External Integrations:**
- ERP 系统集成：通过适配器模式与企业 ERP 系统同步客户信息和订单数据
- 邮件服务集成：使用 SMTP 发送报表通知和提醒
- 短信服务集成：使用短信 API 发送逾期提醒
- 云存储集成：使用 AWS S3 或阿里云 OSS 存储文件

**Data Flow:**
1. **客户信息管理流程：** 用户操作 → 前端表单 → API 请求 → 后端校验 → 数据库操作 → 返回结果
2. **Excel 数据导入流程：** 用户上传 → 前端上传 → 后端解析 → 数据校验 → 清洗转换 → 批量入库
3. **用量数据采集流程：** Celery 定时任务 → 调用外部 API → 数据解析 → 数据校验 → 更新客户用量
4. **账单生成流程：** Celery 定时任务 → 获取客户列表 → 读取定价规则 → 计算账单金额 → 生成账单记录
5. **收款核销流程：** 用户录入收款 → 后端校验 → 匹配待核销账单 → 用户确认 → 更新账单状态

---

## 附录

### 术语表

| 术语 | 说明 |
|------|------|
| **ERP** | 企业资源计划系统，客户使用的业务系统 |
| **单层定价** | 固定单价 × 用量的计费模式 |
| **多层定价** | 阶梯定价，不同用量区间不同单价 |
| **收款核销** | 收款记录与账单的匹配确认过程 |

### 参考资料

- [Sanic 官方文档](https://sanic.dev/)
- [Tortoise ORM 官方文档](https://tortoise.github.io/)
- [Vue 3 官方文档](https://vuejs.org/)
- [Arco Design Vue 文档](https://arco.design/vue/)
- [Celery 官方文档](https://docs.celeryq.dev/)
