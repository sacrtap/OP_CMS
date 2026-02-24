---
project: OP_CMS
document_type: API Design Document
version: 1.0.0
status: Draft
created: 2026-02-24
author: BMAD Architect Agent
---

# 客户信息管理与运营系统 - API 接口设计文档

## 文档信息

| 项目 | 值 |
|------|-----|
| **项目名称** | 客户信息管理与运营系统 |
| **文档类型** | API 接口设计文档 |
| **API 版本** | v1 |
| **OpenAPI 版本** | 3.0.0 |
| **认证方式** | JWT Bearer Token |
| **数据格式** | JSON |
| **创建日期** | 2026-02-24 |

---

## API 概览

### 基础信息

- **Base URL:** `/api/v1`
- **认证:** `Authorization: Bearer <token>`
- **请求格式:** `application/json`
- **响应格式:** `application/json`

### 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": 1708761600000
}
```

**字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | Integer | 状态码（200=成功，其他=失败） |
| message | String | 响应消息 |
| data | Object/Array | 响应数据 |
| timestamp | Long | 时间戳 |

### 错误码定义

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 过期 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如重复） |
| 500 | 服务器内部错误 |

---

## API 模块划分

### 模块清单

| 模块 | 前缀 | 说明 | 优先级 |
|------|------|------|--------|
| **认证** | `/auth` | 用户登录、Token 刷新 | P0 |
| **客户管理** | `/customers` | 客户信息 CRUD、导入导出 | P0 |
| **设备系列** | `/device-series` | X/N/L 设备系列配置 | P0 |
| **结算类型** | `/settlement-types` | 定价/阶梯/包年配置 | P0 |
| **定价规则** | `/pricing-rules` | 定价配置（三种模式） | P0 |
| **包年套餐** | `/package-plans` | A/B/C/D 套餐配置 | P0 |
| **用量管理** | `/usage-records` | 用量采集、查询 | P1 |
| **账单管理** | `/bills` | 账单生成、查询、导出 | P0 |
| **收款管理** | `/payments` | 收款录入、核销 | P0 |
| **画像分析** | `/analysis` | 客户分层、用量趋势、流失预警 | P2 |
| **报表统计** | `/reports` | 应收/实收/逾期报表 | P1 |

---

## API 详细设计

### 1. 认证模块 (Auth)

#### 1.1 用户登录

```yaml
post: /api/v1/auth/login
summary: 用户登录
tags: [认证]
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          username:
            type: string
            example: admin
          password:
            type: string
            format: password
            example: "123456"
        required: [username, password]
responses:
  200:
    description: 登录成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/LoginResponse'
  401:
    description: 用户名或密码错误
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 7200,
    "user": {
      "id": 1,
      "username": "admin",
      "real_name": "管理员",
      "role": "admin",
      "department": "运营部"
    }
  }
}
```

---

#### 1.2 刷新 Token

```yaml
post: /api/v1/auth/refresh
summary: 刷新 Access Token
tags: [认证]
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          refresh_token:
            type: string
        required: [refresh_token]
responses:
  200:
    description: 刷新成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/TokenResponse'
