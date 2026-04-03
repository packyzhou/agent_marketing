<template>
  <div class="min-h-screen bg-gray-100">
    <div class="bg-primary text-white p-4">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-xl font-bold">AI智能体平台</h1>
        <el-button @click="logout" type="danger" size="small">退出</el-button>
      </div>
    </div>
    <div class="container mx-auto mt-4 flex">
      <aside class="w-48 bg-white p-4 rounded shadow mr-4">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/user/dashboard">数据中心</el-menu-item>
          <el-menu-item index="/user/tenants">我的租户</el-menu-item>
          <el-menu-item index="/user/group-tenants">分组租户</el-menu-item>
          <el-menu-item index="/user/tokens">Token统计</el-menu-item>
        </el-menu>
      </aside>
      <main class="flex-1 bg-white p-6 rounded shadow">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.bg-primary {
  background-color: #00796B;
}
</style>
