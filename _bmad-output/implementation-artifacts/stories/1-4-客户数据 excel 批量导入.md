# Story 1.4: 客户数据 excel 批量导入

**Status:** ready-for-dev  
**Epic:** Epic 1 - 客户管理  
**Story Points:** 8  
**Priority:** High  

---

## User Story

As a 运营人员,  
I want 可以通过 excel 批量导入客户数据,  
So that 快速录入大量客户信息（1320 条客户数据）。

---

## Acceptance Criteria

### AC 1: Excel 模板下载
- **Given** 运营人员进入批量导入页面  
- **When** 点击"下载模板"按钮  
- **Then** 系统提供标准 Excel 模板文件  
- **And** 模板包含所有必填字段和示例数据

### AC 2: Excel 文件上传
- **Given** 运营人员准备好 Excel 文件  
- **When** 上传 Excel 文件并点击"导入"  
- **Then** 系统解析 Excel 文件并显示预览  
- **And** 显示总记录数和字段映射

### AC 3: 数据验证
- **Given** Excel 文件已上传  
- **When** 系统验证每行数据  
- **Then** 标记有效数据和错误数据  
- **And** 显示详细错误信息（必填字段、格式错误、重复数据）

### AC 4: 批量导入执行
- **Given** 数据验证通过  
- **When** 点击"确认导入"按钮  
- **Then** 系统批量创建客户记录  
- **And** 显示导入结果（成功数量、失败数量、失败原因）

---

## Tasks / Subtasks

- [ ] Task 1: 实现后端 Excel 解析功能 (AC: 1, 2)
  - [ ] Subtask 1.1: 添加 openpyxl/xlsxwriter 依赖
  - [ ] Subtask 1.2: 实现 Excel 模板生成功能
  - [ ] Subtask 1.3: 实现 Excel 文件解析功能

- [ ] Task 2: 实现数据验证功能 (AC: 3)
  - [ ] Subtask 2.1: 必填字段验证
  - [ ] Subtask 2.2: 字段格式验证（手机号、邮箱、信用代码）
  - [ ] Subtask 2.3: 重复数据检测（批量）

- [ ] Task 3: 实现批量导入功能 (AC: 4)
  - [ ] Subtask 3.1: 批量插入数据库（事务处理）
  - [ ] Subtask 3.2: 导入结果统计
  - [ ] Subtask 3.3: 错误日志记录

- [ ] Task 4: 实现前端导入界面 (AC: 1, 2, 4)
  - [ ] Subtask 4.1: 上传组件（支持拖拽）
  - [ ] Subtask 4.2: 数据预览表格
  - [ ] Subtask 4.3: 导入进度显示
  - [ ] Subtask 4.4: 结果展示和错误下载

- [ ] Task 5: 编写导入功能测试 (AC: 2, 3, 4)
  - [ ] Subtask 5.1: Excel 解析测试
  - [ ] Subtask 5.2: 数据验证测试
  - [ ] Subtask 5.3: 批量导入性能测试

---

## Technical Implementation Notes

### Backend - Excel Processing

**Dependencies:**
```bash
pip install openpyxl pandas
```

**Excel Template Structure:**
```
| 公司名称 | 联系人 | 联系电话 | 统一社会信用代码 | 客户类型 | 省份 | 城市 | 邮箱 | ... |
| Test 公司 | 张三 | 13800138000 | 91310000MA1K3YJ12X | enterprise | Shanghai | Shanghai | test@example.com | ... |
```

**Upload API:**
```python
POST /api/v1/customers/import
Content-Type: multipart/form-data

Request:
- file: Excel file (.xlsx, .xls)
- validate_only: boolean (default: false)

Response:
{
  "success": true,
  "data": {
    "total": 100,
    "valid": 95,
    "invalid": 5,
    "errors": [
      { "row": 5, "field": "contact_phone", "error": "Invalid phone format" },
      { "row": 12, "field": "company_name", "error": "Duplicate company name" }
    ],
    "preview": [...] // First 10 valid records
  }
}
```

**Import Execution API:**
```python
POST /api/v1/customers/import/execute
{
  "file_id": "temp_file_uuid",
  "skip_invalid": true
}

Response:
{
  "success": true,
  "data": {
    "imported": 95,
    "failed": 5,
    "import_log_id": 123
  }
}
```

### Frontend Components

**New Components:**
- `CustomerImport.vue` - Main import page
- `UploadZone.vue` - Drag & drop upload area
- `ImportPreview.vue` - Data preview table
- `ImportResult.vue` - Import results display

**Features:**
- Drag & drop file upload
- File type validation (.xlsx only)
- Row-by-row validation display
- Progress bar for large imports
- Download error report as Excel

---

## Dependencies

- ✅ Story 1.1: 客户基础信息维护 (已完成 - Customer 模型)
- ✅ Story 1.2: 客户信息查询与搜索 (已完成 - 数据验证逻辑)

---

## Definition of Done

- [ ] All 4 ACs implemented and tested
- [ ] Excel template generation works
- [ ] File upload and parsing works
- [ ] Data validation with detailed errors
- [ ] Batch import with transaction support
- [ ] Frontend has complete import UI
- [ ] Unit tests pass (>90% coverage)
- [ ] Performance: Can handle 1000+ records in <30s

---

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

### Next Steps

---

## Change Log

- {{date}}: Story created from epics.md
