import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminLayout from '../views/admin/Layout.vue'
import UserLayout from '../views/user/Layout.vue'

const routes = [
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
        path: 'tokens',
        name: 'UserTokens',
        component: () => import('../views/user/Tokens.vue')
      }
    ]
  },
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
