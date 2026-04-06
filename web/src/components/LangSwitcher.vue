<template>
  <div class="relative" ref="containerRef">
    <button
      @click="open = !open"
      class="flex items-center space-x-1.5 text-[11px] font-bold uppercase tracking-widest transition-colors"
      :class="dark ? 'text-slate-400 hover:text-white' : 'text-slate-400 hover:text-slate-950'">
      <Globe class="w-3.5 h-3.5" />
      <span>{{ currentLabel }}</span>
    </button>
    <div v-if="open"
      class="absolute right-0 mt-2 w-32 bg-white border border-slate-100 rounded-xl shadow-[0_20px_40px_-10px_rgba(0,0,0,0.1)] py-1 z-50">
      <button v-for="l in langs" :key="l.code"
        @click="switchLang(l.code)"
        class="w-full text-left px-4 py-2 text-sm font-medium transition-colors"
        :class="locale === l.code ? 'text-cyan-500 bg-cyan-50/50' : 'text-slate-600 hover:bg-slate-50'">
        {{ l.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { Globe } from 'lucide-vue-next'

defineProps({
  dark: { type: Boolean, default: false }
})

const { locale } = useI18n()
const open = ref(false)
const containerRef = ref(null)

const langs = [
  { code: 'zh', label: '中文' },
  { code: 'en', label: 'English' },
  { code: 'ja', label: '日本語' }
]

const currentLabel = computed(() => langs.find(l => l.code === locale.value)?.label || 'EN')

const switchLang = (code) => {
  locale.value = code
  localStorage.setItem('locale', code)
  open.value = false
}

const handleClickOutside = (e) => {
  if (containerRef.value && !containerRef.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>
