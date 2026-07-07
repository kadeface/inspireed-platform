<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <div class="text-sm text-slate-500">个性化学习伴学</div>
          <h1 class="text-2xl font-bold text-slate-900">个性化学习</h1>
          <p class="mt-1 text-sm text-slate-600">
            上传你已经做完的一道小学数学题，再用语音或文字说明你想检查什么，获得针对你的个性化讲解。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50"
            @click="router.push('/student/self-study/history')"
          >
            我的学习记录
          </button>
          <button
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50"
            @click="router.push('/student')"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
            返回工作台
          </button>
        </div>
      </div>

      <div v-if="pageError" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ pageError }}
      </div>

      <div v-if="loading" class="rounded-2xl bg-white p-8 shadow-sm text-center text-slate-500">
        正在加载...
      </div>

      <template v-else>
        <div v-if="!session" class="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-5">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">1. 导入题图</h2>
              <p class="mt-1 text-sm text-slate-600">
                支持上传图片或直接粘贴截图。图片不清晰、多题混在一起、看不到你的作答时会被直接丢弃。
              </p>
            </div>

            <div class="flex flex-wrap gap-3">
              <button
                class="px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700"
                @click="openInitialPicker"
              >
                上传图片
              </button>
              <button
                class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50"
                @click="pasteHintVisible = !pasteHintVisible"
              >
                从剪贴板粘贴
              </button>
            </div>
            <input
              ref="initialFileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="onInitialFileChange"
            />

            <div v-if="pasteHintVisible" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              把焦点放在当前页面，直接按 `Ctrl/Cmd + V` 粘贴截图即可。
            </div>

            <div v-if="uploadChecking" class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
              正在检查图片是否清晰、是否只包含一道题...
            </div>

            <div v-if="uploadError" class="rounded-xl border border-amber-200 bg-amber-50 px-4 py-4">
              <div class="font-medium text-amber-800">{{ uploadError }}</div>
              <ul v-if="uploadSuggestions.length" class="mt-2 list-disc pl-5 text-sm text-amber-700 space-y-1">
                <li v-for="item in uploadSuggestions" :key="item">{{ item }}</li>
              </ul>
            </div>

            <div v-if="acceptedUpload?.file_url" class="rounded-2xl border border-slate-200 overflow-hidden">
              <img :src="acceptedUpload.file_url" alt="题图预览" class="w-full max-h-[420px] object-contain bg-slate-100" />
              <div class="p-4 text-sm text-slate-600 space-y-2">
                <div class="font-medium text-slate-900">题图已通过检查</div>
                <div v-if="acceptedUpload.problem_text_preview">
                  题干识别预览：{{ acceptedUpload.problem_text_preview }}
                </div>
                <div v-if="acceptedUpload.student_work_text_preview">
                  作答识别预览：{{ acceptedUpload.student_work_text_preview }}
                </div>
              </div>
            </div>
          </div>

          <div class="rounded-2xl bg-white p-6 shadow-sm space-y-5">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">2. 确认你的提问</h2>
              <p class="mt-1 text-sm text-slate-600">
                说清楚你想检查什么。可以直接打字，也可以用输入法的语音输入，提交前都能再修改。
              </p>
            </div>

            <textarea
              v-model="draftQuestion"
              rows="6"
              class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              placeholder="例如：我觉得我做对了，但不知道为什么第三步要先算这个。"
            />

            <div class="rounded-xl bg-slate-50 px-4 py-3 text-xs text-slate-500">
              想用说的？点进上面的输入框，用输入法自带的语音输入（手机/平板键盘的语音按钮，电脑上 macOS 听写或 Windows 的 Win+H）即可把话转成文字。
            </div>

            <button
              class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
              :disabled="!acceptedUpload?.upload_token || !draftQuestion.trim() || submitting"
              @click="handleCreateSession"
            >
              {{ submitting ? '正在检查，请稍候…' : '开始检查' }}
            </button>
          </div>
        </div>

        <div v-else class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div class="space-y-6">
            <div class="rounded-2xl bg-white p-6 shadow-sm">
              <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div class="text-sm text-slate-500">会话 #{{ session.id }}</div>
                  <h2 class="text-xl font-semibold text-slate-900">当前学习会话</h2>
                  <p class="mt-1 text-sm text-slate-600">
                    状态：{{ phaseLabel(session.session_phase) }}，当前判断：{{ resultLabel(session.result_judgment) }}
                  </p>
                </div>
                <div class="text-sm text-slate-500">
                  已失败引导轮次：{{ session.guidance_round_count }}
                </div>
              </div>

              <div class="mt-6 grid gap-4 md:grid-cols-2">
                <div class="rounded-xl border border-slate-200 overflow-hidden">
                  <div class="px-4 py-2 bg-slate-50 text-sm font-medium text-slate-700">原始题图</div>
                  <img :src="session.original_image_url" alt="原始题图" class="w-full max-h-[420px] object-contain bg-slate-100" />
                </div>
                <div class="rounded-xl border border-slate-200 overflow-hidden">
                  <div class="px-4 py-2 bg-slate-50 text-sm font-medium text-slate-700">修正后题图</div>
                  <img
                    v-if="session.revised_image_url"
                    :src="session.revised_image_url"
                    alt="修正后题图"
                    class="w-full max-h-[420px] object-contain bg-slate-100"
                  />
                  <div v-else class="flex items-center justify-center h-[240px] text-sm text-slate-400 bg-slate-50">
                    你重新上传后会显示在这里
                  </div>
                </div>
              </div>

              <div class="mt-4 grid gap-3 md:grid-cols-2 text-sm text-slate-600">
                <div class="rounded-xl bg-slate-50 px-4 py-3">
                  <div class="font-medium text-slate-900 mb-1">题干识别预览</div>
                  {{ session.problem_text || '暂无' }}
                </div>
                <div class="rounded-xl bg-slate-50 px-4 py-3">
                  <div class="font-medium text-slate-900 mb-1">作答识别预览</div>
                  {{ session.student_work_text || '暂无' }}
                </div>
              </div>
            </div>

            <div class="rounded-2xl bg-white p-6 shadow-sm">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-slate-900">对话记录</h2>
                <div v-if="session.current_ai_message" class="text-sm text-slate-500">
                  最近 AI：{{ turnKindLabel(session.current_ai_message.turn_kind) }}
                </div>
              </div>

              <div class="mt-5 space-y-4">
                <div
                  v-for="turn in session.turns"
                  :key="turn.turn_index"
                  class="rounded-2xl px-4 py-4"
                  :class="turn.speaker === 'student'
                    ? 'bg-emerald-50 border border-emerald-100'
                    : turn.speaker === 'ai'
                      ? 'bg-sky-50 border border-sky-100'
                      : 'bg-slate-50 border border-slate-200'"
                >
                  <div class="flex items-center justify-between text-xs uppercase tracking-wide">
                    <span class="font-semibold text-slate-600">{{ speakerLabel(turn.speaker) }}</span>
                    <span class="text-slate-400">{{ turnKindLabel(turn.turn_kind) }}</span>
                  </div>
                  <div v-if="turn.speaker === 'ai' && turnDiagram(turn)" class="mt-3">
                    <SelfStudyDiagram :code="turnDiagram(turn)!" />
                  </div>
                  <div class="mt-2 whitespace-pre-wrap text-sm text-slate-700">
                    {{ turn.content_text }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-2xl bg-white p-6 shadow-sm space-y-5">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">继续提问或解释</h2>
                <p class="mt-1 text-sm text-slate-600">
                  你可以补充自己原来的想法，或者解释你为什么改成现在这样。
                </p>
              </div>

              <textarea
                v-model="draftQuestion"
                rows="5"
                class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="把你的想法说清楚，例如：我原来把总数当成了单价，所以第三步会错。"
              />

              <div class="text-xs text-slate-500">
                可以打字，也可以点进输入框用输入法的语音输入。
              </div>

              <button
                class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
                :disabled="!draftQuestion.trim() || submitting"
                @click="handleAppendTurn"
              >
                {{ submitting ? '正在思考，请稍候…' : '发送给 AI' }}
              </button>
            </div>

            <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">我改好了，再检查一次</h2>
                <p class="mt-1 text-sm text-slate-600">
                  复查必须重新上传修正后的题图；不重新上传，后端不会允许复查。
                </p>
              </div>
              <button
                class="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50"
                :disabled="submitting"
                @click="openRevisionPicker"
              >
                上传修正后的题图
              </button>
              <input
                ref="revisionFileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onRevisionFileChange"
              />
            </div>

            <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">后续动作</h2>
                <p class="mt-1 text-sm text-slate-600">
                  两轮失败引导后，才会开放标准解释；看完标准解释后，才可以转交老师。
                </p>
              </div>

              <button
                class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
                :disabled="!session.can_view_explanation || submitting"
                @click="handleUnlockExplanation"
              >
                查看标准解释
              </button>

              <textarea
                v-model="handoffConfusion"
                rows="4"
                class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="如果仍然不清楚，再写一句你最后卡在哪里。"
              />
              <button
                class="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                :disabled="!session.can_handoff_to_teacher || !handoffConfusion.trim() || submitting"
                @click="handleCreateHandoff"
              >
                转交老师
              </button>
            </div>

            <div
              v-if="session.teacher_handoff_status || session.teacher_reply_text || session.teacher_reply_image_url"
              class="rounded-2xl bg-white p-6 shadow-sm space-y-4"
            >
              <div>
                <h2 class="text-lg font-semibold text-slate-900">老师处理结果</h2>
                <p class="mt-1 text-sm text-slate-600">
                  当前状态：{{ session.teacher_handoff_status || '待处理' }}
                </p>
              </div>
              <div v-if="session.teacher_reply_text" class="whitespace-pre-wrap text-sm text-slate-700">
                {{ session.teacher_reply_text }}
              </div>
              <img
                v-if="session.teacher_reply_image_url"
                :src="session.teacher_reply_image_url"
                alt="老师标注图"
                class="w-full rounded-xl border border-slate-200"
              />
            </div>

            <div
              v-if="showSummaryForm"
              class="rounded-2xl bg-white p-6 shadow-sm space-y-4"
            >
              <div>
                <h2 class="text-lg font-semibold text-slate-900">完成前总结</h2>
                <p class="mt-1 text-sm text-slate-600">
                  结束前必须各写一句：你原来为什么错、你现在为什么知道这样改对了。
                </p>
              </div>
              <textarea
                v-model="summaryBefore"
                rows="3"
                class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="我原来为什么错："
              />
              <textarea
                v-model="summaryAfter"
                rows="3"
                class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="我现在为什么知道这样改对了："
              />
              <button
                class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
                :disabled="!summaryBefore.trim() || !summaryAfter.trim() || submitting"
                @click="handleCompleteSession"
              >
                完成本次学习
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import selfStudyService from '@/services/selfStudy'
import SelfStudyDiagram from '@/components/Student/SelfStudyDiagram.vue'
import type {
  SelfStudySession,
  SelfStudySpeaker,
  SelfStudyTurn,
  SelfStudyTurnKind,
  SelfStudyUploadCheckResponse,
} from '@/types/selfStudy'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const submitting = ref(false)
const pageError = ref<string | null>(null)

const session = ref<SelfStudySession | null>(null)
const acceptedUpload = ref<SelfStudyUploadCheckResponse | null>(null)
const uploadChecking = ref(false)
const uploadError = ref<string | null>(null)
const uploadSuggestions = ref<string[]>([])
const pasteHintVisible = ref(false)

const draftQuestion = ref('')
const handoffConfusion = ref('')
const summaryBefore = ref('')
const summaryAfter = ref('')

const initialFileInput = ref<HTMLInputElement | null>(null)
const revisionFileInput = ref<HTMLInputElement | null>(null)

const showSummaryForm = computed(() => {
  const current = session.value
  if (!current) return false
  return current.result_judgment === 'understood' || current.session_phase === 'handed_off'
})

function openInitialPicker() {
  initialFileInput.value?.click()
}

function openRevisionPicker() {
  revisionFileInput.value?.click()
}

async function loadSession(sessionId: number) {
  loading.value = true
  pageError.value = null
  try {
    const data = await selfStudyService.getSession(sessionId)
    session.value = data
    summaryBefore.value = data.summary_before || ''
    summaryAfter.value = data.summary_after || ''
  } catch (error: any) {
    pageError.value = error.message || '加载会话失败'
  } finally {
    loading.value = false
  }
}

async function handleCheckedFile(file: File, source: 'upload' | 'paste') {
  uploadChecking.value = true
  uploadError.value = null
  uploadSuggestions.value = []
  try {
    acceptedUpload.value = await selfStudyService.checkUpload(file, source)
  } catch (error: any) {
    acceptedUpload.value = null
    uploadError.value = error.message || '图片检查失败'
    uploadSuggestions.value = error.suggestions || []
  } finally {
    uploadChecking.value = false
  }
}

async function onInitialFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    await handleCheckedFile(file, 'upload')
  }
  target.value = ''
}

