<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>{{ $t('agent.plugins.title') }}</h2>
        <p>{{ $t('agent.plugins.subtitle') }}</p>
      </div>
      <el-button type="primary" :disabled="!appKey" @click="openCreate">{{ $t('agent.plugins.new') }}</el-button>
    </div>

    <el-card class="mb-4">
      <el-form label-width="100px" :inline="true">
        <el-form-item :label="$t('agent.common.appKey')">
          <el-select v-model="appKey" filterable style="width: 360px" @change="loadPlugins">
            <el-option v-for="t in tenantOptions" :key="t.app_key" :label="t.app_key" :value="t.app_key" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="appKey">
      <el-table :data="plugins" size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="plugin_name" :label="$t('agent.plugins.name')" />
        <el-table-column prop="plugin_type" :label="$t('agent.plugins.type')" width="100" />
        <el-table-column prop="builtin_key" :label="$t('agent.plugins.builtinKey')" width="130" />
        <el-table-column :label="$t('agent.plugins.enabled')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? 'ON' : 'OFF' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" :label="$t('agent.plugins.sort')" width="80" />
        <el-table-column :label="$t('agent.common.actions')" width="160">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">{{ $t('agent.common.edit') }}</el-button>
            <el-button size="small" type="danger" @click="removePlugin(row)">{{ $t('agent.common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!plugins.length" :description="$t('agent.plugins.empty')" />
    </el-card>

    <!-- Editor dialog -->
    <el-dialog v-model="editorVisible" :title="editing.id ? $t('agent.plugins.editTitle') : $t('agent.plugins.newTitle')" width="900px" top="5vh">
      <el-form :model="editing" label-width="120px">
        <el-form-item :label="$t('agent.plugins.name')">
          <el-input v-model="editing.plugin_name" style="width: 360px" />
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.type')">
          <el-radio-group v-model="editing.plugin_type">
            <el-radio-button label="custom">{{ $t('agent.plugins.typeCustom') }}</el-radio-button>
            <el-radio-button label="builtin">{{ $t('agent.plugins.typeBuiltin') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="editing.plugin_type === 'builtin'" :label="$t('agent.plugins.builtinKey')">
          <el-select v-model="editing.builtin_key" style="width: 360px">
            <el-option v-for="b in builtinOptions" :key="b.builtin_key" :label="b.builtin_key" :value="b.builtin_key" />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.description')">
          <el-input v-model="editing.description" />
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.enabled')">
          <el-switch v-model="editing.enabled" />
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.sort')">
          <el-input-number v-model="editing.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item v-if="editing.plugin_type === 'custom'" :label="$t('agent.plugins.script')">
          <el-input v-model="editing.script_content" type="textarea" :rows="14" class="code-area"
            :placeholder="$t('agent.plugins.scriptPh')" />
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.configJson')">
          <el-input v-model="editing.config_json_text" type="textarea" :rows="3"
            placeholder='{"env": {"AGENT_FILE_BASE_DIR": "/data"}, "args": []}' />
        </el-form-item>
      </el-form>

      <!-- Debug -->
      <el-divider>{{ $t('agent.plugins.debug') }}</el-divider>
      <p class="debug-hint">{{ $t('agent.plugins.debugHint') }}</p>
      <el-form label-width="120px">
        <el-form-item :label="$t('agent.plugins.toolName')">
          <el-select
            v-model="debug.tool_name"
            filterable
            allow-create
            default-first-option
            :placeholder="$t('agent.plugins.toolNamePh')"
            style="width: 260px"
            @change="onToolChange"
          >
            <el-option v-for="t in debug.tools" :key="t.name" :label="t.name" :value="t.name" />
          </el-select>
          <el-button class="ml-2" :loading="loadingTools" @click="loadTools">{{ $t('agent.plugins.loadTools') }}</el-button>
        </el-form-item>
        <el-form-item v-if="currentToolDesc" :label="$t('agent.plugins.description')">
          <span class="tool-desc">{{ currentToolDesc }}</span>
        </el-form-item>
        <el-form-item :label="$t('agent.plugins.toolArgs')">
          <el-input v-model="debug.tool_args_text" type="textarea" :rows="3" placeholder='{"dir_path": "/path/to/dir"}' />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="debugging" :disabled="!debug.tool_name" @click="runDebug">
            {{ $t('agent.plugins.runDebug') }}
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="debugResult" class="debug-result">
        <div class="debug-result-label">{{ $t('agent.plugins.callResult') }}</div>
        <pre>{{ debugResult }}</pre>
      </div>
      <div v-if="debugRaw" class="debug-raw">
        <details>
          <summary>{{ $t('agent.plugins.rawResult') }}</summary>
          <pre>{{ debugRaw }}</pre>
        </details>
      </div>

      <template #footer>
        <el-button @click="editorVisible = false">{{ $t('agent.common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="savePlugin">{{ $t('agent.common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/request'

const DEFAULT_SCRIPT = `from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my_plugin")


@mcp.tool()
def echo(text: str) -> str:
    """Return the text unchanged."""
    return text


if __name__ == "__main__":
    mcp.run()
`

const tenantOptions = ref([])
const appKey = ref('')
const plugins = ref([])
const builtinOptions = ref([])

const editorVisible = ref(false)
const saving = ref(false)
const debugging = ref(false)
const loadingTools = ref(false)
const debugResult = ref('')
const debugRaw = ref('')

const emptyEditing = () => ({
  id: null,
  plugin_name: '',
  plugin_type: 'custom',
  builtin_key: '',
  description: '',
  enabled: true,
  sort_order: 0,
  script_content: DEFAULT_SCRIPT,
  config_json_text: ''
})
const editing = ref(emptyEditing())
const debug = ref({ tool_name: '', tool_args_text: '', tools: [] })

const currentToolDesc = computed(() => {
  const t = (debug.value.tools || []).find(x => x.name === debug.value.tool_name)
  return t ? (t.description || '').trim() : ''
})

const resetDebug = () => {
  debug.value = { tool_name: '', tool_args_text: '', tools: [] }
  debugResult.value = ''
  debugRaw.value = ''
}

const loadTenants = async () => {
  try {
    tenantOptions.value = await api.get('/user/tenants')
    if (!appKey.value && tenantOptions.value.length) {
      appKey.value = tenantOptions.value[0].app_key
      await loadPlugins()
    }
  } catch (e) {
    ElMessage.error('加载AppKey列表失败')
  }
}

const loadBuiltins = async () => {
  try {
    builtinOptions.value = await api.get('/admin/agent/plugin-builtins')
  } catch (e) {
    builtinOptions.value = []
  }
}

const loadPlugins = async () => {
  if (!appKey.value) return
  try {
    plugins.value = await api.get(`/admin/agent/flows/${appKey.value}/plugins`)
  } catch (e) {
    plugins.value = []
  }
}

const openCreate = () => {
  editing.value = emptyEditing()
  resetDebug()
  editorVisible.value = true
}

const openEdit = (row) => {
  editing.value = {
    id: row.id,
    plugin_name: row.plugin_name,
    plugin_type: row.plugin_type,
    builtin_key: row.builtin_key || '',
    description: row.description || '',
    enabled: row.enabled !== false,
    sort_order: row.sort_order || 0,
    script_content: row.script_content || DEFAULT_SCRIPT,
    config_json_text: row.config_json || ''
  }
  resetDebug()
  editorVisible.value = true
}

const buildPayload = () => {
  let config_json = null
  if (editing.value.config_json_text && editing.value.config_json_text.trim()) {
    try {
      config_json = JSON.parse(editing.value.config_json_text)
    } catch {
      throw new Error('config_json 不是合法的 JSON')
    }
  }
  return {
    plugin_name: editing.value.plugin_name.trim(),
    plugin_type: editing.value.plugin_type,
    builtin_key: editing.value.plugin_type === 'builtin' ? editing.value.builtin_key : null,
    description: editing.value.description,
    enabled: editing.value.enabled,
    sort_order: editing.value.sort_order,
    script_content: editing.value.plugin_type === 'custom' ? editing.value.script_content : null,
    config_json
  }
}

const savePlugin = async () => {
  let payload
  try {
    payload = buildPayload()
  } catch (e) {
    ElMessage.error(e.message)
    return
  }
  saving.value = true
  try {
    if (editing.value.id) {
      await api.put(`/admin/agent/plugins/${editing.value.id}`, payload)
    } else {
      await api.post(`/admin/agent/flows/${appKey.value}/plugins`, payload)
    }
    editorVisible.value = false
    await loadPlugins()
    ElMessage.success('已保存并更新该AppKey的Agent实例')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// Build the /debug request body from the current editor + debug fields.
// Throws on invalid JSON in config_json / tool_args.
const buildDebugRequest = (includeTool) => {
  const payload = buildPayload()
  let tool_args = null
  if (includeTool && debug.value.tool_args_text && debug.value.tool_args_text.trim()) {
    try {
      tool_args = JSON.parse(debug.value.tool_args_text)
    } catch {
      throw new Error('调用参数不是合法的 JSON')
    }
  }
  return {
    app_key: appKey.value,
    plugin_id: editing.value.id,
    plugin_name: payload.plugin_name || 'debug_plugin',
    plugin_type: payload.plugin_type,
    builtin_key: payload.builtin_key,
    script_content: payload.script_content,
    config_json: payload.config_json,
    tool_name: includeTool ? (debug.value.tool_name || null) : null,
    tool_args: includeTool ? tool_args : null
  }
}

const defaultForType = (type) => {
  const t = Array.isArray(type) ? type[0] : type
  switch (t) {
    case 'integer':
    case 'number': return 0
    case 'boolean': return false
    case 'array': return []
    case 'object': return {}
    default: return ''
  }
}

// When a tool is selected, prefill the args textarea with a template from its schema.
const onToolChange = (name) => {
  const tool = (debug.value.tools || []).find(x => x.name === name)
  const props = tool?.input_schema?.properties
  if (!props) return
  const tmpl = {}
  for (const [key, spec] of Object.entries(props)) {
    tmpl[key] = defaultForType(spec?.type)
  }
  debug.value.tool_args_text = JSON.stringify(tmpl, null, 2)
}

// Parse the MCP tool result blocks into a clean object/array for display.
const extractCalledResult = (called) => {
  if (!called) return ''
  const blocks = called.content || []
  if (!blocks.length) return '（无返回内容）'
  const parsed = []
  let allJson = true
  for (const b of blocks) {
    const text = b && typeof b.text === 'string' ? b.text : null
    if (text === null) { allJson = false; parsed.push(b); continue }
    try { parsed.push(JSON.parse(text)) } catch { allJson = false; parsed.push(text) }
  }
  if (allJson) {
    return JSON.stringify(parsed.length === 1 ? parsed[0] : parsed, null, 2)
  }
  return blocks.map(b => (b && b.text != null ? b.text : JSON.stringify(b))).join('\n')
}

const loadTools = async () => {
  let req
  try {
    req = buildDebugRequest(false)
  } catch (e) {
    ElMessage.error(e.message)
    return
  }
  loadingTools.value = true
  try {
    const result = await api.post('/admin/agent/plugins/debug', req)
    debug.value.tools = result.tools || []
    if (!debug.value.tools.length) {
      ElMessage.warning('脚本未暴露任何工具')
    } else {
      if (!debug.value.tool_name || !debug.value.tools.some(t => t.name === debug.value.tool_name)) {
        debug.value.tool_name = debug.value.tools[0].name
      }
      onToolChange(debug.value.tool_name)
      ElMessage.success(`发现 ${debug.value.tools.length} 个工具，已选择「${debug.value.tool_name}」`)
    }
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '加载工具失败')
  } finally {
    loadingTools.value = false
  }
}

const runDebug = async () => {
  let req
  try {
    req = buildDebugRequest(true)
  } catch (e) {
    ElMessage.error(e.message)
    return
  }
  if (!req.tool_name) {
    ElMessage.warning('请先选择工具名（点击“加载工具”可自动发现）')
    return
  }
  debugging.value = true
  debugResult.value = ''
  debugRaw.value = ''
  try {
    const result = await api.post('/admin/agent/plugins/debug', req)
    debug.value.tools = result.tools || debug.value.tools
    debugResult.value = extractCalledResult(result.called)
    debugRaw.value = JSON.stringify(result, null, 2)
    if (result.called && result.called.is_error) {
      ElMessage.warning('工具返回错误，请查看结果')
    }
  } catch (e) {
    debugResult.value = e?.response?.data?.detail || '调试失败'
  } finally {
    debugging.value = false
  }
}

const removePlugin = async (row) => {
  try {
    await ElMessageBox.confirm(`确认删除插件「${row.plugin_name}」?`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await api.delete(`/admin/agent/plugins/${row.id}`)
    await loadPlugins()
    ElMessage.success('已删除并更新实例')
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadBuiltins()
  loadTenants()
})
</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.ml-2 { margin-left: 8px; }
.code-area :deep(textarea) {
  font-family: 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 12px;
}
.debug-hint {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 12px;
}
.tool-desc {
  font-size: 12px;
  color: #475569;
  white-space: pre-wrap;
}
.debug-result {
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  max-height: 300px;
  overflow: auto;
}
.debug-result-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #38bdf8;
  margin-bottom: 6px;
}
.debug-result pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.debug-raw {
  margin-top: 10px;
  font-size: 12px;
}
.debug-raw summary {
  cursor: pointer;
  color: #64748b;
}
.debug-raw pre {
  margin: 8px 0 0;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 10px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 220px;
  overflow: auto;
}
</style>
