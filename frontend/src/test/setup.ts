// Vitest test setup file
import { config } from '@vue/test-utils'
import { beforeAll, vi } from 'vitest'

// Mock echarts globally
vi.mock('echarts', () => ({
  default: {
    init: vi.fn(() => ({
      setOption: vi.fn(),
      dispose: vi.fn(),
      resize: vi.fn(),
      clear: vi.fn()
    }))
  }
}))

// Mock window objects - runs before all tests
beforeAll(() => {
  // Mock matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    }))
  })

  // Mock innerWidth
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: 1024
  })
})

// Enable slot rendering for all stubs by default
config.global.renderStubDefaultSlot = true

// Global test setup - stub Arco Design components to avoid compatibility issues
config.global.stubs = {
  RouterLink: {
    template: '<a :href="to" class="nav-item"><slot /></a>',
    props: ['to']
  },
  // Stub common Arco Design components with proper rendering
  ATag: {
    template: '<span class="arco-tag"><slot /></span>',
    props: ['color', 'size', 'bordered']
  },
  AButton: {
    template: '<button class="arco-btn"><slot /></button>',
    props: ['type', 'size', 'shape']
  },
  ATable: {
    template: '<table class="arco-table"><thead><slot name="header" /></thead><tbody><slot /></tbody></table>',
    props: ['data', 'bordered', 'striped', 'size', 'pagination']
  },
  ATableColumn: {
    template: '<th><slot /></th>',
    props: ['title', 'dataIndex', 'width', 'sortable']
  },
  AInput: {
    template: '<input class="arco-input" :placeholder="placeholder" :value="modelValue" /><slot />',
    props: ['placeholder', 'modelValue', 'disabled', 'allowClear']
  },
  ASelect: {
    template: '<select class="arco-select"><slot /></select>',
    props: ['modelValue', 'placeholder', 'disabled']
  },
  AOption: {
    template: '<option :value="value"><slot /></option>',
    props: ['value', 'label', 'disabled']
  },
  APagination: {
    template: '<div class="arco-pagination"><slot /></div>',
    props: ['current', 'pageSize', 'total']
  },
  AForm: {
    template: '<form class="arco-form"><slot /></form>',
    props: ['model', 'layout']
  },
  AFormItem: {
    template: '<div class="arco-form-item"><slot /></div>',
    props: ['label', 'field', 'rules']
  },
  AModal: {
    template: '<div class="arco-modal"><slot /></div>',
    props: ['visible', 'title']
  },
  ACard: {
    template: '<div class="arco-card"><slot /></div>',
    props: ['title', 'bordered']
  },
  ADescriptions: {
    template: '<dl class="arco-descriptions"><slot /></dl>',
    props: ['column', 'bordered']
  },
  ADescriptionsItem: {
    template: '<div class="arco-descriptions-item"><slot /></div>',
    props: ['label', 'span']
  },
  AAlert: true,
  ARow: {
    template: '<div class="arco-row"><slot /></div>',
    props: ['gutter']
  },
  ACol: {
    template: '<div class="arco-col"><slot /></div>',
    props: ['span']
  },
  ADivider: true,
  ATextarea: true,
  ASpace: true,
  ALink: true,
  ATooltip: true,
  ADatepicker: true,
  ATreeSelect: true,
  ATimeline: true,
  ATimelineItem: true,
  AList: true,
  AListItem: true,
  ADropdown: true,
  ADropdownItem: true,
  AMenu: true,
  AMenuItem: true,
  ABadge: true,
  AAvatar: true,
  AProgress: true,
  ASpin: true,
  ASkeleton: true,
  AStatistic: true,
  APopover: true,
  APopconfirm: true,
  ADrawer: true,
  AUpload: true,
  ACascader: true,
  ARadio: true,
  ARadioGroup: true,
  ACascaderPanel: true,
  ACheckbox: true,
  ACheckboxGroup: true,
  ADatePicker: true,
  ARangePicker: true,
  AInputNumber: true,
  ARate: true,
  ASlider: true,
  ATransfer: true,
  ATabs: true,
  ATabPane: true,
  ACollapse: true,
  ACollapseItem: true,
  AComment: true,
  AEmpty: true,
  ACalendar: true,
  AImage: true,
  AImagePreview: true,
  // Icon components
  IconSearch: true,
  IconPlus: true,
  IconUser: true,
  IconPhone: true,
  IconLocation: true,
  IconFile: true,
  IconBar: true,
  IconDesktop: true,
  IconEdit: true,
  IconUp: true,
  IconDown: true,
  IconRefresh: true,
  IconStar: true,
  IconFolder: true,
  IconQuestionCircle: true,
  IconClose: true,
  IconCheck: true,
  IconEye: true,
  IconDelete: true,
  IconMore: true,
  IconExport: true,
  IconImport: true
}
