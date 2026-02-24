<template>
  <div class="settlement-list">
    <div class="header-actions">
      <h2 class="page-title">结算管理</h2>
      <div class="actions">
        <el-button type="primary" @click="handleGenerate">
          <el-icon><Plus /></el-icon>
          生成账单
        </el-button>
      </div>
    </div>

    <!-- 过滤条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters">
        <el-form-item label="客户 ID">
          <el-input v-model="filters.customer_id" placeholder="请输入客户 ID" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待结算" value="pending" />
            <el-option label="已审核" value="approved" />
            <el-option label="已付款" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作">
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 账单列表 -->
    <el-table :data="settlements" v-loading="loading" style="width: 100%">
      <el-table-column prop="record_id" label="账单 ID" width="200" />
      <el-table-column prop="customer_id" label="客户 ID" width="100" />
      <el-table-column prop="period_start" label="结算周期" width="200">
        <template #default="{ row }">
          {{ formatDate(row.period_start) }} - {{ formatDate(row.period_end) }}
        </template>
      </el-table-column>
      <el-table-column prop="price_model" label="定价模式" width="100">
        <template #default="{ row }">
          <el-tag>{{ getPriceModelLabel(row.price_model) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="usage_quantity" label="用量" width="100" />
      <el-table-column prop="total_amount" label="总金额" width="100">
        <template #default="{ row }">
          ¥{{ row.total_amount?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="生成时间" width="160">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
          <el-button link type="success" size="small" @click="handleExport(row)">导出</el-button>
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

    <!-- 生成账单对话框 -->
    <GenerateSettlement
      v-if="generateVisible"
      v-model:visible="generateVisible"
      @success="handleGenerateSuccess"
    />

    <!-- 账单详情对话框 -->
    <SettlementDetail
      v-if="detailVisible"
      v-model:visible="detailVisible"
      :settlement="selectedSettlement"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { settlementAPI } from '@/api/settlement'
import GenerateSettlement from './GenerateSettlement.vue'
import SettlementDetail from './SettlementDetail.vue'

const loading = ref(false)
const settlements = ref<any[]>([])
const generateVisible = ref(false)
const detailVisible = ref(false)
const selectedSettlement = ref<any>(null)

const filters = reactive({
  customer_id: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

const loadSettlements = async () => {
  loading.value = true
  try {
    const data = await settlementAPI.listSettlements({
      page: pagination.page,
      page_size: pagination.pageSize,
      customer_id: filters.customer_id ? Number(filters.customer_id) : undefined,
      status: filters.status || undefined
    })
    settlements.value = data.settlements
    pagination.total = data.total
    pagination.totalPages = data.total_pages
  } catch (error) {
    ElMessage.error('加载账单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadSettlements()
}

const handleReset = () => {
  filters.customer_id = ''
  filters.status = ''
  handleSearch()
}

const handleGenerate = () => {
  generateVisible.value = true
}

const handleGenerateSuccess = () => {
  generateVisible.value = false
  ElMessage.success('账单生成成功')
  loadSettlements()
}

const handleView = (row: any) => {
  selectedSettlement.value = row
  detailVisible.value = true
}

const handleExport = (row: any) => {
  // TODO: Implement export functionality
  ElMessage.info('导出功能开发中')
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadSettlements()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadSettlements()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const types: any = {
    pending: 'warning',
    approved: 'success',
    paid: 'success'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: any = {
    pending: '待结算',
    approved: '已审核',
    paid: '已付款'
  }
  return labels[status] || status
}

const getPriceModelLabel = (model: string) => {
  const labels: any = {
    single: '单层',
    multi: '多层',
    tiered: '阶梯'
  }
  return labels[model] || model
}

onMounted(() => {
  loadSettlements()
})
</script>

<style scoped>
.settlement-list {
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
.filter-card {
  margin-bottom: 20px;
}
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
