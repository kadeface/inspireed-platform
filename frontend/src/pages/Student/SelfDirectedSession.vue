<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div class="flex items-center justify-between gap-4">
        <div>
          <div class="text-sm text-slate-500">个性化学习 · 自主学习</div>
          <h1 class="text-2xl font-bold text-slate-900">
            {{ session?.lesson_json?.title || '微课学习' }}
          </h1>
          <p class="mt-1 text-sm text-slate-600">
            目标：{{ session?.goal_text || '加载中…' }}
          </p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white"
          @click="router.push('/student/self-directed')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>
      </div>

      <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="rounded-2xl bg-white p-8 shadow-sm text-center text-slate-500">
        正在加载微课…
      </div>

      <template v-else-if="session">
        <div
          v-if="session.status === 'failed'"
          class="rounded-2xl bg-white p-6 shadow-sm text-sm text-red-700"
        >
          {{ session.error_message || '微课生成失败，请返回重试。' }}
        </div>

        <template v-else-if="lesson">
          <div v-if="session.prior_summary" class="rounded-2xl border border-emerald-100 bg-emerald-50/70 px-4 py-3 text-sm text-emerald-900">
            <div class="font-medium mb-1">开课前参考了你的知识库</div>
            {{ session.prior_summary }}
          </div>

          <div
            v-if="curriculumSources.length"
            class="rounded-2xl border border-sky-100 bg-sky-50/70 px-4 py-4 text-sm text-sky-950 space-y-3"
          >
            <div>
              <div class="font-medium">本课结合了平台 MathLab 课例</div>
              <p class="mt-1 text-xs text-sky-800/80">
                讲解会按现有课程手册给出具体操作，而不只是空泛方法。
              </p>
            </div>
            <div
              v-for="src in curriculumSources"
              :key="src.id"
              class="rounded-xl bg-white/80 border border-sky-100 px-3 py-3 space-y-1.5"
            >
              <div class="font-medium text-slate-900">
                {{ src.id }} · {{ src.title }}
              </div>
              <div class="text-xs text-slate-500">
                {{ [src.stage_name, src.unit].filter(Boolean).join(' / ') }}
              </div>
              <p v-if="src.goals?.length" class="text-xs text-slate-600">
                目标：{{ src.goals.join('；') }}
              </p>
              <a
                :href="src.mathlab_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1 text-sky-700 font-medium hover:underline"
              >
                打开 MathLab 实操
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-3">
            <h2 class="text-lg font-semibold text-slate-900">本课目标</h2>
            <p class="text-sm text-slate-700">{{ lesson.objective }}</p>
            <p v-if="session.mission_why" class="text-xs text-slate-500">
              为什么学：{{ session.mission_why }}
            </p>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
            <h2 class="text-lg font-semibold text-slate-900">讲解</h2>
            <div class="prose prose-slate max-w-none text-sm" v-html="explanationHtml" />
            <SelfStudyDiagram v-if="lesson.diagram_mermaid" :code="lesson.diagram_mermaid" />
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
            <h2 class="text-lg font-semibold text-slate-900">练一练</h2>
            <div
              v-for="item in lesson.practice"
              :key="item.id"
              class="space-y-2 rounded-xl border border-slate-200 p-4"
            >
              <div class="text-sm font-medium text-slate-900">
                <span
                  class="mr-2 inline-flex rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="item.type === 'multiple_choice' ? 'bg-sky-50 text-sky-700' : 'bg-violet-50 text-violet-700'"
                >
                  {{ item.type === 'multiple_choice' ? '选择题' : '简答题' }}
                </span>
                {{ item.prompt }}
              </div>

              <div v-if="item.type === 'multiple_choice'" class="space-y-2">
                <label
                  v-for="opt in item.options || []"
                  :key="`${item.id}-${opt.key}`"
                  class="flex items-start gap-3 rounded-xl border px-3 py-2 text-sm cursor-pointer transition-colors"
                  :class="
                    practiceAnswers[item.id] === opt.key
                      ? 'border-emerald-500 bg-emerald-50'
                      : 'border-slate-200 hover:border-emerald-300'
                  "
                >
                  <input
                    type="radio"
                    class="mt-1"
                    :name="`practice-${item.id}`"
                    :value="opt.key"
                    v-model="practiceAnswers[item.id]"
                    :disabled="session.status === 'completed'"
                  />
                  <span>
                    <span class="font-semibold text-slate-800">{{ opt.key }}.</span>
                    {{ opt.label }}
                  </span>
                </label>
              </div>

              <textarea
                v-else
                v-model="practiceAnswers[item.id]"
                rows="3"
                class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                :disabled="session.status === 'completed'"
                placeholder="用自己的话简答…"
              />

              <div
                v-if="practiceFeedback[item.id]"
                class="text-xs rounded-lg px-3 py-2"
                :class="practiceFeedback[item.id].ok ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-800'"
              >
                {{ practiceFeedback[item.id].feedback }}
              </div>
            </div>
            <button
              v-if="session.status !== 'completed'"
              class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-sm font-medium disabled:opacity-50"
              :disabled="submittingPractice || !canSubmitPractice"
              @click="handleSubmitPractice"
            >
              {{ submittingPractice ? '正在批改…' : '提交练习，获取反馈' }}
            </button>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
            <h2 class="text-lg font-semibold text-slate-900">验收</h2>
            <p class="text-sm text-slate-600">{{ lesson.mastery_prompt }}</p>
            <textarea
              v-model="masteryAnswer"
              rows="4"
              class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              :disabled="session.status === 'completed'"
              placeholder="用自己的话讲一遍…"
            />
            <button
              v-if="session.status !== 'completed'"
              class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
              :disabled="completing || !masteryAnswer.trim()"
              @click="handleComplete"
            >
              {{ completing ? '正在保存到知识库…' : '完成本课并写入知识库' }}
            </button>
            <div v-else class="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-800 space-y-2">
              <div>本课已完成，笔记已沉淀到知识库。</div>
              <button
                class="text-emerald-700 font-medium underline"
                @click="router.push('/student/knowledge-base')"
              >
                去知识库查看
              </button>
            </div>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import SelfStudyDiagram from '@/components/Student/SelfStudyDiagram.vue'
