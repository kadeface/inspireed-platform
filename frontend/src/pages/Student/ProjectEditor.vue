<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- 顶部工具栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-30">
      <div class="mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- 左侧：返回按钮 + 标题 -->
          <div class="flex items-center gap-4 flex-1">
            <button
              @click="handle_back"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
              返回
            </button>
            
            <input
              v-model="project_title"
              type="text"
              placeholder="项目标题"
              class="text-lg font-semibold text-gray-900 border-none outline-none bg-transparent flex-1 max-w-md focus:ring-2 focus:ring-emerald-500 rounded px-2"
              @blur="handle_save_title"
            />
          </div>

          <!-- 右侧：操作按钮 -->
          <div class="flex items-center gap-3">
            <!-- 保存状态指示器 -->
            <div class="flex items-center gap-2 text-sm">
              <span v-if="save_status === 'saving'" class="text-gray-500 flex items-center gap-1">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                保存中...
              </span>
              <span v-else-if="save_status === 'saved'" class="text-green-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                已保存
              </span>
              <span v-else-if="save_status === 'error'" class="text-red-600 flex items-center gap-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                保存失败
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主要内容区域 -->
    <main class="flex-1 flex overflow-hidden">
      <!-- 左侧：5E阶段导航 -->
      <aside class="w-64 bg-white border-r border-gray-200 overflow-y-auto">
        <ProjectStageNavigator
          :active_stage="active_stage"
          :completion="project?.completion || { engage: 0, explore: 0, explain: 0, elaborate: 0, evaluate: 0 }"
          @stage_change="handle_stage_change"
        />
      </aside>

      <!-- 中间：Cell编辑区 -->
      <div class="flex-1 overflow-y-auto">
        <div class="max-w-4xl mx-auto px-6 py-8">
          <!-- 项目描述 -->
          <div class="mb-6">
            <textarea
              v-model="project_description"
              placeholder="输入项目描述（可选）"
              rows="2"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              @blur="handle_save_description"
            ></textarea>
          </div>

          <!-- 当前阶段的Cells -->
          <div v-if="current_stage_cells.length === 0" class="bg-white border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="mt-4 text-lg font-medium text-gray-900">开始添加内容</h3>
            <p class="mt-2 text-sm text-gray-600">点击下方按钮添加单元</p>
          </div>

          <!-- Cell列表 -->
          <div class="space-y-4">
            <CellContainer
              v-for="(cell, index) in display_cells"
              :key="cell.id || `cell-${index}`"
              :cell="cell"
              :index="index"
              :editable="true"
              :draggable="false"
              :show-move-buttons="false"
              :compact-mode="false"
              @update="handle_cell_update"
              @delete="handle_delete_cell"
            />
          </div>

          <!-- 添加Cell按钮 -->
          <div class="mt-6 flex justify-center">
            <div class="relative">
              <button
                @click.stop="show_add_menu = !show_add_menu"
                type="button"
                class="flex h-12 w-12 items-center justify-center rounded-full border-2 border-dashed border-gray-300 bg-white text-gray-400 shadow-sm transition-all hover:border-emerald-500 hover:text-emerald-500 hover:shadow-md"
                :class="{ 'border-emerald-500 text-emerald-500': show_add_menu }"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>

              <!-- 添加菜单 -->
              <Transition name="menu">
                <div
                  v-if="show_add_menu"
                  v-click-outside="() => (show_add_menu = false)"
                  class="absolute left-1/2 z-50 mt-3 w-64 max-h-96 overflow-y-auto -translate-x-1/2 transform rounded-xl border border-gray-200 bg-white shadow-2xl"
                  @click.stop
                >
                  <div class="p-3 space-y-1">
                    <button
                      v-for="cell_type in available_cell_types"
                      :key="cell_type.type"
                      @click.stop="handle_add_cell(cell_type.type)"
                      type="button"
                      class="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm hover:bg-blue-50 transition-colors"
                    >
                      <span class="text-xl">{{ cell_type.icon }}</span>
                      <div>
                        <div class="font-medium text-gray-800">{{ cell_type.name }}</div>
                        <div class="text-xs text-gray-500">{{ cell_type.description }}</div>
                      </div>
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：属性面板 -->
      <aside class="w-64 bg-white border-l border-gray-200 overflow-y-auto p-4">
        <div class="space-y-4">
          <div>
            <h3 class="text-sm font-semibold text-gray-700 mb-2">项目信息</h3>
            <div class="space-y-2 text-sm">
              <div>
                <span class="text-gray-600">状态：</span>
                <span :class="status_class">{{ status_label }}</span>
              </div>
              <div>
                <span class="text-gray-600">创建时间：</span>
                <span class="text-gray-900">{{ formatted_created_at }}</span>
              </div>
              <div>
                <span class="text-gray-600">更新时间：</span>
                <span class="text-gray-900">{{ formatted_updated_at }}</span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { v4 as uuidv4 } from 'uuid'