async function onRevisionFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file || !session.value) return
  submitting.value = true
  pageError.value = null
  try {
    session.value = await selfStudyService.reuploadRevision(session.value.id, file, {
      question_text_confirmed: draftQuestion.value.trim() || undefined,
    })
    draftQuestion.value = ''
  } catch (error: any) {
    pageError.value = error.message || '重新上传失败'
  } finally {
    submitting.value = false
    target.value = ''
  }
}

async function handleCreateSession() {
  if (!acceptedUpload.value?.upload_token) return
  submitting.value = true
  pageError.value = null
  try {
    const created = await selfStudyService.createSession({
      upload_token: acceptedUpload.value.upload_token,
      question_text_confirmed: draftQuestion.value.trim(),
      input_mode: 'text',
    })
    session.value = created
    await router.replace(`/student/self-study/session/${created.id}`)
    draftQuestion.value = ''
    acceptedUpload.value = null
  } catch (error: any) {
    pageError.value = error.message || '创建会话失败'
  } finally {
    submitting.value = false
  }
}

async function handleAppendTurn() {
  if (!session.value || !draftQuestion.value.trim()) return
  submitting.value = true
  pageError.value = null
  try {
    session.value = await selfStudyService.appendTurn(session.value.id, {
      question_text_confirmed: draftQuestion.value.trim(),
      input_mode: 'text',
    })
    draftQuestion.value = ''
  } catch (error: any) {
    pageError.value = error.message || '发送提问失败'
  } finally {
    submitting.value = false
  }
}