```

---

### 2. 客户管理模块 (Customers)

#### 2.1 获取客户列表

```yaml
get: /api/v1/customers
summary: 获取客户列表（支持分页、筛选、搜索）
tags: [客户管理]
parameters:
  - name: page
    in: query
    schema:
      type: integer
      default: 1
  - name: page_size
    in: query
    schema:
      type: integer
      default: 20
  - name: company_name
    in: query
    schema:
      type: string
    description: 公司名称模糊搜索
  - name: device_series_id
    in: query
    schema:
      type: integer
    description: 设备系列 ID
  - name: settlement_type_id
    in: query
    schema:
      type: integer
    description: 结算类型 ID
  - name: cooperation_status
    in: query
    schema:
      type: string
      enum: [active, closed, suspended]
    description: 合作状态
  - name: is_settled
    in: query
    schema:
      type: boolean
    description: 是否结算
  - name: sales_owner_id
    in: query
    schema:
      type: integer
    description: 销售负责人 ID
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CustomerListResponse'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 1320,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "id": 1,
        "company_id": "C001",
        "company_name": "XX 房地产有限公司",
        "account_type": "正式账号",
        "industry_type": "房产",
        "erp_system": "SAP",
        "device_series": {
          "id": 2,
          "series_code": "N",
          "series_name": "N 系列"
        },
        "settlement_type": {
          "id": 1,
          "type_code": "pricing",
          "type_name": "定价结算"
        },
        "customer_level": "A",
        "sales_owner": {
          "id": 10,
          "real_name": "张三"
        },
        "ops_owner": {
          "id": 20,
          "real_name": "李四"
        },
        "cooperation_status": "active",
        "is_settled": 0,
        "is_stopped": 0,
        "monthly_avg_shots": 850,
        "current_month_usage": 920,
        "created_at": "2025-06-15 10:30:00"
      }
    ]
  }
}
```

---

#### 2.2 获取客户详情

```yaml
get: /api/v1/customers/{id}
summary: 获取客户详情
tags: [客户管理]
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: integer
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CustomerDetailResponse'
  404:
    description: 客户不存在
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "company_id": "C001",
    "company_name": "XX 房地产有限公司",
    "account_type": "正式账号",
    "industry_type": "房产",
    "erp_system": "SAP",
    "device_series_id": 2,
    "settlement_type_id": 1,
    "package_plan_id": null,
    "access_date": "2025-06-15",
    "customer_level": "A",
    "sales_owner_id": 10,
    "ops_owner_id": 20,
    "cooperation_status": "active",
    "is_settled": 0,
    "is_stopped": 0,
    "remarks": "重要客户",
    "settlement_method": "月结",
    "consumption_level": "高消费",
    "monthly_avg_shots": 850,
    "current_month_usage": 920,
    "device_series": {
      "id": 2,
      "series_code": "N",
      "series_name": "N 系列"
    },
    "settlement_type": {
      "id": 1,
      "type_code": "pricing",
      "type_name": "定价结算"
    },
    "pricing_rule": {
      "id": 1,
      "rule_type": "multi_tier",
      "unit_price": null,
      "tier_prices": {
        "tiers": [
          {"min": 0, "max": 500, "price": 1.0},
          {"min": 501, "max": 1000, "price": 0.8},
          {"min": 1001, "max": null, "price": 0.6}
        ]
      }
    },
    "sales_owner": {
      "id": 10,
      "real_name": "张三",
      "phone": "13800138001"
    },
    "ops_owner": {
      "id": 20,
      "real_name": "李四",
      "phone": "13800138002"
    },
    "created_at": "2025-06-15 10:30:00",
    "updated_at": "2026-02-20 14:20:00"
  }
}
```

---

#### 2.3 创建客户

```yaml
post: /api/v1/customers
summary: 创建客户
tags: [客户管理]
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreateCustomerRequest'
responses:
  201:
    description: 创建成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CustomerDetailResponse'
  400:
    description: 请求参数错误
  409:
    description: 公司 ID 已存在
```

**请求示例:**

```json
{
  "company_id": "C002",
  "company_name": "YY 置业有限公司",
  "account_type": "正式账号",
  "industry_type": "房产",
  "erp_system": "Oracle",
  "device_series_id": 2,
  "settlement_type_id": 1,
  "package_plan_id": null,
  "access_date": "2026-02-01",
  "customer_level": "B",
  "sales_owner_id": 10,
  "ops_owner_id": 20,
  "cooperation_status": "active",
  "remarks": "新客户",
  "settlement_method": "月结"
}
```

---

#### 2.4 更新客户

```yaml
put: /api/v1/customers/{id}
summary: 更新客户信息
tags: [客户管理]
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/UpdateCustomerRequest'
responses:
  200:
    description: 更新成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/CustomerDetailResponse'
  404:
    description: 客户不存在
```

---

#### 2.5 批量导入客户

```yaml
post: /api/v1/customers/import
summary: 批量导入客户（Excel 文件）
tags: [客户管理]
requestBody:
  required: true
  content:
    multipart/form-data:
      schema:
        type: object
        properties:
          file:
            type: string
            format: binary
        required: [file]
