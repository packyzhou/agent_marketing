<template>
  <div class="min-h-screen bg-white font-sans text-slate-900 antialiased flex flex-col">
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
          <router-link to="/about" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.about') }}</router-link>
          <LangSwitcher />
        </div>
      </div>
    </nav>

    <!-- Login Form -->
    <div class="flex-1 flex items-center justify-center pt-20 px-6">
      <div class="w-full max-w-md">
        <div class="text-center mb-10">
          <h1 class="text-3xl font-black tracking-tighter mb-3">
            {{ $t('login.welcome') }}
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">{{ $t('login.back') }}</span>
          </h1>
          <p class="text-sm text-slate-400 font-medium">{{ $t('login.subtitle') }}</p>
        </div>

        <div class="bg-white border border-slate-100 rounded-[2rem] p-8 shadow-[0_40px_80px_-20px_rgba(0,0,0,0.06)]">
          <!-- Tabs -->
          <div class="flex mb-8 bg-slate-50 rounded-xl p-1">
            <button
              class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
              :class="activeTab === 'login' ? 'bg-slate-950 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'"
              @click="activeTab = 'login'">
              {{ $t('login.signIn') }}
            </button>
            <button
              class="flex-1 py-2.5 text-sm font-bold rounded-lg transition-all"
              :class="activeTab === 'register' ? 'bg-slate-950 text-white shadow-lg' : 'text-slate-400 hover:text-slate-600'"
              @click="activeTab = 'register'">
              {{ $t('login.register') }}
            </button>
          </div>

          <!-- Login -->
          <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.username') }}</label>
              <input v-model="loginForm.username" type="text" :placeholder="$t('login.usernamePh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.password') }}</label>
              <input v-model="loginForm.password" type="password" :placeholder="$t('login.passwordPh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <button type="submit"
              class="w-full py-3.5 bg-slate-950 text-white text-sm font-bold rounded-xl hover:bg-cyan-500 transition-all duration-300 shadow-2xl shadow-slate-200 mt-2">
              {{ $t('login.signInBtn') }}
            </button>
          </form>

          <!-- Register -->
          <form v-else @submit.prevent="handleRegister" class="space-y-4">
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.username') }} *</label>
              <input v-model="registerForm.username" type="text" :placeholder="$t('login.usernamePh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.phone') }} *</label>
              <input v-model="registerForm.phone" type="text" :placeholder="$t('login.phonePh')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.realName') }}</label>
              <input v-model="registerForm.real_name" type="text" :placeholder="$t('login.optional')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.password') }} *</label>
              <input v-model="registerForm.password" type="password" :placeholder="$t('login.passwordRule')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <div>
              <label class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 block">{{ $t('login.referrerPhone') }}</label>
              <input v-model="registerForm.referrer_phone" type="text" :placeholder="$t('login.optional')"
                class="w-full px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-sm font-medium placeholder-slate-300 focus:outline-none focus:border-slate-300 focus:bg-white transition-all" />
            </div>
            <button type="submit"
              class="w-full py-3.5 bg-slate-950 text-white text-sm font-bold rounded-xl hover:bg-cyan-500 transition-all duration-300 shadow-2xl shadow-slate-200 mt-2">
              {{ $t('login.registerBtn') }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '../api/request'
import LangSwitcher from '../components/LangSwitcher.vue'

const router = useRouter()
const { t } = useI18n()
const activeTab = ref('login')
const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', phone: '', real_name: '', password: '', referrer_phone: '' })

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (typeof first === 'string') return first
    if (first?.msg) return first.msg
  }
  return fallback
}

const handleLogin = async () => {
  try {
    const res = await api.post('/auth/login', loginForm.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('role', (res.role || 'USER').toUpperCase())
    localStorage.setItem('roleName', res.role_name || res.role || '普通用户')
    localStorage.setItem('roleType', (res.role_type || 'USER').toUpperCase())
    localStorage.setItem('username', res.username || loginForm.value.username)
    ElMessage.success(t('login.loginSuccess'))
    if ((res.role_type || '').toUpperCase() === 'ADMIN') {
      router.push('/admin/users')
      return
    }
    router.push('/admin/groups')
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('login.loginFail')))
  }
}

const handleRegister = async () => {
  const username = registerForm.value.username.trim()
  const phone = registerForm.value.phone.trim()
  const password = registerForm.value.password.trim()
  const realName = registerForm.value.real_name.trim()
  const referrerPhone = registerForm.value.referrer_phone.trim()

  if (!username || !phone || !password) {
    ElMessage.error(t('login.required'))
    return
  }
  if (password.length <= 6) {
    ElMessage.error(t('login.passwordTooShort'))
    return
  }

  try {
    await api.post('/auth/register', {
      username, phone, password,
      real_name: realName || null,
      referrer_phone: referrerPhone || null
    })
    ElMessage.success(t('login.registerSuccess'))
    registerForm.value = { username: '', phone: '', real_name: '', password: '', referrer_phone: '' }
    activeTab.value = 'login'
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('login.registerFail')))
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
