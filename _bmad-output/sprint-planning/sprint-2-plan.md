# Sprint 2 Plan

**Sprint:** Sprint 2 - 定价配置管理 + 技术债务偿还  
**Duration:** 5 days (2026-02-26 to 2026-03-04)  
**Capacity:** 1 developer + AI collaboration  
**Sprint Goal:** 实现定价配置核心功能 + 解决高优先级技术债务

---

## 📋 Sprint 2 Commitment

### Epic-2: 定价配置管理 (Stories: 4)

**Story 2.1:** 单层定价模式配置  
- **Story Points:** 3  
- **Priority:** High  
- **AC:** 固定价格配置，支持不同设备系列 (X/N/L)  
- **Dependencies:** Story 1.1 (Customer 模型)

**Story 2.2:** 多层定价模式配置  
- **Story Points:** 5  
- **Priority:** High  
- **AC:** 分段价格配置，多层价格阶梯  
- **Dependencies:** Story 2.1

**Story 2.3:** 阶梯定价模式配置  
- **Story Points:** 5  
- **Priority:** High  
- **AC:** 累进价格配置，阶梯计算逻辑  
- **Dependencies:** Story 2.1

**Story 2.4:** 价格配置版本控制  
- **Story Points:** 5  
- **Priority:** Medium  
- **AC:** 变更历史记录，版本回滚功能  
- **Dependencies:** Story 2.1, 2.2, 2.3

**Total Epic-2 Points:** 18 点

---

### 技术债务偿还 (Sprint 1 Retrospective Action Items)

**High Priority (Must Do):**

1. **前端依赖完善** - 2 小时
   ```bash
   cd frontend
   npm install axios vue-router pinia element-plus
   ```
   - ✅ 安装 axios (HTTP 客户端)
   - ✅ 安装 vue-router (路由管理)
   - ✅ 安装 pinia (状态管理)
   - ✅ 配置 TypeScript 类型

2. **用户认证框架** - 8 小时
   - JWT Token 认证
   - 登录/注册页面
   - 权限中间件
   - 用户状态管理 (Pinia)
   - **Story Points:** 5

3. **数据库迁移脚本** - 4 小时
   - 初始化 MySQL 表结构
   - 插入测试数据
   - 迁移脚本自动化
   - **Story Points:** 3

**Medium Priority (Should Do):**

4. **API 文档自动化** - 3 小时
   - 配置 sanic-ext
   - 生成 Swagger/OpenAPI 文档
   - 前端集成 API 文档查看
   - **Story Points:** 2

5. **测试框架完善** - 6 小时
   - 前端：Vitest + Vue Test Utils
   - 后端：集成测试框架
   - 配置测试覆盖率报告
   - **Story Points:** 3

**Total Tech Debt Points:** 13 点

---

## 📊 Sprint 2 Capacity Planning

### Available Capacity
- **Sprint Duration:** 5 days
- **Developer Capacity:** 8 hours/day = 40 hours
- **AI Collaboration:** 10x multiplier
- **Total Capacity:** ~400 story points (AI-assisted)

### Committed Work
- **Epic-2 Stories:** 18 points
- **Tech Debt:** 13 points
- **Buffer (20%):** 6 points
- **Total Committed:** 37 points

### Velocity Projection
- **Sprint 1 Velocity:** 34 points / 3 days = 11.3 pts/day
- **Sprint 2 Projection:** 11.3 × 5 = 56.5 points
- **Committed:** 37 points (66% of capacity) ✅

---

## 📅 Sprint 2 Schedule

