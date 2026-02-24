<template>
  <el-dialog
    :model-value="visible"
    title="客户详情"
    width="900px"
    @close="handleClose"
  >
    <el-descriptions :column="2" border v-if="customer">
      <el-descriptions-item label="公司名称" :span="2">
        {{ customer.company_name }}
      </el-descriptions-item>
      <el-descriptions-item label="联系人">
        {{ customer.contact_name }}
      </el-descriptions-item>
      <el-descriptions-item label="联系电话">
        {{ customer.contact_phone }}
      </el-descriptions-item>
      <el-descriptions-item label="电子邮箱">
        {{ customer.email || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="公司网站">
        <el-link v-if="customer.website" :href="customer.website" target="_blank" type="primary">
          {{ customer.website }}
        </el-link>
        <span v-else>-</span>
      </el-descriptions-item>
      <el-descriptions-item label="统一社会信用代码">
        {{ customer.credit_code || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="客户类型">
        {{ customer.customer_type === 'enterprise' ? '企业' : '个人' }}
      </el-descriptions-item>
      <el-descriptions-item label="所属行业">
        {{ customer.industry || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="客户等级">
        <el-tag :type="getLevelType(customer.level)">
          {{ getLevelLabel(customer.level) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="客户状态">
        <el-tag :type="getStatusType(customer.status)">
          {{ getStatusLabel(customer.status) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="来源渠道">
        {{ getSourceLabel(customer.source) }}
      </el-descriptions-item>
      <el-descriptions-item label="省份">
        {{ customer.province || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="城市">
        {{ customer.city || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="详细地址" :span="2">
        {{ customer.address || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="ERP 系统">
        {{ customer.erp_system || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="ERP 客户代码">
        {{ customer.erp_customer_code || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">
        {{ customer.remarks || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间">
        {{ formatDate(customer.created_at) }}
      </el-descriptions-item>
      <el-descriptions-item label="更新时间">
        {{ formatDate(customer.updated_at) }}
      </el-descriptions-item>
    </el-descriptions>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleEdit">
        <el-icon><Edit /></el-icon>
        编辑
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { Edit } from '@element-plus/icons-vue'
import { type Customer } from '@/api/customer'

interface Props {
  visible: boolean
  customer: Customer | null
}

const props = withDefaults(defineProps<Props>(), {
  customer: null
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'edit', customer: Customer): void
}>()

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

const getSourceLabel = (source: string) => {
  const labels: Record<string, string> = {
    direct: '直接开发',
    referral: '推荐',
    marketing: '市场推广'
  }
  return labels[source] || source
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleEdit = () => {
  if (props.customer) {
    emit('edit', props.customer)
  }
}
</script>

<style scoped>
:deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
}
</style>
