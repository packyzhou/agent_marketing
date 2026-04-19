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
              <span class="text-[8px] font-bold text-slate-400 tracking-[0.15em] uppercase">{{ $t('admin.title') }}</span>
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
            <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest px-3 pt-2 pb-3">{{ $t('admin.title') }}</div>
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
        <div class="admin-content bg-white border border-slate-100 rounded-2xl p-6 shadow-sm">
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
  User as UserIcon, ChevronDown, Users, Shield, FolderOpen,
  Building2, Server, BarChart3, Brain, MessageSquare, FileText
} from 'lucide-vue-next'
import LangSwitcher from '../../components/LangSwitcher.vue'

const router = useRouter()
const { t } = useI18n()
const profileVisible = ref(false)
const showDropdown = ref(false)
const dropdownRef = ref(null)
const profileForm = ref({ username: '', phone: '', real_name: '', password: '' })

const roleType = computed(() => (localStorage.getItem('roleType') || '').toUpperCase())
const isAdmin = computed(() => roleType.value === 'ADMIN')

const allMenuItems = [
  { path: '/admin/users', labelKey: 'admin.menu.users', icon: Users, adminOnly: true },
  { path: '/admin/roles', labelKey: 'admin.menu.roles', icon: Shield, adminOnly: true },
  { path: '/admin/groups', labelKey: 'admin.menu.groups', icon: FolderOpen, adminOnly: false },
  { path: '/admin/tenants', labelKey: 'admin.menu.tenants', icon: Building2, adminOnly: false },
  { path: '/admin/providers', labelKey: 'admin.menu.providers', icon: Server, adminOnly: true },
  { path: '/admin/tokens', labelKey: 'admin.menu.tokens', icon: BarChart3, adminOnly: true },
  { path: '/admin/memory', labelKey: 'admin.menu.memory', icon: Brain, adminOnly: false },
  { path: '/admin/system-prompts', labelKey: 'admin.menu.systemPrompts', icon: FileText, adminOnly: true },
  { path: '/admin/proxy-debug', labelKey: 'admin.menu.chatDebug', icon: MessageSquare, adminOnly: false }
]

const menuItems = computed(() =>
  isAdmin.value ? allMenuItems : allMenuItems.filter(item => !item.adminOnly)
)

const displayName = computed(() => localStorage.getItem('username') || 'User')

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) showDropdown.value = false
}
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.body.classList.add('admin-active')
})
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
  document.body.classList.remove('admin-active')
})

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

/* ============================================================
 * Shared admin page styles — keep all admin pages visually
 * aligned with the Home / SystemPrompts aesthetic.
 * Targets Element Plus components rendered inside <router-view/>.
 * ============================================================ */

/* ── el-table ─────────────────────────────────────────────── */
.admin-content :deep(.el-table) {
  --el-table-border-color: rgb(241 245 249);
  --el-table-header-bg-color: rgb(248 250 252);
  --el-table-row-hover-bg-color: rgb(248 250 252);
  border: 1px solid rgb(241 245 249) !important;
  border-radius: 1rem;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}
.admin-content :deep(.el-table::before),
.admin-content :deep(.el-table::after),
.admin-content :deep(.el-table__inner-wrapper::before),
.admin-content :deep(.el-table__inner-wrapper::after) {
  display: none;
}
.admin-content :deep(.el-table th.el-table__cell) {
  background-color: rgb(248 250 252) !important;
  color: rgb(100 116 139);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid rgb(241 245 249) !important;
}
.admin-content :deep(.el-table th.el-table__cell .cell) {
  padding-top: 6px;
  padding-bottom: 6px;
}
.admin-content :deep(.el-table td.el-table__cell) {
  font-size: 13px;
  color: rgb(51 65 85);
  border-bottom: 1px solid rgb(241 245 249) !important;
}
.admin-content :deep(.el-table tr:last-child td.el-table__cell) {
  border-bottom: none !important;
}

