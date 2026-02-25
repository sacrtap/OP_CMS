<template>
  <div class="login-container">
    <a-card class="login-card" title="OP CMS 登录">
      <a-form :model="form" layout="vertical">
        <a-form-item label="用户名" field="username">
          <a-input
            v-model="form.username"
            placeholder="请输入用户名"
          />
        </a-form-item>
        <a-form-item label="密码" field="password">
          <a-input-password
            v-model="form.password"
            placeholder="请输入密码"
          />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" long @click="handleLogin">
            登录
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const form = reactive({
  username: '',
  password: '',
});

const handleLogin = async () => {
  // Mock login - always succeeds for testing
  console.log('Login attempt:', form.username);
  router.push('/customers');
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-card {
  width: 400px;
  max-width: 90%;
}
</style>
