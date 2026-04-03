<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Token使用统计</h2>

    <el-card class="mb-4">
      <template #header>
        <span class="font-bold">总体统计</span>
      </template>
      <div class="grid grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-gray-500 text-sm">总Token数</div>
          <div class="text-2xl font-bold text-primary">{{ summary.total_tokens?.toLocaleString() }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500 text-sm">本月Token</div>
          <div class="text-2xl font-bold text-green-600">{{ summary.current_month_tokens?.toLocaleString() }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500 text-sm">上月Token</div>
          <div class="text-2xl font-bold text-gray-600">{{ summary.last_month_tokens?.toLocaleString() }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500 text-sm">月度变化</div>
          <div class="text-2xl font-bold" :class="summary.monthly_change_percent >= 0 ? 'text-red-600' : 'text-green-600'">
            {{ summary.monthly_change_percent?.toFixed(2) }}%
          </div>
        </div>
      </div>
    </el-card>

    <el-table :data="tokenStats" border stripe>
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

    <el-dialog v-model="chartVisible" title="30天Token使用趋势" width="800px">
      <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
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
const chartContainer = ref(null)
let chartInstance = null

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

    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(chartContainer.value)
    const dates = response.data.map(item => item.date)
    const tokens = response.data.map(item => item.token_count)
    const requests = response.data.map(item => item.request_count)

    chartInstance.setOption({
      title: {
        text: `${row.tenant_name || row.app_key} - 30天使用趋势`
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['Token数量', '请求次数']
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: [
        {
          type: 'value',
          name: 'Token数量'
        },
        {
          type: 'value',
          name: '请求次数'
        }
      ],
      series: [
        {
          name: 'Token数量',
          type: 'line',
          data: tokens,
          smooth: true,
          itemStyle: { color: '#00796B' }
        },
        {
          name: '请求次数',
          type: 'bar',
          yAxisIndex: 1,
          data: requests,
          itemStyle: { color: '#B2DFDB' }
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

<style scoped>
.text-primary {
  color: #00796B;
}
</style>
