<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 overflow-y-auto"
    @click.self="handleClose"
  >
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="handleClose"></div>

    <div class="flex min-h-full items-center justify-center p-4">
      <div class="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <!-- 头部 -->
        <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between flex-shrink-0">
          <h3 class="text-xl font-semibold text-gray-900">选择模板</h3>
          <button @click="handleClose" class="text-gray-400 hover:text-gray-500">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 内容 -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="template in templates"
              :key="template.id"
              class="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-all cursor-pointer"
              :class="{ 'border-purple-500 bg-purple-50': selectedTemplate?.id === template.id }"
              @click="selectedTemplate = template"
            >
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span class="text-2xl">{{ template.icon }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-medium text-gray-900 mb-1">{{ template.name }}</h4>
                  <p class="text-sm text-gray-500 mb-2">{{ template.description }}</p>
                  <div class="flex gap-2">
                    <button
                      @click.stop="previewTemplate(template)"
                      class="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      预览
                    </button>
                    <span class="text-xs text-gray-400">{{ template.category }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部 -->
        <div class="px-6 py-4 bg-gray-50 flex justify-end gap-3 flex-shrink-0 border-t">
          <button
            @click="handleClose"
            class="px-4 py-2 border rounded-lg hover:bg-gray-100"
          >
            取消
          </button>
          <button
            @click="handleSelect"
            :disabled="!selectedTemplate"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            使用此模板
          </button>
        </div>
      </div>
    </div>

    <!-- 预览模态框 -->
    <div
      v-if="previewTemplateData"
      class="fixed inset-0 z-[60] overflow-y-auto"
      @click.self="previewTemplateData = null"
    >
      <div class="fixed inset-0 bg-gray-900 bg-opacity-75" @click="previewTemplateData = null"></div>
      <div class="flex min-h-full items-center justify-center p-4">
        <div class="relative bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
          <div class="px-6 pt-6 pb-4 border-b flex items-center justify-between flex-shrink-0">
            <h3 class="text-xl font-semibold text-gray-900">预览：{{ previewTemplateData.name }}</h3>
            <button @click="previewTemplateData = null" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-hidden">
            <iframe
              :src="previewTemplateData.url"
              class="w-full h-full border-0"
              style="min-height: 500px;"
            ></iframe>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Template {
  id: string
  name: string
  description: string
  icon: string
  category: string
  path: string
}

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
  select: [template: Template]
}>()

const selectedTemplate = ref<Template | null>(null)
const previewTemplateData = ref<{ name: string; url: string } | null>(null)

const templates: Template[] = [
  {
    id: 'base',
    name: '基础模板',
    description: '包含基础样式和交互框架的通用模板',
    icon: '📄',
    category: '通用',
    path: '/templates/interactive-base.html'
  },
  {
    id: 'multiplication',
    name: '乘法口诀可视化',
    description: '交互式乘法口诀表，点击查看结果',
    icon: '🔢',
    category: '计算类/速算技巧',
    path: '/templates/knowledge-points/multiplication-table.html'
  },
  {
    id: 'geometry',
    name: '图形认知互动',
    description: '认识基本图形，点击了解图形特点',
    icon: '🔷',
    category: '几何类/图形认知',
    path: '/templates/knowledge-points/geometry-shapes.html'
  },
  {
    id: 'calculation',
    name: '速算练习',
    description: '随机生成计算题，练习速算能力',
    icon: '⚡',
    category: '计算类/速算技巧',
    path: '/templates/knowledge-points/calculation-practice.html'
  }
]

const handleClose = () => {
  selectedTemplate.value = null
  emit('close')
}

const handleSelect = () => {
  if (selectedTemplate.value) {
    emit('select', selectedTemplate.value)
    handleClose()
  }
}

const previewTemplate = async (template: Template) => {
  // 获取模板内容
  try {
    const response = await fetch(template.path)
    if (response.ok) {
      const html = await response.text()
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      previewTemplateData.value = {
        name: template.name,
        url: url
      }
    } else {
      alert('无法加载模板预览')
    }
  } catch (error) {
    console.error('Failed to load template:', error)
    alert('加载模板失败')
  }
}

// 清理预览URL
const cleanupPreview = () => {
  if (previewTemplateData.value) {
    URL.revokeObjectURL(previewTemplateData.value.url)
  }
}

// 监听组件关闭，清理资源
watch(() => props.isOpen, (isOpen) => {
  if (!isOpen) {
    cleanupPreview()
  }
})
</script>

<style scoped>
/* 下拉选项样式 */
select option {
  background-color: white;
  color: rgb(17, 24, 39);
}
</style>
