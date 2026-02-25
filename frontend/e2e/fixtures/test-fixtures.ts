/**
 * E2E Test Fixtures for Epic 1 - Customer Management
 */

import { test as base, expect, Page } from '@playwright/test';

// Test data types
export interface CustomerData {
  company_name: string;
  credit_code: string;
  contact_name: string;
  contact_phone: string;
  province: string;
  city: string;
  address: string;
  email: string;
  bank_name: string;
  bank_account: string;
  status: string;
}

// Extended test fixture
export const test = base.extend<{
  page: Page;
  customerData: CustomerData;
}>({
  page: async ({ page }, use) => {
    // Setup: Navigate to app
    await page.goto('/');
    await page.waitForTimeout(2000); // Wait for app to load
    
    await use(page);
    
    // Teardown: Clear test data if needed
  },
  
  customerData: async ({}, use) => {
    // Generate unique test data
    const timestamp = Date.now();
    const testData: CustomerData = {
      company_name: `测试公司-${timestamp}`,
      credit_code: `91${Math.floor(100000000000000000 + Math.random() * 900000000000000000)}`,
      contact_name: `测试联系人-${timestamp}`,
      contact_phone: `138${Math.floor(10000000 + Math.random() * 90000000)}`,
      province: '广东省',
      city: '深圳市',
      address: `测试地址-${timestamp}`,
      email: `test${timestamp}@example.com`,
      bank_name: '中国银行',
      bank_account: `${Math.floor(100000000000 + Math.random() * 900000000000)}`,
      status: 'active',
    };
    
    await use(testData);
  },
});

// Re-export expect
export { expect };

/**
 * Helper function to fill customer form
 */
export async function fillCustomerForm(
  page: Page,
  data: CustomerData
) {
  // Fill company name
  await page.getByPlaceholder('请输入公司名称').fill(data.company_name);
  
  // Fill credit code
  await page.getByPlaceholder('请输入统一社会信用代码').fill(data.credit_code);
  
  // Fill contact name
  await page.getByPlaceholder('请输入联系人姓名').fill(data.contact_name);
  
  // Fill contact phone
  await page.getByPlaceholder('请输入联系电话').fill(data.contact_phone);
  
  // Select province
  await page.getByPlaceholder('请选择省份').click();
  await page.getByText(data.province).click();
  
  // Select city
  await page.getByPlaceholder('请选择城市').click();
  await page.getByText(data.city).click();
  
  // Fill address
  await page.getByPlaceholder('请输入详细地址').fill(data.address);
  
  // Fill email
  await page.getByPlaceholder('请输入邮箱').fill(data.email);
  
  // Fill bank name
  await page.getByPlaceholder('请输入开户行').fill(data.bank_name);
  
  // Fill bank account
  await page.getByPlaceholder('请输入银行账号').fill(data.bank_account);
}

/**
 * Helper function to verify customer data in table
 */
export async function verifyCustomerInTable(
  page: Page,
  data: Partial<CustomerData>
) {
  // Search for customer
  const searchInput = page.getByPlaceholder('搜索客户...');
  await searchInput.fill(data.company_name!);
  await page.waitForTimeout(1000);
  
  // Verify customer appears in table
  const table = page.locator('.arco-table');
  await expect(table).toBeVisible();
  
  // Verify company name appears
  await expect(page.getByText(data.company_name!)).toBeVisible();
}
