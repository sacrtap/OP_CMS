---
name: Epic-8 技术债务清理与质量提升
version: 1.0
sprint: 8
priority: high
status: planning
created_date: 2026-02-25
---

# Epic-8 技术债务清理与质量提升

## 📊 Epic 概述

**Epic 名称:** 技术债务清理与质量提升  
**优先级:** High  
**计划 Sprint:** Sprint 8  
**预计周期:** 2 周

---

## 🎯 Epic 目标

基于 Epic-7 Retrospective 和测试执行结果，Epic-8 将专注于清理剩余技术债务，提升项目整体质量，为后续功能开发奠定坚实基础。

### 主要目标

1. **测试覆盖率提升至 90%** (当前 ~83%)
2. **实现缺失的 DataValidationService**
3. **修复剩余测试问题** (18 个失败测试)
4. **前端测试运行与优化**
5. **文档完善与代码清理**

---

## 📋 User Stories

### Story 8.1: 完成 DataValidationService 实现 [8 SP]

**作为** 开发人员  
**我希望** 有完整的数据验证服务  
**以便** 确保数据质量和一致性

#### 验收标准

- [ ] AC1: 实现 `validate_customer_data()` 方法
  - 必填字段验证 (公司名称、联系人、联系电话)
  - 格式验证 (电话、邮箱、统一社会信用代码)
  - 枚举值验证 (客户类型、状态、级别)
  
- [ ] AC2: 实现 `detect_duplicates()` 方法
  - 按公司名称检测重复
  - 按联系电话检测重复
  - 按统一社会信用代码检测重复
  
- [ ] AC3: 实现 `validate_data_batch()` 方法
  - 批量数据验证
  - 错误收集与报告
  - 验证进度跟踪
  
- [ ] AC4: 单元测试覆盖率 ≥90%
  - 至少 30 个测试用例
  - 覆盖正常流程和异常流程

**Definition of Done:**
- ✅ 所有 AC 完成
- ✅ 测试覆盖率 ≥90%
- ✅ 代码审查通过
- ✅ 文档完善

---

### Story 8.2: 修复 BackupService 测试问题 [3 SP]

**作为** QA 工程师  
**我希望** BackupService 所有测试通过  
**以便** 确保备份功能的可靠性

#### 验收标准

- [ ] AC1: 修复 `test_create_backup_subprocess_failure` (1h)
  - 标准化错误消息
  - 完善 Mock 设置
  
- [ ] AC2: 修复 `test_create_backup_invalid_type` (1h)
  - 完善 Mock 对象属性
  - 添加错误处理验证
  
- [ ] AC3: 修复 `test_restore_backup_*` 测试 (2h)
  - 添加文件存在 Mock
  - 标准化错误消息
  
- [ ] AC4: BackupService 测试通过率 100% (18/18)

**Definition of Done:**
- ✅ 所有测试通过
- ✅ 测试代码优化
- ✅ Mock 设置规范化

---

### Story 8.3: 修复 SettlementService 测试问题 [2 SP]

**作为** QA 工程师  
**我希望** SettlementService 所有测试通过  
**以便** 确保结算计算的准确性

#### 验收标准

- [ ] AC1: 修复 `test_calculate_tiered_progressive_basic` (1h)
  - 添加完整的 setUp 方法
  - 初始化 self.service
  
- [ ] AC2: 修复 `test_create_settlement_record_*` (2h)
  - 修正 uuid Mock 路径
  - 完善 Mock 对象设置
  
- [ ] AC3: 修复 `test_complete_settlement_workflow` (1h)
  - 统一 Mock 路径
  - 完善工作流程测试
  
- [ ] AC4: SettlementService 测试通过率 100% (21/21)

**Definition of Done:**
- ✅ 所有测试通过
- ✅ Mock 路径统一
- ✅ 测试代码优化

---

### Story 8.4: 修复 CustomerExcelService 测试问题 [5 SP]

**作为** QA 工程师  
**我希望** CustomerExcelService 所有测试通过  
**以便** 确保 Excel 导入导出功能的稳定性

#### 验收标准

- [ ] AC1: 修复 openpyxl Mock 问题 (2h)
  - 统一 Mock 路径
  - 完善 Workbook Mock
  
- [ ] AC2: 修复 pandas Mock 问题 (2h)
  - 规范 DataFrame Mock
  - 处理 ExcelError
  
- [ ] AC3: 修复 Mock 迭代问题 (2h)
  - 优化 Mock 对象行为
  - 完善错误报告测试
  
- [ ] AC4: CustomerExcelService 测试通过率 100% (28/28)

**Definition of Done:**
- ✅ 所有测试通过
- ✅ Mock 规范化
- ✅ 测试稳定性提升

---

### Story 8.5: 前端测试运行与覆盖率提升 [5 SP]

**作为** 前端开发人员  
**我希望** 运行前端测试并提升覆盖率  
**以便** 确保前端组件质量

#### 验收标准

- [ ] AC1: 配置 vitest.config.ts (2h)
  - 配置 @ 别名
  - 配置 jsdom 环境
  - 配置全局测试设置
  
- [ ] AC2: 运行所有前端测试 (1h)
  - CustomerCard.spec.ts (13 用例)
  - MobileNav.spec.ts (12 用例)
  - ResponsiveTable.spec.ts (14 用例)
  - 测试通过率 ≥90%
  
- [ ] AC3: 补充 Store 模块测试 (4h)
  - auth store 测试 (5 用例)
  - 状态管理测试
  
- [ ] AC4: 补充工具函数测试 (3h)
  - api.ts 测试 (8 用例)
  - 工具函数测试 (6 用例)
  
- [ ] AC5: 前端测试覆盖率 ≥85%

