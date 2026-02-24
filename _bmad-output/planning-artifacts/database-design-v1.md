---
project: OP_CMS
document_type: Database Design Document
version: 1.0.0
status: Approved
created: 2026-02-24
author: BMAD Architect Agent
---

# 客户信息管理与运营系统 - 数据库设计文档

## 文档信息

| 项目 | 值 |
|------|-----|
| **项目名称** | 客户信息管理与运营系统 |
| **文档类型** | 数据库设计文档 |
| **版本号** | 1.0.0 |
| **状态** | 已批准 |
| **创建日期** | 2026-02-24 |
| **数据库** | MySQL 8.0+ |

---

## 定价模式说明

### 三种结算模式

| 结算模式 | 代码 | 说明 | 适用场景 |
|----------|------|------|----------|
| **定价结算** | pricing | 按设备类型配置单层/多层定价 | 标准定价，简单快速 |
| **阶梯结算** | tiered | 按设备类型自定义阶梯，区分单/多层定价 | 复杂阶梯定价策略 |
| **包年结算** | package | A/B/C/D 套餐，不同套餐等级对应不同用量 | 年费套餐制客户 |

### 设备系列分类

| 系列代码 | 系列名称 | 说明 |
|----------|----------|------|
| **X** | X 系列 | X 系列硬件设备 |
| **N** | N 系列 | N 系列硬件设备 |
| **L** | L 系列 | L 系列硬件设备 |

---

## 数据库 ER 图

```
┌─────────────────┐       ┌─────────────────┐
│  device_series  │       │ settlement_type │
│─────────────────│       │─────────────────│
│ id              │       │ id              │
│ series_code     │       │ type_code       │
│ series_name     │       │ type_name       │
│ is_active       │       │ is_active       │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ 1:N                     │ 1:N
         │                         │
         ▼                         ▼
┌─────────────────────────────────────────────────┐
│              pricing_rule                        │
│─────────────────────────────────────────────────│
│ id                                              │
│ customer_id                                     │
│ device_series_id  ──────────────────────────────┤
│ settlement_type_id ─────────────────────────────┤
│ package_plan_id   ───────┐                      │
│ rule_type                                       │
│ unit_price                                      │
│ tier_prices                                     │
│ custom_tiers                                    │
└─────────────────────────────────────────────────┘
         │
         │ 1:1
         │
         ▼
┌─────────────────┐       ┌─────────────────┐
│    customer     │       │   package_plan  │
│─────────────────│       │─────────────────│
│ id              │       │ id              │
│ company_name    │       │ plan_code       │
│ device_series_id│───┐   │ package_price   │
│ settlement_type_│───┘   │ included_usage  │
│ package_plan_id │───────┤ overuse_price   │
└─────────────────┘       └─────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐       ┌─────────────────┐
│  usage_record   │       │      bill       │
│─────────────────│       │─────────────────│
│ id              │       │ id              │
│ customer_id     │       │ customer_id     │
│ month           │       │ device_series_id│
│ usage_amount    │       │ settlement_type │
│ source          │       │ amount          │
└─────────────────┘       │ status          │
                          │ paid_amount     │
                          └─────────────────┘
                                 │
                                 │ 1:N
                                 │
                                 ▼
                          ┌─────────────────┐
                          │    payment      │
                          │─────────────────│
                          │ id              │
                          │ customer_id     │
                          │ bill_id         │
                          │ amount          │
                          │ payment_method  │
                          └─────────────────┘
```

---

## 核心表结构设计

### 1. device_series (设备系列表)

