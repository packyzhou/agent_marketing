<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">我的租户</h2>
    <el-button type="primary" @click="openCreateDialog" class="mb-4">创建租户</el-button>

    <el-table :data="tenants" border stripe>
      <el-table-column label="AppKey" min-width="240">
        <template #default="{ row }">
          <div class="break-all text-xs leading-5">{{ row.app_key }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="tenant_name" label="租户名称" min-width="150" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status.toUpperCase() === 'ACTIVE' ? 'success' : 'danger'">
            {{ row.status.toUpperCase() === 'ACTIVE' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="360">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="viewDetail(row)">查看</el-button>
          <el-button
            size="small"
            type="success"
            :disabled="!isTenantActive(row)"
            @click="configProvider(row)"
          >
            配置API
          </el-button>
          <el-button
            size="small"
            :type="row.status.toUpperCase() === 'ACTIVE' ? 'warning' : 'success'"
            @click="toggleTenantStatus(row)"
          >
            {{ row.status.toUpperCase() === 'ACTIVE' ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="createDialogVisible" title="创建租户" width="92vw" max-width="720px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="租户名称">
          <el-input v-model="createForm.tenant_name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="绑定用户">
          <el-button size="small" @click="addBoundUser">添加用户</el-button>
          <div v-for="(user, index) in createForm.bound_users" :key="index" class="mt-2 flex flex-wrap gap-2">
            <el-input v-model="user.id" placeholder="用户ID" style="width: 140px" />
            <el-input v-model="user.name" placeholder="姓名" style="width: 160px" />
            <el-input v-model="user.phone" placeholder="手机号" style="width: 180px" />
            <el-button size="small" type="danger" @click="removeBoundUser(index)">删除</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="租户详情" width="92vw" max-width="860px">
      <div v-if="currentTenant">
        <el-descriptions :column="1" border class="tenant-detail-descriptions">
          <el-descriptions-item label="AppKey">
            <div class="break-all leading-6">{{ currentTenant.app_key }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="AppSecret">
            <div class="break-all leading-6">{{ currentTenant.app_secret }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="租户名称">{{ currentTenant.tenant_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ currentTenant.status }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ currentTenant.created_at }}</el-descriptions-item>
        </el-descriptions>
        <p class="mt-4 text-sm text-gray-600">
          请妥善保管您的AppKey和AppSecret，用于调用API时的身份验证。
        </p>
      </div>
    </el-dialog>

    <el-dialog v-model="providerDialogVisible" title="配置供应商API" width="92vw" max-width="960px">
      <div v-if="currentTenant">
        <el-button
          type="primary"
          size="small"
          :disabled="providerKeys.length > 0"
          @click="openAddProviderKey"
          class="mb-4"
        >
          添加API配置
        </el-button>

        <el-table :data="providerKeys" border size="small">
          <el-table-column prop="provider_name" label="供应商" min-width="120" />
          <el-table-column prop="model_name" label="模型" min-width="150" />
          <el-table-column prop="api_key" label="API Key" min-width="220">
            <template #default="{ row }">
              <div class="break-all text-xs leading-5">{{ row.api_key }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="160" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" type="danger" @click="deleteProviderKey(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <el-dialog v-model="addKeyDialogVisible" title="添加API配置" width="92vw" max-width="760px">
      <el-form :model="keyForm" label-width="100px">
        <el-form-item label="供应商">
          <el-select v-model="keyForm.provider_id" placeholder="选择供应商" @change="onProviderChange" style="width: 100%">
            <el-option v-for="p in providers" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="配置指南" v-if="selectedProviderGuide">
          <el-alert type="info" :closable="false">
            <pre class="whitespace-pre-wrap text-sm">{{ selectedProviderGuide }}</pre>
          </el-alert>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="keyForm.api_key" placeholder="请输入API Key" />
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="keyForm.model_name" placeholder="例如: gpt-4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addKeyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddProviderKey">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const tenants = ref([])
const providers = ref([])
const providerKeys = ref([])
const createDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const providerDialogVisible = ref(false)
const addKeyDialogVisible = ref(false)
const currentTenant = ref(null)

const createForm = ref({
  tenant_name: '',
  bound_users: []
})

const keyForm = ref({
  provider_id: null,
  api_key: '',
  model_name: ''
})

const selectedProviderGuide = computed(() => {
  if (!keyForm.value.provider_id) return null
  const provider = providers.value.find(p => p.id === keyForm.value.provider_id)
  return provider?.config_guide || null
})

const isTenantActive = (tenant) => {
  return (tenant?.status || '').toUpperCase() === 'ACTIVE'
}

const loadTenants = async () => {
  try {
    tenants.value = await api.get('/user/tenants')
  } catch (error) {
    ElMessage.error('加载租户列表失败')
  }
}

const loadProviders = async () => {
  try {
    providers.value = await api.get('/user/providers')
  } catch (error) {
    ElMessage.error('加载供应商列表失败')
  }
}

const openCreateDialog = () => {
  createForm.value = { tenant_name: '', bound_users: [] }
  createDialogVisible.value = true
}

const addBoundUser = () => {
  createForm.value.bound_users.push({ id: '', name: '', phone: '' })
}

const removeBoundUser = (index) => {
  createForm.value.bound_users.splice(index, 1)
}

const handleCreate = async () => {
  try {
    await api.post('/user/tenants', {
      tenant_name: createForm.value.tenant_name,
      group_binding_json: JSON.stringify(createForm.value.bound_users)
    })
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    loadTenants()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const viewDetail = (row) => {
  currentTenant.value = row
  detailDialogVisible.value = true
}

const configProvider = async (row) => {
  if (!isTenantActive(row)) {
    ElMessage.warning('租户已禁用，无法配置API')
    return
  }
  currentTenant.value = row
  try {
    providerKeys.value = await api.get(`/user/tenants/${row.app_key}/provider-keys`)
    providerDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载API配置失败')
  }
}

const openAddProviderKey = () => {
  keyForm.value = { provider_id: null, api_key: '', model_name: '' }
  addKeyDialogVisible.value = true
}

const onProviderChange = () => {
  // 当选择供应商时，显示配置指南
}

const handleAddProviderKey = async () => {
  try {
    await api.post(`/user/tenants/${currentTenant.value.app_key}/provider-keys`, keyForm.value)
    ElMessage.success('添加成功')
    addKeyDialogVisible.value = false
    configProvider(currentTenant.value)
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const deleteProviderKey = async (keyId) => {
  try {
    await api.delete(`/user/tenants/${currentTenant.value.app_key}/provider-keys/${keyId}`)
    ElMessage.success('删除成功')
    configProvider(currentTenant.value)
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const toggleTenantStatus = async (row) => {
  try {
    const nextStatus = row.status.toUpperCase() === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
    await api.put(`/user/tenants/${row.app_key}`, { status: nextStatus })
    ElMessage.success(nextStatus === 'ACTIVE' ? '启用成功' : '禁用成功')
    loadTenants()
  } catch (error) {
    ElMessage.error('状态更新失败')
  }
}

onMounted(() => {
  loadTenants()
  loadProviders()
})
</script>

<style scoped>
:deep(.tenant-detail-descriptions .el-descriptions__label) {
  width: 120px;
}
</style>
