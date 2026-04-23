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
          <router-link to="/market" class="text-slate-950 transition-colors py-2">{{ $t('nav.marketplace') }}</router-link>
          <router-link to="/docs" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.docs') }}</router-link>
          <router-link to="/about" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.about') }}</router-link>
          <LangSwitcher />
        </div>
      </div>
    </nav>

    <!-- Spacer for fixed nav -->
    <div class="h-20"></div>

    <!-- Sticky Tab Bar -->
    <div class="sticky top-20 bg-white/95 backdrop-blur-xl z-40 border-b border-slate-100">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center">
        <div class="flex h-full">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="handleTabClick(tab)"
            :class="[
              'px-8 h-full text-[11px] font-bold uppercase tracking-widest transition-all border-b-2 -mb-px',
              activeTab === tab.id
                ? 'text-slate-950 border-slate-950'
                : 'text-slate-400 border-transparent hover:text-slate-700 hover:border-slate-300'
            ]">
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Agent Cards Grid -->
    <main class="max-w-7xl mx-auto px-6 py-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div
          v-for="agent in displayedAgents"
          :key="agent.id"
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
                <span class="text-xs font-bold font-mono">{{ agent.rating.toFixed(1) }}</span>
              </div>
              <div class="flex items-center space-x-1 text-slate-400">
                <TrendingUp class="w-3 h-3" />
                <span class="text-[10px] font-bold uppercase tracking-tighter">{{ formatHires(agent.hires) }} {{ $t('home.hires') }}</span>
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
              <span class="text-sm font-black font-mono">{{ agent.memory }} TB</span>
            </div>
            <div class="bg-slate-50/50 rounded-2xl p-4 border border-transparent group-hover:border-slate-100 transition-colors">
              <div class="flex items-center text-slate-400 mb-1">
                <Clock class="w-3 h-3 mr-1.5" />
                <span class="text-[9px] font-bold uppercase tracking-widest">{{ $t('home.duration') }}</span>
              </div>
              <span class="text-sm font-black font-mono">{{ agent.duration }}</span>
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
                @click="buyAgent(agent)"
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

      <!-- Infinite Scroll Sentinel -->
      <div ref="sentinel" class="h-12 flex items-center justify-center mt-4">
        <div v-if="loading" class="flex items-center space-x-1.5">
          <div class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style="animation-delay:0.15s"></div>
          <div class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style="animation-delay:0.3s"></div>
        </div>
        <p v-else-if="!hasMore" class="text-slate-300 text-[10px] font-bold uppercase tracking-widest">
          已加载全部 {{ allAgents.length }} 个智能体
        </p>
      </div>
    </main>
  </div>

  <PaymentModal v-model:visible="paymentVisible" :agent="paymentAgent" />
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Star, TrendingUp, Building2, Database, Clock, ChevronRight } from 'lucide-vue-next'
import LangSwitcher from '../components/LangSwitcher.vue'
import PaymentModal from '../components/PaymentModal.vue'

const router = useRouter()
const { t } = useI18n()

const paymentVisible = ref(false)
const paymentAgent   = ref(null)

// ── Tab Config ──────────────────────────────────────────────────────────────
const tabs = computed(() => [
  { id: 'home',      label: t('nav.home'),       to: '/home' },
  { id: 'rating',    label: '评分（从高到低）' },
  { id: 'purchases', label: '购买量（从多到少）' },
  { id: 'memory',    label: '记忆量（从大到小）' },
])
const activeTab = ref('rating')

function handleTabClick(tab) {
  if (tab.to) {
    router.push(tab.to)
    return
  }
  activeTab.value = tab.id
  currentPage.value = 1
}

