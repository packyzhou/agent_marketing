<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">分组租户</h2>
    <p class="text-gray-500 text-sm mb-4">管理您推荐成员与AppKey的绑定关系</p>

    <el-card>
      <template #header>
        <span class="font-bold">我的分组成员</span>
      </template>
      <el-table :data="members" border stripe>
        <el-table-column prop="member_id" label="成员ID" width="180" />
        <el-table-column prop="member_name" label="成员名称" />
        <el-table-column prop="app_key" label="绑定AppKey" width="280" />
        <el-table-column prop="app_key_status" label="AppKey状态" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.app_key_status" :type="row.app_key_status === 'ACTIVE' ? 'success' : 'danger'">
              {{ row.app_key_status === 'ACTIVE' ? '启用' : '禁用' }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openBindDialog(row)">绑定AppKey</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="bindDialogVisible" title="绑定AppKey" width="500px">
      <el-form label-width="90px">
        <el-form-item label="成员ID">
          <el-input :model-value="currentMember?.member_id || ''" disabled />
        </el-form-item>
        <el-form-item label="成员名称">
          <el-input :model-value="currentMember?.member_name || ''" disabled />
        </el-form-item>
        <el-form-item label="AppKey">
          <el-select v-model="selectedAppKey" clearable placeholder="选择要绑定的AppKey" style="width: 100%">
            <el-option v-for="item in activeAppKeys" :key="item.app_key" :label="item.tenant_name || item.app_key" :value="item.app_key" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="bindAppKey">确定</el-button>
      </template>
    </el-dialog>

    <el-empty v-if="members.length === 0" description="暂无成员数据" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const members = ref([])
const activeAppKeys = ref([])
const bindDialogVisible = ref(false)
const currentMember = ref(null)
const selectedAppKey = ref(null)

const loadMembers = async () => {
  try {
    members.value = await api.get('/user/group-members')
  } catch (error) {
    ElMessage.error('加载成员列表失败')
  }
}

const loadActiveAppKeys = async () => {
  try {
    activeAppKeys.value = await api.get('/user/active-app-keys')
  } catch (error) {
    ElMessage.error('加载AppKey列表失败')
  }
}

const openBindDialog = async (row) => {
  currentMember.value = row
  selectedAppKey.value = row.app_key || null
  await loadActiveAppKeys()
  bindDialogVisible.value = true
}

const bindAppKey = async () => {
  if (!currentMember.value) return
  try {
    await api.post(`/user/group-members/${currentMember.value.member_id}/bind-app-key`, {
      app_key: selectedAppKey.value || null
    })
    ElMessage.success('绑定成功')
    bindDialogVisible.value = false
    loadMembers()
  } catch (error) {
    ElMessage.error('绑定失败')
  }
}

onMounted(() => {
  loadMembers()
})
</script>