```sql
CREATE TABLE `device_series` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `series_code` VARCHAR(10) NOT NULL COMMENT '系列代码：X/N/L',
  `series_name` VARCHAR(50) NOT NULL COMMENT '系列名称',
  `description` VARCHAR(200) DEFAULT NULL COMMENT '描述',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否激活',
  `sort_order` INT DEFAULT 0 COMMENT '排序顺序',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_series_code` (`series_code`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备系列表';

-- 初始化数据
INSERT INTO `device_series` (series_code, series_name, description, sort_order) VALUES
('X', 'X 系列', 'X 系列硬件设备', 1),
('N', 'N 系列', 'N 系列硬件设备', 2),
('L', 'L 系列', 'L 系列硬件设备', 3);
```

---

### 2. settlement_type (结算类型表)

```sql
CREATE TABLE `settlement_type` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `type_code` VARCHAR(20) NOT NULL COMMENT '类型代码：pricing/tiered/package',
  `type_name` VARCHAR(50) NOT NULL COMMENT '类型名称',
  `description` VARCHAR(200) DEFAULT NULL COMMENT '描述',
  `calculation_logic` TEXT DEFAULT NULL COMMENT '计算逻辑说明',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否激活',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_type_code` (`type_code`),
  KEY `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='结算类型表';

-- 初始化数据
INSERT INTO `settlement_type` (type_code, type_name, description, calculation_logic) VALUES
('pricing', '定价结算', '按设备类型配置单层/多层定价', '结算金额 = 用量 × 单价 (单层) 或 Σ(各阶梯用量 × 对应单价) (多层)'),
('tiered', '阶梯结算', '按设备类型自定义阶梯，区分单/多层定价', '支持自定义阶梯区间和价格'),
('package', '包年结算', 'A/B/C/D 套餐，不同套餐等级对应不同用量', '套餐内用量固定，超出部分按约定价格计算');
```

---

### 3. package_plan (包年套餐表)

```sql
CREATE TABLE `package_plan` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `plan_code` VARCHAR(20) NOT NULL COMMENT '套餐代码：A/B/C/D',
  `plan_name` VARCHAR(50) NOT NULL COMMENT '套餐名称',
  `device_series_id` BIGINT UNSIGNED NOT NULL COMMENT '设备系列 ID',
  `included_usage` INT NOT NULL DEFAULT 0 COMMENT '套餐包含用量 (张)',
  `package_price` DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '套餐价格 (元/年)',
  `overuse_price` DECIMAL(10,4) DEFAULT NULL COMMENT '超出用量单价 (元/张)',
  `monthly_limit` INT DEFAULT NULL COMMENT '月度用量上限 (可选)',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否激活',
  `effective_date` DATE NOT NULL COMMENT '生效日期',
  `expiry_date` DATE DEFAULT NULL COMMENT '失效日期',
  `remarks` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
  `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '更新人',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_plan_code_series` (`plan_code`, `device_series_id`),
  KEY `idx_device_series_id` (`device_series_id`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `fk_package_device_series` FOREIGN KEY (`device_series_id`) REFERENCES `device_series` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='包年套餐表';

-- 示例数据 (X 系列)
INSERT INTO `package_plan` (plan_code, plan_name, device_series_id, included_usage, package_price, overuse_price, effective_date) VALUES
('A', 'A 套餐', 1, 50000, 50000.00, 0.8, '2026-01-01'),
('B', 'B 套餐', 1, 100000, 90000.00, 0.7, '2026-01-01'),
('C', 'C 套餐', 1, 200000, 170000.00, 0.6, '2026-01-01'),
('D', 'D 套餐', 1, 500000, 400000.00, 0.5, '2026-01-01');
```

---

### 4. customer (客户基础信息表)

```sql
CREATE TABLE `customer` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `company_id` VARCHAR(50) NOT NULL COMMENT '公司 ID (外部系统)',
  `company_name` VARCHAR(200) NOT NULL COMMENT '公司名称',
  `account_type` VARCHAR(50) DEFAULT NULL COMMENT '账号类型',
  `industry_type` VARCHAR(50) DEFAULT NULL COMMENT '行业类型',
  `erp_system` VARCHAR(50) DEFAULT NULL COMMENT '所属 ERP 系统',
  `device_series_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '设备系列 ID',
  `settlement_type_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '结算类型 ID',
  `package_plan_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '套餐 ID (包年结算时使用)',
  `access_date` DATE DEFAULT NULL COMMENT '接入时间',
  `customer_level` VARCHAR(20) DEFAULT NULL COMMENT '客户等级',
  `sales_owner_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '销售负责人 ID',
  `ops_owner_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '运营负责人 ID',
  `cooperation_status` VARCHAR(20) DEFAULT 'active' COMMENT '合作状态：active/closed/suspended',
  `is_settled` TINYINT(1) DEFAULT 0 COMMENT '是否结算：0-未结算/1-已结算',
  `is_stopped` TINYINT(1) DEFAULT 0 COMMENT '是否停用：0-正常/1-停用',
  `remarks` TEXT DEFAULT NULL COMMENT '备注',
  `settlement_method` VARCHAR(50) DEFAULT NULL COMMENT '结算方式',
  `single_tier_price` DECIMAL(10,4) DEFAULT NULL COMMENT '单层定价 (元/张) - 已废弃，使用 pricing_rule 表',
  `multi_tier_price` JSON DEFAULT NULL COMMENT '多层定价 (JSON 格式) - 已废弃，使用 pricing_rule 表',
  `consumption_level` VARCHAR(20) DEFAULT NULL COMMENT '客户消费等级',
  `monthly_avg_shots` INT DEFAULT 0 COMMENT '月均拍摄量 (张)',
  `current_month_usage` INT DEFAULT 0 COMMENT '当月用量 (张)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
  `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '更新人',
  `is_deleted` TINYINT(1) DEFAULT 0 COMMENT '软删除标记',
  `deleted_at` TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_company_id` (`company_id`),
  KEY `idx_company_name` (`company_name`(50)),
  KEY `idx_device_series` (`device_series_id`),
  KEY `idx_settlement_type` (`settlement_type_id`),
  KEY `idx_package_plan` (`package_plan_id`),
  KEY `idx_erp_system` (`erp_system`),
  KEY `idx_customer_level` (`customer_level`),
  KEY `idx_sales_owner` (`sales_owner_id`),
  KEY `idx_ops_owner` (`ops_owner_id`),
  KEY `idx_cooperation_status` (`cooperation_status`),
  KEY `idx_is_settled` (`is_settled`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `fk_customer_device_series` FOREIGN KEY (`device_series_id`) REFERENCES `device_series` (`id`),
  CONSTRAINT `fk_customer_settlement_type` FOREIGN KEY (`settlement_type_id`) REFERENCES `settlement_type` (`id`),
  CONSTRAINT `fk_customer_package_plan` FOREIGN KEY (`package_plan_id`) REFERENCES `package_plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='客户基础信息表';
```

---

### 5. pricing_rule (定价规则表)

```sql
CREATE TABLE `pricing_rule` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `customer_id` BIGINT UNSIGNED NOT NULL COMMENT '客户 ID',
  `device_series_id` BIGINT UNSIGNED NOT NULL COMMENT '设备系列 ID',
  `settlement_type_id` BIGINT UNSIGNED NOT NULL COMMENT '结算类型 ID',
  `package_plan_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '套餐 ID (包年结算时使用)',
  
  -- 定价结算/阶梯结算 字段
  `rule_type` VARCHAR(20) DEFAULT NULL COMMENT '规则类型：single_tier/multi_tier (包年结算时为空)',
  `unit_price` DECIMAL(10,4) DEFAULT NULL COMMENT '单价 (单层定价时使用)',
  `tier_prices` JSON DEFAULT NULL COMMENT '阶梯价格 (多层定价/阶梯结算时使用)',
  
  -- 阶梯结算专有字段
  `custom_tiers` JSON DEFAULT NULL COMMENT '自定义阶梯区间 (仅阶梯结算使用)',
  
  -- 公共字段
  `min_usage` INT DEFAULT 0 COMMENT '最低用量阈值',
  `max_usage` INT DEFAULT NULL COMMENT '最高用量阈值',
  `effective_date` DATE NOT NULL COMMENT '生效日期',
  `expiry_date` DATE DEFAULT NULL COMMENT '失效日期',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否激活',
  `approval_status` VARCHAR(20) DEFAULT 'pending' COMMENT '审批状态：pending/approved/rejected',
  `approved_by` BIGINT UNSIGNED DEFAULT NULL COMMENT '审批人 ID',
  `approved_at` TIMESTAMP NULL DEFAULT NULL COMMENT '审批时间',
  `remarks` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
  `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '更新人',
  
  PRIMARY KEY (`id`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_device_series_id` (`device_series_id`),
  KEY `idx_settlement_type_id` (`settlement_type_id`),
  KEY `idx_package_plan_id` (`package_plan_id`),
  KEY `idx_effective_date` (`effective_date`),
  KEY `idx_is_active` (`is_active`),
  CONSTRAINT `fk_pricing_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`),
  CONSTRAINT `fk_pricing_device_series` FOREIGN KEY (`device_series_id`) REFERENCES `device_series` (`id`),
  CONSTRAINT `fk_pricing_settlement_type` FOREIGN KEY (`settlement_type_id`) REFERENCES `settlement_type` (`id`),
  CONSTRAINT `fk_pricing_package_plan` FOREIGN KEY (`package_plan_id`) REFERENCES `package_plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='定价规则表';
```

**定价规则配置示例:**

```sql
-- 定价结算 - 单层定价 (N 系列设备)
INSERT INTO `pricing_rule` (customer_id, device_series_id, settlement_type_id, rule_type, unit_price, effective_date)
VALUES (1, 2, 1, 'single_tier', 1.0, '2026-01-01');

-- 定价结算 - 多层定价 (N 系列设备)
INSERT INTO `pricing_rule` (customer_id, device_series_id, settlement_type_id, rule_type, tier_prices, effective_date)
VALUES (2, 2, 1, 'multi_tier', 
'{
  "tiers": [
    {"min": 0, "max": 500, "price": 1.0},
    {"min": 501, "max": 1000, "price": 0.8},
    {"min": 1001, "max": null, "price": 0.6}
  ]
}', '2026-01-01');

-- 阶梯结算 - 自定义阶梯 (X 系列设备)
INSERT INTO `pricing_rule` (customer_id, device_series_id, settlement_type_id, custom_tiers, effective_date)
VALUES (3, 1, 2, 
'{
  "tiers": [
    {"level": 1, "min": 0, "max": 1000, "price": 1.2, "rule_type": "single_tier"},
    {"level": 2, "min": 1001, "max": 5000, "price": 0.9, "rule_type": "single_tier"},
    {"level": 3, "min": 5001, "max": null, "price": 0.7, "rule_type": "single_tier"}
  ]
}', '2026-01-01');

-- 包年结算 - B 套餐 (N 系列设备)
INSERT INTO `pricing_rule` (customer_id, device_series_id, settlement_type_id, package_plan_id, effective_date)
VALUES (4, 2, 3, 6, '2026-01-01');  -- package_plan_id=6 对应 N 系列 B 套餐
```

---

### 6. bill (账单表)

```sql
CREATE TABLE `bill` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `bill_no` VARCHAR(50) NOT NULL COMMENT '账单号 (规则：BILL-YYYYMM-客户 ID-序号)',
  `customer_id` BIGINT UNSIGNED NOT NULL COMMENT '客户 ID',
  `device_series_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '设备系列 ID',
  `settlement_type_id` BIGINT UNSIGNED NOT NULL COMMENT '结算类型 ID',
  `package_plan_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '套餐 ID (包年结算时使用)',
  `month` VARCHAR(7) NOT NULL COMMENT '账期月份 (格式：2026-02)',
  `usage_amount` INT NOT NULL DEFAULT 0 COMMENT '用量 (拍摄量/张)',
  `pricing_rule_type` VARCHAR(20) DEFAULT NULL COMMENT '定价类型：single_tier/multi_tier',
  `unit_price` DECIMAL(10,4) DEFAULT NULL COMMENT '单价',
  `tier_prices` JSON DEFAULT NULL COMMENT '阶梯价格详情',
  `included_usage` INT DEFAULT 0 COMMENT '套餐包含用量 (包年结算时使用)',
  `overuse_usage` INT DEFAULT 0 COMMENT '超出套餐用量 (包年结算时使用)',
  `overuse_price` DECIMAL(10,4) DEFAULT NULL COMMENT '超出单价 (包年结算时使用)',
  `amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '账单金额',
  `discount_amount` DECIMAL(12,2) DEFAULT 0.00 COMMENT '折扣金额',
  `final_amount` DECIMAL(12,2) NOT NULL DEFAULT 0.00 COMMENT '最终金额 (amount - discount)',
  `status` VARCHAR(20) NOT NULL DEFAULT 'unpaid' COMMENT '状态：unpaid/partial/paid/overdue/cancelled',
  `due_date` DATE NOT NULL COMMENT '到期日期',
  `issued_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '出账时间',
  `paid_amount` DECIMAL(12,2) DEFAULT 0.00 COMMENT '已付金额',
  `settled_at` TIMESTAMP NULL DEFAULT NULL COMMENT '结清时间',
  `invoice_status` VARCHAR(20) DEFAULT 'uninvoiced' COMMENT '发票状态：uninvoiced/invoiced',
  `invoice_no` VARCHAR(100) DEFAULT NULL COMMENT '发票号',
  `remarks` TEXT DEFAULT NULL COMMENT '备注',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_by` VARCHAR(50) DEFAULT NULL COMMENT '创建人',
  `updated_by` VARCHAR(50) DEFAULT NULL COMMENT '更新人',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_bill_no` (`bill_no`),
  KEY `idx_customer_id` (`customer_id`),
  KEY `idx_device_series_id` (`device_series_id`),
  KEY `idx_settlement_type_id` (`settlement_type_id`),
  KEY `idx_month` (`month`),
  KEY `idx_status` (`status`),
  KEY `idx_due_date` (`due_date`),
  CONSTRAINT `fk_bill_customer` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`),
  CONSTRAINT `fk_bill_device_series` FOREIGN KEY (`device_series_id`) REFERENCES `device_series` (`id`),
  CONSTRAINT `fk_bill_settlement_type` FOREIGN KEY (`settlement_type_id`) REFERENCES `settlement_type` (`id`),
  CONSTRAINT `fk_bill_package_plan` FOREIGN KEY (`package_plan_id`) REFERENCES `package_plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账单表';
```

