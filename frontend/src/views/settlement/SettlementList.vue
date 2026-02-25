<template>
  <div class="settlement-list">
    <div class="header-actions">
      <h2 class="page-title">结算管理</h2>
      <div class="actions">
        <a-button type="primary" @click="handleGenerate">
          <icon-plus />
          生成账单
        </a-button>
      </div>
    </div>

    <!-- 过滤条件 -->
    <a-card class="filter-card">
      <a-form :inline="true">
        <a-form-item label="客户 ID">
          <a-input v-model="filters.customer_id" placeholder="请输入客户 ID" allow-clear />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model="filters.status" placeholder="全部" allow-clear>
            <a-option value="pending">待结算</a-option>
            <a-option value="approved">已审核</a-option>
            <a-option value="paid">已付款</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="操作">
          <a-button type="primary" @click="handleSearch">查询</a-button>
          <a-button @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 账单列表 -->
    <a-table :data="settlements" :loading="loading">
      <a-table-column title="账单 ID" data-index="record_id" :width="200" />
      <a-table-column title="客户 ID" data-index="customer_id" :width="100" />
      <a-table-column title="结算周期" :width="200">
        <template #cell="{ record }">
          {{ formatDate(record.period_start) }} - {{ formatDate(record.period_end) }}
        </template>
      </a-table-column>
      <a-table-column title="定价模式" :width="100">
        <template #cell="{ record }">
          <a-tag>{{ getPriceModelLabel(record.price_model) }}</a-tag>
        </template>
      </a-table-column>
      <a-table-column title="用量" data-index="usage_quantity" :width="100" />
      <a-table-column title="总金额" :width="100">
        <template #cell="{ record }">
          ¥{{ record.total_amount?.toFixed(2) }}
        </template>
      </a-table-column>
      <a-table-column title="状态" :width="80">
        <template #cell="{ record }">
          <a-tag :color="getStatusType(record.status)">
            {{ getStatusLabel(record.status) }}
          </a-tag>
        </template>
      </a-table-column>
      <a-table-column title="生成时间" data-index="created_at" :width="160">
        <template #cell="{ record }">
          {{ formatDateTime(record.created_at) }}
        </template>
      </a-table-column>
      <a-table-column title="操作" :width="150" fixed="right">
        <template #cell="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleView(record)">查看</a-button>
            <a-button type="text" size="small" @click="handleExport(record)">导出</a-button>
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
import { Message } from '@arco-design/web-vue'
import { settlementAPI } from '@/api/settlement'
import GenerateSettlement from './GenerateSettlement.vue'
import SettlementDetail from './SettlementDetail.vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'

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
    Message.error('加载账单列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadSettlements()
}

// 重置
const handleReset = () => {
  filters.customer_id = ''
  filters.status = ''
  handleSearch()
}

// 生成账单
const handleGenerate = () => {
  generateVisible.value = true
}

const handleGenerateSuccess = () => {
  generateVisible.value = false
  Message.success('账单生成成功')
  loadSettlements()
}

// 查看详情
const handleView = (row: any) => {
  selectedSettlement.value = row
  detailVisible.value = true
}

// 导出
const handleExport = (row: any) => {
  // TODO: Implement export functionality
  Message.info('导出功能开发中')
}

// 分页处理
const handlePageChange = (page: number) => {
  pagination.page = page
  loadSettlements()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadSettlements()
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
