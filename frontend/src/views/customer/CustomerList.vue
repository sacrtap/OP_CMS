<template>
  <div class="customer-list">
    <!-- 顶部操作栏 -->
    <div class="header-actions">
      <h2 class="page-title">客户管理</h2>
      <div class="actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索公司名称或联系人"
          clearable
          class="search-input"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filterStatus"
          placeholder="客户状态"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="活跃" value="active" />
          <el-option label="非活跃" value="inactive" />
          <el-option label="潜在客户" value="potential" />
        </el-select>
        <el-select
          v-model="filterLevel"
          placeholder="客户等级"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="VIP" value="vip" />
          <el-option label="标准" value="standard" />
          <el-option label="经济" value="economy" />
        </el-select>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增客户
        </el-button>
      </div>
    </div>

    <!-- 客户列表表格 -->
    <el-table
      :data="customers"
      v-loading="loading"
      style="width: 100%"
      @sort-change="handleSortChange"
    >
      <el-table-column prop="company_name" label="公司名称" min-width="200" sortable="custom" />
      <el-table-column prop="contact_name" label="联系人" width="100" />
      <el-table-column prop="contact_phone" label="联系方式" width="120" />
      <el-table-column prop="province" label="省份" width="80" />
      <el-table-column prop="city" label="城市" width="80" />
      <el-table-column label="客户等级" width="80">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)">
            {{ getLevelLabel(row.level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" sortable="custom">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleView(row)">
            查看
          </el-button>
          <el-button link type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
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
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { customerAPI, type Customer } from '@/api/customer'
import CustomerForm from './CustomerForm.vue'
import CustomerDetail from './CustomerDetail.vue'

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
    ElMessage.error('加载客户列表失败')
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
    await ElMessageBox.confirm(
      `确定要删除客户 "${customer.company_name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await customerAPI.deleteCustomer(customer.customer_id)
    ElMessage.success('删除成功')
    loadCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 表单成功回调
const handleFormSuccess = () => {
  formVisible.value = false
  ElMessage.success('操作成功')
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
