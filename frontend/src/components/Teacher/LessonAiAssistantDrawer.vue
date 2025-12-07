<template>
  <Transition name="drawer">
    <div v-if="modelValue" class="fixed inset-0 z-50">
      <div
        class="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px]"
        @click="handleClose"
      ></div>

      <aside
        class="absolute right-0 top-0 flex h-full w-full max-w-xl flex-col bg-white/95 backdrop-blur-sm shadow-2xl"
      >
        <header class="relative overflow-hidden border-b border-gray-200 bg-white/80 backdrop-blur-sm px-6 py-5">
          <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-violet-500 to-purple-600"></span>
          <div class="relative flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-violet-600">
                教学共创
              </p>
              <h2 class="mt-1 text-xl font-bold text-gray-900">
                AI 教案助理
              </h2>
              <p class="mt-1 text-sm text-gray-600">
                根据当前教案结构，生成教学目标、活动设计与优化建议。
              </p>
            </div>
            <button
              type="button"
              class="rounded-xl p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2"
              @click="handleClose"
            >
              <span class="sr-only">关闭</span>
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path
                  fill-rule="evenodd"
                  d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10l-4.95-4.95A1 1 0 115.05 3.636L10 8.586z"
                  clip-rule="evenodd"
                />
              </svg>
            </button>
          </div>
        </header>

        <main class="flex-1 overflow-y-auto px-6 py-5">
          <!-- 标签页导航 -->
          <div class="mb-4 inline-flex rounded-xl shadow-sm bg-white/80 backdrop-blur-sm border border-gray-200" role="tablist">
            <button
              type="button"
              :class="[
                'px-5 py-2.5 text-sm font-medium transition-all rounded-l-xl',
                activeTab === 'overview'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                  : 'bg-transparent text-gray-700 hover:bg-gray-50'
              ]"
              @click="activeTab = 'overview'"
            >
              教案概览
            </button>
            <button
              type="button"
              :class="[
                'px-5 py-2.5 text-sm font-medium transition-all rounded-r-xl',
                activeTab === 'resources'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                  : 'bg-transparent text-gray-700 hover:bg-gray-50'
              ]"
              @click="activeTab = 'resources'"
            >
              AI资源链接
            </button>
          </div>

          <!-- 教案概览标签页 -->
          <div v-show="activeTab === 'overview'">
            <section class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg">
              <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-violet-500 to-purple-600"></span>
              <h3 class="relative text-sm font-semibold text-gray-900">教案概览</h3>
              <p class="relative mt-2 text-xs text-gray-600">
                标题：
                <span class="font-medium text-violet-600">
                  {{ lessonTitle || '未命名教案' }}
                </span>
              </p>
              <div v-if="lessonOutline" class="relative mt-3 space-y-2 text-xs text-gray-700">
                <p class="font-semibold text-gray-600">结构要点</p>
                <ul class="list-outside list-disc space-y-1 pl-5">
                  <li v-for="(item, index) in outlineItems" :key="index">
                    {{ item }}
                  </li>
                </ul>
              </div>
              <p v-else class="relative mt-3 text-xs text-gray-500">
                尚未检测到详细结构，AI 将根据标题提供通用建议。
              </p>
            </section>

            <section class="mt-5 space-y-3">
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
            <div class="space-y-3">
              <!-- 基础推荐 -->
              <div>
                <p class="mb-2 text-xs font-medium text-gray-600">基础推荐</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="prompt in visibleBasePrompts"
                    :key="prompt"
                    type="button"
                    class="rounded-xl border border-emerald-100 bg-emerald-50/50 px-3 py-1.5 text-left text-xs text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100/70"
                    @click="applyPrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>
              <!-- 学习科学推荐 -->
              <div>
                <p class="mb-2 text-xs font-medium text-gray-600">学习科学</p>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="prompt in visibleLearningSciencePrompts"
                    :key="prompt"
                    type="button"
                    class="rounded-xl border border-teal-100 bg-teal-50/50 px-3 py-1.5 text-left text-xs text-teal-700 transition hover:border-teal-300 hover:bg-teal-100/70"
                    @click="applyPrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>
            </div>
          </section>

          <section class="mt-5 space-y-2">
            <label class="text-sm font-semibold text-gray-900" for="lesson-assistant-question">
              输入问题或描述需求
            </label>
            <textarea
              id="lesson-assistant-question"
              v-model="question"
              rows="4"
              class="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white/80 backdrop-blur-sm"
              placeholder="例如：帮我为《{{ lessonTitle || '本节课' }}》设计课堂导入活动。"
            ></textarea>
          </section>

          <div class="mt-3 flex items-center justify-between gap-2 text-xs text-gray-600">
            <p>AI 会结合标题与结构，生成大纲、活动或优化建议。</p>
            <button
              type="button"
              :disabled="isSubmitting || !canSubmit"
              class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-emerald-500/40 enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-emerald-500/50 disabled:cursor-not-allowed disabled:opacity-60"
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
            class="mt-3 rounded-xl border border-red-200 bg-red-50/80 backdrop-blur-sm px-3 py-2 text-xs text-red-700 shadow-sm"
          >
            {{ errorMessage }}
          </p>

            <section
              v-if="response"
              class="group relative overflow-hidden mt-5 space-y-3 rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg"
            >
              <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
              <div class="relative flex items-center justify-between">
                <h3 class="text-sm font-semibold text-gray-900">助手回答</h3>
                <div class="flex items-center gap-2 text-[11px] text-gray-500">
                  <span v-if="response.model_used">模型 {{ response.model_used }}</span>
                  <span v-if="response.response_time_ms">
                    {{ Math.round(response.response_time_ms) }} ms
                  </span>
                </div>
              </div>
              <div class="relative rounded-xl bg-white/90 backdrop-blur-sm p-4 text-sm text-gray-900 shadow-inner border border-gray-100">
                <MarkdownPreview :content="response.answer" />
              </div>
              <div class="relative flex flex-wrap gap-2">
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
                  @click="emitInsert"
                >
                  插入到教案
                </button>
              </div>
              <p v-if="copyToast.show" class="relative text-xs text-emerald-600">
                {{ copyToast.message }}
              </p>
            </section>
          </div>

          <!-- AI资源链接标签页 -->
          <div v-show="activeTab === 'resources'" class="space-y-4">
            <section
              v-for="category in aiResourceCategories"
              :key="category.name"
              class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg"
            >
              <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-cyan-500 to-teal-600"></span>
              <h3 class="relative mb-3 text-sm font-semibold text-gray-900">
                {{ category.name }}
              </h3>
              <div class="relative grid grid-cols-1 gap-2 sm:grid-cols-2">
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

        <footer class="border-t border-gray-200 bg-gradient-to-r from-emerald-50/50 via-teal-50/30 to-cyan-50/30 px-6 py-4 text-xs text-gray-600">
          AI 建议仅供参考，请结合课堂实际进行调整。
        </footer>
      </aside>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'
