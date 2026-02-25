<template>
  <a-modal
    :visible="visible"
    :title="isEdit ? '编辑客户' : '新增客户'"
    width="800px"
    @cancel="handleClose"
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      :label-col-props="{ span: 7 }"
      :wrapper-col-props="{ span: 17 }"
      class="customer-form"
    >
      <!-- 必填字段 -->
      <a-row :gutter="20">
        <a-col :span="12">
          <a-form-item label="公司名称" field="company_name">
            <a-input v-model="formData.company_name" placeholder="请输入公司名称" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="联系人" field="contact_name">
            <a-input v-model="formData.contact_name" placeholder="请输入联系人姓名" />
          </a-form-item>
        </a-col>
      </a-row>

      <a-row :gutter="20">
        <a-col :span="12">
          <a-form-item label="联系电话" field="contact_phone">
            <a-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="电子邮箱" field="email">
            <a-input v-model="formData.email" placeholder="请输入电子邮箱" />
          </a-form-item>
        </a-col>
      </a-row>

      <!-- 企业信息 -->
      <a-divider>企业信息</a-divider>
      <a-row :gutter="20">
        <a-col :span="12">
          <a-form-item label="统一社会信用代码" field="credit_code">
            <a-input v-model="formData.credit_code" placeholder="18 位统一社会信用代码" :max-length="18" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="客户类型" field="customer_type">
            <a-select v-model="formData.customer_type" placeholder="请选择客户类型">
              <a-option value="enterprise">企业</a-option>
              <a-option value="individual">个人</a-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>

      <a-row :gutter="20">
        <a-col :span="12">
          <a-form-item label="所属行业" field="industry">
            <a-input v-model="formData.industry" placeholder="请输入所属行业" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="公司网站" field="website">
            <a-input v-model="formData.website" placeholder="请输入公司网站" />
          </a-form-item>
        </a-col>
      </a-row>

      <!-- 地址信息 -->
      <a-divider>地址信息</a-divider>
      <a-row :gutter="20">
        <a-col :span="8">
          <a-form-item label="省份" field="province">
            <a-input v-model="formData.province" placeholder="请输入省份" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="城市" field="city">
            <a-input v-model="formData.city" placeholder="请输入城市" />
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="客户等级" field="level">
            <a-select v-model="formData.level" placeholder="请选择客户等级">
              <a-option value="vip">VIP</a-option>
              <a-option value="standard">标准</a-option>
              <a-option value="economy">经济</a-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>

      <a-row :gutter="20">
        <a-col :span="24">
          <a-form-item label="详细地址" field="address">
            <a-textarea v-model="formData.address" :auto-size="{ minRows: 2, maxRows: 4 }" placeholder="请输入详细地址" />
          </a-form-item>
        </a-col>
      </a-row>

      <!-- ERP 信息 -->
      <a-divider>ERP 信息</a-divider>
      <a-row :gutter="20">
        <a-col :span="12">
          <a-form-item label="ERP 系统" field="erp_system">
            <a-input v-model="formData.erp_system" placeholder="请输入 ERP 系统名称" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="ERP 客户代码" field="erp_customer_code">
            <a-input v-model="formData.erp_customer_code" placeholder="请输入 ERP 客户代码" />
          </a-form-item>
        </a-col>
      </a-row>

      <!-- 其他信息 -->
      <a-divider>其他信息</a-divider>
      <a-row :gutter="20">
        <a-col :span="8">
          <a-form-item label="客户状态" field="status">
            <a-select v-model="formData.status" placeholder="请选择客户状态">
              <a-option value="active">活跃</a-option>
              <a-option value="inactive">非活跃</a-option>
              <a-option value="potential">潜在客户</a-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="来源渠道" field="source">
            <a-select v-model="formData.source" placeholder="请选择来源渠道">
              <a-option value="direct">直接开发</a-option>
              <a-option value="referral">推荐</a-option>
              <a-option value="marketing">市场推广</a-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="8">
          <a-form-item label="备注" field="remarks">
            <a-textarea v-model="formData.remarks" :auto-size="{ minRows: 2, maxRows: 4 }" placeholder="请输入备注" />
          </a-form-item>
        </a-col>
      </a-row>
    </a-form>

    <template #footer>
      <a-button @click="handleClose">取消</a-button>
      <a-button @click="handleDuplicateCheck" :loading="checkingDuplicate">
        检查重复
      </a-button>
      <a-button type="primary" @click="handleSubmit" :loading="submitting">
        确定
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { Message, type FormInstance, type FormRules } from '@arco-design/web-vue'
import { customerAPI, type Customer, type CustomerCreate } from '@/api/customer'

interface Props {
  visible: boolean
  customer?: Customer | null
}

const props = withDefaults(defineProps<Props>(), {
  customer: null
})

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}>()

// 表单引用
const formRef = ref<FormInstance>()
const checkingDuplicate = ref(false)
const submitting = ref(false)

// 表单数据
const formData = reactive<CustomerCreate>({
  company_name: '',
  contact_name: '',
  contact_phone: '',
  credit_code: undefined,
  customer_type: 'enterprise',
  province: undefined,
  city: undefined,
  address: undefined,
  email: undefined,
  website: undefined,
  industry: undefined,
  erp_system: undefined,
  erp_customer_code: undefined,
  status: 'active',
  level: 'standard',
  source: 'direct',
  remarks: undefined
})

// 表单验证规则
const formRules: FormRules = {
  company_name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  contact_name: [
    { required: true, message: '请输入联系人', trigger: 'blur' },
    { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^[\d\s\-\+\(\)]+$/, message: '电话格式不正确', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  credit_code: [
    { max: 50, message: '长度不能超过 50 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const isEdit = computed(() => !!props.customer)

// 监听 customer 变化，填充表单
watch(() => props.customer, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { immediate: true })

// 检查重复
const handleDuplicateCheck = async () => {
  if (!formData.company_name) {
    Message.warning('请输入公司名称')
    return
  }

  checkingDuplicate.value = true
  try {
    const result = await customerAPI.checkDuplicate(
      formData.company_name,
      formData.credit_code
    )
    
    if (result.is_duplicate) {
      Message.warning(`检测到重复：${result.duplicate_field === 'company_name' ? '公司名称' : '信用代码'} 已存在`)
    } else {
      Message.success('未检测到重复数据')
    }
  } catch (error) {
    Message.error('检查失败')
    console.error(error)
  } finally {
    checkingDuplicate.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  const valid = await formRef.value.validate()
  if (!valid) return

  submitting.value = true
  try {
    // 检查必填字段
    if (!formData.company_name || !formData.contact_name || !formData.contact_phone) {
      Message.warning('请填写必填字段')
      return
    }

    if (props.customer) {
      // 更新
      await customerAPI.updateCustomer(props.customer.customer_id, formData)
    } else {
      // 新增
      await customerAPI.createCustomer(formData)
    }
    
    emit('success')
    handleClose()
  } catch (error: any) {
    if (error.response?.status === 409) {
      Message.error('数据已存在，无法重复添加')
    } else {
      Message.error(isEdit ? '更新失败' : '创建失败')
    }
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields()
  emit('update:visible', false)
}
</script>

<style scoped>
.customer-form {
  padding: 10px 0;
}

:deep(.arco-divider-text) {
  font-weight: 600;
  font-size: 14px;
}
</style>
