<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold">租户管理</h2>
      <el-select v-model="statusFilter" placeholder="筛选状态" clearable @change="loadTenants" style="width: 150px">
        <el-option label="全部" value="" />
        <el-option label="启用" value="active" />
        <el-option label="禁用" value="inactive" />
      </el-select>
    </div>

    <el-table :data="tenants" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="app_key" label="AppKey" width="200" />
      <el-table-column prop="tenant_name" label="租户名称" width="150" />
      <el-table-column prop="username" label="所属用户" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status.toUpperCase() === 'ACTIVE' ? 'success' : 'danger'">
            {{ row.status.toUpperCase() === 'ACTIVE' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="租户详情" width="700px">
      <div v-if="selectedTenant">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedTenant.id }}</el-descriptions-item>
          <el-descriptions-item label="AppKey">{{ selectedTenant.app_key }}</el-descriptions-item>
          <el-descriptions-item label="AppSecret">{{ selectedTenant.app_secret }}</el-descriptions-item>
          <el-descriptions-item label="租户名称">{{ selectedTenant.tenant_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ selectedTenant.status }}</el-descriptions-item>
          <el-descriptions-item label="所属用户">{{ selectedTenant.username }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ selectedTenant.created_at }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt-4" v-if="selectedTenant.bound_users && selectedTenant.bound_users.length > 0">
          <h3 class="font-bold mb-2">绑定用户</h3>
          <el-table :data="selectedTenant.bound_users" border size="small">
            <el-table-column prop="id" label="用户ID" width="100" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="phone" label="手机号" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const tenants = ref([])
const statusFilter = ref('')
const detailVisible = ref(false)
const selectedTenant = ref(null)

const loadTenants = async () => {
  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    tenants.value = await api.get('/admin/tenants', { params })
  } catch (error) {
    ElMessage.error('加载租户列表失败')
  }
}

const viewDetail = async (tenant) => {
  try {
    selectedTenant.value = await api.get(`/admin/tenants/${tenant.id}`)
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载租户详情失败')
  }
}

onMounted(loadTenants)
</script>