import assistantService from '@/services/assistant'

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
  modelValue: {
    type: Boolean,
    default: false,
  },
  lessonTitle: {
    type: String,
    default: '',
  },
  lessonOutline: {
    type: String,
    default: '',
  },
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'insert', payload: string): void
}>()

const question = ref('')
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const response = ref<any>(null)
const promptIndex = ref(0)
const copyToast = ref({ show: false, message: '' })
const activeTab = ref<'overview' | 'resources'>('overview')

const basePrompts = computed(() => [
  `请根据"${props.lessonTitle || '本节课'}"生成教学目标和达成指标。`,
  '帮我设计一个课堂导入活动，强调学生参与感。',
  '为本课安排三个课堂活动，并给出时间分配建议。',
  '请提供学习评价/作业设计，突出形成性反馈。',
  '给出课后延伸或家校交流建议，支持学生持续实践。',
])

const outlinePrompts = computed(() => {
  if (!props.lessonOutline) {
    return []
  }
  return [
    '结合当前教案结构，优化活动衔接和过渡语。',
    '根据教案单元，提炼每个单元的核心提示语。',
    '请指出教案结构中的薄弱环节，并给出调整方案。',
  ]
})

const learningSciencePrompts = computed(() => [
  '基于布鲁姆分类法，为本课设计从记忆到创造的认知层次活动。',
  '设计苏格拉底式提问序列，引导学生逐步深入思考。',
  '结合费曼学习法，设计让学生用自己的话解释概念的活动。',
  '分析不同学习风格学生的特点，提供差异化教学建议。',
  '基于5E教学模型，优化本课的探索和解释环节。',
  '设计促进学生主动输出的活动，培养元认知能力。',
  '结合最近发展区理论，为本课设计脚手架支持。',
  '基于建构主义理论，设计让学生主动建构知识的活动。',
])

const allPrompts = computed(() => [
  ...basePrompts.value,
  ...outlinePrompts.value,
  ...learningSciencePrompts.value,
])

