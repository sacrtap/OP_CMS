<template>
  <div class="customer-list">
    <!-- 顶部操作栏 -->
    <div class="header-actions">
      <h2 class="page-title">客户管理</h2>
      <div class="actions">
        <a-input
          v-model="searchQuery"
          placeholder="搜索公司名称或联系人"
          allow-clear
          class="search-input"
          @clear="handleSearch"
          @press-enter="handleSearch"
        >
          <template #prefix>
            <icon-search />
          </template>
        </a-input>
        <a-select
          v-model="filterStatus"
          placeholder="客户状态"
          allow-clear
          class="filter-select"
          @change="handleSearch"
        >
          <a-option value="active">活跃</a-option>
          <a-option value="inactive">非活跃</a-option>
          <a-option value="potential">潜在客户</a-option>
        </a-select>
        <a-select
          v-model="filterLevel"
          placeholder="客户等级"
          allow-clear
          class="filter-select"
          @change="handleSearch"
        >
          <a-option value="vip">VIP</a-option>
          <a-option value="standard">标准</a-option>
          <a-option value="economy">经济</a-option>
        </a-select>
        <a-button type="primary" @click="handleAdd">
          <icon-plus />
          新增客户
        </a-button>
      </div>
    </div>

    <!-- 客户列表表格 -->
    <a-table
      :data="customers"
      :loading="loading"
      @sort-change="handleSortChange"
    >
      <a-table-column title="公司名称" data-index="company_name" :width="200" sortable />
      <a-table-column title="联系人" data-index="contact_name" :width="100" />
      <a-table-column title="联系方式" data-index="contact_phone" :width="120" />
      <a-table-column title="省份" data-index="province" :width="80" />
      <a-table-column title="城市" data-index="city" :width="80" />
      <a-table-column title="客户等级" :width="80">
        <template #cell="{ record }">
          <a-tag :color="getLevelType(record.level)">
            {{ getLevelLabel(record.level) }}
          </a-tag>
        </template>
      </a-table-column>
      <a-table-column title="状态" :width="80">
        <template #cell="{ record }">
          <a-tag :color="getStatusType(record.status)">
            {{ getStatusLabel(record.status) }}
          </a-tag>
        </template>
      </a-table-column>
      <a-table-column title="创建时间" data-index="created_at" :width="160" sortable>
        <template #cell="{ record }">
          {{ formatDate(record.created_at) }}
        </template>
      </a-table-column>
      <a-table-column title="操作" :width="200" fixed="right">
        <template #cell="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleView(record)">
              查看
            </a-button>
            <a-button type="text" size="small" @click="handleEdit(record)">
              编辑
            </a-button>
            <a-button type="text" status="danger" size="small" @click="handleDelete(record)">
              删除
            </a-button>
          </a-space>
        </template>
      </a-table-column>
    </a-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <a-pagination
        v-model:current="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-size-options="[10, 20, 50, 100]"
        show-total
        show-jumper
        @change="handlePageChange"
        @page-size-change="handleSizeChange"
      />
    </div>

    <!-- 新增/编辑客户对话框 -->
    <CustomerForm
      v-if="formVisible"
      v-model:visible="formVisible"
      :customer="selectedCustomer"
      @success="handleFormSuccess"
    />

    <!-- 查看客户详情对话框 -->
    <CustomerDetail
      v-if="detailVisible"
      v-model:visible="detailVisible"
      :customer="selectedCustomer"
      @edit="handleEdit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, MessageBox } from '@arco-design/web-vue'
import { customerAPI, type Customer } from '@/api/customer'
import CustomerForm from './CustomerForm.vue'
import CustomerDetail from './CustomerDetail.vue'
import {
  IconSearch,
  IconPlus
} from '@arco-design/web-vue/es/icon'

// 状态
const loading = ref(false)
const customers = ref<Customer[]>([])
const formVisible = ref(false)
const detailVisible = ref(false)
const selectedCustomer = ref<Customer | null>(null)

// 搜索和过滤
const searchQuery = ref('')
const filterStatus = ref('')
const filterLevel = ref('')
const sortBy = ref('')
const sortOrder = ref('')

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

// 加载客户列表
const loadCustomers = async () => {
  loading.value = true
  try {
    const data = await customerAPI.listCustomers(
      pagination.page,
      pagination.pageSize,
      searchQuery.value,
      filterStatus.value,
      '', // province filter - can be added
      filterLevel.value
    )
    customers.value = data.customers
    pagination.total = data.total
    pagination.totalPages = data.total_pages
  } catch (error) {
    Message.error('加载客户列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadCustomers()
}

// 分页处理
const handlePageChange = (page: number) => {
  pagination.page = page
  loadCustomers()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadCustomers()
}

// 排序处理
const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortBy.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  loadCustomers()
}

// 新增客户
const handleAdd = () => {
  selectedCustomer.value = null
  formVisible.value = true
}

// 查看客户详情
const handleView = (customer: Customer) => {
  selectedCustomer.value = customer
  detailVisible.value = true
}

// 编辑客户
const handleEdit = (customer: Customer) => {
  selectedCustomer.value = customer
  formVisible.value = true
}

// 删除客户
const handleDelete = async (customer: Customer) => {
  try {
    await MessageBox.confirm(
      `确定要删除客户 "${customer.company_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        okText: '确定',
        cancelText: '取消',
        type: 'warning'
      }
    )
    
    await customerAPI.deleteCustomer(customer.customer_id)
    Message.success('删除成功')
    loadCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      Message.error('删除失败')
      console.error(error)
    }
  }
}

// 表单成功回调
const handleFormSuccess = () => {
  formVisible.value = false
  Message.success('操作成功')
  loadCustomers()
}

// 辅助函数
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const types: Record<string, 'success' | 'info' | 'warning'> = {
    active: 'success',
    inactive: 'info',
    potential: 'warning'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    active: '活跃',
    inactive: '非活跃',
    potential: '潜在'
  }
  return labels[status] || status
}

const getLevelType = (level: string) => {
  const types: Record<string, 'success' | 'warning' | 'info'> = {
    vip: 'success',
    standard: 'warning',
    economy: 'info'
  }
  return types[level] || 'info'
}

const getLevelLabel = (level: string) => {
  const labels: Record<string, string> = {
    vip: 'VIP',
    standard: '标准',
    economy: '经济'
  }
  return labels[level] || level
}

// 初始化
onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.customer-list {
  padding: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 10px;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 120px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