/* ── el-button ────────────────────────────────────────────── */
.admin-content :deep(.el-button) {
  border-radius: 0.625rem;
  font-weight: 700;
  font-size: 12px;
  height: 32px;
  padding: 0 14px;
  transition: all 0.25s ease;
  border-width: 1px;
}
.admin-content :deep(.el-button--small) {
  height: 28px;
  padding: 0 12px;
  font-size: 11px;
  border-radius: 0.5rem;
}
.admin-content :deep(.el-button + .el-button) {
  margin-left: 8px;
}
.admin-content :deep(.el-button--primary) {
  background-color: rgb(2 6 23);
  border-color: rgb(2 6 23);
  color: #fff;
}
.admin-content :deep(.el-button--primary:hover),
.admin-content :deep(.el-button--primary:focus) {
  background-color: rgb(6 182 212);
  border-color: rgb(6 182 212);
  color: #fff;
}
.admin-content :deep(.el-button--success) {
  background-color: rgb(16 185 129);
  border-color: rgb(16 185 129);
}
.admin-content :deep(.el-button--success:hover) {
  background-color: rgb(5 150 105);
  border-color: rgb(5 150 105);
}
.admin-content :deep(.el-button--danger) {
  background-color: rgb(239 68 68);
  border-color: rgb(239 68 68);
}
.admin-content :deep(.el-button--danger:hover) {
  background-color: rgb(220 38 38);
  border-color: rgb(220 38 38);
}
.admin-content :deep(.el-button--warning) {
  background-color: rgb(245 158 11);
  border-color: rgb(245 158 11);
}
.admin-content :deep(.el-button--warning:hover) {
  background-color: rgb(217 119 6);
  border-color: rgb(217 119 6);
}
.admin-content :deep(.el-button--info) {
  background-color: rgb(100 116 139);
  border-color: rgb(100 116 139);
}
.admin-content :deep(.el-button--info:hover) {
  background-color: rgb(71 85 105);
  border-color: rgb(71 85 105);
}
.admin-content :deep(.el-button.is-disabled),
.admin-content :deep(.el-button.is-disabled:hover) {
  opacity: 0.5;
}

/* ── el-input / el-select ─────────────────────────────────── */
.admin-content :deep(.el-input__wrapper),
.admin-content :deep(.el-select .el-select__wrapper),
.admin-content :deep(.el-textarea__inner) {
  border-radius: 0.625rem !important;
  box-shadow: 0 0 0 1px rgb(226 232 240) inset !important;
  font-size: 13px;
  font-family: 'Inter', system-ui, sans-serif;
}
.admin-content :deep(.el-input__wrapper:hover),
.admin-content :deep(.el-select .el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px rgb(148 163 184) inset !important;
}
.admin-content :deep(.el-input__wrapper.is-focus),
.admin-content :deep(.el-select .el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px rgb(2 6 23) inset !important;
}

/* ── el-tag ───────────────────────────────────────────────── */
.admin-content :deep(.el-tag) {
  border-radius: 0.5rem;
  font-weight: 700;
  font-size: 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  height: 22px;
  padding: 0 8px;
  border: none;
}

/* ── el-pagination ────────────────────────────────────────── */
.admin-content :deep(.el-pagination) {
  font-family: 'Inter', system-ui, sans-serif;
  --el-pagination-button-color: rgb(100 116 139);
  --el-pagination-hover-color: rgb(2 6 23);
  font-weight: 600;
  margin-top: 16px;
}
.admin-content :deep(.el-pagination .btn-prev),
.admin-content :deep(.el-pagination .btn-next),
.admin-content :deep(.el-pagination .el-pager li) {
  border-radius: 0.5rem !important;
  background-color: rgb(248 250 252) !important;
  margin: 0 2px;
}
.admin-content :deep(.el-pagination .el-pager li.is-active) {
  background-color: rgb(2 6 23) !important;
  color: #fff !important;
}

