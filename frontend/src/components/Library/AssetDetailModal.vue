<template>
  <div
    v-if="isOpen && asset"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="handleClose"></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white rounded-lg shadow-xl max-w-2xl w-full">
        <!-- 头部 -->
        <div class="px-6 pt-6 pb-4 border-b">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900">{{ isEditing ? '编辑资源' : '资源详情' }}</h3>
            <button @click="handleClose" class="text-gray-400 hover:text-gray-500" :disabled="saving">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 内容 -->
        <div class="px-6 py-4 space-y-4">
          <!-- 资源预览 -->
          <div v-if="previewUrl && !isEditingCode" class="rounded-lg border border-gray-200 bg-gray-50 overflow-hidden relative">
            <!-- 全屏按钮 -->
            <button
              v-if="!isEditing"
              @click="showFullscreenPreview = true"
              class="absolute top-2 right-2 z-10 p-2 bg-black/50 hover:bg-black/70 text-white rounded-lg transition-colors"
              title="全屏预览"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>

            <!-- 图片预览 -->
            <div
              v-if="asset.asset_type === 'image'"
              class="flex items-center justify-center bg-black/5 overflow-auto max-h-[420px]"
            >
              <img
                :src="previewUrl"
                :alt="asset.title"
                class="max-h-[420px] w-full object-contain"
              />
            </div>

            <!-- 视频预览 -->
            <div
              v-else-if="asset.asset_type === 'video'"
              class="aspect-video bg-black"
            >
              <video
                :src="previewUrl"
                class="w-full h-full"
                controls
                controlsList="nodownload"
              />
            </div>

            <!-- 音频预览 -->
            <div
              v-else-if="asset.asset_type === 'audio'"
              class="p-4 flex items-center gap-3"
            >
              <span class="text-gray-600 text-sm whitespace-nowrap">音频预览</span>
              <audio :src="previewUrl" controls class="flex-1" />
            </div>

            <!-- PDF / 文档预览 -->
            <div
              v-else-if="asset.asset_type === 'pdf' || asset.asset_type === 'document'"
              class="h-[420px] bg-white overflow-auto"
            >
              <iframe
                :src="previewUrl"
                class="w-full h-full border-0"
              />
            </div>

            <!-- 交互式课件 / 链接预览（通过 iframe 简单嵌入） -->
            <div
              v-else-if="asset.asset_type === 'interactive' || asset.asset_type === 'link'"
              class="h-[420px] bg-white overflow-auto"
            >
              <iframe
                :src="previewUrl"
                class="w-full h-full border-0"
              />
            </div>

            <!-- 其他类型：仅提供打开按钮 -->
            <div v-else class="p-4 flex items-center justify-between gap-3">
              <div class="text-sm text-gray-600">
                <p class="font-medium text-gray-900">暂不支持内嵌预览的文件类型</p>
                <p class="mt-1 text-xs text-gray-500">
                  可以点击右侧按钮在新窗口中打开查看。
                </p>
              </div>
              <a
                :href="previewUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                打开资源
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 3h7m0 0v7m0-7L10 14" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5v14h14" />
                </svg>
              </a>
            </div>
          </div>

          <!-- 编辑模式 -->
          <form v-if="isEditing" @submit.prevent="handleSave" class="space-y-4">
            <!-- 标题 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                资源标题 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="editForm.title"
                type="text"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="请输入资源标题"
              />
            </div>

            <!-- 描述 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">资源描述</label>
              <textarea
                v-model="editForm.description"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="请输入资源描述"
              ></textarea>
            </div>

            <!-- 可见性 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">可见性</label>
              <select
                v-model="editForm.visibility"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option value="teacher_only">仅自己可见</option>
                <option value="school">全校可见</option>
              </select>
            </div>

            <!-- 学科 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">学科分类</label>
              <select
                v-model="editForm.subject_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                @change="handleSubjectChange"
              >
                <option :value="undefined">不分类</option>
                <option
                  v-for="subject in subjects"
                  :key="subject.id"
                  :value="subject.id"
                >
                  {{ subject.name }}
                </option>
              </select>
            </div>

            <!-- 年级 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">年级分类</label>
              <select
                v-model="editForm.grade_id"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
              >
                <option :value="null">不分类（跨年级通用）</option>
                <option
                  v-for="grade in grades"
                  :key="grade.id"
                  :value="grade.id"
                >
                  {{ grade.name }}
                </option>
              </select>
            </div>

            <!-- 知识点分类（仅当选择数学学科时显示） -->
            <div v-if="isMathSubject">
              <label class="block text-sm font-medium text-gray-700 mb-2">知识点分类</label>
              <input
                v-model="editForm.knowledge_point_category"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="例如：计算类/速算技巧"
              />
            </div>

            <!-- 知识点名称（仅当选择数学学科时显示） -->
            <div v-if="isMathSubject">
              <label class="block text-sm font-medium text-gray-700 mb-2">知识点名称</label>
              <input
                v-model="editForm.knowledge_point_name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900"
                placeholder="例如：乘法口诀可视化"
              />
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-3 pt-4 border-t">
              <button
                type="button"
                @click="handleCancelEdit"
                class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                :disabled="saving"
              >
                取消
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="saving"
              >
                {{ saving ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>

          <!-- HTML代码编辑模式 -->
          <div v-if="isEditingCode" class="space-y-4">
            <div v-if="loadingCode" class="flex items-center justify-center py-8">
              <div class="flex flex-col items-center gap-2">
                <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p class="text-sm text-gray-600">正在加载HTML代码...</p>
              </div>
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                HTML代码 <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <textarea
                  v-model="htmlCode"
                  rows="20"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 font-mono text-sm"
                  placeholder="请输入HTML代码..."
                  style="font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace; line-height: 1.5; tab-size: 2;"
                ></textarea>
              </div>
              <p class="mt-2 text-xs text-gray-500">
                修改HTML代码后，点击保存将创建新版本，保留历史版本记录。
              </p>
              <div class="mt-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  版本变更说明（可选）
                </label>
                <input
                  v-model="changeNote"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 text-sm"
                  placeholder="例如：修复了计算错误、添加了新功能等"
                />
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="flex gap-3 pt-4 border-t">
              <button
                type="button"
                @click="handleCancelCodeEdit"
                class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                :disabled="savingCode"
              >
                取消
              </button>
              <button
                type="button"
                @click="handleSaveCode"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="savingCode || !htmlCode.trim()"
              >
                {{ savingCode ? '保存中...' : '保存代码' }}
              </button>
            </div>
          </div>

          <!-- 查看模式 -->
          <template v-else-if="!isEditingCode">
            <!-- 基本信息 -->
            <div>
              <h4 class="text-lg font-medium text-gray-900">{{ asset.title }}</h4>
              <p v-if="asset.description" class="mt-2 text-gray-600">{{ asset.description }}</p>
            </div>

            <!-- 元数据 -->
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">类型：</span>
                <span class="text-gray-900">{{ getAssetTypeName(asset.asset_type) }}</span>
              </div>
              <div v-if="asset.size_bytes">
                <span class="text-gray-500">大小：</span>
                <span class="text-gray-900">{{ formatSize(asset.size_bytes) }}</span>
              </div>
              <div v-if="asset.subject_id && subjectName">
                <span class="text-gray-500">学科：</span>
                <span class="text-gray-900">{{ subjectName }}</span>
              </div>
              <div v-if="asset.grade_id !== undefined && asset.grade_id !== null && gradeName">
                <span class="text-gray-500">年级：</span>
                <span class="text-gray-900">{{ gradeName }}</span>
              </div>
              <div v-else-if="asset.grade_id === null || asset.grade_id === undefined">
                <span class="text-gray-500">年级：</span>
                <span class="text-gray-900">跨年级通用</span>
              </div>
              <div v-if="asset.page_count">
                <span class="text-gray-500">页数：</span>
                <span class="text-gray-900">{{ asset.page_count }} 页</span>
              </div>
              <div>
                <span class="text-gray-500">可见性：</span>
                <span class="text-gray-900">{{ getVisibilityName(asset.visibility) }}</span>
              </div>
              <div v-if="asset.knowledge_point_category">
                <span class="text-gray-500">知识点分类：</span>
                <span class="text-gray-900">{{ asset.knowledge_point_category }}</span>
              </div>
              <div v-if="asset.knowledge_point_name">
                <span class="text-gray-500">知识点名称：</span>
                <span class="text-gray-900">{{ asset.knowledge_point_name }}</span>
              </div>
              <div>
                <span class="text-gray-500">创建时间：</span>
                <span class="text-gray-900">{{ formatDateTime(asset.created_at) }}</span>
              </div>
              <div>
                <span class="text-gray-500">更新时间：</span>
                <span class="text-gray-900">{{ formatDateTime(asset.updated_at) }}</span>
              </div>
              <div v-if="asset.version">
                <span class="text-gray-500">当前版本：</span>
                <span class="text-gray-900 font-medium">v{{ asset.version }}</span>
              </div>
            </div>

            <!-- 版本管理按钮 -->
            <div v-if="isHtmlAsset" class="pt-2 border-t">
              <button
                @click="handleShowVersions"
                class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors"
              >
                📋 查看版本历史
              </button>
            </div>

            <!-- 版本历史列表 -->
            <div v-if="showVersions" class="mt-4 pt-4 border-t">
              <div class="flex items-center justify-between mb-3">
                <h5 class="text-sm font-medium text-gray-900">版本历史</h5>
                <button
                  @click="showVersions = false"
                  class="text-gray-400 hover:text-gray-500 text-sm"
                >
                  收起
                </button>
              </div>
              <div v-if="loadingVersions" class="text-center py-4 text-sm text-gray-500">
                加载中...
              </div>
              <div v-else-if="versions.length === 0" class="text-center py-4 text-sm text-gray-500">
                暂无版本历史
              </div>
              <div v-else class="space-y-2 max-h-64 overflow-y-auto">
                <div
                  v-for="version in versions"
                  :key="version.id"
                  class="p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                  :class="{ 'border-blue-500 bg-blue-50': version.version === asset.version }"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                      <span class="font-medium text-gray-900">v{{ version.version }}</span>
                      <span v-if="version.version === asset.version" class="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">
                        当前版本
                      </span>
                    </div>
                    <span class="text-xs text-gray-500">{{ formatDateTime(version.created_at) }}</span>
                  </div>
                  <div v-if="version.change_note" class="mt-1 text-sm text-gray-600">
                    {{ version.change_note }}
                  </div>
                  <div class="mt-1 text-xs text-gray-500">
                    大小: {{ formatSize(version.size_bytes) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 操作 -->
            <div class="flex gap-3 pt-4 border-t">
              <button
                v-if="isHtmlAsset && !isEditingCode"
                @click="handleEditCode"
                class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                编辑代码
              </button>
              <button
                @click="handleEdit"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                编辑
              </button>
              <button
                @click="handleDelete"
                class="px-4 py-2 border border-red-600 text-red-600 rounded-lg hover:bg-red-50"
              >
                删除
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 全屏预览覆盖层 -->
    <Transition name="fullscreen-fade">
      <div
        v-if="showFullscreenPreview && previewUrl"
        class="fixed inset-0 z-[60] bg-black"
        @click.self="showFullscreenPreview = false"
      >
        <!-- 关闭按钮 -->
        <button
          @click="showFullscreenPreview = false"
          class="absolute top-4 right-4 z-10 p-3 bg-black/50 hover:bg-black/70 text-white rounded-lg transition-colors"
          title="退出全屏 (ESC)"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- 全屏预览内容 -->
        <div class="w-full h-full overflow-y-auto overflow-x-auto p-4">
          <div class="min-h-full flex items-center justify-center">
            <!-- 图片全屏预览 -->
            <div
              v-if="asset?.asset_type === 'image'"
              class="flex items-center justify-center py-4"
            >
              <img
                :src="previewUrl"
                :alt="asset.title"
                class="object-contain"
                style="max-width: 100%; height: auto;"
              />
            </div>

            <!-- 视频全屏预览 -->
            <div
              v-else-if="asset?.asset_type === 'video'"
              class="w-full min-h-full flex items-center justify-center"
            >
              <video
                :src="previewUrl"
                class="max-w-full max-h-full"
                controls
                controlsList="nodownload"
                autoplay
              />
            </div>

            <!-- 音频全屏预览 -->
            <div
              v-else-if="asset?.asset_type === 'audio'"
              class="w-full max-w-2xl px-8"
            >
              <div class="bg-white/10 rounded-lg p-8 backdrop-blur-sm">
                <h3 class="text-white text-xl font-semibold mb-6 text-center">{{ asset?.title }}</h3>
                <audio :src="previewUrl" controls class="w-full" autoplay />
              </div>
            </div>

            <!-- PDF / 文档全屏预览 -->
            <div
              v-else-if="asset?.asset_type === 'pdf' || asset?.asset_type === 'document'"
              class="w-full min-h-full bg-white"
            >
              <iframe
                :src="previewUrl"
                class="w-full h-full border-0 min-h-screen"
              />
            </div>

            <!-- 交互式课件 / 链接全屏预览 -->
            <div
              v-else-if="asset?.asset_type === 'interactive' || asset?.asset_type === 'link'"
              class="w-full min-h-full bg-white"
            >
              <iframe
                :src="previewUrl"
                class="w-full h-full border-0 min-h-screen"
                allowfullscreen
              />
            </div>

            <!-- 其他类型：显示打开链接提示 -->
            <div v-else class="text-center text-white">
              <p class="text-xl mb-4">此类型资源不支持全屏预览</p>
              <a
                :href="previewUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                在新窗口打开
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 3h7m0 0v7m0-7L10 14" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5v14h14" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { libraryService } from '@/services/library'
import { curriculumService } from '@/services/curriculum'
import type { LibraryAssetDetail, LibraryAssetUpdateRequest } from '@/types/library'
import type { Subject, Grade } from '@/types/curriculum'
import { getAssetTypeName, getVisibilityName, formatFileSize } from '@/types/library'
import { getServerBaseUrl } from '@/utils/url'

interface Props {
  isOpen: boolean
  assetId: number | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  updated: []
  deleted: []
}>()

const asset = ref<LibraryAssetDetail | null>(null)
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const subjects = ref<Subject[]>([])
const grades = ref<Grade[]>([])
const showFullscreenPreview = ref(false)
const isEditingCode = ref(false)
const htmlCode = ref('')
const savingCode = ref(false)
const loadingCode = ref(false)
const changeNote = ref('')
const showVersions = ref(false)
const versions = ref<Array<{
  id: number
  asset_id: number
  version: number
  storage_key: string
  public_url?: string
  size_bytes?: number
  sha256?: string
  created_by: number
  change_note?: string
  created_at: string
}>>([])
const loadingVersions = ref(false)

// 编辑表单数据
const editForm = ref<{
  title: string
  description?: string
  visibility: string
  subject_id?: number
  grade_id?: number | null
  knowledge_point_category?: string
  knowledge_point_name?: string
}>({
  title: '',
  description: '',
  visibility: 'teacher_only',
  subject_id: undefined,
  grade_id: null,
  knowledge_point_category: '',
  knowledge_point_name: '',
})

// 判断是否为数学学科
const isMathSubject = computed(() => {
  const mathSubject = subjects.value.find(s => s.name === '数学' || s.name?.includes('数学'))
  return editForm.value.subject_id === mathSubject?.id
})

// 判断是否为HTML资源
const isHtmlAsset = computed(() => {
  return asset.value?.asset_type === 'interactive' && 
         (asset.value?.mime_type === 'text/html' || 
          asset.value?.public_url?.endsWith('.html') ||
          asset.value?.storage_key?.endsWith('.html'))
})

// 资源预览 URL（优先使用 public_url，回退到 thumbnail）
const previewUrl = computed(() => {
  if (!asset.value) return null
  let url = asset.value.public_url || asset.value.thumbnail_url
  if (!url) return null

  // 将相对路径转换为完整 URL（与其他预览组件保持一致）
  if (url.startsWith('/uploads/')) {
    const baseURL = getServerBaseUrl()
    url = `${baseURL}${url}`
  }

  return url
})

// 获取学科名称
const subjectName = computed(() => {
  if (!asset.value?.subject_id) return null
  const subject = subjects.value.find(s => s.id === asset.value?.subject_id)
  return subject?.name || null
})

// 获取年级名称
const gradeName = computed(() => {
  if (asset.value?.grade_id === undefined || asset.value?.grade_id === null) return null
  const grade = grades.value.find(g => g.id === asset.value?.grade_id)
  return grade?.name || null
})

// 加载学科列表
const loadSubjects = async () => {
  try {
    subjects.value = await curriculumService.getSubjects()
  } catch (error) {
    console.error('Failed to load subjects:', error)
  }
}

// 加载年级列表
const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades()
  } catch (error) {
    console.error('Failed to load grades:', error)
  }
}

watch(() => props.assetId, async (newId) => {
  if (newId && props.isOpen) {
    loading.value = true
    try {
      asset.value = await libraryService.getAsset(newId)
      // 重置编辑状态
      isEditing.value = false
    } catch (error) {
      console.error('Failed to load asset:', error)
    } finally {
      loading.value = false
    }
  }
}, { immediate: true })

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    if (subjects.value.length === 0) {
      loadSubjects()
    }
    if (grades.value.length === 0) {
      loadGrades()
    }
  } else {
    // 关闭时重置编辑状态和全屏预览
    isEditing.value = false
    showFullscreenPreview.value = false
    isEditingCode.value = false
    htmlCode.value = ''
    changeNote.value = ''
    showVersions.value = false
    versions.value = []
  }
}, { immediate: true })

