<template>
  <div class="min-h-screen bg-slate-50">
    <main class="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
      <header class="mb-6 flex items-center justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div>
          <h1 class="text-xl font-bold text-slate-900">作品评审通道管理</h1>
          <p class="mt-1 text-sm text-slate-600">管理评审活动、导入作品、分配评委任务</p>
        </div>
        <button
          type="button"
          class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          @click="showCreateDialog = true"
        >
          创建新活动
        </button>
      </header>

      <!-- 创建活动对话框 -->
      <div
        v-if="showCreateDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
        @click.self="showCreateDialog = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl" @click.stop>
          <h2 class="mb-4 text-lg font-bold text-slate-900">创建评审活动</h2>
          <form @submit.prevent="handleCreateActivity">
            <div class="mb-4">
              <label class="mb-1 block text-sm font-medium text-slate-700">活动名称 *</label>
              <input
                v-model="createForm.name"
                type="text"
                required
                class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
                placeholder="例如：2026年春季作品评审"
              />
            </div>
            <div class="mb-4">
              <label class="mb-1 block text-sm font-medium text-slate-700">活动描述</label>
              <textarea
                v-model="createForm.description"
                rows="3"
                class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
                placeholder="描述评审活动的目的、范围等"
              />
            </div>
            <div class="mb-4 grid grid-cols-2 gap-4">
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">开始时间</label>
                <input
                  v-model="createForm.starts_at"
                  type="datetime-local"
                  class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-slate-700">结束时间</label>
                <input
                  v-model="createForm.ends_at"
                  type="datetime-local"
                  class="w-full rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
                />
              </div>
            </div>
            <div v-if="createError" class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
              {{ createError }}
            </div>
            <div class="flex justify-end gap-3">
              <button
                type="button"
                class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                @click="showCreateDialog = false"
              >
                取消
              </button>
              <button
                type="submit"
                class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                :disabled="creating"
              >
                {{ creating ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 活动列表 -->
      <section v-if="activities.length === 0 && !loading" class="rounded-2xl border border-slate-200 bg-white p-10 text-center text-slate-500">
        <p class="mb-4 text-lg">暂无评审活动</p>
        <button
          type="button"
          class="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          @click="showCreateDialog = true"
        >
          创建第一个活动
        </button>
      </section>

      <section v-else class="space-y-4">
        <div
          v-for="activity in activities"
          :key="activity.activity_id"
          class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow-md"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-slate-900">{{ activity.name }}</h3>
              <p v-if="activity.description" class="mt-1 text-sm text-slate-600">{{ activity.description }}</p>
              <div class="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
                <span class="rounded-full bg-slate-100 px-2 py-1">ID: {{ activity.activity_id }}</span>
                <span v-if="activity.status" class="rounded-full bg-indigo-100 px-2 py-1 text-indigo-700">
                  {{ activity.status === 'active' ? '进行中' : activity.status }}
                </span>
                <span v-if="activity.created_at">
                  创建于 {{ new Date(activity.created_at).toLocaleDateString('zh-CN') }}
                </span>
              </div>
            </div>
            <router-link
              :to="`/admin/review-channel/${activity.activity_id}`"
              class="ml-4 rounded-xl border border-indigo-300 bg-indigo-50 px-4 py-2 text-sm font-medium text-indigo-700 hover:bg-indigo-100"
            >
              查看详情
            </router-link>
          </div>
        </div>
      </section>

      <!-- 手动输入活动ID访问（用于测试） -->
      <section class="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 class="mb-3 text-sm font-semibold text-slate-800">通过活动ID访问</h2>
        <div class="flex gap-3">
          <input
            v-model="manualActivityId"
            type="text"
            class="flex-1 rounded-xl border border-slate-300 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            placeholder="输入活动ID，例如：act_20260409_499b345c"
          />
          <router-link
            :to="`/admin/review-channel/${manualActivityId}`"
            class="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            进入
          </router-link>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reviewChannelApi, type ReviewActivity, type CreateActivityPayload } from '@/services/reviewChannel'

const router = useRouter()

const showCreateDialog = ref(false)
const creating = ref(false)
const createError = ref('')
const loading = ref(false)
const activities = ref<ReviewActivity[]>([])
const manualActivityId = ref('')

const createForm = ref<CreateActivityPayload>({
  name: '',
  description: '',
  starts_at: '',
  ends_at: '',
})

async function handleCreateActivity() {
  createError.value = ''
  if (!createForm.value.name.trim()) {
    createError.value = '请输入活动名称'
    return
  }
  creating.value = true
  try {
    const result = await reviewChannelApi.createActivity(createForm.value)
    showCreateDialog.value = false
    createForm.value = { name: '', description: '', starts_at: '', ends_at: '' }
    router.push(`/admin/review-channel/${result.activity_id}`)
  } catch (e: any) {
    createError.value = e?.response?.data?.detail || e?.message || '创建失败'
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  // 可以在这里加载活动列表（如果后端提供了列表接口）
  // 目前先显示手动输入的方式
})
</script>
