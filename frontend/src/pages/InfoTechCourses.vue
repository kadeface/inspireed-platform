<template>
  <div class="min-h-screen bg-slate-50 font-sans selection:bg-emerald-100 selection:text-emerald-900">
    <!-- 顶部导航栏 - 与 Login 一致的玻璃拟态 -->
    <header
      class="fixed top-0 z-50 w-full transition-all duration-300"
      :class="isScrolled ? 'border-b border-slate-200/50 bg-white/80 py-2 shadow-sm backdrop-blur-md' : 'bg-transparent py-4'"
    >
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <RouterLink :to="{ name: 'Home' }" class="group flex cursor-pointer items-center space-x-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 shadow-lg shadow-emerald-500/20 ring-2 ring-white/50 transition-transform duration-300 group-hover:scale-105">
              <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span class="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-900 bg-clip-text text-2xl font-bold tracking-tight text-transparent transition-opacity group-hover:opacity-80">InspireEd</span>
          </RouterLink>
          <RouterLink
            :to="{ name: 'Home' }"
            class="relative inline-flex items-center gap-2 rounded-full border border-slate-100 bg-white px-6 py-2.5 leading-none shadow-sm transition duration-200 hover:bg-slate-50"
          >
            <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            <span class="font-semibold text-slate-700 transition-colors hover:text-emerald-600">返回首页</span>
          </RouterLink>
        </div>
      </div>
    </header>

    <main class="relative pt-24 min-h-screen">
      <!-- Hero：柔和渐变背景 + 标题区，与 Login 一致 -->
      <section class="relative overflow-hidden pb-12 lg:pb-16">
        <div class="pointer-events-none absolute inset-0">
          <div class="absolute -top-20 left-1/2 h-[400px] w-[800px] -translate-x-1/2 rounded-[100%] bg-gradient-to-b from-emerald-50/80 via-teal-50/50 to-transparent blur-3xl -z-10"></div>
          <div class="absolute right-0 top-20 h-96 w-96 rounded-full bg-cyan-100/40 mix-blend-multiply blur-3xl -z-10 animate-blob"></div>
          <div class="animation-delay-2000 absolute left-0 top-40 h-96 w-96 rounded-full bg-emerald-100/40 mix-blend-multiply blur-3xl -z-10 animate-blob"></div>
        </div>
        <div class="relative z-10 mx-auto max-w-7xl px-4 text-center sm:px-6 lg:px-8">
          <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-4 py-1.5 shadow-sm">
            <span class="relative flex h-2 w-2"><span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span><span class="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span></span>
            <span class="text-xs font-bold uppercase tracking-wide text-emerald-800">{{ activeSubject?.name || '课程矩阵' }}</span>
          </div>
          <h1 class="mb-4 text-4xl font-extrabold leading-tight tracking-tight text-slate-900 md:text-5xl lg:text-6xl">
            探索 <span class="bg-gradient-to-r bg-clip-text text-transparent" :class="[theme.cardFrom, theme.cardTo]">{{ activeSubject?.name || '学科' }}</span> 课程体系
          </h1>
          <p class="mx-auto max-w-2xl text-lg text-slate-600 md:text-xl">{{ headerSubtitle }}</p>
        </div>
      </section>

    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-16">
      <section class="mb-10">
        <div class="mb-4 flex items-center justify-between gap-4">
          <h2 class="text-lg font-semibold text-slate-700">学科导航</h2>
          <span v-if="subjects.length > 0" class="text-xs uppercase tracking-wide text-slate-400">点击学科切换课程</span>
        </div>
        <div v-if="loadingSubjects" class="flex flex-wrap justify-center gap-3">
          <div v-for="index in 6" :key="index" class="h-10 w-32 animate-pulse rounded-full bg-slate-200/70"></div>
        </div>
        <div v-else-if="subjectsError" class="rounded-2xl border border-slate-100 bg-white p-10 text-center shadow-lg">
          <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
            <svg class="h-7 w-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
          <h3 class="mt-6 text-xl font-bold text-slate-900">无法加载学科信息</h3>
          <p class="mt-2 text-sm text-slate-500">{{ subjectsError }}</p>
          <button
            type="button"
            class="mt-6 inline-flex cursor-pointer items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-6 py-2.5 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600 hover:shadow-emerald-500/40 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
            @click="retrySubjects"
          >
            重新加载学科
          </button>
        </div>
        <template v-else>
          <div v-if="subjects.length > 0" class="flex flex-wrap justify-center">
            <div class="inline-flex rounded-full border border-slate-200/60 bg-slate-100/80 p-1.5 shadow-inner backdrop-blur-sm">
              <RouterLink
                v-for="subject in subjects"
                :key="subject.id"
                :to="{ name: 'SubjectCourses', params: { subjectCode: subject.code } }"
                class="inline-flex cursor-pointer items-center gap-2 rounded-full px-5 py-2.5 text-sm font-bold transition-all duration-300"
                :class="subject.code === selectedSubjectCode ? activePillClass : inactivePillClass"
              >
                <span>{{ subject.name }}</span>
              </RouterLink>
            </div>
          </div>
          <p v-else class="mt-6 text-center text-sm text-slate-500">暂未开放任何公开学科，敬请期待。</p>
        </template>
      </section>

      <section class="mb-12 flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-2xl font-semibold text-slate-900">
            {{ activeSubject?.name || '课程列表' }}
          </h2>
          <p class="mt-1 text-sm text-slate-500">
            {{ coursesCountLabel }}
          </p>
        </div>
        <div v-if="!loadingCourses && !coursesError" class="flex items-center gap-4 text-sm text-slate-500">
          <div class="flex items-center gap-2 rounded-full bg-white px-4 py-2 shadow-sm">
            <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span>正在更新</span>
          </div>
          <div class="flex items-center gap-2 rounded-full bg-white px-4 py-2 shadow-sm">
            <span class="h-2 w-2 rounded-full bg-slate-300"></span>
            <span>暂未启用</span>
          </div>
        </div>
      </section>

      <section v-if="loadingCourses" class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="index in 3"
          :key="index"
          class="h-56 animate-pulse rounded-2xl bg-gradient-to-br from-slate-200 via-slate-100 to-slate-200"
        ></div>
      </section>

      <section v-else-if="coursesError" class="rounded-2xl border border-slate-100 bg-white p-10 text-center shadow-lg">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
          <svg class="h-7 w-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        </div>
        <h3 class="mt-6 text-xl font-bold text-slate-900">无法加载课程信息</h3>
        <p class="mt-2 text-sm text-slate-500">{{ coursesError }}</p>
        <button
          type="button"
          class="mt-6 inline-flex cursor-pointer items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-6 py-2.5 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600 hover:shadow-emerald-500/40 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
          @click="retryCourses"
        >
          重新加载课程
        </button>
      </section>

      <section v-else-if="courses.length === 0" class="rounded-2xl border border-slate-100 bg-white p-10 text-center shadow-lg">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
          <svg class="h-7 w-7 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>
        </div>
        <h3 class="mt-6 text-xl font-bold text-slate-900">暂时没有 {{ activeSubject?.name || '该学科' }} 课程</h3>
        <p class="mt-2 text-sm text-slate-500">欢迎稍后再来，或联系教研团队了解最新进展。</p>
      </section>

      <section v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="course in courses"
          :key="course.id"
          class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all duration-200 hover:border-emerald-200/80 hover:shadow-xl"
        >
          <RouterLink
            :to="{ name: 'CourseOverview', params: { courseId: course.id } }"
            class="flex h-full cursor-pointer flex-col focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2"
          >
            <!-- 卡片头部：学科渐变 + 无 emoji，用 SVG 图标 -->
            <div :class="['relative overflow-hidden p-6 text-white', 'bg-gradient-to-br', theme.cardFrom, theme.cardTo]">
              <div class="absolute right-0 top-0 h-24 w-24 translate-x-6 -translate-y-6 rounded-full bg-white/10"></div>
              <div class="relative flex items-center gap-2 rounded-full bg-white/20 px-3 py-1.5 text-xs font-bold uppercase tracking-wide">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                <span>{{ activeSubject?.name || '学科课程' }}</span>
              </div>
              <h3 class="relative mt-4 text-xl font-bold leading-snug tracking-tight md:text-2xl">
                {{ course.name }}
              </h3>
              <p class="relative mt-2 text-sm text-white/90 line-clamp-2">
                {{ course.description || defaultCourseDescription }}
              </p>
            </div>
            <!-- 卡片正文：元信息用 SVG 图标，层次更清晰 -->
            <div class="flex flex-1 flex-col justify-between gap-4 border-t border-slate-100 bg-white p-6">
              <div class="space-y-3 text-sm text-slate-600">
                <div class="flex items-center gap-3">
                  <span class="flex h-2 w-2 shrink-0 items-center justify-center rounded-full bg-emerald-500" aria-hidden="true"></span>
                  <span>课程进行中</span>
                </div>
                <div class="flex items-center gap-3">
                  <svg class="h-4 w-4 shrink-0 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" /></svg>
                  <span><span class="text-slate-400">适用年级</span> <span class="font-medium text-slate-700">{{ course.grade?.name || '未指定' }}</span></span>
                </div>
                <div class="flex items-center gap-3">
                  <svg class="h-4 w-4 shrink-0 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" /></svg>
                  <span><span class="text-slate-400">课程编码</span> <span class="font-mono text-slate-700">{{ course.code || '待定' }}</span></span>
                </div>
              </div>
              <div class="flex items-center justify-between border-t border-slate-100 pt-4 text-sm font-semibold text-emerald-600 transition-colors duration-200 group-hover:text-emerald-700">
                <span>查看课程详情</span>
                <svg class="h-5 w-5 transition-transform duration-200 group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
              </div>
            </div>
          </RouterLink>
        </article>
      </section>
    </div>
    </main>

    <!-- Footer：与 Login 一致 + 开发者信息 -->
    <footer class="border-t border-slate-800 bg-slate-900 py-12 text-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col items-center justify-between gap-8 md:flex-row">
          <div class="flex items-center space-x-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
              <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
            </div>
            <span class="text-xl font-bold tracking-tight">InspireEd</span>
          </div>
          <div class="text-sm text-slate-400">© 2025 InspireEd. Evidence-based Learning & Teaching Platform.</div>
        </div>
        <address class="mt-6 not-italic border-t border-slate-700/60 pt-6 text-center text-sm text-slate-400 md:text-left">
          开发者：广东省开平市教师发展中心 廖作东 · 邮箱
          <a
            href="mailto:382241106@qq.com"
            aria-label="发送邮件至 382241106@qq.com"
            class="inline-flex cursor-pointer items-center gap-1.5 text-slate-300 underline decoration-slate-500/60 decoration-1 underline-offset-2 transition-colors duration-200 hover:text-emerald-400 hover:decoration-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 focus-visible:decoration-emerald-400"
          >
            <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            382241106@qq.com
          </a>
        </address>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import publicCurriculumService from '@/services/publicCurriculum'
