/**
 * Tests for ResponsiveTable Component
 * 响应式表格组件测试 - Story 4.4 (移动端访问支持)
 */

import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import ResponsiveTable from '../components/ResponsiveTable.vue'
import CustomerCard from '../components/CustomerCard.vue'

describe('ResponsiveTable', () => {
  const mockData = [
    {
      id: 1,
      company_name: '公司 1',
      contact_name: '联系人 1',
      contact_phone: '13800138001',
      province: '广东省',
      city: '深圳市',
      status: 'active'
    },
    {
      id: 2,
      company_name: '公司 2',
      contact_name: '联系人 2',
      contact_phone: '13800138002',
      province: '广东省',
      city: '广州市',
      status: 'inactive'
    }
  ]

  it('renders table container', () => {
    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    expect(wrapper.find('.responsive-table-container').exists()).toBe(true)
  })

  it('shows table view on desktop', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    expect(wrapper.find('.el-table').exists()).toBe(true)
    expect(wrapper.find('.mobile-card-list').exists()).toBe(false)
  })

  it('shows card view on mobile', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    expect(wrapper.find('.el-table').exists()).toBe(false)
    expect(wrapper.find('.mobile-card-list').exists()).toBe(true)
  })

  it('renders CustomerCard components for each item on mobile', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()

    const cards = wrapper.findAllComponents(CustomerCard)
    expect(cards.length).toBe(2)
  })

  it('passes customer data to CustomerCard components', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()

    const cards = wrapper.findAllComponents(CustomerCard)
    expect(cards[0].props('customer')).toEqual(mockData[0])
    expect(cards[1].props('customer')).toEqual(mockData[1])
  })

  it('emits view event from CustomerCard', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()

    const card = wrapper.findComponent(CustomerCard)
    await card.vm.$emit('view', mockData[0])

    expect(wrapper.emitted('view')).toBeTruthy()
    expect(wrapper.emitted('view')?.[0]).toEqual([mockData[0]])
  })

  it('emits edit event from CustomerCard', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()

    const card = wrapper.findComponent(CustomerCard)
    await card.vm.$emit('edit', mockData[0])

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([mockData[0]])
  })

  it('responds to window resize events', async () => {
    // Start as desktop
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.find('.el-table').exists()).toBe(true)

    // Resize to mobile
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()

    // Should switch to card view
    expect(wrapper.find('.mobile-card-list').exists()).toBe(true)
  })

  it('handles empty data array', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: []
      }
    })

    expect(wrapper.find('.mobile-card-list').exists()).toBe(true)
    const cards = wrapper.findAllComponents(CustomerCard)
    expect(cards.length).toBe(0)
  })

  it('forwards Element Plus table attributes', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData,
        border: true,
        stripe: true
      },
      attrs: {
        border: true,
        stripe: true
      }
    })

    const table = wrapper.find('.el-table')
    expect(table.attributes('border')).toBe('true')
    expect(table.attributes('stripe')).toBe('true')
  })

  it('cleans up event listeners on unmount', async () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(ResponsiveTable, {
      props: {
        data: mockData
      }
    })

    await wrapper.vm.$nextTick()
    wrapper.unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'resize',
      expect.any(Function)
    )
  })
})
