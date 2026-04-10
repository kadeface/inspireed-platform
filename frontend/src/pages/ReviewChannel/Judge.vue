<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      <header class="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h1 class="text-xl font-bold text-slate-900">评委评审通道</h1>
        <p class="mt-1 text-sm text-slate-600">活动 {{ activityId }} · {{ sessionName }}</p>
        <div class="mt-3">
          <button
            type="button"
            class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs text-slate-700 hover:bg-slate-50"
            @click="copyCurrentLink"
          >
            复制当前评审链接
          </button>
          <span v-if="copyMessage" class="ml-2 text-xs text-emerald-700">{{ copyMessage }}</span>
        </div>
      </header>

      <section v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
        正在加载评审数据...
      </section>

      <section v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        {{ error }}
      </section>

      <section v-else class="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm lg:col-span-1">
          <div class="mb-3 flex items-center justify-between">
            <h2 class="text-sm font-semibold text-slate-800">作品列表</h2>
            <span class="text-xs text-slate-500">{{ works.length }} 项</span>
          </div>
          <div class="max-h-[68vh] space-y-2 overflow-y-auto pr-1">
            <button
              v-for="item in works"
              :key="item.work_id"
              type="button"
              class="w-full rounded-xl border p-3 text-left transition"
              :class="selectedWork?.work_id === item.work_id ? 'border-emerald-300 bg-emerald-50' : 'border-slate-200 hover:bg-slate-50'"
              @click="selectWork(item.work_id)"
            >
              <p class="text-sm font-semibold text-slate-900">{{ item.work_number }} · {{ item.title }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ item.grade_band }} / {{ item.subject }} / {{ item.school_name || '未填学校' }}</p>
              <p class="mt-1 text-xs flex items-center gap-2">
                <span v-if="item.status === '我已评分'" class="text-emerald-600 font-medium">
                  ✓ 我已评分
                </span>
                <span v-else-if="item.status === '待我评分'" class="text-amber-600">
                  待我评分 · {{ item.review_count }} 位评委已评
                </span>
                <span v-else class="text-slate-400">
                  未评分
                </span>
              </p>
            </button>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <template v-if="selectedWork">
            <div class="mb-4">
              <h2 class="text-lg font-bold text-slate-900">{{ selectedWork.title }}</h2>
              <p class="mt-1 text-sm text-slate-600">
                编号 {{ selectedWork.work_number }} · {{ selectedWork.grade_band }} {{ selectedWork.subject }}
              </p>
              <p class="text-sm text-slate-600">{{ selectedWork.school_name || '未填写学校' }}</p>
            </div>

            <div class="mb-4 flex items-center gap-2">
              <button
                type="button"
                class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                :disabled="selectedIndex <= 0"
                @click="goPrev"
              >
                上一条
              </button>
              <button
                type="button"
                class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                :disabled="selectedIndex < 0 || selectedIndex >= works.length - 1"
                @click="goNext"
              >
                下一条
              </button>
              <span class="text-xs text-slate-500" v-if="selectedIndex >= 0">
                {{ selectedIndex + 1 }} / {{ works.length }}
              </span>
            </div>

            <div class="mb-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h3 class="mb-3 text-sm font-semibold text-slate-800">附件链接</h3>
              <div class="space-y-2">
                <a
                  v-for="(att, idx) in selectedWork.attachments"
                  :key="`${att.url}-${idx}`"
                  :href="att.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
                >
                  <span>{{ att.name || '附件' }} <span class="text-slate-400">({{ att.format || '未知格式' }})</span></span>
                  <span class="text-emerald-600">打开</span>
                </a>
              </div>
            </div>

            <!-- 评分说明 -->
            <div class="mb-4 rounded-lg bg-blue-50 border border-blue-200 p-3 text-sm text-blue-800">
              <p class="font-medium mb-1">💡 评分说明</p>
              <ul class="list-disc list-inside space-y-1 text-xs">
                <li><strong>✓ 我已评分</strong>：您已经提交过评分，可以继续修改</li>
                <li><strong>待我评分</strong>：其他评委已评分，但您还没有评</li>
                <li><strong>未评分</strong>：该作品还没有任何评委评分</li>
                <li>每位评委独立评分，作品的最终分数是所有评委的平均值</li>
              </ul>
            </div>

            <form class="space-y-4" @submit.prevent="submitCurrentScore">
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">评分（0-100）</label>
                <input
                  v-model.number="scoreTotal"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">评语</label>
                <textarea
                  v-model="comment"
                  rows="5"
                  class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-emerald-500"
                  placeholder="请输入评语"
                />
              </div>
              <div class="flex items-center gap-3">
                <button
                  type="submit"
                  class="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                  :disabled="submitting"
                >
                  {{ submitting ? '提交中...' : '提交评分' }}
                </button>
                <span v-if="submitMessage" class="text-sm text-emerald-700">{{ submitMessage }}</span>
              </div>
            </form>
          </template>

          <template v-else>
            <p class="text-sm text-slate-500">请选择左侧作品后评分。</p>
          </template>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { reviewChannelApi, type ReviewWork } from '@/services/reviewChannel'