import selfDirectedService, {
  type PracticeFeedbackItem,
  type SelfDirectedLesson,
  type SelfDirectedSession,
} from '@/services/selfDirected'
import { markdownToHtml } from '@/utils/lessonEditorHelpers'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const submittingPractice = ref(false)
const completing = ref(false)
const errorMessage = ref('')
const session = ref<SelfDirectedSession | null>(null)
const practiceAnswers = reactive<Record<string, string>>({})
const practiceFeedback = reactive<Record<string, PracticeFeedbackItem>>({})
const masteryAnswer = ref('')

const lesson = computed<SelfDirectedLesson | null>(() => session.value?.lesson_json || null)

const curriculumSources = computed(() => lesson.value?.curriculum_sources || [])

const explanationHtml = computed(() => {
  if (!lesson.value?.explanation_md) return ''
  return markdownToHtml(lesson.value.explanation_md)
})

const canSubmitPractice = computed(() => {
  if (!lesson.value?.practice?.length) return false
  return lesson.value.practice.every((item) => (practiceAnswers[item.id] || '').trim())
})

async function loadSession() {
  const id = Number(route.params.id)
  if (!id) {
    errorMessage.value = '无效的学习会话'
    loading.value = false
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    session.value = await selfDirectedService.getSession(id)
    const saved = session.value.check_answers_json || {}
    const practice = Array.isArray(saved.practice) ? saved.practice : []
    practice.forEach((item: any) => {
      if (item?.id) practiceAnswers[item.id] = item.answer || ''
    })
    const feedback = Array.isArray(saved.practice_feedback) ? saved.practice_feedback : []
    feedback.forEach((item: PracticeFeedbackItem) => {
      if (item?.id) practiceFeedback[item.id] = item
    })
    masteryAnswer.value = saved.mastery_answer || ''
  } catch (error: any) {
    errorMessage.value = error.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function handleSubmitPractice() {
  if (!session.value || !lesson.value) return
  submittingPractice.value = true
  errorMessage.value = ''
  try {
    const answers = lesson.value.practice.map((item) => ({
      id: item.id,
      answer: (practiceAnswers[item.id] || '').trim(),
    }))
    const result = await selfDirectedService.submitPractice(session.value.id, answers)
    result.items.forEach((item) => {
      practiceFeedback[item.id] = item
    })
  } catch (error: any) {
    errorMessage.value = error.message || '提交练习失败'
  } finally {
    submittingPractice.value = false
  }
}

async function handleComplete() {
  if (!session.value || !lesson.value || !masteryAnswer.value.trim()) return
  completing.value = true
  errorMessage.value = ''
  try {
    const practice_answers = lesson.value.practice.map((item) => ({
      id: item.id,
      answer: (practiceAnswers[item.id] || '').trim() || '（未作答）',
    }))
    session.value = await selfDirectedService.completeSession(session.value.id, {
      mastery_answer: masteryAnswer.value.trim(),
      practice_answers,
    })
    const feedback = session.value.check_answers_json?.practice_feedback
    if (Array.isArray(feedback)) {
      feedback.forEach((item: PracticeFeedbackItem) => {
        if (item?.id) practiceFeedback[item.id] = item
      })
    }
  } catch (error: any) {
    errorMessage.value = error.message || '完成本课失败'
  } finally {
    completing.value = false
  }
}

onMounted(loadSession)
</script>
