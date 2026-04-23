<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>Token 使用统计</h2>
        <p>掌握租户 Token 消耗与月度变化趋势</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="border border-slate-100 rounded-2xl p-5 hover:border-slate-200 transition-colors">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">总 Token 数</div>
        <div class="text-2xl font-black tracking-tight text-slate-900 font-mono">
          {{ summary.total_tokens?.toLocaleString() || '0' }}
        </div>
      </div>
      <div class="border border-slate-100 rounded-2xl p-5 hover:border-slate-200 transition-colors">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">本月 Token</div>
        <div class="text-2xl font-black tracking-tight text-cyan-500 font-mono">
          {{ summary.current_month_tokens?.toLocaleString() || '0' }}
        </div>
      </div>
      <div class="border border-slate-100 rounded-2xl p-5 hover:border-slate-200 transition-colors">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">上月 Token</div>
        <div class="text-2xl font-black tracking-tight text-slate-500 font-mono">
          {{ summary.last_month_tokens?.toLocaleString() || '0' }}
        </div>
      </div>
      <div class="border border-slate-100 rounded-2xl p-5 hover:border-slate-200 transition-colors">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">月度变化</div>
        <div class="text-2xl font-black tracking-tight font-mono"
          :class="summary.monthly_change_percent >= 0 ? 'text-rose-500' : 'text-emerald-500'">
          {{ summary.monthly_change_percent?.toFixed(2) || '0.00' }}%
        </div>
      </div>
    </div>

    <el-table :data="tokenStats" stripe>
      <el-table-column prop="app_key" label="AppKey" width="200" />
      <el-table-column prop="tenant_name" label="租户名称" width="150" />
      <el-table-column prop="total_tokens" label="总Token" width="120" sortable>
        <template #default="{ row }">
          {{ row.total_tokens.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="current_month_tokens" label="本月Token" width="120" sortable>
        <template #default="{ row }">
          {{ row.current_month_tokens.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="last_month_tokens" label="上月Token" width="120" sortable>
        <template #default="{ row }">
          {{ row.last_month_tokens.toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="monthly_change_percent" label="月度变化" width="100" sortable>
        <template #default="{ row }">
          <span :class="row.monthly_change_percent >= 0 ? 'text-red-600' : 'text-green-600'">
            {{ row.monthly_change_percent?.toFixed(2) }}%
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="viewChart(row)">
            查看趋势
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="chartVisible" title="30天 Token 使用趋势" width="900px">
      <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Token 数量趋势图</div>
      <div ref="tokenChartContainer" style="width: 100%; height: 320px;"></div>
      <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mt-8 mb-3">请求次数趋势图</div>
      <div ref="requestChartContainer" style="width: 100%; height: 320px;"></div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const tokenStats = ref([])
const summary = ref({})
const chartVisible = ref(false)
const tokenChartContainer = ref(null)
const requestChartContainer = ref(null)
let tokenChartInstance = null
let requestChartInstance = null

const formatDateLabel = (dateText) => {
  if (!dateText || typeof dateText !== 'string') return ''
  const parts = dateText.split('-')
  if (parts.length !== 3) return dateText
  return `${parts[1]}-${parts[2]}`
}

const loadTokenStats = async () => {
  try {
    const response = await axios.get('/api/admin/token-stats', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    tokenStats.value = response.data
  } catch (error) {
    ElMessage.error('加载Token统计失败')
  }
}

const loadSummary = async () => {
  try {
    const response = await axios.get('/api/admin/token-stats/summary', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    summary.value = response.data
  } catch (error) {
    ElMessage.error('加载总体统计失败')
  }
}

const viewChart = async (row) => {
  try {
    const response = await axios.get(`/api/admin/token-stats/${row.app_key}/daily`, {
      params: { days: 30 },
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })

    chartVisible.value = true
    await nextTick()

    if (tokenChartInstance) {
      tokenChartInstance.dispose()
    }
    if (requestChartInstance) {
      requestChartInstance.dispose()
    }
    tokenChartInstance = echarts.init(tokenChartContainer.value)
    requestChartInstance = echarts.init(requestChartContainer.value)

    const dates = response.data.map(item => formatDateLabel(item.date))
    const tokens = response.data.map(item => item.token_count)
    const requests = response.data.map(item => item.request_count)

    tokenChartInstance.setOption({
      title: {
        text: `${row.tenant_name || row.app_key} - Token数量趋势`
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: 'Token数量'
      },
      series: [
        {
          name: 'Token数量',
          type: 'line',
          data: tokens,
          smooth: true,
          itemStyle: { color: '#00796B' }
        }
      ]
    })

    requestChartInstance.setOption({
      title: {
        text: `${row.tenant_name || row.app_key} - 请求次数趋势`
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '请求次数'
      },
      series: [
        {
          name: '请求次数',
          type: 'line',
          data: requests,
          smooth: true,
          itemStyle: { color: '#3B82F6' }
        }
      ]
    })
  } catch (error) {
    ElMessage.error('加载趋势数据失败')
  }
}

onMounted(() => {
  loadTokenStats()
  loadSummary()
})
</script>

