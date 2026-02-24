<template>
  <el-dialog
    :model-value="visible"
    title="生成账单"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="结算周期开始" prop="period_start">
        <el-date-picker
          v-model="formData.period_start"
          type="date"
          placeholder="选择开始日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="结算周期结束" prop="period_end">
        <el-date-picker
          v-model="formData.period_end"
          type="date"
          placeholder="选择结束日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="客户选择" prop="customer_ids">
        <el-select
          v-model="formData.customer_ids"
          multiple
          placeholder="选择客户（留空表示全部）"
          style="width: 100%"
        >
          <!-- TODO: Load customers from API -->
          <el-option label="全部客户" :value="[]" />
        </el-select>
      </el-form-item>

      <el-alert
        title="账单生成说明"
        type="info"
        :closable="false"
        style="margin-top: 20px"
      >
        <p>1. 系统将根据客户的价格配置自动计算账单金额</p>
        <p>2. 支持单层、多层、阶梯三种定价模式</p>
        <p>3. 生成过程中可随时取消</p>
      </el-alert>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        生成账单
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { settlementAPI } from '@/api/settlement'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}>()

const formRef = ref<FormInstance>()
const submitting = ref(false)

const formData = reactive({
  period_start: '',
  period_end: '',
  customer_ids: [] as number[]
})

const formRules: FormRules = {
  period_start: [
    { required: true, message: '请选择结算周期开始日期', trigger: 'change' }
  ],
  period_end: [
    { required: true, message: '请选择结算周期结束日期', trigger: 'change' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // Validate date range
    if (formData.period_start && formData.period_end) {
      const start = new Date(formData.period_start)
      const end = new Date(formData.period_end)
      if (start > end) {
        ElMessage.error('结算周期开始日期不能晚于结束日期')
        return
      }
    }

    submitting.value = true
    try {
      await settlementAPI.generateSettlement({
        period_start: formData.period_start,
        period_end: formData.period_end,
        customer_ids: formData.customer_ids.length > 0 ? formData.customer_ids : undefined
      })
      
      emit('success')
      handleClose()
    } catch (error) {
      ElMessage.error('账单生成失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}
</script>
