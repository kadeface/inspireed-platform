<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <div class="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div class="text-sm text-emerald-700 font-medium">学习中心</div>
          <h1 class="text-2xl font-bold text-slate-900 mt-1">个性化学习</h1>
          <p class="mt-2 text-sm text-slate-600 max-w-xl">
            想学什么就直接开始：自主学习让 AI 按你的目标开讲，遇到具体题目用答疑解惑，学过的内容会自动沉淀进你的知识库。
          </p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 bg-white/80 hover:bg-white"
          @click="router.push('/student')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          返回工作台
        </button>
      </div>

      <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <button
          v-for="card in cards"
          :key="card.id"
          class="group text-left rounded-2xl bg-white/90 backdrop-blur-sm border border-white/60 shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02] p-6"
          @click="router.push(card.to)"
        >
          <div class="text-4xl mb-4 transform group-hover:scale-110 transition-transform">{{ card.icon }}</div>
          <h2 class="text-lg font-semibold text-slate-900">{{ card.title }}</h2>
          <p class="mt-2 text-sm text-slate-600 leading-relaxed">{{ card.description }}</p>
          <div class="mt-4 text-sm font-medium text-emerald-600 flex items-center gap-1">
            <span>{{ card.action }}</span>
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const cards = [
  {
    id: 'self-directed',
    icon: '🧭',
    title: '自主学习',
            description: '说出你想学的知识点，AI 生成一节微课；学完会沉淀进知识库。',
    action: '开始自主学习',
    to: '/student/self-directed',
  },
  {
    id: 'qa',
    icon: '💬',
    title: '答疑解惑',
    description: '拍一道已做完的题，选择助教风格，让 AI 陪你检查、讲明白。',
    action: '去答疑解惑',
    to: '/student/self-study',
  },
  {
    id: 'knowledge-base',
    icon: '📚',
    title: '知识库',
    description: '你学过的知识点、参考卡和错题都会沉淀在这里，从空开始，越学越厚。',
    action: '查看我的知识库',
    to: '/student/knowledge-base',
  },
]
</script>
