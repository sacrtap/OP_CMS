<template>
  <div class="customer-card">
    <div class="card-header">
      <h3>{{ customer.company_name }}</h3>
      <el-tag :type="getStatusType(customer.status)" size="small">
        {{ getStatusLabel(customer.status) }}
      </el-tag>
    </div>
    
    <div class="card-body">
      <div class="info-row">
        <el-icon><User /></el-icon>
        <span>{{ customer.contact_name }}</span>
      </div>
      <div class="info-row">
        <el-icon><Phone /></el-icon>
        <span>{{ customer.contact_phone }}</span>
      </div>
      <div class="info-row">
        <el-icon><Location /></el-icon>
        <span>{{ customer.province }} {{ customer.city }}</span>
      </div>
    </div>
    
    <div class="card-footer">
      <el-button size="small" @click="handleView">查看</el-button>
      <el-button size="small" type="primary" @click="handleEdit">编辑</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Phone, Location } from '@element-plus/icons-vue'

defineProps<{
  customer: {
    id: number
    company_name: string
    contact_name: string
    contact_phone: string
    province: string
    city: string
    status: string
  }
}>()

const emit = defineEmits<{
  (e: 'view', customer: any): void
  (e: 'edit', customer: any): void
}>()

const getStatusType = (status: string) => {
  const types: any = { active: 'success', inactive: 'info', potential: 'warning' }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: any = { active: '活跃', inactive: '非活跃', potential: '潜在' }
  return labels[status] || status
}

const handleView = () => emit('view', props.customer)
const handleEdit = () => emit('edit', props.customer)
</script>

<style scoped>
.customer-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.card-body {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
}

.info-row .el-icon {
  margin-right: 8px;
  color: #999;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid #eee;
  padding-top: 12px;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .customer-card {
    padding: 12px;
  }
  
  .card-header h3 {
    font-size: 14px;
  }
  
  .info-row {
    font-size: 13px;
  }
}
</style>
