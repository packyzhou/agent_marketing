<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">对话调试</h2>

    <el-card class="mb-4">
      <el-form :model="form" label-width="140px">
        <el-form-item label="转发服务API地址">
          <el-input v-model="form.apiUrl" placeholder="例如: http://127.0.0.1:8000/api/proxy/chat/completions/sse" />
        </el-form-item>
        <el-form-item label="AppKey">
          <el-select v-model="form.appKey" placeholder="请选择AppKey" filterable style="width: 100%">
            <el-option
              v-for="tenant in tenantOptions"
              :key="tenant.app_key"
              :label="tenant.app_key"
              :value="tenant.app_key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模型(可选)">
          <el-input v-model="form.model" placeholder="不填则使用租户配置模型" />
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

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card>
          <template #header>AI响应（流式）</template>
          <div class="panel">{{ aiResponse || '等待响应...' }}</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>用户输入信息</template>
          <div class="panel">
            <pre>{{ displayRequest }}</pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="mt-4">
      <template #header>错误详情</template>
      <div class="panel">
        <pre>{{ displayError }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const form = ref({
  apiUrl: `${window.location.origin}/api/proxy/chat/completions/sse`,
  appKey: '',
  model: '',
  question: ''
})

const loading = ref(false)
const aiResponse = ref('')
const requestInfo = ref(null)
const errorInfo = ref(null)
const tenantOptions = ref([])
let abortController = null

const displayRequest = computed(() => {
  if (!requestInfo.value) return '尚未发送请求'
  return JSON.stringify(requestInfo.value, null, 2)
})

const displayError = computed(() => {
  if (!errorInfo.value) return '暂无错误'
  return JSON.stringify(errorInfo.value, null, 2)
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
    }
  } catch (error) {
    ElMessage.error('加载AppKey列表失败')
  }
}

onMounted(() => {
  loadTenantOptions()
})
</script>

<style scoped>
.panel {
  min-height: 360px;
  white-space: pre-wrap;
  word-break: break-word;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
