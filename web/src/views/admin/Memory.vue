<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>记忆查看</h2>
        <p>查看与维护各租户的事实记忆、行为摘要与领域记忆文件</p>
      </div>
    </div>

    <el-table :data="memories" stripe>
      <el-table-column label="AppKey" min-width="220">
        <template #default="{ row }">
          <div class="break-all text-xs leading-5">{{ row.app_key }}</div>
        </template>
      </el-table-column>
      <el-table-column v-if="isAdmin" prop="username" label="所属用户" width="120">
        <template #default="{ row }">
          <span v-if="row.username">{{ row.username }}</span>
          <span v-else class="text-slate-300 text-xs">-</span>
        </template>
      </el-table-column>
      <el-table-column label="文件状态" width="210">
        <template #default="{ row }">
          <el-tag v-if="row.has_kv_file" type="success" size="small">KV</el-tag>
          <el-tag v-if="row.has_digest_file" type="primary" size="small" class="ml-1">Digest</el-tag>
          <el-tag v-if="row.has_domain_file" type="warning" size="small" class="ml-1">Domain</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewMemory(row)">
            查看详情
          </el-button>
          <el-button v-if="isAdmin" type="danger" size="small" @click="clearMemory(row)">
            清理记忆文件
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="对话总时长" width="140">
        <template #default="{ row }">
          <span class="font-mono text-xs">{{ formatDuration(row.total_duration_seconds) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="记忆库容量" width="140">
        <template #default="{ row }">
          <span class="font-mono text-xs">{{ formatMemorySize(row.memory_size) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="last_processed_at" label="最后处理时间" width="180" />
    </el-table>

    <el-dialog v-model="detailVisible" title="记忆详情" width="900px">
      <div v-if="selectedMemory">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="KV 事实记忆" name="kv">
            <el-input
              v-model="memoryForm.kv_content"
              type="textarea"
              :rows="18"
              resize="vertical"
              placeholder="暂无 KV 记忆"
            />
          </el-tab-pane>
          <el-tab-pane label="行为摘要记忆" name="digest">
            <el-input
              v-model="memoryForm.digest_content"
              type="textarea"
              :rows="18"
              resize="vertical"
              placeholder="暂无摘要记忆"
            />
          </el-tab-pane>
          <el-tab-pane label="领域记忆" name="domain">
            <el-input
              v-model="memoryForm.domain_content"
              type="textarea"
              :rows="18"
              resize="vertical"
              placeholder="暂无领域记忆"
            />
          </el-tab-pane>
        </el-tabs>
        <div class="mt-4 flex items-center gap-6 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          <span>对话总时长：<span class="text-slate-700 font-mono">{{ formatDuration(selectedMemory.total_duration_seconds) }}</span></span>
          <span>记忆库容量：<span class="text-slate-700 font-mono">{{ formatMemorySize(selectedMemory.memory_size) }}</span></span>
          <span>最后处理：<span class="text-slate-700 font-mono">{{ selectedMemory.last_processed_at || '未处理' }}</span></span>
        </div>
        <div class="mt-4 flex justify-end gap-2">
          <el-button :loading="detailLoading" @click="refreshMemoryDetail">
            刷新
          </el-button>
          <el-button type="primary" :loading="savingMemory" @click="saveMemoryDetail">
            保存修改
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/request'

const isAdmin = computed(() => (localStorage.getItem('roleType') || '').toUpperCase() === 'ADMIN')

const memories = ref([])
const detailVisible = ref(false)
const selectedMemory = ref(null)
const activeTab = ref('kv')
const detailLoading = ref(false)
const savingMemory = ref(false)
const memoryForm = ref({
  kv_content: '',
  digest_content: '',
  domain_content: ''
})

const syncMemoryForm = (memory) => {
  memoryForm.value = {
    kv_content: memory?.kv_content || '',
    digest_content: memory?.digest_content || '',
    domain_content: memory?.domain_content || ''
  }
}

const formatDuration = (seconds) => {
  const total = Number(seconds) || 0
  if (total <= 0) return '0 秒'
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const parts = []
  if (h > 0) parts.push(`${h} 小时`)
  if (m > 0) parts.push(`${m} 分`)
  if (s > 0 || parts.length === 0) parts.push(`${s} 秒`)
  return parts.join(' ')
}

const formatMemorySize = (size) => {
  const n = Number(size) || 0
  if (n < 1024) return `${n} 字`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(2)} K 字`
  return `${(n / (1024 * 1024)).toFixed(2)} M 字`
}

const loadMemories = async () => {
  try {
    memories.value = await api.get('/admin/memory')
  } catch (error) {
    ElMessage.error('加载记忆列表失败')
  }
}

const viewMemory = async (memory) => {
  try {
    detailLoading.value = true
    selectedMemory.value = await api.get(`/admin/memory/${memory.app_key}`)
    syncMemoryForm(selectedMemory.value)
    detailVisible.value = true
    activeTab.value = 'kv'
  } catch (error) {
    ElMessage.error('加载记忆详情失败')
  } finally {
    detailLoading.value = false
  }
}

const refreshMemoryDetail = async () => {
  if (!selectedMemory.value?.app_key) return
  try {
    detailLoading.value = true
    selectedMemory.value = await api.get(`/admin/memory/${selectedMemory.value.app_key}`)
    syncMemoryForm(selectedMemory.value)
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新记忆详情失败')
  } finally {
    detailLoading.value = false
  }
}

const saveMemoryDetail = async () => {
  if (!selectedMemory.value?.app_key) return
  try {
    savingMemory.value = true
    await api.put(`/admin/memory/${selectedMemory.value.app_key}`, {
      kv_content: memoryForm.value.kv_content,
      digest_content: memoryForm.value.digest_content,
      domain_content: memoryForm.value.domain_content
    })
    selectedMemory.value = await api.get(`/admin/memory/${selectedMemory.value.app_key}`)
    syncMemoryForm(selectedMemory.value)
    await loadMemories()
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存记忆详情失败')
  } finally {
    savingMemory.value = false
  }
}

const clearMemory = async (memory) => {
  try {
    await ElMessageBox.confirm(
      `确认清理 AppKey=${memory.app_key} 的事实记忆、行为摘要与领域记忆文件内容吗？`,
      '清理确认',
      {
        confirmButtonText: '确认清理',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await api.post(`/admin/memory/${memory.app_key}/clear`, {})
    ElMessage.success('清理成功')
    if (selectedMemory.value && selectedMemory.value.app_key === memory.app_key) {
      selectedMemory.value.kv_content = ''
      selectedMemory.value.digest_content = ''
      selectedMemory.value.domain_content = ''
      selectedMemory.value.total_duration_seconds = 0
      selectedMemory.value.memory_size = 0
      syncMemoryForm(selectedMemory.value)
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