---

### 7. 其他核心表 (完整设计见 architecture-design-v1.md)

- `user` - 系统用户表
- `usage_record` - 用量记录表
- `payment` - 收款记录表
- `settlement` - 结算单表
- `reminder` - 逾期提醒表
- `data_import_log` - 数据导入日志表
- `operation_log` - 操作审计日志表

---

## 三种结算模式计算逻辑

### 模式 1: 定价结算 (Pricing Settlement)

**Python 伪代码:**

```python
def calculate_pricing(usage_amount: int, rule_type: str, unit_price: Decimal, tier_prices: dict) -> Decimal:
    """
    定价结算计算
    
    Args:
        usage_amount: 用量 (张)
        rule_type: single_tier | multi_tier
        unit_price: 单价 (单层定价)
        tier_prices: 阶梯价格配置 (多层定价)
    
    Returns:
        结算金额
    """
    if rule_type == 'single_tier':
        return usage_amount * unit_price
    
    elif rule_type == 'multi_tier':
        total = Decimal('0')
        remaining = usage_amount
        
        for tier in tier_prices['tiers']:
            tier_max = tier['max'] if tier['max'] else float('inf')
            tier_usage = min(remaining, tier_max - tier['min'])
            
            if tier_usage > 0:
                total += tier_usage * Decimal(str(tier['price']))
                remaining -= tier_usage
            
            if remaining <= 0:
                break
        
        return total
    
    raise ValueError(f"Invalid rule_type: {rule_type}")
```