import ProjectStageNavigator from '../../components/Student/ProjectStageNavigator.vue'
import CellContainer from '../../components/Cell/CellContainer.vue'
import { student_project_service } from '../../services/student_project'
import type { StudentProject, ProjectStage, ProjectCell } from '../../types/student_project'
import type { Cell } from '../../types/cell'
import { CellType } from '../../types/cell'
import { useToast } from '@/composables/useToast'

const router = useRouter()
const route = useRoute()
const toast = useToast()

// 状态
const loading = ref(true)
const project = ref<StudentProject | null>(null)
const project_title = ref('')
const project_description = ref('')
const active_stage = ref<ProjectStage>('engage')
const save_status = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const show_add_menu = ref(false)

// 可用的Cell类型列表（按使用频率排序）
const available_cell_types = [
  { type: 'TEXT', name: '文本单元', icon: '📝', description: '富文本编辑器' },
  { type: 'VIDEO', name: '视频单元', icon: '🎥', description: '视频教学内容' },
  { type: 'INTERACTIVE', name: '交互式课件单元', icon: '🎨', description: 'HTML交互式课件' },
  { type: 'BROWSER', name: '浏览器单元', icon: '🌐', description: '嵌入网页内容' },
  { type: 'ACTIVITY', name: '活动单元', icon: '🎯', description: '互动任务、课堂练习' },
  { type: 'CODE', name: '代码单元', icon: '💻', description: 'Python/JavaScript/HTML' },
  { type: 'FLOWCHART', name: '流程图单元', icon: '🗺️', description: '步骤梳理、思维导图' },
  { type: 'SIM', name: '仿真单元', icon: '🎮', description: '3D仿真' },
  { type: 'CHART', name: '图表单元', icon: '📊', description: '数据可视化' },
  { type: 'CONTEST', name: '竞赛单元', icon: '🏆', description: '积分竞赛、排行榜' },
  { type: 'PARAM', name: '参数单元', icon: '⚙️', description: '参数配置' },
]

// 计算属性
const current_stage_cells = computed(() => {
  if (!project.value) return []
  const stage_field = `${active_stage.value}_content` as keyof StudentProject
  return (project.value[stage_field] as ProjectCell[]) || []
})

