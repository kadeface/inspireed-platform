<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-5xl px-4 py-6 sm:px-6 lg:px-8">
      <header class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-slate-900">教研员工作台</h1>
            <p class="mt-1 text-sm text-slate-600">活动 {{ activityId }} · {{ sessionName }}</p>
          </div>
          <div class="flex gap-3">
            <button
              type="button"
              class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
              @click="copyCurrentLink"
            >
              复制链接
            </button>
          </div>
        </div>
      </header>

      <section v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
        正在加载...
      </section>

      <section v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        {{ error }}
      </section>

      <section v-else class="space-y-5">
        <!-- 进度看板 -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p class="text-sm text-slate-500">作品总数</p>
            <p class="mt-2 text-2xl font-bold text-slate-900">{{ progress.total_works }}</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p class="text-sm text-slate-500">已评分</p>
            <p class="mt-2 text-2xl font-bold text-emerald-700">{{ progress.scored_works }}</p>
          </div>
          <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <p class="text-sm text-slate-500">未评分</p>
            <p class="mt-2 text-2xl font-bold text-amber-700">{{ progress.unscored_works }}</p>
          </div>
        </div>

        <!-- 分配评委 -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-900">分配评委</h2>

          <!-- 负责范围 -->
          <div v-if="session && session.scopes" class="mb-4 rounded-xl bg-slate-50 p-4">
            <p class="mb-2 text-sm font-medium text-slate-700">您负责的范围：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(scope, i) in session.scopes"
                :key="i"
                class="rounded-full bg-indigo-100 px-3 py-1 text-xs text-indigo-700"
              >
                {{ scope.grade_band }} - {{ scope.subject }}
              </span>
            </div>
          </div>

          <!-- 分享链接 -->
          <div class="mb-4 rounded-xl bg-indigo-50 border border-indigo-200 p-4">
            <div class="flex items-center justify-between mb-2">
              <p class="text-sm font-medium text-indigo-900">🔗 您的专属访问链接</p>
              <button
                type="button"
                class="text-xs bg-indigo-600 text-white px-3 py-1 rounded-lg hover:bg-indigo-700"
                @click="copyCurrentLink"
              >
                {{ linkCopied ? '✓ 已复制' : '复制链接' }}
              </button>
            </div>
            <div class="bg-white rounded-lg p-2 border border-indigo-200 break-all text-xs text-slate-600">
              {{ currentLink }}
            </div>
          </div>

          <!-- 添加评委表单 -->
          <div class="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p class="mb-3 text-sm font-medium text-slate-700">添加评委：</p>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-4">
              <select v-model="newJudge.scopeIndex" class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm">
                <option value="">选择范围</option>
                <option v-for="(scope, i) in session.scopes" :key="i" :value="i">
                  {{ scope.grade_band }} - {{ scope.subject }}
                </option>
              </select>
              <input
                v-model="newJudge.name"
                type="text"
                placeholder="评委姓名"
                class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
              />
              <input
                v-model="newJudge.contact"
                type="text"
                placeholder="联系方式（可选）"
                class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
              />
              <button
                type="button"
                class="rounded-lg bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
                :disabled="!canAddJudge"
                @click="addJudge"
              >
                添加
              </button>
            </div>
          </div>

          <!-- 评委列表 -->
          <div v-if="judgeList.length > 0" class="mb-4 rounded-xl border border-slate-200 bg-white p-4">
            <div class="mb-3 flex items-center justify-between">
              <p class="text-sm font-medium text-slate-700">已分配 {{ judgeList.length }} 位评委：</p>
              <button
                v-if="hasChanges"
                type="button"
                class="text-xs text-red-600 hover:text-red-700"
                @click="resetChanges"
              >
                撤销未保存更改
              </button>
            </div>
            <div class="max-h-64 space-y-2 overflow-y-auto">
              <div
                v-for="(judge, i) in judgeList"
                :key="judge.id || i"
                class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
                :class="judge.isNew ? 'bg-green-50 border border-green-200' : ''"
              >
                <div class="flex-1">
                  <span class="font-medium text-slate-900">{{ judge.name }}</span>
                  <span v-if="judge.contact" class="ml-2 text-xs text-slate-500">({{ judge.contact }})</span>
                  <span class="ml-2 rounded-full px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700">
                    {{ judge.grade_band }} - {{ judge.subject }}
                  </span>
                  <span v-if="judge.isNew" class="ml-2 text-xs text-green-600">新增</span>
                </div>
                <button
                  type="button"
                  class="text-red-500 hover:text-red-700"
                  @click="removeJudge(i)"
                >
                  删除
                </button>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              :disabled="!hasChanges || saving"
              @click="saveJudges"
            >
              {{ saving ? '保存中...' : '保存评委分配' }}
            </button>
            <span v-if="saveMessage" class="text-sm text-emerald-700">{{ saveMessage }}</span>
          </div>

          <div v-if="saveError" class="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            {{ saveError }}
          </div>
        </div>

        <!-- 导出结果 -->
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-3 text-sm font-semibold text-slate-800">导出结果</h2>
          <div class="flex flex-wrap gap-3">
            <button
              type="button"
              class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
              :disabled="downloading"
              @click="downloadSummary"
            >
              导出汇总（含评委评分）
            </button>
            <button
              type="button"
              class="rounded-xl bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
              :disabled="downloading"
              @click="downloadDetails"
            >
              导出明细（评分事件）
            </button>
            <button
              type="button"
              class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              :disabled="loading"
              @click="loadData"
            >
              刷新进度
            </button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { reviewChannelApi, type ReviewProgress, type ReviewSession, type AssignmentRule } from '@/services/reviewChannel'

