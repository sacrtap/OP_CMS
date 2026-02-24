<template>
  <div class="responsive-table-container">
    <!-- Desktop: Table view -->
    <el-table 
      v-if="!isMobile"
      :data="data"
      style="width: 100%"
      v-bind="$attrs"
    >
      <slot></slot>
    </el-table>
    
    <!-- Mobile: Card view -->
    <div v-else class="mobile-card-list">
      <CustomerCard 
        v-for="item in data"
        :key="item.id"
        :customer="item"
        @view="$emit('view', item)"
        @edit="$emit('edit', item)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import CustomerCard from './CustomerCard.vue'

defineProps<{
  data: any[]
}>()

defineEmits<{
  (e: 'view', item: any): void
  (e: 'edit', item: any): void
}>()

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
.responsive-table-container {
  width: 100%;
}

.mobile-card-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Hide table on mobile */
@media (max-width: 768px) {
  :deep(.el-table) {
    display: none;
  }
}

/* Hide cards on desktop */
@media (min-width: 768px) {
  .mobile-card-list {
    display: none;
  }
}
</style>
