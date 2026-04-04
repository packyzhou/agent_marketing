<template>
  <div class="min-h-screen bg-gray-100">
    <div class="bg-primary text-white p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">AI智能体平台</h1>
        <div class="flex items-center gap-3">
          <span class="text-sm">{{ displayName }}</span>
          <el-dropdown trigger="click">
            <el-button size="small">
              用户
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="openProfileDialog">用户信息</el-dropdown-item>
                <el-dropdown-item @click="logout">退出</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>
    <div class="container mx-auto mt-4 flex">
      <aside class="w-48 bg-white p-4 rounded shadow mr-4">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/user/dashboard">数据中心</el-menu-item>
          <el-menu-item index="/user/tenants">我的租户</el-menu-item>
          <el-menu-item index="/user/groups">分组管理</el-menu-item>
          <el-menu-item index="/user/group-tenants">分组租户</el-menu-item>
          <el-menu-item index="/user/tokens">Token统计</el-menu-item>
          <el-menu-item index="/user/memory">记忆查看</el-menu-item>
          <el-menu-item index="/user/proxy-debug">对话调试</el-menu-item>
        </el-menu>
      </aside>
      <main class="flex-1 bg-white p-6 rounded shadow">
        <router-view />
      </main>
    </div>

    <el-dialog v-model="profileVisible" title="用户信息" width="520px">
      <el-form :model="profileForm" label-width="90px">
        <el-form-item label="账号">
          <el-input v-model="profileForm.username" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="profileForm.phone" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="profileForm.real_name" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="profileForm.password" type="password" show-password placeholder="不修改可留空" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const router = useRouter()
const profileVisible = ref(false)
const profileForm = ref({
  username: '',
  phone: '',
  real_name: '',
  password: ''
})

const displayName = computed(() => {
  return localStorage.getItem('username') || '当前用户'
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

const openProfileDialog = async () => {
  try {
    const response = await api.get('/user/profile')
    profileForm.value = {
      username: response.username || '',
      phone: response.phone || '',
      real_name: response.real_name || '',
      password: ''
    }
    profileVisible.value = true
  } catch (error) {
    ElMessage.error('加载用户信息失败')
  }
}

const saveProfile = async () => {
  const password = profileForm.value.password?.trim() || ''
  if (password && password.length <= 6) {
    ElMessage.error('密码长度必须大于6位')
    return
  }
  try {
    const payload = {
      username: profileForm.value.username.trim(),
      phone: profileForm.value.phone.trim(),
      real_name: profileForm.value.real_name?.trim() || null,
      password: password || null
    }
    await api.put('/user/profile', payload)
    localStorage.setItem('username', payload.username)
    ElMessage.success('保存成功')
    profileVisible.value = false
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存失败'))
  }
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('roleName')
  localStorage.removeItem('roleType')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.bg-primary {
  background-color: #00796B;
}
</style>
