<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">数据中心</h2>
    <el-card class="mb-4">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold">Token趋势</span>
          <el-select
            v-model="selectedAppKey"
            placeholder="选择租户"
            style="width: 250px"
            @change="loadStatsAndChart"
          >
            <el-option
              v-for="tenant in tenants"
              :key="tenant.app_key"
              :label="tenant.tenant_name || tenant.app_key"
              :value="tenant.app_key"
            />
          </el-select>
        </div>
      </template>
      <div class="text-lg font-medium mb-2">Token数量趋势图</div>
      <div ref="chartRef" style="width: 100%; height: 360px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import api from '../../api/request'

const tenants = ref([])
const selectedAppKey = ref(null)
const chartRef = ref(null)
let chartInstance = null

const formatDateLabel = (dateText) => {
  if (!dateText || typeof dateText !== 'string') return ''
  const parts = dateText.split('-')
  if (parts.length !== 3) return dateText
  return `${parts[1]}-${parts[2]}`
}

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
    await nextTick()
    if (chartInstance) {
      chartInstance.dispose()
    }
    chartInstance = echarts.init(chartRef.value)
    const daily = Array.isArray(response.daily) ? response.daily : []
    const dates = daily.map(item => formatDateLabel(item.date))
    const tokens = daily.map(item => item.token_count)
    chartInstance.setOption({
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
