<template>
  <a-modal
    :visible="visible"
    title="生成账单"
    width="600px"
    @cancel="handleClose"
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      :label-col-props="{ span: 8 }"
      :wrapper-col-props="{ span: 16 }"
    >
      <a-form-item label="结算周期开始" field="period_start">
        <a-date-picker
          v-model="formData.period_start"
          placeholder="选择开始日期"
          format="YYYY-MM-DD"
          style="width: 100%"
        />
      </a-form-item>

      <a-form-item label="结算周期结束" field="period_end">
        <a-date-picker
          v-model="formData.period_end"
          placeholder="选择结束日期"
          format="YYYY-MM-DD"
          style="width: 100%"
        />
      </a-form-item>

      <a-form-item label="客户选择" field="customer_ids">
        <a-select
          v-model="formData.customer_ids"
          multiple
          placeholder="选择客户（留空表示全部）"
          style="width: 100%"
        >
          <!-- TODO: Load customers from API -->
          <a-option value="">全部客户</a-option>
        </a-select>
      </a-form-item>

      <a-alert type="info" style="margin-top: 20px">
        账单生成说明
        <template #content>
          <ul>
            <li>系统将根据客户的价格配置自动计算账单金额</li>
            <li>支持单层、多层、阶梯三种定价模式</li>
            <li>生成过程中可随时取消</li>
          </ul>
        </template>
      </a-alert>
    </a-form>

    <template #footer>
      <a-button @click="handleClose">取消</a-button>
      <a-button type="primary" @click="handleSubmit" :loading="submitting">
        生成账单
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message, type FormInstance, type FormRules } from '@arco-design/web-vue'
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
    { required: true, message: '请选择结算周期开始日期', trigger: 'blur' }
  ],
  period_end: [
    { required: true, message: '请选择结算周期结束日期', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate()
  if (!valid) return

  // Validate date range
  if (formData.period_start && formData.period_end) {
    const start = new Date(formData.period_start)
    const end = new Date(formData.period_end)
    if (start > end) {
      Message.error('结算周期开始日期不能晚于结束日期')
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
    Message.error('账单生成失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}
</script>
