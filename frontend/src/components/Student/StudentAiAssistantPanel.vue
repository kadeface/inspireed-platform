<template>
  <div class="flex h-full flex-col">
    <header class="border-b border-[#E2E6F6] bg-white px-5 py-4">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wide text-[#4C6EF5]">
            学习助手
          </p>
          <h2 class="mt-1 text-lg font-semibold text-[#2B2F48]">AI 学习教练</h2>
        </div>
        <span
          v-if="progress !== undefined"
          class="rounded-full bg-[#EFF2FF] px-3 py-1 text-xs font-medium text-[#4C6EF5]"
        >
          学习进度 {{ progress }}%
        </span>
      </div>
      <p class="mt-2 text-xs text-[#6E7590]">
        根据当前课程，为你整理知识点、练习建议和复习提示。
      </p>
    </header>

    <main class="flex-1 overflow-y-auto px-5 py-4 space-y-5 bg-[#F7F8FC]">
      <section class="rounded-2xl border border-[#D9DFF5] bg-white p-4">
        <h3 class="text-sm font-semibold text-[#2B2F48]">课程概览</h3>
        <p class="mt-1 text-xs text-[#6E7590]">
          {{ lessonTitle || '未命名课程' }}
        </p>
        <ul v-if="outlineItems.length" class="mt-3 space-y-1 text-xs text-[#4C568E]">
          <li v-for="(item, index) in outlineItems" :key="index" class="flex gap-2">
            <span class="mt-0.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-[#4C6EF5]"></span>
            <span>{{ item }}</span>
          </li>
        </ul>
        <p v-else class="mt-3 text-xs text-[#8D93AA]">
          暂无结构概览，AI 将根据标题提供通用建议。
        </p>
      </section>

      <section class="space-y-3">
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

      <section class="space-y-2">
        <label class="text-sm font-semibold text-[#2B2F48]" for="student-assistant-question">
          想了解什么？
        </label>
        <textarea
          id="student-assistant-question"
          v-model="question"
          rows="4"
          class="w-full resize-none rounded-xl border border-[#D9DFF5] px-4 py-3 text-sm text-[#2B2F48] shadow-sm focus:border-[#4C6EF5] focus:outline-none focus:ring-2 focus:ring-[#C8D4FF]"
          placeholder="例如：帮我总结这节课的重点，或推荐复习习题。"
        ></textarea>
      </section>

      <div class="flex items-center justify-between text-xs text-[#8D93AA]">
        <p>AI 会结合课程结构与进度给出建议，可一键加入笔记。</p>
        <button
          type="button"
          :disabled="isSubmitting || !canSubmit"
          class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#4C6EF5] to-[#6C8DFF] px-3 py-2 text-sm font-semibold text-white shadow transition enabled:hover:shadow-lg enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-[#BFD0FF] disabled:cursor-not-allowed disabled:opacity-50"
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
        class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600"
      >
        {{ errorMessage }}
      </p>

      <section v-if="response" class="space-y-3 rounded-2xl border border-[#D9DFF5] bg-white p-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-semibold text-[#2B2F48]">助手回答</h3>
          <div class="flex items-center gap-2 text-[11px] text-[#8D93AA]">
            <span v-if="response.model_used">模型 {{ response.model_used }}</span>
            <span v-if="response.response_time_ms">
              {{ Math.round(response.response_time_ms) }} ms
            </span>
          </div>
        </div>

        <div class="rounded-xl bg-[#F7F8FC] p-3 text-sm text-[#2B2F48]">
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
            @click="emitAppendNote"
          >
            添加到笔记
          </button>
        </div>

        <div v-if="response.follow_up_questions.length" class="pt-2">
          <h4 class="text-xs font-semibold text-[#6E7590]">续问建议</h4>
          <div class="mt-2 flex flex-wrap gap-2">
            <button
              v-for="item in response.follow_up_questions"
              :key="item"
              type="button"
              class="rounded-full border border-transparent bg-[#EFF2FF] px-3 py-1 text-xs text-[#4C6EF5] transition hover:border-[#4C6EF5]"
              @click="applyPrompt(item)"
            >
              {{ item }}
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'
import assistantService from '@/services/assistant'
import type { AssistantRequest, AssistantResponse } from '@/types/assistant'

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

