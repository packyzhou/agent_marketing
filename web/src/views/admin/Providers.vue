<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">供应商管理</h2>
    <el-button type="primary" @click="dialogVisible = true" class="mb-4">添加供应商</el-button>

    <el-table :data="providers" border>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="base_url" label="Base URL" />
      <el-table-column prop="status" label="状态" />
    </el-table>

    <el-dialog v-model="dialogVisible" title="添加供应商">
      <el-form :model="form">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const providers = ref([])
const dialogVisible = ref(false)
const form = ref({ name: '', base_url: '' })

const loadProviders = async () => {
  try {
    providers.value = await api.get('/admin/providers')
  } catch (error) {
    ElMessage.error('加载失败')
  }
}

const handleCreate = async () => {
  try {
    await api.post('/admin/providers', form.value)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadProviders()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

onMounted(loadProviders)
</script>