import type { Course, Subject } from '@/types/curriculum'
import {
  defaultCourseDescription,
  defaultSubjectTheme,
  subjectIntros,
  subjectThemes,
  type SubjectTheme
} from '@/constants/subjectThemes'

const route = useRoute()
const router = useRouter()

const subjects = ref<Subject[]>([])
const courses = ref<Course[]>([])
const selectedSubjectCode = ref('')

const loadingSubjects = ref(true)
const loadingCourses = ref(false)
const subjectsError = ref<string | null>(null)
const coursesError = ref<string | null>(null)
const isScrolled = ref(false)

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

const subjectCodeParam = computed(() => (route.params.subjectCode as string | undefined) ?? '')

const activeSubject = computed(
  () => subjects.value.find(subject => subject.code === selectedSubjectCode.value) ?? null
)

const theme = computed<SubjectTheme>(
  () => subjectThemes[selectedSubjectCode.value] ?? defaultSubjectTheme
)

const headerSubtitle = computed(() => {
  const intro = subjectIntros[selectedSubjectCode.value]
  if (intro) return intro
  if (activeSubject.value?.description) return activeSubject.value.description
  return '探索该学科的结构化课程体系与真实场景项目。'
})

const coursesCountLabel = computed(() => {
  if (!activeSubject.value) return '请选择上方学科查看课程'
  if (loadingCourses.value) return `正在加载 ${activeSubject.value.name} 课程...`
  if (courses.value.length === 0) return `${activeSubject.value.name} 课程暂未发布`
  return `包含 ${courses.value.length} 门${activeSubject.value.name}课程`
})

