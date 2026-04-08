<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>用户管理</h2>
        <p>查看与维护平台用户、角色及关联租户信息</p>
      </div>
      <el-select v-model="roleFilter" placeholder="筛选角色" clearable @change="loadUsers" style="width: 160px">
        <el-option label="全部" value="" />
        <el-option label="管理员" value="ADMIN" />
        <el-option label="普通用户" value="USER" />
      </el-select>
    </div>

    <el-table :data="users" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="email" label="邮箱" width="200" />
      <el-table-column prop="phone" label="手机号" width="120" />
      <el-table-column prop="real_name" label="真实姓名" width="100" />
      <el-table-column prop="role" label="角色" width="80">
        <template #default="{ row }">
          <el-tag :type="row.role_type === 'ADMIN' ? 'danger' : 'primary'">
            {{ row.role_name || row.role }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="group_id" label="组ID" width="80" />
      <el-table-column prop="referral_id" label="推荐人ID" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="mt-4"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      @current-change="loadUsers"
      layout="total, prev, pager, next"
    />

    <el-dialog v-model="detailVisible" title="用户详情" width="600px">
      <div v-if="selectedUser">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedUser.id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ selectedUser.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ selectedUser.email }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ selectedUser.phone || '-' }}</el-descriptions-item>
          <el-descriptions-item label="真实姓名">{{ selectedUser.real_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="角色">{{ selectedUser.role }}</el-descriptions-item>
          <el-descriptions-item label="组ID">{{ selectedUser.group_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="推荐人ID">{{ selectedUser.referral_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="租户数量">{{ selectedUser.tenant_count }}</el-descriptions-item>
          <el-descriptions-item label="推荐人数">{{ selectedUser.referral_count }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">{{ selectedUser.created_at }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const roleFilter = ref('')
const detailVisible = ref(false)
const selectedUser = ref(null)

const loadUsers = async () => {
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const params = { skip, limit: pageSize.value }
    if (roleFilter.value) {
      params.role = roleFilter.value
    }

    const response = await api.get('/admin/users', { params })
    users.value = response.items || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  }
}

const viewDetail = async (user) => {
  try {
    selectedUser.value = await api.get(`/admin/users/${user.id}`)
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载用户详情失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>
