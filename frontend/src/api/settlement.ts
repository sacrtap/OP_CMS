import api from '@/utils/api'

export interface Settlement {
  id: number
  record_id: string
  customer_id: number
  period_start: string
  period_end: string
  usage_quantity: number
  unit: string
  price_model: string
  unit_price: number
  total_amount: number
  currency: string
  status: string
  created_at: string
  updated_at: string
}

export interface SettlementGenerateParams {
  period_start: string
  period_end: string
  customer_ids?: number[]
}

export interface SettlementListParams {
  page?: number
  page_size?: number
  customer_id?: number
  status?: string
  period_start?: string
  period_end?: string
}

export interface SettlementListResponse {
  settlements: Settlement[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SettlementGenerateResponse {
  generation_id: string
  total_customers: number
  generated: number
  failed: number
  status: 'completed' | 'partial'
}

export const settlementAPI = {
  generateSettlement(data: SettlementGenerateParams) {
    return api.post<SettlementGenerateResponse>('/settlements/generate', data)
  },

  listSettlements(params?: SettlementListParams) {
    return api.get<SettlementListResponse>('/settlements', params)
  },

  getSettlement(id: number) {
    return api.get<Settlement>(`/settlements/${id}`)
  }
}
