<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <!-- 头部 -->
      <header class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <div class="flex items-center gap-3">
              <h1 class="text-xl font-bold text-slate-900">{{ activityName }}</h1>
              <span class="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{{ activityId }}</span>
            </div>
            <p class="mt-1 text-sm text-slate-600">作品评审活动配置与管理</p>
          </div>
          <div class="flex gap-3">
            <button
              type="button"
              class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              @click="goBack"
            >
              返回列表
            </button>
          </div>
        </div>
      </header>

      <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
        正在加载活动信息...
      </div>

      <div v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        {{ error }}
      </div>

      <div v-else class="space-y-6">
        <!-- 1. 作品导入卡片 -->
        <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-900">作品导入</h2>
            <div class="flex gap-2">
              <button
                type="button"
                class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
                @click="downloadTemplate"
              >
                下载作品模板
              </button>
            </div>
          </div>

          <div class="mb-4 rounded-xl bg-slate-50 p-4">
            <p class="mb-2 text-sm font-medium text-slate-700">Excel 文件要求：</p>
            <ul class="list-inside list-disc space-y-1 text-xs text-slate-600">
              <li>必填列：作品编号、作品名、学段、学科、链接地址</li>
              <li>可选列：上传者、市、区、学校、章节、附件名、格式</li>
              <li>同一作品编号的多行会合并为一个作品（多附件）</li>
              <li>链接地址必须以 http:// 或 https:// 开头</li>
            </ul>
          </div>

          <div class="mb-4">
            <input
              ref="fileInput"
              type="file"
              accept=".xlsx,.xls"
              class="hidden"
              @change="handleFileChange"
            />
            <div
              class="inline-flex cursor-pointer rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-4 text-sm text-slate-600 hover:border-indigo-400 hover:bg-indigo-50"
              @click="fileInput?.click()"
            >
              <span v-if="!selectedFile">点击选择 Excel 文件</span>
              <span v-else>{{ selectedFile.name }}</span>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              :disabled="!selectedFile || importing"
              @click="handleImport"
            >
              {{ importing ? '导入中...' : '导入作品' }}
            </button>
            <button
              v-if="importResult"
              type="button"
              class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              @click="importResult = null"
            >
              清除结果
            </button>
          </div>

          <!-- 导入结果 -->
          <div v-if="importResult" class="mt-4 rounded-xl bg-emerald-50 p-4">
            <div class="flex items-center gap-2 text-sm font-medium text-emerald-800">
              <span class="text-emerald-600">✓</span>
              导入成功！
            </div>
            <div class="mt-2 text-sm text-emerald-700">
              作品数：{{ importResult.works_upserted }} · 附件数：{{ importResult.attachments_inserted }}
            </div>
            <div v-if="importResult.warnings.length > 0" class="mt-3 rounded-lg bg-yellow-50 p-3">
              <p class="text-xs font-medium text-yellow-800">警告：</p>
              <ul class="mt-1 list-inside list-disc space-y-1 text-xs text-yellow-700">
                <li v-for="(w, i) in importResult.warnings.slice(0, 5)" :key="i">{{ w }}</li>
                <li v-if="importResult.warnings.length > 5" class="text-yellow-600">
                  还有 {{ importResult.warnings.length - 5 }} 条警告...
                </li>
              </ul>
            </div>
          </div>

          <!-- 导入错误 -->
          <div v-if="importError" class="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            {{ importError }}
          </div>
        </section>

        <!-- 2. 分配配置卡片 -->
        <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-900">评委/教研员分配</h2>
            <div class="flex gap-2">
              <button
                type="button"
                class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
                @click="downloadAssignmentTemplate"
              >
                下载分配模板
              </button>
              <label class="cursor-pointer rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50">
                导入分配模板
                <input
                  ref="assignmentTemplateInput"
                  type="file"
                  accept=".xlsx,.xls,.csv"
                  class="hidden"
                  @change="handleAssignmentTemplateImport"
                />
              </label>
            </div>
          </div>

          <!-- 学段学科范围提示 -->
          <div v-if="assignmentColumns" class="mb-4 rounded-xl bg-slate-50 p-4">
            <p class="mb-2 text-sm font-medium text-slate-700">当前作品的学段学科范围：</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(scope, i) in assignmentColumns.scopes"
                :key="i"
                class="rounded-full bg-indigo-100 px-2 py-1 text-xs text-indigo-700"
              >
                {{ scope.grade_band }} - {{ scope.subject }}
              </span>
              <span v-if="assignmentColumns.scopes.length === 0" class="text-xs text-slate-500">
                暂无作品，请先导入作品
              </span>
            </div>
          </div>

          <!-- 手动添加分配规则 -->
          <div class="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <p class="mb-3 text-sm font-medium text-slate-700">手动添加评委/教研员：</p>
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-5">
              <select v-model="newRule.grade_band" class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm">
                <option value="">学段</option>
                <option>小学</option>
                <option>初中</option>
                <option>高中</option>
                <option>中职</option>
                <option>高职</option>
              </select>
              <select v-model="newRule.subject" class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm">
                <option value="">学科</option>
                <option v-for="subject in subjectsForSelectedGrade" :key="subject" :value="subject">
                  {{ subject }}
                </option>
              </select>
              <select v-model="newRule.role" class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm">
                <option value="judge">评委</option>
                <option value="coordinator">教研员</option>
              </select>
              <input
                v-model="newRule.name"
                type="text"
                placeholder="姓名"
                class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
              />
              <input
                v-model="newRule.contact"
                type="text"
                placeholder="联系方式（可选）"
                class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
              />
            </div>
            <button
              type="button"
              class="mt-3 rounded-lg bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
              :disabled="!canAddRule"
              @click="addRule"
            >
              添加
            </button>
          </div>

          <!-- 已添加的规则列表 -->
          <div v-if="assignmentRules.length > 0" class="mb-4 rounded-xl border border-slate-200 bg-white p-4">
            <div class="mb-2 flex items-center justify-between">
              <p class="text-sm font-medium text-slate-700">已添加 {{ assignmentRules.length }} 条规则：</p>
              <button
                type="button"
                class="text-xs text-red-600 hover:text-red-700"
                @click="clearRules"
              >
                清空全部
              </button>
            </div>
            <div class="max-h-48 space-y-2 overflow-y-auto">
              <div
                v-for="(rule, i) in assignmentRules"
                :key="i"
                class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
              >
                <span class="text-slate-700">
                  <span class="font-medium">{{ rule.grade_band }}</span> -
                  <span class="font-medium">{{ rule.subject }}</span> ·
                  <span :class="rule.role === 'coordinator' ? 'text-purple-700' : 'text-indigo-700'">
                    {{ rule.role === 'coordinator' ? '教研员' : '评委' }}
                  </span> ·
                  <span class="font-medium">{{ rule.name }}</span>
                  <span v-if="rule.contact" class="text-slate-500">({{ rule.contact }})</span>
                </span>
                <button
                  type="button"
                  class="text-red-500 hover:text-red-700"
                  @click="removeRule(i)"
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
              :disabled="assignmentRules.length === 0 || savingAssignments"
              @click="handleSaveAssignments"
            >
              {{ savingAssignments ? '保存中...' : '保存分配规则' }}
            </button>
            <span v-if="saveResult" class="text-sm text-emerald-700">
              ✓ 已保存 {{ saveResult.saved }} 条规则
            </span>
          </div>

          <!-- 未覆盖范围提示 -->
          <div v-if="saveResult?.uncovered_scopes && saveResult.uncovered_scopes.length > 0" class="mt-4 rounded-xl bg-amber-50 p-4">
            <p class="text-xs font-medium text-amber-800">⚠️ 以下学段学科尚未分配评委：</p>
            <div class="mt-2 flex flex-wrap gap-2">
              <span
                v-for="(scope, i) in saveResult.uncovered_scopes"
                :key="i"
                class="rounded-full bg-amber-100 px-2 py-1 text-xs text-amber-700"
              >
                {{ scope.grade_band }} - {{ scope.subject }}
              </span>
            </div>
          </div>

          <div v-if="saveError" class="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            {{ saveError }}
          </div>
        </section>

        <!-- 3. 链接管理卡片 -->
        <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-900">评审链接生成</h2>

          <div class="mb-4 rounded-xl bg-slate-50 p-4">
            <p class="mb-2 text-sm font-medium text-slate-700">生成说明：</p>
            <ul class="list-inside list-disc space-y-1 text-xs text-slate-600">
              <li>为所有已分配的评委和教研员生成专属访问链接</li>
              <li>链接包含身份信息和权限范围，通过链接即可访问</li>
              <li>可设置过期时间，过期后链接将失效</li>
              <li>勾选"重新生成"将覆盖现有链接</li>
            </ul>
          </div>

          <div class="mb-4 flex items-center gap-4">
            <div class="flex items-center gap-2 text-sm text-slate-700">
              <input v-model="linkForm.expires_at_enabled" type="checkbox" class="rounded border-slate-300" />
              <label>设置过期时间：</label>
            </div>
            <input
              v-if="linkForm.expires_at_enabled"
              v-model="linkForm.expires_at"
              type="datetime-local"
              class="rounded-lg border border-slate-300 px-2 py-1.5 text-sm"
            />
            <div class="flex items-center gap-2 text-sm text-slate-700">
              <input v-model="linkForm.regenerate" type="checkbox" class="rounded border-slate-300" />
              <label>重新生成（覆盖现有链接）</label>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              :disabled="generatingLinks"
              @click="handleGenerateLinks"
            >
              {{ generatingLinks ? '生成中...' : '生成评审链接' }}
            </button>
            <button
              v-if="generatedLinks.length > 0"
              type="button"
              class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              @click="downloadGeneratedLinks"
            >
              导出链接清单
            </button>
          </div>

          <!-- 生成的链接列表 -->
          <div v-if="generatedLinks.length > 0" class="mt-4 rounded-xl border border-slate-200 p-4">
            <p class="mb-3 text-sm font-medium text-slate-700">已生成 {{ generatedLinks.length }} 条链接：</p>
            <div class="max-h-64 space-y-2 overflow-y-auto">
              <div
                v-for="(link, i) in generatedLinks"
                :key="i"
                class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
              >
                <div class="flex-1">
                  <span class="font-medium text-slate-900">{{ link.name }}</span>
                  <span class="ml-2 rounded-full px-2 py-0.5 text-xs"
                    :class="link.role === 'coordinator' ? 'bg-purple-100 text-purple-700' : 'bg-indigo-100 text-indigo-700'">
                    {{ link.role === 'coordinator' ? '教研员' : '评委' }}
                  </span>
                  <span class="ml-2 text-xs text-slate-500">
                    {{ formatScope(link) }}
                  </span>
                </div>
                <button
                  type="button"
                  class="ml-3 rounded border border-slate-300 bg-white px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
                  @click="copyLink(link)"
                >
                  {{ copiedLinkId === i ? '已复制' : '复制链接' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="linkError" class="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
            {{ linkError }}
          </div>
        </section>

        <!-- 4. 快捷操作 -->
        <section class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 text-lg font-semibold text-slate-900">快捷操作</h2>
          <div class="flex flex-wrap gap-3">
  <button
              type="button"
              class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              @click="recomputeSummary"
            >
              重新计算汇总
            </button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewChannelApi, type AssignmentRule, type ImportResult, type SaveAssignmentsResult, type AccessLink, type AssignmentColumns } from '@/services/reviewChannel'

const route = useRoute()
const router = useRouter()

const activityId = computed(() => String(route.params.activityId || ''))
const activityName = ref('评审活动')

const loading = ref(true)
const error = ref('')

// 作品导入
const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const importing = ref(false)
const importResult = ref<ImportResult | null>(null)
const importError = ref('')

// 分配配置
const assignmentTemplateInput = ref<HTMLInputElement | null>(null)
const assignmentColumns = ref<AssignmentColumns | null>(null)
const assignmentRules = ref<AssignmentRule[]>([])
const newRule = ref<AssignmentRule>({
  grade_band: '',
  subject: '',
  role: 'judge',
  name: '',
  contact: '',
})
const savingAssignments = ref(false)
const saveResult = ref<SaveAssignmentsResult | null>(null)
const saveError = ref('')

// 链接生成
const linkForm = ref({
  expires_at_enabled: false,
  expires_at: '',
  regenerate: false,
})
const generatingLinks = ref(false)
const generatedLinks = ref<AccessLink[]>([])
const linkError = ref('')
const copiedLinkId = ref<number | null>(null)

// 获取当前选择的学段对应的学科列表
const subjectsForSelectedGrade = computed(() => {
  if (!assignmentColumns.value || !newRule.value.grade_band) return []

  const gradeSubjects = assignmentColumns.value.scopes
    .filter(s => s.grade_band === newRule.value.grade_band)
    .map(s => s.subject)

  // 去重并排序
  return [...new Set(gradeSubjects)].sort()
})

// 当学段变化时，清空学科（如果不再在可用列表中）
watch(() => newRule.value.grade_band, (newGrade) => {
  if (newGrade && !subjectsForSelectedGrade.value.includes(newRule.value.subject)) {
    newRule.value.subject = ''
  }
})

const canAddRule = computed(() => {
  return newRule.value.grade_band && newRule.value.subject && newRule.value.name
})

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    importResult.value = null
    importError.value = ''
  }
}

