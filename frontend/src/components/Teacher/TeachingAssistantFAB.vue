<template>
  <!-- 嵌入极简浮动导播台：与「模块切换」面板同层，菜单在按钮上方展开 -->
  <div
    v-if="layout === 'embedded' && visible"
    class="teaching-assistant-fab-container teaching-assistant-fab-container--embedded"
  >
    <Transition name="menu-slide">
      <div v-if="showMenu" class="fab-menu fab-menu--embedded">
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
                <span class="fab-menu-tip-text">请先发布教案，上课时选择班级</span>
              </div>

              <!-- 点名考勤 -->
              <button
                @click="handleAttendance"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '上课时选择班级后可用' : '快速点名'"
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
                :title="!classroomId ? '上课时选择班级后可用' : '记录课堂表现'"
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
                :title="!classroomId ? '上课时选择班级后可用' : '记录纪律'"
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
                :title="!classroomId ? '上课时选择班级后可用' : '查看值日安排'"
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

            </div>
          </div>
    </Transition>
    <button
      type="button"
      @click="toggleMenu"
      class="fab-button fab-button--embedded"
      :class="{ 'fab-button-active': showMenu }"
      :title="embeddedFabTitle"
      :aria-label="embeddedFabAriaLabel"
    >
      <Transition name="icon-rotate" mode="out-in">
        <svg
          v-if="!showMenu"
          key="menu"
          class="fab-button-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
        <svg
          v-else
          key="close"
          class="fab-button-icon"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </Transition>
    </button>
  </div>

  <!-- 默认：视口角落浮动按钮 -->
  <Teleport v-if="layout !== 'embedded'" to="body">
    <Transition name="fab-fade">
      <div v-if="visible" class="teaching-assistant-fab-container">
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
              <div v-if="!classroomId" class="fab-menu-tip">
                <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="fab-menu-tip-text">请先发布教案，上课时选择班级</span>
              </div>

              <button
                @click="handleAttendance"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '上课时选择班级后可用' : '快速点名'"
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

              <button
                @click="handlePositiveBehavior"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '上课时选择班级后可用' : '记录课堂表现'"
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

              <button
                @click="handleDiscipline"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '上课时选择班级后可用' : '记录纪律'"
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

              <button
                @click="handleDuty"
                class="fab-menu-item"
                :disabled="!classroomId"
                :title="!classroomId ? '上课时选择班级后可用' : '查看值日安排'"
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

            </div>
          </div>
        </Transition>

        <button
          type="button"
          @click="toggleMenu"
          class="fab-button"
          :class="{ 'fab-button-active': showMenu }"
          :title="cornerFabTitle"
          :aria-label="cornerFabAriaLabel"
        >
          <Transition name="icon-rotate" mode="out-in">
            <svg
              v-if="!showMenu"
              key="menu"
              class="fab-button-icon text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <svg
              v-else
              key="close"
              class="fab-button-icon text-white"
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
import { ref, computed, watch, onBeforeUnmount, withDefaults } from 'vue'

const props = withDefaults(
  defineProps<{
    visible: boolean
    classroomId?: number | null
    /** floating：Teleport 到视口角落；embedded：由父级（如极简浮动导播台标题栏）布局 */
    layout?: 'floating' | 'embedded'
  }>(),
  { layout: 'floating' }
)

const showMenu = ref(false)

/** 嵌入导播台：悬停说明与人像/叉号图标对应关系 */
const embeddedFabTitle = computed(() =>
  showMenu.value
    ? '关闭教学助手菜单（当前图标为叉号）'
    : '教学助手（当前图标为人像剪影）：打开菜单，可使用点名考勤、课堂表现、纪律记录、值日管理等'
)
const embeddedFabAriaLabel = computed(() =>
  showMenu.value ? '关闭教学助手菜单' : '打开教学助手功能菜单'
)

/** 视口角落 FAB：同上，并说明为浮动按钮 */
const cornerFabTitle = computed(() =>
  showMenu.value
    ? '关闭教学助手菜单（当前图标为叉号）'
    : '教学助手（人像图标浮动按钮）：打开菜单，点名、课堂表现、纪律、值日等'
)
const cornerFabAriaLabel = computed(() =>
  showMenu.value ? '关闭教学助手菜单' : '打开教学助手功能菜单'
)

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

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

const emit = defineEmits<{
  'open-drawer': [type: 'attendance' | 'behavior' | 'discipline' | 'duty']
}>()

// 处理点名考勤
const handleAttendance = () => {
  if (!props.classroomId) {
    alert('请先进入授课并选择班级')
    return
  }
  emit('open-drawer', 'attendance')
  showMenu.value = false
}

// 处理课堂表现
const handlePositiveBehavior = () => {
  if (!props.classroomId) {
    alert('请先进入授课并选择班级')
    return
  }
  emit('open-drawer', 'behavior')
  showMenu.value = false
}

// 处理纪律记录
const handleDiscipline = () => {
  if (!props.classroomId) {
    alert('请先进入授课并选择班级')
    return
  }
  emit('open-drawer', 'discipline')
  showMenu.value = false
}

// 处理值日管理
const handleDuty = () => {
  if (!props.classroomId) {
    alert('请先进入授课并选择班级')
    return
  }
  emit('open-drawer', 'duty')
  showMenu.value = false
}

