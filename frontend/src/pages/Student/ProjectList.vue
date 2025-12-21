<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 头部 -->
    <div class="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">我的项目</h1>
            <p class="text-sm text-gray-600 mt-1">创建和管理您的5E科学学习项目</p>
          </div>
          <button
            @click="handle_create_project"
            class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-medium rounded-lg hover:from-emerald-600 hover:to-teal-600 shadow-md transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            创建项目
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 返回按钮 -->
      <div class="flex items-center justify-between mb-6">
        <button
          @click="router.push('/student')"
          class="flex items-center text-gray-600 hover:text-gray-900"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回
        </button>
      </div>

      <!-- 筛选栏 -->
      <div class="mb-6 flex items-center gap-4">
        <div class="flex items-center gap-2">
          <label class="text-sm font-medium text-gray-700">状态筛选：</label>
          <select
            v-model="selected_status"
            @change="load_projects"
            class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
          >
            <option value="">全部</option>
            <option value="draft">草稿</option>
            <option value="in_progress">进行中</option>
            <option value="completed">已完成</option>
            <option value="submitted">已提交</option>
          </select>
        </div>
        <div class="text-sm text-gray-600">
          共 {{ total }} 个项目
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="i in 6"
          :key="i"
          class="h-64 bg-white rounded-2xl border border-gray-200 animate-pulse"
        ></div>
      </div>

      <!-- 项目列表 -->
      <div v-else-if="projects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ProjectCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
          @edit="handle_edit"
          @delete="handle_delete"
          @view="handle_view"
        />
      </div>

      <!-- 空状态 -->
      <div v-else class="flex flex-col items-center justify-center py-20">
        <div class="text-center">
          <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="1.5"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">还没有项目</h3>
          <p class="mt-2 text-sm text-gray-500">开始创建您的第一个5E科学学习项目吧！</p>
          <button
            @click="handle_create_project"
            class="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-medium rounded-lg hover:from-emerald-600 hover:to-teal-600 shadow-md transition-all"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            创建项目
          </button>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > page_size" class="mt-8 flex items-center justify-center gap-4">
        <button
          @click="handle_prev_page"
          :disabled="page === 1"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一页
        </button>
        <span class="text-sm text-gray-600">
          第 {{ page }} / {{ Math.ceil(total / page_size) }} 页
        </span>
        <button
          @click="handle_next_page"
          :disabled="page * page_size >= total"
          class="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一页
        </button>
      </div>
    </main>

    <!-- 创建项目对话框 -->
    <div
      v-if="show_create_dialog"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="show_create_dialog = false"
    >
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h2 class="text-xl font-bold text-gray-900 mb-4">创建新项目</h2>
        <form @submit.prevent="handle_submit_create">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">项目标题 *</label>
              <input
                v-model="new_project.title"
                type="text"
                required
                placeholder="输入项目标题"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">项目描述</label>
              <textarea
                v-model="new_project.description"
                rows="3"
                placeholder="输入项目描述（可选）"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">项目类型</label>
              <select
                v-model="new_project.project_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="">选择项目类型（可选）</option>
                <option value="scientific_inquiry">科学探究</option>
                <option value="engineering_design">工程设计</option>
                <option value="data_analysis">数据分析</option>
                <option value="integrated_project">综合项目</option>
              </select>
            </div>
          </div>
          <div class="mt-6 flex items-center justify-end gap-3">
            <button
              type="button"
              @click="show_create_dialog = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="creating"
              class="px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg hover:from-emerald-600 hover:to-teal-600 disabled:opacity-50"
            >
              {{ creating ? '创建中...' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProjectCard from '../../components/Student/ProjectCard.vue'
import { student_project_service } from '../../services/student_project'
import type { StudentProject, StudentProjectCreate, ProjectStatus } from '../../types/student_project'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const toast = useToast()

// 状态
const loading = ref(false)
const projects = ref<StudentProject[]>([])
const total = ref(0)
const page = ref(1)
const page_size = ref(12)
const selected_status = ref<ProjectStatus | ''>('')

// 创建对话框
const show_create_dialog = ref(false)
const creating = ref(false)
const new_project = ref<StudentProjectCreate>({
  title: '',
  description: '',
  project_type: '',
})

// 加载项目列表
async function load_projects() {
  loading.value = true
  try {
    const response = await student_project_service.fetch_projects({
      page: page.value,
      page_size: page_size.value,
      status: selected_status.value || undefined,
    })
    projects.value = response.items
    total.value = response.total
  } catch (error: any) {
    console.error('加载项目列表失败:', error)
    toast.error(error.message || '加载项目列表失败')
  } finally {
    loading.value = false
  }
}

// 创建项目
function handle_create_project() {
  new_project.value = {
    title: '',
    description: '',
    project_type: '',
  }
  show_create_dialog.value = true
}

async function handle_submit_create() {
  if (!new_project.value.title.trim()) {
    toast.error('请输入项目标题')
    return
  }

  creating.value = true
  try {
    const project = await student_project_service.create_project(new_project.value)
    toast.success('项目创建成功')
    show_create_dialog.value = false
    // 跳转到编辑器
    router.push(`/student/projects/${project.id}`)
  } catch (error: any) {
    console.error('创建项目失败:', error)
    toast.error(error.message || '创建项目失败')
  } finally {
    creating.value = false
  }
}

// 编辑项目
function handle_edit(project_id: number) {
  router.push(`/student/projects/${project_id}`)
}

// 查看项目
function handle_view(project_id: number) {
  router.push(`/student/projects/${project_id}`)
}

// 删除项目
async function handle_delete(project_id: number) {
  if (!confirm('确定要删除这个项目吗？此操作不可恢复。')) {
    return
  }

  try {
    await student_project_service.delete_project(project_id)
    toast.success('项目已删除')
    load_projects()
  } catch (error: any) {
    console.error('删除项目失败:', error)
    toast.error(error.message || '删除项目失败')
  }
}

// 分页
function handle_prev_page() {
  if (page.value > 1) {
    page.value--
    load_projects()
  }
}

function handle_next_page() {
  if (page.value * page_size.value < total.value) {
    page.value++
    load_projects()
  }
}

onMounted(() => {
  load_projects()
})
</script>

