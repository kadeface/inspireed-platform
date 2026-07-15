<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div class="flex items-center justify-between gap-4">
        <div>
          <div class="text-sm text-slate-500">个性化学习 · 自主学习</div>
          <h1 class="text-2xl font-bold text-slate-900">自主学习</h1>
          <p class="mt-1 text-sm text-slate-600">
            想学什么，直接说出来。AI 会按你的目标生成一节微课，学完会沉淀进知识库。
          </p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white"
          @click="router.push('/student/personalized-learning')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          返回
        </button>
      </div>

      <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">我想学的知识点</h2>
          <p class="mt-1 text-sm text-slate-600">
            例如：分数加法、三角形面积、乘法竖式……写清楚你想弄懂的内容。
          </p>
        </div>
        <textarea
          v-model="goal"
          rows="3"
          class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="我想学会……"
        />

        <div>
          <h3 class="text-sm font-semibold text-slate-900">为什么学（可选）</h3>
          <p class="mt-1 text-xs text-slate-500">学了之后你想能做什么？有助于生成更贴合的一课。</p>
          <textarea
            v-model="missionWhy"
            rows="2"
            class="mt-2 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            placeholder="例如：作业里总卡在通分，想自己能讲清楚。"
          />
        </div>

        <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ errorMessage }}
        </div>

        <button
          class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
          :disabled="!goal.trim() || submitting"
          @click="startLearning"
        >
          {{ submitting ? '正在生成微课，请稍候…' : '开始学习' }}
        </button>
      </div>

      <div class="rounded-2xl bg-white p-6 shadow-sm space-y-3">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">老师推荐的学习路径</h2>
            <p class="mt-1 text-sm text-slate-600">还没想好学什么？可以从老师排好的路径里选一个开始。</p>
          </div>
          <button
            class="shrink-0 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-sm font-medium"
            @click="router.push('/student/learning-paths')"
          >
            浏览推荐路径
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import selfDirectedService from '@/services/selfDirected'

const router = useRouter()

const goal = ref('')
const missionWhy = ref('')
const submitting = ref(false)
const errorMessage = ref('')

async function startLearning() {
  if (!goal.value.trim() || submitting.value) return
  submitting.value = true
  errorMessage.value = ''
  try {
    const session = await selfDirectedService.createSession({
      goal_text: goal.value.trim(),
      mission_why: missionWhy.value.trim() || undefined,
    })
    await router.push(`/student/self-directed/session/${session.id}`)
  } catch (error: any) {
    errorMessage.value = error.message || '创建学习会话失败'
  } finally {
    submitting.value = false
  }
}
</script>
