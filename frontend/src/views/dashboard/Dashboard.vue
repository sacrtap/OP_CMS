<template>
  <div class="dashboard">
    <h1 class="page-title">管理驾驶舱</h1>
    <p class="last-update">数据更新时间：{{ lastUpdateTime }}</p>

    <!-- 核心指标卡片 -->
    <a-row :gutter="20" class="metrics-row">
      <a-col :span="6" v-for="metric in metrics" :key="metric.title">
        <a-card hoverable class="metric-card">
          <div class="metric-header">
            <span class="metric-title">{{ metric.title }}</span>
            <a-tooltip :content="metric.description" position="top">
              <icon-question-circle style="font-size: 16px; color: #999" />
            </a-tooltip>
          </div>
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-footer">
            <span :class="metric.trendClass">{{ metric.trend }}</span>
            <span class="metric-label">{{ metric.label }}</span>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 趋势图表 -->
    <a-row :gutter="20" class="charts-row">
      <a-col :span="12">
        <a-card hoverable>
          <template #title>
            <div class="card-header">
              <span>收入趋势</span>
              <a-select v-model="revenueDimension" size="small" @change="loadTrendData">
                <a-option value="day">日</a-option>
                <a-option value="week">周</a-option>
                <a-option value="month">月</a-option>
              </a-select>
            </div>
          </template>
          <div ref="revenueChart" class="chart" style="height: 300px;"></div>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card hoverable>
          <template #title>
            <div class="card-header">
              <span>回款趋势</span>
              <a-select v-model="paymentDimension" size="small" @change="loadTrendData">
                <a-option value="day">日</a-option>
                <a-option value="week">周</a-option>
                <a-option value="month">月</a-option>
              </a-select>
            </div>
          </template>
          <div ref="paymentChart" class="chart" style="height: 300px;"></div>
        </a-card>
      </a-col>
    </a-row>

    <!-- 客户分布 -->
    <a-row :gutter="20" class="charts-row">
      <a-col :span="8">
        <a-card hoverable>
          <template #title>
            <span>客户行业分布</span>
          </template>
          <div ref="industryChart" class="chart" style="height: 300px;"></div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card hoverable>
          <template #title>
            <span>客户地域分布</span>
          </template>
          <div ref="regionChart" class="chart" style="height: 300px;"></div>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card hoverable>
          <template #title>
            <span>客户等级分布</span>
          </template>
          <div ref="levelChart" class="chart" style="height: 300px;"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as echarts from 'echarts'
import { dashboardAPI } from '@/api/dashboard'
import { IconQuestionCircle } from '@arco-design/web-vue/es/icon'

const lastUpdateTime = ref('')
const revenueDimension = ref('month')
const paymentDimension = ref('month')

const metrics = ref([
  { title: '总收入', value: '¥0', trend: '+0%', trendClass: 'trend-up', label: '环比增长', description: '所有已付款账单的总金额' },
  { title: '客户总数', value: '0', trend: '+0', trendClass: 'trend-up', label: '活跃客户', description: '系统注册的客户总数' },
  { title: '待回款', value: '¥0', trend: '0%', trendClass: 'trend-neutral', label: '待回款比例', description: '已审核但未付款的金额' },
  { title: '逾期金额', value: '¥0', trend: '0%', trendClass: 'trend-down', label: '逾期率', description: '逾期 30 天以上的金额' }
])

const loadMetrics = async () => {
  try {
    const data = await dashboardAPI.getMetrics()
    metrics.value[0].value = `¥${data.total_revenue.toLocaleString()}`
    metrics.value[1].value = data.total_customers.toString()
    metrics.value[2].value = `¥${data.pending_payment.toLocaleString()}`
    metrics.value[3].value = `¥${data.overdue_payment.toLocaleString()}`
    lastUpdateTime.value = new Date(data.last_updated).toLocaleString('zh-CN')
  } catch (error) {
    Message.error('加载指标数据失败')
  }
}

// 加载趋势数据
const loadTrendData = async () => {
  try {
    const data = await dashboardAPI.getTrends(revenueDimension.value)
    
    // 渲染收入趋势图
    const revenueChart = echarts.init(document.querySelector('.chart') as HTMLElement)
    revenueChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: data.revenue_trend.map(item => item.date) },
      yAxis: { type: 'value' },
      series: [{ data: data.revenue_trend.map(item => item.value), type: 'line', smooth: true }]
    })
  } catch (error) {
    Message.error('加载趋势数据失败')
  }
}

// 加载客户统计
const loadCustomerStats = async () => {
  try {
    const data = await dashboardAPI.getCustomerStats()
    
    // 渲染行业分布图
    const industryChart = echarts.init(document.querySelectorAll('.chart')[2] as HTMLElement)
    industryChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: data.industry_distribution
      }]
    })
  } catch (error) {
    Message.error('加载客户统计失败')
  }
}

onMounted(() => {
  loadMetrics()
  loadTrendData()
  loadCustomerStats()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-title {
  margin-bottom: 10px;
}

.last-update {
  color: #999;
  margin-bottom: 20px;
}

.metrics-row {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.metric-title {
  font-size: 14px;
  color: #666;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 10px 0;
}

.metric-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.trend-up {
  color: #67C23A;
}

.trend-down {
  color: #F56C6C;
}

.trend-neutral {
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart {
  width: 100%;
}
</style>
