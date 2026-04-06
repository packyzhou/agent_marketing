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
            <span class="text-[10px] font-bold text-slate-400 tracking-[0.2em] uppercase">Clone Human Intelligence</span>
          </div>
        </router-link>
        <div class="hidden md:flex items-center space-x-10 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
          <router-link to="/home" class="hover:text-slate-950 transition-colors py-2">Home</router-link>
          <router-link to="/docs" class="hover:text-slate-950 transition-colors py-2">Docs</router-link>
          <router-link to="/about" class="text-slate-950 transition-colors py-2">About</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-36 pb-16 px-6 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-black tracking-tighter mb-6 leading-[1.05]">
          About
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">Agent Market</span>
        </h1>
        <p class="text-lg text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
          Redefining "hiring" — turning personal expertise into scalable digital assets.
        </p>
      </div>
    </header>

    <!-- Main content -->
    <main class="max-w-6xl mx-auto px-6 pb-32">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <!-- Left: Initiator & Partners -->
        <div class="space-y-10">
          <!-- Initiator Card -->
          <div class="bg-white border border-slate-100 rounded-[2rem] p-8 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] transition-all duration-700">
            <div class="flex items-center space-x-2 mb-6">
              <div class="w-8 h-8 bg-slate-950 rounded-xl flex items-center justify-center">
                <User class="w-4 h-4 text-white" />
              </div>
              <h2 class="text-lg font-black tracking-tight uppercase">Initiator</h2>
            </div>
            <div class="space-y-4">
              <div class="flex items-center space-x-3">
                <div class="w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center text-white text-xl font-black">
                  J
                </div>
                <div>
                  <p class="text-xl font-black tracking-tight">Mr. Joe</p>
                  <p class="text-[11px] font-bold text-cyan-500 uppercase tracking-[0.15em]">Founder & Creator</p>
                </div>
              </div>
              <div class="mt-6 space-y-3">
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

          <!-- Cooperation Partners -->
          <div class="bg-white border border-slate-100 rounded-[2rem] p-8 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] transition-all duration-700">
            <div class="flex items-center space-x-2 mb-6">
              <div class="w-8 h-8 bg-slate-950 rounded-xl flex items-center justify-center">
                <Building2 class="w-4 h-4 text-white" />
              </div>
              <h2 class="text-lg font-black tracking-tight uppercase">Cooperation Partners</h2>
            </div>
            <div class="space-y-4">
              <div v-for="partner in partners" :key="partner.name"
                class="flex items-start space-x-4 bg-slate-50 px-5 py-4 rounded-xl border border-slate-100 hover:border-cyan-200 transition-colors">
                <div class="w-10 h-10 bg-white rounded-xl border border-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Building2 class="w-5 h-5 text-cyan-500" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-bold text-slate-900">{{ partner.name }}</p>
                  <p class="text-xs text-slate-400 mt-0.5">{{ partner.field }}</p>
                  <div class="flex items-center space-x-2 mt-2">
                    <Mail class="w-3 h-3 text-slate-300" />
                    <span class="text-xs text-slate-500">{{ partner.contact }}</span>
                  </div>
                </div>
                <span class="text-[9px] font-bold uppercase tracking-widest px-2 py-1 rounded-md"
                  :class="partner.status === 'confirmed' ? 'bg-emerald-50 text-emerald-500' : 'bg-amber-50 text-amber-500'">
                  {{ partner.status === 'confirmed' ? 'Confirmed' : 'In Talk' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Project Vision -->
        <div class="space-y-10">
          <div class="bg-gradient-to-br from-slate-950 to-slate-800 rounded-[2rem] p-10 text-white hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.3)] transition-all duration-700">
            <div class="flex items-center space-x-2 mb-8">
              <div class="w-8 h-8 bg-white/10 rounded-xl flex items-center justify-center">
                <Lightbulb class="w-4 h-4 text-cyan-400" />
              </div>
              <h2 class="text-lg font-black tracking-tight uppercase">Project Vision</h2>
            </div>
            <blockquote class="text-2xl md:text-3xl font-black tracking-tight leading-snug mb-8">
              A project that realizes monetization by replicating human capabilities through
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">AI technology</span>.
            </blockquote>
            <p class="text-slate-400 text-sm leading-relaxed mb-6">
              We believe that everyone's expertise and experience have immeasurable value. Through neural extraction technology, we convert expert experience into elastically scalable digital assets, enabling global productivity equality.
            </p>
            <div class="grid grid-cols-2 gap-4 mt-8">
              <div class="bg-white/5 rounded-xl p-4 border border-white/10">
                <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Mission</div>
                <p class="text-sm font-bold">Democratize human expertise through AI replication</p>
              </div>
              <div class="bg-white/5 rounded-xl p-4 border border-white/10">
                <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Goal</div>
                <p class="text-sm font-bold">Build the world's largest talent cloning marketplace</p>
              </div>
              <div class="bg-white/5 rounded-xl p-4 border border-white/10">
                <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Technology</div>
                <p class="text-sm font-bold">Neural extraction & dual-layer memory system</p>
              </div>
              <div class="bg-white/5 rounded-xl p-4 border border-white/10">
                <div class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-1">Model</div>
                <p class="text-sm font-bold">Expert experience as tradeable digital assets</p>
              </div>
            </div>
          </div>

          <!-- Roadmap -->
          <div class="bg-white border border-slate-100 rounded-[2rem] p-8 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.08)] transition-all duration-700">
            <div class="flex items-center space-x-2 mb-6">
              <div class="w-8 h-8 bg-slate-950 rounded-xl flex items-center justify-center">
                <Rocket class="w-4 h-4 text-white" />
              </div>
              <h2 class="text-lg font-black tracking-tight uppercase">Roadmap</h2>
            </div>
            <div class="space-y-4">
              <div v-for="(item, idx) in roadmap" :key="idx"
                class="flex items-start space-x-4">
                <div class="flex flex-col items-center">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-black"
                    :class="item.done ? 'bg-cyan-500 text-white' : 'bg-slate-100 text-slate-400'">
                    {{ idx + 1 }}
                  </div>
                  <div v-if="idx < roadmap.length - 1" class="w-px h-8 bg-slate-100 mt-1"></div>
                </div>
                <div class="pt-1">
                  <p class="text-sm font-bold" :class="item.done ? 'text-slate-900' : 'text-slate-400'">{{ item.title }}</p>
                  <p class="text-xs text-slate-400 mt-0.5">{{ item.desc }}</p>
                </div>
              </div>
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
          <p class="text-slate-500 text-sm leading-relaxed">
            Redefining "hiring". Commercializing personal experience is the first step towards global productivity equality.
          </p>
        </div>
        <div class="grid grid-cols-2 gap-16">
          <div class="flex flex-col space-y-4">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-2">Navigate</span>
            <router-link to="/home" class="text-slate-500 text-sm hover:text-white transition-colors">Home</router-link>
            <router-link to="/docs" class="text-slate-500 text-sm hover:text-white transition-colors">Docs</router-link>
            <router-link to="/about" class="text-slate-500 text-sm hover:text-white transition-colors">About</router-link>
          </div>
          <div class="flex flex-col space-y-4">
            <span class="text-[10px] font-bold text-white uppercase tracking-[0.2em] mb-2">Connect</span>
            <a href="https://github.com/packyzhou/agent_marketing" class="text-slate-500 text-sm hover:text-white transition-colors">GitHub</a>
          </div>
        </div>
      </div>
      <div class="max-w-6xl mx-auto mt-20 pt-10 border-t border-slate-900 flex justify-between items-center text-[10px] font-bold text-slate-700 uppercase tracking-widest">
        <span>Mr.Joe &copy; 2026 AI Agent Market.</span>
        <span>Designed for the intelligence era.</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
import {
  User,
  Mail,
  MessageCircle,
  Building2,
  Lightbulb,
  Rocket
} from 'lucide-vue-next'
import { ref } from 'vue'

const partners = ref([
  {
    name: 'TechVision AI Lab',
    field: 'AI Research & Development',
    contact: 'biz@techvision-ai.com',
    status: 'in_talk'
  },
  {
    name: 'CloudBridge Solutions',
    field: 'Cloud Infrastructure',
    contact: 'partner@cloudbridge.io',
    status: 'in_talk'
  },
  {
    name: 'DataMind Analytics',
    field: 'Data Analytics & BI',
    contact: 'coop@datamind.tech',
    status: 'in_talk'
  }
])

const roadmap = ref([
  { title: 'Core Platform Launch', desc: 'Multi-tenant architecture, dual-layer memory, token analytics', done: true },
  { title: 'Agent Marketplace', desc: 'Expert cloning, pricing engine, hire workflow', done: true },
  { title: 'Enterprise Partnerships', desc: 'B2B cooperation, API integration, custom solutions', done: false },
  { title: 'Global Expansion', desc: 'Multi-language support, international payment, compliance', done: false }
])
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