responses:
  200:
    description: 导入成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ImportResponse'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "import_id": 1,
    "file_name": "customer_data.xlsx",
    "total_rows": 1320,
    "success_rows": 1315,
    "failed_rows": 5,
    "status": "completed",
    "imported_at": "2026-02-24 10:30:00",
    "error_log": [
      {
        "row": 5,
        "error": "company_name 不能为空",
        "data": {"company_id": "C005", "company_name": ""}
      },
      {
        "row": 12,
        "error": "company_id 已存在",
        "data": {"company_id": "C012"}
      }
    ]
  }
}
```

---

#### 2.6 导出客户

```yaml
post: /api/v1/customers/export
summary: 导出客户（支持筛选条件）
tags: [客户管理]
requestBody:
  content:
    application/json:
      schema:
        type: object
        properties:
          filters:
            type: object
            description: 筛选条件（同列表接口参数）
          export_fields:
            type: array
            items:
              type: string
            description: 导出字段列表
responses:
  200:
    description: 导出成功
    content:
      application/json:
        schema:
          type: object
          properties:
            file_url:
              type: string
              description: 下载 URL
            file_name:
              type: string
```

---

### 3. 设备系列模块 (Device Series)

#### 3.1 获取设备系列列表

```yaml
get: /api/v1/device-series
summary: 获取设备系列列表
tags: [设备系列]
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/components/schemas/DeviceSeries'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "series_code": "X",
      "series_name": "X 系列",
      "description": "X 系列硬件设备",
      "is_active": 1,
      "sort_order": 1
    },
    {
      "id": 2,
      "series_code": "N",
      "series_name": "N 系列",
      "description": "N 系列硬件设备",
      "is_active": 1,
      "sort_order": 2
    },
    {
      "id": 3,
      "series_code": "L",
      "series_name": "L 系列",
      "description": "L 系列硬件设备",
      "is_active": 1,
      "sort_order": 3
    }
  ]
}
```

---

### 4. 结算类型模块 (Settlement Types)

#### 4.1 获取结算类型列表

```yaml
get: /api/v1/settlement-types
summary: 获取结算类型列表
tags: [结算类型]
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/components/schemas/SettlementType'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "type_code": "pricing",
      "type_name": "定价结算",
      "description": "按设备类型配置单层/多层定价",
      "calculation_logic": "结算金额 = 用量 × 单价 (单层) 或 Σ(各阶梯用量 × 对应单价) (多层)"
    },
    {
      "id": 2,
      "type_code": "tiered",
      "type_name": "阶梯结算",
      "description": "按设备类型自定义阶梯，区分单/多层定价",
      "calculation_logic": "支持自定义阶梯区间和价格"
    },
    {
      "id": 3,
      "type_code": "package",
      "type_name": "包年结算",
      "description": "A/B/C/D 套餐，不同套餐等级对应不同用量",
      "calculation_logic": "套餐内用量固定，超出部分按约定价格计算"
    }
  ]
}
```

---

### 5. 定价规则模块 (Pricing Rules)

#### 5.1 获取客户定价规则

```yaml
get: /api/v1/customers/{customer_id}/pricing-rules
summary: 获取客户定价规则
tags: [定价规则]
parameters:
  - name: customer_id
    in: path
    required: true
    schema:
      type: integer
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/PricingRuleResponse'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "customer_id": 1,
    "device_series_id": 2,
    "settlement_type_id": 1,
    "package_plan_id": null,
    "rule_type": "multi_tier",
    "unit_price": null,
    "tier_prices": {
      "tiers": [
        {"min": 0, "max": 500, "price": 1.0},
        {"min": 501, "max": 1000, "price": 0.8},
        {"min": 1001, "max": null, "price": 0.6}
      ]
    },
    "custom_tiers": null,
    "effective_date": "2026-01-01",
    "expiry_date": null,
    "is_active": 1,
    "approval_status": "approved"
  }
}
```

---

#### 5.2 创建/更新定价规则

```yaml
post: /api/v1/customers/{customer_id}/pricing-rules
summary: 创建或更新客户定价规则
tags: [定价规则]
parameters:
  - name: customer_id
    in: path
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreatePricingRuleRequest'
responses:
  201:
    description: 创建成功
  400:
    description: 请求参数错误