// ── Agent Data Generator ────────────────────────────────────────────────────
const NAMES = [
  'Anna','Ben','Chloe','David','Emma','Frank','Grace','Henry','Iris','Jack',
  'Kate','Leo','Mia','Noah','Olivia','Paul','Quinn','Rachel','Sam','Tina',
  'Uma','Victor','Wendy','Xavier','Yuki','Zoe'
]
const TITLES = [
  'Senior Product Designer','Full-Stack Engineer','Data Strategist','ML Research Scientist',
  'DevOps Architect','UX Researcher','Blockchain Developer','AI Product Manager',
  'Security Engineer','Cloud Architect','Frontend Lead','Backend Architect',
  'NLP Specialist','Computer Vision Expert','Robotics Engineer'
]
const COMPANY_SETS = [
  ['Apple','Airbnb','Stripe'],['Google','DeepMind','Vercel'],['Palantir','Meta','Snowflake'],
  ['OpenAI','Anthropic','Cohere'],['Amazon','Netflix','Uber'],['Microsoft','GitHub','LinkedIn'],
  ['Nvidia','Intel','AMD'],['Salesforce','Slack','HubSpot'],['Spotify','Discord','Figma'],
  ['Tesla','SpaceX','Neuralink'],['ByteDance','Tencent','Alibaba'],['Baidu','Meituan','JD.com']
]
const DESCRIPTIONS = [
  '专注于高性能分布式架构与底层算法优化，其智能体具备解决复杂工程难题的逻辑思维路径。',
  '10年设计经验沉淀，精通多维视觉语言与用户行为逻辑，其智能体完整保留了审美判断力。',
  '擅长从海量非结构化数据中提取商业洞察，能够快速进行行业趋势预测与建模分析。',
  '深耕机器学习前沿领域，擅长大模型设计与大规模训练优化，推动AI工程化落地。',
  '构建云原生基础设施，保障系统高可用性与弹性扩展，主导多次大规模系统重构。',
  '通过用户研究与数据分析驱动产品决策，在体验优化领域拥有丰富的实战经验。',
  '区块链技术专家，精通智能合约开发与DeFi协议设计，参与多个头部项目建设。',
  '连接技术与商业战略，推动AI产品从研发到市场的全流程高效落地与商业化。',
  '网络安全领域资深专家，擅长渗透测试与零信任安全架构设计，守护系统边界。',
  '云架构专家，主导大型企业级系统的云端迁移与微服务重构，提升整体研发效能。',
]
const HIRE_COUNTS  = [150,280,420,630,950,1200,1600,2100,3200,5000]
const MEMORY_SIZES = [0.5,0.8,1.2,1.5,1.8,2.1,2.5,2.8,3.2,3.5,4.1,4.8]
const DURATIONS    = ['7 Days','10 Days','12 Days','15 Days','18 Days','21 Days','30 Days']
const PRICES       = [49,69,89,99,109,129,149,159,179,199]

function generateAgent(i) {
  const baseName = NAMES[i % NAMES.length]
  const suffix   = i >= NAMES.length ? ` ${String.fromCharCode(65 + Math.floor(i / NAMES.length) - 1)}` : ''
  return {
    id:          i + 1,
    name:        baseName + suffix,
    age:         24 + (i * 7 % 16),
    title:       TITLES[i % TITLES.length],
    avatar:      `https://i.pravatar.cc/200?img=${(i % 70) + 1}`,
    rating:      parseFloat((4.0 + (i * 13 % 10) / 10).toFixed(1)),
    hires:       HIRE_COUNTS[i % HIRE_COUNTS.length],
    companies:   COMPANY_SETS[i % COMPANY_SETS.length],
    description: DESCRIPTIONS[i % DESCRIPTIONS.length],
    memory:      MEMORY_SIZES[i % MEMORY_SIZES.length],
    duration:    DURATIONS[i % DURATIONS.length],
    price:       PRICES[i % PRICES.length],
  }
}

const allAgents = Array.from({ length: 100 }, (_, i) => generateAgent(i))

// ── Sorting ─────────────────────────────────────────────────────────────────
const sortedAgents = computed(() => {
  const list = [...allAgents]
  if (activeTab.value === 'rating')    return list.sort((a, b) => b.rating - a.rating || b.hires - a.hires)
  if (activeTab.value === 'purchases') return list.sort((a, b) => b.hires  - a.hires)
  if (activeTab.value === 'memory')    return list.sort((a, b) => b.memory - a.memory)
  return list
})

// ── Infinite Scroll ──────────────────────────────────────────────────────────
const PAGE_SIZE  = 9
const currentPage = ref(1)
const loading     = ref(false)

const displayedAgents = computed(() =>
  sortedAgents.value.slice(0, currentPage.value * PAGE_SIZE)
)

const hasMore = computed(() =>
  currentPage.value * PAGE_SIZE < sortedAgents.value.length
)

function loadNextPage() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  setTimeout(() => {
    currentPage.value++
    loading.value = false
  }, 400)
}

const sentinel = ref(null)
let observer   = null

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) loadNextPage()
    },
    { threshold: 0.1 }
  )
  if (sentinel.value) observer.observe(sentinel.value)
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatHires(n) {
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n)
}

function buyAgent(agent) {
  paymentAgent.value   = agent
  paymentVisible.value = true
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