const handleClose = () => {
  if (saving.value) return
  isEditing.value = false
  emit('close')
}

const formatSize = (bytes: number) => formatFileSize(bytes)

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleEdit = () => {
  if (!asset.value) return
  
  // 初始化编辑表单
  editForm.value = {
    title: asset.value.title,
    description: asset.value.description || '',
    visibility: asset.value.visibility,
    subject_id: asset.value.subject_id,
    grade_id: asset.value.grade_id ?? null,
    knowledge_point_category: asset.value.knowledge_point_category || '',
    knowledge_point_name: asset.value.knowledge_point_name || '',
  }
  
  isEditing.value = true
}

const handleCancelEdit = () => {
  isEditing.value = false
}

const handleSubjectChange = () => {
  // 当学科改变时，如果不是数学学科，清空知识点数据
  if (!isMathSubject.value) {
    editForm.value.knowledge_point_category = ''
    editForm.value.knowledge_point_name = ''
  }
}

const handleSave = async () => {
  if (!asset.value) return
  
  saving.value = true
  try {
    const updateData: LibraryAssetUpdateRequest = {
      title: editForm.value.title,
      description: editForm.value.description || undefined,
      visibility: editForm.value.visibility as any,
      subject_id: editForm.value.subject_id,
      grade_id: editForm.value.grade_id ?? undefined,
    }
    
    // 只有数学学科才包含知识点信息
    if (isMathSubject.value) {
      updateData.knowledge_point_category = editForm.value.knowledge_point_category || undefined
      updateData.knowledge_point_name = editForm.value.knowledge_point_name || undefined
    } else {
      // 如果不是数学学科，清空知识点信息
      updateData.knowledge_point_category = undefined
      updateData.knowledge_point_name = undefined
    }
    
    // 调用更新API
    asset.value = await libraryService.updateAsset(asset.value.id, updateData)
    
    isEditing.value = false
    emit('updated')
  } catch (error: any) {
    console.error('Update failed:', error)
    alert(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  if (!asset.value) return
  
  if (!confirm(`确定要删除资源"${asset.value.title}"吗？`)) {
    return
  }

  try {
    await libraryService.deleteAsset(asset.value.id)
    emit('deleted')
  } catch (error: any) {
    console.error('Delete failed:', error)
    alert(error.response?.data?.detail || '删除失败')
  }
}

// 处理全屏预览的键盘事件
const handleFullscreenKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && showFullscreenPreview.value) {
    showFullscreenPreview.value = false
  }
}

