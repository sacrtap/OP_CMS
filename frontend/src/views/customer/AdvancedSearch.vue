<template>
  <div class="advanced-search">
    <el-card class="search-card">
      <template #header>
        <div class="card-header">
          <span>高级搜索</span>
          <el-button link type="primary" @click="toggleExpand">
            <el-icon><ArrowUp v-if="expanded" /><ArrowDown v-else /></el-icon>
            {{ expanded ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>

      <el-collapse-transition>
        <div v-show="expanded" class="search-content">
          <el-form :model="searchForm" label-width="100px" size="default">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="客户类型">
                  <el-select v-model="searchForm.customer_type" placeholder="全部" clearable>
                    <el-option label="企业" value="enterprise" />
                    <el-option label="个人" value="individual" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="客户等级">
                  <el-select v-model="searchForm.level" placeholder="全部" clearable>
                    <el-option label="VIP" value="vip" />
                    <el-option label="标准" value="standard" />
                    <el-option label="经济" value="economy" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="客户状态">
                  <el-select v-model="searchForm.status" placeholder="全部" clearable>
                    <el-option label="活跃" value="active" />
                    <el-option label="非活跃" value="inactive" />
                    <el-option label="潜在客户" value="potential" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="省份">
                  <el-input v-model="searchForm.province" placeholder="请输入省份" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="城市">
                  <el-input v-model="searchForm.city" placeholder="请输入城市" clearable />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="来源渠道">
                  <el-select v-model="searchForm.source" placeholder="全部" clearable>
                    <el-option label="直接开发" value="direct" />
                    <el-option label="推荐" value="referral" />
                    <el-option label="市场推广" value="marketing" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="创建时间从">
                  <el-date-picker
                    v-model="searchForm.created_from"
                    type="date"
                    placeholder="选择开始日期"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="到">
                  <el-date-picker
                    v-model="searchForm.created_to"
                    type="date"
                    placeholder="选择结束日期"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="搜索字段">
                  <el-select v-model="searchForm.search_fields" multiple placeholder="选择搜索字段">
                    <el-option label="公司名称" value="company_name" />
                    <el-option label="联系人" value="contact_name" />
                    <el-option label="信用代码" value="credit_code" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="排序方式">
                  <el-select v-model="searchForm.sort" placeholder="选择排序">
                    <el-option label="创建时间降序" value="created_at:desc" />
                    <el-option label="创建时间升序" value="created_at:asc" />
                    <el-option label="公司名称升序" value="company_name:asc" />
                    <el-option label="公司名称降序" value="company_name:desc" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="24">
                <div class="search-actions">
                  <el-button @click="handleReset">
                    <el-icon><RefreshLeft /></el-icon>
                    重置
                  </el-button>
                  <el-button type="primary" @click="handleSaveSearch" :disabled="!saveName">
                    <el-icon><Star /></el-icon>
                    保存搜索条件
                  </el-button>
                  <el-input
                    v-model="saveName"
                    placeholder="输入搜索条件名称"
                    style="width: 200px"
                    v-if="showSaveInput"
                  />
                  <el-button @click="showSavedSearches">
                    <el-icon><FolderOpened /></el-icon>
                    已保存的搜索
                  </el-button>
                  <el-button type="primary" @click="handleSearch">
                    <el-icon><Search /></el-icon>
                    搜索
                  </el-button>
                </div>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </el-collapse-transition>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ArrowUp, ArrowDown, Search, RefreshLeft, Star, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

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
  ElMessage.success('搜索条件已应用')
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
  ElMessage.info('搜索条件已重置')
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
  
  ElMessage.success(`搜索条件 "${saveName.value}" 已保存`)
  saveName.value = ''
  showSaveInput.value = false
}

const showSavedSearches = () => {
  const savedSearches = JSON.parse(localStorage.getItem('savedSearches') || '[]')
  if (savedSearches.length === 0) {
    ElMessage.info('暂无保存的搜索条件')
    return
  }
  // In production, show a dialog with saved searches
  ElMessage.info(`已保存 ${savedSearches.length} 个搜索条件`)
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