</script>

<style scoped>
.teaching-assistant-fab-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.teaching-assistant-fab-container:not(.teaching-assistant-fab-container--embedded) {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.teaching-assistant-fab-container--embedded {
  position: relative;
  z-index: 6;
  flex-shrink: 0;
  gap: 0;
  align-items: flex-end;
}

.teaching-assistant-fab-container--embedded .fab-menu--embedded {
  position: absolute;
  right: 0;
  bottom: calc(100% + 6px);
  min-width: 260px;
  max-width: min(320px, calc(100vw - 20px));
  max-height: min(72vh, 440px);
  z-index: 20;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.9) inset,
    0 14px 30px rgba(15, 23, 42, 0.12);
}

.teaching-assistant-fab-container--embedded .fab-menu-content {
  max-height: min(52vh, 360px);
  padding: 8px;
}

/* 与 TeacherControlPanel 浮动导播台「课堂详情 / 展开」图标按钮同一套工具按钮语言 */
.teaching-assistant-fab-container--embedded .fab-button--embedded {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: #fff;
  color: #475569;
  box-shadow: none;
  transform: none;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}

.teaching-assistant-fab-container--embedded .fab-button--embedded:hover {
  background: #f8fafc;
  border-color: rgba(15, 23, 42, 0.16);
  color: #0f172a;
  transform: none;
  box-shadow: none;
}

.teaching-assistant-fab-container--embedded .fab-button--embedded:active {
  transform: none;
}

.teaching-assistant-fab-container--embedded .fab-button--embedded.fab-button-active {
  background: rgba(79, 70, 229, 0.12);
  border-color: rgba(79, 70, 229, 0.35);
  color: #3730a3;
  box-shadow: none;
}

.teaching-assistant-fab-container--embedded .fab-menu-header {
  min-height: 44px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
}

.teaching-assistant-fab-container--embedded .fab-menu-title {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #0f172a;
}

.teaching-assistant-fab-container--embedded .fab-menu-close {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.1);
  background: #fff;
  color: #475569;
}

.teaching-assistant-fab-container--embedded .fab-menu-close:hover {
  background: #f8fafc;
  border-color: rgba(15, 23, 42, 0.16);
  color: #0f172a;
}

.teaching-assistant-fab-container--embedded .fab-menu-item {
  position: relative;
  border-radius: 10px;
  padding: 10px 12px;
  gap: 10px;
  margin-bottom: 2px;
  border: 1px solid transparent;
}

.teaching-assistant-fab-container--embedded .fab-menu-item:hover:not(:disabled) {
  background: rgba(79, 70, 229, 0.08);
  border-color: rgba(79, 70, 229, 0.16);
  transform: none;
}

.teaching-assistant-fab-container--embedded .fab-menu-item:hover:not(:disabled)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 2px;
  border-radius: 999px;
  background: #4f46e5;
}

.teaching-assistant-fab-container--embedded .fab-menu-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(79, 70, 229, 0.12) !important;
  color: #4f46e5;
  box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.14);
}

.teaching-assistant-fab-container--embedded .fab-menu-item-icon svg {
  color: #4f46e5 !important;
}

.teaching-assistant-fab-container--embedded .fab-menu-item-title {
  font-size: 13px;
  font-weight: 600;
  color: #0f172a;
}

.teaching-assistant-fab-container--embedded .fab-menu-item-desc {
  font-size: 12px;
  color: #64748b;
}

.teaching-assistant-fab-container--embedded .fab-menu-item > svg {
  color: #6366f1 !important;
}

.teaching-assistant-fab-container--embedded .fab-menu-tip {
  margin-bottom: 6px;
  border-radius: 10px;
  background: rgba(79, 70, 229, 0.08);
  border: 1px solid rgba(79, 70, 229, 0.22);
}

.teaching-assistant-fab-container--embedded .fab-menu-tip svg {
  color: #4f46e5 !important;
}

.teaching-assistant-fab-container--embedded .fab-menu-tip-text {
  color: #3730a3;
}

.fab-button-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.teaching-assistant-fab-container--embedded .fab-button--embedded .fab-button-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .teaching-assistant-fab-container:not(.teaching-assistant-fab-container--embedded) {
    right: auto;
    left: 12px;
    /* 避开底部导航条与极简翻页控件 */
    bottom: calc(env(safe-area-inset-bottom, 0px) + 92px);
    z-index: 960;
  }

  .teaching-assistant-fab-container:not(.teaching-assistant-fab-container--embedded) .fab-button {
    width: 52px;
    height: 52px;
  }

  .fab-menu:not(.fab-menu--embedded) {
    min-width: min(320px, calc(100vw - 24px));
    max-width: calc(100vw - 24px);
    max-height: 60vh;
  }

  .teaching-assistant-fab-container:not(.teaching-assistant-fab-container--embedded) .fab-menu-content {
    max-height: calc(60vh - 60px);
  }

  .teaching-assistant-fab-container--embedded .fab-button--embedded {
    width: 28px;
    height: 28px;
  }

  .teaching-assistant-fab-container--embedded .fab-button--embedded .fab-button-icon {
    width: 14px;
    height: 14px;
  }
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