const activePillClass = computed(
  () =>
    'bg-white shadow-md scale-105 ring-1 ring-black/5 text-slate-800 ' + (theme.value.focusRing || '')
)

const inactivePillClass =
  'text-slate-500 hover:bg-slate-200/50 hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-200'

function extractErrorMessage(err: unknown, fallback: string): string {
  if (err && typeof err === 'object' && 'response' in err) {
    const response = (err as { response?: { data?: { detail?: string } } }).response
    if (response?.data?.detail) {
      return response.data.detail
    }
  }
  if (err instanceof Error && err.message) {
    return err.message
  }
  return fallback
}

async function loadSubjects() {
  loadingSubjects.value = true
  subjectsError.value = null

  try {
    subjects.value = await publicCurriculumService.getSubjects()
  } catch (err: unknown) {
    subjectsError.value = extractErrorMessage(err, '加载学科信息失败，请稍后再试。')
    subjects.value = []
  } finally {
    loadingSubjects.value = false
  }
}

async function loadCoursesBySubject(code: string) {
  loadingCourses.value = true
  coursesError.value = null

  try {
    courses.value = await publicCurriculumService.getCoursesBySubject(code)
  } catch (err: unknown) {
    coursesError.value = extractErrorMessage(err, '加载课程数据失败，请稍后再试。')
    courses.value = []
  } finally {
    loadingCourses.value = false
  }
}

