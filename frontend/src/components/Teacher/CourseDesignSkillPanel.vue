<template>
  <div class="space-y-4">
    <div class="grid gap-3 sm:grid-cols-2">
      <label class="text-xs font-medium text-gray-700">
        年级
        <input v-model="form.grade" class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="例如：七年级" />
      </label>
      <label class="text-xs font-medium text-gray-700">
        学科
        <input v-model="form.subject" class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="例如：数学" />
      </label>
      <label class="text-xs font-medium text-gray-700 sm:col-span-2">
        课题
        <input v-model="form.topic_title" class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="例如：解一元一次方程" />
      </label>
      <label class="text-xs font-medium text-gray-700">
        课时（分钟）
        <input v-model.number="form.duration_minutes" type="number" min="10" max="120" class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" />
      </label>
      <label class="text-xs font-medium text-gray-700">
        学情备注（可选）
        <input v-model="form.student_notes" class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="学生可能的困难" />
      </label>
    </div>

    <button
      type="button"
      class="inline-flex items-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-50"
      :disabled="!canGenerate || isGenerating"
      @click="handleGenerate"
    >
      {{ isGenerating ? '生成中…' : '生成课程设计四件套' }}
    </button>

    <p v-if="errorMessage" class="text-sm text-rose-600">{{ errorMessage }}</p>

    <div v-if="rawFallback" class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
      <p class="font-medium">未能解析结构化结果，已显示原文：</p>
      <pre class="mt-2 max-h-64 overflow-auto whitespace-pre-wrap">{{ rawFallback }}</pre>
      <button type="button" class="mt-2 text-xs font-medium text-emerald-700 underline" @click="handleGenerate">重新生成</button>
    </div>

    <div v-if="pkg" class="space-y-3">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="rounded-full border px-3 py-1 text-xs font-medium"
          :class="activeTab === tab.id ? 'border-emerald-500 bg-emerald-50 text-emerald-800' : 'border-gray-200 text-gray-600'"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="max-h-80 overflow-auto rounded-xl border border-gray-100 bg-white p-4 text-sm text-gray-800 whitespace-pre-wrap">
        {{ currentTabMarkdown }}
      </div>
      <div class="flex flex-wrap gap-2">
        <button type="button" class="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium" @click="copyCurrent">
          复制当前 Tab
        </button>
        <button
          v-if="insertHandler"
          type="button"
          class="rounded-lg border border-violet-200 px-3 py-1.5 text-xs font-medium text-violet-700"
          @click="insertHandler(currentTabMarkdown)"
        >
          插入为 TEXT
        </button>
      </div>
      <p v-if="copyHint" class="text-xs text-emerald-700">{{ copyHint }}</p>
    </div>

    <div class="rounded-xl border border-gray-100 bg-slate-50/80 p-4 space-y-3">
      <h3 class="text-sm font-semibold text-gray-900">写回 Skill（本机）</h3>
      <textarea
        v-model="feedbackText"
        rows="3"
        class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
        placeholder="例如：提示卡不要直接给答案；观察表对齐等式性质…"
      />
      <button
        type="button"
        class="rounded-lg bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
        :disabled="!feedbackText.trim()"
        @click="handleWriteBack"
      >
        写回 Skill
      </button>
      <p v-if="trimNotice" class="text-xs text-amber-700">{{ trimNotice }}</p>
      <ul v-if="patches.length" class="space-y-2 text-xs text-gray-700">
        <li v-for="p in patches" :key="p.id" class="flex items-start justify-between gap-2 rounded-lg bg-white px-3 py-2 border border-gray-100">
          <span>{{ p.text }}</span>
          <button type="button" class="shrink-0 text-rose-600" @click="patches = removeCourseDesignPatch(p.id)">删除</button>
        </li>
      </ul>
      <button
        v-if="patches.length"
        type="button"
        class="text-xs text-gray-500 underline"
        @click="patches = clearCourseDesignPatches()"
      >
        清空全部补丁
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { assistantService } from '@/services/assistant'
import {
  addCourseDesignPatch,
  buildCourseDesignQuestion,
  buildCourseDesignSkillManual,
  clearCourseDesignPatches,
  formatCourseDesignTabMarkdown,
  loadCourseDesignPatches,
  parseCourseDesignPackage,
  removeCourseDesignPatch,
  type CourseDesignPackage,
  type CourseDesignSkillPatch,
  type CourseDesignTabId,
} from '@/utils/courseDesignSkill'