async function handleUnlockExplanation() {
  if (!session.value) return
  submitting.value = true
  pageError.value = null
  try {
    session.value = await selfStudyService.unlockExplanation(session.value.id)
  } catch (error: any) {
    pageError.value = error.message || '解锁标准解释失败'
  } finally {
    submitting.value = false
  }
}

async function handleCreateHandoff() {
  if (!session.value || !handoffConfusion.value.trim()) return
  submitting.value = true
  pageError.value = null
  try {
    await selfStudyService.createHandoff(session.value.id, handoffConfusion.value.trim())
    session.value = await selfStudyService.getSession(session.value.id)
    handoffConfusion.value = ''
  } catch (error: any) {
    pageError.value = error.message || '转交老师失败'
  } finally {
    submitting.value = false
  }
}

async function handleCompleteSession() {
  if (!session.value) return
  submitting.value = true
  pageError.value = null
  try {
    session.value = await selfStudyService.completeSession(session.value.id, {
      summary_before: summaryBefore.value.trim(),
      summary_after: summaryAfter.value.trim(),
    })
  } catch (error: any) {
    pageError.value = error.message || '保存总结失败'
  } finally {
    submitting.value = false
  }
}

function speakerLabel(speaker: SelfStudySpeaker) {
  if (speaker === 'student') return '学生'
  if (speaker === 'ai') return 'AI'
  return '系统'
}