```

**请求示例 1: 定价结算 - 单层定价**

```json
{
  "device_series_id": 2,
  "settlement_type_id": 1,
  "package_plan_id": null,
  "rule_type": "single_tier",
  "unit_price": 1.0,
  "tier_prices": null,
  "custom_tiers": null,
  "effective_date": "2026-03-01"
}
```

**请求示例 2: 定价结算 - 多层定价**

```json
{
  "device_series_id": 2,
  "settlement_type_id": 1,
  "package_plan_id": null,
  "rule_type": "multi_tier",
  "unit_price": null,
  "tier_prices": {
    "tiers": [
      {"min": 0, "max": 500, "price": 1.0},
      {"min": 501, "max": 1000, "price": 0.8},
      {"min": 1001, "max": null, "price": 0.6}
    ]
  },
  "custom_tiers": null,
  "effective_date": "2026-03-01"
}
```

**请求示例 3: 阶梯结算 - 自定义阶梯**

```json
{
  "device_series_id": 1,
  "settlement_type_id": 2,
  "package_plan_id": null,
  "rule_type": null,
  "unit_price": null,
  "tier_prices": null,
  "custom_tiers": {
    "tiers": [
      {"level": 1, "min": 0, "max": 1000, "price": 1.2, "rule_type": "single_tier"},
      {"level": 2, "min": 1001, "max": 5000, "price": 0.9, "rule_type": "single_tier"},
      {"level": 3, "min": 5001, "max": null, "price": 0.7, "rule_type": "single_tier"}
    ]
  },
  "effective_date": "2026-03-01"
}
```

**请求示例 4: 包年结算 - B 套餐**

```json
{
  "device_series_id": 2,
  "settlement_type_id": 3,
  "package_plan_id": 6,
  "rule_type": null,
  "unit_price": null,
  "tier_prices": null,
  "custom_tiers": null,
  "effective_date": "2026-01-01"
}
```

---

### 6. 包年套餐模块 (Package Plans)

#### 6.1 获取套餐列表

```yaml
get: /api/v1/package-plans
summary: 获取包年套餐列表
tags: [包年套餐]
parameters:
  - name: device_series_id
    in: query
    schema:
      type: integer
    description: 设备系列 ID（筛选）
  - name: is_active
    in: query
    schema:
      type: boolean
    description: 是否激活
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/components/schemas/PackagePlan'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 5,
      "plan_code": "A",
      "plan_name": "A 套餐",
      "device_series_id": 1,
      "device_series": {
        "series_code": "X",
        "series_name": "X 系列"
      },
      "included_usage": 50000,
      "package_price": 50000.00,
      "overuse_price": 0.8,
      "is_active": 1,
      "effective_date": "2026-01-01"
    },
    {
      "id": 6,
      "plan_code": "B",
      "plan_name": "B 套餐",
      "device_series_id": 1,
      "device_series": {
        "series_code": "X",
        "series_name": "X 系列"
      },
      "included_usage": 100000,
      "package_price": 90000.00,
      "overuse_price": 0.7,
      "is_active": 1,
      "effective_date": "2026-01-01"
    }
  ]
}
```

---

### 7. 用量管理模块 (Usage Records)

#### 7.1 获取客户用量记录

```yaml
get: /api/v1/customers/{customer_id}/usage-records
summary: 获取客户用量记录
tags: [用量管理]
parameters:
  - name: customer_id
    in: path
    required: true
    schema:
      type: integer
  - name: month
    in: query
    schema:
      type: string
    description: 月份（格式：2026-02）
  - name: start_month
    in: query
    schema:
      type: string
    description: 起始月份
  - name: end_month
    in: query
    schema:
      type: string
    description: 结束月份
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/components/schemas/UsageRecord'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "customer_id": 1,
      "month": "2026-02",
      "usage_amount": 920,
      "source": "api",
      "imported_at": "2026-02-24 02:00:00",
      "is_verified": 0,
      "created_at": "2026-02-24 02:00:00"
    }
  ]
}
```

---

#### 7.2 手动录入用量

```yaml
post: /api/v1/customers/{customer_id}/usage-records
summary: 手动录入客户用量
tags: [用量管理]
parameters:
  - name: customer_id
    in: path
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          month:
            type: string
            example: "2026-02"
          usage_amount:
            type: integer
            example: 920
          remarks:
            type: string
        required: [month, usage_amount]