async function downloadTemplate() {
  // 创建一个示例模板下载
  const headers = ['作品编号', '作品名', '上传者', '市', '区', '学校', '学段', '学科', '章节', '附件名', '格式', '链接地址']
  const exampleData = [
    ['WP001', 'Python教学设计', '张老师', '北京', '海淀区', '第一小学', '小学', '信息技术', '第一章', '课件', 'pptx', 'https://example.com/work1'],
    ['WP001', 'Python教学设计', '张老师', '北京', '海淀区', '第一小学', '小学', '信息技术', '第一章', '教学设计', 'docx', 'https://example.com/work2'],
    ['WP002', '数学互动课件', '李老师', '上海', '浦东新区', '第二中学', '初中', '数学', '第二章', '课件', 'pptx', 'https://example.com/work3'],
  ]

  let csv = headers.join(',') + '\n'
  exampleData.forEach(row => {
    csv += row.map(cell => `"${cell}"`).join(',') + '\n'
  })

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'works-template.csv'
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

async function handleImport() {
  console.log('[handleImport] called', {
    selectedFile: selectedFile.value,
    activityId: activityId.value,
  })
  if (!selectedFile.value) {
    console.log('[handleImport] no file selected')
    return
  }
  importing.value = true
  importError.value = ''
  importResult.value = null
  try {
    console.log('[handleImport] starting import', {
      fileName: selectedFile.value.name,
      fileSize: selectedFile.value.size,
    })
    importResult.value = await reviewChannelApi.importWorks(activityId.value, selectedFile.value)
    console.log('[handleImport] import success', importResult.value)
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    // 导入成功后重新加载分配列
    await loadAssignmentColumns()
  } catch (e: any) {
    console.error('[handleImport] import error', e)
    importError.value = e?.response?.data?.detail || e?.message || '导入失败'
  } finally {
    importing.value = false
  }
}

async function loadAssignmentColumns() {
  try {
    assignmentColumns.value = await reviewChannelApi.getAssignmentColumns(activityId.value)
  } catch (e: any) {
    console.warn('Failed to load assignment columns:', e)
  }
}

function addRule() {
  if (!canAddRule.value) return
  assignmentRules.value.push({
    grade_band: newRule.value.grade_band,
    subject: newRule.value.subject,
    role: newRule.value.role,
    name: newRule.value.name,
    contact: newRule.value.contact || '',
  })
  newRule.value = { grade_band: '', subject: '', role: 'judge', name: '', contact: '' }
}

function removeRule(index: number) {
  assignmentRules.value.splice(index, 1)
}

function clearRules() {
  assignmentRules.value = []
}

async function handleSaveAssignments() {
  savingAssignments.value = true
  saveError.value = ''
  saveResult.value = null
  try {
    saveResult.value = await reviewChannelApi.saveAssignments(activityId.value, {
      rules: assignmentRules.value,
    })
  } catch (e: any) {
    saveError.value = e?.response?.data?.detail || e?.message || '保存失败'
  } finally {
    savingAssignments.value = false
  }
}

async function downloadAssignmentTemplate() {
  try {
    await reviewChannelApi.downloadAssignmentTemplate(activityId.value)
  } catch (e: any) {
    alert('下载模板失败：' + (e?.response?.data?.detail || e?.message))
  }
}

function handleAssignmentTemplateImport(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    importAssignmentTemplateFile(file)
  }
}