function turnKindLabel(kind: SelfStudyTurnKind) {
  const map: Record<SelfStudyTurnKind, string> = {
    question: '学生说明',
    probe: '追问',
    hint: '提示',
    explanation: '标准解释',
    summary: '总结',
  }
  return map[kind] || kind
}

function turnDiagram(turn: SelfStudyTurn): string | null {
  const code = turn.meta_json?.diagram_mermaid
  return typeof code === 'string' && code.trim() ? code.trim() : null
}

function phaseLabel(phase?: string | null) {
  const map: Record<string, string> = {
    awaiting_question: '待提问',
    guiding: '引导中',
    awaiting_reupload: '等待改图复查',
    explanation_unlocked: '已开放标准解释',
    handed_off: '已转交老师',
    completed: '已完成',
  }
  return (phase && map[phase]) || '进行中'
}

function resultLabel(result?: string | null) {
  const map: Record<string, string> = {
    incorrect: '还没做对',
    correct_unexplained: '结果对了，但解释还不够清楚',
    understood: '已经理解了',
    needs_teacher: '需要老师接手',
  }
  return (result && map[result]) || '待判断'
}

function handlePaste(event: ClipboardEvent) {
  if (session.value) return
  const items = event.clipboardData?.items || []
  for (const item of Array.from(items)) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        handleCheckedFile(file, 'paste')
        event.preventDefault()
        return
      }
    }
  }
}

onMounted(() => {
  window.addEventListener('paste', handlePaste)
  const sessionId = Number(route.params.id)
  if (sessionId) {
    loadSession(sessionId)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('paste', handlePaste)
})
</script>
