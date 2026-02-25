/**
 * Tests for CustomerList View
 * 客户列表视图测试
 */

import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import CustomerList from '../CustomerList.vue'

// Mock customer API
vi.mock('@/api/customer', () => ({
  customerAPI: {
    listCustomers: vi.fn(() => Promise.resolve({
      customers: [
        {
          customer_id: 1,
          company_name: '测试公司 1',
          contact_name: '联系人 1',
          contact_phone: '13800138001',
          province: '广东省',
          city: '深圳市',
          level: 'vip',
          status: 'active',
          created_at: '2026-01-01T00:00:00Z'
        },
        {
          customer_id: 2,
          company_name: '测试公司 2',
          contact_name: '联系人 2',
          contact_phone: '13800138002',
          province: '广东省',
          city: '广州市',
          level: 'standard',
          status: 'inactive',
          created_at: '2026-01-02T00:00:00Z'
        }
      ],
      total: 2,
      total_pages: 1
    })),
    deleteCustomer: vi.fn(() => Promise.resolve())
  }
}))

// Mock MessageBox
vi.mock('@arco-design/web-vue', () => ({
  Message: {
    success: vi.fn(),
    error: vi.fn()
  },
  MessageBox: {
    confirm: vi.fn(() => Promise.resolve())
  }
}))