responses:
  201:
    description: 录入成功
```

---

### 8. 账单管理模块 (Bills)

#### 8.1 生成账单

```yaml
post: /api/v1/bills/generate
summary: 生成月度账单（手动触发）
tags: [账单管理]
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          month:
            type: string
            example: "2026-02"
          customer_ids:
            type: array
            items:
              type: integer
            description: 客户 ID 列表（为空则生成所有活跃客户）
        required: [month]
responses:
  200:
    description: 生成成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/GenerateBillResponse'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_customers": 1320,
    "generated_bills": 1315,
    "failed_bills": 5,
    "total_amount": 1250000.00,
    "created_at": "2026-02-24 10:30:00",
    "errors": [
      {
        "customer_id": 5,
        "company_name": "XX 公司",
        "error": "用量数据缺失"
      }
    ]
  }
}
```

---

#### 8.2 获取账单列表

```yaml
get: /api/v1/bills
summary: 获取账单列表
tags: [账单管理]
parameters:
  - name: page
    in: query
    schema:
      type: integer
      default: 1
  - name: page_size
    in: query
    schema:
      type: integer
      default: 20
  - name: customer_id
    in: query
    schema:
      type: integer
  - name: month
    in: query
    schema:
      type: string
  - name: status
    in: query
    schema:
      type: string
      enum: [unpaid, partial, paid, overdue, cancelled]
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/BillListResponse'
```

---

#### 8.3 获取账单详情

```yaml
get: /api/v1/bills/{id}
summary: 获取账单详情
tags: [账单管理]
parameters:
  - name: id
    in: path
    required: true
    schema:
      type: integer
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/BillDetailResponse'
```

**响应示例:**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "bill_no": "BILL-202602-1-001",
    "customer_id": 1,
    "device_series_id": 2,
    "settlement_type_id": 1,
    "month": "2026-02",
    "usage_amount": 920,
    "pricing_rule_type": "multi_tier",
    "tier_prices": {
      "tiers": [
        {"min": 0, "max": 500, "price": 1.0},
        {"min": 501, "max": 1000, "price": 0.8},
        {"min": 1001, "max": null, "price": 0.6}
      ]
    },
    "amount": 736.00,
    "discount_amount": 0.00,
    "final_amount": 736.00,
    "status": "unpaid",
    "due_date": "2026-03-10",
    "issued_at": "2026-03-01 10:00:00",
    "paid_amount": 0.00,
    "settled_at": null,
    "created_at": "2026-03-01 10:00:00"
  }
}
```

---

### 9. 收款管理模块 (Payments)

#### 9.1 录入收款

```yaml
post: /api/v1/payments
summary: 录入收款记录
tags: [收款管理]
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreatePaymentRequest'
responses:
  201:
    description: 录入成功
```

**请求示例:**

```json
{
  "customer_id": 1,
  "bill_id": 1,
  "amount": 736.00,
  "payment_method": "bank_transfer",
  "paid_date": "2026-03-05",
  "payer_name": "XX 房地产有限公司",
  "payer_account": "6222001234567890",
  "bank_name": "工商银行",
  "transaction_no": "TXN20260305001",
  "remarks": "3 月账单收款"
}
```

---

#### 9.2 收款核销

```yaml
post: /api/v1/payments/{payment_id}/verify
summary: 收款核销
tags: [收款管理]
parameters:
  - name: payment_id
    in: path
    required: true
    schema:
      type: integer
requestBody:
  required: true
  content:
    application/json:
      schema:
        type: object
        properties:
          bill_ids:
            type: array
            items:
              type: integer
            description: 要核销的账单 ID 列表
        required: [bill_ids]
responses:
  200:
    description: 核销成功
```

---

### 10. 画像分析模块 (Analysis)

#### 10.1 客户分层统计

