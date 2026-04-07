<template>
  <div class="min-h-screen bg-slate-50 font-sans text-slate-900 antialiased">
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

    <!-- Payment Content -->
    <main class="pt-20 pb-16">
      <div class="max-w-2xl mx-auto px-6 py-12">

        <!-- Header -->
        <div class="text-center mb-10">
          <h1 class="text-3xl font-black tracking-tighter mb-2">订阅智能体</h1>
          <p class="text-slate-400 text-sm font-medium">选择计划与支付方式，立即开始使用</p>
        </div>

        <!-- Agent Info (if from card) -->
        <div v-if="agentName" class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm mb-6 flex items-center space-x-4">
          <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black text-xl">
            {{ agentName.charAt(0) }}
          </div>
          <div>
            <p class="font-black text-lg tracking-tight">{{ agentName }}</p>
            <p class="text-cyan-500 text-xs font-bold uppercase tracking-widest">{{ agentTitle }}</p>
          </div>
          <div class="ml-auto text-right">
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">单价</p>
            <p class="text-2xl font-black font-mono">${{ agentPrice }}<span class="text-xs text-slate-400 font-bold ml-1">/HR</span></p>
          </div>
        </div>

        <!-- Subscription Plan -->
        <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm mb-6">
          <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">选择订阅计划</p>
          <div class="grid grid-cols-2 gap-4">
            <button
              @click="selectedPlan = 'monthly'"
              :class="[
                'rounded-2xl p-5 border-2 text-left transition-all duration-300',
                selectedPlan === 'monthly'
                  ? 'border-cyan-500 bg-cyan-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">月付</p>
              <div class="flex items-baseline">
                <span class="text-2xl font-black tracking-tighter">${{ monthlyPrice }}</span>
                <span class="text-xs text-slate-400 font-bold ml-1">/月</span>
              </div>
              <p class="text-[10px] text-slate-400 mt-1.5 font-medium">按月计费，随时取消</p>
            </button>
            <button
              @click="selectedPlan = 'annual'"
              :class="[
                'rounded-2xl p-5 border-2 text-left transition-all duration-300 relative overflow-hidden',
                selectedPlan === 'annual'
                  ? 'border-cyan-500 bg-cyan-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="absolute top-3 right-3 bg-cyan-500 text-white text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider">
                省20%
              </div>
              <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">年付</p>
              <div class="flex items-baseline">
                <span class="text-2xl font-black tracking-tighter">${{ annualPrice }}</span>
                <span class="text-xs text-slate-400 font-bold ml-1">/年</span>
              </div>
              <p class="text-[10px] text-slate-400 mt-1.5 font-medium">一次性年付，享折扣优惠</p>
            </button>
          </div>
        </div>

        <!-- Payment Methods -->
        <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm mb-6">
          <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">选择支付方式</p>
          <div class="grid grid-cols-5 gap-3">
            <!-- Alipay -->
            <button
              @click="selectedMethod = 'alipay'"
              :class="[
                'flex flex-col items-center py-4 px-2 rounded-2xl border-2 transition-all duration-300',
                selectedMethod === 'alipay'
                  ? 'border-[#1677FF] bg-blue-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="w-10 h-10 rounded-xl bg-[#1677FF] flex items-center justify-center mb-2">
                <svg viewBox="0 0 24 24" class="w-6 h-6 fill-white">
                  <path d="M21.422 15.358c-3.83-1.153-6.055-1.9-7.718-2.516a9.206 9.206 0 0 0 1.47-4.399h-3.565V7.035h4.005V5.976H11.61V4h-2.44v1.976H5.06v1.059h4.111v1.408H5.583v1.059h7.23a7.273 7.273 0 0 1-.913 2.954C9.525 11.25 6.697 9.962 3 9.52v2.44c3.028.39 5.547 1.167 7.712 2.11a19.918 19.918 0 0 1-7.712 5.93v2.44c3.15-1.007 5.9-2.87 8.054-5.35 1.756 1.094 2.99 2.13 3.773 2.86L16.7 18c-.784-.783-2.046-1.82-3.873-2.947 1.46-2.3 2.17-5.031 2.17-7.76H5.06V6.235H11.17V5.177H5.06V4H2.62v1.177H.06v1.058h2.56v1.059H.06v1.059h2.56v1.408H0v1.059h2.62C2.8 15.03 4.47 19.39 5.583 22h2.44c-1.3-2.9-2.44-6.063-2.56-10.17 2.9.52 5.03 1.41 6.75 2.43a22.23 22.23 0 0 1-1.38 1.82l1.9 1.5c.52-.67 1.01-1.37 1.46-2.1 1.54.98 2.65 1.96 3.25 2.56l1.9-1.9c-.67-.67-1.82-1.68-3.38-2.72.8-1.71 1.24-3.55 1.35-5.42h1.87V6.24h-1.87V5.18h1.87V4.12h-1.87V4h-2.44v.12h-4.11V5.18h4.11v1.06H9.17v1.06h4.11v1.06H5.06v1.06h8.31c-.09 1.46-.41 2.86-.96 4.16-1.8-.7-4.04-1.45-7.28-1.97V12.5c2.9.45 5.03 1.15 6.75 2.01A17.47 17.47 0 0 1 3 20.17v2.44a19.88 19.88 0 0 0 10.17-7.53c1.7 1.09 2.89 2.11 3.62 2.81l1.9-1.9c-.74-.74-1.97-1.79-3.72-2.92a16.64 16.64 0 0 0 1.16-2.59c1.64.6 3.89 1.37 7.28 2.44v-2.44z"/>
                </svg>
              </div>
              <span class="text-[10px] font-bold text-slate-700">支付宝</span>
            </button>

            <!-- WeChat Pay -->
            <button
              @click="selectedMethod = 'wechat'"
              :class="[
                'flex flex-col items-center py-4 px-2 rounded-2xl border-2 transition-all duration-300',
                selectedMethod === 'wechat'
                  ? 'border-[#07C160] bg-green-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="w-10 h-10 rounded-xl bg-[#07C160] flex items-center justify-center mb-2">
                <svg viewBox="0 0 24 24" class="w-6 h-6 fill-white">
                  <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C22.962 18.006 24 16.4 24 14.506c0-3.33-2.955-5.98-7.062-5.648zm-3.11 3.13a.98.98 0 0 1 .972.979.98.98 0 0 1-.972.979.98.98 0 0 1-.972-.98.98.98 0 0 1 .972-.978zm6.188 0a.98.98 0 0 1 .972.979.98.98 0 0 1-.972.979.98.98 0 0 1-.972-.98.98.98 0 0 1 .972-.978z"/>
                </svg>
              </div>
              <span class="text-[10px] font-bold text-slate-700">微信支付</span>
            </button>

            <!-- Mastercard -->
            <button
              @click="selectedMethod = 'mastercard'"
              :class="[
                'flex flex-col items-center py-4 px-2 rounded-2xl border-2 transition-all duration-300',
                selectedMethod === 'mastercard'
                  ? 'border-slate-400 bg-slate-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="w-10 h-10 flex items-center justify-center mb-2 relative">
                <div class="absolute left-0.5 w-7 h-7 rounded-full bg-[#EB001B] opacity-90"></div>
                <div class="absolute right-0.5 w-7 h-7 rounded-full bg-[#F79E1B] opacity-90 mix-blend-multiply"></div>
              </div>
              <span class="text-[10px] font-bold text-slate-700">Mastercard</span>
            </button>

            <!-- Visa -->
            <button
              @click="selectedMethod = 'visa'"
              :class="[
                'flex flex-col items-center py-4 px-2 rounded-2xl border-2 transition-all duration-300',
                selectedMethod === 'visa'
                  ? 'border-[#1A1F71] bg-blue-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="w-10 h-10 rounded-xl bg-[#1A1F71] flex items-center justify-center mb-2">
                <span class="text-[#F7B600] font-black text-sm italic tracking-tight">VISA</span>
              </div>
              <span class="text-[10px] font-bold text-slate-700">Visa</span>
            </button>

            <!-- UnionPay -->
            <button
              @click="selectedMethod = 'unionpay'"
              :class="[
                'flex flex-col items-center py-4 px-2 rounded-2xl border-2 transition-all duration-300',
                selectedMethod === 'unionpay'
                  ? 'border-red-500 bg-red-50'
                  : 'border-slate-100 hover:border-slate-300'
              ]">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center mb-2">
                <span class="text-white font-black text-xs tracking-wide">银联</span>
              </div>
              <span class="text-[10px] font-bold text-slate-700">UnionPay</span>
            </button>
          </div>
        </div>

        <!-- Order Summary & Pay -->
        <div class="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm">
          <p class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">订单详情</p>
          <div class="space-y-3 mb-6">
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-500">智能体</span>
              <span class="font-bold">{{ agentName || '— —' }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-500">计划</span>
              <span class="font-bold">{{ selectedPlan === 'monthly' ? '月付订阅' : '年付订阅' }}</span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-500">支付方式</span>
              <span class="font-bold">{{ methodLabel }}</span>
            </div>
            <div class="border-t border-slate-100 pt-3 flex justify-between items-center">
              <span class="text-sm text-slate-500">合计</span>
              <div class="flex items-baseline">
                <span class="text-sm font-mono mr-0.5">$</span>
                <span class="text-2xl font-black tracking-tighter">{{ totalPrice }}</span>
              </div>
            </div>
          </div>
          <button
            @click="handlePay"
            :disabled="!selectedMethod"
            :class="[
              'w-full py-4 rounded-2xl text-sm font-bold transition-all duration-300',
              selectedMethod
                ? 'bg-slate-950 text-white hover:bg-cyan-500 hover:shadow-lg hover:shadow-cyan-200'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            ]">
            {{ selectedMethod ? '立即订阅' : '请先选择支付方式' }}
          </button>
          <p class="text-center text-[10px] text-slate-400 mt-3 font-medium">
            点击订阅即表示您同意我们的服务条款和隐私政策
          </p>
        </div>

      </div>
    </main>

    <!-- Success Dialog -->
    <div v-if="showSuccess" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center" @click.self="showSuccess = false">
      <div class="bg-white rounded-3xl p-10 max-w-sm w-full mx-6 text-center shadow-2xl">
        <div class="w-16 h-16 bg-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 class="text-2xl font-black tracking-tighter mb-2">订阅成功</h2>
        <p class="text-slate-400 text-sm mb-8">您已成功订阅 <strong>{{ agentName }}</strong>，智能体即将为您服务。</p>
        <button
          @click="$router.push('/market')"
          class="w-full py-3.5 bg-slate-950 text-white text-sm font-bold rounded-2xl hover:bg-cyan-500 transition-all duration-300">
          返回市场
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import LangSwitcher from '../components/LangSwitcher.vue'

const route = useRoute()

const agentName  = ref(route.query.name  || '')
const agentTitle = ref(route.query.title || '')
const agentPrice = ref(Number(route.query.price) || 99)

const selectedPlan   = ref('monthly')
const selectedMethod = ref('')
const showSuccess    = ref(false)

const monthlyPrice = computed(() => agentPrice.value)
const annualPrice  = computed(() => Math.round(agentPrice.value * 12 * 0.8))

const totalPrice = computed(() =>
  selectedPlan.value === 'monthly' ? monthlyPrice.value : annualPrice.value
)

const METHOD_LABELS = {
  alipay:     '支付宝',
  wechat:     '微信支付',
  mastercard: 'Mastercard',
  visa:       'Visa',
  unionpay:   '银联 UnionPay',
}

const methodLabel = computed(() =>
  selectedMethod.value ? METHOD_LABELS[selectedMethod.value] : '—'
)

function handlePay() {
  if (!selectedMethod.value) return
  showSuccess.value = true
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
