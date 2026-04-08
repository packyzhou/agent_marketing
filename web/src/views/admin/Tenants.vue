<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>租户管理</h2>
        <p>管理平台租户、AppKey 及供应商 API 配置</p>
      </div>
      <div class="flex gap-2">
        <el-select v-model="statusFilter" placeholder="筛选状态" clearable @change="loadTenants" style="width: 160px">
          <el-option label="全部" value="" />
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="inactive" />
        </el-select>
        <el-button type="primary" @click="openCreateDialog">创建租户</el-button>
      </div>
    </div>

    <el-table :data="tenants" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="AppKey" min-width="240">
        <template #default="{ row }">
          <div class="break-all text-xs leading-5">{{ row.app_key }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="tenant_name" label="租户名称" min-width="150" />
      <el-table-column label="联系信息" min-width="180">
        <template #default="{ row }">
          <div v-if="row.contact_name || row.contact_phone" class="text-xs leading-5">
            <div v-if="row.contact_name" class="text-slate-700">{{ row.contact_name }}</div>
            <div v-if="row.contact_phone" class="text-slate-500 font-mono">{{ row.contact_phone }}</div>
          </div>
          <span v-else class="text-slate-300 text-xs">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="所属用户" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status.toUpperCase() === 'ACTIVE' ? 'success' : 'danger'">
            {{ row.status.toUpperCase() === 'ACTIVE' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="320">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            详情
          </el-button>
          <el-button
            type="info"
            size="small"
            :disabled="!isTenantActive(row)"
            @click="configProvider(row)"
          >
            配置API
          </el-button>
          <el-button type="success" size="small" @click="openEditDialog(row)">修改</el-button>
          <el-button
            :type="row.status.toUpperCase() === 'ACTIVE' ? 'warning' : 'success'"
            size="small"
            @click="toggleTenantStatus(row)"
          >
            {{ row.status.toUpperCase() === 'ACTIVE' ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" :title="isCreateMode ? '创建租户' : '修改租户'" width="92vw" max-width="760px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="租户名称">
          <el-input v-model="editForm.tenant_name" placeholder="请输入租户名称" />
        </el-form-item>
        <el-form-item label="联系人姓名">
          <el-input v-model="editForm.contact_name" placeholder="选填" />
        </el-form-item>
        <el-form-item label="联系人电话">
          <el-input v-model="editForm.contact_phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option label="启用" value="ACTIVE" />
            <el-option label="禁用" value="INACTIVE" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTenant">{{ isCreateMode ? '创建' : '保存' }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="租户详情" width="92vw" max-width="960px">
      <div v-if="selectedTenant">
        <el-descriptions :column="1" border class="tenant-detail-descriptions">
          <el-descriptions-item label="ID">{{ selectedTenant.id }}</el-descriptions-item>
          <el-descriptions-item label="AppKey">
            <div class="break-all leading-6">{{ selectedTenant.app_key }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="AppSecret">
            <div class="break-all leading-6">{{ selectedTenant.app_secret }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="租户名称">{{ selectedTenant.tenant_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系人姓名">{{ selectedTenant.contact_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系人电话">{{ selectedTenant.contact_phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ selectedTenant.status }}</el-descriptions-item>
          <el-descriptions-item label="所属用户">{{ selectedTenant.username }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ selectedTenant.created_at }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt-6" v-if="selectedTenant.bound_users && selectedTenant.bound_users.length > 0">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">绑定用户</h3>
          <el-table :data="selectedTenant.bound_users" size="small">
            <el-table-column prop="id" label="用户ID" min-width="140" />
            <el-table-column prop="name" label="姓名" min-width="120" />
            <el-table-column prop="phone" label="手机号" />
          </el-table>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="providerDialogVisible" title="配置供应商API" width="92vw" max-width="960px">
      <div v-if="selectedTenantForProvider">
        <el-button
          type="primary"
          size="small"
          :disabled="providerKeys.length > 0"
          @click="openAddProviderKey"
          class="mb-4"
        >
          添加API配置
        </el-button>
        <el-table :data="providerKeys" size="small">
          <el-table-column prop="provider_name" label="供应商" min-width="120" />
          <el-table-column prop="model_name" label="模型" min-width="150" />
          <el-table-column prop="api_key" label="API Key" min-width="240">
            <template #default="{ row }">
              <div class="break-all text-xs leading-5">{{ row.api_key }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" min-width="180" />
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
          <el-select v-model="keyForm.provider_id" placeholder="选择供应商" style="width: 100%">
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
          <el-input v-model="keyForm.model_name" placeholder="例如: qwen-plus" />
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
const statusFilter = ref('')
const detailVisible = ref(false)
const selectedTenant = ref(null)
const editVisible = ref(false)
const isCreateMode = ref(true)
const currentAppKey = ref('')
const providers = ref([])
const providerKeys = ref([])
const providerDialogVisible = ref(false)
const addKeyDialogVisible = ref(false)
const selectedTenantForProvider = ref(null)
const editForm = ref({
  tenant_name: '',
  contact_name: '',
  contact_phone: '',
  status: 'ACTIVE'
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
    const params = {
      skip: 0,
      limit: 200
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const response = await api.get('/admin/tenants', { params })
    tenants.value = response.items || []
  } catch (error) {
    ElMessage.error('加载租户列表失败')
  }
}

const viewDetail = async (tenant) => {
  try {
    selectedTenant.value = await api.get(`/admin/tenants/${tenant.app_key}`)
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载租户详情失败')
  }
}

const openCreateDialog = async () => {
  isCreateMode.value = true
  currentAppKey.value = ''
  editForm.value = {
    tenant_name: '',
    contact_name: '',
    contact_phone: '',
    status: 'ACTIVE'
  }
  editVisible.value = true
}

const openEditDialog = async (row) => {
  isCreateMode.value = false
  currentAppKey.value = row.app_key
  editForm.value = {
    tenant_name: row.tenant_name || '',
    contact_name: row.contact_name || '',
    contact_phone: row.contact_phone || '',
    status: (row.status || 'ACTIVE').toUpperCase()
  }
  editVisible.value = true
}

const submitTenant = async () => {
  try {
    if (isCreateMode.value) {
      await api.post('/admin/tenants', editForm.value)
      ElMessage.success('创建成功')
    } else {
      await api.put(`/admin/tenants/${currentAppKey.value}`, editForm.value)
      ElMessage.success('修改成功')
    }
    editVisible.value = false
    loadTenants()
  } catch (error) {
    ElMessage.error(isCreateMode.value ? '创建失败' : '修改失败')
  }
}

const toggleTenantStatus = async (row) => {
  const currentStatus = (row.status || '').toUpperCase()
  const nextStatus = currentStatus === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
  try {
    await api.put(`/admin/tenants/${row.app_key}`, { status: nextStatus })
    ElMessage.success(nextStatus === 'ACTIVE' ? '启用成功' : '禁用成功')
    loadTenants()
  } catch (error) {
    ElMessage.error(nextStatus === 'ACTIVE' ? '启用失败' : '禁用失败')
  }
}

const loadProviders = async () => {
  try {
    const res = await api.get('/admin/providers', { params: { skip: 0, limit: 200, status: 'ACTIVE' } })
    providers.value = res.items || []
  } catch (error) {
    ElMessage.error('加载供应商列表失败')
  }
}

const configProvider = async (row) => {
  if (!isTenantActive(row)) {
    ElMessage.warning('租户已禁用，无法配置API')
    return
  }
  selectedTenantForProvider.value = row
  try {
    providerKeys.value = await api.get(`/admin/tenants/${row.app_key}/provider-keys`)
    providerDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载API配置失败')
  }
}

const openAddProviderKey = () => {
  keyForm.value = { provider_id: null, api_key: '', model_name: '' }
  addKeyDialogVisible.value = true
}

const handleAddProviderKey = async () => {
  try {
    await api.post(`/admin/tenants/${selectedTenantForProvider.value.app_key}/provider-keys`, keyForm.value)
    ElMessage.success('添加成功')
    addKeyDialogVisible.value = false
    configProvider(selectedTenantForProvider.value)
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const deleteProviderKey = async (keyId) => {
  try {
    await api.delete(`/admin/tenants/${selectedTenantForProvider.value.app_key}/provider-keys/${keyId}`)
    ElMessage.success('删除成功')
    configProvider(selectedTenantForProvider.value)
  } catch (error) {
    ElMessage.error('删除失败')
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
