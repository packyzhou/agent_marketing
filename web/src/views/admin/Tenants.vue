<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">租户管理</h2>
    <el-table :data="tenants" border>
      <el-table-column prop="app_key" label="App Key" />
      <el-table-column prop="user_id" label="用户ID" />
      <el-table-column prop="created_at" label="创建时间" />
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../api/request'

const tenants = ref([])

const loadTenants = async () => {
  try {
    tenants.value = await api.get('/admin/tenants')
  } catch (error) {
    console.error(error)
  }
}

onMounted(loadTenants)
</script>
