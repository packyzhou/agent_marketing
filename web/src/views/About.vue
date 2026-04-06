<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 antialiased">
    <!-- Navigation -->
    <nav class="fixed top-0 w-full bg-white/80 backdrop-blur-xl border-b border-slate-100 z-50">
      <div class="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
        <router-link to="/home" class="flex items-center space-x-3 group cursor-pointer">
          <div class="h-16 w-24 flex items-center justify-center transition-transform duration-500 group-hover:scale-105">
            <img src="/logo_main_page.png" alt="Logo" class="w-full h-full object-contain mix-blend-multiply" />
          </div>
          <div class="flex flex-col leading-tight">
            <span class="font-black tracking-tighter text-xl uppercase">Agent Market</span>
            <span class="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">{{ $t('home.subtitle') }}</span>
          </div>
        </router-link>
        <div class="hidden md:flex items-center space-x-10 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          <router-link to="/home" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.home') }}</router-link>
          <router-link to="/docs" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.docs') }}</router-link>
          <router-link to="/about" class="text-slate-950 transition-colors py-2">{{ $t('nav.about') }}</router-link>
          <LangSwitcher />
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-36 pb-10 px-6 text-center">
      <h1 class="text-4xl md:text-5xl font-black tracking-tighter mb-4">
        {{ $t('about.title') }}
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">{{ $t('about.titleHighlight') }}</span>
      </h1>
      <p class="text-base text-slate-400 font-medium">{{ $t('about.subtitle') }}</p>
    </header>

    <!-- Two columns -->
    <main class="max-w-5xl mx-auto px-6 pb-32">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <!-- Left: Cooperation Form -->
        <div class="bg-white border border-slate-100 rounded-[2rem] p-8">
          <h2 class="text-lg font-black tracking-tight mb-1">{{ $t('about.formTitle') }}</h2>
          <p class="text-sm text-slate-400 mb-6">{{ $t('about.formDesc') }}</p>
          <form @submit.prevent="handleSubmit" class="space-y-5">
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('about.company') }}</label>
              <input v-model="form.company" type="text" :placeholder="$t('about.companyPh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('about.contact') }}</label>
              <input v-model="form.contact" type="text" :placeholder="$t('about.contactPh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('about.intention') }}</label>
              <select v-model="form.intention"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium text-slate-600 focus:outline-none focus:border-slate-300 focus:bg-white transition-all">
                <option value="" disabled>{{ $t('about.intentionPh') }}</option>
                <option value="tech">{{ $t('about.intentionOpts.tech') }}</option>
                <option value="business">{{ $t('about.intentionOpts.business') }}</option>
                <option value="invest">{{ $t('about.intentionOpts.invest') }}</option>
                <option value="other">{{ $t('about.intentionOpts.other') }}</option>
              </select>
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('about.purpose') }}</label>
              <textarea v-model="form.purpose" rows="4" :placeholder="$t('about.purposePh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all resize-none"></textarea>
            </div>
            <button type="submit"
              class="w-full py-3.5 bg-slate-950 text-white text-sm font-bold rounded-xl hover:bg-cyan-500 transition-all duration-300 shadow-2xl shadow-slate-200">
              {{ $t('about.submit') }}
            </button>
          </form>
        </div>

        <!-- Right: Vision + Contact -->
        <div class="space-y-6">
          <!-- Vision -->
          <div class="bg-gradient-to-br from-slate-950 to-slate-800 rounded-[2rem] p-8 text-white">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">{{ $t('about.visionTitle') }}</div>
            <blockquote class="text-xl md:text-2xl font-black tracking-tight leading-snug mb-6">
              {{ $t('about.visionQuote') }}
            </blockquote>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ $t('about.visionDesc') }}
            </p>
          </div>

          <!-- Initiator -->
          <div class="bg-white border border-slate-100 rounded-[2rem] p-8">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">{{ $t('about.initiator') }}</div>
            <div class="flex items-center space-x-3 mb-5">
              <div class="w-12 h-12 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center text-white text-lg font-black">J</div>
              <div>
                <p class="text-lg font-black tracking-tight">Mr. Joe</p>
                <p class="text-[11px] font-bold text-cyan-500 uppercase tracking-[0.15em]">{{ $t('about.founder') }}</p>
              </div>
            </div>
            <div class="space-y-2.5">
              <div class="flex items-center space-x-3 bg-slate-50 px-4 py-3 rounded-xl border border-slate-100">
                <Mail class="w-4 h-4 text-slate-400" />
                <span class="text-sm font-medium text-slate-600">packyzhou1990@gmail.com</span>
              </div>
              <div class="flex items-center space-x-3 bg-slate-50 px-4 py-3 rounded-xl border border-slate-100">
                <MessageCircle class="w-4 h-4 text-slate-400" />
                <span class="text-sm font-medium text-slate-600">WeChat: packyzhou</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-slate-950 py-16 px-6">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start space-y-10 md:space-y-0">
        <div class="max-w-sm">
          <div class="flex items-center space-x-3 mb-4">
            <div class="bg-white px-2 py-1.5 rounded-lg flex items-center justify-center">
              <img src="/logo.png" alt="Logo" class="h-5 w-auto object-contain" />
            </div>
            <span class="font-black text-white tracking-tight uppercase">Agent Market</span>
          </div>
          <p class="text-slate-500 text-sm leading-relaxed">{{ $t('footer.desc') }}</p>
        </div>
        <div class="grid grid-cols-2 gap-16">
          <div class="flex flex-col space-y-3">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-1">{{ $t('footer.navigate') }}</span>
            <router-link to="/home" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.home') }}</router-link>
            <router-link to="/docs" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.docs') }}</router-link>
            <router-link to="/about" class="text-slate-500 text-sm hover:text-white transition-colors">{{ $t('nav.about') }}</router-link>
          </div>
          <div class="flex flex-col space-y-3">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-1">{{ $t('footer.connect') }}</span>
            <a href="https://github.com/packyzhou/agent_marketing" class="text-slate-500 text-sm hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </div>
      <div class="max-w-6xl mx-auto mt-16 pt-8 border-t border-slate-900 flex justify-between items-center text-[10px] font-bold text-slate-700 uppercase tracking-widest">
        <span>{{ $t('footer.copyright') }}</span>
        <span>{{ $t('footer.slogan') }}</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Mail, MessageCircle } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import LangSwitcher from '../components/LangSwitcher.vue'

const { t } = useI18n()

const form = ref({
  company: '',
  contact: '',
  intention: '',
  purpose: ''
})

const handleSubmit = () => {
  if (!form.value.company || !form.value.contact || !form.value.intention || !form.value.purpose) {
    ElMessage.warning(t('about.submitFail'))
    return
  }
  ElMessage.success(t('about.submitSuccess'))
  form.value = { company: '', contact: '', intention: '', purpose: '' }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
