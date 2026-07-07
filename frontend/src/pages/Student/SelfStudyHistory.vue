<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">个性化学习伴学</div>
          <h1 class="text-2xl font-bold text-slate-900">我的学习记录</h1>
        </div>
        <button
          class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white"
          @click="router.push('/student/self-study')"
        >
          返回个性化学习
        </button>
      </div>

      <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div class="rounded-2xl bg-white shadow-sm overflow-hidden">
        <div v-if="loading" class="p-8 text-center text-slate-500">加载中...</div>
        <div v-else-if="!items.length" class="p-8 text-center text-slate-500">还没有学习记录。</div>
        <div v-else class="divide-y divide-slate-100">
          <button
            v-for="item in items"
            :key="item.id"
            class="w-full px-6 py-5 text-left hover:bg-slate-50 transition-colors"
            @click="router.push(`/student/self-study/session/${item.id}`)"
          >
            <div class="flex flex-col gap-4 md:flex-row md:items-center">
              <img
                :src="item.thumbnail_url"
                alt="缩略图"
                class="w-full md:w-32 h-24 rounded-lg object-cover bg-slate-100 border border-slate-200"
              />
              <div class="flex-1">
                <div class="flex items-center gap-3">
                  <div class="font-semibold text-slate-900">会话 #{{ item.id }}</div>
                  <span class="px-2 py-1 rounded bg-slate-100 text-xs text-slate-600">
                    {{ phaseLabel(item.session_phase) }}
                  </span>
                </div>
                <div class="mt-1 text-sm text-slate-500">
                  {{ resultLabel(item.result_judgment) }} · {{ formatDate(item.created_at) }}
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import selfStudyService from '@/services/selfStudy'
import type { SelfStudyHistoryItem } from '@/types/selfStudy'

const router = useRouter()
const items = ref<SelfStudyHistoryItem[]>([])
const loading = ref(false)
const errorMessage = ref<string | null>(null)

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
    correct_unexplained: '结果对了，但解释不够清楚',
    understood: '已经理解',
    needs_teacher: '老师处理中',
  }
  return (result && map[result]) || '待判断'
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

async function loadHistory() {
  loading.value = true
  errorMessage.value = null
  try {
    const result = await selfStudyService.listHistory({ page: 1, page_size: 50 })
    items.value = result.items
  } catch (error: any) {
    errorMessage.value = error.message || '加载学习记录失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)
</script>
