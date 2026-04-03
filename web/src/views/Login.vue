<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-96">
      <h2 class="text-2xl font-bold mb-6 text-center" style="color: #00796B">AI智能体平台</h2>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" @submit.prevent="handleLogin">
            <el-form-item>
              <el-input v-model="loginForm.username" placeholder="用户名" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleLogin" class="w-full" style="background-color: #00796B">
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" @submit.prevent="handleRegister">
            <el-form-item>
              <el-input v-model="registerForm.username" placeholder="用户名" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.email" placeholder="邮箱" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.phone" placeholder="手机号（选填）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.real_name" placeholder="真实姓名（选填）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.password" type="password" placeholder="密码" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.referral_id" placeholder="推荐人ID（选填）" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleRegister" class="w-full" style="background-color: #00796B">
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api/request'

const router = useRouter()
const activeTab = ref('login')
const loginForm = ref({
  username: '',
  password: ''
})
const registerForm = ref({
  username: '',
  email: '',
  phone: '',
  real_name: '',
  password: '',
  referral_id: ''
})

const handleLogin = async () => {
  try {
    const res = await api.post('/auth/login', loginForm.value)
    localStorage.setItem('token', res.access_token)
    ElMessage.success('登录成功')
    router.push('/user/dashboard')
  } catch (error) {
    ElMessage.error('登录失败')
  }
}

const handleRegister = async () => {
  try {
    await api.post('/auth/register', registerForm.value)
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
  } catch (error) {
    ElMessage.error('注册失败')
  }
}
</script>
