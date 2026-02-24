<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑客户' : '新增客户'"
    width="800px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="140px"
      class="customer-form"
    >
      <!-- 必填字段 -->
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="公司名称" prop="company_name">
            <el-input v-model="formData.company_name" placeholder="请输入公司名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系人" prop="contact_name">
            <el-input v-model="formData.contact_name" placeholder="请输入联系人姓名" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电子邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="请输入电子邮箱" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 企业信息 -->
      <el-divider>企业信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="统一社会信用代码" prop="credit_code">
            <el-input v-model="formData.credit_code" placeholder="18 位统一社会信用代码" maxlength="18" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="客户类型" prop="customer_type">
            <el-select v-model="formData.customer_type" placeholder="请选择客户类型">
              <el-option label="企业" value="enterprise" />
              <el-option label="个人" value="individual" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="所属行业" prop="industry">
            <el-input v-model="formData.industry" placeholder="请输入所属行业" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="公司网站" prop="website">
            <el-input v-model="formData.website" placeholder="请输入公司网站" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 地址信息 -->
      <el-divider>地址信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="省份" prop="province">
            <el-input v-model="formData.province" placeholder="请输入省份" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="城市" prop="city">
            <el-input v-model="formData.city" placeholder="请输入城市" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="客户等级" prop="level">
            <el-select v-model="formData.level" placeholder="请选择客户等级">
              <el-option label="VIP" value="vip" />
              <el-option label="标准" value="standard" />
              <el-option label="经济" value="economy" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="详细地址" prop="address">
            <el-input v-model="formData.address" type="textarea" :rows="2" placeholder="请输入详细地址" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- ERP 信息 -->
      <el-divider>ERP 信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="ERP 系统" prop="erp_system">
            <el-input v-model="formData.erp_system" placeholder="请输入 ERP 系统名称" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="ERP 客户代码" prop="erp_customer_code">
            <el-input v-model="formData.erp_customer_code" placeholder="请输入 ERP 客户代码" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 其他信息 -->
      <el-divider>其他信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="客户状态" prop="status">
            <el-select v-model="formData.status" placeholder="请选择客户状态">
              <el-option label="活跃" value="active" />
              <el-option label="非活跃" value="inactive" />
              <el-option label="潜在客户" value="potential" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="来源渠道" prop="source">
            <el-select v-model="formData.source" placeholder="请选择来源渠道">
              <el-option label="直接开发" value="direct" />
              <el-option label="推荐" value="referral" />
              <el-option label="市场推广" value="marketing" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="备注" prop="remarks">
            <el-input v-model="formData.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button @click="handleDuplicateCheck" :loading="checkingDuplicate">
        检查重复
      </el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
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
    ElMessage.warning('请输入公司名称')
    return
  }

  checkingDuplicate.value = true
  try {
    const result = await customerAPI.checkDuplicate(
      formData.company_name,
      formData.credit_code
    )
    
    if (result.is_duplicate) {
      ElMessage.warning(`检测到重复：${result.duplicate_field === 'company_name' ? '公司名称' : '信用代码'} 已存在`)
    } else {
      ElMessage.success('未检测到重复数据')
    }
  } catch (error) {
    ElMessage.error('检查失败')
    console.error(error)
  } finally {
    checkingDuplicate.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      // 检查必填字段
      if (!formData.company_name || !formData.contact_name || !formData.contact_phone) {
        ElMessage.warning('请填写必填字段')
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
        ElMessage.error('数据已存在，无法重复添加')
      } else {
        ElMessage.error(isEdit ? '更新失败' : '创建失败')
      }
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
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

:deep(.el-divider__text) {
  font-weight: 600;
  font-size: 14px;
}
</style>