**计算示例:**

```python
# 单层定价：1.0 元/张，用量 800 张
amount = calculate_pricing(800, 'single_tier', 1.0, None)
# 结果：800.00 元

# 多层定价：
# 0-500 张：1.0 元/张
# 501-1000 张：0.8 元/张
# 1001+ 张：0.6 元/张
# 用量 800 张
tier_prices = {
    "tiers": [
        {"min": 0, "max": 500, "price": 1.0},
        {"min": 501, "max": 1000, "price": 0.8},
        {"min": 1001, "max": None, "price": 0.6}
    ]
}
amount = calculate_pricing(800, 'multi_tier', None, tier_prices)
# 计算：500×1.0 + 300×0.8 = 500 + 240 = 740.00 元
```

---

### 模式 2: 阶梯结算 (Tiered Settlement)

**Python 伪代码:**

```python
def calculate_tiered(usage_amount: int, custom_tiers: dict) -> Decimal:
    """
    阶梯结算计算
    
    Args:
        usage_amount: 用量 (张)
        custom_tiers: 自定义阶梯配置
    
    Returns:
        结算金额
    """
    total = Decimal('0')
    
    for tier in custom_tiers['tiers']:
        if usage_amount <= tier['min']:
            break
        
        tier_max = tier['max'] if tier['max'] else float('inf')
        tier_usage = min(usage_amount, tier_max) - tier['min']
        
        if tier_usage > 0:
            tier_price = Decimal(str(tier['price']))
            
            # 支持阶梯内再区分单/多层
            if tier.get('rule_type') == 'multi_tier' and 'sub_tiers' in tier:
                total += calculate_pricing(tier_usage, 'multi_tier', None, {'tiers': tier['sub_tiers']})
            else:
                total += tier_usage * tier_price
    
    return total
```

