<template>
  <div v-if="showDisplay" class="waiting-students-banner">
    <div class="waiting-banner-content">
      <div class="waiting-banner-icon">⏳</div>
      <div class="waiting-banner-text">
        <div class="waiting-banner-title">
          <span v-if="activeCount === 0">讲授型模式：可随时开始上课</span>
          <template v-else>
            互动型模式
            <span class="student-count-badge">{{ activeCount }} 人已加入</span>
          </template>
        </div>
        <div class="waiting-banner-subtitle">
          <span v-if="activeCount === 0">
            讲授型模式：无学生时可直接开始上课，将以幻灯片模式展示
          </span>
          <span v-else>
            互动型模式：已有 {{ activeCount }} 名学生加入，可以开始上课
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  sessionStatus?: string
  activeCount?: number
  showDisplay?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  sessionStatus: 'PREPARING',
  activeCount: 0,
  showDisplay: true
})

// 只在PREPARING状态显示
const showDisplay = computed(() => {
  const normalizedStatus = props.sessionStatus.toUpperCase()
  return normalizedStatus === 'PREPARING' && props.showDisplay
})

import { computed } from 'vue'
</script>

<style scoped>
.waiting-students-banner {
  margin-bottom: 1rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.waiting-banner-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.waiting-banner-icon {
  font-size: 2rem;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.waiting-banner-text {
  flex: 1;
}

.waiting-banner-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e40af;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.student-count-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: #3b82f6;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 9999px;
  animation: popIn 0.3s ease-out;
}

@keyframes popIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.waiting-banner-subtitle {
  font-size: 0.875rem;
  color: #64748b;
}
</style>