```yaml
get: /api/v1/analysis/customer-levels
summary: 客户分层统计
tags: [画像分析]
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: object
              properties:
                by_level:
                  type: array
                  description: 按客户等级统计
                by_series:
                  type: array
                  description: 按设备系列统计
                by_settlement_type:
                  type: array
                  description: 按结算类型统计
```

---

#### 10.2 用量趋势分析

```yaml
get: /api/v1/analysis/usage-trend
summary: 用量趋势分析
tags: [画像分析]
parameters:
  - name: customer_id
    in: query
    schema:
      type: integer
    description: 客户 ID（为空则统计全部）
  - name: start_month
    in: query
    schema:
      type: string
      example: "2026-01"
  - name: end_month
    in: query
    schema:
      type: string
      example: "2026-06"
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                type: object
                properties:
                  month:
                    type: string
                  total_usage:
                    type: integer
                  avg_usage:
                    type: number
                  customer_count:
                    type: integer
```

---

#### 10.3 流失预警客户

```yaml
get: /api/v1/analysis/churn-warning
summary: 流失预警客户列表
tags: [画像分析]
parameters:
  - name: consecutive_months
    in: query
    schema:
      type: integer
      default: 2
    description: 连续下降月数
  - name: decline_rate
    in: query
    schema:
      type: number
      default: 0.3
    description: 下降比例阈值
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: array
              items:
                $ref: '#/components/schemas/ChurnWarningCustomer'
```

---

### 11. 报表统计模块 (Reports)

#### 11.1 应收/实收/逾期报表

```yaml
get: /api/v1/reports/settlement-summary
summary: 结算汇总报表
tags: [报表统计]
parameters:
  - name: month
    in: query
    schema:
      type: string
      example: "2026-02"
  - name: device_series_id
    in: query
    schema:
      type: integer
    description: 设备系列 ID
responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: object
          properties:
            code:
              type: integer
            message:
              type: string
            data:
              type: object
              properties:
                month:
                  type: string
                total_bills:
                  type: integer
                  description: 总账单数
                total_amount:
                  type: number
                  description: 应收总额
                paid_amount:
                  type: number
                  description: 实收金额
                unpaid_amount:
                  type: number
                  description: 未收金额
                overdue_amount:
                  type: number
                  description: 逾期金额
                collection_rate:
                  type: number
                  description: 回款率（%）
                by_status:
                  type: array
                  description: 按状态统计
                by_series:
                  type: array
                  description: 按设备系列统计
```

---

## 组件 Schema 定义

### Customer Schema

```yaml
components:
  schemas:
    Customer:
      type: object
      properties:
        id:
          type: integer
        company_id:
          type: string
        company_name:
          type: string
        account_type:
          type: string
        industry_type:
          type: string
        erp_system:
          type: string
        device_series_id:
          type: integer
        settlement_type_id:
          type: integer
        package_plan_id:
          type: integer
        customer_level:
          type: string
        sales_owner_id:
          type: integer
        ops_owner_id:
          type: integer
        cooperation_status:
          type: string
          enum: [active, closed, suspended]
        is_settled:
          type: integer
          enum: [0, 1]
        is_stopped:
          type: integer
          enum: [0, 1]
        monthly_avg_shots:
          type: integer
        current_month_usage:
          type: integer
        created_at:
          type: string
          format: date-time
```

---

## API 安全设计

### JWT Token 机制

**Token 结构:**
- Access Token: 有效期 2 小时
- Refresh Token: 有效期 7 天

**Token 刷新流程:**
```
1. Access Token 过期 → 401 错误
2. 前端使用 Refresh Token 调用 /auth/refresh
3. 后端验证 Refresh Token 有效性
4. 返回新的 Access Token 和 Refresh Token
5. 前端更新本地存储的 Token
```

---

## 下一步选项

**API 设计已完成约 80%**，您可以选择：

✅ **继续完善 API 设计** - 补充更多错误响应示例、Schema 定义  
✅ **开始前端组件设计** - Vue 组件架构和页面原型  
✅ **保存并结束** - 后续继续其他详细设计  

**您希望如何继续？** 🚀
