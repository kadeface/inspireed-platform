import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
  },
  {
    path: '/teacher',
    name: 'Teacher',
    component: () => import('../pages/Teacher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/teacher/lesson/:id',
    name: 'TeacherLessonEdit',
    component: () => import('../pages/Teacher/LessonEditor.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/student',
    name: 'Student',
    component: () => import('../pages/Student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/lesson/:id',
    name: 'StudentLessonView',
    component: () => import('../pages/Student/LessonView.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: () => import('../pages/Student/Profile.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/researcher',
    name: 'Researcher',
    component: () => import('../pages/Researcher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'researcher' },
  },
  {
    path: '/admin/curriculum',
    name: 'AdminCurriculum',
    component: () => import('../pages/Admin/CurriculumManagement.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router

