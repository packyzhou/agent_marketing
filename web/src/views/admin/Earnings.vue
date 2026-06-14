<template>
  <div>
    <div class="admin-page-header">
      <div>
        <h2>收益</h2>
        <p>按 AppKey 查看收益明细、正负收益分布与总收益</p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">总收益</div>
        <div class="text-3xl font-black font-mono" :class="earningTextClass(overallTotal)">
          {{ formatCurrency(overallTotal) }}
        </div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">收益文件</div>
        <div class="text-3xl font-black font-mono text-slate-950">{{ earningsRows.length }}</div>
      </div>
      <div class="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm">
        <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">收益项</div>
        <div class="text-3xl font-black font-mono text-slate-950">{{ itemCount }}</div>
      </div>
    </div>

    <el-table :data="earningsRows" stripe v-loading="loading">
      <el-table-column label="AppKey" min-width="220">
        <template #default="{ row }">
          <div class="break-all text-xs leading-5">{{ row.app_key }}</div>
          <div v-if="row.tenant_name" class="text-[10px] text-slate-400 mt-1">{{ row.tenant_name }}</div>
        </template>
      </el-table-column>
      <el-table-column v-if="isAdmin" prop="username" label="所属用户" width="120" />
      <el-table-column label="总收益" width="140">
        <template #default="{ row }">
          <span class="font-mono font-black" :class="earningTextClass(row.total_earnings)">
            {{ formatCurrency(row.total_earnings) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="收益分布" min-width="460">
        <template #default="{ row }">
          <div v-if="row.earnings_items?.length" class="space-y-2 py-1">
            <div v-for="item in row.earnings_items" :key="`${row.app_key}-${item.label}`" class="grid grid-cols-[96px_1fr_1px_72px_1fr] items-center gap-3">
              <div class="truncate text-[11px] text-slate-400" :title="item.label">{{ item.label }}</div>
              <div class="h-1.5 bg-slate-100/70 rounded-full flex justify-end overflow-hidden">
                <div v-if="Number(item.amount) < 0" class="h-full bg-emerald-300 rounded-full" :style="{ width: barWidth(item.amount, row.maxAbsAmount) }"></div>
              </div>
              <div class="h-4 bg-slate-200"></div>
              <div class="text-center text-[10px] font-semibold font-mono text-slate-500">
                {{ formatCurrency(item.amount) }}
              </div>
              <div class="h-1.5 bg-slate-100/70 rounded-full overflow-hidden">
                <div v-if="Number(item.amount) >= 0" class="h-full bg-rose-300 rounded-full" :style="{ width: barWidth(item.amount, row.maxAbsAmount) }"></div>
              </div>
            </div>
          </div>
          <span v-else class="text-slate-300 text-xs">暂无收益数据</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api/request'

const isAdmin = computed(() => (localStorage.getItem('roleType') || '').toUpperCase() === 'ADMIN')
const loading = ref(false)
const earnings = ref([])

const earningsRows = computed(() => earnings.value.map(row => {
  const items = Array.isArray(row.earnings_items) ? row.earnings_items : []
  const maxAbsAmount = Math.max(...items.map(item => Math.abs(Number(item.amount) || 0)), 0)
  return { ...row, maxAbsAmount }
}))

const overallTotal = computed(() => earnings.value.reduce((sum, row) => sum + (Number(row.total_earnings) || 0), 0))
const itemCount = computed(() => earnings.value.reduce((sum, row) => sum + (row.earnings_items?.length || 0), 0))

const formatCurrency = (value) => {
  const n = Number(value) || 0
  const sign = n < 0 ? '-' : ''
  return `${sign}$${Math.abs(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const earningTextClass = (value) => {
  const n = Number(value) || 0
  if (n > 0) return 'text-rose-600'
  if (n < 0) return 'text-emerald-600'
  return 'text-slate-950'
}

const barWidth = (amount, maxAbsAmount) => {
  const max = Number(maxAbsAmount) || 0
  if (max <= 0) return '0%'
  return `${Math.max(4, Math.round(Math.abs(Number(amount) || 0) / max * 100))}%`
}

const loadEarnings = async () => {
  try {
    loading.value = true
    earnings.value = await api.get('/admin/earnings')
  } catch (error) {
    ElMessage.error('加载收益数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadEarnings)
</script>
