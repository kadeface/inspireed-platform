<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div class="flex items-center justify-between gap-4">
        <div>
          <div class="text-sm text-slate-500">个性化学习 · 知识库</div>
          <h1 class="text-2xl font-bold text-slate-900">我的知识库</h1>
          <p class="mt-1 text-sm text-slate-600">
            完成答疑解惑并写完总结后，笔记会沉淀在这里，供下次答疑作为先前知识。
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white text-sm"
            @click="router.push('/student/self-study/history')"
          >
            答疑记录
          </button>
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
      </div>

      <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div class="grid gap-6 lg:grid-cols-[280px_1fr]">
        <div class="rounded-2xl bg-white shadow-sm overflow-hidden">
          <div class="px-4 py-3 border-b border-slate-100 text-sm font-semibold text-slate-800">
            笔记列表
          </div>
          <div v-if="loading" class="p-6 text-sm text-slate-500">加载中...</div>
          <div v-else-if="!notes.length" class="p-6 text-sm text-slate-500 leading-relaxed">
            你的知识库还是空的。去完成一次答疑解惑并写完「原来为什么错 / 现在为什么对了」总结后，笔记会出现在这里。
          </div>
          <div v-else class="max-h-[70vh] overflow-y-auto divide-y divide-slate-100">
            <button
              v-for="item in notes"
              :key="item.path"
              type="button"
              class="w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors"
              :class="selectedPath === item.path ? 'bg-emerald-50' : ''"
              @click="openNote(item.path)"
            >
              <div class="text-sm font-medium text-slate-900 truncate">{{ item.title }}</div>
              <div class="mt-0.5 text-xs text-slate-500 truncate">{{ item.path }}</div>
            </button>
          </div>
        </div>

        <div class="rounded-2xl bg-white shadow-sm min-h-[420px]">
          <div v-if="contentLoading" class="p-8 text-sm text-slate-500">正在打开笔记...</div>
          <div v-else-if="!selectedNote" class="p-8 text-sm text-slate-500">
            从左侧选择一篇笔记查看。
          </div>
          <div v-else class="p-6 space-y-4">
            <div>
              <h2 class="text-xl font-semibold text-slate-900">{{ selectedNote.title }}</h2>
              <div class="mt-1 text-xs text-slate-500">{{ selectedNote.path }}</div>
            </div>
            <div
              class="prose prose-slate max-w-none text-sm leading-relaxed"
              v-html="renderedHtml"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import knowledgeBaseService, {
  type KnowledgeBaseNoteContent,
  type KnowledgeBaseNoteItem,
} from '@/services/knowledgeBase'
import { markdownToHtml } from '@/utils/lessonEditorHelpers'

const router = useRouter()

const loading = ref(false)
const contentLoading = ref(false)
const errorMessage = ref('')
const notes = ref<KnowledgeBaseNoteItem[]>([])
const selectedPath = ref('')
const selectedNote = ref<KnowledgeBaseNoteContent | null>(null)

const renderedHtml = computed(() => {
  if (!selectedNote.value?.content_markdown) return ''
  return markdownToHtml(selectedNote.value.content_markdown)
})

async function loadNotes() {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await knowledgeBaseService.listNotes()
    notes.value = data.items || []
    if (notes.value.length && !selectedPath.value) {
      await openNote(notes.value[0].path)
    }
  } catch (error: any) {
    errorMessage.value = error.message || '加载知识库失败'
  } finally {
    loading.value = false
  }
}

async function openNote(path: string) {
  selectedPath.value = path
  contentLoading.value = true
  errorMessage.value = ''
  try {
    selectedNote.value = await knowledgeBaseService.getNote(path)
  } catch (error: any) {
    selectedNote.value = null
    errorMessage.value = error.message || '加载笔记失败'
  } finally {
    contentLoading.value = false
  }
}

onMounted(loadNotes)
</script>