/* ── el-descriptions ──────────────────────────────────────── */
.admin-content :deep(.el-descriptions__label) {
  font-weight: 700 !important;
  color: rgb(100 116 139) !important;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.admin-content :deep(.el-descriptions__content) {
  font-size: 13px;
  color: rgb(15 23 42);
}

/* ── el-card / el-empty / el-tabs ─────────────────────────── */
.admin-content :deep(.el-card) {
  border: 1px solid rgb(241 245 249);
  border-radius: 1rem;
  box-shadow: none;
}
.admin-content :deep(.el-card__header) {
  border-bottom: 1px solid rgb(241 245 249);
  padding: 14px 20px;
}
.admin-content :deep(.el-tabs__item) {
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(148 163 184);
}
.admin-content :deep(.el-tabs__item.is-active) {
  color: rgb(2 6 23);
}
.admin-content :deep(.el-tabs__active-bar) {
  background-color: rgb(2 6 23);
}

/* ── el-form ──────────────────────────────────────────────── */
.admin-content :deep(.el-form-item__label) {
  font-weight: 600;
  color: rgb(71 85 105);
  font-size: 13px;
}

/* ── raw <h2> page titles in shared sub-pages (e.g. ProxyDebug) ── */
.admin-content :deep(h2.text-2xl) {
  font-size: 20px !important;
  font-weight: 800;
  color: rgb(15 23 42);
  letter-spacing: -0.01em;
  margin: 0 0 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgb(241 245 249);
}

/* ── shared page header (used by admin pages) ────────────── */
.admin-content :deep(.admin-page-header) {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgb(241 245 249);
}
.admin-content :deep(.admin-page-header h2) {
  font-size: 20px;
  font-weight: 800;
  color: rgb(15 23 42);
  letter-spacing: -0.01em;
  margin: 0;
}
.admin-content :deep(.admin-page-header p) {
  font-size: 12px;
  color: rgb(148 163 184);
  margin: 4px 0 0;
}
</style>

<!--
  Global style block (non-scoped) — only takes effect while
  `body.admin-active` is set (toggled by this component's lifecycle).
  Used for el-dialog and other Element Plus elements that are
  teleported outside the admin layout DOM tree.
-->
<style>
body.admin-active .el-overlay-dialog .el-dialog {
  border-radius: 1.25rem;
  overflow: hidden;
  box-shadow: 0 40px 80px -20px rgba(0, 0, 0, 0.15);
  font-family: 'Inter', system-ui, sans-serif;
}
body.admin-active .el-overlay-dialog .el-dialog__header {
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgb(241 245 249);
  margin-right: 0;
}
body.admin-active .el-overlay-dialog .el-dialog__title {
  font-size: 16px;
  font-weight: 800;
  color: rgb(15 23 42);
  letter-spacing: -0.01em;
}
body.admin-active .el-overlay-dialog .el-dialog__body {
  padding: 24px;
  color: rgb(51 65 85);
}
body.admin-active .el-overlay-dialog .el-dialog__footer {
  padding: 16px 24px 20px;
  border-top: 1px solid rgb(241 245 249);
}
body.admin-active .el-overlay-dialog .el-button {
  border-radius: 0.625rem;
  font-weight: 700;
  font-size: 12px;
  height: 32px;
  padding: 0 14px;
}
body.admin-active .el-overlay-dialog .el-button--small {
  height: 28px;
  padding: 0 12px;
  font-size: 11px;
}
body.admin-active .el-overlay-dialog .el-button--primary {
  background-color: rgb(2 6 23);
  border-color: rgb(2 6 23);
}
body.admin-active .el-overlay-dialog .el-button--primary:hover,
body.admin-active .el-overlay-dialog .el-button--primary:focus {
  background-color: rgb(6 182 212);
  border-color: rgb(6 182 212);
}
body.admin-active .el-overlay-dialog .el-button--success {
  background-color: rgb(16 185 129);
  border-color: rgb(16 185 129);
}
body.admin-active .el-overlay-dialog .el-button--danger {
  background-color: rgb(239 68 68);
  border-color: rgb(239 68 68);
}
body.admin-active .el-overlay-dialog .el-button--warning {
  background-color: rgb(245 158 11);
  border-color: rgb(245 158 11);
}
body.admin-active .el-overlay-dialog .el-button--info {
  background-color: rgb(100 116 139);
  border-color: rgb(100 116 139);
}
body.admin-active .el-overlay-dialog .el-input__wrapper,
body.admin-active .el-overlay-dialog .el-select .el-select__wrapper,
body.admin-active .el-overlay-dialog .el-textarea__inner {
  border-radius: 0.625rem !important;
  box-shadow: 0 0 0 1px rgb(226 232 240) inset !important;
  font-size: 13px;
}
body.admin-active .el-overlay-dialog .el-input__wrapper.is-focus,
body.admin-active .el-overlay-dialog .el-select .el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px rgb(2 6 23) inset !important;
}
body.admin-active .el-overlay-dialog .el-table {
  border: 1px solid rgb(241 245 249) !important;
  border-radius: 0.75rem;
  overflow: hidden;
}
body.admin-active .el-overlay-dialog .el-table::before,
body.admin-active .el-overlay-dialog .el-table::after,
body.admin-active .el-overlay-dialog .el-table__inner-wrapper::before,
body.admin-active .el-overlay-dialog .el-table__inner-wrapper::after {
  display: none;
}
body.admin-active .el-overlay-dialog .el-table th.el-table__cell {
  background-color: rgb(248 250 252) !important;
  color: rgb(100 116 139);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  border-bottom: 1px solid rgb(241 245 249) !important;
}
body.admin-active .el-overlay-dialog .el-table td.el-table__cell {
  font-size: 13px;
  color: rgb(51 65 85);
  border-bottom: 1px solid rgb(241 245 249) !important;
}
body.admin-active .el-overlay-dialog .el-tag {
  border-radius: 0.5rem;
  font-weight: 700;
  font-size: 10px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  height: 22px;
  padding: 0 8px;
  border: none;
}
body.admin-active .el-overlay-dialog .el-pagination .btn-prev,
body.admin-active .el-overlay-dialog .el-pagination .btn-next,
body.admin-active .el-overlay-dialog .el-pagination .el-pager li {
  border-radius: 0.5rem !important;
  background-color: rgb(248 250 252) !important;
  margin: 0 2px;
}
body.admin-active .el-overlay-dialog .el-pagination .el-pager li.is-active {
  background-color: rgb(2 6 23) !important;
  color: #fff !important;
}
body.admin-active .el-overlay-dialog .el-form-item__label {
  font-weight: 600;
  color: rgb(71 85 105);
  font-size: 13px;
}
body.admin-active .el-overlay-dialog .el-descriptions__label {
  font-weight: 700 !important;
  color: rgb(100 116 139) !important;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
body.admin-active .el-overlay-dialog .el-descriptions__content {
  font-size: 13px;
  color: rgb(15 23 42);
}
body.admin-active .el-overlay-dialog .el-tabs__item {
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgb(148 163 184);
}
body.admin-active .el-overlay-dialog .el-tabs__item.is-active {
  color: rgb(2 6 23);
}
body.admin-active .el-overlay-dialog .el-tabs__active-bar {
  background-color: rgb(2 6 23);
}

/* el-message-box (confirm dialogs) */
body.admin-active .el-message-box {
  border-radius: 1.25rem;
  overflow: hidden;
  border: 1px solid rgb(241 245 249);
}
body.admin-active .el-message-box__title {
  font-size: 16px;
  font-weight: 800;
  color: rgb(15 23 42);
}
body.admin-active .el-message-box__btns .el-button {
  border-radius: 0.625rem;
  font-weight: 700;
  font-size: 12px;
}
body.admin-active .el-message-box__btns .el-button--primary {
  background-color: rgb(2 6 23);
  border-color: rgb(2 6 23);
}
body.admin-active .el-message-box__btns .el-button--primary:hover {
  background-color: rgb(6 182 212);
  border-color: rgb(6 182 212);
}
</style>
