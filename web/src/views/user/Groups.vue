<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <div>
        <h2 class="text-2xl font-bold">分组管理</h2>
        <p class="text-gray-500 text-sm mt-1">仅查看当前所属分组成员，并展示成员创建的租户、AppKey与状态</p>
      </div>
    </div>

    <el-table :data="groups" border stripe v-loading="groupLoading">
      <el-table-column prop="group_name" label="分组名称" min-width="220" />
      <el-table-column prop="owner_id" label="组长ID" width="180" />
      <el-table-column prop="member_count" label="成员数" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openMembersDialog(row)">查看成员</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="mt-4"
      v-model:current-page="groupPage"
      :page-size="groupPageSize"
      :total="groupTotal"
      layout="total, prev, pager, next"
      @current-change="loadGroups"
    />

    <el-dialog
      v-model="membersDialogVisible"
      :title="selectedGroup ? `${selectedGroup.group_name} - 成员管理` : '成员管理'"
      width="1280px"
    >
      <div v-if="selectedGroup" class="mb-4 text-sm text-gray-500">
        当前分组共 {{ membersTotal }} 名成员
      </div>

      <el-table :data="members" border stripe v-loading="memberLoading">
        <el-table-column prop="member_id" label="成员ID" width="180" />
        <el-table-column prop="username" label="用户账号" width="160" />
        <el-table-column prop="member_name" label="姓名" width="140" />
        <el-table-column prop="phone" label="手机号" width="160" />
        <el-table-column label="绑定AppKey / 状态" min-width="240">
          <template #default="{ row }">
            <div v-if="row.app_key" class="space-y-2">
              <div class="break-all text-xs leading-5 text-gray-600">{{ row.app_key }}</div>
              <el-tag v-if="row.app_key_status" size="small" :type="row.app_key_status === 'ACTIVE' ? 'success' : 'danger'">
                {{ row.app_key_status === 'ACTIVE' ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="成员租户 / AppKey列表" min-width="360">
          <template #default="{ row }">
            <div v-if="row.owned_tenants?.length" class="space-y-2">
              <div
                v-for="tenant in row.owned_tenants"
                :key="tenant.app_key"
                class="rounded border border-gray-200 px-3 py-2"
              >
                <div class="font-medium text-gray-800">{{ tenant.tenant_name || '未命名租户' }}</div>
                <div class="mt-1 break-all text-xs text-gray-500">{{ tenant.app_key }}</div>
                <el-tag class="mt-2" size="small" :type="tenant.status === 'ACTIVE' ? 'success' : 'danger'">
                  {{ tenant.status === 'ACTIVE' ? '启用' : '禁用' }}
                </el-tag>
              </div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              :disabled="!selectedGroup?.can_manage"
              @click="handleDeleteMember(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!memberLoading && members.length === 0" description="暂无成员数据" />

      <el-pagination
        class="mt-4"
        v-model:current-page="memberPage"
        :page-size="memberPageSize"
        :total="membersTotal"
        layout="total, prev, pager, next"
        @current-change="loadMembers"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/request'

const groups = ref([])
const groupLoading = ref(false)
const groupPage = ref(1)
const groupPageSize = ref(10)
const groupTotal = ref(0)

const membersDialogVisible = ref(false)
const selectedGroup = ref(null)
const members = ref([])
const memberLoading = ref(false)
const memberPage = ref(1)
const memberPageSize = ref(10)
const membersTotal = ref(0)

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) {
    return detail
  }
  return fallback
}

const loadGroups = async () => {
  groupLoading.value = true
  try {
    const skip = (groupPage.value - 1) * groupPageSize.value
    const response = await api.get('/user/groups', {
      params: {
        skip,
        limit: groupPageSize.value
      }
    })
    groups.value = response.items || []
    groupTotal.value = response.total || 0
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载分组列表失败'))
  } finally {
    groupLoading.value = false
  }
}

const loadMembers = async () => {
  if (!selectedGroup.value) {
    return
  }

  memberLoading.value = true
  try {
    const skip = (memberPage.value - 1) * memberPageSize.value
    const response = await api.get(`/user/groups/${selectedGroup.value.id}/members`, {
      params: {
        skip,
        limit: memberPageSize.value
      }
    })
    members.value = response.items || []
    membersTotal.value = response.total || 0
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '加载成员列表失败'))
  } finally {
    memberLoading.value = false
  }
}

const openMembersDialog = async (group) => {
  selectedGroup.value = group
  memberPage.value = 1
  membersDialogVisible.value = true
  await loadMembers()
}

const handleDeleteMember = async (member) => {
  if (!selectedGroup.value?.can_manage) {
    ElMessage.warning('当前分组不支持删除成员')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认将成员“${member.member_name}”移出当前分组吗？移出后该成员会回到自己的默认分组，当前推荐关系与绑定关系会被清理。`,
      '删除确认',
      {
        type: 'warning'
      }
    )

    await api.delete(`/user/groups/${selectedGroup.value.id}/members/${member.member_id}`)
    ElMessage.success('删除成功')

    if (members.value.length === 1 && memberPage.value > 1) {
      memberPage.value -= 1
    }

    await Promise.all([loadMembers(), loadGroups()])
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error(getErrorMessage(error, '删除成员失败'))
  }
}

onMounted(() => {
  loadGroups()
})
</script>