const props = defineProps<{
  insertHandler?: (markdown: string) => void
}>()

const form = reactive({
  grade: '七年级',
  subject: '数学',
  topic_title: '',
  duration_minutes: 45,
  student_notes: '',
})

const isGenerating = ref(false)
const errorMessage = ref<string | null>(null)
const rawFallback = ref<string | null>(null)
const pkg = ref<CourseDesignPackage | null>(null)
const activeTab = ref<CourseDesignTabId>('teacher_lesson_plan')
const feedbackText = ref('')
const patches = ref<CourseDesignSkillPatch[]>([])
const copyHint = ref('')
const trimNotice = ref('')

const tabs: Array<{ id: CourseDesignTabId; label: string }> = [
  { id: 'teacher_lesson_plan', label: '教师教案' },
  { id: 'student_worksheet', label: '学生学习单' },
  { id: 'scaffold_cards', label: '分层提示卡' },
  { id: 'observation_rubric', label: '课堂观察表' },
]

const canGenerate = computed(
  () =>
    !!form.grade.trim() &&
    !!form.subject.trim() &&
    !!form.topic_title.trim() &&
    Number(form.duration_minutes) > 0
)

const currentTabMarkdown = computed(() =>
  pkg.value ? formatCourseDesignTabMarkdown(pkg.value, activeTab.value) : ''
)

onMounted(() => {
  patches.value = loadCourseDesignPatches()
})

async function handleGenerate() {
  errorMessage.value = null
  rawFallback.value = null
  isGenerating.value = true
  try {
    const input = {
      grade: form.grade.trim(),
      subject: form.subject.trim(),
      topic_title: form.topic_title.trim(),
      duration_minutes: Number(form.duration_minutes) || 45,
      student_notes: form.student_notes.trim() || undefined,
    }
    const manual = buildCourseDesignSkillManual(patches.value)
    const response = await assistantService.askTeacherAssistant({
      question: buildCourseDesignQuestion(input),
      topic: 'course_design',
      context: { agent_prompt: manual },
    })
    const parsed = parseCourseDesignPackage(response.answer)
    if (!parsed.ok) {
      pkg.value = null
      rawFallback.value = parsed.raw
      return
    }
    pkg.value = parsed.package
    activeTab.value = 'teacher_lesson_plan'
  } catch (e: unknown) {
    errorMessage.value = e instanceof Error ? e.message : '生成失败，请稍后重试'
  } finally {
    isGenerating.value = false
  }
}

async function copyCurrent() {
  await navigator.clipboard.writeText(currentTabMarkdown.value)
  copyHint.value = '已复制到剪贴板'
  window.setTimeout(() => {
    copyHint.value = ''
  }, 2000)
}

function handleWriteBack() {
  const text = feedbackText.value.trim()
  if (!text) return
  const beforeCount = patches.value.length
  const beforeChars = patches.value.reduce((sum, p) => sum + p.text.length, 0)
  patches.value = addCourseDesignPatch(
    text,
    form.topic_title.trim() || undefined
  )
  feedbackText.value = ''
  const afterChars = patches.value.reduce((sum, p) => sum + p.text.length, 0)
  const trimmed =
    patches.value.length < beforeCount + 1 || afterChars < beforeChars + text.length
  trimNotice.value = trimmed
    ? '已达存储上限，较早的规则已被自动丢弃。'
    : ''
}
</script>