// 将 ProjectCell 转换为 Cell 格式
function project_cell_to_cell(project_cell: ProjectCell, index: number): Cell {
  const cell_type_lower = project_cell.cell_type.toLowerCase()
  // 使用稳定的后备 ID（基于 stage 和 index），确保同一 cell 总是有相同的 ID
  // 注意：这应该很少被使用，因为所有 cell 在加载时都应该有 id
  const stableId = project_cell.id || `project-cell-${active_stage.value}-${index}`
  const base_cell: any = {
    id: stableId,
    type: cell_type_lower as CellType,
    order: project_cell.order ?? index,
    title: project_cell.title,
    editable: true,
  }

  switch (cell_type_lower) {
    case 'text':
      return {
        ...base_cell,
        type: CellType.TEXT,
        content: {
          html: project_cell.content?.html || project_cell.content?.text || '<p>在此输入文本内容...</p>',
          json: project_cell.content?.json,
          markdown: project_cell.content?.markdown,
          editorMode: project_cell.content?.editorMode || 'html',
        },
      } as Cell

    case 'video':
      return {
        ...base_cell,
        type: CellType.VIDEO,
        content: {
          videoUrl: project_cell.content?.videoUrl || '',
          title: project_cell.content?.title,
          description: project_cell.content?.description,
          duration: project_cell.content?.duration,
          thumbnail: project_cell.content?.thumbnail,
          subtitles: project_cell.content?.subtitles,
          chapters: project_cell.content?.chapters,
        },
        config: project_cell.config || {
          autoplay: false,
          controls: true,
          loop: false,
          muted: false,
        },
      } as Cell

    case 'code':
      return {
        ...base_cell,
        type: CellType.CODE,
        content: {
          code: project_cell.content?.code || '# 在此编写代码\nprint("Hello, World!")',
          language: project_cell.content?.language || 'python',
          output: project_cell.content?.output,
        },
        config: project_cell.config || {
          timeout: 30,
          maxMemory: 100,
          environment: 'jupyterlite',
        },
      } as Cell

    case 'sim':
      return {
        ...base_cell,
        type: CellType.SIM,
        content: {
          type: project_cell.content?.type || 'iframe',
          url: project_cell.content?.url || '',
          phetSim: project_cell.content?.phetSim,
          phetCategory: project_cell.content?.phetCategory,
          hardwareSim: project_cell.content?.hardwareSim,
          hardwarePlatform: project_cell.content?.hardwarePlatform,
          hardwareCategory: project_cell.content?.hardwareCategory,
          config: project_cell.content?.config || {
            width: 800,
            height: 600,
            autoplay: false,
            fullScreen: false,
          },
        },
      } as Cell

    case 'chart':
      return {
        ...base_cell,
        type: CellType.CHART,
        content: {
          chartType: project_cell.content?.chartType || 'bar',
          data: project_cell.content?.data || {},
          options: project_cell.content?.options || {},
        },
      } as Cell

    case 'flowchart':
      return {
        ...base_cell,
        type: CellType.FLOWCHART,
        content: {
          nodes: project_cell.content?.nodes || [],
          edges: project_cell.content?.edges || [],
          style: project_cell.content?.style || { theme: 'light', layoutDirection: 'TB' },
        },
        config: project_cell.config || {
          editable: true,
          showMinimap: false,
        },
      } as Cell

    case 'param':
      return {
        ...base_cell,
        type: CellType.PARAM,
        content: {
          schema: project_cell.content?.schema || {},
          values: project_cell.content?.values || {},
        },
      } as Cell

    case 'contest':
      return {
        ...base_cell,
        type: CellType.CONTEST,
        content: {
          title: project_cell.content?.title || '竞赛任务',
          description: project_cell.content?.description || '',
          rules: project_cell.content?.rules || {},
          leaderboard: project_cell.content?.leaderboard,
        },
      } as Cell

    case 'activity':
      return {
        ...base_cell,
        type: CellType.ACTIVITY,
        content: {
          title: project_cell.content?.title || '新活动',
          description: project_cell.content?.description || '',
          activityType: project_cell.content?.activityType || 'quiz',
          timing: project_cell.content?.timing || { phase: 'in-class' },
          items: project_cell.content?.items || [],
          grading: project_cell.content?.grading || { enabled: true, totalPoints: 100, autoGrade: false },
          submission: project_cell.content?.submission || { allowMultiple: false, showFeedback: 'immediate' },
          display: project_cell.content?.display || { showProgress: true },
        },
        config: project_cell.config || {
          allowOffline: true,
        },
      } as Cell

    case 'browser':
      return {
        ...base_cell,
        type: CellType.BROWSER,
        content: {
          url: project_cell.content?.url || '',
          title: project_cell.content?.title,
          description: project_cell.content?.description,
          thumbnail: project_cell.content?.thumbnail,
        },
        config: project_cell.config || {
          allowFullscreen: true,
          allowNavigation: true,
          showToolbar: false,
          height: '600px',
        },
      } as Cell

    case 'interactive':
      return {
        ...base_cell,
        type: CellType.INTERACTIVE,
        content: {
          asset_id: project_cell.content?.asset_id,
          url: project_cell.content?.url || '',
          html_code: project_cell.content?.html_code,
          title: project_cell.content?.title,
          description: project_cell.content?.description,
          thumbnail: project_cell.content?.thumbnail,
        },
        config: project_cell.config || {
          allowFullscreen: true,
          height: '800px',
        },
      } as Cell

    default:
      return {
        ...base_cell,
        type: CellType.TEXT,
        content: {
          html: '<p>未知单元类型</p>',
        },
      } as Cell
  }
}

