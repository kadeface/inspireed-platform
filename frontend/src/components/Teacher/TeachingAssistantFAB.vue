<template>
  <!-- 浮动助手按钮 -->
  <Teleport to="body">
    <Transition name="fab-fade">
      <div v-if="visible" class="teaching-assistant-fab-container">
        <!-- 快捷菜单 -->
        <Transition name="menu-slide">
          <div v-if="showMenu" class="fab-menu">
            <div class="fab-menu-header">
              <h3 class="fab-menu-title">教学助手</h3>
              <button
                @click="showMenu = false"
                class="fab-menu-close"
                title="关闭菜单"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div class="fab-menu-content">
              <!-- 提示信息（如果没有班级ID） -->
              <div v-if="!classroomId" class="fab-menu-tip">
                <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="fab-menu-tip-text">请先发布教案并选择班级</span>
              </div>

              <!-- 点名考勤 -->
              <button
                @click="handleAttendance"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '请先选择班级' : '快速点名'"
              >
                <div class="fab-menu-item-icon bg-blue-500">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="fab-menu-item-content">
                  <div class="fab-menu-item-title">点名考勤</div>
                  <div class="fab-menu-item-desc">快速记录学生出勤</div>
                </div>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- 课堂表现 -->
              <button
                @click="handlePositiveBehavior"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '请先选择班级' : '记录课堂表现'"
              >
                <div class="fab-menu-item-icon bg-green-500">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                  </svg>
                </div>
                <div class="fab-menu-item-content">
                  <div class="fab-menu-item-title">课堂表现</div>
                  <div class="fab-menu-item-desc">记录积极表现</div>
                </div>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- 纪律记录 -->
              <button
                @click="handleDiscipline"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '请先选择班级' : '记录纪律'"
              >
                <div class="fab-menu-item-icon bg-amber-500">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="fab-menu-item-content">
                  <div class="fab-menu-item-title">纪律记录</div>
                  <div class="fab-menu-item-desc">记录课堂纪律</div>
                </div>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- 值日管理 -->
              <button
                @click="handleDuty"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '请先选择班级' : '查看值日安排'"
              >
                <div class="fab-menu-item-icon bg-purple-500">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="fab-menu-item-content">
                  <div class="fab-menu-item-title">值日管理</div>
                  <div class="fab-menu-item-desc">查看值日安排</div>
                </div>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>

              <!-- 班级助手 -->
              <button
                @click="handleClassAssistant"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '请先选择班级' : '进入班级助手'"
              >
                <div class="fab-menu-item-icon bg-indigo-500">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <div class="fab-menu-item-content">
                  <div class="fab-menu-item-title">班级助手</div>
                  <div class="fab-menu-item-desc">进入完整功能</div>
                </div>
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        </Transition>

        <!-- 主按钮 -->
        <button
          @click="toggleMenu"
          class="fab-button"
          :class="{ 'fab-button-active': showMenu }"
          :title="showMenu ? '关闭菜单' : '打开教学助手'"
        >
          <Transition name="icon-rotate" mode="out-in">
            <svg
              v-if="!showMenu"
              key="menu"
              class="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg
              v-else
              key="close"
              class="w-6 h-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </Transition>
        </button>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  visible: boolean
  classroomId?: number | null
}>()

const router = useRouter()
const showMenu = ref(false)

const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

// 关闭菜单（点击外部区域）
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.teaching-assistant-fab-container')) {
    showMenu.value = false
  }
}

// 监听菜单显示状态，添加/移除点击外部关闭的监听
watch(showMenu, (isOpen) => {
  if (isOpen) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})

const emit = defineEmits<{
  'open-drawer': [type: 'attendance' | 'behavior' | 'discipline' | 'duty']
}>()

// 处理点名考勤
const handleAttendance = () => {
  if (!props.classroomId) {
    alert('请先选择班级')
    return
  }
  emit('open-drawer', 'attendance')
  showMenu.value = false
}

// 处理课堂表现
const handlePositiveBehavior = () => {
  if (!props.classroomId) {
    alert('请先选择班级')
    return
  }
  emit('open-drawer', 'behavior')
  showMenu.value = false
}

// 处理纪律记录
const handleDiscipline = () => {
  if (!props.classroomId) {
    alert('请先选择班级')
    return
  }
  emit('open-drawer', 'discipline')
  showMenu.value = false
}

// 处理值日管理
const handleDuty = () => {
  if (!props.classroomId) {
    alert('请先选择班级')
    return
  }
  emit('open-drawer', 'duty')
  showMenu.value = false
}

// 处理班级助手
const handleClassAssistant = () => {
  if (!props.classroomId) {
    router.push('/teacher/class-assistant')
  } else {
    router.push(`/teacher/class-assistant`)
  }
  showMenu.value = false
}
</script>

<style scoped>
.teaching-assistant-fab-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.fab-button {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4), 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: white;
}

.fab-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5), 0 4px 8px rgba(0, 0, 0, 0.15);
}

.fab-button:active {
  transform: scale(0.95);
}

.fab-button-active {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4), 0 2px 4px rgba(0, 0, 0, 0.1);
}

.fab-menu {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 4px 16px rgba(0, 0, 0, 0.08);
  min-width: 320px;
  max-width: 400px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.fab-menu-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.fab-menu-title {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

.fab-menu-close {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.fab-menu-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.fab-menu-content {
  padding: 8px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}

.fab-menu-item {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
  text-align: left;
  margin-bottom: 4px;
}

.fab-menu-item:hover:not(:disabled) {
  background: #f3f4f6;
  transform: translateX(4px);
}

.fab-menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fab-menu-item-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.fab-menu-item-content {
  flex: 1;
  min-width: 0;
}

.fab-menu-item-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.fab-menu-item-desc {
  font-size: 13px;
  color: #6b7280;
}

/* 动画 */
.fab-fade-enter-active,
.fab-fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-fade-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.fab-fade-leave-to {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.menu-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.icon-rotate-enter-active,
.icon-rotate-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.icon-rotate-enter-from {
  opacity: 0;
  transform: rotate(-90deg);
}

.icon-rotate-leave-to {
  opacity: 0;
  transform: rotate(90deg);
}

/* 滚动条样式 */
.fab-menu-content::-webkit-scrollbar {
  width: 6px;
}

.fab-menu-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.fab-menu-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.fab-menu-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.fab-menu-tip {
  padding: 12px 16px;
  margin-bottom: 8px;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.fab-menu-tip-text {
  font-size: 13px;
  color: #92400e;
  font-weight: 500;
}
</style>

