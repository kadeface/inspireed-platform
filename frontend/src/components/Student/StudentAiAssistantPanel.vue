<template>
  <div class="flex h-full flex-col">
    <header class="border-b border-gray-200 bg-white/80 backdrop-blur-sm px-5 py-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-emerald-600">
            学习助手
          </p>
          <h2 class="mt-1 text-lg font-semibold text-gray-900">AI 学习教练</h2>
        </div>
        <span
          v-if="progress !== undefined"
          class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 border border-emerald-100"
        >
          学习进度 {{ progress }}%
        </span>
      </div>
      <p class="mt-2 text-xs text-gray-600">
        根据当前课程，为你整理知识点、练习建议和复习提示。
      </p>
    </header>

    <main class="flex-1 overflow-y-auto px-5 py-4 bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
      <!-- 标签页导航 -->
      <div class="mb-4 flex gap-2 border-b border-gray-200">
        <button
          type="button"
          :class="[
            'px-4 py-2 text-sm font-medium transition-colors',
            activeTab === 'assistant'
              ? 'border-b-2 border-emerald-500 text-emerald-600'
              : 'text-gray-600 hover:text-emerald-600'
          ]"
          @click="activeTab = 'assistant'"
        >
          学习助手
        </button>
        <button
          type="button"
          :class="[
            'px-4 py-2 text-sm font-medium transition-colors',
            activeTab === 'resources'
              ? 'border-b-2 border-emerald-500 text-emerald-600'
              : 'text-gray-600 hover:text-emerald-600'
          ]"
          @click="activeTab = 'resources'"
        >
          AI资源链接
        </button>
      </div>

      <!-- 学习助手标签页 -->
      <div v-show="activeTab === 'assistant'" class="space-y-5">
        <section class="rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg">
          <h3 class="text-sm font-semibold text-gray-900">课程概览</h3>
          <p class="mt-1 text-xs text-gray-600">
            {{ lessonTitle || '未命名课程' }}
          </p>
          <ul v-if="outlineItems.length" class="mt-3 space-y-1 text-xs text-gray-700">
            <li v-for="(item, index) in outlineItems" :key="index" class="flex gap-2">
              <span class="mt-0.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-emerald-500"></span>
              <span>{{ item }}</span>
            </li>
          </ul>
          <p v-else class="mt-3 text-xs text-gray-500">
            暂无结构概览，AI 将根据标题提供通用建议。
          </p>
        </section>

        <section class="space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-900">智能推荐提问</h3>
            <button
              type="button"
              class="rounded-full border border-emerald-300 px-3 py-1 text-xs font-medium text-emerald-700 transition hover:bg-emerald-500 hover:text-white hover:border-emerald-500"
              @click="rotatePrompts"
            >
              换一批
            </button>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="prompt in visiblePrompts"
              :key="prompt"
              type="button"
              class="rounded-xl border border-emerald-100 bg-emerald-50/50 px-3 py-1.5 text-left text-xs text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100/70"
              @click="applyPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>
        </section>

        <section class="space-y-2">
          <label class="text-sm font-semibold text-gray-900" for="student-assistant-question">
            想了解什么？
          </label>
          <textarea
            id="student-assistant-question"
            v-model="question"
            rows="4"
            class="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white/80 backdrop-blur-sm"
            placeholder="例如：帮我总结这节课的重点，或推荐复习习题。"
          ></textarea>
        </section>

        <div class="flex items-center justify-between text-xs text-gray-600">
          <p>AI 会结合课程结构与进度给出建议，可一键加入笔记。</p>
          <button
            type="button"
            :disabled="isSubmitting || !canSubmit"
            class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-3 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-emerald-500/40 enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-emerald-500/50 disabled:cursor-not-allowed disabled:opacity-60"
            @click="handleSubmit"
          >
            <svg
              v-if="isSubmitting"
              class="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 0 0-4 4H4z"
              />
            </svg>
            <span>{{ isSubmitting ? '生成中…' : '生成建议' }}</span>
          </button>
        </div>

        <p
          v-if="errorMessage"
          class="rounded-xl border border-red-200 bg-red-50/80 backdrop-blur-sm px-3 py-2 text-xs text-red-700 shadow-sm"
        >
          {{ errorMessage }}
        </p>

        <section v-if="response" class="space-y-3 rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-semibold text-gray-900">助手回答</h3>
            <div class="flex items-center gap-2 text-[11px] text-gray-500">
              <span v-if="response.model_used">模型 {{ response.model_used }}</span>
              <span v-if="response.response_time_ms">
                {{ Math.round(response.response_time_ms) }} ms
              </span>
            </div>
          </div>

          <div class="rounded-xl bg-white/90 backdrop-blur-sm p-3 text-sm text-gray-900 shadow-inner border border-gray-100">
            <MarkdownPreview :content="response.answer" />
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="rounded-full border border-emerald-300 px-3 py-1 text-xs text-emerald-700 transition hover:bg-emerald-500 hover:text-white hover:border-emerald-500"
              @click="copyAnswer"
            >
              复制内容
            </button>
            <button
              type="button"
              class="rounded-full border border-transparent bg-teal-50 px-3 py-1 text-xs text-teal-700 transition hover:bg-teal-100"
              @click="emitAppendNote"
            >
              添加到笔记
            </button>
          </div>

          <div v-if="response.follow_up_questions.length" class="pt-2">
            <h4 class="text-xs font-semibold text-gray-600">续问建议</h4>
            <div class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="item in response.follow_up_questions"
                :key="item"
                type="button"
                class="rounded-full border border-emerald-100 bg-emerald-50/50 px-3 py-1 text-xs text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100/70"
                @click="applyPrompt(item)"
              >
                {{ item }}
              </button>
            </div>
          </div>
        </section>
      </div>

      <!-- AI资源链接标签页 -->
      <div v-show="activeTab === 'resources'" class="space-y-4">
        <section
          v-for="category in aiResourceCategories"
          :key="category.name"
          class="rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg"
        >
          <h3 class="mb-3 text-sm font-semibold text-gray-900">
            {{ category.name }}
          </h3>
          <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <a
              v-for="resource in category.resources"
              :key="resource.name"
              :href="resource.url"
              target="_blank"
              rel="noopener noreferrer"
              class="group flex items-center gap-2 rounded-lg border border-gray-200 bg-white/90 backdrop-blur-sm px-3 py-2 text-xs text-gray-700 transition hover:border-emerald-300 hover:bg-emerald-50/50 hover:text-emerald-700"
            >
              <div class="relative h-5 w-5 flex-shrink-0">
                <img
                  :src="getResourceIcon(resource)"
                  :alt="resource.name"
                  class="h-5 w-5 rounded object-contain"
                  @error="handleImageError($event, resource)"
                />
              </div>
              <span class="truncate">{{ resource.name }}</span>
              <svg
                class="ml-auto h-3 w-3 flex-shrink-0 text-gray-400 group-hover:text-emerald-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'
