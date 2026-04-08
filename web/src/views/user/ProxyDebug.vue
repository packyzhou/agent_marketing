<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">对话调试</h2>

    <el-card class="mb-4">
      <el-form :model="form" label-width="140px">
        <el-form-item label="转发服务API地址">
          <el-input v-model="form.apiUrl" placeholder="例如: http://127.0.0.1:8000/chat/completions" />
        </el-form-item>
        <el-form-item label="AppKey">
          <el-select
            v-model="form.appKey"
            placeholder="请选择AppKey"
            filterable
            style="width: 100%"
            @change="handleAppKeyChange"
          >
            <el-option
              v-for="tenant in tenantOptions"
              :key="tenant.app_key"
              :label="tenant.app_key"
              :value="tenant.app_key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型(可选)">
          <el-input
            v-model="form.model"
            :placeholder="modelLoading ? '正在查询租户配置模型…' : '不填则使用租户配置模型'"
          />
        </el-form-item>
        <el-form-item label="问题输入">
          <el-input v-model="form.question" type="textarea" :rows="4" placeholder="请输入问题后点击发送" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="sendMessage">发送并开始流式调试</el-button>
          <el-button :disabled="!loading" @click="stopStream">停止</el-button>
          <el-button @click="resetResult">清空结果</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="mb-4">
      <template #header>AI响应（流式 Markdown）</template>
      <div v-if="aiResponse" class="panel markdown-panel">
        <div class="markdown-body" v-html="renderedAiResponse"></div>
      </div>
      <div v-else class="panel placeholder-panel">等待响应...</div>
    </el-card>

    <el-row :gutter="16">
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>用户输入信息</template>
          <div class="meta-panel">
            <pre>{{ displayRequest }}</pre>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card>
          <template #header>错误详情</template>
          <div class="meta-panel">
            <pre>{{ displayError }}</pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import api from '../../api/request'

const form = ref({
  apiUrl: `${window.location.origin}/chat/completions`,
  appKey: '',
  model: '',
  question: ''
})

const loading = ref(false)
const aiResponse = ref('')
const requestInfo = ref(null)
const errorInfo = ref(null)
const tenantOptions = ref([])
const modelLoading = ref(false)
let abortController = null

marked.setOptions({
  gfm: true,
  breaks: true
})

const displayRequest = computed(() => {
  if (!requestInfo.value) return '尚未发送请求'
  return JSON.stringify(requestInfo.value, null, 2)
})

const displayError = computed(() => {
  if (!errorInfo.value) return '暂无错误'
  return JSON.stringify(errorInfo.value, null, 2)
})

const renderedAiResponse = computed(() => {
  if (!aiResponse.value) {
    return ''
  }
  return DOMPurify.sanitize(marked.parse(aiResponse.value))
})

const resetResult = () => {
  aiResponse.value = ''
  errorInfo.value = null
}

const stopStream = () => {
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  loading.value = false
}

const processSseText = (text) => {
  const blocks = text.split('\n\n')
  for (const block of blocks) {
    const lines = block.split('\n').map(line => line.trim()).filter(Boolean)
    for (const line of lines) {
      if (!line.startsWith('data:')) {
        continue
      }
      const payload = line.slice(5).trim()
      if (!payload || payload === '[DONE]') {
        continue
      }
      try {
        const json = JSON.parse(payload)
        if (json?.error) {
          errorInfo.value = {
            type: 'sse_error',
            url: form.value.apiUrl,
            detail: json.error
          }
          ElMessage.error(`调试失败: ${json.error.message || '上游服务异常'}`)
          continue
        }
        const choice = json?.choices?.[0]
        const deltaText = choice?.delta?.content || choice?.message?.content || ''
        if (deltaText) {
          aiResponse.value += deltaText
        }
      } catch (error) {
        continue
      }
    }
  }
}