// 编辑HTML代码
const handleEditCode = async () => {
  if (!asset.value) return
  
  isEditingCode.value = true
  loadingCode.value = true
  
  try {
    // 使用API端点获取文件内容，避免CORS问题
    const result = await libraryService.getAssetContent(asset.value.id)
    htmlCode.value = result.content
  } catch (error: any) {
    console.error('Failed to load HTML code:', error)
    alert(error.response?.data?.detail || error.message || '加载HTML代码失败')
    isEditingCode.value = false
  } finally {
    loadingCode.value = false
  }
}

// 取消代码编辑
const handleCancelCodeEdit = () => {
  isEditingCode.value = false
  htmlCode.value = ''
  changeNote.value = ''
}

// 显示版本历史
const handleShowVersions = async () => {
  if (!asset.value) return
  
  if (showVersions.value) {
    showVersions.value = false
    return
  }
  
  showVersions.value = true
  loadingVersions.value = true
  
  try {
    const result = await libraryService.getAssetVersions(asset.value.id)
    versions.value = result.versions
  } catch (error: any) {
    console.error('Failed to load versions:', error)
    alert(error.response?.data?.detail || error.message || '加载版本历史失败')
  } finally {
    loadingVersions.value = false
  }
}

// 保存HTML代码
const handleSaveCode = async () => {
  if (!asset.value || !htmlCode.value.trim()) return
  
  const newVersion = (asset.value.version || 1) + 1
  if (!confirm(`保存HTML代码将创建版本 ${newVersion}，保留历史版本记录。是否继续？`)) {
    return
  }
  
  savingCode.value = true
  try {
    // 将HTML代码转换为File对象
    const htmlBlob = new Blob([htmlCode.value], { type: 'text/html' })
    const htmlFile = new File([htmlBlob], `${asset.value.title.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}.html`, {
      type: 'text/html'
    })
    
    // 创建新版本（保留历史版本）
    const updatedAsset = await libraryService.createAssetVersion(
      asset.value.id,
      htmlFile,
      changeNote.value || undefined
    )
    
    // 更新资源信息
    asset.value = updatedAsset
    
    isEditingCode.value = false
    htmlCode.value = ''
    changeNote.value = ''
    emit('updated')
    
    alert(`HTML代码已保存！已创建版本 ${newVersion}，历史版本已保留。`)
  } catch (error: any) {
    console.error('Save HTML code failed:', error)
    alert(error.response?.data?.detail || error.message || '保存失败')
  } finally {
    savingCode.value = false
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleFullscreenKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleFullscreenKeydown)
})
</script>