// 将 Cell 转换回 ProjectCell 格式
function cell_to_project_cell(cell: Cell): ProjectCell {
  const project_cell: ProjectCell = {
    stage: active_stage.value,
    cell_type: cell.type.toUpperCase(),
    title: cell.title,
    order: cell.order,
    content: {} as any,
    config: (cell as any).config || {},
  }

  switch (cell.type) {
    case CellType.TEXT:
      project_cell.content = {
        html: (cell.content as any).html || '',
        text: (cell.content as any).text || '',
        json: (cell.content as any).json,
        markdown: (cell.content as any).markdown,
        editorMode: (cell.content as any).editorMode || 'html',
      }
      break

    case CellType.VIDEO:
      project_cell.content = {
        videoUrl: (cell.content as any).videoUrl || '',
        title: (cell.content as any).title,
        description: (cell.content as any).description,
        duration: (cell.content as any).duration,
        thumbnail: (cell.content as any).thumbnail,
        subtitles: (cell.content as any).subtitles,
        chapters: (cell.content as any).chapters,
      }
      break

    case CellType.CODE:
      project_cell.content = {
        code: (cell.content as any).code || '',
        language: (cell.content as any).language || 'python',
        output: (cell.content as any).output,
      }
      break

    case CellType.SIM:
      project_cell.content = {
        type: (cell.content as any).type || 'iframe',
        url: (cell.content as any).url || '',
        phetSim: (cell.content as any).phetSim,
        phetCategory: (cell.content as any).phetCategory,
        hardwareSim: (cell.content as any).hardwareSim,
        hardwarePlatform: (cell.content as any).hardwarePlatform,
        hardwareCategory: (cell.content as any).hardwareCategory,
        config: (cell.content as any).config || {
          width: 800,
          height: 600,
          autoplay: false,
          fullScreen: false,
        },
      }
      break

    case CellType.CHART:
      project_cell.content = {
        chartType: (cell.content as any).chartType || 'bar',
        data: (cell.content as any).data || {},
        options: (cell.content as any).options || {},
      }
      break

    case CellType.FLOWCHART:
      project_cell.content = {
        nodes: (cell.content as any).nodes || [],
        edges: (cell.content as any).edges || [],
        style: (cell.content as any).style || { theme: 'light', layoutDirection: 'TB' },
      }
      break

    case CellType.PARAM:
      project_cell.content = {
        schema: (cell.content as any).schema || {},
        values: (cell.content as any).values || {},
      }
      break

    case CellType.CONTEST:
      project_cell.content = {
        title: (cell.content as any).title || '竞赛任务',
        description: (cell.content as any).description || '',
        rules: (cell.content as any).rules || {},
        leaderboard: (cell.content as any).leaderboard,
      }
      break

    case CellType.ACTIVITY:
      project_cell.content = {
        title: (cell.content as any).title || '新活动',
        description: (cell.content as any).description || '',
        activityType: (cell.content as any).activityType || 'quiz',
        timing: (cell.content as any).timing || { phase: 'in-class' },
        items: (cell.content as any).items || [],
        grading: (cell.content as any).grading || { enabled: true, totalPoints: 100, autoGrade: false },
        submission: (cell.content as any).submission || { allowMultiple: false, showFeedback: 'immediate' },
        display: (cell.content as any).display || { showProgress: true },
      }
      break

    case CellType.BROWSER:
      project_cell.content = {
        url: (cell.content as any).url || '',
        title: (cell.content as any).title,
        description: (cell.content as any).description,
        thumbnail: (cell.content as any).thumbnail,
      }
      break

    case CellType.INTERACTIVE:
      project_cell.content = {
        asset_id: (cell.content as any).asset_id,
        url: (cell.content as any).url || '',
        html_code: (cell.content as any).html_code,
        title: (cell.content as any).title,
        description: (cell.content as any).description,
        thumbnail: (cell.content as any).thumbnail,
      }
      break
  }

  // 保留 cell 的 ID（支持数字和字符串类型，如 UUID）
  if (cell.id !== undefined && cell.id !== null) {
    project_cell.id = cell.id as string | number
  }

  return project_cell
}

// 显示用的 Cells（转换为 Cell 格式）
const display_cells = computed(() => {
  return current_stage_cells.value.map((project_cell, index) =>
    project_cell_to_cell(project_cell, index)
  )
})

const status_label = computed(() => {
  if (!project.value) return ''
  const label_map = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成',
    submitted: '已提交',
  }
  return label_map[project.value.status]
})

