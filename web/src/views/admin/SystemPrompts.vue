<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-slate-900">提示词管理</h2>
        <p class="text-sm text-slate-400 mt-0.5">管理系统级 AI 提示词，通过 prompt_type 在配置中引用</p>
      </div>
      <button @click="openCreate"
        class="flex items-center space-x-2 px-4 py-2.5 bg-slate-950 text-white text-sm font-bold rounded-xl hover:bg-cyan-500 transition-all duration-300">
        <PlusIcon class="w-4 h-4" />
        <span>新建提示词</span>
      </button>
    </div>

    <!-- List -->
    <div v-if="items.length === 0" class="flex flex-col items-center justify-center py-24 text-slate-400">
      <FileTextIcon class="w-10 h-10 mb-3 opacity-30" />
      <span class="text-sm">暂无提示词，点击右上角新建</span>
    </div>

    <div v-else class="space-y-3">
      <div v-for="item in items" :key="item.id"
        class="border border-slate-100 rounded-2xl p-5 hover:border-slate-200 transition-colors">
        <div class="flex items-start justify-between gap-4">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-2">
              <span class="text-xs font-bold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-lg font-mono">
                {{ item.prompt_type }}
              </span>
              <span class="text-xs text-slate-400">{{ formatDate(item.updated_at) }}</span>
            </div>
            <div class="text-sm text-slate-500 line-clamp-2 whitespace-pre-wrap leading-relaxed">{{ item.content }}</div>
          </div>
          <div class="flex items-center space-x-2 flex-shrink-0">
            <button @click="openEdit(item)"
              class="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-50 rounded-lg transition-colors">
              <PencilIcon class="w-4 h-4" />
            </button>
            <button @click="confirmDelete(item)"
              class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
              <Trash2Icon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="editingItem ? '编辑提示词' : '新建提示词'" width="900px"
      :close-on-click-modal="false" destroy-on-close>
      <el-form :model="form" label-width="90px" class="pr-2">
        <el-form-item label="类型标识">
          <el-input v-model="form.prompt_type" :disabled="!!editingItem" placeholder="如 marketing_assistant（唯一，不可修改）"
            class="font-mono" />
          <div class="text-xs text-slate-400 mt-1">用于在 agent_config.json 的 system_llm.prompt_type 中引用</div>
        </el-form-item>
        <el-form-item label="提示词内容">
          <!-- Split-pane Markdown Editor -->
          <div class="w-full border border-slate-200 rounded-xl overflow-hidden">
            <div class="flex border-b border-slate-100 bg-slate-50 text-xs font-medium text-slate-500">
              <span class="px-4 py-2 border-r border-slate-100">编辑 (Markdown)</span>
              <span class="px-4 py-2">预览</span>
            </div>
            <div class="flex" style="height: 400px">
              <textarea v-model="form.content"
                class="flex-1 resize-none p-4 text-sm font-mono leading-relaxed focus:outline-none border-r border-slate-100"
                placeholder="在此输入 Markdown 格式的系统提示词…" />
              <div class="flex-1 p-4 overflow-y-auto prose prose-sm max-w-none text-slate-700"
                v-html="renderedContent" />
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end space-x-3">
          <button @click="dialogVisible = false"
            class="px-5 py-2.5 text-sm font-bold text-slate-500 border border-slate-200 rounded-xl hover:border-slate-300 transition-colors">
            取消
          </button>
          <button @click="save" :disabled="saving"
            class="px-5 py-2.5 text-sm font-bold text-white bg-slate-950 rounded-xl hover:bg-cyan-500 transition-all duration-300 disabled:opacity-50">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { PlusIcon, PencilIcon, Trash2Icon, FileTextIcon } from 'lucide-vue-next'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import api from '../../api/request'

const items = ref([])
const dialogVisible = ref(false)
const editingItem = ref(null)
const saving = ref(false)
const form = ref({ prompt_type: '', content: '' })

const renderedContent = computed(() => {
  if (!form.value.content) return '<span class="text-slate-300 text-sm">预览将在此处显示…</span>'
  return DOMPurify.sanitize(marked.parse(form.value.content))
})

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' })
}

const load = async () => {
  try {
    items.value = await api.get('/admin/system-prompts')
  } catch {
    ElMessage.error('加载提示词列表失败')
  }
}

const openCreate = () => {
  editingItem.value = null
  form.value = { prompt_type: '', content: '' }
  dialogVisible.value = true
}

const openEdit = (item) => {
  editingItem.value = item
  form.value = { prompt_type: item.prompt_type, content: item.content }
  dialogVisible.value = true
}

const save = async () => {
  if (!form.value.prompt_type.trim()) return ElMessage.warning('请输入类型标识')
  if (!form.value.content.trim()) return ElMessage.warning('请输入提示词内容')
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/admin/system-prompts/${editingItem.value.id}`, { content: form.value.content })
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/system-prompts', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    load()
  } catch (error) {
    const detail = error?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : (editingItem.value ? '更新失败' : '创建失败'))
  } finally {
    saving.value = false
  }
}

const confirmDelete = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确认删除提示词 "${item.prompt_type}" 吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确认删除', cancelButtonText: '取消', type: 'warning' }
    )
    await api.delete(`/admin/system-prompts/${item.id}`)
    ElMessage.success('删除成功')
    load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.prose :deep(h1), .prose :deep(h2), .prose :deep(h3) { font-weight: 700; margin: 0.75em 0 0.4em; }
.prose :deep(p) { margin: 0.4em 0; }
.prose :deep(ul), .prose :deep(ol) { padding-left: 1.4em; margin: 0.4em 0; }
.prose :deep(code) { background: #f1f5f9; padding: 0.1em 0.4em; border-radius: 4px; font-size: 0.85em; }
.prose :deep(pre) { background: #f1f5f9; padding: 0.75em 1em; border-radius: 8px; overflow-x: auto; }
.prose :deep(blockquote) { border-left: 3px solid #cbd5e1; padding-left: 1em; color: #64748b; }
</style>
