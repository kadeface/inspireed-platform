<template>
  <section class="unfinished-session-choice" data-testid="unfinished-session-choice">
    <h3 class="choice-title">上一节课尚未结束</h3>
    <p class="choice-lead">可以继续上一节，或结束授课后再创建课堂。</p>
    <ul class="choice-list">
      <li v-for="item in rows" :key="item.id" class="choice-row" :data-session-id="item.id">
        <div class="choice-copy">
          <div class="choice-heading">
            {{ item.classroomLabel }}
            <span class="choice-status">{{ item.statusLabel }}</span>
          </div>
          <p class="choice-detail">{{ item.detail }}</p>
          <p v-if="item.whenLabel" class="choice-time">{{ item.whenLabel }}</p>
        </div>
        <div class="choice-actions">
          <button
            type="button"
            class="choice-btn choice-btn-continue"
            data-testid="continue-unfinished-session"
            :disabled="loading"
            @click="$emit('continue', item.id)"
          >
            继续上一节
          </button>
          <button
            type="button"
            class="choice-btn choice-btn-replace"
            data-testid="end-unfinished-session"
            :disabled="loading"
            @click="$emit('end', item.session)"
          >
            结束授课
          </button>
        </div>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { isHiddenFromStudents } from '@/utils/activeSessionConflict'

interface SessionChoice {
  id: number
  status?: string
  classroomId?: number
  classroom_id?: number
  classroomName?: string
  createdAt?: string
  created_at?: string
  actualStart?: string
  actual_start?: string
}

const props = withDefaults(
  defineProps<{
    sessions: SessionChoice[]
    classroomNames?: Record<number, string>
    loading?: boolean
  }>(),
  {
    classroomNames: () => ({}),
    loading: false,
  },
)

defineEmits<{
  continue: [sessionId: number]
  end: [session: SessionChoice]
}>()

function statusLabel(status: string | undefined): string {
  const normalized = String(status || '').toLowerCase()
  if (normalized === 'teaching' || normalized === 'active') return '上课中'
  if (normalized === 'preparing' || normalized === 'pending') return '准备中'
  return '未结束'
}

function timeSource(session: SessionChoice): string | undefined {
  const normalized = String(session.status || '').toLowerCase()
  if (normalized === 'teaching' || normalized === 'active') {
    return session.actualStart || session.actual_start || session.createdAt || session.created_at
  }
  return session.createdAt || session.created_at
}

function formatWhen(session: SessionChoice): string {
  const raw = timeSource(session)
  if (!raw) return ''
  const date = new Date(raw)
  if (Number.isNaN(date.getTime())) return ''
  const normalized = String(session.status || '').toLowerCase()
  const prefix = normalized === 'teaching' || normalized === 'active' ? '开始于' : '创建于'
  return `${prefix} ${date.toLocaleString('zh-CN', { hour12: false })}`
}

const rows = computed(() =>
  (props.sessions ?? []).map((session) => {
    const classroomId = session.classroomId ?? session.classroom_id
    const classroomLabel =
      session.classroomName ||
      (classroomId != null ? props.classroomNames[classroomId] : '') ||
      (classroomId != null ? `班级 ${classroomId}` : '未指定班级')
    const hidden = isHiddenFromStudents(session)
    return {
      id: session.id,
      session,
      classroomLabel,
      statusLabel: statusLabel(session.status),
      whenLabel: formatWhen(session),
      detail: hidden
        ? '学生端已经看不到这节课。'
        : '学生端仍可进入这节课。',
    }
  }),
)
</script>

<style scoped>
.unfinished-session-choice {
  margin: 0.75rem 1rem 0;
  padding: 0.9rem 1rem;
  border: 1px solid #fcd34d;
  border-radius: 0.75rem;
  background: #fffbeb;
}

.choice-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #92400e;
}

.choice-lead {
  margin: 0.25rem 0 0.75rem;
  font-size: 0.8rem;
  color: #78350f;
}

.choice-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.choice-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: space-between;
}

.choice-heading {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.choice-status {
  margin-left: 0.4rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #b45309;
}

.choice-detail,
.choice-time {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  color: #6b7280;
}

.choice-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.choice-btn {
  height: 34px;
  padding: 0 0.75rem;
  border-radius: 0.7rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.choice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.choice-btn-continue {
  border: 1px solid transparent;
  color: white;
  background: linear-gradient(to right, #10b981, #14b8a6);
}

.choice-btn-replace {
  border: 1px solid #fcd34d;
  color: #92400e;
  background: white;
}
</style>
