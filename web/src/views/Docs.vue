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
          <router-link to="/docs" class="text-slate-950 transition-colors py-2">Docs</router-link>
          <router-link to="/about" class="hover:text-slate-950 transition-colors py-2">About</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-36 pb-12 px-6 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-black tracking-tighter mb-6 leading-[1.05]">
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-cyan-500 to-blue-600">Documentation</span>
        </h1>
        <p class="text-lg text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
          Everything you need to deploy, configure, and run the AI Agent Marketing Platform.
        </p>
      </div>
    </header>

    <!-- Docs Layout -->
    <main class="max-w-6xl mx-auto px-6 pb-32">
      <div class="flex flex-col lg:flex-row gap-10">
        <!-- Sidebar -->
        <aside class="lg:w-56 flex-shrink-0">
          <div class="lg:sticky lg:top-28">
            <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-4">Contents</div>
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
              <h2 class="text-2xl font-black tracking-tight">Project Overview</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8 space-y-4">
              <p class="text-slate-600 leading-relaxed">
                AI Agent Marketing Platform is a full-featured AI agent SaaS platform supporting multi-tenancy,
                referral grouping, dual-layer memory system, and token usage analytics. It enables the commercialization
                of human expertise through AI-powered agent replication.
              </p>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
                <div v-for="feature in features" :key="feature.title"
                  class="bg-slate-50/50 rounded-xl p-5 border border-slate-100">
                  <div class="flex items-center space-x-2 mb-2">
                    <component :is="feature.icon" class="w-4 h-4 text-cyan-500" />
                    <span class="text-xs font-bold text-slate-900 uppercase tracking-wide">{{ feature.title }}</span>
                  </div>
                  <p class="text-sm text-slate-500 leading-relaxed">{{ feature.desc }}</p>
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
              <h2 class="text-2xl font-black tracking-tight">Tech Stack</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">Backend</h3>
                <div class="space-y-2">
                  <div v-for="item in backendStack" :key="item.name" class="flex justify-between items-center py-2 border-b border-slate-50">
                    <span class="text-sm font-bold text-slate-900">{{ item.name }}</span>
                    <span class="text-xs font-mono text-slate-400">{{ item.version }}</span>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-sm font-black uppercase tracking-widest text-slate-400 mb-4">Frontend</h3>
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
              <h2 class="text-2xl font-black tracking-tight">Prerequisites</h2>
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
              <h2 class="text-2xl font-black tracking-tight">Quick Start</h2>
            </div>
            <div class="space-y-6">
              <!-- Docker Deployment -->
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">Option 1: Docker Compose (Recommended)</h3>
                <div class="space-y-4">
                  <div v-for="(step, idx) in dockerSteps" :key="idx">
                    <div class="flex items-center space-x-2 mb-2">
                      <div class="w-6 h-6 rounded-full bg-slate-950 text-white text-xs font-bold flex items-center justify-center">{{ idx + 1 }}</div>
                      <span class="text-sm font-bold text-slate-700">{{ step.label }}</span>
                    </div>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">{{ step.code }}</pre>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Startup Script -->
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">Option 2: Startup Script (Windows)</h3>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300">
                  <pre class="whitespace-pre">double-click start.bat</pre>
                </div>
                <p class="text-sm text-slate-400 mt-3">The script auto-checks Docker, builds, and starts all services.</p>
              </div>

              <!-- Local Dev -->
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">Option 3: Local Development</h3>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Backend</h4>
                    <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                      <pre class="whitespace-pre">cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload</pre>
                    </div>
                  </div>
                  <div>
                    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Frontend</h4>
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

          <!-- Access & Credentials -->
          <section id="access" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <KeyRound class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">Access & Credentials</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div v-for="endpoint in endpoints" :key="endpoint.label"
                  class="bg-slate-50 rounded-xl p-5 border border-slate-100">
                  <div class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">{{ endpoint.label }}</div>
                  <p class="text-sm font-bold font-mono text-slate-900">{{ endpoint.url }}</p>
                </div>
              </div>
              <div class="mt-6 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl p-5 border border-cyan-100">
                <div class="text-[10px] font-bold text-cyan-600 uppercase tracking-widest mb-2">Default Admin Account</div>
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
              <h2 class="text-2xl font-black tracking-tight">Architecture</h2>
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
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">AI Proxy</h4>
                  <p class="text-xs text-slate-500">Unified API to multiple LLM providers with stream support</p>
                </div>
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">Dual Memory</h4>
                  <p class="text-xs text-slate-500">KV fact storage + recursive behavior digest compression</p>
                </div>
                <div class="bg-slate-50 rounded-xl p-4 border border-slate-100">
                  <h4 class="text-xs font-bold uppercase tracking-wide text-slate-900 mb-1">Token Analytics</h4>
                  <p class="text-xs text-slate-500">Real-time usage tracking with 30-day trend visualization</p>
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
              <h2 class="text-2xl font-black tracking-tight">Configuration</h2>
            </div>
            <div class="space-y-6">
              <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
                <h3 class="text-base font-black mb-4">Memory System</h3>
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
                <h3 class="text-base font-black mb-4">Environment Variables</h3>
                <p class="text-sm text-slate-500 mb-4">Edit <code class="bg-slate-100 px-2 py-0.5 rounded text-xs font-mono">docker-compose.yml</code></p>
                <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                  <pre class="whitespace-pre">environment:
  MYSQL_ROOT_PASSWORD: your-secure-password
  SECRET_KEY: your-jwt-secret-key</pre>
                </div>
              </div>
            </div>
          </section>

          <!-- Common Commands -->
          <section id="commands" class="scroll-mt-28">
            <div class="flex items-center space-x-3 mb-6">
              <div class="w-10 h-10 bg-slate-950 rounded-2xl flex items-center justify-center">
                <Terminal class="w-5 h-5 text-white" />
              </div>
              <h2 class="text-2xl font-black tracking-tight">Common Commands</h2>
            </div>
            <div class="bg-white border border-slate-100 rounded-[1.5rem] p-8">
              <div class="space-y-4">
                <div v-for="cmd in commands" :key="cmd.label">
                  <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">{{ cmd.label }}</div>
                  <div class="bg-slate-950 rounded-xl p-4 font-mono text-sm text-slate-300 overflow-x-auto">
                    <pre class="whitespace-pre">{{ cmd.code }}</pre>
                  </div>
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
import { ref } from 'vue'
import {
  BookOpen,
  Layers,
  CheckCircle,
  Check,
  Zap,
  KeyRound,
  Network,
  Settings,
  Terminal,
  Shield,
  Brain,
  BarChart3,
  Users
} from 'lucide-vue-next'

