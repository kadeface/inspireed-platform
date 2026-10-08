<template>
  <div class="space-y-4">
    <div class="rounded-xl border border-emerald-100 bg-emerald-50/60 p-4 space-y-3">
      <p class="text-xs font-medium text-emerald-900">最小实验主题（固定）</p>
      <div class="grid gap-2 sm:grid-cols-2 text-sm text-gray-800">
        <p>年级：{{ snapshot.grade }}</p>
        <p>学科：{{ snapshot.subject }}</p>
        <p class="sm:col-span-2">课题：{{ snapshot.title }}</p>
        <p>课时：{{ snapshot.duration_minutes }} 分钟</p>
        <p>快照：{{ snapshot.snapshot_id }}@{{ snapshot.version }}</p>
        <p class="sm:col-span-2 text-xs text-gray-600">整理日期：{{ snapshot.captured_at }}</p>
        <p v-if="snapshot.bundle_ref" class="sm:col-span-2 text-xs text-gray-600">
          来源 bundle：{{ snapshot.bundle_ref }}
        </p>
      </div>
      <div class="text-xs text-gray-700 space-y-1">
        <p class="font-medium">核心要点</p>
        <ul class="list-disc pl-4">
          <li v-for="idea in snapshot.core_ideas" :key="idea">{{ idea }}</li>
        </ul>
      </div>
      <div class="text-xs text-gray-700 space-y-1">
        <p class="font-medium">Wiki 来源</p>
        <ul class="space-y-1">
          <li v-for="source in snapshot.sources" :key="source.id">
            <span class="font-medium">{{ source.label }}</span>
            <span class="text-gray-500"> — {{ source.wiki_path }}</span>
          </li>
        </ul>
      </div>
      <p class="text-xs text-gray-500">本课知识来自已发布快照；内容更新请联系教研。</p>
    </div>

    <label class="block text-xs font-medium text-gray-700">
      学情备注（可选）
      <input
        v-model="studentNotes"
        class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
        placeholder="本班可能的困难或已有基础"
      />
    </label>

    <div class="flex flex-wrap gap-2">
      <button
        type="button"
        class="inline-flex items-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-50"
        :disabled="isDrafting || isGeneratingPackage"
        @click="handleGenerateDraft"
      >
        {{ isDrafting ? '生成草案中…' : draft ? '重新生成草案' : '生成课程草案' }}
      </button>
      <button
        v-if="draft && !draftConfirmed"
        type="button"
        class="rounded-xl border border-emerald-300 bg-white px-4 py-2 text-sm font-semibold text-emerald-800"
        @click="confirmDraft"
      >
        确认草案
      </button>
      <button
        type="button"
        data-testid="generate-package"
        class="inline-flex items-center rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white shadow disabled:opacity-50"
        :disabled="!canGeneratePackage || isGeneratingPackage"
        @click="handleGeneratePackage"
      >
        {{ isGeneratingPackage ? '生成四件套中…' : '生成课程四件套' }}
      </button>
    </div>

    <p v-if="errorMessage" class="text-sm text-rose-600">{{ errorMessage }}</p>

    <div v-if="draftRawFallback" class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
      <p class="font-medium">草案未能解析，已显示原文：</p>
      <pre class="mt-2 max-h-64 overflow-auto whitespace-pre-wrap">{{ draftRawFallback }}</pre>
    </div>

    <div v-if="draft" class="rounded-xl border border-gray-100 bg-white p-4 text-sm space-y-2">
      <p class="font-semibold text-gray-900">课程草案</p>
      <p><span class="font-medium">核心理解：</span>{{ draft.core_understanding }}</p>
      <p v-if="draftConfirmed" class="text-xs text-emerald-700">已确认（指纹 {{ confirmedFingerprint }}）</p>
      <p v-else class="text-xs text-amber-700">请先确认草案后再生成四件套。</p>
    </div>

    <div v-if="packageRawFallback" class="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
      <p class="font-medium">四件套未能解析，已显示原文：</p>
      <pre class="mt-2 max-h-64 overflow-auto whitespace-pre-wrap">{{ packageRawFallback }}</pre>
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

      <div v-if="qualityChecks.length" class="rounded-xl border border-gray-100 bg-slate-50 p-3 space-y-2">
        <p class="text-sm font-semibold text-gray-900">质量检查</p>
        <p
          class="text-xs font-medium"
          :class="allQualityPassed ? 'text-emerald-700' : 'text-amber-700'"
        >
          {{ allQualityPassed ? '质量检查通过' : '存在未通过项，请查看说明后重新生成' }}
        </p>
        <ul class="space-y-1 text-xs">
          <li v-for="check in qualityChecks" :key="check.id">
            <span :class="check.status === 'pass' ? 'text-emerald-700' : 'text-rose-700'">
              {{ check.id }} — {{ check.status }}：{{ check.message }}
            </span>
          </li>
        </ul>
      </div>
    </div>

    <div v-if="pkg" class="rounded-xl border border-gray-100 bg-white p-4 space-y-3">
      <h3 class="text-sm font-semibold text-gray-900">课堂反馈</h3>
      <textarea v-model="courseFeedback.observed_evidence" rows="2" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="课堂上实际看到或听到的学生证据" />
      <textarea v-model="courseFeedback.student_difficulties" rows="2" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="仍然出现的困难" />
      <textarea v-model="courseFeedback.effective_scaffolds" rows="2" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="有效或无效的提示" />
      <textarea v-model="courseFeedback.teacher_reflection" rows="2" class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" placeholder="教师补充判断（可选）" />
      <button
        type="button"
        class="rounded-lg bg-teal-600 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50"
        :disabled="!canSaveFeedback"
        @click="handleSaveFeedback"
      >
        形成待审核 Wiki 建议
      </button>
    </div>

    <div v-if="wikiSuggestions.length" class="rounded-xl border border-gray-100 bg-slate-50/80 p-4 space-y-2">
      <h3 class="text-sm font-semibold text-gray-900">待审核 Wiki 建议</h3>
      <div
        v-for="item in wikiSuggestions"
        :key="item.id"
        class="rounded-lg border border-gray-100 bg-white p-3 text-xs space-y-1"
      >
        <p><span class="font-medium">状态：</span>{{ item.status }} · v{{ item.snapshot_version }}</p>
        <p><span class="font-medium">证据摘要：</span>{{ item.evidence_summary }}</p>
        <p class="whitespace-pre-wrap"><span class="font-medium">建议：</span>{{ item.suggested_change }}</p>
        <div class="flex gap-2 pt-1">
          <button type="button" class="text-emerald-700 underline" @click="copySuggestion(item.suggested_change)">复制</button>
          <button type="button" class="text-rose-600 underline" @click="wikiSuggestions = removeWikiUpdateSuggestion(item.id)">删除</button>
        </div>
      </div>
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
          <button type="button" class="shrink-0 text-rose-600" @click="removePatch(p.id)">删除</button>
        </li>
      </ul>
      <button
        v-if="patches.length"
        type="button"
        class="text-xs text-gray-500 underline"
        @click="onPatchesCleared"
      >
        清空全部补丁
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { assistantService } from '@/services/assistant'
import {
  CYCLE_REMAINDER_WIKI_SNAPSHOT,
  serializeWikiSnapshotContext,
} from '@/data/courseDesignWikiSnapshots'
import {
  addCourseDesignPatch,
  addWikiUpdateSuggestion,
  buildCourseDesignDraftManual,
  buildCourseDesignDraftQuestion,
  buildCourseDesignPackageManual,
  buildCourseDesignPackageQuestion,
  clearCourseDesignPatches,
  createCourseDesignDraftFingerprint,
  formatCourseDesignTabMarkdown,
  loadCourseDesignPatches,
  loadWikiUpdateSuggestions,
  parseCourseDesignDraft,
  parseCourseDesignPackage,
  removeCourseDesignPatch,
  removeWikiUpdateSuggestion,
  runCourseDesignQualityChecks,
  validateCourseFeedback,
  type CourseDesignDraft,
  type CourseDesignPackage,
  type CourseDesignQualityCheck,
  type CourseDesignSkillPatch,
  type CourseDesignTabId,
  type CourseFeedbackInput,
  type WikiUpdateSuggestion,
} from '@/utils/courseDesignSkill'