**计算示例:**

```python
# X 系列设备自定义阶梯
custom_tiers = {
    "tiers": [
        {"level": 1, "min": 0, "max": 1000, "price": 1.2, "rule_type": "single_tier"},
        {"level": 2, "min": 1001, "max": 5000, "price": 0.9, "rule_type": "single_tier"},
        {"level": 3, "min": 5001, "max": None, "price": 0.7, "rule_type": "single_tier"}
    ]
}

# 用量 3000 张
amount = calculate_tiered(3000, custom_tiers)
# 计算：1000×1.2 + 2000×0.9 = 1200 + 1800 = 3000.00 元
```

---

### 模式 3: 包年结算 (Package Settlement)

**Python 伪代码:**

```python
def calculate_package(usage_amount: int, included_usage: int, overuse_price: Decimal) -> Decimal:
    """
    包年结算计算
    
    Args:
        usage_amount: 实际用量 (张)
        included_usage: 套餐包含用量 (张)
        overuse_price: 超出单价 (元/张)
    
    Returns:
        超出部分金额 (套餐内用量不收费，只收年费)
    """
    if usage_amount <= included_usage:
        return Decimal('0')  # 套餐内用量，无需额外付费
    
    overuse_usage = usage_amount - included_usage
    return overuse_usage * overuse_price
```