async function syncSubjectFromRoute() {
  const requestedCode = subjectCodeParam.value
  const exists = requestedCode && subjects.value.some(subject => subject.code === requestedCode)
  const fallbackCode = subjects.value[0]?.code

  if (!fallbackCode) {
    selectedSubjectCode.value = ''
    courses.value = []
    loadingCourses.value = false
    return
  }
  const targetCode = exists ? requestedCode : fallbackCode

  if (!exists && requestedCode !== targetCode) {
    await router.replace({ name: 'SubjectCourses', params: { subjectCode: targetCode } })
    return
  }

  if (selectedSubjectCode.value !== targetCode || courses.value.length === 0) {
    selectedSubjectCode.value = targetCode
    await loadCoursesBySubject(targetCode)
  }
}

async function initialize() {
  await loadSubjects()
  if (subjectsError.value) {
    loadingCourses.value = false
    selectedSubjectCode.value = ''
    courses.value = []
    return
  }

  await syncSubjectFromRoute()
}

async function retrySubjects() {
  await initialize()
}

async function retryCourses() {
  if (selectedSubjectCode.value) {
    await loadCoursesBySubject(selectedSubjectCode.value)
  } else {
    await initialize()
  }
}

watch(
  () => subjectCodeParam.value,
  () => {
    if (loadingSubjects.value || subjectsError.value) return
    void syncSubjectFromRoute()
  }
)

onMounted(() => {
  void initialize()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}
@keyframes blob {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
</style>

