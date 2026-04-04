<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">记忆查看</h2>

    <el-table :data="memories" border stripe v-loading="loading">
      <el-table-column prop="app_key" label="AppKey" width="220" />
      <el-table-column prop="tenant_name" label="租户名称" width="160" />
      <el-table-column prop="rounds_count" label="处理轮数" width="100" />
      <el-table-column prop="last_processed_at" label="最后处理时间" width="180" />
      <el-table-column label="文件状态" width="150">
        <template #default="{ row }">
          <el-tag v-if="row.has_kv_file" type="success" size="small">KV</el-tag>
          <el-tag v-if="row.has_digest_file" type="primary" size="small" class="ml-1">Digest</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewMemory(row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && memories.length === 0" description="暂无记忆数据" />

    <el-dialog v-model="detailVisible" title="记忆详情" width="900px">
      <div v-if="selectedMemory">
        <div class="mb-4 text-sm text-gray-500">
          <p>租户名称：{{ selectedMemory.tenant_name || '-' }}</p>
          <p>对话轮数：{{ selectedMemory.rounds_count }}</p>
          <p>最后处理：{{ selectedMemory.last_processed_at || '未处理' }}</p>
        </div>
        <el-tabs v-model="activeTab">
          <el-tab-pane label="KV事实记忆" name="kv">
            <el-card v-if="selectedMemory.kv_content">
              <pre class="whitespace-pre-wrap text-sm">{{ selectedMemory.kv_content }}</pre>
            </el-card>
            <el-empty v-else description="暂无KV记忆" />
          </el-tab-pane>
          <el-tab-pane label="行为摘要记忆" name="digest">
            <el-card v-if="selectedMemory.digest_content">
              <pre class="whitespace-pre-wrap text-sm">{{ selectedMemory.digest_content }}</pre>
            </el-card>
            <el-empty v-else description="暂无摘要记忆" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const memories = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const selectedMemory = ref(null)
const activeTab = ref('kv')

const loadMemories = async () => {
  loading.value = true
  try {
    memories.value = await api.get('/user/memory')
  } catch (error) {
    ElMessage.error('加载记忆列表失败')
  } finally {
    loading.value = false
  }
}

const viewMemory = async (memory) => {
  try {
    selectedMemory.value = await api.get(`/user/memory/${memory.app_key}`)
    activeTab.value = 'kv'
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('加载记忆详情失败')
  }
}

onMounted(() => {
  loadMemories()
})
</script>
