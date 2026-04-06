<template>
  <div class="min-h-screen bg-slate-50/50 font-sans text-slate-900 antialiased">
    <!-- Top Navigation -->
    <nav class="fixed top-0 w-full bg-white/80 backdrop-blur-xl border-b border-slate-100 z-50">
      <div class="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center space-x-6">
          <router-link to="/home" class="flex items-center space-x-2 group cursor-pointer">
            <div class="h-10 w-14 flex items-center justify-center">
              <img src="/logo_main_page.png" alt="Logo" class="w-full h-full object-contain mix-blend-multiply" />
            </div>
            <div class="flex flex-col leading-tight">
              <span class="font-black tracking-tighter text-sm uppercase">Agent Market</span>
              <span class="text-[8px] font-bold text-slate-400 tracking-[0.15em] uppercase">{{ $t('user.title') }}</span>
            </div>
          </router-link>
        </div>
        <div class="flex items-center space-x-4">
          <LangSwitcher />
          <span class="text-xs font-bold text-slate-400">{{ displayName }}</span>
          <div class="relative" ref="dropdownRef">
            <button @click="showDropdown = !showDropdown"
              class="h-9 px-4 bg-slate-950 text-white text-xs font-bold rounded-xl hover:bg-cyan-500 transition-all duration-300 flex items-center space-x-1.5">
              <UserIcon class="w-3.5 h-3.5" />
              <ChevronDown class="w-3 h-3" :class="showDropdown ? 'rotate-180' : ''" style="transition: transform 0.2s" />
            </button>
            <div v-if="showDropdown"
              class="absolute right-0 mt-2 w-44 bg-white border border-slate-100 rounded-xl shadow-[0_20px_40px_-10px_rgba(0,0,0,0.1)] py-2 z-50">
              <button @click="openProfileDialog" class="w-full text-left px-4 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors">
                {{ $t('profile.title') }}
              </button>
              <button @click="logout" class="w-full text-left px-4 py-2.5 text-sm font-medium text-red-500 hover:bg-red-50 transition-colors">
                {{ $t('profile.signOut') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Body -->
    <div class="max-w-[1400px] mx-auto pt-20 px-6 pb-10 flex gap-6">
      <!-- Sidebar -->
      <aside class="w-52 flex-shrink-0">
        <div class="sticky top-20">
          <div class="bg-white border border-slate-100 rounded-2xl p-3 shadow-sm">
            <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-3 pt-2 pb-3">{{ $t('user.title') }}</div>
            <nav class="space-y-0.5">
              <router-link v-for="item in menuItems" :key="item.path" :to="item.path"
                class="flex items-center space-x-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
                :class="$route.path === item.path
                  ? 'bg-slate-950 text-white font-bold shadow-lg'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50'">
                <component :is="item.icon" class="w-4 h-4" />
                <span>{{ $t(item.labelKey) }}</span>
              </router-link>
            </nav>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 min-w-0">
        <div class="bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Profile Dialog -->
    <el-dialog v-model="profileVisible" :title="$t('profile.title')" width="480px">
      <el-form :model="profileForm" label-width="100px">
        <el-form-item :label="$t('profile.username')">
          <el-input v-model="profileForm.username" />
        </el-form-item>
        <el-form-item :label="$t('profile.phone')">
          <el-input v-model="profileForm.phone" />
        </el-form-item>
        <el-form-item :label="$t('profile.realName')">
          <el-input v-model="profileForm.real_name" />
        </el-form-item>
        <el-form-item :label="$t('profile.newPassword')">
          <el-input v-model="profileForm.password" type="password" show-password :placeholder="$t('profile.newPasswordPh')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="flex justify-end space-x-3">
          <button @click="profileVisible = false"
            class="px-5 py-2.5 text-sm font-bold text-slate-500 border border-slate-200 rounded-xl hover:border-slate-300 transition-colors">
            {{ $t('profile.cancel') }}
          </button>
          <button @click="saveProfile"
            class="px-5 py-2.5 text-sm font-bold text-white bg-slate-950 rounded-xl hover:bg-cyan-500 transition-all duration-300">
            {{ $t('profile.save') }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '../../api/request'
import {
  User as UserIcon, ChevronDown, LayoutDashboard, Building2,
  FolderOpen, Link, BarChart3, Brain, MessageSquare
} from 'lucide-vue-next'
import LangSwitcher from '../../components/LangSwitcher.vue'

const router = useRouter()
const { t } = useI18n()
const profileVisible = ref(false)
const showDropdown = ref(false)
const dropdownRef = ref(null)
const profileForm = ref({ username: '', phone: '', real_name: '', password: '' })

const menuItems = [
  { path: '/user/dashboard', labelKey: 'user.menu.dashboard', icon: LayoutDashboard },
  { path: '/user/tenants', labelKey: 'user.menu.tenants', icon: Building2 },
  { path: '/user/groups', labelKey: 'user.menu.groups', icon: FolderOpen },
  { path: '/user/group-tenants', labelKey: 'user.menu.groupTenants', icon: Link },
  { path: '/user/tokens', labelKey: 'user.menu.tokens', icon: BarChart3 },
  { path: '/user/memory', labelKey: 'user.menu.memory', icon: Brain },
  { path: '/user/proxy-debug', labelKey: 'user.menu.chatDebug', icon: MessageSquare }
]

const displayName = computed(() => localStorage.getItem('username') || 'User')

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) showDropdown.value = false
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))

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

const openProfileDialog = async () => {
  showDropdown.value = false
  try {
    const response = await api.get('/user/profile')
    profileForm.value = { username: response.username || '', phone: response.phone || '', real_name: response.real_name || '', password: '' }
    profileVisible.value = true
  } catch (error) {
    ElMessage.error(t('profile.loadFail'))
  }
}

const saveProfile = async () => {
  const password = profileForm.value.password?.trim() || ''
  if (password && password.length <= 6) {
    ElMessage.error(t('profile.passwordTooShort'))
    return
  }
  try {
    const payload = {
      username: profileForm.value.username.trim(),
      phone: profileForm.value.phone.trim(),
      real_name: profileForm.value.real_name?.trim() || null,
      password: password || null
    }
    await api.put('/user/profile', payload)
    localStorage.setItem('username', payload.username)
    ElMessage.success(t('profile.saveSuccess'))
    profileVisible.value = false
  } catch (error) {
    ElMessage.error(getErrorMessage(error, t('profile.saveFail')))
  }
}

const logout = () => {
  showDropdown.value = false
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('roleName')
  localStorage.removeItem('roleType')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
