<template>
  <div class="min-h-screen bg-slate-50">
    <header :class="['text-white shadow-lg', 'bg-gradient-to-br', theme.headerFrom, theme.headerTo]">
      <div class="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-16 md:px-12">
        <nav class="flex flex-wrap items-center gap-2 text-sm text-white/80">
          <RouterLink
            v-if="subjectLink"
            :to="subjectLink"
            class="hover:text-white hover:underline"
          >
            {{ course?.subject?.name || '学科课程' }}
          </RouterLink>
          <span v-if="subjectLink">/</span>
          <span class="text-white">{{ course?.name ?? '加载中...' }}</span>
        </nav>
        <div class="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <div class="inline-flex items-center gap-3 rounded-full bg-white/15 px-5 py-2 text-sm font-medium uppercase tracking-wide">
              <span class="text-lg">{{ theme.emoji }}</span>
              <span>{{ course?.subject?.name || '课程详情' }}</span>
            </div>
            <h1 class="mt-5 text-4xl font-bold md:text-5xl">
              {{ course?.name ?? '课程详情' }}
            </h1>
            <p :class="['mt-4 max-w-2xl text-base md:text-lg', theme.accentText]">
              {{ heroDescription }}
            </p>
          </div>
          <div class="flex flex-col gap-3 rounded-2xl bg-white/10 p-6 text-sm md:min-w-[240px]">
            <div class="flex items-center justify-between">
              <span class="text-white/80">学科</span>
              <span class="font-semibold text-white">{{ course?.subject?.name || '未指定' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-white/80">年级</span>
              <span class="font-semibold text-white">{{ course?.grade?.name || '未指定' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-white/80">课程编码</span>
              <span class="font-mono text-white">{{ course?.code || '待定' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-white/80">章节数量</span>
              <span class="font-semibold text-white">{{ course?.total_chapters ?? '--' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-white/80">教案数量</span>
              <span class="font-semibold text-white">{{ course?.total_lessons ?? '--' }}</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-6xl px-6 py-12 md:px-12 md:py-16">
      <section v-if="loading" class="rounded-2xl bg-white p-12 text-center shadow-lg">
        <div class="mx-auto h-14 w-14 animate-spin rounded-full border-4 border-white/30 border-t-white"></div>
        <p class="mt-6 text-sm text-slate-500">正在加载课程详情...</p>
      </section>

      <section v-else-if="error" class="rounded-2xl bg-white p-12 text-center shadow-lg">
        <div class="mx-auto h-14 w-14 rounded-full bg-orange-50 text-3xl leading-[56px] text-orange-500">
          ⚠️
        </div>
        <h2 class="mt-6 text-2xl font-semibold text-slate-900">无法加载课程详情</h2>
        <p class="mt-2 text-sm text-slate-500">{{ error }}</p>
        <div class="mt-6 flex items-center justify-center gap-4">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-2 text-sm font-medium text-white shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-orange-300"
            @click="retry"
          >
            重新加载
          </button>
          <RouterLink
            :to="subjectLink || { name: 'SubjectCourses', params: { subjectCode: 'computer' } }"
            class="text-sm font-medium text-orange-600 hover:text-orange-700 hover:underline"
          >
            返回课程列表
          </RouterLink>
        </div>
      </section>

      <section v-else class="space-y-10">
        <article class="rounded-2xl bg-white p-10 shadow-lg">
          <h2 class="text-2xl font-semibold text-slate-900">课程概览</h2>
          <div class="mt-6 grid gap-6 md:grid-cols-2">
            <div class="rounded-xl border border-slate-100 bg-slate-50/60 p-6">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">核心定位</h3>
              <p class="mt-3 text-sm leading-relaxed text-slate-600">
                {{ course?.description || heroDescription }}
              </p>
            </div>
            <div class="rounded-xl border border-slate-100 bg-slate-50/60 p-6">
              <h3 class="text-sm font-semibold uppercase tracking-wide text-slate-500">学习建议</h3>
              <ul class="mt-3 space-y-2 text-sm text-slate-600">
                <li>· 按章节树逐步推进，理解知识之间的关联。</li>
                <li>· 结合真实项目或实验任务完成阶段性成果。</li>
                <li>· 记录数据与反思，形成可复用的学习档案。</li>
              </ul>
            </div>
          </div>
        </article>

        <article class="rounded-2xl bg-white p-10 shadow-lg">
          <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-2xl font-semibold text-slate-900">章节结构</h2>
              <p class="mt-1 text-sm text-slate-500">
                共 {{ flattenedChapters.length }} 个章节节点，支持多级展开
              </p>
            </div>
            <RouterLink
              v-if="subjectLink"
              :to="subjectLink"
              class="inline-flex items-center gap-2 text-sm font-medium text-orange-600 hover:text-orange-700 hover:underline"
            >
              ← 返回 {{ course?.subject?.name || '课程' }} 列表
            </RouterLink>
          </div>

          <div v-if="flattenedChapters.length" class="mt-6 space-y-3">
            <div
              v-for="item in flattenedChapters"
              :key="item.chapter.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
              :style="{ paddingLeft: `${item.level * 1.5}rem` }"
            >
              <div class="flex items-center justify-between gap-4">
                <div>
                  <h3 class="text-sm font-semibold text-slate-900">
                    {{ item.chapter.name }}
                  </h3>
                  <p v-if="item.chapter.description" class="mt-1 text-xs text-slate-500">
                    {{ item.chapter.description }}
                  </p>
                </div>
                <div class="flex items-center gap-3 text-xs text-slate-400">
                  <span>章节代码: {{ item.chapter.code || '—' }}</span>
                  <span>教案: {{ item.chapter.lesson_count ?? 0 }}</span>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="mt-6 rounded-xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center text-sm text-slate-500">
            暂无章节信息，欢迎稍后再来查看更新。
          </p>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import publicCurriculumService from '@/services/publicCurriculum'
import {
  defaultCourseDescription,
  defaultSubjectTheme,
  subjectIntros,
  subjectThemes,
  type SubjectTheme
} from '@/constants/subjectThemes'
import type { ChapterTreeNode, CourseWithChapters } from '@/types/curriculum'

const route = useRoute()

const loading = ref(true)
const error = ref<string | null>(null)
const course = ref<CourseWithChapters | null>(null)

const courseId = computed(() => Number(route.params.courseId))
const subjectCode = computed(() => course.value?.subject?.code ?? '')

interface ChapterWithLevel {
  chapter: ChapterTreeNode
  level: number
}

const flattenedChapters = computed<ChapterWithLevel[]>(() => {
  if (!course.value) return []
  return flattenChapters(course.value.chapters || [], 0)
})

const theme = computed<SubjectTheme>(() => subjectThemes[subjectCode.value] ?? defaultSubjectTheme)

const heroDescription = computed(() => {
  if (course.value?.description) return course.value.description
  const intro = subjectIntros[subjectCode.value]
  if (intro) return intro
  return defaultCourseDescription
})

const subjectLink = computed(() => {
  if (!subjectCode.value) return null
  return { name: 'SubjectCourses', params: { subjectCode: subjectCode.value } }
})

function flattenChapters(chapters: ChapterTreeNode[], level: number): ChapterWithLevel[] {
  const result: ChapterWithLevel[] = []
  chapters.forEach((chapter) => {
    result.push({ chapter, level })
    if (chapter.children && chapter.children.length > 0) {
      result.push(...flattenChapters(chapter.children, level + 1))
    }
  })
  return result
}

function ensureValidId(id: number): id is number {
  return Number.isFinite(id) && id > 0
}

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

async function loadCourseDetails() {
  const id = courseId.value
  if (!ensureValidId(id)) {
    error.value = '无效的课程编号。'
    loading.value = false
    course.value = null
    return
  }

  loading.value = true
  error.value = null

  try {
    course.value = await publicCurriculumService.getCourseWithChapters(id)
  } catch (err: unknown) {
    course.value = null
    error.value = extractErrorMessage(err, '加载课程信息时出现未知错误，请稍后再试。')
  } finally {
    loading.value = false
  }
}

function retry() {
  void loadCourseDetails()
}

watch(
  () => route.params.courseId,
  () => {
    void loadCourseDetails()
  }
)

onMounted(() => {
  void loadCourseDetails()
})
</script>

