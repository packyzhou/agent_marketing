<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">记忆查看</h2>

    <el-table :data="memories" border stripe>
      <el-table-column prop="app_key" label="AppKey" width="200" />
      <el-table-column prop="rounds_count" label="对话轮数" width="100" />
      <el-table-column prop="last_processed_at" label="最后处理时间" width="180" />
      <el-table-column label="文件状态" width="150">
        <template #default="{ row }">
          <el-tag v-if="row.has_kv_file" type="success" size="small">KV</el-tag>
          <el-tag v-if="row.has_digest_file" type="primary" size="small" class="ml-1">Digest</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewMemory(row)">
            查看详情
          </el-button>
          <el-button type="danger" size="small" @click="clearMemory(row)">
            清理KV和Digest
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" title="记忆详情" width="900px">
      <div v-if="selectedMemory">
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
        <div class="mt-4 text-gray-500 text-sm">
          <p>对话轮数: {{ selectedMemory.rounds_count }}</p>
          <p>最后处理: {{ selectedMemory.last_processed_at || '未处理' }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const memories = ref([])
const detailVisible = ref(false)
const selectedMemory = ref(null)
const activeTab = ref('kv')

const loadMemories = async () => {
  try {
    const response = await axios.get('/api/admin/memory', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    memories.value = response.data
  } catch (error) {
    ElMessage.error('加载记忆列表失败')
  }
}

const viewMemory = async (memory) => {
  try {
    const response = await axios.get(`/api/admin/memory/${memory.app_key}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    selectedMemory.value = response.data
    detailVisible.value = true
    activeTab.value = 'kv'
  } catch (error) {
    ElMessage.error('加载记忆详情失败')
  }
}

const clearMemory = async (memory) => {
  try {
    await ElMessageBox.confirm(
      `确认清理 AppKey=${memory.app_key} 的 KV 和 Digest 文件内容吗？`,
      '清理确认',
      {
        confirmButtonText: '确认清理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await axios.post(`/api/admin/memory/${memory.app_key}/clear`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    ElMessage.success('清理成功')
    if (selectedMemory.value && selectedMemory.value.app_key === memory.app_key) {
      selectedMemory.value.kv_content = ''
      selectedMemory.value.digest_content = ''
      selectedMemory.value.rounds_count = 0
    }
    loadMemories()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error('清理失败')
  }
}

onMounted(() => {
  loadMemories()
})
</script>