import assistantService from '@/services/assistant'
import type { AssistantRequest, AssistantResponse } from '@/types/assistant'

interface AiResource {
  name: string
  url: string
  icon?: string
}

interface AiResourceCategory {
  name: string
  resources: AiResource[]
}

const props = defineProps({
  lessonTitle: {
    type: String,
    default: '',
  },
  lessonOutline: {
    type: String,
    default: '',
  },
  progress: {
    type: Number,
    default: undefined,
  },
  lessonId: {
    type: Number,
    default: undefined,
  },
})

const emit = defineEmits<{
  (e: 'append-note', payload: string): void
}>()

const question = ref('')
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const response = ref<AssistantResponse | null>(null)
const promptIndex = ref(0)
const activeTab = ref<'assistant' | 'resources'>('assistant')

const basePrompts = computed(() => [
  '帮我总结当前课程的核心知识点。',
  '根据这节课内容，给我制定一个复习清单。',
  '推荐几个课堂练习或生活中的应用示例。',
  '请列出老师可能会考察的问题。',
  '帮我生成一段自主学习计划，总结要做的事情。',
])

const outlinePrompts = computed(() => {
  if (!props.lessonOutline) return []
  return [
    '结合课程结构，为每个单元写一句要点。',
    '根据课程结构，推荐我在笔记里记录的重点。',
    '请指出课程中最容易混淆的地方，并给出解释。',
  ]
})