const status_class = computed(() => {
  if (!project.value) return ''
  const class_map = {
    draft: 'text-gray-600',
    in_progress: 'text-blue-600',
    completed: 'text-green-600',
    submitted: 'text-purple-600',
  }
  return class_map[project.value.status]
})

const formatted_created_at = computed(() => {
  if (!project.value) return ''
  return dayjs(project.value.created_at).format('YYYY-MM-DD HH:mm')
})

const formatted_updated_at = computed(() => {
  if (!project.value) return ''
  return dayjs(project.value.updated_at).format('YYYY-MM-DD HH:mm')
})

// 确保所有 cells 都有稳定的 id（用于避免 ID 查找失败）
function ensure_cell_ids(project_data: StudentProject): void {
  const stages: ProjectStage[] = ['engage', 'explore', 'explain', 'elaborate', 'evaluate']
  
  stages.forEach((stage) => {
    const stage_field = `${stage}_content` as keyof StudentProject
    const cells = (project_data[stage_field] as ProjectCell[]) || []
    
    cells.forEach((cell, index) => {
      // 如果 cell 没有 id，分配一个稳定的 UUID
      if (!cell.id) {
        cell.id = uuidv4()
      }
    })
  })
}

// 加载项目
async function load_project() {
  const project_id = parseInt(route.params.id as string)
  if (!project_id) {
    toast.error('无效的项目ID')
    router.push('/student/projects')
    return
  }

  loading.value = true
  try {
    const data = await student_project_service.fetch_project_by_id(project_id)
    // 确保所有 cells 都有稳定的 id
    ensure_cell_ids(data)
    project.value = data
    project_title.value = data.title
    project_description.value = data.description || ''
  } catch (error: any) {
    console.error('加载项目失败:', error)
    toast.error(error.message || '加载项目失败')
    router.push('/student/projects')
  } finally {
    loading.value = false
  }
}

// 保存项目（自动保存）
let save_timer: ReturnType<typeof setTimeout> | null = null
async function save_project() {
  if (!project.value) return

  save_status.value = 'saving'
  try {
    const update_data: any = {
      title: project_title.value,
      description: project_description.value,
    }

    // 更新当前阶段的内容
    const stage_field = `${active_stage.value}_content` as keyof StudentProject
    update_data[stage_field] = current_stage_cells.value

    await student_project_service.update_project(project.value.id, update_data)
    save_status.value = 'saved'
    
    // 重新加载项目以获取最新数据
    await load_project()
    
    // 3秒后重置状态
    setTimeout(() => {
      if (save_status.value === 'saved') {
        save_status.value = 'idle'
      }
    }, 3000)
  } catch (error: any) {
    console.error('保存项目失败:', error)
    save_status.value = 'error'
    toast.error(error.message || '保存项目失败')
  }
}

// 防抖保存
function debounced_save() {
  if (save_timer) {
    clearTimeout(save_timer)
  }
  save_timer = setTimeout(() => {
    save_project()
  }, 2000)
}

// 处理函数
function handle_back() {
  router.push('/student/projects')
}

function handle_stage_change(stage: ProjectStage) {
  active_stage.value = stage
}

function handle_save_title() {
  if (project.value && project_title.value !== project.value.title) {
    debounced_save()
  }
}

function handle_save_description() {
  if (project.value && project_description.value !== (project.value.description || '')) {
    debounced_save()
  }
}

