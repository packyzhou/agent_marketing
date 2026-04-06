import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLayout from '../views/admin/Layout.vue'
import UserLayout from '../views/user/Layout.vue'

const routes = [
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue')
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
        component: () => import('../views/admin/Users.vue')
      },
      {
        path: 'roles',
        name: 'AdminRoles',
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
        component: () => import('../views/admin/Providers.vue')
      },
      {
        path: 'tokens',
        name: 'AdminTokens',
        component: () => import('../views/admin/Tokens.vue')
      },
      {
        path: 'memory',
        name: 'AdminMemory',
        component: () => import('../views/admin/Memory.vue')
      },
      {
        path: 'proxy-debug',
        name: 'AdminProxyDebug',
        component: () => import('../views/user/ProxyDebug.vue')
      }
    ]
  },
  {
    path: '/user',
    component: UserLayout,
    children: [
      {
        path: 'dashboard',
        name: 'UserDashboard',
        component: () => import('../views/user/Dashboard.vue')
      },
      {
        path: 'tenants',
        name: 'UserTenants',
        component: () => import('../views/user/Tenants.vue')
      },
      {
        path: 'group-tenants',
        name: 'UserGroupTenants',
        component: () => import('../views/user/GroupTenants.vue')
      },
      {
        path: 'groups',
        name: 'UserGroups',
        component: () => import('../views/user/Groups.vue')
      },
      {
        path: 'tokens',
        name: 'UserTokens',
        component: () => import('../views/user/Tokens.vue')
      },
      {
        path: 'memory',
        name: 'UserMemory',
        component: () => import('../views/user/Memory.vue')
      },
      {
        path: 'proxy-debug',
        name: 'UserProxyDebug',
        component: () => import('../views/user/ProxyDebug.vue')
      }
    ]
  },
  {
    path: '/',
    redirect: '/home'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const publicPaths = ['/login', '/home', '/about', '/docs']

router.beforeEach((to, from, next) => {
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

  if (to.path.startsWith('/admin') && roleType !== 'ADMIN') {
    next('/user/dashboard')
    return
  }

  next()
})

export default router