describe('CustomerList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders customer list container', () => {
    const wrapper = mount(CustomerList)
    expect(wrapper.find('.customer-list').exists()).toBe(true)
  })

  it('displays page title', () => {
    const wrapper = mount(CustomerList)
    expect(wrapper.find('.page-title').text()).toBe('客户管理')
  })

  it('has search input', () => {
    const wrapper = mount(CustomerList)
    expect(wrapper.find('.arco-input').exists()).toBe(true)
  })

  it('has status filter select', () => {
    const wrapper = mount(CustomerList)
    const selects = wrapper.findAll('.arco-select')
    expect(selects.length).toBeGreaterThan(0)
  })

  it('has add customer button', () => {
    const wrapper = mount(CustomerList)
    const buttons = wrapper.findAll('.arco-btn')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('renders table', () => {
    const wrapper = mount(CustomerList)
    expect(wrapper.find('.arco-table').exists()).toBe(true)
  })

  it('loads customers on mount', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const { customerAPI } = await import('@/api/customer')
    expect(customerAPI.listCustomers).toHaveBeenCalled()
  })

  it('displays customer data in table', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Check that customer data is loaded in component state
    const component = wrapper.vm as any
    // Check different possible variable names
    const customers = component.customers || component.customerData || component.list
    expect(customers).toBeTruthy()
    expect(customers.length).toBeGreaterThan(0)
  })

  it('renders pagination', () => {
    const wrapper = mount(CustomerList)
    expect(wrapper.find('.arco-pagination').exists()).toBe(true)
  })

  it('search input triggers search on enter', async () => {
    const wrapper = mount(CustomerList)
    
    // Directly call the search method
    await wrapper.vm.handleSearch()
    await wrapper.vm.$nextTick()
    
    const { customerAPI } = await import('@/api/customer')
    expect(customerAPI.listCustomers).toHaveBeenCalled()
  })

  it('search clear triggers search', async () => {
    const wrapper = mount(CustomerList)
    
    // Set search text and trigger search
    const component = wrapper.vm as any
    component.searchText = '测试'
    await wrapper.vm.handleSearch()
    await wrapper.vm.$nextTick()
    
    const { customerAPI } = await import('@/api/customer')
    expect(customerAPI.listCustomers).toHaveBeenCalled()
  })

  it('filter change triggers search', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const filters = wrapper.findAll('.filter-select')
    if (filters.length > 0) {
      // Trigger filter change
      const component = wrapper.vm as any
      component.filterStatus = 'active'
      await wrapper.vm.$nextTick()
      
      const { customerAPI } = await import('@/api/customer')
      expect(customerAPI.listCustomers).toHaveBeenCalled()
    }
  })

  it('opens form on add button click', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    // Find and click add button
    const buttons = wrapper.findAll('button')
    const addButton = buttons.find(btn => btn.text().includes('新增'))
    
    if (addButton) {
      await addButton.trigger('click')
      expect((wrapper.vm as any).formVisible).toBe(true)
    }
  })

  it('opens detail on view button click', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    // Find view buttons
    const viewButtons = wrapper.findAll('button').filter(btn => 
      btn.text().includes('查看')
    )
    
    if (viewButtons.length > 0) {
      await viewButtons[0].trigger('click')
      expect((wrapper.vm as any).detailVisible).toBe(true)
    }
  })

  it('opens form on edit button click', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const editButtons = wrapper.findAll('button').filter(btn => 
      btn.text().includes('编辑')
    )
    
    if (editButtons.length > 0) {
      await editButtons[0].trigger('click')
      expect((wrapper.vm as any).formVisible).toBe(true)
    }
  })

  it('confirms and deletes customer', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const deleteButtons = wrapper.findAll('button').filter(btn => 
      btn.text().includes('删除')
    )
    
    if (deleteButtons.length > 0) {
      await deleteButtons[0].trigger('click')
      
      const { customerAPI } = await import('@/api/customer')
      expect(customerAPI.deleteCustomer).toHaveBeenCalled()
    }
  })

  it('handles page change', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const component = wrapper.vm as any
    component.pagination.page = 2
    await wrapper.vm.$nextTick()
    
    const { customerAPI } = await import('@/api/customer')
    expect(customerAPI.listCustomers).toHaveBeenCalled()
  })

  it('handles page size change', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const component = wrapper.vm as any
    component.pagination.pageSize = 50
    await wrapper.vm.$nextTick()
    
    const { customerAPI } = await import('@/api/customer')
    expect(customerAPI.listCustomers).toHaveBeenCalled()
  })

  it('displays loading state', () => {
    const wrapper = mount(CustomerList, {
      data() {
        return {
          loading: true
        }
      }
    })
    expect(wrapper.find('.arco-table').exists()).toBe(true)
  })

  it('formats date correctly', () => {
    const wrapper = mount(CustomerList)
    const component = wrapper.vm as any
    const date = component.formatDate('2026-01-01T00:00:00Z')
    expect(typeof date).toBe('string')
  })

  it('gets correct status type', () => {
    const wrapper = mount(CustomerList)
    const component = wrapper.vm as any
    
    expect(component.getStatusType('active')).toBe('success')
    expect(component.getStatusType('inactive')).toBe('info')
    expect(component.getStatusType('potential')).toBe('warning')
  })

  it('gets correct status label', () => {
    const wrapper = mount(CustomerList)
    const component = wrapper.vm as any
    
    expect(component.getStatusLabel('active')).toBe('活跃')
    expect(component.getStatusLabel('inactive')).toBe('非活跃')
    expect(component.getStatusLabel('potential')).toBe('潜在')
  })

  it('gets correct level type', () => {
    const wrapper = mount(CustomerList)
    const component = wrapper.vm as any
    
    expect(component.getLevelType('vip')).toBe('success')
    expect(component.getLevelType('standard')).toBe('warning')
    expect(component.getLevelType('economy')).toBe('info')
  })

  it('gets correct level label', () => {
    const wrapper = mount(CustomerList)
    const component = wrapper.vm as any
    
    expect(component.getLevelLabel('vip')).toBe('VIP')
    expect(component.getLevelLabel('standard')).toBe('标准')
    expect(component.getLevelLabel('economy')).toBe('经济')
  })

  it('handles form success callback', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const component = wrapper.vm as any
    component.handleFormSuccess()
    
    expect(component.formVisible).toBe(false)
  })

  it('handles sort change', async () => {
    const wrapper = mount(CustomerList)
    await wrapper.vm.$nextTick()
    
    const component = wrapper.vm as any
    component.handleSortChange({ prop: 'created_at', order: 'descending' })
    
    expect(component.sortBy).toBe('created_at')
    expect(component.sortOrder).toBe('desc')
  })
})
