<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="handleClose"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-slate-900/60"></div>

        <div
          class="relative w-full max-w-5xl transform overflow-hidden rounded-2xl bg-white/95 backdrop-blur-sm shadow-2xl transition-all"
        >
          <!-- Header with Dashboard style -->
          <header class="relative overflow-hidden border-b border-gray-200 bg-white/80 backdrop-blur-md shadow-sm">
            <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-200/40 to-transparent"></div>
            <div class="absolute inset-y-0 left-0 w-48 bg-gradient-to-br from-emerald-50/60 via-transparent to-transparent pointer-events-none"></div>
            <div class="absolute -bottom-8 -right-8 h-32 w-32 rounded-full bg-emerald-100/40 blur-3xl pointer-events-none"></div>

            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div class="flex flex-col gap-5">
                <div class="header-top flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <!-- 左侧：标题和欢迎信息 -->
                  <div class="relative z-10">
                    <div class="flex items-center gap-3">
                      <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 shadow-lg shadow-violet-500/20">
                        <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <div>
                        <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent tracking-tight">AI 教学助理</h1>
                        <p class="text-sm text-gray-600 mt-1 font-medium">
                          基于当前教学数据，智能生成课堂洞察与行动建议。
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- 右侧：用户信息和操作 -->
                  <div class="relative z-10 flex items-center gap-4">
                    <!-- 用户信息 -->
                    <div class="flex flex-col items-end text-right">
                      <div class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-800 bg-gray-100 rounded-full shadow-inner">
                        <svg class="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>{{ userName }}</span>
                      </div>
                      <div
                        v-if="organizationInfo.length"
                        class="mt-2 flex flex-wrap justify-end gap-2 text-xs text-gray-500"
                      >
                        <span
                          v-for="(info, index) in organizationInfo"
                          :key="index"
                          class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700 border border-emerald-100"
                        >
                          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 10-6 0 3 3 0 006 0z" />
                          </svg>
                          {{ info }}
                        </span>
                      </div>
                    </div>

                    <div class="h-10 w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent"></div>

                    <!-- 退出登录按钮 -->
                    <button
                      @click="handleLogout"
                      class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-rose-500 to-rose-600 rounded-xl shadow-lg shadow-rose-500/30 hover:shadow-xl hover:shadow-rose-500/40 hover:from-rose-600 hover:to-rose-700 transition-all transform hover:scale-105"
                    >
                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H3m12 0l-4 4m4-4l-4-4m13 8v-8" />
                      </svg>
                      退出登录
                    </button>

                    <button
                      type="button"
                      @click="handleClose"
                      class="rounded-xl p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
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
                </div>
              </div>
            </div>
          </header>

          <div class="grid gap-6 border-b border-gray-200 px-6 py-5 lg:grid-cols-[2fr,3fr]">
            <section class="space-y-4">
              <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg">
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
                <div class="flex items-center justify-between text-sm font-semibold text-gray-700">
                  <span>课堂概览</span>
                  <span
                    v-if="isLoading"
                    class="flex items-center gap-2 text-xs font-normal text-emerald-600"
                  >
                    <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
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
                    同步数据...
                  </span>
                </div>

                <dl class="mt-3 grid grid-cols-3 gap-3 text-sm text-gray-700">
                  <div class="rounded-xl bg-emerald-50/50 px-3 py-2 shadow-sm border border-emerald-100/50">
                    <dt class="text-xs text-gray-600">草稿</dt>
                    <dd class="text-lg font-semibold text-emerald-700">
                      {{ lessonSummary?.draft ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-teal-50/50 px-3 py-2 shadow-sm border border-teal-100/50">
                    <dt class="text-xs text-gray-600">已发布</dt>
                    <dd class="text-lg font-semibold text-teal-700">
                      {{ lessonSummary?.published ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-cyan-50/50 px-3 py-2 shadow-sm border border-cyan-100/50">
                    <dt class="text-xs text-gray-600">待答问题</dt>
                    <dd class="text-lg font-semibold text-cyan-700">
                      {{ questionStats?.pending ?? 0 }}
                    </dd>
                  </div>
                </dl>

                <div
                  v-if="subjectGroupStats"
                  class="mt-3 grid grid-cols-2 gap-3 text-xs"
                >
                  <div class="rounded-xl bg-emerald-50/50 px-3 py-2 shadow-sm border border-emerald-100/50">
                    <p class="font-medium text-gray-600">我的教研组</p>
                    <p class="text-base font-semibold text-emerald-700">
                      {{ subjectGroupStats.my_groups }}
                    </p>
                  </div>
                  <div class="rounded-xl bg-teal-50/50 px-3 py-2 shadow-sm border border-teal-100/50">
                    <p class="font-medium text-gray-600">共享教案</p>
                    <p class="text-base font-semibold text-teal-700">
                      {{ subjectGroupStats.my_shared_lessons }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <label class="text-sm font-semibold text-gray-900">助手关注主题</label>
                <div class="flex flex-wrap gap-2 text-xs font-medium">
                  <button
                    v-for="option in topicOptions"
                    :key="option.value"
                    type="button"
                    @click="selectedTopic = option.value"
                    :class="[
                      'rounded-full px-3 py-1 transition border',
                      selectedTopic === option.value
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                        : 'border-emerald-300 text-emerald-700 bg-white hover:bg-emerald-50',
                    ]"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-semibold text-gray-900">智能推荐提问</label>
                  <button
                    type="button"
                    class="rounded-full border border-emerald-300 px-3 py-1 text-xs font-medium text-emerald-700 transition hover:bg-emerald-500 hover:text-white hover:border-emerald-500"
                    @click="refreshSuggestions"
                  >
                    换一批
                  </button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="prompt in recommendedPrompts"
                    :key="prompt"
                    type="button"
                    class="rounded-xl border border-emerald-100 bg-emerald-50/50 px-3 py-1.5 text-left text-xs text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100/70"
                    @click="applyPrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-900" for="assistant-question">
                  提问或描述需求
                </label>
                <textarea
                  id="assistant-question"
                  v-model="question"
                  rows="4"
                  class="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white/80 backdrop-blur-sm"
                  placeholder="例如：帮我总结目前课堂的亮点和下节课的优化建议。"
                ></textarea>
              </div>

              <div class="flex items-center justify-between gap-3">
                <p class="text-xs text-gray-600">
                  AI 会综合当前仪表盘数据，生成总结与下一步行动建议。
                </p>
                <button
                  type="button"
                  :disabled="!isReady || isSubmitting"
                  class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-emerald-500/40 enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-emerald-500/50 disabled:cursor-not-allowed disabled:opacity-60"
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
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                    />
                  </svg>
                  <span>{{ isSubmitting ? '生成中...' : '生成建议' }}</span>
                </button>
              </div>

              <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50/80 backdrop-blur-sm px-3 py-2 text-xs text-red-700 shadow-sm">
                {{ errorMessage }}
              </p>
            </section>

            <section
              class="flex max-h-[70vh] flex-col gap-4 overflow-hidden rounded-2xl border border-gray-100 bg-gradient-to-br from-emerald-50/30 via-teal-50/20 to-cyan-50/30 p-5"
            >
              <div
                v-if="response"
                class="flex-1 overflow-y-auto rounded-2xl bg-white/90 backdrop-blur-sm p-5 text-sm text-gray-900 shadow-inner border border-gray-100"
              >
                <div class="flex items-center justify-between gap-3 border-b border-gray-200 pb-3">
                  <h3 class="text-base font-semibold text-gray-900">助手回答</h3>
                  <div class="flex items-center gap-3 text-xs text-gray-600">
                    <span v-if="response.model_used">模型：{{ response.model_used }}</span>
                    <span v-if="response.response_time_ms">
                      {{ Math.round(response.response_time_ms) }} ms
                    </span>
                    <span v-if="response.confidence !== undefined">
                      置信度 {{ Math.round((response.confidence ?? 0) * 100) }}%
                    </span>
                  </div>
                </div>

                <div class="mt-3 text-sm leading-relaxed text-slate-800">
                  <MarkdownPreview :content="response.answer" />
                </div>

                <div v-if="response.insights.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">关键洞察</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="insight in response.insights"
                      :key="insight.title"
                      class="rounded-xl border border-emerald-200 bg-emerald-50/50 px-3 py-2 text-sm text-emerald-900"
                    >
                      <p class="font-semibold">{{ insight.title }}</p>
                      <p class="mt-1 text-xs text-emerald-700">{{ insight.detail }}</p>
                      <p v-if="insight.metric" class="mt-1 text-[11px] text-gray-600">
                        {{ insight.metric }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.suggested_actions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">建议行动</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="action in response.suggested_actions"
                      :key="action.label"
                      class="rounded-xl border border-teal-200 bg-teal-50/50 px-3 py-2 text-sm text-teal-900"
                    >
                      <p class="font-semibold text-gray-900">{{ action.label }}</p>
                      <p v-if="action.description" class="mt-1 text-xs text-gray-700">
                        {{ action.description }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.follow_up_questions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">续问建议</h4>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="item in response.follow_up_questions"
                      :key="item"
                      type="button"
                      class="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-700 transition hover:border-emerald-400 hover:bg-emerald-50"
                      @click="applyPrompt(item)"
                    >
                      {{ item }}
                    </button>
                  </div>
                </div>

                <div
                  v-if="response.context_used?.length"
                  class="mt-4 border-t border-gray-200 pt-3 text-[11px] text-gray-600"
                >
                  <p>已引用的仪表盘数据：</p>
                  <ul class="mt-1 list-outside list-disc space-y-1 pl-4">
                    <li v-for="item in response.context_used" :key="item">
                      {{ item }}
                    </li>
                  </ul>
                </div>
              </div>

              <div
                v-else
                class="flex flex-1 flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white/70 backdrop-blur-sm text-center text-sm text-gray-600"
              >
                <div
                  class="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 text-2xl text-white shadow-lg shadow-violet-500/30"
                >
                  🤖
                </div>
                <p class="font-semibold text-gray-900">等待您的问题</p>
                <p class="mt-1 text-xs text-gray-600">
                  选择主题并输入问题，AI 将结合最新数据给出建议。
                </p>
              </div>
            </section>
          </div>

          <footer
            class="flex items-center justify-between border-t border-gray-200 bg-gradient-to-r from-emerald-50/50 via-teal-50/30 to-cyan-50/30 px-6 py-4 text-xs text-gray-600"
          >
            <span>AI 输出仅供教学辅助，请结合课堂实际判断使用。</span>
            <button
              type="button"
              class="text-emerald-700 hover:text-emerald-800 font-medium transition-colors"
              @click="handleClose"
            >
              关闭
            </button>
          </footer>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { PropType } from 'vue'
import { useUserStore } from '@/store/user'
import type { QuestionStats } from '@/types/question'
import type { SubjectGroupStatistics } from '@/types/subjectGroup'
import type { Lesson } from '@/types/lesson'
import type {
  TeacherAssistantContextPayload,
  TeacherAssistantResponse,
  TeacherAssistantTopic,
} from '@/types/assistant'
import assistantService from '@/services/assistant'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教师')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const organizationInfo = computed(() => {
  const info: string[] = []
  if (regionName.value) {
    info.push(`区域：${regionName.value}`)
  }
  if (schoolName.value) {
    info.push(`学校：${schoolName.value}`)
  }
  if (gradeName.value) {
    info.push(`年级：${gradeName.value}`)
  }
  return info
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  lessonSummary: {
    type: Object as PropType<Record<string, number>>,
    default: () => ({ draft: 0, published: 0, archived: 0 }),
  },
  questionStats: {
    type: Object as PropType<QuestionStats | null>,
    default: null,
  },
  subjectGroupStats: {
    type: Object as PropType<SubjectGroupStatistics | null>,
    default: null,
  },
  latestLessons: {
    type: Array as PropType<Lesson[]>,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'close'])

const question = ref('')
const selectedTopic = ref<TeacherAssistantTopic>('pdca')
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const response = ref<TeacherAssistantResponse | null>(null)
const suggestionOffset = ref(0)

const topicOptions: Array<{ label: string; value: TeacherAssistantTopic }> = [
  { label: '教学循环 (PDCA)', value: 'pdca' },
  { label: '教案共创', value: 'lesson_plan' },
  { label: '课堂问答辅导', value: 'qa' },
]

const normalizedContext = computed<TeacherAssistantContextPayload>(() => {
  const payload: TeacherAssistantContextPayload = {}

  if (props.lessonSummary) {
    const totalValue = Object.values(props.lessonSummary).reduce(
      (sum, value) => sum + (Number.isFinite(value) ? value : 0),
      0
    )
    if (totalValue > 0) {
      payload.lesson_summary = props.lessonSummary
    }
  }

  if (props.questionStats && (props.questionStats.total ?? 0) > 0) {
    payload.question_stats = props.questionStats
  }

  if (
    props.subjectGroupStats &&
    (props.subjectGroupStats.total_groups ?? 0) > 0
  ) {
    payload.subject_group_stats = props.subjectGroupStats
  }

  if (props.latestLessons.length > 0) {
    payload.recent_lessons = props.latestLessons.slice(0, 3).map((lesson) => ({
      id: lesson.id,
      title: lesson.title,
      status: lesson.status,
      updated_at: lesson.updated_at,
    }))
  }

  return payload
})

const recommendedPrompts = computed(() => {
  const promptsByTopic: Record<TeacherAssistantTopic, string[]> = {
    pdca: [
      '结合当前教案状态，帮我安排下一周的课堂重点和改进行动。',
      '根据待答问题和发布教案情况，提出课堂循环中的薄弱环节。',
      '请总结目前课堂执行的亮点，并给出循证改进建议。',
    ],
    lesson_plan: [
      '根据最近发布的教案，帮我提炼一次共研分享提纲。',
      '为当前草稿教案生成一个课堂导入活动。',
      '请为最近的教案提出一个面向教研组的优化建议。',
    ],
    qa: [
      '帮我整理学生提问的主要关注点，并给出统一答复框架。',
      '请为待答问题生成一份高质量回答草稿。',
      '结合问答数据，为家校沟通准备一段反馈说明。',
    ],
  }

  const basePrompts = promptsByTopic[selectedTopic.value] ?? []

  // 根据数据追加定制推荐
  const customPrompts: string[] = []
  const stats = props.questionStats
  if (stats && stats.pending > 0) {
    customPrompts.push(`针对当前 ${stats.pending} 个待答问题，生成优先处理建议。`)
  }

  if (
    props.lessonSummary &&
    (props.lessonSummary.draft ?? 0) > (props.lessonSummary.published ?? 0)
  ) {
    customPrompts.push('草稿教案较多，请帮我规划一份整理与发布的时间表。')
  }

  if (
    props.subjectGroupStats &&
    props.subjectGroupStats.my_shared_lessons === 0 &&
    selectedTopic.value === 'lesson_plan'
  ) {
    customPrompts.push('我还未在教研组共享教案，请给出一个分享流程与内容要点。')
  }

  const suggestions = [...basePrompts, ...customPrompts]
  if (suggestions.length <= 3) {
    return suggestions
  }

  const start = suggestionOffset.value % suggestions.length
  return suggestions.slice(start, start + 3)
})

const isReady = computed(() => question.value.trim().length >= 4)

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

function applyPrompt(prompt: string) {
  question.value = prompt
}

function refreshSuggestions() {
  suggestionOffset.value += 1
}

async function handleSubmit() {
  if (!isReady.value || isSubmitting.value) {
    return
  }

  errorMessage.value = null
  isSubmitting.value = true

  try {
    const assistantResponse = await assistantService.askTeacherAssistant({
      question: question.value.trim(),
      topic: selectedTopic.value,
      context: normalizedContext.value,
    })

    response.value = assistantResponse
  } catch (error: any) {
    errorMessage.value = error.message || '请求 AI 助手失败，请稍后重试。'
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      question.value = ''
      errorMessage.value = null
      response.value = null
      suggestionOffset.value = 0
    }
  }
)
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

.header-top {
  display: flex;
}
</style>