const props = defineProps<{
  insertHandler?: (markdown: string) => void
}>()

const snapshot = CYCLE_REMAINDER_WIKI_SNAPSHOT
const studentNotes = ref('')
const isDrafting = ref(false)
const isGeneratingPackage = ref(false)
const errorMessage = ref<string | null>(null)
const draftRawFallback = ref<string | null>(null)
const packageRawFallback = ref<string | null>(null)
const draft = ref<CourseDesignDraft | null>(null)
const draftConfirmed = ref(false)
const confirmedFingerprint = ref<string | null>(null)
const pkg = ref<CourseDesignPackage | null>(null)
const qualityChecks = ref<CourseDesignQualityCheck[]>([])
const activeTab = ref<CourseDesignTabId>('teacher_lesson_plan')
const feedbackText = ref('')
const patches = ref<CourseDesignSkillPatch[]>([])
const copyHint = ref('')
const trimNotice = ref('')
const wikiSuggestions = ref<WikiUpdateSuggestion[]>([])
const courseFeedback = ref<CourseFeedbackInput>({
  observed_evidence: '',
  student_difficulties: '',
  effective_scaffolds: '',
  teacher_reflection: '',
})

const tabs: Array<{ id: CourseDesignTabId; label: string }> = [
  { id: 'teacher_lesson_plan', label: '教师教案' },
  { id: 'student_worksheet', label: '学生学习单' },
  { id: 'scaffold_cards', label: '分层提示卡' },
  { id: 'observation_rubric', label: '课堂观察表' },
]

