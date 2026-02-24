// OP_CMS Frontend API Client
// Customer API integration

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export interface Customer {
  id: number
  customer_id: string
  company_name: string
  contact_name: string
  contact_phone: string
  credit_code?: string
  customer_type: string
  province?: string
  city?: string
  address?: string
  email?: string
  website?: string
  industry?: string
  erp_system?: string
  erp_customer_code?: string
  status: string
  level: string
  source: string
  remarks?: string
  created_at: string
  updated_at: string
}

export interface CustomerCreate {
  company_name: string
  contact_name: string
  contact_phone: string
  credit_code?: string
  customer_type?: string
  province?: string
  city?: string
  address?: string
  email?: string
  website?: string
  industry?: string
  erp_system?: string
  erp_customer_code?: string
  status?: string
  level?: string
  source?: string
  remarks?: string
}

export interface CustomerUpdate extends Partial<CustomerCreate> {}

export interface CustomerListResponse {
  customers: Customer[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}

class CustomerAPI {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  async listCustomers(
    page: number = 1,
    page_size: number = 20,
    search?: string,
    status?: string,
    province?: string,
    level?: string
  ): Promise<CustomerListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: page_size.toString()
    })

    if (search) params.append('search', search)
    if (status) params.append('status', status)
    if (province) params.append('province', province)
    if (level) params.append('level', level)

    const response = await axios.get<ApiResponse<CustomerListResponse>>(
      `${this.baseUrl}/customers?${params.toString()}`
    )
    return response.data.data
  }

  async getCustomer(customer_id: string): Promise<Customer> {
    const response = await axios.get<ApiResponse<Customer>>(
      `${this.baseUrl}/customers/${customer_id}`
    )
    return response.data.data
  }

  async createCustomer(data: CustomerCreate): Promise<Customer> {
    const response = await axios.post<ApiResponse<Customer>>(
      `${this.baseUrl}/customers`,
      data
    )
    return response.data.data
  }

  async updateCustomer(customer_id: string, data: CustomerUpdate): Promise<Customer> {
    const response = await axios.put<ApiResponse<Customer>>(
      `${this.baseUrl}/customers/${customer_id}`,
      data
    )
    return response.data.data
  }

  async deleteCustomer(customer_id: string): Promise<void> {
    await axios.delete<ApiResponse<void>>(
      `${this.baseUrl}/customers/${customer_id}`
    )
  }

  async checkDuplicate(
    company_name?: string,
    credit_code?: string
  ): Promise<{ is_duplicate: boolean; duplicate_field?: string; duplicate_value?: string }> {
    const params = new URLSearchParams()
    if (company_name) params.append('company_name', company_name)
    if (credit_code) params.append('credit_code', credit_code)

    const response = await axios.get<ApiResponse<{
      is_duplicate: boolean
      duplicate_field?: string
      duplicate_value?: string
    }>>(`${this.baseUrl}/customers/check-duplicate?${params.toString()}`)
    return response.data.data
  }
}

export const customerAPI = new CustomerAPI()
