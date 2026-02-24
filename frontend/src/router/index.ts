import { createRouter, createWebHistory } from 'vue-router'
import CustomerList from '@/views/customer/CustomerList.vue'
import PricingList from '@/views/pricing/PricingList.vue'
import Login from '@/views/auth/Login.vue'

const routes = [
  {
    path: '/customers',
    name: 'CustomerList',
    component: CustomerList,
    meta: { title: '客户管理' }
  },
  {
    path: '/pricing',
    name: 'PricingList',
    component: PricingList,
    meta: { title: '定价配置' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' }
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