const snapshotIdentity = computed(() => `${snapshot.snapshot_id}@${snapshot.version}`)

const canGeneratePackage = computed(
  () => draftConfirmed.value && !!confirmedFingerprint.value && !isDrafting.value,
)

const currentTabMarkdown = computed(() =>
  pkg.value ? formatCourseDesignTabMarkdown(pkg.value, activeTab.value) : '',
)

const allQualityPassed = computed(
  () => qualityChecks.value.length > 0 && qualityChecks.value.every((item) => item.status === 'pass'),
)

const canSaveFeedback = computed(() => validateCourseFeedback(courseFeedback.value).ok)

function courseInput() {
  return {
    grade: snapshot.grade,
    subject: snapshot.subject,
    topic_title: snapshot.title,
    duration_minutes: snapshot.duration_minutes,
    student_notes: studentNotes.value.trim() || undefined,
  }
}

function invalidateDraftConfirmation() {
  draftConfirmed.value = false
  confirmedFingerprint.value = null
  pkg.value = null
  packageRawFallback.value = null
  qualityChecks.value = []
}

function recomputeDraftFingerprint() {
  if (!draft.value) return null
  return createCourseDesignDraftFingerprint(
    draft.value,
    snapshotIdentity.value,
    studentNotes.value.trim(),
    patches.value,
  )
}

function confirmDraft() {
  if (!draft.value) return
  confirmedFingerprint.value = recomputeDraftFingerprint()
  draftConfirmed.value = true
}

watch(studentNotes, () => {
  if (draftConfirmed.value) invalidateDraftConfirmation()
})

onMounted(() => {
  patches.value = loadCourseDesignPatches()
  wikiSuggestions.value = loadWikiUpdateSuggestions()
})

