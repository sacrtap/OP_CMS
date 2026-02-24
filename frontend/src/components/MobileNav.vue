<template>
  <!-- Mobile Bottom Navigation -->
  <nav v-if="isMobile" class="bottom-nav">
    <router-link to="/customers" class="nav-item" active-class="active">
      <el-icon><User /></el-icon>
      <span>客户</span>
    </router-link>
    <router-link to="/settlements" class="nav-item" active-class="active">
      <el-icon><Document /></el-icon>
      <span>结算</span>
    </router-link>
    <router-link to="/reports" class="nav-item" active-class="active">
      <el-icon><DataAnalysis /></el-icon>
      <span>报表</span>
    </router-link>
    <router-link to="/dashboard" class="nav-item" active-class="active">
      <el-icon><Monitor /></el-icon>
      <span>驾驶舱</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { User, Document, DataAnalysis, Monitor } from '@element-plus/icons-vue'

const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #666;
  font-size: 12px;
}

.nav-item.active {
  color: #409EFF;
}

.nav-item .el-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

/* Hide bottom nav on desktop */
@media (min-width: 768px) {
  .bottom-nav {
    display: none;
  }
}
</style>
