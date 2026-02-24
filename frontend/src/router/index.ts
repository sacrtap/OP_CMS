import { createRouter, createWebHistory } from 'vue-router'
import CustomerList from '@/views/customer/CustomerList.vue'

const routes = [
  {
    path: '/customers',
    name: 'CustomerList',
    component: CustomerList,
    meta: {
      title: '客户管理'
    }
  },
  {
    path: '/',
    redirect: '/customers'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
