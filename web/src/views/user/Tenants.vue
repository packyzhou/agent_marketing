<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">租户配置</h2>
    <el-button type="primary" @click="handleCreate" class="mb-4">创建租户</el-button>

    <el-table :data="tenants" border>
      <el-table-column prop="app_key" label="App Key" />
      <el-table-column prop="app_secret" label="App Secret" show-overflow-tooltip />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="租户详情" width="600px">
      <div v-if="currentTenant">
        <p><strong>App Key:</strong> {{ currentTenant.app_key }}</p>
        <p><strong>App Secret:</strong> {{ currentTenant.app_secret }}</p>
        <p class="mt-4 text-sm text-gray-600">
          请妥善保管您的App Key和App Secret，用于调用API时的身份验证。
        </p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const tenants = ref([])
const dialogVisible = ref(false)
const currentTenant = ref(null)

const loadTenants = async () => {
  try {
    tenants.value = await api.get('/user/tenants')
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handleCreate = async () => {
  try {
    await api.post('/user/tenants', { group_binding_json: '' })
    ElMessage.success('创建成功')
    loadTenants()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const viewDetail = (row) => {
  currentTenant.value = row
  dialogVisible.value = true
}

onMounted(loadTenants)
</script>
