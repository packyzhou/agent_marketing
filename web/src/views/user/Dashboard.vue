<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">数据中心</h2>

    <el-select v-model="selectedAppKey" placeholder="选择租户" class="mb-4" @change="loadStats">
      <el-option
        v-for="tenant in tenants"
        :key="tenant.app_key"
        :label="tenant.app_key"
        :value="tenant.app_key"
      />
    </el-select>

    <div v-if="stats" class="mb-6">
      <el-card>
        <h3 class="text-lg font-bold mb-2">总Token消耗</h3>
        <p class="text-3xl font-bold text-primary">{{ stats.total }}</p>
      </el-card>
    </div>

    <div ref="chartRef" style="width: 100%; height: 400px"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import api from '../../api/request'

const tenants = ref([])
const selectedAppKey = ref('')
const stats = ref(null)
const chartRef = ref(null)
let chart = null

const loadTenants = async () => {
  try {
    tenants.value = await api.get('/user/tenants')
    if (tenants.value.length > 0) {
      selectedAppKey.value = tenants.value[0].app_key
      loadStats()
    }
  } catch (error) {
    console.error(error)
  }
}

const loadStats = async () => {
  if (!selectedAppKey.value) return

  try {
    stats.value = await api.get(`/user/stats/${selectedAppKey.value}`)
    renderChart()
  } catch (error) {
    console.error(error)
  }
}

const renderChart = () => {
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }

  const option = {
    title: { text: '30天Token消耗趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: stats.value.daily.map(d => d.date)
    },
    yAxis: { type: 'value' },
    series: [{
      data: stats.value.daily.map(d => d.count),
      type: 'line',
      smooth: true,
      itemStyle: { color: '#00796B' }
    }]
  }

  chart.setOption(option)
}

onMounted(loadTenants)
</script>

<style scoped>
.text-primary {
  color: #00796B;
}
</style>
