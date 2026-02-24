---
project: OP_CMS
document_type: Frontend Component Design Document
version: 1.0.0
status: Draft
created: 2026-02-24
author: BMAD Architect Agent
---

# 客户信息管理与运营系统 - 前端组件设计文档

## 文档信息

| 项目 | 值 |
|------|-----|
| **项目名称** | 客户信息管理与运营系统 |
| **文档类型** | 前端组件设计文档 |
| **技术栈** | Vue 3.3+ + Arco Design Vue 2.x |
| **状态管理** | Pinia 2.x |
| **路由** | Vue Router 4.x |
| **创建日期** | 2026-02-24 |

---

## 前端架构概览

### 技术选型

| 技术组件 | 选型 | 说明 |
|----------|------|------|
| **框架** | Vue 3.3+ | 组合式 API (Composition API) |
| **UI 组件库** | Arco Design Vue 2.x | 字节开源，60+ 组件 |
| **状态管理** | Pinia 2.x | Vue 3 官方推荐 |
| **路由** | Vue Router 4.x | 支持动态路由 |
| **HTTP 客户端** | Axios 1.x | 拦截器、请求取消 |
| **构建工具** | Vite 4.x | 极速开发体验 |
| **图表库** | ECharts 5.x | 数据可视化 |

---

## 核心页面清单

| 页面 | 路径 | 功能 | 优先级 |
|------|------|------|--------|
| **登录页** | `/login` | 用户登录 | P0 |
| **管理驾驶舱** | `/dashboard` | 核心数据概览、快捷入口 | P0 |
| **客户列表** | `/customer/list` | 客户管理、搜索、筛选 | P0 |
| **客户详情** | `/customer/detail/:id` | 客户详情、定价配置、用量历史 | P0 |
| **数据导入** | `/customer/import` | Excel 批量导入 | P0 |
| **账单生成** | `/settlement/bill-generate` | 月度账单生成 | P0 |
| **账单列表** | `/settlement/bill-list` | 账单查询、导出 | P0 |
| **收款录入** | `/settlement/payment` | 收款核销 | P0 |
| **客户分层分析** | `/analysis/customer-level` | 客户分层统计 | P2 |
| **用量趋势分析** | `/analysis/usage-trend` | 用量趋势图表 | P2 |
| **流失预警** | `/analysis/churn-warning` | 流失客户预警 | P2 |
| **结算报表** | `/report/settlement` | 应收/实收/逾期报表 | P1 |

---

## 核心组件设计

### 1. 定价配置器 (PricingConfig)

**功能:** 支持三种结算模式的定价配置

**核心逻辑:**
- 根据结算类型动态显示不同配置表单
- 定价结算：单层/多层定价配置
- 阶梯结算：自定义阶梯配置
- 包年结算：套餐选择

### 2. 数据表格组件 (DataTable)

**功能:** 封装 Arco Table，统一表格样式和行为

**特性:**
- 自动分页
- 排序支持
- 列显示/隐藏配置
- 批量操作工具栏

### 3. 搜索表单组件 (SearchForm)

**功能:** 通用搜索表单，支持动态字段配置

**特性:**
- 字段类型：input/select/date/cascader
- 展开/收起更多筛选
- 保存筛选条件为常用方案

### 4. 用量趋势图 (UsageTrendChart)

**功能:** ECharts 图表展示用量趋势

**图表类型:** 折线图 + 柱状图混合

---

## 状态管理设计

### Stores 清单

| Store | 职责 | 核心 State |
|-------|------|-----------|
| **user** | 用户认证 | token, user, roles |
| **app** | 应用全局 | theme, collapsed, loading |
| **customer** | 客户缓存 | customerList, searchParams |

---

## 下一步选项

前端组件设计已完成核心框架。

**请选择:**

✅ **保存并结束** - 文档已保存，后续继续其他详细设计  
✅ **开始业务逻辑设计** - 三种结算模式的计算逻辑实现  
✅ **开始部署架构设计** - Docker 容器化部署方案  

**您希望如何继续？** 🚀
