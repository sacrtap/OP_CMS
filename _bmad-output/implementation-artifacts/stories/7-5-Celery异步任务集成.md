# Story 7.1: Celery 异步任务集成

**Status:** ready-for-dev  
**Epic:** Epic 7 - 系统集成与自动化  
**Story Points:** 8  
**Priority:** High  

---

## User Story

As a 运营人员,  
I want 可以在后台异步执行大批量导入导出任务,  
So that 不阻塞界面并提高工作效率。

---

## Acceptance Criteria

### AC 1: Celery 配置
- **Given** 系统需要异步任务支持  
- **When** 配置 Celery + Redis  
- **Then** 系统支持异步任务队列  
- **And** 支持任务结果存储

### AC 2: 异步导入任务
- **Given** 运营人员上传大批量数据  
- **When** 点击"异步导入"  
- **Then** 任务提交到 Celery 队列  
- **And** 显示任务 ID 和预估时间

### AC 3: 异步导出任务
- **Given** 运营人员需要导出大量数据  
- **When** 点击"异步导出"  
- **Then** 任务提交到 Celery 队列  
- **And** 完成后提供下载链接

### AC 4: 任务状态查询
- **Given** 异步任务已提交  
- **When** 查询任务状态  
- **Then** 显示任务进度（0-100%）  
- **And** 支持取消任务

---

## Tasks / Subtasks

- [ ] Task 1: 配置 Celery + Redis (AC: 1)
  - [ ] Subtask 1.1: 安装 Celery 和 Redis
  - [ ] Subtask 1.2: 配置 Celery Worker
  - [ ] Subtask 1.3: 配置任务结果存储

- [ ] Task 2: 实现异步导入任务 (AC: 2)
  - [ ] Subtask 2.1: 创建 import_customers_task 异步任务
  - [ ] Subtask 2.2: 实现任务进度更新
  - [ ] Subtask 2.3: 集成到导入 API

- [ ] Task 3: 实现异步导出任务 (AC: 3)
  - [ ] Subtask 3.1: 创建 export_customers_task 异步任务
  - [ ] Subtask 3.2: 实现文件上传到存储
  - [ ] Subtask 3.3: 集成到导出 API

- [ ] Task 4: 实现任务状态 API (AC: 4)
  - [ ] Subtask 4.1: GET /api/v1/async-tasks/:id - 查询任务状态
  - [ ] Subtask 4.2: DELETE /api/v1/async-tasks/:id - 取消任务
  - [ ] Subtask 4.3: WebSocket 实时更新（可选）

- [ ] Task 5: 编写单元测试 (AC: 2, 4)
  - [ ] Subtask 5.1: 测试 Celery 配置
  - [ ] Subtask 5.2: 测试异步任务
  - [ ] Subtask 5.3: 测试任务状态 API

---

## Technical Implementation Notes

### Backend Implementation

**Celery Configuration:**
```python
# celery_app.py
from celery import Celery

celery_app = Celery(
    'op_cms',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

@celery_app.task(bind=True)
def import_customers_task(self, file_data, import_mode):
    # Update progress: self.update_state(state='PROGRESS', meta={'progress': 50})
    # Return result
```

**Async Task API:**
```python
POST /api/v1/customers/import-async
GET /api/v1/async-tasks/:id
DELETE /api/v1/async-tasks/:id
```

### Redis Configuration

**Docker Compose:**
```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
```

---

## Dependencies

- ✅ Story 6.2: 导入导出增强 (已完成 - 导入导出基础)
- ✅ Story 6.4: 批量处理 (已完成 - 批量处理框架)

---

## Definition of Done

- [ ] All 4 ACs implemented and tested
- [ ] Celery + Redis configured
- [ ] Async import/export tasks working
- [ ] Task status API working
- [ ] Progress tracking implemented
- [ ] Unit tests pass (>90% coverage)

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
