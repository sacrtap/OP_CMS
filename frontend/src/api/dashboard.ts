import api from '@/utils/api'

export interface DashboardMetrics {
  total_revenue: number
  total_customers: number
  active_customers: number
  pending_payment: number
  overdue_payment: number
  collection_rate: number
  customer_churn_rate: number
  month_over_month_growth: number
  last_updated: string
}

export interface TrendData {
  date: string
  value: number
}

export interface TrendResponse {
  revenue_trend: TrendData[]
  payment_trend: TrendData[]
  customer_growth: TrendData[]
  dimension: string
  range: number
}

export interface DistributionData {
  name: string
  value: number
}

export interface CustomerStats {
  industry_distribution: DistributionData[]
  region_distribution: DistributionData[]
  level_distribution: DistributionData[]
  total_customers: number
}

export const dashboardAPI = {
  getMetrics() {
    return api.get<DashboardMetrics>('/dashboard/metrics')
  },

  getTrends(dimension: string = 'month', range: number = 6) {
    return api.get<TrendResponse>('/dashboard/trends', { params: { dimension, range } })
  },

  getCustomerStats() {
    return api.get<CustomerStats>('/dashboard/customer-stats')
  }
}