const sendMessage = async () => {
  if (!form.value.apiUrl || !form.value.appKey || !form.value.question) {
    ElMessage.warning('请先填写API地址、appKey和问题')
    return
  }

  const normalizedApiUrl = form.value.apiUrl.trim()
  const normalizedAppKey = form.value.appKey.trim()
  const normalizedQuestion = form.value.question.trim()
  const normalizedModel = form.value.model.trim()

  if (!normalizedApiUrl || !normalizedAppKey || !normalizedQuestion) {
    ElMessage.warning('请先填写API地址、appKey和问题')
    return
  }

  form.value.apiUrl = normalizedApiUrl
  form.value.appKey = normalizedAppKey
  form.value.question = normalizedQuestion
  form.value.model = normalizedModel

  stopStream()
  loading.value = true
  aiResponse.value = ''
  errorInfo.value = null
  abortController = new AbortController()

  const payload = {
    app_key: normalizedAppKey,
    messages: [{ role: 'user', content: normalizedQuestion }],
    stream: true
  }
  if (normalizedModel) {
    payload.model = normalizedModel
  }

  requestInfo.value = {
    url: normalizedApiUrl,
    headers: {
      'Content-Type': 'application/json',
      'X-App-Key': normalizedAppKey
    },
    body: payload
  }

  try {
    const response = await fetch(normalizedApiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-App-Key': normalizedAppKey
      },
      body: JSON.stringify(payload),
      signal: abortController.signal
    })

    if (!response.ok || !response.body) {
      const errorText = await response.text()
      errorInfo.value = {
        type: 'http_error',
        status: response.status,
        statusText: response.statusText,
        url: normalizedApiUrl,
        responseText: errorText || ''
      }
      throw new Error(errorText || `请求失败: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let pending = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      pending += decoder.decode(value, { stream: true })
      const parts = pending.split('\n\n')
      pending = parts.pop() || ''
      processSseText(parts.join('\n\n'))
    }
    if (pending) {
      processSseText(pending)
    }
  } catch (error) {
    if (error.name !== 'AbortError') {
      if (!errorInfo.value) {
        errorInfo.value = {
          type: 'network_error',
          message: error.message || '未知错误',
          url: normalizedApiUrl
        }
      }
      ElMessage.error(`调试失败: ${error.message || '未知错误'}`)
    }
  } finally {
    loading.value = false
    abortController = null
  }
}

const loadTenantOptions = async () => {
  try {
    tenantOptions.value = await api.get('/user/tenants')
    if (!form.value.appKey && tenantOptions.value.length > 0) {
      form.value.appKey = tenantOptions.value[0].app_key
      await loadAppKeyModel(form.value.appKey)
    }
  } catch (error) {
    ElMessage.error('加载AppKey列表失败')
  }
}

const loadAppKeyModel = async (appKey) => {
  if (!appKey) {
    form.value.model = ''
    return
  }
  modelLoading.value = true
  try {
    const keys = await api.get(`/user/tenants/${appKey}/provider-keys`)
    const modelName = Array.isArray(keys) && keys.length > 0 ? (keys[0].model_name || '') : ''
    form.value.model = modelName
  } catch (error) {
    form.value.model = ''
  } finally {
    modelLoading.value = false
  }
}

const handleAppKeyChange = (appKey) => {
  loadAppKeyModel(appKey)
}

onMounted(() => {
  loadTenantOptions()
})
</script>

<style scoped>
.panel {
  min-height: 360px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.meta-panel {
  min-height: 360px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.placeholder-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.markdown-panel {
  overflow-wrap: anywhere;
}

.markdown-body {
  color: #111827;
  line-height: 1.75;
  overflow-wrap: anywhere;
}

.markdown-body :deep(p) {
  margin: 0 0 12px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0 0 12px;
  padding-left: 20px;
}

.markdown-body :deep(li) {
  margin-bottom: 4px;
}

.markdown-body :deep(pre) {
  margin: 12px 0;
  padding: 12px;
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-body :deep(code) {
  font-size: 12px;
  background: rgba(15, 23, 42, 0.08);
  border-radius: 4px;
  padding: 2px 4px;
}

.markdown-body :deep(pre code) {
  background: transparent;
  padding: 0;
}

.markdown-body :deep(blockquote) {
  margin: 12px 0;
  padding-left: 12px;
  border-left: 4px solid #d1d5db;
  color: #4b5563;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #d1d5db;
  padding: 8px 10px;
  text-align: left;
}

.markdown-body :deep(img) {
  max-width: 100%;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