**计算示例:**

```python
# B 套餐：100000 张/年，90000 元，超出 0.7 元/张
included_usage = 100000
overuse_price = Decimal('0.7')

# 情况 1: 用量 80000 张 (未超出)
amount = calculate_package(80000, included_usage, overuse_price)
# 结果：0.00 元 (只收年费 90000 元)

# 情况 2: 用量 120000 张 (超出 20000 张)
amount = calculate_package(120000, included_usage, overuse_price)
# 计算：20000 × 0.7 = 14000.00 元
```

---

## 数据迁移策略

### 历史数据处理

**现状:** 1320 条 Excel 数据，包含 `single_tier_price` 和 `multi_tier_price` 字段

**迁移步骤:**

```sql
-- Step 1: 默认设备系列和结算类型
UPDATE customer 
SET device_series_id = 2,  -- 默认 N 系列
    settlement_type_id = 1  -- 默认定价结算
WHERE device_series_id IS NULL;

-- Step 2: 迁移历史定价数据到 pricing_rule 表
INSERT INTO pricing_rule (customer_id, device_series_id, settlement_type_id, rule_type, unit_price, tier_prices, effective_date, is_active, approval_status)
SELECT 
    id AS customer_id,
    2 AS device_series_id,
    1 AS settlement_type_id,
    CASE 
        WHEN multi_tier_price IS NOT NULL THEN 'multi_tier'
        WHEN single_tier_price IS NOT NULL THEN 'single_tier'
        ELSE NULL
    END AS rule_type,
    single_tier_price AS unit_price,
    multi_tier_price AS tier_prices,
    '2026-01-01' AS effective_date,
    1 AS is_active,
    'approved' AS approval_status
FROM customer
WHERE single_tier_price IS NOT NULL OR multi_tier_price IS NOT NULL;

-- Step 3: 验证迁移结果
SELECT 
    c.id,
    c.company_name,
    pr.rule_type,
    pr.unit_price,
    pr.tier_prices
FROM customer c
LEFT JOIN pricing_rule pr ON c.id = pr.customer_id
WHERE pr.id IS NOT NULL
LIMIT 10;
```