const visibleBasePrompts = computed(() => {
  const prompts = [...basePrompts.value, ...outlinePrompts.value]
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

const visibleLearningSciencePrompts = computed(() => {
  const prompts = learningSciencePrompts.value
  if (prompts.length <= 4) {
    return prompts
  }
  const start = (promptIndex.value * 2) % prompts.length
  return [
    prompts[start],
    prompts[(start + 1) % prompts.length],
    prompts[(start + 2) % prompts.length],
    prompts[(start + 3) % prompts.length],
  ]
})

const outlineItems = computed(() => {
  return props.lessonOutline
    ? props.lessonOutline.split('\n').filter((item) => item.trim().length > 0)
    : []
})

const canSubmit = computed(() => question.value.trim().length >= 4)

const aiResourceCategories: AiResourceCategory[] = [
  {
    name: 'AI工具大全',
    resources: [
      { name: 'AI-Bot', url: 'https://ai-bot.cn' },
    ],
  },
  {
    name: '知识库',
    resources: [
      { name: 'IMA', url: 'https://ima.qq.com/' },
      { name: 'Notion AI', url: 'https://www.notion.so/product/ai' },
      { name: 'Obsidian', url: 'https://obsidian.md' },
    ],
  },
  {
    name: '大模型',
    resources: [
      { name: 'DeepSeek', url: 'https://www.deepseek.com' },
      { name: '文心一言', url: 'https://yiyan.baidu.com' },
      { name: 'Kimi', url: 'https://kimi.moonshot.cn' },
      { name: 'ChatGPT', url: 'https://chat.openai.com' },
      { name: 'Claude', url: 'https://claude.ai' },
      { name: '通义千问', url: 'https://tongyi.aliyun.com' },
      { name: '智谱清言', url: 'https://chatglm.cn' },
      { name: '豆包', url: 'https://www.doubao.com' },
    ],
  },
  {
    name: '文生图',
    resources: [
      { name: '可灵', url: 'https://app.klingai.com/cn/' },
      { name: 'Midjourney', url: 'https://www.midjourney.com' },
      { name: 'DALL·E', url: 'https://openai.com/dall-e-2' },
      { name: 'Stable Diffusion', url: 'https://stablediffusionweb.com' },
      { name: '文心一格', url: 'https://yige.baidu.com' },
      { name: '通义万相', url: 'https://tongyi.aliyun.com/wanxiang' },
      { name: '6pen', url: 'https://6pen.art' },
    ],
  },
  {
    name: '文生视频',
    resources: [
      { name: '即梦', url: 'https://jimeng.jianying.com/ai-tool/home' },
      { name: '蝉镜', url: 'https://www.chanjing.cc' },
      { name: 'Runway', url: 'https://runwayml.com' },
      { name: 'Pika', url: 'https://pika.art' },
      { name: 'Sora', url: 'https://openai.com/sora' },
      { name: 'Stable Video', url: 'https://stability.ai/stable-video' },
      { name: '快剪辑', url: 'https://www.kuaijianji.com' },
    ],
  },
  {
    name: '文生html',
    resources: [
      { name: '飞象老师', url: 'https://www.feixianglaoshi.com' },
    ],
  },
]

function getResourceIcon(resource: AiResource): string {
  if (resource.icon) {
    return resource.icon
  }
  // 如果没有指定图标，从URL提取域名并使用网站自己的favicon
  try {
    const url = new URL(resource.url)
    return `${url.protocol}//${url.hostname}/favicon.ico`
  } catch {
    return ''
  }
}

function handleImageError(event: Event, resource: AiResource) {
  const img = event.target as HTMLImageElement
  // 如果图标加载失败，尝试使用备用路径
  try {
    const url = new URL(resource.url)
    const hostname = url.hostname
    const protocol = url.protocol
    
    // 如果当前不是 /favicon.ico，尝试使用它
    if (!img.src.includes('/favicon.ico')) {
      img.src = `${protocol}//${hostname}/favicon.ico`
    } else {
      // 如果 favicon.ico 也加载失败，隐藏图片
      img.style.display = 'none'
    }
  } catch {
    img.style.display = 'none'
  }
}

function handleClose() {
  emit('update:modelValue', false)
}

function applyPrompt(prompt: string) {
  question.value = prompt
}

function rotatePrompts() {
  promptIndex.value += 1
}

async function handleSubmit() {
  if (!canSubmit.value || isSubmitting.value) {
    return
  }
  isSubmitting.value = true
  errorMessage.value = null

  try {
    response.value = await assistantService.askTeacherAssistant({
      question: question.value.trim(),
      topic: 'lesson_plan',
      context: {
        lesson_outline: props.lessonOutline,
        recent_lessons: [
          {
            id: 0,
            title: props.lessonTitle || '当前教案',
            status: 'draft',
            updated_at: new Date().toISOString(),
          },
        ],
      },
    })
  } catch (error: any) {
    errorMessage.value = error.message || '生成失败，请稍后重试。'
  } finally {
    isSubmitting.value = false
  }
}

function copyAnswer() {
  if (!response.value?.answer) return
  navigator.clipboard
    .writeText(response.value.answer)
    .then(() => {
      copyToast.value = { show: true, message: '已复制到剪贴板' }
      setTimeout(() => {
        copyToast.value.show = false
      }, 2000)
    })
    .catch(() => {
      copyToast.value = { show: true, message: '复制失败，请手动选择复制' }
      setTimeout(() => {
        copyToast.value.show = false
      }, 2000)
    })
}

function emitInsert() {
  if (response.value?.answer) {
    emit('insert', response.value.answer)
  }
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      question.value = ''
      isSubmitting.value = false
      response.value = null
      errorMessage.value = null
      promptIndex.value = 0
      activeTab.value = 'overview'
    }
  }
)
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-active aside,
.drawer-leave-active aside {
  transition: transform 0.3s cubic-bezier(0.22, 0.61, 0.36, 1);
}

.drawer-enter-from aside,
.drawer-leave-to aside {
  transform: translateX(100%);
}
</style>


