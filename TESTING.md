# OP_CMS Testing Guide

## Overview

This project uses comprehensive testing frameworks for both frontend and backend:

- **Frontend**: Vitest + Vue Test Utils + jsdom
- **Backend**: pytest + pytest-cov
- **Coverage Target**: 70%+

---

## Frontend Testing

### Setup

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Install test dependencies
npm install -D vitest @vue/test-utils jsdom @vitest/coverage-v8
```

### Run Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:ui

# Run tests with coverage report
npm run test:coverage

# Run specific test file
npx vitest src/components/__tests__/HelloWorld.spec.ts
```

### Test File Structure

```
frontend/src/
├── components/
│   ├── Button.vue
│   └── __tests__/
│       └── Button.spec.ts
├── views/
│   ├── CustomerList.vue
│   └── __tests__/
│       └── CustomerList.spec.ts
├── stores/
│   ├── auth.ts
│   └── __tests__/
│       └── auth.spec.ts
└── test/
    └── setup.ts
```

### Example Test

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CustomerList from '@/views/customer/CustomerList.vue'

describe('CustomerList', () => {
  it('renders customer list', () => {
    const wrapper = mount(CustomerList, {
      props: {
        customers: [
          { id: 1, company_name: 'Test Co' }
        ]
      }
    })
    
    expect(wrapper.text()).toContain('Test Co')
  })
})
```

---

## Backend Testing

### Setup

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest backend/tests/test_customer_api.py -v

# Run specific test function
pytest backend/tests/test_customer_api.py::TestCustomerAPI::test_list_customers -v

# Run with coverage
pytest --cov=backend --cov-report=html

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Test File Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── test_customer_api.py
│   ├── test_auth.py
│   ├── test_excel_import.py
│   └── conftest.py
└── ...
```

### Example Test

```python
import pytest
from backend.models.database_models import Customer

def test_customer_creation():
    customer = Customer(
        company_name='Test Co',
        contact_name='John',
        contact_phone='13800138000'
    )
    
    assert customer.company_name == 'Test Co'
    assert customer.contact_name == 'John'
```

### Test Configuration (pytest.ini)

```ini
[pytest]
testpaths = backend/tests
python_files = test_*.py
addopts = 
    -v
    --tb=short
    --cov=backend
    --cov-report=term-missing
    --cov-fail-under=70
```

---

## Coverage Reports

### Frontend Coverage

After running `npm run test:coverage`:

```bash
# View HTML report
open coverage/index.html
```

**Coverage Thresholds:**
- Statements: 70%
- Branches: 70%
- Functions: 70%
- Lines: 70%

### Backend Coverage

After running `pytest --cov=backend`:

```bash
# View HTML report
open htmlcov/index.html
```

**Coverage Target:** 70%

---

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm install
      
      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:coverage
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install backend dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run backend tests
        run: |
          pytest --cov=backend --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Test Categories

### Unit Tests
- Test individual functions/components
- Fast execution (< 100ms per test)
- No external dependencies
- Mark with `@pytest.mark.unit`

### Integration Tests
- Test component interactions
- May require database
- Slower execution
- Mark with `@pytest.mark.integration`

### End-to-End Tests (Future)
- Test complete user workflows
- Use Playwright or Cypress
- Slowest execution
- Mark with `@pytest.mark.e2e`

---

## Best Practices

1. **Test Names**: Use descriptive names (test_[feature]_[expected_behavior])
2. **AAA Pattern**: Arrange, Act, Assert
3. **One Assertion**: One assertion per test (ideally)
4. **Isolation**: Tests should be independent
5. **Repeatable**: Tests should pass/fail consistently
6. **Fast**: Keep tests fast (< 1s per test)
7. **Coverage**: Aim for 70%+ coverage

---

## Tech Debt #5 Status

✅ **COMPLETE**

- Vitest configuration for frontend
- pytest configuration for backend  
- Test setup files created
- Coverage reporting configured
- 70% coverage threshold set

---

## Next Steps

1. Write tests for existing components
2. Add integration tests for API endpoints
3. Set up CI/CD with GitHub Actions
4. Add E2E tests with Playwright/Cypress