---

## 性能优化建议

### 索引优化

```sql
-- 高频查询字段组合索引
CREATE INDEX idx_customer_status_device ON customer(cooperation_status, device_series_id, is_stopped);
CREATE INDEX idx_bill_customer_month_status ON bill(customer_id, month, status);
CREATE INDEX idx_pricing_active_effective ON pricing_rule(is_active, effective_date, expiry_date);

-- 用量统计查询优化
CREATE INDEX idx_usage_month_amount ON usage_record(month, usage_amount);
```

### 分区表建议

```sql
-- usage_record 表按月分区 (预计每年 1320 条记录)
ALTER TABLE usage_record 
PARTITION BY RANGE (YEAR(month)) (
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p2027 VALUES LESS THAN (2028),
    PARTITION p_max VALUES LESS THAN MAXVALUE
);

-- bill 表按月分区
ALTER TABLE bill
PARTITION BY RANGE COLUMNS(month) (
    PARTITION p202601 VALUES LESS THAN ('2026-02'),
    PARTITION p202602 VALUES LESS THAN ('2026-03'),
    ...
    PARTITION p_max VALUES LESS THAN MAXVALUE
);
```

---

## 下一步行动

1. ✅ **数据库设计完成** - 支持三种结算模式
2. ⏳ **API 接口设计** - OpenAPI 规范定义
3. ⏳ **前端组件设计** - Vue 组件架构
4. ⏳ **部署架构设计** - Docker + K8s

---

## 附录

### 术语表

| 术语 | 说明 |
|------|------|
| **设备系列** | X/N/L 三个系列的硬件设备拍摄类型 |
| **定价结算** | 按设备类型配置单层/多层定价 |
| **阶梯结算** | 按设备类型自定义阶梯，区分单/多层定价 |
| **包年结算** | A/B/C/D 套餐，不同套餐等级对应不同用量 |
| **单层定价** | 固定单价 × 用量 |
| **多层定价** | 不同用量区间不同单价 |

### 参考资料

- [MySQL 8.0 JSON 字段最佳实践](https://dev.mysql.com/doc/refman/8.0/en/json.html)
- [MySQL 分区表设计](https://dev.mysql.com/doc/refman/8.0/en/partitioning.html)
