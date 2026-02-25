<template>
  <div>
    <a-modal
      v-model:visible="visible"
      title="价格信息"
      width="600px"
      @ok="handleSubmit"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="价格名称" field="name">
          <a-input v-model="form.name" placeholder="请输入价格名称" />
        </a-form-item>
        <a-form-item label="价格" field="price">
          <a-input-number v-model="form.price" placeholder="请输入价格" :min="0" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { Message } from '@arco-design/web-vue';

interface PricingData {
  name: string;
  price: number;
}

const visible = ref(false);
const form = reactive<PricingData>({
  name: '',
  price: 0,
});

const emit = defineEmits(['submit']);

watch(() => visible.value, (val) => {
  if (!val) {
    form.name = '';
    form.price = 0;
  }
});

const handleSubmit = () => {
  if (!form.name) {
    Message.error('请输入价格名称');
    return;
  }
  emit('submit', { ...form });
  visible.value = false;
};

defineExpose({
  open: () => {
    visible.value = true;
  }
});
</script>
