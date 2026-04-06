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
          <router-link to="/docs" class="text-slate-950 transition-colors py-2">{{ $t('nav.docs') }}</router-link>
          <router-link to="/about" class="hover:text-slate-950 transition-colors py-2">{{ $t('nav.about') }}</router-link>
          <LangSwitcher />
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-36 pb-12 px-6 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-black tracking-tighter mb-6 leading-[1.05]">
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">{{ $t('docs.title') }}</span>
        </h1>
        <p class="text-lg text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">{{ $t('docs.subtitle') }}</p>
      </div>
    </header>

    <!-- Docs Layout -->
    <main class="max-w-6xl mx-auto px-6 pb-32">
      <div class="flex flex-col lg:flex-row gap-10">
        <!-- Sidebar -->
        <aside class="lg:w-56 flex-shrink-0">
          <div class="lg:sticky lg:top-28">
            <nav class="space-y-1">
              <a v-for="section in sections" :key="section.id"
                :href="'#' + section.id"
                class="block px-3 py-2 text-sm rounded-lg transition-colors"
                :class="activeSection === section.id
                  ? 'bg-slate-950 text-white font-bold'
                  : 'text-slate-500 hover:text-slate-900 hover:bg-slate-50 font-medium'"
                @click="activeSection = section.id">
                {{ section.title }}
              </a>
            </nav>
          </div>
        </aside>

        <!-- Content -->
        <div class="flex-1 min-w-0 space-y-16">
          <!-- Overview -->
          <section id="overview" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <BookOpen class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.overview') }}</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8 space-y-4">
              <p class="text-slate-600 leading-relaxed">{{ $t('docs.overviewDesc') }}</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                  <div class="flex items-center space-x-2 mb-2">
                    <Shield class="w-4 h-4 text-cyan-500" />
                    <span class="text-xs font-bold text-slate-900 uppercase tracking-wide">{{ $t('docs.features.multiTenant') }}</span>
                  </div>
                  <p class="text-sm text-slate-500 leading-relaxed">{{ $t('docs.features.multiTenantDesc') }}</p>
                </div>
                <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                  <div class="flex items-center space-x-2 mb-2">
                    <Brain class="w-4 h-4 text-cyan-500" />
                    <span class="text-xs font-bold text-slate-900 uppercase tracking-wide">{{ $t('docs.features.dualMemory') }}</span>
                  </div>
                  <p class="text-sm text-slate-500 leading-relaxed">{{ $t('docs.features.dualMemoryDesc') }}</p>
                </div>
                <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                  <div class="flex items-center space-x-2 mb-2">
                    <BarChart3 class="w-4 h-4 text-cyan-500" />
                    <span class="text-xs font-bold text-slate-900 uppercase tracking-wide">{{ $t('docs.features.tokenAnalytics') }}</span>
                  </div>
                  <p class="text-sm text-slate-500 leading-relaxed">{{ $t('docs.features.tokenAnalyticsDesc') }}</p>
                </div>
                <div class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                  <div class="flex items-center space-x-2 mb-2">
                    <Users class="w-4 h-4 text-cyan-500" />
                    <span class="text-xs font-bold text-slate-900 uppercase tracking-wide">{{ $t('docs.features.referralGroups') }}</span>
                  </div>
                  <p class="text-sm text-slate-500 leading-relaxed">{{ $t('docs.features.referralGroupsDesc') }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Tech Stack -->
          <section id="tech-stack" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Layers class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.techStack') }}</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">{{ $t('docs.backend') }}</h3>
                <div class="space-y-2">
                  <div v-for="item in backendStack" :key="item.name" class="flex justify-between items-center py-2 border-b border-slate-50">
                    <span class="text-sm font-bold text-slate-900">{{ item.name }}</span>
                    <span class="text-xs font-mono text-slate-400">{{ item.version }}</span>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">{{ $t('docs.frontend') }}</h3>
                <div class="space-y-2">
                  <div v-for="item in frontendStack" :key="item.name" class="flex justify-between items-center py-2 border-b border-slate-50">
                    <span class="text-sm font-bold text-slate-900">{{ item.name }}</span>
                    <span class="text-xs font-mono text-slate-400">{{ item.version }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Prerequisites -->
          <section id="prerequisites" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <CheckCircle class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.prerequisites') }}</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
              <ul class="space-y-3">
                <li v-for="req in prerequisites" :key="req" class="flex items-start space-x-3">
                  <div class="w-5 h-5 rounded-full bg-cyan-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Check class="w-3 h-3 text-cyan-500" />
                  </div>
                  <span class="text-sm text-slate-600">{{ req }}</span>
                </li>
              </ul>
            </div>
          </section>

          <!-- Quick Start -->
          <section id="quick-start" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Zap class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.quickStart') }}</h2>
            </div>
            <div class="space-y-6">
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">{{ $t('docs.option1') }}</h3>
                <div class="space-y-4">
                  <div>
                    <div class="flex items-center space-x-2 mb-2">
                      <div class="w-6 h-6 rounded-full bg-slate-950 text-white text-xs font-bold flex items-center justify-center">1</div>
                      <span class="text-sm font-bold text-slate-700">{{ $t('docs.dockerSteps.step1') }}</span>
                    </div>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">git clone https://github.com/packyzhou/agent_marketing.git
cd agent_marketing</pre>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center space-x-2 mb-2">
                      <div class="w-6 h-6 rounded-full bg-slate-950 text-white text-xs font-bold flex items-center justify-center">2</div>
                      <span class="text-sm font-bold text-slate-700">{{ $t('docs.dockerSteps.step2') }}</span>
                    </div>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">docker-compose up -d --build</pre>
                    </div>
                  </div>
                  <div>
                    <div class="flex items-center space-x-2 mb-2">
                      <div class="w-6 h-6 rounded-full bg-slate-950 text-white text-xs font-bold flex items-center justify-center">3</div>
                      <span class="text-sm font-bold text-slate-700">{{ $t('docs.dockerSteps.step3') }}</span>
                    </div>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">docker-compose ps
# All services should show "Up" status</pre>
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">{{ $t('docs.option2') }}</h3>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300">
                  <pre class="whitespace-pre">double-click start.bat</pre>
                </div>
                <p class="text-sm text-slate-400 mt-3">{{ $t('docs.option2Desc') }}</p>
              </div>

              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">{{ $t('docs.option3') }}</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">{{ $t('docs.backend') }}</h4>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload</pre>
                    </div>
                  </div>
                  <div>
                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">{{ $t('docs.frontend') }}</h4>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">cd web
npm install
npm run dev</pre>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Access -->
          <section id="access" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <KeyRound class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.access') }}</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div v-for="ep in endpoints" :key="ep.label" class="bg-slate-50 rounded-xl p-5 border border-slate-100">
                  <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">{{ ep.label }}</div>
                  <p class="text-sm font-bold font-mono text-slate-900">{{ ep.url }}</p>
                </div>
              </div>
              <div class="mt-6 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl p-5 border border-cyan-100">
                <div class="text-[10px] font-bold text-cyan-600 uppercase tracking-widest mb-2">{{ $t('docs.defaultAdmin') }}</div>
                <div class="flex items-center space-x-6">
                  <span class="text-sm text-slate-700"><span class="font-bold">Username:</span> admin</span>
                  <span class="text-sm text-slate-700"><span class="font-bold">Password:</span> admin123</span>
                </div>
              </div>
            </div>
          </section>

          <!-- Architecture -->
          <section id="architecture" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Network class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.architecture') }}</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
              <div class="bg-slate-950 rounded-xl p-6 font-mono text-sm text-slate-300 overflow-x-auto">
                <pre class="whitespace-pre">
  Browser (Vue3 SPA)
        |
        v
  Nginx (Frontend :80)  ----->  FastAPI (Backend :8000)
                                       |
                                       v
                                 MySQL Database
                                       |
                                       v
                              AI Providers (LLM APIs)
                                       |
                                       v
                              Memory Files (KV + Digest)</pre>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">{{ $t('docs.archBlocks.proxy') }}</h4>
                  <p class="text-xs text-slate-500">{{ $t('docs.archBlocks.proxyDesc') }}</p>
                </div>
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">{{ $t('docs.archBlocks.memory') }}</h4>
                  <p class="text-xs text-slate-500">{{ $t('docs.archBlocks.memoryDesc') }}</p>
                </div>
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">{{ $t('docs.archBlocks.analytics') }}</h4>
                  <p class="text-xs text-slate-500">{{ $t('docs.archBlocks.analyticsDesc') }}</p>
                </div>
              </div>
            </div>
          </section>

          <!-- Configuration -->
          <section id="configuration" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Settings class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.configuration') }}</h2>
            </div>
            <div class="space-y-6">
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">{{ $t('docs.memorySystem') }}</h3>
                <p class="text-sm text-slate-500 mb-4">Edit <code class="bg-slate-100 px-2 py-0.5 rounded text-xs font-mono">server/agent_config.json</code></p>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                  <pre class="whitespace-pre">{
  "memory_processing": {
    "rounds_threshold": 5,
    "enable_auto_processing": true,
    "digest_rounds": 10
  }
}</pre>
                </div>
              </div>
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">{{ $t('docs.envVars') }}</h3>
                <p class="text-sm text-slate-500 mb-4">Edit <code class="bg-slate-100 px-2 py-0.5 rounded text-xs font-mono">docker-compose.yml</code></p>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                  <pre class="whitespace-pre">environment:
  MYSQL_ROOT_PASSWORD: your-secure-password
  SECRET_KEY: your-jwt-secret-key</pre>
                </div>
              </div>
            </div>
          </section>

          <!-- Commands -->
          <section id="commands" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Terminal class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">{{ $t('docs.sections.commands') }}</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8 space-y-4">
              <div v-for="cmd in commands" :key="cmd.key">
                <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">{{ $t('docs.commands.' + cmd.key) }}</div>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                  <pre class="whitespace-pre">{{ cmd.code }}</pre>
                </div>
              </div>
            </div>
          </section>
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  BookOpen, Layers, CheckCircle, Check, Zap, KeyRound, Network, Settings, Terminal,
  Shield, Brain, BarChart3, Users
} from 'lucide-vue-next'
import LangSwitcher from '../components/LangSwitcher.vue'

const { t } = useI18n()
const activeSection = ref('overview')

const sections = computed(() => [
  { id: 'overview', title: t('docs.sections.overview') },
  { id: 'tech-stack', title: t('docs.sections.techStack') },
  { id: 'prerequisites', title: t('docs.sections.prerequisites') },
  { id: 'quick-start', title: t('docs.sections.quickStart') },
  { id: 'access', title: t('docs.sections.access') },
  { id: 'architecture', title: t('docs.sections.architecture') },
  { id: 'configuration', title: t('docs.sections.configuration') },
  { id: 'commands', title: t('docs.sections.commands') }
])

const backendStack = [
  { name: 'Python', version: '3.11' },
  { name: 'FastAPI', version: '0.109' },
  { name: 'MySQL', version: '8.0' },
  { name: 'SQLAlchemy', version: '2.0' },
  { name: 'JWT + Bcrypt', version: '-' },
  { name: 'httpx', version: '0.26' }
]

const frontendStack = [
  { name: 'Vue 3', version: '3.4' },
  { name: 'Element Plus', version: '2.5' },
  { name: 'Tailwind CSS', version: '3.4' },
  { name: 'ECharts', version: '5.4' },
  { name: 'Vite', version: '5.0' },
  { name: 'Axios', version: '1.6' }
]

const prerequisites = [
  'Docker Desktop 4.0+ (Windows 11 / macOS / Linux)',
  '4GB+ available memory',
  '10GB+ available disk space',
  'Ports 80, 3306, 8000 available'
]

const endpoints = [
  { label: 'Frontend', url: 'http://localhost' },
  { label: 'Backend API', url: 'http://localhost:8000' },
  { label: 'API Docs', url: 'http://localhost:8000/docs' }
]

const commands = [
  { key: 'viewLogs', code: 'docker-compose logs -f' },
  { key: 'restart', code: 'docker-compose restart' },
  { key: 'stop', code: 'docker-compose down' },
  { key: 'resetDb', code: 'docker-compose down -v\ndocker-compose up -d --build' },
  { key: 'rebuild', code: 'docker-compose down\ndocker-compose up -d --build' }
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
