<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>角色管理</h2>
        <p>定义系统内可分配的角色及其权限类型</p>
      </div>
      <el-button type="primary" @click="openCreateDialog">新增角色</el-button>
    </div>

    <div class="flex gap-2 mb-4">
      <el-input
        v-model="keyword"
        placeholder="搜索角色编码 / 名称"
        clearable
        style="width: 280px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      />
      <el-button type="primary" @click="handleSearch">查询</el-button>
    </div>

    <el-table :data="roles" stripe v-loading="loading">
      <el-table-column prop="code" label="角色编码" width="140" />
      <el-table-column prop="name" label="角色名称" width="140" />
      <el-table-column prop="role_type" label="权限类型" width="120">
        <template #default="{ row }">
          <el-tag :type="row.role_type === 'ADMIN' ? 'danger' : 'primary'">
            {{ row.role_type === 'ADMIN' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="说明" min-width="220" />
      <el-table-column prop="user_count" label="用户数" width="90" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="280">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openEditDialog(row)">修改</el-button>
          <el-button type="success" size="small" @click="openAssignDialog(row)">配置用户角色</el-button>
          <el-button type="danger" size="small" :disabled="row.is_system" @click="deleteRole(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="mt-4"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="loadRoles"
    />

    <el-dialog v-model="editVisible" :title="isCreateMode ? '新增角色' : '修改角色'" width="520px">
      <el-form :model="editForm" label-width="90px">
        <el-form-item label="角色编码">
          <el-input v-model="editForm.code" :disabled="!isCreateMode" />
        </el-form-item>
        <el-form-item label="角色名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="权限类型">
          <el-select v-model="editForm.role_type" style="width: 100%">
            <el-option label="管理员" value="ADMIN" />
            <el-option label="普通用户" value="USER" />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRole">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignVisible" title="配置用户角色" width="680px">
      <div class="mb-3 text-xs font-bold text-slate-400 uppercase tracking-widest">当前角色：{{ selectedRole?.name || '-' }}</div>
      <el-table :data="users" stripe v-loading="userLoading">
        <el-table-column prop="username" label="账号" width="150" />
        <el-table-column prop="phone" label="手机号" width="150" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="role_name" label="当前角色" width="140" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="assignRole(row)">设为当前角色</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/request'

const keyword = ref('')
const loading = ref(false)
const roles = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const editVisible = ref(false)
const isCreateMode = ref(true)
const editForm = ref({
  code: '',
  name: '',
  role_type: 'USER',
  description: ''
})

const assignVisible = ref(false)
const selectedRole = ref(null)
const users = ref([])
const userLoading = ref(false)

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) {
    return detail
  }
  return fallback
}

const loadRoles = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params = { skip, limit: pageSize.value }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    const response = await api.get('/admin/roles', { params })
    roles.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载角色列表失败'))
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  currentPage.value = 1
  await loadRoles()
}

const openCreateDialog = () => {
  isCreateMode.value = true
  editForm.value = {
    code: '',
    name: '',
    role_type: 'USER',
    description: ''
  }
  editVisible.value = true
}

const openEditDialog = (row) => {
  isCreateMode.value = false
  editForm.value = {
    code: row.code,
    name: row.name,
    role_type: row.role_type,
    description: row.description || ''
  }
  editVisible.value = true
}

const submitRole = async () => {
  try {
    const payload = {
      code: editForm.value.code.trim().toUpperCase(),
      name: editForm.value.name.trim(),
      role_type: editForm.value.role_type,
      description: editForm.value.description?.trim() || null
    }
    if (isCreateMode.value) {
      await api.post('/admin/roles', payload)
    } else {
      await api.put(`/admin/roles/${payload.code}`, {
        name: payload.name,
        role_type: payload.role_type,
        description: payload.description
      })
    }
    ElMessage.success('保存成功')
    editVisible.value = false
    loadRoles()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存角色失败'))
  }
}

const deleteRole = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除角色“${row.name}”吗？`, '删除确认', { type: 'warning' })
    await api.delete(`/admin/roles/${row.code}`)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error(getErrorMessage(error, '删除角色失败'))
  }
}

const openAssignDialog = async (row) => {
  selectedRole.value = row
  userLoading.value = true
  try {
    const response = await api.get('/admin/users', { params: { skip: 0, limit: 500 } })
    users.value = response.items || []
    assignVisible.value = true
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载用户列表失败'))
  } finally {
    userLoading.value = false
  }
}

const assignRole = async (user) => {
  if (!selectedRole.value) {
    return
  }
  try {
    await api.put(`/admin/users/${user.id}/role`, {
      role_code: selectedRole.value.code
    })
    ElMessage.success('角色分配成功')
    openAssignDialog(selectedRole.value)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '角色分配失败'))
  }
}

onMounted(() => {
  loadRoles()
})
</script>