const progressPrompts = computed(() => {
  if (props.progress === undefined) return []
  if (props.progress < 50) {
    return [
      '帮我把剩余内容拆成三次学习任务。',
      '请提醒我哪些单元应该优先完成。',
    ]
  }
  if (props.progress >= 90) {
    return [
      '请给我设计一个自测题单。',
      '帮我准备一段课堂分享的总结稿。',
    ]
  }
  return []
})

const allPrompts = computed(() => [
  ...basePrompts.value,
  ...outlinePrompts.value,
  ...progressPrompts.value,
])

const visiblePrompts = computed(() => {
  const prompts = allPrompts.value
  if (prompts.length <= 3) {
    return prompts
  }
  const start = promptIndex.value % prompts.length
  return [
    prompts[start],
    prompts[(start + 1) % prompts.length],
    prompts[(start + 2) % prompts.length],
  ]
})

const outlineItems = computed(() =>
  props.lessonOutline
    ? props.lessonOutline.split('\n').filter((item) => item.trim().length > 0)
    : []
)

const canSubmit = computed(() => question.value.trim().length >= 4)

const aiResourceCategories: AiResourceCategory[] = [
  {
    name: 'AI工具大全',
    resources: [
      { name: 'AI-Bot', url: 'https://ai-bot.cn', icon: 'https://ai-bot.cn/favicon.ico' },
    ],
  },
  {
    name: '知识库',
    resources: [
      { name: 'IMA', url: 'https://ima.qq.com/', icon: 'https://ima.qq.com/favicon.ico' },
      { name: 'Notion AI', url: 'https://www.notion.so/product/ai', icon: 'https://www.notion.so/images/favicon.ico' },
      { name: 'Obsidian', url: 'https://obsidian.md', icon: 'https://obsidian.md/favicon.ico' },
    ],
  },
  {
    name: '大模型',
    resources: [
      { name: 'DeepSeek', url: 'https://www.deepseek.com', icon: 'https://www.deepseek.com/favicon.ico' },
      { name: '文心一言', url: 'https://yiyan.baidu.com', icon: 'https://yiyan.baidu.com/favicon.ico' },
      { name: 'Kimi', url: 'https://kimi.moonshot.cn', icon: 'https://kimi.moonshot.cn/favicon.ico' },
      { name: 'ChatGPT', url: 'https://chat.openai.com', icon: 'https://chat.openai.com/favicon.ico' },
      { name: 'Claude', url: 'https://claude.ai', icon: 'https://claude.ai/favicon.ico' },
      { name: '通义千问', url: 'https://tongyi.aliyun.com', icon: 'https://tongyi.aliyun.com/favicon.ico' },
      { name: '智谱清言', url: 'https://chatglm.cn', icon: 'https://chatglm.cn/favicon.ico' },
      { name: '豆包', url: 'https://www.doubao.com', icon: 'https://www.doubao.com/favicon.ico' },
    ],
  },
  {
    name: '文生图',
    resources: [
      { name: '可灵', url: 'https://app.klingai.com/cn/', icon: 'https://app.klingai.com/favicon.ico' },
      { name: 'Midjourney', url: 'https://www.midjourney.com', icon: 'https://www.midjourney.com/favicon.ico' },
      { name: 'DALL·E', url: 'https://openai.com/dall-e-2', icon: 'https://openai.com/favicon.ico' },
      { name: 'Stable Diffusion', url: 'https://stablediffusionweb.com', icon: 'https://stablediffusionweb.com/favicon.ico' },
      { name: '文心一格', url: 'https://yige.baidu.com', icon: 'https://yige.baidu.com/favicon.ico' },
      { name: '通义万相', url: 'https://tongyi.aliyun.com/wanxiang', icon: 'https://tongyi.aliyun.com/favicon.ico' },
      { name: '6pen', url: 'https://6pen.art', icon: 'https://6pen.art/favicon.ico' },
    ],
  },
  {
    name: '文生视频',
    resources: [
      { name: '即梦', url: 'https://jimeng.jianying.com/ai-tool/home', icon: 'https://jimeng.jianying.com/favicon.ico' },
      { name: '蝉镜', url: 'https://www.chanjing.cc', icon: 'https://www.chanjing.cc/favicon.ico' },
      { name: 'Runway', url: 'https://runwayml.com', icon: 'https://runwayml.com/favicon.ico' },
      { name: 'Pika', url: 'https://pika.art', icon: 'https://pika.art/favicon.ico' },
      { name: 'Sora', url: 'https://openai.com/sora', icon: 'https://openai.com/favicon.ico' },
      { name: 'Stable Video', url: 'https://stability.ai/stable-video', icon: 'https://stability.ai/favicon.ico' },
      { name: '快剪辑', url: 'https://www.kuaijianji.com', icon: 'https://www.kuaijianji.com/favicon.ico' },
    ],
  },
]