const activeSection = ref('overview')

const sections = [
  { id: 'overview', title: 'Project Overview' },
  { id: 'tech-stack', title: 'Tech Stack' },
  { id: 'prerequisites', title: 'Prerequisites' },
  { id: 'quick-start', title: 'Quick Start' },
  { id: 'access', title: 'Access & Credentials' },
  { id: 'architecture', title: 'Architecture' },
  { id: 'configuration', title: 'Configuration' },
  { id: 'commands', title: 'Common Commands' }
]

const features = [
  { title: 'Multi-Tenancy', desc: 'AppKey/AppSecret auth, tenant-level API isolation, group user binding.', icon: Shield },
  { title: 'Dual Memory', desc: 'KV fact memory + recursive behavior digest with cross-layer reference detection.', icon: Brain },
  { title: 'Token Analytics', desc: 'Real-time usage stats, monthly comparison, 30-day trend visualization.', icon: BarChart3 },
  { title: 'Referral Groups', desc: 'Referral-based user grouping, automatic group creation and tenant sharing.', icon: Users }
]

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
  'At least 4GB available memory',
  'At least 10GB available disk space',
  'Ports 80, 3306, 8000 not occupied'
]

const dockerSteps = [
  { label: 'Clone the repository', code: 'git clone https://github.com/packyzhou/agent_marketing.git\ncd agent_marketing' },
  { label: 'Start all services', code: 'docker-compose up -d --build' },
  { label: 'Wait for startup (1-2 minutes), then verify', code: 'docker-compose ps\n# All services should show "Up" status' }
]

const endpoints = [
  { label: 'Frontend', url: 'http://localhost' },
  { label: 'Backend API', url: 'http://localhost:8000' },
  { label: 'API Docs', url: 'http://localhost:8000/docs' }
]

const commands = [
  { label: 'View all logs', code: 'docker-compose logs -f' },
  { label: 'Restart services', code: 'docker-compose restart' },
  { label: 'Stop services', code: 'docker-compose down' },
  { label: 'Reset database', code: 'docker-compose down -v\ndocker-compose up -d --build' },
  { label: 'Rebuild after code changes', code: 'docker-compose down\ndocker-compose up -d --build' }
]
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap');
</style>
