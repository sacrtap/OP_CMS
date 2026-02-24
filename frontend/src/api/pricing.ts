import api from '@/utils/api'
import type {
  PricingConfig,
  PricingConfigCreate,
  PricingConfigUpdate,
  PricingListResponse
} from './pricing'

export const pricingAPI = {
  listPricingConfigs(params?: {
    page?: number
    page_size?: number
    customer_id?: number
    device_series?: string
    price_model?: string
    is_active?: boolean
    search?: string
  }) {
    return api.get<PricingListResponse>('/pricing', params)
  },

  createPricingConfig(data: PricingConfigCreate) {
    return api.post<PricingConfig>('/pricing', data)
  },

  getPricingConfig(id: number) {
    return api.get<PricingConfig>(`/pricing/${id}`)
  },

  updatePricingConfig(id: number, data: PricingConfigUpdate) {
    return api.put<PricingConfig>(`/pricing/${id}`, data)
  },

  deletePricingConfig(id: number) {
    return api.delete(`/pricing/${id}`)
  }
}

export type {
  PricingConfig,
  PricingConfigCreate,
  PricingConfigUpdate,
  PricingListResponse
}
