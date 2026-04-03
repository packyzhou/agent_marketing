<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Token使用统计</h2>

    <el-card class="mb-4">
      <template #header>
        <span class="font-bold">我的Token统计</span>
      </template>
      <div class="grid grid-cols-3 gap-4">
        <div class="text-center">
          <div class="text-gray-500 text-sm">总Token数</div>
          <div class="text-2xl font-bold text-primary">{{ totalTokens.toLocaleString() }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500 text-sm">本月Token</div>
          <div class="text-2xl font-bold text-green-600">{{ currentMonthTokens.toLocaleString() }}</div>
        </div>
        <div class="text-center">
          <div class="text-gray-500 text-sm">月度变化</div>
          <div class="text-2xl font-bold" :class="monthlyChange >= 0 ? 'text-red-600' : 'text-green-600'">
            {{ monthlyChange?.toFixed(2) }}%
          </div>
        </div>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold">30天使用趋势</span>
          <el-select v-model="selectedAppKey" placeholder="选择租户" @change="loadStatsAndChart" style="width: 250px">
            <el-option v-for="t in tenants" :key="t.app_key" :label="t.tenant_name || t.app_key" :value="t.app_key" />
          </el-select>
        </div>
      </template>
      <div class="text-lg font-medium mb-2">Token数量趋势图</div>
      <div ref="tokenChartContainer" style="width: 100%; height: 320px;"></div>
      <div class="text-lg font-medium mt-6 mb-2">请求次数趋势图</div>
      <div ref="requestChartContainer" style="width: 100%; height: 320px;"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'
import * as echarts from 'echarts'

const tenants = ref([])
const selectedAppKey = ref(null)
const totalTokens = ref(0)
const currentMonthTokens = ref(0)
const monthlyChange = ref(0)
const tokenChartContainer = ref(null)
const requestChartContainer = ref(null)
let tokenChartInstance = null
let requestChartInstance = null

const loadTenants = async () => {
  try {
    tenants.value = await api.get('/user/tenants')
    if (tenants.value.length > 0) {
      selectedAppKey.value = tenants.value[0].app_key
      await loadStatsAndChart()
    }
  } catch (error) {
    ElMessage.error('加载租户列表失败')
  }
}

const loadStatsAndChart = async () => {
  if (!selectedAppKey.value) return

  try {
    const response = await api.get(`/user/stats/${selectedAppKey.value}`, {
      params: { days: 30 }
    })
    totalTokens.value = response.total_tokens || 0
    currentMonthTokens.value = response.current_month_tokens || 0
    monthlyChange.value = response.month_comparison || 0

    await nextTick()

    if (tokenChartInstance) {
      tokenChartInstance.dispose()
    }
    if (requestChartInstance) {
      requestChartInstance.dispose()
    }
    tokenChartInstance = echarts.init(tokenChartContainer.value)
    requestChartInstance = echarts.init(requestChartContainer.value)
    const daily = Array.isArray(response.daily) ? response.daily : []
    const dates = daily.map(item => item.date)
    const tokens = daily.map(item => item.token_count)
    const requests = daily.map(item => item.request_count)

    tokenChartInstance.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45
        }
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
          itemStyle: { color: '#00796B' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(0, 121, 107, 0.3)' },
                { offset: 1, color: 'rgba(0, 121, 107, 0.05)' }
              ]
            }
          }
        },
      ]
    })

    requestChartInstance.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45
        }
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
          itemStyle: { color: '#3B82F6' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
              ]
            }
          }
        }
      ]
    })
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

onMounted(loadTenants)
</script>

<style scoped>
.text-primary {
  color: #00796B;
}
</style>