function getResourceIcon(resource: AiResource): string {
  if (resource.icon) {
    return resource.icon
  }
  // 如果没有指定图标，从URL提取域名并使用官网自带的favicon
  try {
    const url = new URL(resource.url)
    return `${url.origin}/favicon.ico`
  } catch {
    return ''
  }
}

function handleImageError(event: Event, resource: AiResource) {
  const img = event.target as HTMLImageElement
  // 如果图标加载失败，尝试使用官网自带的favicon
  try {
    const url = new URL(resource.url)
    const faviconUrl = `${url.origin}/favicon.ico`
    // 如果当前src不是favicon.ico，尝试加载favicon.ico
    if (!img.src.endsWith('/favicon.ico')) {
      img.src = faviconUrl
    } else {
      // 如果favicon也加载失败，隐藏图片
      img.style.display = 'none'
    }
  } catch {
    img.style.display = 'none'
  }
}

function applyPrompt(prompt: string) {
  question.value = prompt
}

function rotatePrompts() {
  promptIndex.value += 1
}

async function handleSubmit() {
  if (!canSubmit.value || isSubmitting.value) return

  isSubmitting.value = true
  errorMessage.value = null

  const payload: AssistantRequest = {
    question: question.value.trim(),
    topic: 'study_support',
    lesson_id: props.lessonId,
    context: {
      lesson_outline: props.lessonOutline,
      progress: props.progress,
      recent_lessons: [
        {
          id: props.lessonId ?? 0,
          title: props.lessonTitle || '当前课程',
          status: 'in-progress',
          updated_at: new Date().toISOString(),
        },
      ],
    },
  }

  try {
    response.value = await assistantService.askStudentAssistant(payload)
  } catch (error: any) {
    errorMessage.value = error.message || '生成失败，请稍后重试。'
  } finally {
    isSubmitting.value = false
  }
}

function copyAnswer() {
  if (!response.value?.answer) return
  navigator.clipboard.writeText(response.value.answer).catch(() => {
    errorMessage.value = '复制失败，请手动选择复制。'
  })
}

function emitAppendNote() {
  if (response.value?.answer) {
    emit('append-note', response.value.answer)
  }
}

watch(
  () => props.lessonOutline,
  () => {
    promptIndex.value = 0
  }
)

watch(
  () => props.progress,
  () => {
    promptIndex.value = 0
  }
)
</script>

