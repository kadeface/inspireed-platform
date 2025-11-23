<template>
  <Transition name="drawer">
    <div v-if="modelValue" class="fixed inset-0 z-50">
      <div
        class="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px]"
        @click="handleClose"
      ></div>

      <aside
        class="absolute right-0 top-0 flex h-full w-full max-w-xl flex-col bg-white shadow-2xl"
      >
        <header class="flex items-start justify-between gap-4 border-b border-[#E2E6F6] px-6 py-5">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-[#4C6EF5]">
              教学共创
            </p>
            <h2 class="mt-1 text-xl font-semibold text-[#2B2F48]">
              AI 教案助理
            </h2>
            <p class="mt-1 text-sm text-[#6E7590]">
              根据当前教案结构，生成教学目标、活动设计与优化建议。
            </p>
          </div>
          <button
            type="button"
            class="rounded-full p-2 text-[#6E7590] transition hover:bg-[#ECF0FF] hover:text-[#4C6EF5] focus:outline-none focus:ring-2 focus:ring-[#4C6EF5] focus:ring-offset-2"
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
        </header>

        <main class="flex-1 overflow-y-auto px-6 py-5">
          <!-- 标签页导航 -->
          <div class="mb-4 flex gap-2 border-b border-[#E2E6F6]">
            <button
              type="button"
              :class="[
                'px-4 py-2 text-sm font-medium transition-colors',
                activeTab === 'overview'
                  ? 'border-b-2 border-[#4C6EF5] text-[#4C6EF5]'
                  : 'text-[#6E7590] hover:text-[#4C6EF5]'
              ]"
              @click="activeTab = 'overview'"
            >
              教案概览
            </button>
            <button
              type="button"
              :class="[
                'px-4 py-2 text-sm font-medium transition-colors',
                activeTab === 'resources'
                  ? 'border-b-2 border-[#4C6EF5] text-[#4C6EF5]'
                  : 'text-[#6E7590] hover:text-[#4C6EF5]'
              ]"
              @click="activeTab = 'resources'"
            >
              AI资源链接
            </button>
          </div>

          <!-- 教案概览标签页 -->
          <div v-show="activeTab === 'overview'">
            <section class="rounded-2xl border border-[#D9DFF5] bg-[#F7F8FC] p-4">
              <h3 class="text-sm font-semibold text-[#2B2F48]">教案概览</h3>
              <p class="mt-2 text-xs text-[#6E7590]">
                标题：
                <span class="font-medium text-[#4C6EF5]">
                  {{ lessonTitle || '未命名教案' }}
                </span>
              </p>
              <div v-if="lessonOutline" class="mt-3 space-y-2 text-xs text-[#4C568E]">
                <p class="font-semibold text-[#6E7590]">结构要点</p>
                <ul class="list-outside list-disc space-y-1 pl-5">
                  <li v-for="(item, index) in outlineItems" :key="index">
                    {{ item }}
                  </li>
                </ul>
              </div>
              <p v-else class="mt-3 text-xs text-[#8D93AA]">
                尚未检测到详细结构，AI 将根据标题提供通用建议。
              </p>
            </section>

            <section class="mt-5 space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-semibold text-[#2B2F48]">智能推荐提问</h3>
              <button
                type="button"
                class="rounded-full border border-[#4C6EF5] px-3 py-1 text-xs font-medium text-[#4C6EF5] transition hover:bg-[#4C6EF5] hover:text-white"
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
                class="rounded-xl border border-transparent bg-[#EFF2FF] px-3 py-1.5 text-left text-xs text-[#4C6EF5] transition hover:border-[#4C6EF5]"
                @click="applyPrompt(prompt)"
              >
                {{ prompt }}
              </button>
            </div>
          </section>

          <section class="mt-5 space-y-2">
            <label class="text-sm font-semibold text-[#2B2F48]" for="lesson-assistant-question">
              输入问题或描述需求
            </label>
            <textarea
              id="lesson-assistant-question"
              v-model="question"
              rows="4"
              class="w-full resize-none rounded-xl border border-[#D9DFF5] px-4 py-3 text-sm text-[#2B2F48] shadow-sm focus:border-[#4C6EF5] focus:outline-none focus:ring-2 focus:ring-[#C8D4FF]"
              placeholder="例如：帮我为《{{ lessonTitle || '本节课' }}》设计课堂导入活动。"
            ></textarea>
          </section>

          <div class="mt-3 flex items-center justify-between gap-2 text-xs text-[#8D93AA]">
            <p>AI 会结合标题与结构，生成大纲、活动或优化建议。</p>
            <button
              type="button"
              :disabled="isSubmitting || !canSubmit"
              class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] px-4 py-2 text-sm font-semibold text-white shadow transition enabled:hover:shadow-lg enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-[#BFD0FF] disabled:cursor-not-allowed disabled:opacity-50"
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
            class="mt-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600"
          >
            {{ errorMessage }}
          </p>

            <section
              v-if="response"
              class="mt-5 space-y-3 rounded-2xl border border-[#D9DFF5] bg-[#F7F8FC] p-4"
            >
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-semibold text-[#2B2F48]">助手回答</h3>
                <div class="flex items-center gap-2 text-[11px] text-[#8D93AA]">
                  <span v-if="response.model_used">模型 {{ response.model_used }}</span>
                  <span v-if="response.response_time_ms">
                    {{ Math.round(response.response_time_ms) }} ms
                  </span>
                </div>
              </div>
              <div class="rounded-xl bg-white p-4 text-sm text-[#2B2F48] shadow-inner">
                <MarkdownPreview :content="response.answer" />
              </div>
              <div class="flex flex-wrap gap-2">
                <button
                  type="button"
                  class="rounded-full border border-[#4C6EF5] px-3 py-1 text-xs text-[#4C6EF5] transition hover:bg-[#4C6EF5] hover:text-white"
                  @click="copyAnswer"
                >
                  复制内容
                </button>
                <button
                  type="button"
                  class="rounded-full border border-transparent bg-[#4FB5A3]/15 px-3 py-1 text-xs text-[#3A917F] transition hover:bg-[#4FB5A3]/25"
                  @click="emitInsert"
                >
                  插入到教案
                </button>
              </div>
              <p v-if="copyToast.show" class="text-xs text-[#4C6EF5]">
                {{ copyToast.message }}
              </p>
            </section>
          </div>

          <!-- AI资源链接标签页 -->
          <div v-show="activeTab === 'resources'" class="space-y-4">
            <section
              v-for="category in aiResourceCategories"
              :key="category.name"
              class="rounded-2xl border border-[#D9DFF5] bg-[#F7F8FC] p-4"
            >
              <h3 class="mb-3 text-sm font-semibold text-[#2B2F48]">
                {{ category.name }}
              </h3>
              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <a
                  v-for="resource in category.resources"
                  :key="resource.name"
                  :href="resource.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="group flex items-center gap-2 rounded-lg border border-transparent bg-white px-3 py-2 text-xs text-[#4C568E] transition hover:border-[#4C6EF5] hover:bg-[#EFF2FF] hover:text-[#4C6EF5]"
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
                    class="ml-auto h-3 w-3 flex-shrink-0 text-[#8D93AA] group-hover:text-[#4C6EF5]"
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

        <footer class="border-t border-[#E2E6F6] bg-[#F7F8FC] px-6 py-4 text-xs text-[#8D93AA]">
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
  `请根据“${props.lessonTitle || '本节课'}”生成教学目标和达成指标。`,
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

const allPrompts = computed(() => [...basePrompts.value, ...outlinePrompts.value])

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
      { name: 'AI-Bot', url: 'https://ai-bot.cn', icon: 'https://www.google.com/s2/favicons?domain=ai-bot.cn&sz=32' },
    ],
  },
  {
    name: '知识库',
    resources: [
      { name: 'IMA', url: 'https://ima.qq.com/', icon: 'https://www.google.com/s2/favicons?domain=ima.qq.com&sz=32' },
      { name: 'Notion AI', url: 'https://www.notion.so/product/ai', icon: 'https://www.google.com/s2/favicons?domain=notion.so&sz=32' },
      { name: 'Obsidian', url: 'https://obsidian.md', icon: 'https://www.google.com/s2/favicons?domain=obsidian.md&sz=32' },
    ],
  },
  {
    name: '大模型',
    resources: [
      { name: 'DeepSeek', url: 'https://www.deepseek.com', icon: 'https://www.google.com/s2/favicons?domain=deepseek.com&sz=32' },
      { name: '文心一言', url: 'https://yiyan.baidu.com', icon: 'https://www.google.com/s2/favicons?domain=baidu.com&sz=32' },
      { name: 'Kimi', url: 'https://kimi.moonshot.cn', icon: 'https://www.google.com/s2/favicons?domain=moonshot.cn&sz=32' },
      { name: 'ChatGPT', url: 'https://chat.openai.com', icon: 'https://www.google.com/s2/favicons?domain=openai.com&sz=32' },
      { name: 'Claude', url: 'https://claude.ai', icon: 'https://www.google.com/s2/favicons?domain=claude.ai&sz=32' },
      { name: '通义千问', url: 'https://tongyi.aliyun.com', icon: 'https://www.google.com/s2/favicons?domain=aliyun.com&sz=32' },
      { name: '智谱清言', url: 'https://chatglm.cn', icon: 'https://www.google.com/s2/favicons?domain=chatglm.cn&sz=32' },
      { name: '豆包', url: 'https://www.doubao.com', icon: 'https://www.google.com/s2/favicons?domain=doubao.com&sz=32' },
    ],
  },
  {
    name: '文生图',
    resources: [
      { name: '可灵', url: 'https://app.klingai.com/cn/', icon: 'https://www.google.com/s2/favicons?domain=klingai.com&sz=32' },
      { name: 'Midjourney', url: 'https://www.midjourney.com', icon: 'https://www.google.com/s2/favicons?domain=midjourney.com&sz=32' },
      { name: 'DALL·E', url: 'https://openai.com/dall-e-2', icon: 'https://www.google.com/s2/favicons?domain=openai.com&sz=32' },
      { name: 'Stable Diffusion', url: 'https://stablediffusionweb.com', icon: 'https://www.google.com/s2/favicons?domain=stablediffusionweb.com&sz=32' },
      { name: '文心一格', url: 'https://yige.baidu.com', icon: 'https://www.google.com/s2/favicons?domain=baidu.com&sz=32' },
      { name: '通义万相', url: 'https://tongyi.aliyun.com/wanxiang', icon: 'https://www.google.com/s2/favicons?domain=aliyun.com&sz=32' },
      { name: '6pen', url: 'https://6pen.art', icon: 'https://www.google.com/s2/favicons?domain=6pen.art&sz=32' },
    ],
  },
  {
    name: '文生视频',
    resources: [
      { name: '即梦', url: 'https://jimeng.jianying.com/ai-tool/home', icon: 'https://www.google.com/s2/favicons?domain=jianying.com&sz=32' },
      { name: '蝉镜', url: 'https://www.chanjing.cc', icon: 'https://www.google.com/s2/favicons?domain=chanjing.cc&sz=32' },
      { name: 'Runway', url: 'https://runwayml.com', icon: 'https://www.google.com/s2/favicons?domain=runwayml.com&sz=32' },
      { name: 'Pika', url: 'https://pika.art', icon: 'https://www.google.com/s2/favicons?domain=pika.art&sz=32' },
      { name: 'Sora', url: 'https://openai.com/sora', icon: 'https://www.google.com/s2/favicons?domain=openai.com&sz=32' },
      { name: 'Stable Video', url: 'https://stability.ai/stable-video', icon: 'https://www.google.com/s2/favicons?domain=stability.ai&sz=32' },
      { name: '快剪辑', url: 'https://www.kuaijianji.com', icon: 'https://www.google.com/s2/favicons?domain=kuaijianji.com&sz=32' },
    ],
  },
]

function getResourceIcon(resource: AiResource): string {
  if (resource.icon) {
    return resource.icon
  }
  // 如果没有指定图标，从URL提取域名并使用favicon服务
  try {
    const domain = new URL(resource.url).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
  } catch {
    return ''
  }
}

function handleImageError(event: Event, resource: AiResource) {
  const img = event.target as HTMLImageElement
  // 如果图标加载失败，尝试使用favicon服务
  try {
    const domain = new URL(resource.url).hostname
    if (!img.src.includes('google.com/s2/favicons')) {
      img.src = `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
    } else {
      // 如果favicon也加载失败，隐藏图片或使用默认图标
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