async function handleGenerateDraft() {
  errorMessage.value = null
  draftRawFallback.value = null
  invalidateDraftConfirmation()
  isDrafting.value = true
  try {
    const input = courseInput()
    const response = await assistantService.askTeacherAssistant({
      question: buildCourseDesignDraftQuestion(input),
      topic: 'course_design',
      context: {
        agent_prompt: buildCourseDesignDraftManual(patches.value),
        course_design_context: {
          snapshot_id: snapshot.snapshot_id,
          snapshot_version: snapshot.version,
          teaching_context: serializeWikiSnapshotContext(snapshot),
        },
      },
    })
    const parsed = parseCourseDesignDraft(response.answer)
    if (!parsed.ok) {
      draft.value = null
      draftRawFallback.value = parsed.raw
      return
    }
    draft.value = parsed.draft
  } catch (e: unknown) {
    errorMessage.value = e instanceof Error ? e.message : '生成草案失败，请稍后重试'
  } finally {
    isDrafting.value = false
  }
}

async function handleGeneratePackage() {
  if (!draft.value || !confirmedFingerprint.value) return
  errorMessage.value = null
  packageRawFallback.value = null
  isGeneratingPackage.value = true
  try {
    const response = await assistantService.askTeacherAssistant({
      question: buildCourseDesignPackageQuestion(confirmedFingerprint.value),
      topic: 'course_design',
      context: {
        agent_prompt: buildCourseDesignPackageManual(
          draft.value,
          confirmedFingerprint.value,
          patches.value,
        ),
        course_design_context: {
          snapshot_id: snapshot.snapshot_id,
          snapshot_version: snapshot.version,
          teaching_context: serializeWikiSnapshotContext(snapshot),
        },
      },
    })
    const parsed = parseCourseDesignPackage(response.answer)
    if (!parsed.ok) {
      pkg.value = null
      qualityChecks.value = []
      packageRawFallback.value = parsed.raw
      return
    }
    if (parsed.package.draft_fingerprint && parsed.package.draft_fingerprint !== confirmedFingerprint.value) {
      pkg.value = null
      qualityChecks.value = []
      packageRawFallback.value = response.answer
      errorMessage.value = '四件套草案指纹与当前确认不一致，结果已作废。'
      return
    }
    pkg.value = parsed.package
    qualityChecks.value = runCourseDesignQualityChecks(
      parsed.package,
      draft.value,
      confirmedFingerprint.value,
      snapshot,
    )
    activeTab.value = 'teacher_lesson_plan'
  } catch (e: unknown) {
    errorMessage.value = e instanceof Error ? e.message : '生成四件套失败，请稍后重试'
  } finally {
    isGeneratingPackage.value = false
  }
}

async function copyCurrent() {
  await navigator.clipboard.writeText(currentTabMarkdown.value)
  copyHint.value = '已复制到剪贴板'
  window.setTimeout(() => {
    copyHint.value = ''
  }, 2000)
}

async function copySuggestion(text: string) {
  await navigator.clipboard.writeText(text)
}

function handleSaveFeedback() {
  if (!validateCourseFeedback(courseFeedback.value).ok) return
  wikiSuggestions.value = addWikiUpdateSuggestion(
    courseFeedback.value,
    snapshot,
    qualityChecks.value,
  )
  courseFeedback.value = {
    observed_evidence: '',
    student_difficulties: '',
    effective_scaffolds: '',
    teacher_reflection: '',
  }
}

function handleWriteBack() {
  const text = feedbackText.value.trim()
  if (!text) return
  const beforeCount = patches.value.length
  const beforeChars = patches.value.reduce((sum, p) => sum + p.text.length, 0)
  patches.value = addCourseDesignPatch(text, snapshot.title)
  feedbackText.value = ''
  invalidateDraftConfirmation()
  const afterChars = patches.value.reduce((sum, p) => sum + p.text.length, 0)
  const trimmed =
    patches.value.length < beforeCount + 1 || afterChars < beforeChars + text.length
  trimNotice.value = trimmed ? '已达存储上限，较早的规则已被自动丢弃。' : ''
}

function removePatch(id: string) {
  patches.value = removeCourseDesignPatch(id)
  invalidateDraftConfirmation()
}

function onPatchesCleared() {
  patches.value = clearCourseDesignPatches()
  invalidateDraftConfirmation()
}
</script>
