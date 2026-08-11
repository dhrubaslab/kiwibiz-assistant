import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue') },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, roles: ['admin', 'staff'] },
  },
  {
    path: '/staff',
    name: 'staff',
    component: () => import('@/views/StaffView.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/companies',
    name: 'companies',
    component: () => import('@/views/CompaniesView.vue'),
    meta: { requiresAuth: true, roles: ['super_admin'] },
  },
  {
  path: '/companies/:id/edit',
  name: 'company-edit',
  component: () => import('@/views/CompanyEditView.vue'),
  meta: { requiresAuth: true, roles: ['super_admin'] },
},
{
  path: '/company-profile',
  name: 'company-profile',
  component: () => import('@/views/CompanyProfileView.vue'),
  meta: { requiresAuth: true, roles: ['admin', 'staff'] },
},
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

function homeRouteFor(role) {
  return role === 'super_admin' ? { name: 'companies' } : { name: 'dashboard' }
}

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) return { name: 'login' }

  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return homeRouteFor(auth.user?.role)
  }

  if (to.meta.roles && auth.user && !to.meta.roles.includes(auth.user.role)) {
    return homeRouteFor(auth.user.role)
  }
})

export default router