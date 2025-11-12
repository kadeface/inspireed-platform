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
    path: '/subjects/:subjectCode/courses',
    name: 'SubjectCourses',
    component: () => import('../pages/InfoTechCourses.vue'),
  },
  {
    path: '/courses/info-tech',
    redirect: { name: 'SubjectCourses', params: { subjectCode: 'computer' } },
  },
  {
    path: '/courses/:courseId',
    name: 'CourseOverview',
    component: () => import('../pages/CourseOverview.vue'),
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
  // 教师端 - 问答系统
  {
    path: '/teacher/questions',
    name: 'TeacherQuestions',
    component: () => import('../pages/Teacher/Questions.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/teacher/questions/:id',
    name: 'TeacherQuestionDetail',
    component: () => import('../pages/Student/QuestionDetail.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/teacher/questions/:id/answer',
    name: 'TeacherAnswerEditor',
    component: () => import('../pages/Teacher/AnswerEditor.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  // 教师端 - 学科教研组
  {
    path: '/teacher/subject-groups',
    name: 'TeacherSubjectGroups',
    component: () => import('../pages/Teacher/SubjectGroups.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/teacher/subject-groups/:id',
    name: 'TeacherSubjectGroupDetail',
    component: () => import('../pages/Teacher/SubjectGroupDetail.vue'),
    meta: { requiresAuth: true, role: 'teacher' },
  },
  {
    path: '/student',
    name: 'Student',
    component: () => import('../pages/Student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/browse',
    name: 'StudentBrowse',
    component: () => import('../pages/Student/BrowseSimulations.vue'),
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
    path: '/student/favorites',
    name: 'StudentFavorites',
    component: () => import('../pages/Student/Favorites.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/student/learning-paths',
    name: 'StudentLearningPaths',
    component: () => import('../pages/Student/LearningPaths.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  // 学生端 - 问答系统
  {
    path: '/student/question/:id',
    name: 'StudentQuestionDetail',
    component: () => import('../pages/Student/QuestionDetail.vue'),
    meta: { requiresAuth: true, role: 'student' },
  },
  {
    path: '/researcher',
    name: 'Researcher',
    component: () => import('../pages/Researcher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'researcher' },
  },
  {
    path: '/researcher/curriculum',
    name: 'ResearcherCurriculum',
    component: () => import('../pages/Researcher/CurriculumManagement.vue'),
    meta: { requiresAuth: true, role: 'researcher' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../pages/Admin/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/curriculum',
    name: 'AdminCurriculum',
    component: () => import('../pages/Admin/CurriculumManagement.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../pages/Admin/UserManagement.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/organization',
    name: 'AdminOrganization',
    component: () => import('../pages/Admin/OrganizationManagement.vue'),
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
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  // 检查角色权限（如果路由定义了角色要求）
  if (to.meta.role && token) {
    try {
      // 从localStorage获取用户信息（如果存在）
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        const requiredRole = to.meta.role as string
        const userRole = user.role?.toLowerCase()
        
        // 检查角色是否匹配（管理员可以访问所有页面）
        if (userRole !== requiredRole && userRole !== 'admin') {
          // 角色不匹配，根据用户角色重定向到相应首页
          if (userRole === 'student') {
            next('/student')
          } else if (userRole === 'teacher') {
            next('/teacher')
          } else if (userRole === 'researcher') {
            next('/researcher')
          } else {
            next('/login')
          }
          return
        }
      }
    } catch (e) {
      // 解析失败，继续路由，让API来处理权限检查
      console.warn('Failed to parse user info from localStorage:', e)
    }
  }
  
  next()
})

export default router


