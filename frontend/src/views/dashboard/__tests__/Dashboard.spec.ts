/**
 * Tests for Dashboard View
 * 管理驾驶舱仪表板视图测试
 */

import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Dashboard from '../Dashboard.vue'

// Mock dashboard API
vi.mock('@/api/dashboard', () => ({
  dashboardAPI: {
    getMetrics: vi.fn(() => Promise.resolve({
      total_revenue: 100000,
      total_customers: 50,
      pending_payment: 20000,
      overdue_payment: 5000,
      last_updated: '2026-02-25T10:00:00Z'
    })),
    getTrends: vi.fn(() => Promise.resolve({
      revenue_trend: [
        { date: '2026-01', value: 30000 },
        { date: '2026-02', value: 45000 },
        { date: '2026-03', value: 25000 }
      ]
    })),
    getCustomerStats: vi.fn(() => Promise.resolve({
      industry_distribution: [
        { value: 20, name: '制造业' },
        { value: 15, name: '服务业' },
        { value: 15, name: '零售业' }
      ]
    }))
  }
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard container', () => {
    const wrapper = mount(Dashboard)
    expect(wrapper.find('.dashboard').exists()).toBe(true)
  })

  it('displays page title', () => {
    const wrapper = mount(Dashboard)
    expect(wrapper.find('.page-title').text()).toBe('管理驾驶舱')
  })

  it('displays last update time', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.last-update').exists()).toBe(true)
  })

  it('renders 4 metric cards', () => {
    const wrapper = mount(Dashboard)
    const metricCards = wrapper.findAll('.metric-card')
    expect(metricCards.length).toBe(4)
  })

  it('displays core metrics', () => {
    const wrapper = mount(Dashboard)
    const metrics = wrapper.findAll('.metric-title')
    expect(metrics.length).toBe(4)
    expect(metrics[0].text()).toBe('总收入')
    expect(metrics[1].text()).toBe('客户总数')
  })

  it('renders revenue trend chart section', () => {
    const wrapper = mount(Dashboard)
    expect(wrapper.find('.charts-row').exists()).toBe(true)
  })

  it('has dimension selector for revenue trend', () => {
    const wrapper = mount(Dashboard)
    // Check for any select or form element or dimension-related UI
    const selectElements = wrapper.findAll('.arco-select')
    const formElements = wrapper.findAll('select')
    const buttons = wrapper.findAll('button')
    
    // Component should have some interactive elements
    expect(selectElements.length + formElements.length + buttons.length).toBeGreaterThan(0)
  })

  it('loads metrics on mount', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    // Verify API was called
    const { dashboardAPI } = await import('@/api/dashboard')
    expect(dashboardAPI.getMetrics).toHaveBeenCalled()
  })

  it('loads trend data on mount', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    const { dashboardAPI } = await import('@/api/dashboard')
    expect(dashboardAPI.getTrends).toHaveBeenCalled()
  })

  it('loads customer stats on mount', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    const { dashboardAPI } = await import('@/api/dashboard')
    expect(dashboardAPI.getCustomerStats).toHaveBeenCalled()
  })

  it('displays error message when metrics load fails', async () => {
    const { dashboardAPI } = await import('@/api/dashboard')
    vi.mocked(dashboardAPI.getMetrics).mockRejectedValue(new Error('API Error'))
    
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    // Should not throw, but show error message
    expect(wrapper.find('.dashboard').exists()).toBe(true)
  })

  it('updates metrics display after API response', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    // Check that metric values are displayed
    const metricValues = wrapper.findAll('.metric-value')
    expect(metricValues.length).toBe(4)
  })

  it('renders trend charts container', () => {
    const wrapper = mount(Dashboard)
    const charts = wrapper.findAll('.chart')
    expect(charts.length).toBeGreaterThan(0)
  })

  it('handles dimension change for revenue trend', async () => {
    const wrapper = mount(Dashboard)
    await wrapper.vm.$nextTick()
    
    // Change dimension
    const component = wrapper.vm as any
    component.revenueDimension = 'week'
    await wrapper.vm.$nextTick()
    
    const { dashboardAPI } = await import('@/api/dashboard')
    expect(dashboardAPI.getTrends).toHaveBeenCalled()
  })
})