async function importAssignmentTemplateFile(file: File) {
  try {
    const result = await reviewChannelApi.importAssignmentTemplate(activityId.value, file)
    saveResult.value = result
    // 导入成功后重新加载分配列
    await loadAssignmentColumns()
  } catch (e: any) {
    saveError.value = e?.response?.data?.detail || e?.message || '导入失败'
  }
}

async function handleGenerateLinks() {
  generatingLinks.value = true
  linkError.value = ''
  try {
    const payload: any = {}
    if (linkForm.value.expires_at_enabled && linkForm.value.expires_at) {
      payload.expires_at = new Date(linkForm.value.expires_at).toISOString()
    }
    if (linkForm.value.regenerate) {
      payload.regenerate = true
    }
    const result = await reviewChannelApi.generateAccessLinks(activityId.value, payload)
    generatedLinks.value = result.links
  } catch (e: any) {
    linkError.value = e?.response?.data?.detail || e?.message || '生成失败'
  } finally {
    generatingLinks.value = false
  }
}

async function downloadGeneratedLinks() {
  try {
    await reviewChannelApi.downloadAccessLinks(activityId.value)
  } catch (e: any) {
    alert('导出失败：' + (e?.response?.data?.detail || e?.message))
  }
}

function formatScope(link: AccessLink): string {
  // Coordinator with wildcard scope or scope is already a string
  if (typeof link.scope === 'string') {
    return link.scope
  }
  // Check if it's an array with wildcard entries (coordinator full access)
  if (Array.isArray(link.scope)) {
    if (link.scope.length === 0) {
      return '活动全量'
    }
    const first = link.scope[0]
    if (first && (first.grade_band === '*' || first.subject === '*')) {
      return '活动全量'
    }
    // Regular judge with specific scopes
    return link.scope.map((s: any) => `${s.grade_band}-${s.subject}`).join('；')
  }
  return '活动全量'
}

async function copyLink(link: AccessLink) {
  try {
    await navigator.clipboard.writeText(link.url)
    const idx = generatedLinks.value.indexOf(link)
    copiedLinkId.value = idx
    setTimeout(() => {
      copiedLinkId.value = null
    }, 1600)
  } catch {
    alert('复制失败，请手动复制')
  }
}

async function recomputeSummary() {
  try {
    await reviewChannelApi.recomputeSummary(activityId.value)
    alert('重新计算完成')
  } catch (e: any) {
    alert('重新计算失败：' + (e?.response?.data?.detail || e?.message))
  }
}

function goBack() {
  router.push('/admin/review-channel')
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    // 加载分配列信息（这会触发活动存在性检查）
    await loadAssignmentColumns()
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '加载活动信息失败'
  } finally {
    loading.value = false
  }
})
</script>
