<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>{{ $t('agent.orchestrator.title') }}</h2>
        <p>{{ $t('agent.orchestrator.subtitle') }}</p>
      </div>
      <div>
        <el-button :disabled="!appKey" @click="refreshInstance">{{ $t('agent.orchestrator.refresh') }}</el-button>
        <el-button type="primary" :loading="saving" :disabled="!appKey" @click="saveFlow">
          {{ $t('agent.orchestrator.save') }}
        </el-button>
      </div>
    </div>

    <el-card class="mb-4">
      <el-form :model="flow" label-width="120px">
        <el-form-item :label="$t('agent.common.appKey')">
          <el-select v-model="appKey" filterable style="width: 360px" @change="loadAll">
            <el-option v-for="t in tenantOptions" :key="t.app_key" :label="t.app_key" :value="t.app_key" />
          </el-select>
          <el-tag v-if="flowExists" type="success" class="ml-3">{{ $t('agent.orchestrator.configured') }}</el-tag>
          <el-tag v-else type="info" class="ml-3">{{ $t('agent.orchestrator.notConfigured') }}</el-tag>
        </el-form-item>

        <template v-if="appKey">
          <el-form-item :label="$t('agent.orchestrator.name')">
            <el-input v-model="flow.name" style="width: 360px" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.mode')">
            <el-radio-group v-model="flow.mode">
              <el-radio-button label="single">{{ $t('agent.orchestrator.modeSingle') }}</el-radio-button>
              <el-radio-button label="tool">{{ $t('agent.orchestrator.modeTool') }}</el-radio-button>
              <el-radio-button label="handoff">{{ $t('agent.orchestrator.modeHandoff') }}</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.model')">
            <el-input v-model="flow.model" style="width: 360px" :placeholder="$t('agent.orchestrator.modelPh')" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.maxTurns')">
            <el-input-number v-model="flow.max_turns" :min="1" :max="50" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.enabled')">
            <el-switch v-model="flow.enabled" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.instructions')">
            <el-input v-model="flow.instructions" type="textarea" :rows="5"
              :placeholder="$t('agent.orchestrator.instructionsPh')" />
          </el-form-item>
        </template>
      </el-form>
    </el-card>

    <!-- Plugin association -->
    <el-card v-if="appKey" class="mb-4">
      <template #header>
        <div class="flex items-center justify-between">
          <span>{{ $t('agent.orchestrator.plugins') }}</span>
          <div>
            <el-select v-model="builtinToAdd" :placeholder="$t('agent.orchestrator.addBuiltin')" style="width: 260px">
              <el-option v-for="b in builtinOptions" :key="b.builtin_key" :label="b.builtin_key" :value="b.builtin_key" />
            </el-select>
            <el-button class="ml-2" :disabled="!builtinToAdd" @click="addBuiltin">{{ $t('agent.orchestrator.add') }}</el-button>
          </div>
        </div>
      </template>
      <el-table :data="plugins" size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="plugin_name" :label="$t('agent.plugins.name')" />
        <el-table-column prop="plugin_type" :label="$t('agent.plugins.type')" width="100" />
        <el-table-column prop="builtin_key" :label="$t('agent.plugins.builtinKey')" width="130" />
        <el-table-column :label="$t('agent.plugins.enabled')" width="90">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="togglePlugin(row)" />
          </template>
        </el-table-column>
        <el-table-column :label="$t('agent.common.actions')" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="removePlugin(row)">{{ $t('agent.common.delete') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!plugins.length" :description="$t('agent.orchestrator.noPlugins')" />
    </el-card>

    <!-- Sub-agents (tool / handoff modes) -->
    <el-card v-if="appKey && flow.mode !== 'single'" class="mb-4">
      <template #header>
        <div class="flex items-center justify-between">
          <span>{{ $t('agent.orchestrator.subAgents') }}</span>
          <el-button @click="addSubAgent">{{ $t('agent.orchestrator.addSubAgent') }}</el-button>
        </div>
      </template>
      <div v-for="(sub, idx) in flow.sub_agents" :key="idx" class="sub-agent-card">
        <div class="flex items-center justify-between mb-2">
          <strong>#{{ idx + 1 }}</strong>
          <el-button size="small" type="danger" @click="flow.sub_agents.splice(idx, 1)">
            {{ $t('agent.common.delete') }}
          </el-button>
        </div>
        <el-form label-width="120px">
          <el-form-item :label="$t('agent.orchestrator.subName')">
            <el-input v-model="sub.name" style="width: 320px" />
          </el-form-item>
          <el-form-item v-if="flow.mode === 'tool'" :label="$t('agent.orchestrator.toolName')">
            <el-input v-model="sub.tool_name" style="width: 320px" placeholder="snake_case" />
          </el-form-item>
          <el-form-item v-if="flow.mode === 'tool'" :label="$t('agent.orchestrator.toolDesc')">
            <el-input v-model="sub.tool_description" style="width: 320px" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.model')">
            <el-input v-model="sub.model" style="width: 320px" :placeholder="$t('agent.orchestrator.modelPh')" />
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.subPlugins')">
            <el-select v-model="sub.plugin_ids" multiple style="width: 420px">
              <el-option v-for="p in plugins" :key="p.id" :label="`#${p.id} ${p.plugin_name}`" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="$t('agent.orchestrator.instructions')">
            <el-input v-model="sub.instructions" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
      </div>
      <el-empty v-if="!flow.sub_agents.length" :description="$t('agent.orchestrator.noSubAgents')" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../../api/request'

const tenantOptions = ref([])
const appKey = ref('')
const flowExists = ref(false)
const saving = ref(false)
const plugins = ref([])
const builtinOptions = ref([])
const builtinToAdd = ref('')

const emptyFlow = () => ({
  name: 'Agent',
  instructions: '',
  mode: 'single',
  model: '',
  max_turns: 10,
  sub_agents: [],
  enabled: true
})
const flow = ref(emptyFlow())

const loadTenants = async () => {
  try {
    tenantOptions.value = await api.get('/user/tenants')
    if (!appKey.value && tenantOptions.value.length) {
      appKey.value = tenantOptions.value[0].app_key
      await loadAll()
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

const loadFlow = async () => {
  if (!appKey.value) return
  try {
    const data = await api.get(`/admin/agent/flows/${appKey.value}`)
    if (data && data.id) {
      flowExists.value = true
      flow.value = {
        name: data.name || 'Agent',
        instructions: data.instructions || '',
        mode: data.mode || 'single',
        model: data.model || '',
        max_turns: data.max_turns || 10,
        sub_agents: Array.isArray(data.sub_agents) ? data.sub_agents.map(s => ({
          name: s.name || '',
          instructions: s.instructions || '',
          model: s.model || '',
          plugin_ids: s.plugin_ids || [],
          tool_name: s.tool_name || '',
          tool_description: s.tool_description || ''
        })) : [],
        enabled: data.enabled !== false
      }
    } else {
      flowExists.value = false
      flow.value = emptyFlow()
    }
  } catch (e) {
    flowExists.value = false
    flow.value = emptyFlow()
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

const loadAll = async () => {
  await Promise.all([loadFlow(), loadPlugins()])
}

const saveFlow = async () => {
  if (!appKey.value) return
  saving.value = true
  try {
    await api.put(`/admin/agent/flows/${appKey.value}`, flow.value)
    flowExists.value = true
    ElMessage.success('已保存并更新该AppKey的Agent实例')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const refreshInstance = async () => {
  if (!appKey.value) return
  try {
    await api.post(`/admin/agent/flows/${appKey.value}/refresh`)
    ElMessage.success('Agent实例缓存已刷新')
  } catch (e) {
    ElMessage.error('刷新失败')
  }
}

const addBuiltin = async () => {
  if (!builtinToAdd.value) return
  try {
    await api.post(`/admin/agent/flows/${appKey.value}/plugins`, {
      plugin_name: builtinToAdd.value,
      plugin_type: 'builtin',
      builtin_key: builtinToAdd.value,
      enabled: true
    })
    builtinToAdd.value = ''
    await loadPlugins()
    ElMessage.success('已添加内置插件并更新实例')
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  }
}

const togglePlugin = async (row) => {
  try {
    await api.put(`/admin/agent/plugins/${row.id}`, { ...row })
    ElMessage.success('已更新')
  } catch (e) {
    row.enabled = !row.enabled
    ElMessage.error('更新失败')
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

const addSubAgent = () => {
  flow.value.sub_agents.push({
    name: `SubAgent${flow.value.sub_agents.length + 1}`,
    instructions: '',
    model: '',
    plugin_ids: [],
    tool_name: '',
    tool_description: ''
  })
}

onMounted(() => {
  loadBuiltins()
  loadTenants()
})
</script>

<style scoped>
.ml-2 { margin-left: 8px; }
.ml-3 { margin-left: 12px; }
.mb-2 { margin-bottom: 8px; }
.mb-4 { margin-bottom: 16px; }
.sub-agent-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px;
  margin-bottom: 12px;
  background: #f8fafc;
}
</style>
