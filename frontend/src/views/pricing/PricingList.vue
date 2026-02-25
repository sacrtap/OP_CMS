<template>
  <div class="pricing-list">
    <div class="header-actions">
      <h2 class="page-title">定价配置</h2>
      <div class="actions">
        <a-button type="primary" @click="handleAdd">
          <icon-plus />
          新增定价
        </a-button>
      </div>

    <a-table :data="pricingConfigs" :loading="loading">
      <a-table-column title="配置名称" data-index="name" :width="150" />
      <a-table-column title="客户 ID" data-index="customer_id" :width="100" />
      <a-table-column title="设备系列" :width="80">
        <template #cell="{ record }">
          <a-tag :color="getSeriesType(record.device_series)">{{ record.device_series }}</a-tag>
        </template>
      </a-table-column>
      <a-table-column title="定价模式" :width="100">
        <template #cell="{ record }">
          <a-tag>{{ getPriceModelLabel(record.price_model) }}</a-tag>
        </template>
      </a-table-column>
      <a-table-column title="单价" :width="100">
        <template #cell="{ record }">
          ¥{{ record.unit_price.toFixed(4) }}
        </template>
      </a-table-column>
      <a-table-column title="状态" :width="80">
        <template #cell="{ record }">
          <a-tag :color="record.is_active ? 'green' : 'gray'">
            {{ record.is_active ? '启用' : '禁用' }}
          </a-tag>
        </template>
      </a-table-column>
      <a-table-column title="操作" :width="200" fixed="right">
        <template #cell="{ record }">
          <a-space>
            <a-button type="text" size="small" @click="handleEdit(record)">编辑</a-button>
            <a-button type="text" status="danger" size="small" @click="handleDelete(record)">删除</a-button>
          </a-space>
        </template>
      </a-table-column>
    </a-table>

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
    </div>

    <el-table :data="pricingConfigs" v-loading="loading" style="width: 100%">
      <el-table-column prop="name" label="配置名称" min-width="150" />
      <el-table-column prop="customer_id" label="客户 ID" width="100" />
      <el-table-column prop="device_series" label="设备系列" width="80">
        <template #default="{ row }">
          <el-tag :type="getSeriesType(row.device_series)">{{ row.device_series }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="price_model" label="定价模式" width="100">
        <template #default="{ row }">
          <el-tag>{{ getPriceModelLabel(row.price_model) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit_price" label="单价" width="100">
        <template #default="{ row }">
          ¥{{ row.unit_price.toFixed(4) }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

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

    <PricingForm
      v-if="formVisible"
      v-model:visible="formVisible"
      :pricing="selectedPricing"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message, MessageBox } from '@arco-design/web-vue'
import { pricingAPI } from '@/api/pricing'
import PricingForm from './PricingForm.vue'
import { IconPlus } from '@arco-design/web-vue/es/icon'

const loading = ref(false)
const pricingConfigs = ref<any[]>([])
const formVisible = ref(false)
const selectedPricing = ref<any>(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

const loadPricingConfigs = async () => {
  loading.value = true
  try {
    const data = await pricingAPI.listPricingConfigs({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    pricingConfigs.value = data.configs
    pagination.total = data.total
    pagination.totalPages = data.total_pages
  } catch (error) {
    Message.error('加载定价配置失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  selectedPricing.value = null
  formVisible.value = true
}

const handleEdit = (row: any) => {
  selectedPricing.value = row
  formVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await MessageBox.confirm('确定要删除此定价配置吗？', '删除确认', {
      okText: '确定',
      cancelText: '取消',
      type: 'warning'
    })
    await pricingAPI.deletePricingConfig(row.id)
    Message.success('删除成功')
    loadPricingConfigs()
  } catch (error) {
    if (error !== 'cancel') {
      Message.error('删除失败')
    }
  }
}

const handleFormSuccess = () => {
  formVisible.value = false
  Message.success('操作成功')
  loadPricingConfigs()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  loadPricingConfigs()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadPricingConfigs()
}

const getSeriesType = (series: string) => {
  const types: any = { X: 'primary', N: 'success', L: 'warning' }
  return types[series] || 'info'
}

const getPriceModelLabel = (model: string) => {
  const labels: any = { single: '单层', multi: '多层', tiered: '阶梯' }
  return labels[model] || model
}

onMounted(() => {
  loadPricingConfigs()
})
</script>

<style scoped>
.pricing-list {
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
.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
