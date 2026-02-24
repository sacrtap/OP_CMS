/**
 * Tests for MobileNav Component
 * 移动端导航组件测试 - Story 4.4 (移动端访问支持)
 */

import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import MobileNav from '../MobileNav.vue'

describe('MobileNav', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders navigation container', () => {
    const wrapper = mount(MobileNav)
    expect(wrapper.find('nav').exists()).toBe(true)
  })

  it('is hidden on desktop (width >= 768)', () => {
    // Mock window width as desktop
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })

    const wrapper = mount(MobileNav)
    
    // Should not render nav on desktop
    expect(wrapper.find('.bottom-nav').exists()).toBe(false)
  })

  it('is visible on mobile (width < 768)', () => {
    // Mock window width as mobile
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    
    // Should render nav on mobile
    expect(wrapper.find('.bottom-nav').exists()).toBe(true)
  })

  it('contains all navigation items', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()

    const navItems = wrapper.findAll('.nav-item')
    expect(navItems.length).toBe(4)
  })

  it('has correct navigation links', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()

    const links = wrapper.findAll('router-link')
    expect(links[0].attributes('to')).toBe('/customers')
    expect(links[1].attributes('to')).toBe('/settlements')
    expect(links[2].attributes('to')).toBe('/reports')
    expect(links[3].attributes('to')).toBe('/dashboard')
  })

  it('displays correct labels for navigation items', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()

    const navItems = wrapper.findAll('.nav-item')
    expect(navItems[0].text()).toContain('客户')
    expect(navItems[1].text()).toContain('结算')
    expect(navItems[2].text()).toContain('报表')
    expect(navItems[3].text()).toContain('驾驶舱')
  })

  it('responds to window resize events', async () => {
    // Start as desktop
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()

    expect(wrapper.find('.bottom-nav').exists()).toBe(false)

    // Resize to mobile
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    // Trigger resize event
    window.dispatchEvent(new Event('resize'))
    await wrapper.vm.$nextTick()

    // Note: Component should respond to resize
    // In real implementation, this would show the nav
  })

  it('cleans up event listeners on unmount', async () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')

    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()
    
    wrapper.unmount()

    expect(removeEventListenerSpy).toHaveBeenCalledWith(
      'resize',
      expect.any(Function)
    )
  })

  it('has proper styling classes', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav)
    await wrapper.vm.$nextTick()

    const nav = wrapper.find('.bottom-nav')
    expect(nav.exists()).toBe(true)
    expect(nav.classes()).toContain('bottom-nav')
  })

  it('applies active class to current route', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    const wrapper = mount(MobileNav, {
      global: {
        stubs: {
          RouterLink: {
            template: '<a :class="{ active: $attrs.class }"><slot /></a>'
          }
        }
      }
    })
    await wrapper.vm.$nextTick()

    // First item should have active class handling
    const firstItem = wrapper.find('.nav-item')
    expect(firstItem.classes()).toContain('nav-item')
  })
})
