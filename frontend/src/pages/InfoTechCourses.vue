<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
    <header :class="['text-white shadow-lg', 'bg-gradient-to-r', theme.headerFrom, theme.headerTo]">
      <div class="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-16 text-center md:px-12">
        <div class="inline-flex items-center justify-center gap-3 self-center rounded-full bg-white/15 px-6 py-2 text-sm font-medium uppercase tracking-wide backdrop-blur">
          <span class="text-lg">{{ theme.emoji }}</span>
          <span>{{ activeSubject?.name || '课程矩阵' }}</span>
        </div>
        <h1 class="text-4xl font-bold md:text-5xl">
          探索 {{ activeSubject?.name || '学科' }} 课程体系
        </h1>
        <p :class="['text-base md:text-lg', theme.accentText]">
          {{ headerSubtitle }}
        </p>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-6 py-12 md:px-12 md:py-16">
      <section class="mb-10">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <h2 class="text-lg font-semibold text-slate-700">学科导航</h2>
            <RouterLink
              :to="{ name: 'Home' }"
              class="inline-flex items-center gap-1.5 rounded-full border border-slate-300 bg-white px-4 py-1.5 text-sm font-medium text-slate-600 transition-all duration-200 hover:border-slate-400 hover:bg-slate-50 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-200"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span>返回首页</span>
            </RouterLink>
          </div>
          <span v-if="subjects.length > 0" class="text-xs uppercase tracking-wide text-slate-400">
            点击任意学科即可查看对应课程
          </span>
        </div>
        <div v-if="loadingSubjects" class="mt-4 flex flex-wrap gap-3">
          <div v-for="index in 6" :key="index" class="h-10 w-32 animate-pulse rounded-full bg-slate-200/70"></div>
        </div>
        <div v-else-if="subjectsError" class="mt-6 rounded-2xl bg-white p-8 text-center shadow-lg">
          <div class="mx-auto h-14 w-14 rounded-full bg-orange-50 text-3xl leading-[56px] text-orange-500">
            ⚠️
          </div>
          <h3 class="mt-6 text-xl font-semibold text-slate-900">无法加载学科信息</h3>
          <p class="mt-2 text-sm text-slate-500">{{ subjectsError }}</p>
          <button
            type="button"
            class="mt-6 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-slate-600 to-slate-700 px-6 py-2 text-sm font-medium text-white shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-slate-300"
            @click="retrySubjects"
          >
            重新加载学科
          </button>
        </div>
        <template v-else>
          <div v-if="subjects.length > 0" class="mt-4 flex flex-wrap gap-3">
            <RouterLink
              v-for="subject in subjects"
              :key="subject.id"
              :to="{ name: 'SubjectCourses', params: { subjectCode: subject.code } }"
              class="group inline-flex items-center gap-2 rounded-full border px-5 py-2 text-sm font-medium transition-all duration-200 focus-visible:outline-none"
              :class="subject.code === selectedSubjectCode ? activePillClass : inactivePillClass"
            >
              <span>{{ subject.name }}</span>
            </RouterLink>
          </div>
          <p v-else class="mt-6 text-sm text-slate-500">
            暂未开放任何公开学科，敬请期待。
          </p>
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

      <section v-else-if="coursesError" class="rounded-2xl bg-white p-10 text-center shadow-lg">
        <div class="mx-auto h-14 w-14 rounded-full bg-orange-50 text-3xl leading-[56px] text-orange-500">
          ⚠️
        </div>
        <h3 class="mt-6 text-xl font-semibold text-slate-900">无法加载课程信息</h3>
        <p class="mt-2 text-sm text-slate-500">{{ coursesError }}</p>
        <button
          type="button"
          class="mt-6 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-2 text-sm font-medium text-white shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-orange-300"
          @click="retryCourses"
        >
          重新加载课程
        </button>
      </section>

      <section v-else-if="courses.length === 0" class="rounded-2xl bg-white p-10 text-center shadow-lg">
        <div class="mx-auto h-14 w-14 rounded-full bg-orange-50 text-3xl leading-[56px] text-orange-500">
          📭
        </div>
        <h3 class="mt-6 text-xl font-semibold text-slate-900">
          暂时没有 {{ activeSubject?.name || '该学科' }} 课程
        </h3>
        <p class="mt-2 text-sm text-slate-500">
          欢迎稍后再来，或联系教研团队了解最新进展。
        </p>
      </section>

      <section v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="course in courses"
          :key="course.id"
          class="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl"
        >
          <RouterLink
            :to="{ name: 'CourseOverview', params: { courseId: course.id } }"
            class="flex h-full flex-col focus:outline-none"
          >
            <div :class="['relative p-6 text-white', 'bg-gradient-to-br', theme.cardFrom, theme.cardTo]">
              <div class="inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-xs font-medium uppercase tracking-wide">
                <span class="text-base">{{ theme.emoji }}</span>
                <span>{{ activeSubject?.name || '学科课程' }}</span>
              </div>
              <h3 class="mt-4 text-2xl font-semibold leading-snug">
                {{ course.name }}
              </h3>
              <p class="mt-2 text-sm text-white/90 line-clamp-2">
                {{ course.description || defaultCourseDescription }}
              </p>
            </div>
            <div class="flex flex-1 flex-col justify-between gap-4 bg-white p-6">
              <div class="space-y-3 text-sm text-slate-500">
                <div class="flex items-center gap-2">
                  <span class="inline-flex h-2 w-2 items-center justify-center rounded-full bg-emerald-500"></span>
                  <span>课程进行中</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400">适用年级</span>
                  <span class="font-medium text-slate-700">
                    {{ course.grade?.name || '未指定' }}
                  </span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400">课程编码</span>
                  <span class="font-mono text-slate-700">{{ course.code || '待定' }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-sm font-medium text-orange-600">
                <span>查看课程详情</span>
                <span class="transition-transform duration-300 group-hover:translate-x-1">→</span>
              </div>
            </div>
          </RouterLink>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
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
    [
      'border-transparent',
      'bg-gradient-to-r',
      theme.value.badgeFrom,
      theme.value.badgeTo,
      'text-white shadow-lg hover:shadow-xl',
      theme.value.focusRing
    ].join(' ')
)

const inactivePillClass =
  'border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:shadow-md focus-visible:ring-2 focus-visible:ring-slate-200'

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
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>

