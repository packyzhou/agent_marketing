<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">分组租户</h2>
    <p class="text-gray-500 text-sm mb-4">以下是您所在分组内所有用户的租户列表</p>

    <el-card class="mb-4">
      <template #header>
        <span class="font-bold">我的分组</span>
      </template>
      <el-table :data="groups" border stripe>
        <el-table-column prop="id" label="分组ID" width="140" />
        <el-table-column prop="group_name" label="分组名称" />
        <el-table-column prop="owner_id" label="所有者ID" width="180" />
        <el-table-column prop="member_count" label="成员数" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="220" />
      </el-table>
      <div class="mt-4 flex justify-end">
        <el-pagination
          v-model:current-page="groupPage"
          v-model:page-size="groupPageSize"
          :total="groupTotal"
          layout="total, prev, pager, next"
          @current-change="loadGroups"
        />
      </div>
    </el-card>

    <el-table :data="tenants" border stripe>
      <el-table-column prop="app_key" label="AppKey" width="200" />
      <el-table-column prop="tenant_name" label="租户名称" width="150" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column prop="group_binding_json" label="绑定信息" show-overflow-tooltip />
    </el-table>

    <el-empty v-if="tenants.length === 0" description="暂无分组租户，或您尚未加入任何分组" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const tenants = ref([])
const groups = ref([])
const groupPage = ref(1)
const groupPageSize = ref(10)
const groupTotal = ref(0)

const loadGroups = async () => {
  try {
    const skip = (groupPage.value - 1) * groupPageSize.value
    const res = await api.get('/user/groups', {
      params: {
        skip,
        limit: groupPageSize.value
      }
    })
    groups.value = res.items || []
    groupTotal.value = res.total || 0
  } catch (error) {
    ElMessage.error('加载分组列表失败')
  }
}

const loadGroupTenants = async () => {
  try {
    tenants.value = await api.get('/user/tenants/group')
  } catch (error) {
    ElMessage.error('加载分组租户失败')
  }
}

onMounted(() => {
  loadGroups()
  loadGroupTenants()
})
</script>