const route = useRoute()

const activityId = computed(() => String(route.query.activity_id || ''))
const token = computed(() => String(route.query.token || ''))

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const submitMessage = ref('')
const sessionName = ref('')
const copyMessage = ref('')

const works = ref<ReviewWork[]>([])
const selectedWorkId = ref('')
const selectedWork = computed(() => works.value.find((x) => x.work_id === selectedWorkId.value) || null)
const selectedIndex = computed(() => works.value.findIndex((x) => x.work_id === selectedWorkId.value))
const unscoredQueue = computed(() => works.value.filter((x) => (x.status || '未评分') === '未评分'))

const scoreTotal = ref<number>(0)
const comment = ref('')

function selectWork(workId: string) {
  selectedWorkId.value = workId
  submitMessage.value = ''
  scoreTotal.value = 0
  comment.value = ''
}

function goPrev() {
  if (selectedIndex.value <= 0) return
  const target = works.value[selectedIndex.value - 1]
  if (target) selectWork(target.work_id)
}

function goNext() {
  if (selectedIndex.value < 0 || selectedIndex.value >= works.value.length - 1) return
  const target = works.value[selectedIndex.value + 1]
  if (target) selectWork(target.work_id)
}

function pickNextUnscored(excludeWorkId: string): string | null {
  const target = unscoredQueue.value.find((x) => x.work_id !== excludeWorkId)
  return target ? target.work_id : null
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    if (!activityId.value || !token.value) {
      throw new Error('缺少 activity_id 或 token')
    }
    const session = await reviewChannelApi.getSession(token.value, activityId.value)
    if (session.role !== 'judge') {
      throw new Error('当前链接不是评委入口')
    }
    sessionName.value = session.name || '评委'

    const list = await reviewChannelApi.listWorks(activityId.value, token.value)
    works.value = list.items || []
    if (works.value.length > 0) {
      selectedWorkId.value = works.value[0].work_id
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function submitCurrentScore() {
  if (!selectedWork.value) return
  submitMessage.value = ''
  if (scoreTotal.value < 0 || scoreTotal.value > 100) {
    error.value = '评分范围应在 0-100'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await reviewChannelApi.submitScore(activityId.value, selectedWork.value.work_id, token.value, {
      score_total: scoreTotal.value,
      comment: comment.value,
    })
    submitMessage.value = '提交成功'
    const submittedWorkId = selectedWork.value.work_id
    const list = await reviewChannelApi.listWorks(activityId.value, token.value)
    works.value = list.items || []
    const nextUnscoredId = pickNextUnscored(submittedWorkId)
    if (nextUnscoredId) {
      selectWork(nextUnscoredId)
    } else {
      const currentIdx = works.value.findIndex((x) => x.work_id === submittedWorkId)
      if (currentIdx >= 0 && currentIdx < works.value.length - 1) {
        selectWork(works.value[currentIdx + 1].work_id)
      } else if (currentIdx >= 0) {
        selectWork(works.value[currentIdx].work_id)
      }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '提交失败'
  } finally {
    submitting.value = false
  }
}

onMounted(loadData)

async function copyCurrentLink() {
  copyMessage.value = ''
  try {
    await navigator.clipboard.writeText(window.location.href)
    copyMessage.value = '已复制'
    window.setTimeout(() => {
      copyMessage.value = ''
    }, 1600)
  } catch {
    copyMessage.value = '复制失败'
  }
}
</script>

