import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLayout from '../views/admin/Layout.vue'

const routes = [
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('../views/Market.vue')
  },
  {
    path: '/payment',
    name: 'Payment',
    component: () => import('../views/Payment.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue')
  },
  {
    path: '/docs',
    name: 'Docs',
    component: () => import('../views/Docs.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      {
        path: 'users',
        name: 'AdminUsers',
        meta: { adminOnly: true },
        component: () => import('../views/admin/Users.vue')
      },
      {
        path: 'roles',
        name: 'AdminRoles',
        meta: { adminOnly: true },
        component: () => import('../views/admin/Roles.vue')
      },
      {
        path: 'groups',
        name: 'AdminGroups',
        component: () => import('../views/admin/Groups.vue')
      },
      {
        path: 'tenants',
        name: 'AdminTenants',
        component: () => import('../views/admin/Tenants.vue')
      },
      {
        path: 'providers',
        name: 'AdminProviders',
        meta: { adminOnly: true },
        component: () => import('../views/admin/Providers.vue')
      },
      {
        path: 'tokens',
        name: 'AdminTokens',
        meta: { adminOnly: true },
        component: () => import('../views/admin/Tokens.vue')
      },
      {
        path: 'memory',
        name: 'AdminMemory',
        component: () => import('../views/admin/Memory.vue')
      },
      {
        path: 'system-prompts',
        name: 'AdminSystemPrompts',
        meta: { adminOnly: true },
        component: () => import('../views/admin/SystemPrompts.vue')
      },
      {
        path: 'proxy-debug',
        name: 'AdminProxyDebug',
        component: () => import('../views/user/ProxyDebug.vue')
      }
    ]
  },
  {
    path: '/user/:pathMatch(.*)*',
    redirect: '/admin/groups'
  },
  {
    path: '/',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory('/agent_marketing/'),
  routes
})

const publicPaths = ['/login', '/home', '/about', '/docs', '/market', '/payment']

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const roleType = (localStorage.getItem('roleType') || '').toUpperCase()

  if (publicPaths.includes(to.path)) {
    next()
    return
  }

  if (!token) {
    next('/login')
    return
  }

  // Admin-only pages require ADMIN role; other admin pages are accessible to all authenticated users
  if (to.path.startsWith('/admin') && to.meta.adminOnly && roleType !== 'ADMIN') {
    next('/admin/groups')
    return
  }

  next()
})

export default router