### Day 1 (2026-02-26): Setup & Foundation
**Morning:**
- [ ] Sprint 2 Planning Meeting (1h)
- [ ] Story 2.1 Kickoff
- [ ] Setup frontend dependencies (Action Item #1)

**Afternoon:**
- [ ] Story 2.1 Implementation - PriceConfig model extension
- [ ] Story 2.1 Backend API - Single-tier pricing CRUD

**Evening:**
- [ ] Story 2.1 Frontend - Basic form component
- [ ] Code review & commit

**Deliverables:**
- ✅ Frontend dependencies installed
- ✅ PriceConfig model extended
- ✅ Story 2.1: 50% complete

---

### Day 2 (2026-02-27): Pricing Implementation
**Morning:**
- [ ] Story 2.1 Completion & Review
- [ ] Story 2.2 Kickoff - Multi-tier pricing model

**Afternoon:**
- [ ] Story 2.2 Backend - Multi-tier pricing logic
- [ ] Story 2.2 Database schema for price tiers

**Evening:**
- [ ] Story 2.2 Frontend - Tier configuration UI
- [ ] Story 2.2 Testing

**Deliverables:**
- ✅ Story 2.1: Done
- ✅ Story 2.2: 70% complete

---

### Day 3 (2026-02-28): Advanced Pricing
**Morning:**
- [ ] Story 2.2 Completion & Review
- [ ] Story 2.3 Kickoff - Tiered pricing (progressive)

**Afternoon:**
- [ ] Story 2.3 Backend - Tiered calculation logic
- [ ] Story 2.3 Math engine for progressive pricing

**Evening:**
- [ ] Story 2.3 Frontend - Tiered pricing UI
- [ ] Story 2.3 Testing & validation

**Deliverables:**
- ✅ Story 2.2: Done
- ✅ Story 2.3: 80% complete

---

### Day 4 (2026-03-01): Version Control & Auth
**Morning:**
- [ ] Story 2.3 Completion & Review
- [ ] Story 2.4 Kickoff - Version control system

**Afternoon:**
- [ ] Story 2.4 Backend - Version history tracking
- [ ] User Authentication implementation (Action Item #2)

**Evening:**
- [ ] Story 2.4 Frontend - Version history UI
- [ ] Auth middleware integration

**Deliverables:**
- ✅ Story 2.3: Done
- ✅ Story 2.4: 60% complete
- ✅ User auth framework: 50% complete

---

### Day 5 (2026-03-02): Testing & Documentation
**Morning:**
- [ ] Story 2.4 Completion & Review
- [ ] API Documentation automation (Action Item #4)

**Afternoon:**
- [ ] Test framework setup (Action Item #5)
- [ ] Integration testing
- [ ] Bug fixes

**Evening:**
- [ ] Sprint 2 Demo preparation
- [ ] Sprint 2 Retrospective
- [ ] Sprint 3 Planning preview

**Deliverables:**
- ✅ Story 2.4: Done
- ✅ API Docs: Auto-generated
- ✅ Test framework: Setup complete
- ✅ Sprint 2: 100% complete

---

## 🎯 Success Criteria

### Must Have (100% Required)
- [ ] All 4 Epic-2 stories completed and tested
- [ ] Frontend dependencies installed and configured
- [ ] User authentication working (JWT)
- [ ] Price configuration CRUD fully functional
- [ ] Code committed and pushed to remote

### Should Have (80% Target)
- [ ] API documentation auto-generated
- [ ] Test framework setup (Vitest + pytest)
- [ ] Database migration scripts working
- [ ] Code coverage >70%

### Nice to Have (Stretch Goals)
- [ ] CI/CD pipeline configured
- [ ] Performance optimization (Redis cache)
- [ ] Mobile-responsive UI improvements

---

## 📋 Story Details

### Story 2.1: 单层定价模式配置

**User Story:**
> As a 运营人员,  
> I want 可以配置单层定价模式（固定价格）,  
> So that 为客户设置简单的定价规则。

**Acceptance Criteria:**
1. ✅ 运营人员进入定价配置页面
2. ✅ 选择"单层定价"模式并设置单价
3. ✅ 系统保存定价配置并关联到客户
4. ✅ 支持为不同设备系列（X/N/L）设置不同价格

**Technical Tasks:**
- [ ] Extend PriceConfig model with device_series field
- [ ] Create SingleTierPricing schema (Pydantic)
- [ ] API endpoints: GET/POST/PUT /api/v1/pricing/single-tier
- [ ] Frontend: SingleTierForm.vue component
- [ ] Unit tests for pricing calculation

**Definition of Done:**
- [ ] All 4 ACs implemented
- [ ] Backend API tested
- [ ] Frontend form working
- [ ] Unit tests passing (>90% coverage)

---

### Story 2.2: 多层定价模式配置

**User Story:**
> As a 运营人员,  
> I want 可以配置多层定价模式（分段价格）,  
> So that 为客户设置复杂的阶梯定价规则。

**Acceptance Criteria:**
1. ✅ 运营人员进入定价配置页面
2. ✅ 选择"多层定价"模式并设置多个价格阶梯
3. ✅ 系统保存定价配置并关联到客户
4. ✅ 支持查看和编辑已配置的价格阶梯

**Technical Tasks:**
- [ ] Create PriceTier model (multiple tiers per config)
- [ ] MultiTierPricing schema with nested tiers
- [ ] API endpoints: GET/POST/PUT /api/v1/pricing/multi-tier
- [ ] Frontend: MultiTierForm.vue with dynamic tier rows
- [ ] Validation: tiers must be sequential and non-overlapping

**Definition of Done:**
- [ ] All 4 ACs implemented
- [ ] Backend API tested with complex scenarios
- [ ] Frontend form with dynamic tier management
- [ ] Unit tests for tier validation

---

### Story 2.3: 阶梯定价模式配置

**User Story:**
> As a 运营人员,  
> I want 可以配置阶梯定价模式（累进价格）,  
> So that 为客户设置累进式的定价规则。

**Acceptance Criteria:**
1. ✅ 运营人员进入定价配置页面
2. ✅ 选择"阶梯定价"模式并设置累进价格
3. ✅ 系统保存定价配置并关联到客户
4. ✅ 支持查看和编辑已配置的阶梯价格

**Technical Tasks:**
- [ ] TieredPricing model with quantity breaks
- [ ] Calculation engine for progressive pricing
- [ ] API endpoints: GET/POST/PUT /api/v1/pricing/tiered
- [ ] Frontend: TieredPricingForm.vue with calculation preview
- [ ] Math validation: ensure correct tier calculations

**Definition of Done:**
- [ ] All 4 ACs implemented
- [ ] Pricing calculation engine tested
- [ ] Frontend with live calculation preview
- [ ] Unit tests for math accuracy

---

### Story 2.4: 价格配置版本控制

**User Story:**
> As a 运营人员,  
> I want 可以查看价格配置的变更历史记录并回滚错误的变更,  
> So that 确保价格配置的准确性和可追溯性。

**Acceptance Criteria:**
1. ✅ 运营人员进入定价配置页面
2. ✅ 点击"查看历史"按钮
3. ✅ 系统显示价格配置的变更历史记录
4. ✅ 支持回滚到指定版本的价格配置

**Technical Tasks:**
- [ ] Create PriceConfigVersion model (audit trail)
- [ ] Version control middleware (auto-save on changes)
- [ ] API endpoints: GET /api/v1/pricing/:id/versions, POST /api/v1/pricing/:id/rollback
- [ ] Frontend: VersionHistory.vue with diff view
- [ ] Rollback mechanism with validation

**Definition of Done:**
- [ ] All 4 ACs implemented
- [ ] Version tracking automatic
- [ ] Frontend history viewer working
- [ ] Rollback tested with edge cases

---

## 🔧 Technical Debt Action Items

### #1: Frontend Dependencies (2 hours)
**Priority:** High  
**Owner:** Frontend Dev  
**Status:** ⏳ Todo

```bash
cd frontend
npm install axios vue-router pinia @element-plus/icons-vue
npm install -D vitest @vue/test-utils jsdom
```

**Configuration:**
- Setup vue-router with routes
- Configure Pinia store
- Setup axios interceptors
- Configure TypeScript types

---

### #2: User Authentication (8 hours)
**Priority:** High  
**Owner:** Backend Dev  
**Status:** ⏳ Todo

**Implementation:**
- JWT token generation and validation
- User model and authentication API
- Login/Register pages
- Auth middleware for protected routes
- Pinia user store

**Files to Create:**
- `backend/models/auth.py` - User model
- `backend/api/auth.py` - Auth endpoints
- `backend/utils/jwt.py` - JWT utilities
- `frontend/src/views/auth/Login.vue`
- `frontend/src/views/auth/Register.vue`
- `frontend/src/stores/auth.ts`

---

### #3: Database Migration Scripts (4 hours)
**Priority:** Medium  
**Owner:** Backend Dev  
**Status:** ⏳ Todo

**Implementation:**
- Alembic setup and configuration
- Initial migration for all models
- Seed data script for testing
- Docker volume for MySQL persistence

**Files to Create:**
- `backend/migrations/env.py`
- `backend/migrations/versions/001_initial.py`
- `backend/scripts/seed_data.py`

---

### #4: API Documentation (3 hours)
**Priority:** Medium  
**Owner:** Backend Dev  
**Status:** ⏳ Todo

**Implementation:**
- sanic-ext configuration
- Swagger/OpenAPI generation
- API documentation decorator
- Frontend docs viewer (optional)

**Files to Modify:**
- `backend/main.py` - Enable sanic-ext
- `backend/api/*.py` - Add docstrings

---

### #5: Test Framework (6 hours)
**Priority:** Medium  
**Owner:** QA  
**Status:** ⏳ Todo

**Implementation:**
- Vitest configuration for Vue 3
- pytest configuration improvements
- Test coverage reporting
- CI/CD integration preparation

**Files to Create:**
- `frontend/vitest.config.ts`
- `frontend/src/stores/__tests__/`
- `pytest.ini` (improved)
- `.github/workflows/test.yml`

---

## 📊 Risk Management

### Identified Risks

1. **Complexity Underestimation**
   - **Risk:** Multi-tier and tiered pricing logic more complex than expected
   - **Mitigation:** Break down into smaller subtasks, test calculation logic thoroughly
   - **Contingency:** Extend Sprint 2 by 1 day if needed

2. **Context Limitations**
   - **Risk:** AI context limits during complex implementations
   - **Mitigation:** Frequent commits, use todowrite for task tracking
   - **Contingency:** Split complex stories across multiple sessions

3. **Dependency Issues**
   - **Risk:** Frontend dependency conflicts
   - **Mitigation:** Use npm/yarn audit, test after each install
   - **Contingency:** Rollback to previous working state

4. **Testing Gaps**
   - **Risk:** Insufficient test coverage for pricing calculations
   - **Mitigation:** Write tests alongside implementation (TDD)
   - **Contingency:** Allocate extra time for testing on Day 5

---

## 📈 Definition of Done (Sprint 2)

A story is considered **Done** when:

1. ✅ All Acceptance Criteria implemented
2. ✅ Code committed and pushed to remote
3. ✅ Unit tests written and passing (>90% coverage)
4. ✅ Code review completed (via BMAD code-review workflow)
5. ✅ Documentation updated (story file + technical docs)
6. ✅ No critical bugs or security issues
7. ✅ Deployable to staging environment

---

## 🎯 Sprint 2 Metrics

### Target Metrics
- **Velocity:** 37 points (committed)
- **Quality:** >70% code coverage
- **Defect Rate:** <5% stories requiring rework
- **Cycle Time:** <1 day per story average

### Tracking
- **Daily Standup:** End of each day (self-sync)
- **Burndown Chart:** Track story completion daily
- **Velocity Tracking:** Compare committed vs completed
- **Quality Metrics:** Test coverage reports

---

## 📝 Sprint 2 Ceremonies

### Planning (Done)
- **Date:** 2026-02-25
- **Duration:** 2 hours
- **Output:** This document

### Daily Standup (Self-sync)
- **Time:** End of each day
- **Format:** What did I do? What's next? Blockers?

### Demo (Scheduled)
- **Date:** 2026-03-02 (Day 5, 4:00 PM)
- **Duration:** 1 hour
- **Audience:** Stakeholders
- **Format:** Live demo of all 4 stories

### Retrospective (Scheduled)
- **Date:** 2026-03-02 (Day 5, 5:00 PM)
- **Duration:** 1 hour
- **Focus:** What went well? What to improve? Action items?

---

## 🚀 Sprint 2 Kickoff

**Ready to Start:** ✅  
**Stories Committed:** 4 Epic-2 + 5 Tech Debt items  
**Capacity Check:** 66% of available capacity ✅  
**Risk Level:** Medium (manageable)  
**Team Readiness:** 100%

**Let's make Sprint 2 even better than Sprint 1! 🚀**

---

**Approved by:**
- **Product Owner:** [Pending Approval]
- **Scrum Master:** [Pending Approval]  
- **Development Team:** [Pending Approval]

**Date:** 2026-02-25
