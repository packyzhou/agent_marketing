<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">供应商管理</h2>
    <el-button type="primary" @click="openDialog()" class="mb-4">添加供应商</el-button>

    <el-table :data="providers" border stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" width="150" />
      <el-table-column prop="code" label="代码" width="120" />
      <el-table-column prop="base_url" label="Base URL" width="300" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status.toUpperCase() === 'ACTIVE' ? 'success' : 'danger'">
            {{ row.status.toUpperCase() === 'ACTIVE' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openDialog(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteProvider(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="mt-4 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadProviders"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑供应商' : '添加供应商'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="例如: OpenAI" />
        </el-form-item>
        <el-form-item label="代码">
          <el-input v-model="form.code" placeholder="例如: openai" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="例如: https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="配置指南">
          <el-input v-model="form.config_guide" type="textarea" :rows="6"
            placeholder="配置说明，例如如何获取API Key等" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const providers = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({ name: '', code: '', base_url: '', config_guide: '' })

const loadProviders = async () => {
  try {
    const skip = (page.value - 1) * pageSize.value
    const res = await api.get('/admin/providers', {
      params: { skip, limit: pageSize.value }
    })
    providers.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const openDialog = (provider = null) => {
  if (provider) {
    isEdit.value = true
    form.value = { ...provider }
  } else {
    isEdit.value = false
    form.value = { name: '', code: '', base_url: '', config_guide: '' }
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await api.put(`/admin/providers/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/providers', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProviders()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  }
}

const deleteProvider = async (providerId) => {
  try {
    await api.delete(`/admin/providers/${providerId}`)
    ElMessage.success('删除成功')
    loadProviders()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadProviders)
</script>
