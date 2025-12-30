<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100">
    <!-- Hero Section -->
    <header class="relative overflow-hidden bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 text-white">
      <div class="absolute inset-0 bg-black/10"></div>
      <div class="relative mx-auto max-w-7xl px-6 py-20 text-center md:px-12 md:py-28">
        <h1 class="mb-6 text-4xl font-bold md:text-5xl lg:text-6xl">
          InspireEd 科创教育平台
        </h1>
        <p class="mx-auto mb-8 max-w-2xl text-lg md:text-xl text-white/90">
          探索前沿科技，培养创新思维，开启未来教育之旅
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <RouterLink
            to="/login"
            class="rounded-full bg-white px-8 py-3 text-emerald-600 font-semibold shadow-lg transition-all hover:scale-105 hover:shadow-xl"
          >
            立即开始
          </RouterLink>
          <RouterLink
            to="/subjects/computer/courses"
            class="rounded-full border-2 border-white px-8 py-3 font-semibold transition-all hover:bg-white/10"
          >
            浏览课程
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Featured Courses Section -->
    <main class="mx-auto max-w-7xl px-6 py-16 md:px-12">
      <!-- Section Header -->
      <div class="mb-12 text-center">
        <h2 class="mb-4 text-3xl font-bold text-slate-900 md:text-4xl">
          ⭐ 精选科创课程
        </h2>
        <p class="text-lg text-slate-600">
          涵盖人工智能、无人机、机器人、开源硬件、虚拟仿真、3D打印等前沿科技领域
        </p>
      </div>

      <!-- Category Filter -->
      <div class="mb-8 flex flex-wrap justify-center gap-3">
        <button
          v-for="cat in categories"
          :key="cat.value"
          @click="selectedCategory = cat.value"
          :class="[
            'rounded-full px-6 py-2.5 text-sm font-medium transition-all',
            selectedCategory === cat.value
              ? 'bg-emerald-600 text-white shadow-lg'
              : 'bg-white text-slate-700 shadow-md hover:bg-slate-50'
          ]"
        >
          {{ cat.label }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <div
          v-for="index in 8"
          :key="index"
          class="h-64 animate-pulse rounded-2xl bg-gradient-to-br from-slate-200 via-slate-100 to-slate-200"
        ></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-2xl bg-white p-12 text-center shadow-lg">
        <div class="mx-auto mb-4 h-16 w-16 rounded-full bg-orange-50 text-4xl leading-[64px] text-orange-500">
          ⚠️
        </div>
        <h3 class="mb-2 text-xl font-semibold text-slate-900">加载失败</h3>
        <p class="mb-6 text-slate-500">{{ error }}</p>
        <button
          @click="loadFeaturedCourses"
          class="rounded-full bg-emerald-600 px-6 py-2.5 text-white font-medium transition-all hover:bg-emerald-700"
        >
          重试
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="courses.length === 0" class="rounded-2xl bg-white p-12 text-center shadow-lg">
        <div class="mx-auto mb-4 h-16 w-16 rounded-full bg-slate-100 text-4xl leading-[64px] text-slate-400">
          📚
        </div>
        <h3 class="mb-2 text-xl font-semibold text-slate-900">暂无精选课程</h3>
        <p class="text-slate-500">当前分类下还没有精选课程，请稍后再来查看</p>
      </div>

      <!-- Courses Grid -->
      <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        <article
          v-for="course in courses"
          :key="course.id"
          class="group relative overflow-hidden rounded-2xl bg-white shadow-lg transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl"
        >
          <RouterLink
            :to="{ name: 'CourseOverview', params: { courseId: course.id } }"
            class="flex h-full flex-col focus:outline-none"
          >
            <!-- Course Header -->
            <div class="relative p-6 text-white bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500">
              <div class="mb-3 flex items-center justify-between">
                <div class="inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-xs font-medium uppercase tracking-wide">
                  <span class="text-base">⭐</span>
                  <span>精选课程</span>
                </div>
                <span
                  v-if="course.category"
                  class="rounded-full bg-white/20 px-2.5 py-1 text-xs font-medium"
                >
                  {{ getCategoryLabel(course.category) }}
                </span>
              </div>
              <h3 class="text-2xl font-semibold leading-snug line-clamp-2">
                {{ course.name }}
              </h3>
              <p v-if="course.description" class="mt-2 text-sm text-white/90 line-clamp-2">
                {{ course.description }}
              </p>
            </div>

            <!-- Course Info -->
            <div class="flex flex-1 flex-col justify-between gap-4 bg-white p-6">
              <div class="space-y-3">
                <div v-if="course.subject" class="flex items-center gap-2 text-sm">
                  <span class="text-slate-400">学科</span>
                  <span class="font-medium text-slate-700">{{ course.subject.name }}</span>
                </div>
                <div v-if="course.grade" class="flex items-center gap-2 text-sm">
                  <span class="text-slate-400">适用年级</span>
                  <span class="font-medium text-slate-700">{{ course.grade.name }}</span>
                </div>
                <div v-if="course.code" class="flex items-center gap-2 text-sm">
                  <span class="text-slate-400">课程编码</span>
                  <span class="font-mono text-slate-700">{{ course.code }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between border-t border-slate-100 pt-4 text-sm font-medium text-emerald-600">
                <span>查看课程详情</span>
                <span class="transition-transform duration-300 group-hover:translate-x-1">→</span>
              </div>
            </div>
          </RouterLink>
        </article>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import publicCurriculumService from '@/services/publicCurriculum'
import type { Course } from '@/types/curriculum'

// 课程分类定义
const categories = [
  { label: '全部', value: '' },
  { label: '人工智能', value: '人工智能' },
  { label: '无人机', value: '无人机' },
  { label: '轮式机器人', value: '轮式机器人' },
  { label: '开源硬件', value: '开源硬件' },
  { label: '虚拟仿真', value: '虚拟仿真' },
  { label: '3D打印', value: '3D打印' }
]

// 状态
const courses = ref<Course[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedCategory = ref<string>('')

// 获取分类标签
const getCategoryLabel = (category: string): string => {
  const categoryMap: Record<string, string> = {
    'ai': '人工智能',
    'artificial_intelligence': '人工智能',
    '人工智能': '人工智能',
    'drone': '无人机',
    'uav': '无人机',
    '无人机': '无人机',
    'wheeled_robot': '轮式机器人',
    'robot': '轮式机器人',
    '轮式机器人': '轮式机器人',
    '机器人': '轮式机器人',
    'open_hardware': '开源硬件',
    'hardware': '开源硬件',
    '开源硬件': '开源硬件',
    '硬件': '开源硬件',
    'simulation': '虚拟仿真',
    'virtual': '虚拟仿真',
    '虚拟仿真': '虚拟仿真',
    '仿真': '虚拟仿真',
    '3d_printing': '3D打印',
    'printing': '3D打印',
    '3D打印': '3D打印',
    '打印': '3D打印'
  }
  return categoryMap[category] || category
}

// 加载精选课程
const loadFeaturedCourses = async () => {
  loading.value = true
  error.value = null
  
  try {
    const category = selectedCategory.value || undefined
    courses.value = await publicCurriculumService.getFeaturedCourses(category, 20)
  } catch (e: any) {
    error.value = e.message || '加载精选课程失败'
    console.error('Failed to load featured courses:', e)
  } finally {
    loading.value = false
  }
}

// 监听分类变化
watch(selectedCategory, () => {
  loadFeaturedCourses()
})

// 组件挂载时加载
onMounted(() => {
  loadFeaturedCourses()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

