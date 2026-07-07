<template>
  <div class="min-h-screen bg-slate-50">
    <div class="max-w-6xl mx-auto px-4 py-6 space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <div class="text-sm text-slate-500">教师处理详情</div>
          <h1 class="text-2xl font-bold text-slate-900">个性化学习求助 #{{ route.params.id }}</h1>
        </div>
        <button
          class="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-white"
          @click="router.push('/teacher/self-study/handoffs')"
        >
          返回队列
        </button>
      </div>

      <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ errorMessage }}
      </div>

      <div v-if="loading" class="rounded-2xl bg-white p-8 shadow-sm text-center text-slate-500">
        加载中...
      </div>

      <template v-else-if="detail">
        <div class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div class="space-y-6">
            <div class="rounded-2xl bg-white p-6 shadow-sm">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <h2 class="text-lg font-semibold text-slate-900">{{ detail.title }}</h2>
                  <p class="mt-1 text-sm text-slate-500">
                    {{ detail.student_name }} · 会话 #{{ detail.session_id }} · {{ new Date(detail.created_at).toLocaleString() }}
                  </p>
                </div>
                <span class="px-2 py-1 rounded bg-slate-100 text-xs text-slate-600">
                  {{ detail.status }}
                </span>
              </div>

              <div class="mt-6 grid gap-4 md:grid-cols-2">
                <div class="rounded-xl border border-slate-200 overflow-hidden">
                  <div class="px-4 py-2 bg-slate-50 text-sm font-medium text-slate-700">原始题图</div>
                  <img :src="detail.original_image_url" alt="原始题图" class="w-full max-h-[420px] object-contain bg-slate-100" />
                </div>
                <div class="rounded-xl border border-slate-200 overflow-hidden">
                  <div class="px-4 py-2 bg-slate-50 text-sm font-medium text-slate-700">修正后题图</div>
                  <img
                    v-if="detail.revised_image_url"
                    :src="detail.revised_image_url"
                    alt="修正后题图"
                    class="w-full max-h-[420px] object-contain bg-slate-100"
                  />
                  <div v-else class="flex items-center justify-center h-[240px] bg-slate-50 text-sm text-slate-400">
                    学生暂未重新上传
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
              <div class="text-sm text-slate-600">
                <div class="font-medium text-slate-900 mb-1">学生确认后的提问</div>
                {{ detail.question_text_confirmed || '暂无' }}
              </div>
              <div class="text-sm text-slate-600">
                <div class="font-medium text-slate-900 mb-1">原始语音转写</div>
                {{ detail.voice_transcript_raw || '暂无' }}
              </div>
              <div class="text-sm text-slate-600">
                <div class="font-medium text-slate-900 mb-1">AI 最近引导摘要</div>
                <ul class="list-disc pl-5 space-y-1">
                  <li v-for="item in detail.ai_guidance_summary" :key="item">{{ item }}</li>
                </ul>
              </div>
              <div class="text-sm text-slate-600">
                <div class="font-medium text-slate-900 mb-1">学生最后的困惑</div>
                {{ detail.student_last_confusion || '暂无' }}
              </div>
              <div class="grid gap-4 md:grid-cols-2 text-sm text-slate-600">
                <div class="rounded-xl bg-slate-50 px-4 py-3">
                  <div class="font-medium text-slate-900 mb-1">我原来为什么错</div>
                  {{ detail.summary_before || '暂无' }}
                </div>
                <div class="rounded-xl bg-slate-50 px-4 py-3">
                  <div class="font-medium text-slate-900 mb-1">我现在为什么知道改对了</div>
                  {{ detail.summary_after || '暂无' }}
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="rounded-2xl bg-white p-6 shadow-sm space-y-4">
              <div>
                <h2 class="text-lg font-semibold text-slate-900">教师回复</h2>
                <p class="mt-1 text-sm text-slate-600">
                  第一版只提交一段文字和一张标注图。
                </p>
              </div>
              <textarea
                v-model="replyText"
                rows="8"
                class="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="请告诉学生：哪里错了、为什么错、应该怎么想。"
              />
              <button
                class="w-full px-4 py-3 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 disabled:opacity-50"
                :disabled="submitting"
                @click="openUpload"
              >
                {{ annotatedImageStorageKey ? '重新上传标注图' : '上传标注图（可选）' }}
              </button>
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                class="hidden"
                @change="onFileChange"
              />
              <div v-if="annotatedImageStorageKey" class="text-xs text-slate-500">
                已上传标注图：{{ annotatedImageStorageKey }}
              </div>
              <button
                class="w-full px-4 py-3 rounded-xl bg-emerald-600 text-white font-medium hover:bg-emerald-700 disabled:opacity-50"
                :disabled="!replyText.trim() || submitting"
                @click="submitReply"
              >
                提交教师回复
              </button>
            </div>

            <div
              v-if="detail.teacher_reply_text || detail.teacher_reply_image_url"
              class="rounded-2xl bg-white p-6 shadow-sm space-y-4"
            >
              <h2 class="text-lg font-semibold text-slate-900">已提交回复</h2>
              <div class="whitespace-pre-wrap text-sm text-slate-700">{{ detail.teacher_reply_text }}</div>
              <img
                v-if="detail.teacher_reply_image_url"
                :src="detail.teacher_reply_image_url"
                alt="教师标注图"
                class="w-full rounded-xl border border-slate-200"
              />
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import selfStudyService from '@/services/selfStudy'
import type { SelfStudyTeacherHandoffDetail } from '@/types/selfStudy'

const route = useRoute()
const router = useRouter()

const detail = ref<SelfStudyTeacherHandoffDetail | null>(null)
const loading = ref(false)
const submitting = ref(false)
const errorMessage = ref<string | null>(null)
const replyText = ref('')
const annotatedImageStorageKey = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

function openUpload() {
  fileInput.value?.click()
}

async function loadDetail() {
  loading.value = true
  errorMessage.value = null
  try {
    detail.value = await selfStudyService.getTeacherHandoff(Number(route.params.id))
    replyText.value = detail.value.teacher_reply_text || ''
  } catch (error: any) {
    errorMessage.value = error.message || '加载教师处理详情失败'
  } finally {
    loading.value = false
  }
}

async function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  submitting.value = true
  errorMessage.value = null
  try {
    annotatedImageStorageKey.value = await selfStudyService.uploadAnnotatedImage(file)
  } catch (error: any) {
    errorMessage.value = error.message || '上传标注图失败'
  } finally {
    submitting.value = false
    target.value = ''
  }
}

async function submitReply() {
  if (!replyText.value.trim()) return
  submitting.value = true
  errorMessage.value = null
  try {
    await selfStudyService.replyTeacherHandoff(Number(route.params.id), {
      reply_text: replyText.value.trim(),
      annotated_image_storage_key: annotatedImageStorageKey.value || undefined,
    })
    await loadDetail()
  } catch (error: any) {
    errorMessage.value = error.message || '提交教师回复失败'
  } finally {
    submitting.value = false
  }
}

onMounted(loadDetail)
</script>
