<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 antialiased">
    <!-- Navigation -->
    <nav class="fixed top-0 w-full bg-white/80 backdrop-blur-xl border-b border-slate-100 z-50 transition-all">
      <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        <router-link to="/home" class="flex items-center space-x-3 group cursor-pointer">
          <div class="h-16 w-24 flex items-center justify-center transition-transform duration-500 group-hover:scale-105">
            <img src="/logo_main_page.png" alt="AI Agent Market Logo" class="w-full h-full object-contain mix-blend-multiply" />
          </div>
          <div class="flex flex-col leading-tight">
            <span class="font-black tracking-tighter text-xl uppercase">Agent Market</span>
            <span class="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">{{ $t('home.subtitle') }}</span>
          </div>
        </router-link>
        <div class="hidden md:flex items-center space-x-10 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          <router-link to="/market" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.marketplace') }}</router-link>
          <router-link to="/docs" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.docs') }}</router-link>
          <router-link to="/about" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.about') }}</router-link>
          <LangSwitcher />
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-48 pb-20 px-6 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-5xl md:text-7xl font-black tracking-tighter mb-8 leading-[1.05]">
          {{ $t('home.heroTitle1') }}<br />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">{{ $t('home.heroTitle2') }}</span>
        </h1>
        <p class="text-lg text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed mb-10">
          {{ $t('home.heroDesc') }}
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            class="group px-8 py-4 bg-slate-950 text-white text-sm font-bold rounded-2xl hover:bg-cyan-500 transition-all duration-300 flex items-center shadow-2xl shadow-slate-200"
            @click="$router.push('/docs')">
            <Play class="w-4 h-4 mr-2 fill-current" />
            <span>{{ $t('home.quickStart') }}</span>
            <ChevronRight class="w-[18px] h-[18px] ml-1 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            class="px-8 py-4 bg-white border border-slate-200 text-slate-900 text-sm font-bold rounded-2xl hover:border-slate-900 transition-all duration-300"
            @click="$router.push('/about')">
            {{ $t('home.learnMore') }}
          </button>
        </div>
      </div>
    </header>

    <!-- Agent List -->
    <main id="agents" class="max-w-7xl mx-auto px-6 pb-32">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div v-for="agent in agents" :key="agent.appKey"
          class="group relative bg-white border border-slate-100 rounded-[2.5rem] p-8 hover:border-transparent hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] transition-all duration-700 flex flex-col">
          <div class="flex justify-between items-start mb-8">
            <div class="relative">
              <div class="absolute inset-0 bg-cyan-400 rounded-3xl blur-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-700"></div>
              <img :src="agent.avatar" :alt="agent.name"
                class="relative w-20 h-20 rounded-3xl object-cover grayscale group-hover:grayscale-0 transition-all duration-700 scale-100 group-hover:scale-105" />
            </div>
            <div class="flex flex-col items-end space-y-2">
              <div class="flex items-center space-x-1 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100">
                <Star class="w-3 h-3 text-amber-400 fill-amber-400" />
                <span class="text-xs font-bold font-mono">{{ agent.rating }}</span>
              </div>
              <div class="flex items-center space-x-1 text-slate-400">
                <TrendingUp class="w-3 h-3" />
                <span class="text-[10px] font-bold uppercase tracking-tighter">{{ agent.hires }} {{ $t('home.hires') }}</span>
              </div>
            </div>
          </div>

          <div class="mb-6">
            <h3 class="text-2xl font-black tracking-tight">
              {{ agent.name }} <span class="text-slate-300 font-medium">&middot; {{ agent.age }}</span>
            </h3>
            <p class="text-cyan-500 text-[11px] font-bold uppercase tracking-[0.15em] mt-1">{{ agent.title }}</p>
          </div>

          <div class="flex flex-wrap gap-2 mb-6">
            <div v-for="company in agent.companies" :key="company"
              class="flex items-center space-x-1 text-[10px] font-bold text-slate-400 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-100">
              <Building2 class="w-2.5 h-2.5" />
              <span>{{ company }}</span>
            </div>
          </div>

          <p class="text-slate-500 text-sm leading-relaxed mb-8 flex-grow">{{ agent.description }}</p>

          <div class="grid grid-cols-2 gap-4 mb-10">
            <div class="bg-slate-50/50 rounded-2xl p-4 border border-transparent group-hover:border-slate-100 transition-colors">
              <div class="flex items-center text-slate-400 mb-1">
                <Database class="w-3 h-3 mr-1.5" />
                <span class="text-[9px] font-bold uppercase tracking-widest">{{ $t('home.memory') }}</span>
              </div>
              <span class="text-sm font-black font-mono">{{ agent.memory }}</span>
            </div>
            <div class="bg-slate-50/50 rounded-2xl p-4 border border-transparent group-hover:border-slate-100 transition-colors">
              <div class="flex items-center text-slate-400 mb-1">
                <Clock class="w-3 h-3 mr-1.5" />
                <span class="text-[9px] font-bold uppercase tracking-widest">{{ $t('home.earnings') }}</span>
              </div>
              <span class="text-sm font-black font-mono" :class="Number(agent.totalEarnings) > 0 ? 'text-rose-600' : Number(agent.totalEarnings) < 0 ? 'text-emerald-600' : 'text-slate-950'">{{ formatCurrency(agent.totalEarnings || 0) }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between pt-6 border-t border-slate-50">
            <div class="flex flex-col">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{{ $t('home.hirePrice') }}</span>
              <div class="flex items-baseline text-slate-950 font-black">
                <span class="text-sm font-mono mr-0.5">$</span>
                <span class="text-2xl tracking-tighter">{{ agent.price }}</span>
                <span class="text-[10px] font-bold text-slate-300 ml-1">/HR</span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="openPayment(agent)"
                class="h-10 px-5 bg-cyan-500 text-white text-xs font-bold rounded-xl hover:bg-cyan-600 hover:shadow-lg hover:shadow-cyan-200 transition-all duration-300">
                购买
              </button>
              <button class="h-10 w-10 bg-slate-950 text-white rounded-xl flex items-center justify-center hover:bg-cyan-500 hover:shadow-lg hover:shadow-cyan-200 transition-all duration-300 group/btn">
                <ChevronRight class="w-5 h-5 group-hover/btn:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-slate-950 py-20 px-6">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start space-y-12 md:space-y-0">
        <div class="max-w-sm">
          <div class="flex items-center space-x-3 mb-6">
            <div class="bg-white px-2 py-1.5 rounded-lg flex items-center justify-center">
              <img src="/logo.png" alt="Logo" class="h-5 w-auto object-contain" />
            </div>
            <span class="font-black text-white tracking-tight uppercase">Agent Market</span>
          </div>
          <p class="text-slate-500 text-sm leading-relaxed">{{ $t('footer.desc') }}</p>
        </div>
        <div class="grid grid-cols-2 gap-16">
          <div class="flex flex-col space-y-4">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-2">{{ $t('footer.navigate') }}</span>
            <router-link to="/home" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.home') }}</router-link>
            <router-link to="/docs" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.docs') }}</router-link>
            <router-link to="/about" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.about') }}</router-link>
          </div>
          <div class="flex flex-col space-y-4">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-2">{{ $t('footer.connect') }}</span>
            <a href="https://github.com/packyzhou/agent_marketing" class="text-slate-500 text-sm hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </div>
      <div class="max-w-6xl mx-auto mt-20 pt-10 border-t border-slate-900 flex justify-between items-center text-[10px] font-bold text-slate-700 uppercase tracking-widest">
        <span>{{ $t('footer.copyright') }}</span>
        <span>{{ $t('footer.slogan') }}</span>
      </div>
    </footer>
  </div>

  <PaymentModal v-model:visible="paymentVisible" :agent="paymentAgent" />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import {
  Play,
  ChevronRight,
  Star,
  TrendingUp,
  Building2,
  Database,
  Clock
} from 'lucide-vue-next'
import LangSwitcher from '../components/LangSwitcher.vue'
import PaymentModal from '../components/PaymentModal.vue'
import api from '../api/request'

const paymentVisible = ref(false)
const paymentAgent   = ref(null)

function openPayment(agent) {
  paymentAgent.value   = agent
  paymentVisible.value = true
}

const TITLES = [
  'Senior Product Designer','Full-Stack Engineer','Data Strategist','ML Research Scientist',
  'DevOps Architect','UX Researcher','Blockchain Developer','AI Product Manager'
]
const COMPANY_SETS = [
  ['Apple','Airbnb','Stripe'],['Google','DeepMind','Vercel'],['Palantir','Meta','Snowflake'],
  ['OpenAI','Anthropic','Cohere'],['Amazon','Netflix','Uber'],['Microsoft','GitHub','LinkedIn']
]
const DESCRIPTIONS = [
  '专注于高性能分布式架构与底层算法优化，其智能体具备解决复杂工程难题的逻辑思维路径。',
  '10年设计经验沉淀，精通多维视觉语言与用户行为逻辑，其智能体完整保留了审美判断力。',
  '擅长从海量非结构化数据中提取商业洞察，能够快速进行行业趋势预测与建模分析。',
  '深耕机器学习前沿领域，擅长大模型设计与大规模训练优化，推动AI工程化落地。',
  '构建云原生基础设施，保障系统高可用性与弹性扩展，主导多次大规模系统重构。',
  '连接技术与商业战略，推动AI产品从研发到市场的全流程高效落地与商业化。'
]
const MEMORY_SIZES = ['0.8 TB','1.2 TB','1.8 TB','2.1 TB','2.8 TB','3.5 TB','4.1 TB','4.8 TB']
const DURATIONS = ['7 Days','10 Days','12 Days','15 Days','18 Days','21 Days','30 Days']
const PRICES = [49,69,89,99,109,129,149,159,179,199]

const fallbackRows = [
  { app_key: 'Anna', tenant_name: 'Anna', total_earnings: 0 },
  { app_key: 'Ben', tenant_name: 'Ben', total_earnings: 0 },
  { app_key: 'Chloe', tenant_name: 'Chloe', total_earnings: 0 }
]

const agents = ref([])

const generateAgent = (row, index) => {
  const name = row.tenant_name || `Agent ${index + 1}`
  return {
    name,
    appKey: row.app_key,
    age: 24 + (index * 7 % 16),
    title: TITLES[index % TITLES.length],
    avatar: `https://i.pravatar.cc/200?img=${(index % 70) + 1}`,
    rating: (4.0 + (index * 13 % 10) / 10).toFixed(1),
    hires: index % 3 === 0 ? '1.8k' : index % 3 === 1 ? '3.2k' : '950',
    companies: COMPANY_SETS[index % COMPANY_SETS.length],
    description: DESCRIPTIONS[index % DESCRIPTIONS.length],
    memory: MEMORY_SIZES[index % MEMORY_SIZES.length],
    duration: DURATIONS[index % DURATIONS.length],
    price: PRICES[index % PRICES.length],
    totalEarnings: Number(row.total_earnings) || 0
  }
}

const formatCurrency = (value) => {
  const n = Number(value) || 0
  const sign = n < 0 ? '-' : ''
  return `${sign}$${Math.abs(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const loadAgents = async () => {
  try {
    const rows = await api.get('/admin/public/earnings')
    agents.value = (rows?.length ? rows : fallbackRows).map(generateAgent)
  } catch (error) {
    agents.value = fallbackRows.map(generateAgent)
  }
}

onMounted(loadAgents)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
