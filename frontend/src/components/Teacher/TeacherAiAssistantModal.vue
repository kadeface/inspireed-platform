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
          class="relative w-full max-w-5xl transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all"
        >
          <header class="flex items-start justify-between gap-4 border-b border-[#E2E6F6] px-6 py-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-[#4C6EF5]">
                智能助手
              </p>
              <h2 class="mt-1 text-xl font-semibold text-[#2B2F48]">
                AI 教学助理
              </h2>
              <p class="mt-1 text-sm text-[#6E7590]">
                基于当前教学数据，智能生成课堂洞察与行动建议。
              </p>
            </div>
            <button
              type="button"
              @click="handleClose"
              class="rounded-full p-2 text-[#6E7590] transition hover:bg-[#ECF0FF] hover:text-[#4C6EF5] focus:outline-none focus:ring-2 focus:ring-[#4C6EF5] focus:ring-offset-2"
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

          <div class="grid gap-6 border-b border-[#E2E6F6] px-6 py-5 lg:grid-cols-[2fr,3fr]">
            <section class="space-y-4">
              <div class="rounded-2xl border border-[#D9DFF5] bg-white p-4 shadow-sm">
                <div class="flex items-center justify-between text-sm font-semibold text-[#4C568E]">
                  <span>课堂概览</span>
                  <span
                    v-if="isLoading"
                    class="flex items-center gap-2 text-xs font-normal text-[#4C6EF5]"
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

                <dl class="mt-3 grid grid-cols-3 gap-3 text-sm text-[#4C568E]">
                  <div class="rounded-xl bg-[#F5F7FF] px-3 py-2 shadow-sm">
                    <dt class="text-xs text-[#8D93AA]">草稿</dt>
                    <dd class="text-lg font-semibold text-[#4C6EF5]">
                      {{ lessonSummary?.draft ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-[#F5F7FF] px-3 py-2 shadow-sm">
                    <dt class="text-xs text-[#8D93AA]">已发布</dt>
                    <dd class="text-lg font-semibold text-[#4C6EF5]">
                      {{ lessonSummary?.published ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-[#F5F7FF] px-3 py-2 shadow-sm">
                    <dt class="text-xs text-[#8D93AA]">待答问题</dt>
                    <dd class="text-lg font-semibold text-[#4C6EF5]">
                      {{ questionStats?.pending ?? 0 }}
                    </dd>
                  </div>
                </dl>

                <div
                  v-if="subjectGroupStats"
                  class="mt-3 grid grid-cols-2 gap-3 text-xs text-[#6E7590]"
                >
                  <div class="rounded-xl bg-[#F5F7FF] px-3 py-2 shadow-sm">
                    <p class="font-medium text-[#8D93AA]">我的教研组</p>
                    <p class="text-base font-semibold text-[#4C6EF5]">
                      {{ subjectGroupStats.my_groups }}
                    </p>
                  </div>
                  <div class="rounded-xl bg-[#F5F7FF] px-3 py-2 shadow-sm">
                    <p class="font-medium text-[#8D93AA]">共享教案</p>
                    <p class="text-base font-semibold text-[#4C6EF5]">
                      {{ subjectGroupStats.my_shared_lessons }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <label class="text-sm font-semibold text-[#2B2F48]">助手关注主题</label>
                <div class="flex flex-wrap gap-2 text-xs font-medium">
                  <button
                    v-for="option in topicOptions"
                    :key="option.value"
                    type="button"
                    @click="selectedTopic = option.value"
                    :class="[
                      'rounded-full px-3 py-1 transition border',
                      selectedTopic === option.value
                        ? 'bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] text-white shadow'
                        : 'border-[#4C6EF5] text-[#4C6EF5] bg-white hover:bg-[#ECF0FF]',
                    ]"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-semibold text-[#2B2F48]">智能推荐提问</label>
                  <button
                    type="button"
                    class="rounded-full border border-[#4C6EF5] px-3 py-1 text-xs font-medium text-[#4C6EF5] transition hover:bg-[#4C6EF5] hover:text-white"
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
                    class="rounded-xl border border-transparent bg-[#EFF2FF] px-3 py-1.5 text-left text-xs text-[#4C6EF5] transition hover:border-[#4C6EF5]"
                    @click="applyPrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-semibold text-[#2B2F48]" for="assistant-question">
                  提问或描述需求
                </label>
                <textarea
                  id="assistant-question"
                  v-model="question"
                  rows="4"
                  class="w-full resize-none rounded-xl border border-[#D9DFF5] px-4 py-3 text-sm text-[#2B2F48] shadow-sm focus:border-[#4C6EF5] focus:outline-none focus:ring-2 focus:ring-[#C8D4FF]"
                  placeholder="例如：帮我总结目前课堂的亮点和下节课的优化建议。"
                ></textarea>
              </div>

              <div class="flex items-center justify-between gap-3">
                <p class="text-xs text-[#8D93AA]">
                  AI 会综合当前仪表盘数据，生成总结与下一步行动建议。
                </p>
                <button
                  type="button"
                  :disabled="!isReady || isSubmitting"
                  class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] px-5 py-2.5 text-sm font-semibold text-white shadow transition enabled:hover:shadow-lg enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-[#BFD0FF] disabled:cursor-not-allowed disabled:opacity-60"
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

              <p v-if="errorMessage" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
                {{ errorMessage }}
              </p>
            </section>

            <section
              class="flex max-h-[70vh] flex-col gap-4 overflow-hidden rounded-2xl border border-transparent bg-[#F1F4FF] p-5"
            >
              <div
                v-if="response"
                class="flex-1 overflow-y-auto rounded-2xl bg-white p-5 text-sm text-[#2B2F48] shadow-inner"
              >
                <div class="flex items-center justify-between gap-3 border-b pb-3">
                  <h3 class="text-base font-semibold text-[#2B2F48]">助手回答</h3>
                  <div class="flex items-center gap-3 text-xs text-[#8D93AA]">
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
                  <h4 class="text-sm font-semibold text-[#2B2F48]">关键洞察</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="insight in response.insights"
                      :key="insight.title"
                      class="rounded-xl border border-[#D9DFF5] bg-[#EFF2FF] px-3 py-2 text-sm text-[#4C568E]"
                    >
                      <p class="font-semibold">{{ insight.title }}</p>
                      <p class="mt-1 text-xs text-[#4C6EF5]">{{ insight.detail }}</p>
                      <p v-if="insight.metric" class="mt-1 text-[11px] text-[#8D93AA]">
                        {{ insight.metric }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.suggested_actions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-[#2B2F48]">建议行动</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="action in response.suggested_actions"
                      :key="action.label"
                      class="rounded-xl border border-[#DCE1F4] bg-[#F7F8FC] px-3 py-2 text-sm text-[#4C568E]"
                    >
                      <p class="font-semibold text-[#2B2F48]">{{ action.label }}</p>
                      <p v-if="action.description" class="mt-1 text-xs text-[#6E7590]">
                        {{ action.description }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.follow_up_questions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-[#2B2F48]">续问建议</h4>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="item in response.follow_up_questions"
                      :key="item"
                      type="button"
                      class="rounded-full border border-transparent bg-white px-3 py-1 text-xs text-[#4C6EF5] transition hover:border-[#4C6EF5]"
                      @click="applyPrompt(item)"
                    >
                      {{ item }}
                    </button>
                  </div>
                </div>

                <div
                  v-if="response.context_used?.length"
                  class="mt-4 border-t border-[#E2E6F6] pt-3 text-[11px] text-[#8D93AA]"
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
                class="flex flex-1 flex-col items-center justify-center rounded-2xl border border-dashed border-[#C9D1F0] bg-white/70 text-center text-sm text-[#6E7590]"
              >
                <div
                  class="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] text-2xl text-white shadow"
                >
                  🤖
                </div>
                <p class="font-semibold text-[#2B2F48]">等待您的问题</p>
                <p class="mt-1 text-xs text-[#8D93AA]">
                  选择主题并输入问题，AI 将结合最新数据给出建议。
                </p>
              </div>
            </section>
          </div>

          <footer
            class="flex items-center justify-between border-t border-[#E2E6F6] bg-[#F7F8FC] px-6 py-4 text-xs text-[#8D93AA]"
          >
            <span>AI 输出仅供教学辅助，请结合课堂实际判断使用。</span>
            <button
              type="button"
              class="text-[#4C6EF5] hover:text-[#365AE0]"
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
import type { PropType } from 'vue'
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
</style>