<style scoped>
/* 下拉选项样式 */
select option {
  background-color: white;
  color: rgb(17, 24, 39); /* text-gray-900 */
}

/* 选择框的下拉箭头颜色 */
select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}

/* 全屏预览过渡动画 */
.fullscreen-fade-enter-active,
.fullscreen-fade-leave-active {
  transition: opacity 0.3s ease;
}

.fullscreen-fade-enter-from,
.fullscreen-fade-leave-to {
  opacity: 0;
}

/* 预览区域滚动条样式 */
.overflow-auto::-webkit-scrollbar,
.overflow-y-auto::-webkit-scrollbar,
.overflow-x-auto::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.overflow-auto::-webkit-scrollbar-track,
.overflow-y-auto::-webkit-scrollbar-track,
.overflow-x-auto::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.overflow-auto::-webkit-scrollbar-thumb,
.overflow-y-auto::-webkit-scrollbar-thumb,
.overflow-x-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.overflow-auto::-webkit-scrollbar-thumb:hover,
.overflow-y-auto::-webkit-scrollbar-thumb:hover,
.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.5);
}

/* 全屏预览区域的滚动条样式（黑色背景） */
.fixed.inset-0.bg-black .overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.fixed.inset-0.bg-black .overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
}

.fixed.inset-0.bg-black .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
