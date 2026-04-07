<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="close" />

        <!-- Modal Card -->
        <div class="relative z-10 bg-white rounded-3xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto font-sans">

          <!-- Header -->
          <div class="flex items-center justify-between px-8 pt-8 pb-6 border-b border-slate-100">
            <div>
              <h2 class="text-xl font-black tracking-tighter">订阅智能体</h2>
              <p class="text-slate-400 text-xs font-medium mt-0.5">选择计划与支付方式，立即开始使用</p>
            </div>
            <button
              @click="close"
              class="w-9 h-9 rounded-xl bg-slate-100 hover:bg-slate-200 flex items-center justify-center transition-colors">
              <svg class="w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="px-8 py-6 space-y-5">

            <!-- Agent Info -->
            <div v-if="agent" class="flex items-center space-x-4 bg-slate-50 rounded-2xl p-4">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center text-white font-black text-lg shrink-0">
                {{ agent.name.charAt(0) }}
              </div>
              <div class="min-w-0">
                <p class="font-black text-base tracking-tight truncate">{{ agent.name }}</p>
                <p class="text-cyan-500 text-[10px] font-bold uppercase tracking-widest truncate">{{ agent.title }}</p>
              </div>
              <div class="ml-auto text-right shrink-0">
                <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">单价</p>
                <p class="text-xl font-black font-mono">${{ agent.price }}<span class="text-[10px] text-slate-400 font-bold ml-0.5">/HR</span></p>
              </div>
            </div>

            <!-- Subscription Plan -->
            <div>
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-3">选择订阅计划</p>
              <div class="grid grid-cols-2 gap-3">
                <button
                  @click="selectedPlan = 'monthly'"
                  :class="[
                    'rounded-2xl p-4 border-2 text-left transition-all duration-200',
                    selectedPlan === 'monthly' ? 'border-cyan-500 bg-cyan-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">月付</p>
                  <div class="flex items-baseline">
                    <span class="text-xl font-black tracking-tighter">${{ monthlyPrice }}</span>
                    <span class="text-[10px] text-slate-400 font-bold ml-1">/月</span>
                  </div>
                  <p class="text-[9px] text-slate-400 mt-1 font-medium">按月计费，随时取消</p>
                </button>
                <button
                  @click="selectedPlan = 'annual'"
                  :class="[
                    'rounded-2xl p-4 border-2 text-left transition-all duration-200 relative overflow-hidden',
                    selectedPlan === 'annual' ? 'border-cyan-500 bg-cyan-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="absolute top-2.5 right-2.5 bg-cyan-500 text-white text-[9px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-wide">
                    省20%
                  </div>
                  <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">年付</p>
                  <div class="flex items-baseline">
                    <span class="text-xl font-black tracking-tighter">${{ annualPrice }}</span>
                    <span class="text-[10px] text-slate-400 font-bold ml-1">/年</span>
                  </div>
                  <p class="text-[9px] text-slate-400 mt-1 font-medium">一次性年付，享折扣优惠</p>
                </button>
              </div>
            </div>

            <!-- Payment Methods -->
            <div>
              <p class="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-3">选择支付方式</p>
              <div class="grid grid-cols-5 gap-2">
                <!-- Alipay -->
                <button
                  @click="selectedMethod = 'alipay'"
                  :class="[
                    'flex flex-col items-center py-3 px-1 rounded-2xl border-2 transition-all duration-200',
                    selectedMethod === 'alipay' ? 'border-[#1677FF] bg-blue-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="w-9 h-9 rounded-xl bg-[#1677FF] flex items-center justify-center mb-1.5">
                    <span class="text-white font-black text-sm">支</span>
                  </div>
                  <span class="text-[9px] font-bold text-slate-700 leading-tight text-center">支付宝</span>
                </button>

                <!-- WeChat Pay -->
                <button
                  @click="selectedMethod = 'wechat'"
                  :class="[
                    'flex flex-col items-center py-3 px-1 rounded-2xl border-2 transition-all duration-200',
                    selectedMethod === 'wechat' ? 'border-[#07C160] bg-green-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="w-9 h-9 rounded-xl bg-[#07C160] flex items-center justify-center mb-1.5">
                    <span class="text-white font-black text-sm">微</span>
                  </div>
                  <span class="text-[9px] font-bold text-slate-700 leading-tight text-center">微信支付</span>
                </button>

                <!-- Mastercard -->
                <button
                  @click="selectedMethod = 'mastercard'"
                  :class="[
                    'flex flex-col items-center py-3 px-1 rounded-2xl border-2 transition-all duration-200',
                    selectedMethod === 'mastercard' ? 'border-slate-400 bg-slate-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="w-9 h-9 flex items-center justify-center mb-1.5 relative">
                    <div class="absolute left-0.5 w-6 h-6 rounded-full bg-[#EB001B] opacity-90"></div>
                    <div class="absolute right-0.5 w-6 h-6 rounded-full bg-[#F79E1B] opacity-90 mix-blend-multiply"></div>
                  </div>
                  <span class="text-[9px] font-bold text-slate-700 leading-tight text-center">Master</span>
                </button>

                <!-- Visa -->
                <button
                  @click="selectedMethod = 'visa'"
                  :class="[
                    'flex flex-col items-center py-3 px-1 rounded-2xl border-2 transition-all duration-200',
                    selectedMethod === 'visa' ? 'border-[#1A1F71] bg-blue-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="w-9 h-9 rounded-xl bg-[#1A1F71] flex items-center justify-center mb-1.5">
                    <span class="text-[#F7B600] font-black text-xs italic tracking-tight">VISA</span>
                  </div>
                  <span class="text-[9px] font-bold text-slate-700 leading-tight text-center">Visa</span>
                </button>

                <!-- UnionPay -->
                <button
                  @click="selectedMethod = 'unionpay'"
                  :class="[
                    'flex flex-col items-center py-3 px-1 rounded-2xl border-2 transition-all duration-200',
                    selectedMethod === 'unionpay' ? 'border-red-500 bg-red-50' : 'border-slate-100 hover:border-slate-300'
                  ]">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-red-600 to-red-800 flex items-center justify-center mb-1.5">
                    <span class="text-white font-black text-xs">银联</span>
                  </div>
                  <span class="text-[9px] font-bold text-slate-700 leading-tight text-center">银联</span>
                </button>
              </div>
            </div>

            <!-- Order Summary -->
            <div class="bg-slate-50 rounded-2xl p-4 space-y-2.5">
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-500">智能体</span>
                <span class="font-bold">{{ agent?.name ?? '—' }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-500">计划</span>
                <span class="font-bold">{{ selectedPlan === 'monthly' ? '月付订阅' : '年付订阅' }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-slate-500">支付方式</span>
                <span class="font-bold">{{ methodLabel }}</span>
              </div>
              <div class="border-t border-slate-200 pt-2.5 flex justify-between items-center">
                <span class="text-sm text-slate-500">合计</span>
                <div class="flex items-baseline">
                  <span class="text-xs font-mono mr-0.5">$</span>
                  <span class="text-2xl font-black tracking-tighter">{{ totalPrice }}</span>
                </div>
              </div>
            </div>

            <!-- Pay Button -->
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
            <p class="text-center text-[10px] text-slate-400 font-medium -mt-2 pb-2">
              点击订阅即表示您同意我们的服务条款和隐私政策
            </p>
          </div>
        </div>

        <!-- Success overlay (inside modal) -->
        <Transition name="fade">
          <div v-if="showSuccess" class="absolute inset-0 z-20 flex items-center justify-center p-4">
            <div class="absolute inset-0 bg-black/30 backdrop-blur-sm" />
            <div class="relative bg-white rounded-3xl p-10 max-w-sm w-full text-center shadow-2xl">
              <div class="w-16 h-16 bg-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 class="text-2xl font-black tracking-tighter mb-2">订阅成功</h2>
              <p class="text-slate-400 text-sm mb-8">
                您已成功订阅 <strong>{{ agent?.name }}</strong>，智能体即将为您服务。
              </p>
              <button
                @click="close"
                class="w-full py-3.5 bg-slate-950 text-white text-sm font-bold rounded-2xl hover:bg-cyan-500 transition-all duration-300">
                完成
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  agent:   { type: Object,  default: null  },
})
const emit = defineEmits(['update:visible'])

const selectedPlan   = ref('monthly')
const selectedMethod = ref('')
const showSuccess    = ref(false)

// Reset state whenever the modal opens
watch(() => props.visible, (val) => {
  if (val) {
    selectedPlan.value   = 'monthly'
    selectedMethod.value = ''
    showSuccess.value    = false
  }
})

const monthlyPrice = computed(() => props.agent?.price ?? 0)
const annualPrice  = computed(() => Math.round((props.agent?.price ?? 0) * 12 * 0.8))
const totalPrice   = computed(() =>
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

function close() {
  showSuccess.value = false
  emit('update:visible', false)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95) translateY(8px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from,
.fade-leave-to      { opacity: 0; }
</style>