**Definition of Done:**
- ✅ 前端测试运行正常
- ✅ 测试覆盖率 ≥85%
- ✅ 所有组件已测试

---

### Story 8.6: 代码清理与文档完善 [3 SP]

**作为** 项目维护者  
**我希望** 代码整洁、文档完善  
**以便** 提高项目可维护性

#### 验收标准

- [ ] AC1: 代码清理 (3h)
  - 删除死代码
  - 优化导入语句
  - 统一代码风格
  - 添加缺失注释
  
- [ ] AC2: 文档完善 (3h)
  - API 文档更新
  - 部署文档完善
  - 开发文档补充
  
- [ ] AC3: 依赖更新 (2h)
  - 检查过期依赖
  - 更新安全补丁
  - 清理未使用依赖
  
- [ ] AC4: 项目结构优化 (2h)
  - 整理目录结构
  - 优化模块划分
  - 添加 .gitignore 规则

**Definition of Done:**
- ✅ 代码整洁规范
- ✅ 文档完整齐全
- ✅ 依赖更新到最新稳定版

---

## 📊 Story 优先级排序

| 优先级 | Story ID | 故事名称 | 故事点 | 依赖关系 |
|--------|----------|----------|--------|----------|
| **P0** | 8.1 | DataValidationService 实现 | 8 SP | 无 |
| **P0** | 8.2 | BackupService 测试修复 | 3 SP | 无 |
| **P1** | 8.3 | SettlementService 测试修复 | 2 SP | 无 |
| **P1** | 8.4 | CustomerExcelService 测试修复 | 5 SP | 无 |
| **P1** | 8.5 | 前端测试运行与提升 | 5 SP | 无 |
| **P2** | 8.6 | 代码清理与文档完善 | 3 SP | 无 |

**总计:** 26 Story Points

---

## 🎯 验收标准

### Epic 完成标准

- [ ] 所有 6 个 Story 完成 (6/6)
- [ ] 测试覆盖率 ≥90% (后端 + 前端)
- [ ] 所有测试通过 (100% 通过率)
- [ ] DataValidationService 完整实现
- [ ] 代码质量提升 (无警告、无错误)
- [ ] 文档完整齐全

### 质量指标

| 指标 | 当前值 | 目标值 | 改进 |
|------|--------|--------|------|
| 后端测试覆盖率 | ~83% | ≥90% | +7% |
| 前端测试覆盖率 | ~80% | ≥85% | +5% |
| 测试通过率 | 73% | 100% | +27% |
| 技术债务 | 中 | 低 | ↓ |

---

## 📅 Sprint 规划

### Sprint 8 (第 1 周)

**目标:** 完成高优先级测试修复

**计划 Story:**
- 8.1 DataValidationService 实现 (8 SP)
- 8.2 BackupService 测试修复 (3 SP)

**预计容量:** 11 SP

---

### Sprint 8 (第 2 周)

**目标:** 完成剩余测试修复和前端测试

**计划 Story:**
- 8.3 SettlementService 测试修复 (2 SP)
- 8.4 CustomerExcelService 测试修复 (5 SP)
- 8.5 前端测试运行与提升 (5 SP)

**预计容量:** 12 SP

---

### Sprint 8 (缓冲周)

**目标:** 代码清理和文档完善

**计划 Story:**
- 8.6 代码清理与文档完善 (3 SP)
- 缓冲时间 (应对延期)

**预计容量:** 3 SP + 缓冲

---

## 🔧 技术实施要点

### DataValidationService 实现

**关键方法:**
```python
def validate_customer_data(self, customer_data: dict) -> tuple[bool, list]:
    """验证单个客户数据"""
    
def detect_duplicates(self, customer_data: dict, session=None) -> list:
    """检测重复数据"""
    
def validate_data_batch(self, batch_data: list[dict]) -> dict:
    """批量数据验证"""
    
def validate_phone(self, phone: str) -> tuple[bool, str]:
    """验证电话号码"""
    
def validate_email(self, email: str) -> tuple[bool, str]:
    """验证邮箱地址"""
    
def validate_credit_code(self, code: str) -> tuple[bool, str]:
    """验证统一社会信用代码"""
```

---

### Mock 路径标准化

**统一 Mock 路径规范:**
```python
# 正确方式：使用完整模块路径
@patch('backend.services.backup_service.subprocess.run')
@patch('backend.services.settlement_service.uuid.uuid4')

# 避免：使用短路径
@patch('subprocess.run')  # ❌
@patch('uuid.uuid4')  # ❌
```

---

### 测试覆盖率工具

**后端:**
```bash
pytest --cov=backend --cov-report=html --cov-report=term-missing
```

**前端:**
```bash
bun test --coverage
```

---

## 📈 风险管理

### 风险识别

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| DataValidationService 实现复杂度高 | 中 | 高 | 分阶段实现，优先核心功能 |
| Mock 问题修复耗时超预期 | 高 | 中 | 制定 Mock 规范，统一路径 |
| 前端测试环境问题 | 中 | 中 | 准备多种配置方案 |
| 依赖更新导致兼容性问题 | 低 | 高 | 逐步更新，充分测试 |

---

## 🎉 预期收益

### 技术收益

1. **测试覆盖率提升至 90%+**
2. **测试通过率 100%**
3. **代码质量显著提升**
4. **技术债务基本清零**

### 业务收益

1. **系统稳定性提升**
2. **Bug 率降低**
3. **开发效率提升**
4. **维护成本降低**

### 团队收益

1. **开发信心提升**
2. **代码审查效率提升**
3. **新人上手更快**
4. **技术文档完善**

---

**文档生成日期:** 2026-02-25  
**创建人:** Dev (Amelia) + PM  
**下次更新:** Sprint 8 开始时  
**Epic 状态:** Planning
