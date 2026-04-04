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
              <el-input v-model="registerForm.username" placeholder="用户账号（必填）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.phone" placeholder="手机号（必填）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.real_name" placeholder="真实姓名（选填）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.password" type="password" placeholder="密码（仅数字且大于6位）" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="registerForm.referrer_phone" placeholder="推荐人手机号（选填）" />
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
  phone: '',
  real_name: '',
  password: '',
  referrer_phone: ''
})

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (typeof first === 'string') {
      return first
    }
    if (first?.msg) {
      return first.msg
    }
  }
  return fallback
}

const handleLogin = async () => {
  try {
    const res = await api.post('/auth/login', loginForm.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('role', (res.role || 'USER').toUpperCase())
    ElMessage.success('登录成功')
    if ((res.role || '').toUpperCase() === 'ADMIN') {
      router.push('/admin/providers')
      return
    }
    router.push('/user/dashboard')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '登录失败'))
  }
}

const handleRegister = async () => {
  const username = registerForm.value.username.trim()
  const phone = registerForm.value.phone.trim()
  const password = registerForm.value.password.trim()
  const realName = registerForm.value.real_name.trim()
  const referrerPhone = registerForm.value.referrer_phone.trim()

  if (!username || !phone || !password) {
    ElMessage.error('用户账号、手机号、密码为必填项')
    return
  }

  if (!/^\d+$/.test(password) || password.length <= 6) {
    ElMessage.error('密码必须为大于6位的纯数字')
    return
  }

  try {
    await api.post('/auth/register', {
      username,
      phone,
      password,
      real_name: realName || null,
      referrer_phone: referrerPhone || null
    })
    ElMessage.success('注册成功，请登录')
    registerForm.value = {
      username: '',
      phone: '',
      real_name: '',
      password: '',
      referrer_phone: ''
    }
    activeTab.value = 'login'
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '注册失败'))
  }
}
</script>