function handle_add_cell(cell_type: string) {
  if (!project.value) {
    toast.error('项目未加载，请稍候再试')
    return
  }

  const cell_type_lower = cell_type.toLowerCase()

  // 根据类型创建默认内容
  let default_content: any = {}
  const cell_type_name_map: Record<string, string> = {
    'TEXT': '文本',
    'VIDEO': '视频',
    'CODE': '代码',
    'SIM': '仿真',
    'CHART': '图表',
    'FLOWCHART': '流程图',
    'PARAM': '参数',
    'CONTEST': '竞赛',
    'ACTIVITY': '活动',
    'BROWSER': '浏览器',
    'INTERACTIVE': '交互式课件',
  }

  switch (cell_type_lower) {
    case 'text':
      default_content = { html: '<p>在此输入文本内容...</p>', text: '' }
      break
    case 'video':
      default_content = { videoUrl: '', title: '', description: '' }
      break
    case 'code':
      default_content = { code: '# 在此编写代码\nprint("Hello, World!")', language: 'python' }
      break
    case 'sim':
      default_content = {
        type: 'iframe',
        url: '',
        config: { width: 800, height: 600, autoplay: false, fullScreen: false }
      }
      break
    case 'chart':
      default_content = { chartType: 'bar', data: {}, options: {} }
      break
    case 'flowchart':
      default_content = { nodes: [], edges: [], style: { theme: 'light', layoutDirection: 'TB' } }
      break
    case 'param':
      default_content = { schema: {}, values: {} }
      break
    case 'contest':
      default_content = { title: '竞赛任务', description: '在此输入竞赛说明...', rules: {} }
      break
    case 'activity':
      default_content = {
        title: '新活动',
        description: '',
        activityType: 'quiz',
        timing: { phase: 'in-class' },
        items: [],
        grading: { enabled: true, totalPoints: 100, autoGrade: false },
        submission: { allowMultiple: false, showFeedback: 'immediate' },
        display: { showProgress: true },
      }
      break
    case 'browser':
      default_content = { url: '', title: '', description: '' }
      break
    case 'interactive':
      default_content = { url: '', html_code: undefined, title: '', description: '' }
      break
    default:
      default_content = { html: '<p>未知单元类型</p>' }
  }

  const new_cell: ProjectCell = {
    id: uuidv4(),
    stage: active_stage.value,
    cell_type: cell_type,
    title: '',
    content: default_content,
    config: {},
    order: current_stage_cells.value.length,
  }

  const stage_field = `${active_stage.value}_content` as keyof StudentProject
  const current_content = [...(project.value[stage_field] as ProjectCell[] || [])]
  current_content.push(new_cell)
  
  // 使用响应式更新
  if (project.value) {
    project.value = {
      ...project.value,
      [stage_field]: current_content,
    }
  }

  show_add_menu.value = false
  toast.success(`已添加${cell_type_name_map[cell_type] || cell_type}单元`)
  debounced_save()
}

function handle_cell_update(updated_cell: Cell) {
  if (!project.value) return

  const stage_field = `${active_stage.value}_content` as keyof StudentProject
  const current_content = [...(project.value[stage_field] as ProjectCell[] || [])]
  
  // 找到对应的 ProjectCell 并更新
  const index = current_content.findIndex((pc, idx) => {
    const cell = project_cell_to_cell(pc, idx)
    return cell.id === updated_cell.id
  })

  if (index !== -1) {
    // 转换回 ProjectCell 格式
    const updated_project_cell = cell_to_project_cell(updated_cell)
    // 保留原有的 id（如果有）
    if (current_content[index].id) {
      updated_project_cell.id = current_content[index].id
    }
    current_content[index] = updated_project_cell
  } else {
    // 如果找不到，可能是新添加的，直接添加
    current_content.push(cell_to_project_cell(updated_cell))
  }

  // 更新项目
  project.value = {
    ...project.value,
    [stage_field]: current_content,
  }

  debounced_save()
}

function handle_delete_cell(cell_id: string | number) {
  if (!project.value) return
  if (!confirm('确定要删除这个单元吗？')) return

  const stage_field = `${active_stage.value}_content` as keyof StudentProject
  const current_content = [...(project.value[stage_field] as ProjectCell[] || [])]
  
  // 找到对应的索引
  const index = current_content.findIndex((pc, idx) => {
    const cell = project_cell_to_cell(pc, idx)
    return cell.id === cell_id
  })

  if (index !== -1) {
    current_content.splice(index, 1)
    project.value = {
      ...project.value,
      [stage_field]: current_content,
    }
    debounced_save()
  }
}

// 点击外部关闭菜单
const vClickOutside = {
  mounted(el: HTMLElement & { clickOutsideEvent?: (event: Event) => void }, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el: HTMLElement & { clickOutsideEvent?: (event: Event) => void }) {
    if (el.clickOutsideEvent) {
      document.removeEventListener('click', el.clickOutsideEvent)
    }
  },
}

onMounted(() => {
  load_project()
})
</script>

<style scoped>
.menu-enter-active,
.menu-leave-active {
  transition: all 0.2s ease;
}

.menu-enter-from,
.menu-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-10px);
}
</style>