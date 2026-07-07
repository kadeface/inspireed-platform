<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">教师处理队列</div>
          <h1 class="text-2xl font-bold text-slate-900">个性化学习待处理</h1>
        </div>
        <button
          class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white"
          @click="router.push('/teacher')"
        >
          返回教师工作台
        </button>
      </div>

      <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div class="rounded-2xl bg-white shadow-sm overflow-hidden">
        <div v-if="loading" class="p-8 text-center text-slate-500">加载中...</div>
        <div v-else-if="!items.length" class="p-8 text-center text-slate-500">当前没有待处理记录。</div>
        <div v-else class="divide-y divide-slate-100">
          <button
            v-for="item in items"
            :key="item.id"
            class="w-full px-6 py-5 text-left hover:bg-slate-50 transition-colors"
            @click="router.push(`/teacher/self-study/handoffs/${item.id}`)"
          >
            <div class="flex items-center justify-between gap-4">
              <div>
                <div class="font-semibold text-slate-900">{{ item.title }}</div>
                <div class="mt-1 text-sm text-slate-500">
                  {{ item.student_name }} · 会话 #{{ item.session_id }} · {{ new Date(item.created_at).toLocaleString() }}
                </div>
              </div>
              <span class="px-2 py-1 rounded bg-slate-100 text-xs text-slate-600">
                {{ item.status }}
              </span>
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
import type { SelfStudyTeacherHandoffListItem } from '@/types/selfStudy'

const router = useRouter()
const items = ref<SelfStudyTeacherHandoffListItem[]>([])
const loading = ref(false)
const errorMessage = ref<string | null>(null)

async function loadItems() {
  loading.value = true
  errorMessage.value = null
  try {
    const result = await selfStudyService.listTeacherHandoffs({ page: 1, page_size: 50 })
    items.value = result.items
  } catch (error: any) {
    errorMessage.value = error.message || '加载教师队列失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadItems)
</script>