const route = useRoute()

const activityId = computed(() => String(route.query.activity_id || ''))
const token = computed(() => String(route.query.token || ''))

const loading = ref(true)
const downloading = ref(false)
const error = ref('')
const saveMessage = ref('')
const linkCopied = ref(false)
const saveError = ref('')
const saving = ref(false)
const sessionName = ref('')
const session = ref<ReviewSession | null>(null)
const progress = ref<ReviewProgress>({
  total_works: 0,
  scored_works: 0,
  unscored_works: 0,
})

// 评委相关
interface JudgeItem extends AssignmentRule {
  id?: string
  isNew?: boolean
}

const judgeList = ref<JudgeItem[]>([])
const originalJudgeList = ref<JudgeItem[]>([])
const newJudge = ref({
  scopeIndex: '',
  name: '',
  contact: '',
})

const currentLink = computed(() => window.location.href)

const canAddJudge = computed(() => {
  return newJudge.value.scopeIndex !== '' && newJudge.value.name.trim() !== ''
})

const hasChanges = computed(() => {
  return JSON.stringify(judgeList.value) !== JSON.stringify(originalJudgeList.value)
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    if (!activityId.value || !token.value) {
      throw new Error('缺少 activity_id 或 token')
    }
    const sessionData = await reviewChannelApi.getSession(token.value, activityId.value)
    if (sessionData.role !== 'coordinator') {
      throw new Error('当前链接不是教研员入口')
    }
    session.value = sessionData
    sessionName.value = sessionData.name || '教研员'
    progress.value = await reviewChannelApi.getProgress(activityId.value, token.value)

    // 加载已分配的评委
    await loadJudges()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function loadJudges() {
  try {
    const data = await reviewChannelApi.getAssignments(activityId.value)
    const allRules = data.rules || []

    // 筛选出当前教研员负责范围内的评委
    const myJudges: JudgeItem[] = []
    for (const rule of allRules) {
      if (rule.role === 'judge') {
        // 检查是否在当前教研员的负责范围内
        for (const scope of session.value?.scopes || []) {
          if (rule.grade_band === scope.grade_band && rule.subject === scope.subject) {
            myJudges.push({ ...rule, isNew: false })
            break
          }
        }
      }
    }
    judgeList.value = myJudges
    originalJudgeList.value = JSON.parse(JSON.stringify(myJudges))
  } catch (e: any) {
    console.warn('加载评委失败:', e)
  }
}

function addJudge() {
  if (!canAddJudge.value || !session.value) return

  const scopeIndex = parseInt(newJudge.value.scopeIndex)
  const scope = session.value.scopes[scopeIndex]

  judgeList.value.push({
    grade_band: scope.grade_band,
    subject: scope.subject,
    role: 'judge',
    name: newJudge.value.name.trim(),
    contact: newJudge.value.contact.trim(),
    isNew: true,
  })

  // 重置表单
  newJudge.value = { scopeIndex: '', name: '', contact: '' }
}

function removeJudge(index: number) {
  judgeList.value.splice(index, 1)
}

function resetChanges() {
  judgeList.value = JSON.parse(JSON.stringify(originalJudgeList.value))
  saveError.value = ''
  saveMessage.value = ''
}

async function saveJudges() {
  if (!session.value) return

  saving.value = true
  saveError.value = ''
  saveMessage.value = ''

  try {
    // 构建完整的规则列表：当前教研员的评委 + 其他不变的规则
    const data = await reviewChannelApi.getAssignments(activityId.value)
    const allRules = data.rules || []

    // 移除当前教研员范围内的旧评委规则
    const filteredRules = allRules.filter((rule: AssignmentRule) => {
      if (rule.role !== 'judge') return true
      // 检查是否在当前教研员负责范围内
      for (const scope of session.value!.scopes) {
        if (rule.grade_band === scope.grade_band && rule.subject === scope.subject) {
          return false // 移除旧规则
        }
      }
      return true
    })

    // 添加新的评委规则
    for (const judge of judgeList.value) {
      filteredRules.push({
        grade_band: judge.grade_band,
        subject: judge.subject,
        role: 'judge',
        name: judge.name,
        contact: judge.contact,
      })
    }

    // 保存
    const result = await reviewChannelApi.saveAssignments(activityId.value, {
      rules: filteredRules,
    })

    saveMessage.value = `✓ 已保存 ${judgeList.value.length} 位评委`
    await loadJudges() // 重新加载
  } catch (e: any) {
    saveError.value = e?.response?.data?.detail || e?.message || '保存失败'
  } finally {
    saving.value = false
  }
}

async function downloadSummary() {
  downloading.value = true
  error.value = ''
  try {
    await reviewChannelApi.downloadSummary(activityId.value, token.value)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '汇总导出失败'
  } finally {
    downloading.value = false
  }
}

async function downloadDetails() {
  downloading.value = true
  error.value = ''
  try {
    await reviewChannelApi.downloadDetails(activityId.value, token.value)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '明细导出失败'
  } finally {
    downloading.value = false
  }
}

onMounted(loadData)

async function copyCurrentLink() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    linkCopied.value = true
    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch {
    saveMessage.value = '复制失败'
  }
}
</script>
