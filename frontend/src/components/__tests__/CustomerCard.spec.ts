/**
 * Tests for CustomerCard Component
 * 客户卡片组件测试 - Story 4.4 (移动端访问支持)
 */

import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import CustomerCard from '../components/CustomerCard.vue'
import { User, Phone, Location } from '@element-plus/icons-vue'

describe('CustomerCard', () => {
  const mockCustomer = {
    id: 1,
    company_name: '测试公司',
    contact_name: '张三',
    contact_phone: '13800138000',
    province: '广东省',
    city: '深圳市',
    status: 'active'
  }

  it('renders customer company name', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    expect(wrapper.find('.card-header h3').text()).toBe('测试公司')
  })

  it('renders customer contact information', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    const infoRows = wrapper.findAll('.info-row')
    expect(infoRows[0].text()).toContain('张三')
    expect(infoRows[1].text()).toContain('13800138000')
    expect(infoRows[2].text()).toContain('广东省 深圳市')
  })

  it('displays correct status tag for active customer', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: { ...mockCustomer, status: 'active' }
      }
    })

    const tag = wrapper.find('.el-tag')
    expect(tag.classes()).toContain('el-tag--success')
    expect(tag.text()).toBe('活跃')
  })

  it('displays correct status tag for inactive customer', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: { ...mockCustomer, status: 'inactive' }
      }
    })

    const tag = wrapper.find('.el-tag')
    expect(tag.classes()).toContain('el-tag--info')
    expect(tag.text()).toBe('非活跃')
  })

  it('displays correct status tag for potential customer', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: { ...mockCustomer, status: 'potential' }
      }
    })

    const tag = wrapper.find('.el-tag')
    expect(tag.classes()).toContain('el-tag--warning')
    expect(tag.text()).toBe('潜在')
  })

  it('displays default status tag for unknown status', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: { ...mockCustomer, status: 'unknown' }
      }
    })

    const tag = wrapper.find('.el-tag')
    expect(tag.classes()).toContain('el-tag--info')
    expect(tag.text()).toBe('unknown')
  })

  it('emits view event when view button clicked', async () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    const viewButton = wrapper.findAll('button')[0]
    await viewButton.trigger('click')

    expect(wrapper.emitted('view')).toBeTruthy()
    expect(wrapper.emitted('view')?.[0]).toEqual([mockCustomer])
  })

  it('emits edit event when edit button clicked', async () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    const editButton = wrapper.findAll('button')[1]
    await editButton.trigger('click')

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')?.[0]).toEqual([mockCustomer])
  })

  it('has proper styling structure', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    expect(wrapper.find('.customer-card').exists()).toBe(true)
    expect(wrapper.find('.card-header').exists()).toBe(true)
    expect(wrapper.find('.card-body').exists()).toBe(true)
    expect(wrapper.find('.card-footer').exists()).toBe(true)
  })

  it('displays all required icons', () => {
    const wrapper = mount(CustomerCard, {
      props: {
        customer: mockCustomer
      }
    })

    const icons = wrapper.findAll('.el-icon')
    expect(icons.length).toBeGreaterThanOrEqual(3)
  })

  it('handles missing customer fields gracefully', () => {
    const incompleteCustomer = {
      id: 2,
      company_name: 'Incomplete Company',
      contact_name: '',
      contact_phone: '',
      province: '',
      city: '',
      status: ''
    }

    const wrapper = mount(CustomerCard, {
      props: {
        customer: incompleteCustomer
      }
    })

    expect(wrapper.find('.card-header h3').text()).toBe('Incomplete Company')
  })
})
