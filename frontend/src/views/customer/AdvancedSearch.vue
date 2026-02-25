<template>
  <div class="advanced-search">
    <a-card class="search-card">
      <template #title>
        <div class="card-header">
          <span>高级搜索</span>
          <a-button type="text" @click="toggleExpand">
            <icon-up v-if="expanded" />
            <icon-down v-else />
            {{ expanded ? '收起' : '展开' }}
          </a-button>
        </div>
      </template>

      <div v-show="expanded" class="search-content">
        <a-form :model="searchForm" :label-col-props="{ span: 8 }" :wrapper-col-props="{ span: 16 }">
          <a-row :gutter="20">
            <a-col :span="8">
              <a-form-item label="客户类型" field="customer_type">
                <a-select v-model="searchForm.customer_type" placeholder="全部" allow-clear>
                  <a-option value="enterprise">企业</a-option>
                  <a-option value="individual">个人</a-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="客户等级" field="level">
                <a-select v-model="searchForm.level" placeholder="全部" allow-clear>
                  <a-option value="vip">VIP</a-option>
                  <a-option value="standard">标准</a-option>
                  <a-option value="economy">经济</a-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="客户状态" field="status">
                <a-select v-model="searchForm.status" placeholder="全部" allow-clear>
                  <a-option value="active">活跃</a-option>
                  <a-option value="inactive">非活跃</a-option>
                  <a-option value="potential">潜在客户</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="20">
            <a-col :span="8">
              <a-form-item label="省份" field="province">
                <a-input v-model="searchForm.province" placeholder="请输入省份" allow-clear />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="城市" field="city">
                <a-input v-model="searchForm.city" placeholder="请输入城市" allow-clear />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="来源渠道" field="source">
                <a-select v-model="searchForm.source" placeholder="全部" allow-clear>
                  <a-option value="direct">直接开发</a-option>
                  <a-option value="referral">推荐</a-option>
                  <a-option value="marketing">市场推广</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="20">
            <a-col :span="8">
              <a-form-item label="创建时间从" field="created_from">
                <a-date-picker
                  v-model="searchForm.created_from"
                  placeholder="选择开始日期"
                  format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="到" field="created_to">
                <a-date-picker
                  v-model="searchForm.created_to"
                  placeholder="选择结束日期"
                  format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="8">
              <a-form-item label="搜索字段" field="search_fields">
                <a-select v-model="searchForm.search_fields" multiple placeholder="选择搜索字段">
                  <a-option value="company_name">公司名称</a-option>
                  <a-option value="contact_name">联系人</a-option>
                  <a-option value="credit_code">信用代码</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="20">
            <a-col :span="8">
              <a-form-item label="排序方式" field="sort">
                <a-select v-model="searchForm.sort" placeholder="选择排序">
                  <a-option value="created_at:desc">创建时间降序</a-option>
                  <a-option value="created_at:asc">创建时间升序</a-option>
                  <a-option value="company_name:asc">公司名称升序</a-option>
                  <a-option value="company_name:desc">公司名称降序</a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row>
            <a-col :span="24">
              <div class="search-actions">
                <a-button @click="handleReset">
                  <icon-refresh />
                  重置
                </a-button>
                <a-button type="primary" @click="handleSaveSearch" :disabled="!saveName">
                  <icon-star />
                  保存搜索条件
                </a-button>
                <a-input
                  v-model="saveName"
                  placeholder="输入搜索条件名称"
                  style="width: 200px"
                  v-if="showSaveInput"
                />
                <a-button @click="showSavedSearches">
                  <icon-folder />
                  已保存的搜索
                </a-button>
                <a-button type="primary" @click="handleSearch">
                  <icon-search />
                  搜索
                </a-button>
              </div>
            </a-col>
          </a-row>
        </a-form>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Message } from '@arco-design/web-vue'
import {
  IconUp,
  IconDown,
  IconSearch,
  IconRefresh,
  IconStar,
  IconFolder
} from '@arco-design/web-vue/es/icon'

interface SearchForm {
  customer_type?: string
  level?: string
  status?: string
  province?: string
  city?: string
  source?: string
  created_from?: string
  created_to?: string
  search_fields?: string[]
  sort?: string
}

const props = defineProps<{
  modelValue: SearchForm
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: SearchForm): void
  (e: 'search', value: SearchForm): void
  (e: 'reset'): void
}>()

const expanded = ref(false)
const saveName = ref('')
const showSaveInput = ref(false)

const searchForm = reactive<SearchForm>({
  customer_type: undefined,
  level: undefined,
  status: undefined,
  province: undefined,
  city: undefined,
  source: undefined,
  created_from: undefined,
  created_to: undefined,
  search_fields: ['company_name', 'contact_name'],
  sort: 'created_at:desc'
})

const toggleExpand = () => {
  expanded.value = !expanded.value
}

const handleSearch = () => {
  const formData = { ...searchForm }
  emit('update:modelValue', formData)
  emit('search', formData)
  Message.success('搜索条件已应用')
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    if (key === 'search_fields') {
      searchForm[key] = ['company_name', 'contact_name']
    } else if (key === 'sort') {
      searchForm[key] = 'created_at:desc'
    } else {
      searchForm[key] = undefined
    }
  })
  saveName.value = ''
  showSaveInput.value = false
  emit('update:modelValue', {})
  emit('reset')
  Message.info('搜索条件已重置')
}

const handleSaveSearch = () => {
  if (!saveName.value) {
    showSaveInput.value = true
    return
  }
  
  // Save to localStorage (in production, save to backend)
  const savedSearches = JSON.parse(localStorage.getItem('savedSearches') || '[]')
  savedSearches.push({
    name: saveName.value,
    criteria: { ...searchForm },
    createdAt: new Date().toISOString()
  })
  localStorage.setItem('savedSearches', JSON.stringify(savedSearches))
  
  Message.success(`搜索条件 "${saveName.value}" 已保存`)
  saveName.value = ''
  showSaveInput.value = false
}

const showSavedSearches = () => {
  const savedSearches = JSON.parse(localStorage.getItem('savedSearches') || '[]')
  if (savedSearches.length === 0) {
    Message.info('暂无保存的搜索条件')
    return
  }
  // In production, show a dialog with saved searches
  Message.info(`已保存 ${savedSearches.length} 个搜索条件`)
}
</script>

<style scoped>
.advanced-search {
  margin-bottom: 20px;
}

.search-card {
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.search-content {
  padding: 10px 0;
}

.search-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
</style>
