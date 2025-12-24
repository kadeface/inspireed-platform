import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import LessonView from '../pages/Student/LessonView.vue'

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
    meta: { title: '登录 - InspireEd' },
  },
  {
    path: '/subjects/:subjectCode/courses',
    name: 'SubjectCourses',
    component: () => import('../pages/InfoTechCourses.vue'),
    meta: { title: '学科课程 - InspireEd' },
  },
  {
    path: '/courses/info-tech',
    redirect: { name: 'SubjectCourses', params: { subjectCode: 'computer' } },
  },
  {
    path: '/courses/:courseId',
    name: 'CourseOverview',
    component: () => import('../pages/CourseOverview.vue'),
    meta: { title: '课程详情 - InspireEd' },
  },
  {
    path: '/teacher',
    name: 'Teacher',
    component: () => import('../pages/Teacher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '教师工作台 - InspireEd' },
  },
  {
    path: '/teacher/lesson/:id',
    name: 'TeacherLessonEdit',
    component: () => import('../pages/Teacher/LessonEditor.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '编辑教案 - InspireEd' },
  },
  // 教师端 - 问答系统
  {
    path: '/teacher/questions',
    name: 'TeacherQuestions',
    component: () => import('../pages/Teacher/Questions.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '问答系统 - InspireEd' },
  },
  {
    path: '/teacher/questions/:id',
    name: 'TeacherQuestionDetail',
    component: () => import('../pages/Student/QuestionDetail.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '问题详情 - InspireEd' },
  },
  {
    path: '/teacher/questions/:id/answer',
    name: 'TeacherAnswerEditor',
    component: () => import('../pages/Teacher/AnswerEditor.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '编辑回答 - InspireEd' },
  },
  // 教师端 - 学科教研组
  {
    path: '/teacher/subject-groups',
    name: 'TeacherSubjectGroups',
    component: () => import('../pages/Teacher/SubjectGroups.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '学科教研组 - InspireEd' },
  },
  {
    path: '/teacher/subject-groups/:id',
    name: 'TeacherSubjectGroupDetail',
    component: () => import('../pages/Teacher/SubjectGroupDetail.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '教研组详情 - InspireEd' },
  },
  // 教师端 - 资源库
  {
    path: '/teacher/resource-library',
    name: 'TeacherResourceLibrary',
    component: () => import('../pages/Teacher/ResourceLibrary.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '资源库 - InspireEd' },
  },
  // 教师端 - 班级教学助手
  {
    path: '/teacher/class-assistant',
    name: 'TeacherClassAssistant',
    component: () => import('../pages/Teacher/ClassAssistantDashboard.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '班级教学助手 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/attendance',
    name: 'TeacherClassAssistantAttendance',
    component: () => import('../pages/Teacher/ClassAssistantAttendance.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '点名考勤 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/positive-behaviors',
    name: 'TeacherClassAssistantPositiveBehaviors',
    component: () => import('../pages/Teacher/ClassAssistantPositiveBehaviors.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '课堂表现 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/discipline',
    name: 'TeacherClassAssistantDiscipline',
    component: () => import('../pages/Teacher/ClassAssistantDiscipline.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '纪律记录 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/duty',
    name: 'TeacherClassAssistantDuty',
    component: () => import('../pages/Teacher/ClassAssistantDuty.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '值日管理 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/stats',
    name: 'TeacherClassAssistantStats',
    component: () => import('../pages/Teacher/ClassAssistantStats.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '数据统计 - InspireEd' },
  },
  {
    path: '/teacher/class-assistant/:classroomId/members',
    name: 'TeacherClassAssistantMembers',
    component: () => import('../pages/Teacher/ClassAssistantMembers.vue'),
    meta: { requiresAuth: true, role: 'teacher', title: '班级教学助手 - 成员管理 - InspireEd' },
  },
  {
    path: '/student',
    name: 'Student',
    component: () => import('../pages/Student/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'student', title: '学生工作台 - InspireEd' },
  },
  {
    path: '/student/browse',
    name: 'StudentBrowse',
    component: () => import('../pages/Student/BrowseSimulations.vue'),
    meta: { requiresAuth: true, role: 'student', title: '浏览仿真实验 - InspireEd' },
  },
  {
    path: '/student/lesson/:id',
    name: 'StudentLessonView',
    component: LessonView,
    meta: { requiresAuth: true, role: 'student', title: '学习课程 - InspireEd' },
  },
  {
    path: '/student/profile',
    name: 'StudentProfile',
    component: () => import('../pages/Student/Profile.vue'),
    meta: { requiresAuth: true, role: 'student', title: '个人资料 - InspireEd' },
  },
  {
    path: '/student/favorites',
    name: 'StudentFavorites',
    component: () => import('../pages/Student/Favorites.vue'),
    meta: { requiresAuth: true, role: 'student', title: '我的收藏 - InspireEd' },
  },
  {
    path: '/student/learning-paths',
    name: 'StudentLearningPaths',
    component: () => import('../pages/Student/LearningPaths.vue'),
    meta: { requiresAuth: true, role: 'student', title: '学习路径 - InspireEd' },
  },
  // 学生端 - 项目设计
  {
    path: '/student/projects',
    name: 'StudentProjects',
    component: () => import('../pages/Student/ProjectList.vue'),
    meta: { requiresAuth: true, role: 'student', title: '我的项目 - InspireEd' },
  },
  {
    path: '/student/projects/:id',
    name: 'StudentProjectEditor',
    component: () => import('../pages/Student/ProjectEditor.vue'),
    meta: { requiresAuth: true, role: 'student', title: '编辑项目 - InspireEd' },
  },
  // 学生端 - 问答系统
  {
    path: '/student/question/:id',
    name: 'StudentQuestionDetail',
    component: () => import('../pages/Student/QuestionDetail.vue'),
    meta: { requiresAuth: true, role: 'student', title: '问题详情 - InspireEd' },
  },
  {
    path: '/researcher',
    name: 'Researcher',
    component: () => import('../pages/Researcher/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'researcher', title: '研究员工作台 - InspireEd' },
  },
  {
    path: '/researcher/curriculum',
    name: 'ResearcherCurriculum',
    component: () => import('../pages/Researcher/CurriculumManagement.vue'),
    meta: { requiresAuth: true, role: 'researcher', title: '课程管理 - InspireEd' },
  },
  {
    path: '/researcher/lesson/:id',
    name: 'ResearcherLessonView',
    component: () => import('../pages/Teacher/LessonEditor.vue'),
    meta: { requiresAuth: true, role: 'researcher', title: '查看教案 - InspireEd' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../pages/Admin/Dashboard.vue'),
    meta: { requiresAuth: true, role: 'admin', title: '管理员工作台 - InspireEd' },
  },
  {
    path: '/admin/curriculum',
    name: 'AdminCurriculum',
    component: () => import('../pages/Admin/CurriculumManagement.vue'),
    meta: { requiresAuth: true, role: 'admin', title: '课程管理 - InspireEd' },
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('../pages/Admin/UserManagement.vue'),
    meta: { requiresAuth: true, role: 'admin', title: '用户管理 - InspireEd' },
  },
  {
    path: '/admin/organization',
    name: 'AdminOrganization',
    component: () => import('../pages/Admin/OrganizationManagement.vue'),
    meta: { requiresAuth: true, role: 'admin', title: '组织管理 - InspireEd' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('access_token')
  
  // 设置页面标题
  const title = to.meta.title as string
  if (title) {
    document.title = title
  } else {
    document.title = 'InspireEd - 探究式STEM教学系统'
  }
  
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
  
  // 添加错误处理，捕获动态导入失败
  try {
    next()
  } catch (error) {
    console.error('Route navigation error:', error)
    // 如果路由加载失败，尝试重定向到登录页
    if (to.path !== '/login') {
      next('/login')
    } else {
      next(false) // 阻止导航
    }
  }
})

// 添加路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  // 如果是模块加载失败，尝试刷新页面
  if (error.message && error.message.includes('Failed to fetch dynamically imported module')) {
    console.warn('Module import failed, this might be a network issue or build problem')
    // 可以在这里添加重试逻辑或错误提示
  }
})

export default router


