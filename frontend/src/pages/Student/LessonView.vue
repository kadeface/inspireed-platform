<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50 relative overflow-hidden">
    <!-- 装饰性背景元素 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-emerald-200/40 to-teal-200/40 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-cyan-200/40 to-blue-200/40 rounded-full blur-3xl"></div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center min-h-screen relative z-10">
      <div class="text-center bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/50">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
        <p class="mt-4 text-gray-700 font-medium">加载中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="flex items-center justify-center min-h-screen relative z-10">
      <div class="bg-red-50/80 backdrop-blur-sm border border-red-200 rounded-2xl p-6 max-w-md shadow-xl">
        <p class="text-red-600 mb-4 font-medium">{{ error }}</p>
        <button
          @click="router.back()"
          class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
        >
          返回
        </button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div v-else-if="lesson" class="flex h-screen relative">
      <!-- 左侧：课程内容 -->
      <div
        class="flex-1"
        :class="teachingImageFill ? 'flex flex-col overflow-hidden' : 'overflow-y-auto'"
      >
        <!-- 全屏提示弹窗 -->
        <Transition name="fade">
          <div
            v-if="showFullscreenPrompt"
            class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            @click.self="showFullscreenPrompt = false"
          >
            <div class="bg-white rounded-2xl shadow-xl p-6 max-w-md mx-4">
              <div class="flex items-center gap-4 mb-4">
                <div class="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900">进入全屏上课</h3>
                  <p class="text-sm text-gray-600">点击下方按钮进入全屏。浏览器需要你确认一次，之后也可以在顶栏退出。</p>
                </div>
              </div>
              <div class="flex gap-3">
                <button
                  @click="toggleFullscreen('fullscreen')"
                  class="inline-flex h-9 flex-1 items-center justify-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-4 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600"
                >
                  进入全屏
                </button>
                <button
                  @click="showFullscreenPrompt = false"
                  class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
                >
                  稍后
                </button>
              </div>
            </div>
          </div>
        </Transition>

        <div
          v-if="isTeachingSession && teachingHeaderOpen"
          class="fixed inset-y-0 left-0 z-30"
          :style="teachingHeaderInset"
          @click="teachingHeaderOpen = false"
        />

        <!-- 顶部导航栏。授课时收成顶栏抽屉，避免挡住学习内容 -->
        <header
          class="border-b border-slate-200 bg-white"
          :class="isTeachingSession ? ['teaching-top-drawer', { 'is-open': teachingHeaderOpen }] : 'sticky top-0 z-10'"
          :style="teachingHeaderInset"
        >
          <div class="px-4 md:px-6" :class="isInClassroomMode && classroomSession ? 'py-2.5' : 'py-3'">
            <div class="flex items-center justify-between gap-3">
              <!-- 左侧：返回按钮 + 课程信息 -->
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <button
                  @click="handleHeaderBack"
                  class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
                  :title="isInClassroomMode && classroomSession ? '退出上课' : '返回'"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                </button>
                <!-- 上课：一行课名。课程名和教师名在悬停提示里 -->
                <div v-if="isInClassroomMode && classroomSession" class="flex min-w-0 flex-1 items-center gap-2">
                  <span
                    class="h-2 w-2 shrink-0 rounded-full"
                    :class="isWebSocketConnected ? 'bg-emerald-500' : 'bg-amber-400'"
                    :title="isWebSocketConnected ? '已同步' : '重连中'"
                  ></span>
                  <span v-if="!isWebSocketConnected" class="shrink-0 text-xs font-medium text-amber-600">重连中</span>
                  <h1 class="min-w-0 truncate text-base font-semibold text-slate-900" :title="classroomHeaderTitle">
                    {{ lesson.title }}
                  </h1>
                </div>
                <div v-else class="min-w-0 flex-1">
                  <h1 class="text-lg md:text-xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent truncate">
                    {{ lesson.title }}
                  </h1>
                  <div class="flex items-center gap-2 mt-0.5 flex-wrap">
                    <span v-if="lesson.course" class="text-xs text-gray-500">{{ lesson.course.name }}</span>
                    <span v-if="lesson.course && lesson.chapter" class="text-xs text-gray-400">/</span>
                    <span v-if="lesson.chapter" class="text-xs text-gray-500">{{ lesson.chapter.name }}</span>
                  </div>
                </div>
              </div>

              <!-- 右侧：进度 + 学习空间 -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <span
                  v-if="isInClassroomMode && classroomSession"
                  class="text-sm font-medium tabular-nums text-emerald-600"
                  :title="`进度 ${progress}%`"
                >{{ progress }}%</span>
                <button
                  v-if="isTeachingSession"
                  type="button"
                  @click="isDocumentFullscreen ? toggleFullscreen('window') : toggleFullscreen('fullscreen')"
                  class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
                  :title="isDocumentFullscreen ? '退出全屏' : '全屏上课'"
                >
                  {{ isDocumentFullscreen ? '退出全屏' : '全屏' }}
                </button>
                <button
                  @click="toggleSidebar"
                  class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-white text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
                  :title="sidebarVisible ? '隐藏学习空间' : '显示学习空间'"
                >
                  <svg 
                    v-if="sidebarVisible" 
                    class="w-5 h-5" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  <svg 
                    v-else 
                    class="w-5 h-5" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          <div
            v-if="isInClassroomMode && classroomSession"
            class="h-0.5 bg-slate-100"
            role="progressbar"
            :aria-valuenow="progress"
            aria-valuemin="0"
            aria-valuemax="100"
            :aria-label="`进度 ${progress}%`"
          >
            <div class="h-full bg-emerald-500 transition-[width] duration-300" :style="{ width: `${progress}%` }"></div>
          </div>
          <button
            v-if="isTeachingSession"
            type="button"
            class="teaching-header-handle"
            :title="teachingHeaderOpen ? '收起顶栏' : '显示顶栏'"
            :aria-expanded="teachingHeaderOpen"
            @click.stop="teachingHeaderOpen = !teachingHeaderOpen"
          >
            <svg class="h-3.5 w-3.5 transition-transform" :class="teachingHeaderOpen ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
            <span
              v-if="!isWebSocketConnected"
              class="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-amber-400"
            />
          </button>
        </header>

        <!-- 课程描述 -->
        <div v-if="lesson.description && !isInClassroomMode" class="bg-gradient-to-r from-emerald-50 to-teal-50 border-l-4 border-emerald-500 px-6 py-4">
          <p class="text-gray-700 font-medium">{{ lesson.description }}</p>
        </div>

        <!-- 课堂模式提示 -->
        <StudentClassroomSync 
          v-if="classroomSession"
          :lesson-id="lessonId"
          :session="classroomSession"
          :on-leave-session="leaveSession"
        />

        <!-- 课堂模式：等待教师切换内容（全屏显示） -->
        <div 
          v-if="isInClassroomMode && !hasDisplayableContent && lessonContentCells.length > 0" 
          class="mx-6 my-8 text-center py-24 bg-gradient-to-br from-emerald-50/80 via-teal-50/80 to-cyan-50/80 rounded-2xl border-2 border-dashed border-emerald-300/50 backdrop-blur-sm shadow-lg"
        >
          <div class="max-w-md mx-auto">
            <div class="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/30">
              <svg class="h-10 w-10 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <!-- preparing 状态：等待教师开始上课 -->
            <template v-if="classroomSession?.status === 'preparing'">
              <h3 class="text-xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent mb-3">等待教师开始上课</h3>
              <p class="text-sm text-gray-700 font-medium mb-2">
                已成功加入课堂，请等待教师开始上课...
              </p>
              <p class="text-xs text-gray-600">
                教师开始上课后，这里将显示相应的学习内容
              </p>
            </template>
            <!-- ACTIVE 状态：等待教师切换内容 -->
            <template v-else>
              <h3 class="text-xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent mb-3">等待教师切换内容</h3>
              <p class="text-sm text-gray-700 font-medium mb-2">
                教师正在准备课程内容，请稍候...
              </p>
              <p class="text-xs text-gray-600">
                教师切换内容后，这里将显示相应的学习模块
              </p>
            </template>
          </div>
        </div>

        <!-- Cell 内容：key 随教师切换模块变化，确保收到 cell_changed 后界面立即刷新 -->
        <div
          v-if="filteredCells.length > 0"
          class="w-full"
          :class="teachingImageFill ? 'flex min-h-0 flex-1 flex-col' : ''"
          :key="classroomDisplayKey"
        >
          <!-- 正常内容显示 -->
          <div :class="teachingImageStage ? (teachingImageFill ? 'flex min-h-0 flex-1 flex-col' : 'space-y-0') : 'space-y-6 px-6'">
            <template v-for="(cell, index) in filteredCells" :key="cell.id">
              <div
                v-if="isTeachingSession && isPresentationImageCell(cell)"
                class="teaching-image-frame"
                :class="{ 'is-fill': teachingImageFill }"
              >
                <component
                  :is="getCellComponent(cell.type)"
                  v-bind="lessonViewCellBind(cell)"
                />
              </div>
              <CellWrapper
                v-else
                :cell="cell"
                :cellIndex="index"
                :allCells="lessonContentCells"
                :completedCellIds="completedCells"
                @complete="markCellAsCompleted"
              >
                <component
                  :is="getCellComponent(cell.type)"
                  v-bind="lessonViewCellBind(cell)"
                />
              </CellWrapper>
            </template>
          </div>

          <!-- 空状态 -->
          <div v-if="!isInClassroomMode || (isInClassroomMode && hasDisplayableContent && filteredCells.length === 0)" class="text-center py-12">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="mt-4 text-lg text-gray-600">该课程暂无内容</p>
          </div>

          <!-- 评分评论区域 -->
          <div v-if="!teachingImageStage" class="mt-12 mb-8">
            <ReviewSection :lesson-id="lessonId" @updated="handleReviewUpdated" />
          </div>

          <!-- 课程问答区域 -->
          <div v-if="!teachingImageStage" class="mt-8 mb-8 border-t border-gray-200 pt-8">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
                <svg class="w-6 h-6 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                课程问答
              </h2>
              <button
                @click="showQuestionForm = true"
                class="inline-flex h-9 items-center gap-1.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-3 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                我要提问
              </button>
            </div>

            <!-- 问题列表 -->
            <QuestionList
              :questions="questions"
              :loading="questionsLoading"
              :has-more="hasMoreQuestions"
              @question-click="handleQuestionClick"
              @load-more="loadMoreQuestions"
            />
          </div>
        </div>
      </div>

      <!-- 移动端遮罩层 -->
      <Transition name="fade">
        <div
          v-if="sidebarVisible && isMobile"
          @click="toggleSidebar"
          class="fixed inset-0 bg-black/50 z-30 md:hidden"
        ></div>
      </Transition>

      <!-- 右侧：学习空间 -->
      <Transition name="slide-sidebar">
        <div 
          v-if="sidebarVisible" 
          :class="[
            'bg-white/80 backdrop-blur-sm shadow-lg flex flex-col relative z-40',
            isMobile 
              ? 'fixed inset-y-0 right-0 w-full max-w-sm' 
              : 'w-96 border-l border-gray-200 flex-shrink-0'
          ]"
        >
        <div class="px-6 py-4 border-b border-gray-200 bg-white/80 backdrop-blur-sm">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              学习空间
            </h2>
            <div class="flex items-center gap-2">
              <span class="text-xs text-emerald-600 font-medium bg-emerald-50 px-2 py-1 rounded-full border border-emerald-100">当前进度 {{ progress }}%</span>
              <!-- 关闭按钮 -->
              <button
                @click="toggleSidebar"
                class="p-1.5 hover:bg-gray-200 rounded-lg transition-colors"
                title="隐藏学习空间"
              >
                <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="mt-3 flex gap-2">
            <button
              type="button"
              @click="activeSidebarTab = 'notes'"
              :class="[
                'inline-flex h-9 items-center rounded-xl px-3 text-sm font-medium transition-all',
                activeSidebarTab === 'notes'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                  : 'bg-white text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 hover:bg-slate-50 hover:ring-slate-300'
              ]"
            >
              学习笔记
            </button>
            <button
              type="button"
              @click="activeSidebarTab = 'assistant'"
              :class="[
                'inline-flex h-9 items-center gap-1.5 rounded-xl px-3 text-sm font-medium transition-all',
                activeSidebarTab === 'assistant'
                  ? 'bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-lg shadow-violet-500/30'
                  : 'bg-white text-violet-700 shadow-sm ring-1 ring-inset ring-violet-200 hover:bg-violet-50 hover:ring-violet-300'
              ]"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 2a6 6 0 00-6 6v1.586l-.707.707A1 1 0 004 12h1v1a4 4 0 004 4v1h2v-1a4 4 0 004-4v-1h1a1 1 0 00.707-1.707L16 9.586V8a6 6 0 00-6-6z" />
              </svg>
              AI 助手
            </button>
          </div>
        </div>

        <div class="flex-1 overflow-hidden">
          <div
            v-if="activeSidebarTab === 'notes'"
            class="flex h-full flex-col"
          >
            <div class="flex-1 overflow-hidden px-6 py-4">
              <MarkdownEditor
                v-model="notes"
                @update:modelValue="handleNotesUpdate"
                placeholder="支持 Markdown 格式，使用工具栏快速插入格式..."
              />
            </div>
            <div class="px-6 py-3 border-t border-gray-200 bg-white/80 backdrop-blur-sm">
              <div class="flex items-center justify-between text-xs text-gray-600">
                <span v-if="notesSaving" class="text-emerald-600">保存中...</span>
                <span v-else-if="notesSaved" class="text-emerald-600 font-medium">✓ 已保存</span>
                <span v-else class="text-gray-500">未保存</span>
                <span class="text-gray-500">{{ notes.length }} 字符</span>
              </div>
            </div>
          </div>
          <StudentAiAssistantPanel
            v-else
            :lesson-title="lesson?.title || ''"
            :lesson-outline="lessonOutline"
            :progress="progress"
            :lesson-id="lesson?.id"
            @append-note="appendNoteFromAssistant"
          />
        </div>
        </div>
      </Transition>
      
      <!-- 浮动按钮（侧边栏隐藏时显示） -->
      <Transition name="fade">
        <button
          v-if="!sidebarVisible"
          @click="toggleSidebar"
          :class="[
            'fixed z-30 p-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-full shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all hover:scale-110',
            isMobile 
              ? 'right-4 bottom-20' 
              : 'right-4 bottom-4'
          ]"
          title="显示学习空间"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </button>
      </Transition>
    </div>

    <!-- 提问表单弹窗 -->
    <QuestionForm
      :show="showQuestionForm"
      :lesson-id="lessonId"
      :cells="lessonContentCells"
      @close="showQuestionForm = false"
      @success="handleQuestionSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { lessonService } from '@/services/lesson'
import { api } from '@/services/api'
import type { Lesson } from '@/types/lesson'
import { CellType } from '@/types/cell'

// 导入所有 Cell 组件
import TextCell from '@/components/Cell/TextCell.vue'
import CodeCell from '@/components/Cell/CodeCell.vue'
import ParamCell from '@/components/Cell/ParamCell.vue'
import SimCell from '@/components/Cell/SimCell.vue'
import ChartCell from '@/components/Cell/ChartCell.vue'
import ContestCell from '@/components/Cell/ContestCell.vue'
import VideoCell from '@/components/Cell/VideoCell.vue'
import ImageCell from '@/components/Cell/ImageCell.vue'
import ActivityCell from '@/components/Cell/ActivityCell.vue'
import BrowserCell from '@/components/Cell/BrowserCell.vue'
import InteractiveCell from '@/components/Cell/InteractiveCell.vue'
import ReferenceMaterialCell from '@/components/Cell/ReferenceMaterialCell.vue'
import ReviewSection from '@/components/Resource/ReviewSection.vue'
import QuestionForm from '@/components/Question/QuestionForm.vue'
import QuestionList from '@/components/Question/QuestionList.vue'
import questionService from '@/services/question'
import type { QuestionListItem } from '@/types/question'
// 🎓 学习科学优化：导入认知脚手架组件
import CellWrapper from '@/components/Cell/CellWrapper.vue'
import FlowchartStudentCell from '@/components/Cell/FlowchartStudentCell.vue'
import StudentAiAssistantPanel from '@/components/Student/StudentAiAssistantPanel.vue'
import MarkdownEditor from '@/components/Editor/MarkdownEditor.vue'
import StudentClassroomSync from '@/components/Classroom/StudentClassroomSync.vue'
import { useClassroomSession } from '@/composables/useClassroomSession'
import { useLessonExternalReturn } from '@/composables/useLessonExternalReturn'
import classroomSessionService from '@/services/classroomSession'
import type { ClassSession } from '@/types/classroomSession'
import { isContentWithSections, normalizeContentToSections, sectionsToFlatCells } from '@/utils/lessonContent'
import { createLogger } from '@/utils/logger'
import { normalizeSessionStatus } from '@/utils/sessionStatus'
import { isPresentationImageCell } from '@/utils/presentationImage'
import { classroomDisplayProgress } from '@/utils/classroomProgress'

const log = createLogger('LessonView')
const route = useRoute()
const router = useRouter()

useLessonExternalReturn()

// 计算属性（需要在使用前定义）
const lessonId = computed(() => Number(route.params.id))

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const lesson = ref<Lesson | null>(null)
const completedCells = ref<Set<string>>(new Set())
const notes = ref('')
const notesSaving = ref(false)
const notesSaved = ref(false)
const activeSidebarTab = ref<'notes' | 'assistant'>('notes')

// 检测是否为移动设备
const isMobile = ref(false)
const checkMobile = () => {
  // 检测屏幕宽度和用户代理
  const screenWidth = window.innerWidth
  const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  const wasMobile = isMobile.value
  isMobile.value = screenWidth < 768 || isMobileDevice
  
  // 如果从桌面切换到移动端，或进入课堂模式，自动隐藏侧边栏
  if (isMobile.value && (!wasMobile || isInClassroomMode.value)) {
    sidebarVisible.value = false
  }
}

// 侧边栏显示状态：手机端默认隐藏，桌面端默认显示
const sidebarVisible = ref(false)

// 问答相关状态
const showQuestionForm = ref(false)
const questions = ref<QuestionListItem[]>([])
const questionsLoading = ref(false)
const hasMoreQuestions = ref(false)
const questionsPage = ref(1)

// 课堂会话相关状态
const dbCells = ref<Array<{ id: number; order: number; cell_type: string }>>([])  // 数据库中的 Cell 记录

// 全屏提示状态
const showFullscreenPrompt = ref(false)
const pendingFullscreenMode = ref<'fullscreen' | 'window' | null>(null)
const isDocumentFullscreen = ref(false)
const teachingFullscreenOffered = ref(false)

function isBrowserFullscreen() {
  return !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).mozFullScreenElement ||
    (document as any).msFullscreenElement
  )
}

// 全屏切换函数（用户交互触发）
async function toggleFullscreen(mode: 'fullscreen' | 'window') {
  try {
    if (mode === 'fullscreen') {
      // 进入全屏
      const element = document.documentElement
      if (element.requestFullscreen) {
        await element.requestFullscreen()
      } else if ((element as any).webkitRequestFullscreen) {
        await (element as any).webkitRequestFullscreen()
      } else if ((element as any).mozRequestFullScreen) {
        await (element as any).mozRequestFullScreen()
      } else if ((element as any).msRequestFullscreen) {
        await (element as any).msRequestFullscreen()
      }
      showFullscreenPrompt.value = false
      pendingFullscreenMode.value = null
    } else {
      // 退出全屏
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if ((document as any).webkitExitFullscreen) {
        await (document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        await (document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        await (document as any).msExitFullscreen()
      }
      showFullscreenPrompt.value = false
      pendingFullscreenMode.value = null
    }
  } catch (error: any) {
    console.error('❌ 全屏切换失败:', error)
    // 如果用户拒绝全屏请求，不显示错误提示（这是正常的浏览器行为）
    if (error.name !== 'NotAllowedError') {
      log.warn('全屏切换被拒绝或浏览器不支持')
    }
    showFullscreenPrompt.value = false
    pendingFullscreenMode.value = null
  }
}

// 处理展示模式变化。进入全屏必须由学生点击，浏览器不允许页面自己进入。
function handleFullscreenRequest(mode: 'fullscreen' | 'window') {
  if (mode === 'fullscreen') {
    if (isBrowserFullscreen()) {
      showFullscreenPrompt.value = false
      pendingFullscreenMode.value = null
      return
    }
    showFullscreenPrompt.value = true
    pendingFullscreenMode.value = 'fullscreen'
    return
  }
  // 切回窗口：只在已经全屏时退出，避免连接时的默认 window 关掉上课提示
  if (isBrowserFullscreen()) {
    toggleFullscreen('window')
  }
}

// 监听浏览器全屏状态变化（用户按Esc退出时）
function handleFullscreenChange() {
  isDocumentFullscreen.value = isBrowserFullscreen()
  log.debug('全屏状态', isDocumentFullscreen.value ? '全屏' : '窗口')
}

const {
  session: classroomSession,  // 直接使用 composable 返回的 session（会通过 WebSocket 实时更新）
  displayVersion,  // 每次 cell_changed/connected 递增，用于 :key 强制刷新内容区
  isInClassroomMode,
  isWebSocketConnected,  // WebSocket 连接状态
  displayCellId,
  shouldSyncDisplay,
  hasDisplayableContent,
  findAndJoinSession,
  leaveSession,
  updateProgress,  // 🆕 导入进度更新函数
} = useClassroomSession(lessonId.value, handleFullscreenRequest)

const isTeachingSession = computed(() => {
  const status = classroomSession.value?.status
  return !!status && normalizeSessionStatus(status) === 'teaching'
})

const teachingHeaderOpen = ref(false)

const teachingHeaderInset = computed(() => {
  if (!isTeachingSession.value) return undefined
  const sidebarTakesSpace = sidebarVisible.value && !isMobile.value
  return { right: sidebarTakesSpace ? '24rem' : '0px' }
})

// 进入授课后提示一次全屏。互动课不会自动改 display_mode，学生仍要点一次。
watch(isTeachingSession, (teaching) => {
  if (!teaching || teachingFullscreenOffered.value) return
  teachingFullscreenOffered.value = true
  if (!isBrowserFullscreen()) {
    handleFullscreenRequest('fullscreen')
  }
})

// 🆕 统一处理 lesson.content：支持 Cell[] 和 LessonContentWithSections 两种格式
const lessonContentCells = computed(() => {
  if (!lesson.value?.content) return []
  
  // 如果已经是数组格式（旧格式），直接返回
  if (Array.isArray(lesson.value.content)) {
    return lesson.value.content
  }
  
  // 如果是 sections 格式（新格式），转换为 flat cells
  if (isContentWithSections(lesson.value.content)) {
    const sections = normalizeContentToSections(lesson.value.content)
    return sectionsToFlatCells(sections)
  }
  
  return []
})

const classroomHeaderTitle = computed(() => {
  if (!lesson.value) return ''
  const meta: string[] = []
  if (lesson.value.course?.name) meta.push(lesson.value.course.name)
  if (classroomSession.value?.teacherName) {
    meta.push(`授课教师：${classroomSession.value.teacherName}`)
  }
  return meta.length ? `${lesson.value.title}\n${meta.join(' · ')}` : lesson.value.title
})

async function handleHeaderBack() {
  if (isInClassroomMode.value && classroomSession.value) {
    if (!confirm('确定要退出上课吗？退出后您将无法继续接收教师的实时同步内容。')) {
      return
    }
    try {
      await leaveSession()
    } catch (error: any) {
      console.error('退出上课失败:', error)
      alert('退出上课失败，请稍后重试')
      return
    }
  }
  router.push('/student')
}

// 自动保存定时器
let notesAutoSaveTimer: ReturnType<typeof setTimeout> | null = null
// Watch停止函数
let stopWatchDisplayCellIds: (() => void) | null = null
// 上次日志输出的时间戳（用于防抖）
let lastErrorLogTime = 0
const ERROR_LOG_DEBOUNCE = 5000 // 5秒内不重复输出相同错误

const progress = computed(() => {
  const cells = lessonContentCells.value
  if (!cells || cells.length === 0) {
    return 0
  }
  
  // 授课时一次只展示当前模块，进度按它在整课中的位置算
  if (isInClassroomMode.value && classroomSession.value?.settings) {
    const settings = classroomSession.value.settings as any
    const displayOrders = settings?.display_cell_orders

    if (displayOrders && Array.isArray(displayOrders)) {
      return classroomDisplayProgress(cells, displayOrders)
    }
  }
  
  // 非课堂模式：基于已完成的cell数
  const completed = completedCells.value.size
  const total = cells.length
  return Math.round((completed / total) * 100)
})

const lessonOutline = computed(() => {
  const cells = lessonContentCells.value
  if (!cells || cells.length === 0) return ''
  return cells
    .slice(0, 6)
    .map((cell, index) => summarizeCell(cell, index))
    .filter((item): item is string => Boolean(item))
    .join('\n')
})

// 上次过滤状态（用于检测变化）
let lastFilterState = ''

// 过滤Cells：在课堂模式下只显示教师指定的Cell
const filteredCells = computed(() => {
  const cells = lessonContentCells.value
  if (!cells || cells.length === 0) return []

  // 关键修复：在 preparing 状态下，学生不能看到任何内容（等待教师开始上课）
  if (isInClassroomMode.value && classroomSession.value?.status === 'preparing') {
    return []
  }

  // 只在状态变化时输出日志
  const currentState = JSON.stringify({
    isInClassroomMode: isInClassroomMode.value,
    displayCellId: displayCellId.value,
    displayCellOrders: classroomSession.value?.settings?.display_cell_orders,
    sessionStatus: classroomSession.value?.status,
  })

  if (currentState !== lastFilterState) {
    lastFilterState = currentState
  }

  // 如果不在课堂模式，显示所有Cell
  if (!isInClassroomMode.value) {
    return cells
  }

  // 课堂模式：严格同步，只显示教师指定的Cell
  if (shouldSyncDisplay.value) {
    const settings = classroomSession.value?.settings

    // 新方式：优先使用 display_cell_orders（推荐）
    const displayOrders = settings?.display_cell_orders
    if (displayOrders && Array.isArray(displayOrders)) {
      // 如果 displayOrders 是空数组，返回空数组（隐藏所有Cell）
      if (displayOrders.length === 0) {
        return []
      }

      // 直接根据 order 过滤，无需映射，无需 dbCells
      const filteredByOrders = cells.filter((cell, index) => {
        const cellOrder = cell.order !== undefined ? cell.order : index
        return displayOrders.includes(cellOrder)
      })

      return filteredByOrders
    }

    // 如果没有 display_cell_orders，返回空数组（隐藏所有Cell）
    return []
  }

  // 非严格同步模式，显示所有Cell
  return cells
})

// 课堂模式下内容区域的 key：displayVersion 在收到 cell_changed 时递增，确保界面自动刷新
const classroomDisplayKey = computed(() => {
  if (!isInClassroomMode.value) return 'default'
  const v = displayVersion.value
  const orders = classroomSession.value?.settings?.display_cell_orders
  const id = displayCellId.value ?? (classroomSession.value as any)?.current_cell_id ?? ''
  if (!orders || !Array.isArray(orders)) return `v${v}-empty-${id}`
  return `v${v}-${orders.join(',')}-${id}`
})

const teachingImageStage = computed(() =>
  isTeachingSession.value &&
  filteredCells.value.length > 0 &&
  filteredCells.value.every((cell) => isPresentationImageCell(cell)),
)

const teachingImageFill = computed(() =>
  teachingImageStage.value && filteredCells.value.length === 1,
)

// ========== 旧代码（已废弃）==========
// 以下代码用于兼容旧的 display_cell_ids 方式，已废弃
/*
      const idToIndexMap = new Map<number, number>()
      dbCells.value.forEach((dbCell: any) => {
        if (dbCell.id && dbCell.order !== undefined) {
          // 通过 order 在 lesson.content 中查找对应的索引
          const index = lesson.value.content.findIndex((cell: any, idx: number) => {
            const cellOrder = cell.order !== undefined ? cell.order : idx
            return cellOrder === dbCell.order
          })
          if (index !== -1) {
            idToIndexMap.set(dbCell.id, index)
          }
        }
      })
      
      // 如果 dbCells 为空，发出详细警告
      if (dbCells.value.length === 0) {
        log.warn('dbCells 为空，无法映射')
        log.warn('当前状态', {
          lessonId: lessonId.value,
          lessonContentCount: lesson.value.content.length,
          multiSelectIds: multiSelectIds,
          sessionId: classroomSession.value?.id,
        })
        log.warn('建议刷新或检查 /cells/lesson/' + lessonId.value)
      }
      
      // 获取所有对应的索引列表
      const targetIndices = new Set<number>()
      multiSelectIds.forEach((id: number) => {
        const index = idToIndexMap.get(id)
        if (index !== undefined && index >= 0) {
          targetIndices.add(index)
        } else {
          // 如果 dbCells 为空，尝试通过 cell.order 直接匹配
          // 假设 lesson.content 中的 order 值与数据库中的 order 值一致
          if (dbCells.value.length === 0) {
              // 遍历 lesson.content，查找 order 值对应的索引
              lesson.value.content.forEach((cell: any, idx: number) => {
                const cellOrder = cell.order !== undefined ? cell.order : idx
                // 如果这个 cell 的 order 值在某个范围内，尝试匹配
                // 注意：这个 fallback 假设 order 值与索引一致，可能不准确
              })
            }
          }
        })
      
      const matchedCells = lesson.value.content.filter((cell, index) => {
        // 优先使用索引匹配（最可靠，与导播台一致）
        if (targetIndices.has(index)) {
          return true
        }
        
        // Fallback 2: 通过数据库 ID 匹配（如果 cell.id 是数字）
        const cellId = cell.id
        const numericId = typeof cellId === 'number' ? cellId : 
                         typeof cellId === 'string' ? parseInt(cellId, 10) : null
        
        if (numericId && !isNaN(numericId) && multiSelectIds.includes(numericId)) {
          return true
        }
        
        // Fallback 3: 通过 order 匹配（如果 dbCells 可用）
        if (dbCells.value.length > 0) {
          const cellOrder = cell.order !== undefined ? cell.order : index
          const dbCell = dbCells.value.find((c: any) => c.order === cellOrder)
          if (dbCell && dbCell.id && multiSelectIds.includes(dbCell.id)) {
            return true
          }
        }
        
        return false
      })
      
      // 确保按 lesson.content 的索引顺序排序（与导播台一致）
      const sortedCells = matchedCells.sort((a, b) => {
        const indexA = lesson.value.content.indexOf(a)
        const indexB = lesson.value.content.indexOf(b)
        return indexA - indexB
      })
      
      // 如果匹配结果少于目标数量，记录警告（使用防抖）
      if (sortedCells.length < multiSelectIds.length) {
        const now = Date.now()
        if (now - lastErrorLogTime > ERROR_LOG_DEBOUNCE) {
          lastErrorLogTime = now
          log.warn(`匹配不完整 ${sortedCells.length}/${multiSelectIds.length}`)
          log.warn('匹配信息', {
            targetIds: multiSelectIds,
            matchedCount: sortedCells.length,
            dbCellsCount: dbCells.value.length,
          })
        }
      }
      
      // 重要：返回所有匹配的 Cell，确保多个单元都能显示
      if (sortedCells.length === 0 && multiSelectIds.length > 0) {
        // 使用防抖机制避免频繁输出相同错误
        const now = Date.now()
        if (now - lastErrorLogTime > ERROR_LOG_DEBOUNCE) {
          lastErrorLogTime = now
          console.error('❌ 严重错误：多选模式有选中模块，但没有匹配到任何 Cell！')
          console.error('这可能是因为：')
          console.error('1. dbCells 未正确加载 (当前数量:', dbCells.value.length, ')')
          console.error('2. ID 到 order 的映射失败')
          console.error('3. lesson.content 中的 order 与数据库不一致')
          console.error('调试信息:', {
            multiSelectIds,
            dbCellsCount: dbCells.value.length,
            lessonContentCount: lesson.value?.content?.length || 0,
            idToIndexMap: Object.fromEntries(idToIndexMap),
          })
        }
      }
      
      return sortedCells
*/
// ========== 旧代码结束 ==========

/*
    // 单选模式：如果教师还未切换到任何Cell，不显示任何内容
    // 注意：只有在 display_cell_ids 为空或不存在时，才使用单选模式
    if (!displayCellId.value) {
      return []
    }
    
    // 查找匹配的Cell
    const currentId = displayCellId.value
    
    // 先尝试通过数字 ID 查找匹配的 Cell（后端返回的是数据库 ID）
    // 然后通过 order 或索引匹配（当 ID 不匹配时使用）
    const matchedCells = lesson.value.content.filter((cell, index) => {
      // 1. 直接匹配 cell.id（数字或字符串）
      if (cell.id === currentId) return true
      
      // 2. 如果 cell.id 是字符串（UUID），尝试转换为数字后匹配
      if (typeof cell.id === 'string') {
        const numId = parseInt(cell.id, 10)
        if (!isNaN(numId) && numId === currentId) return true
      }
      
      // 3. 如果 currentId 是字符串，尝试与 cell.id 字符串匹配
      if (typeof currentId === 'string' && String(cell.id) === currentId) return true
      
      // 4. 通过 order 匹配（最可靠的方式，因为后端通过 cellOrder 创建/查找 Cell）
      // 如果后端返回的 current_cell_id 是通过 cellOrder 创建的，那么该 Cell 的 order 应该匹配
      if (cell.order !== undefined && typeof currentId === 'number') {
        // 需要从后端获取当前 Cell 的 order 来匹配
        // 但我们可以通过数据库 ID 反向查找：如果后端返回了数据库 ID，
        // 说明该 Cell 已经存在于数据库中，可能通过 order 创建
        // 暂时跳过，因为我们没有直接的 order 信息
      }
      
      // 5. 通过索引匹配（如果 currentId 是顺序索引）
      // 注意：如果后端返回的是数据库 ID（不是索引），这个匹配可能会失败
      if (typeof currentId === 'number') {
        // 如果 currentId 小于 lesson.content.length，可能是索引
        if (index === currentId && currentId < lesson.value.content.length) {
          // 但需要确认这不是数据库 ID
          // 如果 currentId 很大（大于内容数量），应该是数据库 ID，不是索引
          return true
        }
      }
      
      return false
    })
    
    // 如果通过 ID 没有匹配到，尝试使用索引作为 fallback
    if (matchedCells.length === 0 && typeof currentId === 'number') {
      if (currentId >= 0 && currentId < lesson.value.content.length) {
        const cellByIndex = lesson.value.content[currentId]
        if (cellByIndex) {
          return [cellByIndex]
        }
      }
    }
    
    return matchedCells
  }
  
  // 如果sync_mode不是strict，显示所有Cell（允许学生自由浏览）
  return lesson.value.content
*/
// ========== 旧代码全部结束 ==========

function lessonViewCellBind(cell: { type: string; id?: string | number }) {
  const base: Record<string, unknown> = {
    cell,
    editable: false,
    sessionId: classroomSession.value?.id,
    lessonId: lessonId.value,
  }
  const t = cell.type
  if (t === CellType.INTERACTIVE || t === 'interactive' || t === 'INTERACTIVE') {
    base.interactiveViewerMode = 'student'
  }
  if (isTeachingSession.value && isPresentationImageCell(cell)) {
    base.presentation = true
  }
  return base
}

const getCellComponent = (type: CellType | string): Component => {
  // 与 CellContainer / 后端 CellType 一致（大写）；保留小写键以兼容旧数据
  const components: Record<string, Component> = {
    [CellType.TEXT]: TextCell,
    [CellType.CODE]: CodeCell,
    [CellType.SIM]: SimCell,
    [CellType.CHART]: ChartCell,
    [CellType.CONTEST]: ContestCell,
    [CellType.VIDEO]: VideoCell,
    [CellType.IMAGE]: ImageCell,
    [CellType.ACTIVITY]: ActivityCell,
    [CellType.FLOWCHART]: FlowchartStudentCell,
    [CellType.BROWSER]: BrowserCell,
    [CellType.INTERACTIVE]: InteractiveCell,
    [CellType.REFERENCE_MATERIAL]: ReferenceMaterialCell,
    PARAM: ParamCell,
    text: TextCell,
    code: CodeCell,
    param: ParamCell,
    sim: SimCell,
    chart: ChartCell,
    contest: ContestCell,
    video: VideoCell,
    image: ImageCell,
    activity: ActivityCell,
    flowchart: FlowchartStudentCell,
    browser: BrowserCell,
    interactive: InteractiveCell,
    reference_material: ReferenceMaterialCell,
  }
  return components[type as string] ?? TextCell
}

const loadLesson = async () => {
  loading.value = true
  error.value = null

  try {
    // 从服务器获取最新教案数据（不使用缓存）
    lesson.value = await lessonService.fetchLessonById(lessonId.value)
    
    // 检查教案版本是否更新
    checkLessonVersionUpdate()
    
    // 加载该课程的完成状态（这些是本地操作，不阻塞）
    loadCompletedCells()
    loadNotes()
    
    // 先显示页面内容，再异步加载其他数据
    loading.value = false
    
    // 异步加载数据库中的 Cell 记录（用于 ID 匹配）
    loadDbCells().catch(err => {
      log.warn('加载 Cell 记录失败', err)
    })
    
    // 异步查找并加入课堂会话（不阻塞页面显示）
    findAndJoinSession().then(session => {
      if (!session) {
        log.debug('无课堂会话，学生可自主学习')
      }
    }).catch(err => {
      log.warn('加入会话失败', err)
      // 不显示错误提示，因为可能是正常的（没有正在进行的会话）
    })
  } catch (e: any) {
    error.value = e.message || '加载课程失败'
    console.error('Failed to load lesson:', e)
    loading.value = false
  }
}

// 初始化 display_cell_ids 监听器（只创建一次）
const initDisplayCellIdsWatcher = () => {
  // 清理旧的监听器（如果存在）
  if (stopWatchDisplayCellIds) {
    stopWatchDisplayCellIds()
    stopWatchDisplayCellIds = null
  }
  
  // 创建新的监听器
  stopWatchDisplayCellIds = watch(
    () => classroomSession.value?.settings?.display_cell_ids, 
    async (newIds, oldIds) => {
      if (newIds && newIds.length > 0 && JSON.stringify(newIds) !== JSON.stringify(oldIds)) {
        await loadDbCells()
      }
    }, 
    { deep: true, immediate: false }
  )
}

// 加载数据库中的 Cell 记录
const loadDbCells = async () => {
  try {
    const response = await api.get(`/cells/lesson/${lessonId.value}`)
    dbCells.value = Array.isArray(response) ? response : ((response as any)?.data || [])
  } catch (error: any) {
    console.error('Failed to load cell records:', error)
    dbCells.value = []
  }
}

// 检查教案版本是否更新
const checkLessonVersionUpdate = () => {
  if (!lesson.value) return
  
  const versionKey = `lesson_${lessonId.value}_version`
  const lastKnownVersion = localStorage.getItem(versionKey)
  
  if (lastKnownVersion) {
    const lastVersion = parseInt(lastKnownVersion, 10)
    if (lesson.value.version > lastVersion) {
      // 教案已更新，清除旧的完成状态，让学生重新学习新内容
      const completedCellsKey = `lesson_${lessonId.value}_completed_cells`
      localStorage.removeItem(completedCellsKey)
      completedCells.value = new Set()
      
      // 教案已更新，清除旧的完成状态
    }
  }
  
  // 保存当前版本号
  localStorage.setItem(versionKey, String(lesson.value.version))
}

const loadCompletedCells = () => {
  const key = `lesson_${lessonId.value}_completed_cells`
  const saved = localStorage.getItem(key)
  if (saved) {
    try {
      const cellIds = JSON.parse(saved)
      completedCells.value = new Set(cellIds)
    } catch (e) {
      console.error('Failed to load completed cells:', e)
    }
  }
}

const saveCompletedCells = () => {
  const key = `lesson_${lessonId.value}_completed_cells`
  const cellIds = Array.from(completedCells.value)
  localStorage.setItem(key, JSON.stringify(cellIds))
  
  // 更新总体学习进度
  updateLessonProgress()
}

const markCellAsCompleted = (cellId: string) => {
  completedCells.value.add(cellId)
  saveCompletedCells()
}

const markAsCompleted = () => {
  const cells = lessonContentCells.value
  if (!cells || cells.length === 0) return
  
  // 标记所有 Cell 为完成
  cells.forEach(cell => {
    completedCells.value.add(String(cell.id))
  })
  
  saveCompletedCells()
}

// 切换侧边栏显示/隐藏
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
  // 只在桌面端保存状态到 localStorage（手机端总是默认隐藏）
  if (!isMobile.value) {
    localStorage.setItem('student_sidebar_visible', String(sidebarVisible.value))
  }
}

// 监听课堂模式和移动设备状态变化，在手机端自动隐藏侧边栏
watch(
  () => [isInClassroomMode.value, isMobile.value],
  ([isInClassroom, mobile]) => {
    if (isInClassroom && mobile) {
      // 进入课堂模式时，手机端自动隐藏学习空间，优先显示授课内容
      sidebarVisible.value = false
    }
  },
  { immediate: true }
)

// 🆕 监听 display_cell_orders 变化，自动更新学生进度
watch(
  () => {
    const settings = classroomSession.value?.settings as any
    return settings?.display_cell_orders
  },
  async (newOrders, oldOrders) => {
    // 只在课堂模式下且 display_cell_orders 发生变化时更新
    if (!isInClassroomMode.value || !classroomSession.value) return
    
    const newOrdersStr = JSON.stringify(newOrders || [])
    const oldOrdersStr = JSON.stringify(oldOrders || [])
    
    if (newOrdersStr !== oldOrdersStr && Array.isArray(newOrders)) {
      const progressPercentage = classroomDisplayProgress(
        lessonContentCells.value || [],
        newOrders,
      )
      
      // 将 orders 转换为 cellIds（用于 updateProgress）
      const completedCellIds: number[] = []
      const cells = lessonContentCells.value
      if (cells && cells.length > 0) {
        newOrders.forEach((order: number) => {
          const cell = cells.find(
            (c, idx) => (c.order !== undefined ? c.order : idx) === order
          )
          if (cell) {
            const cellId = typeof cell.id === 'number' ? cell.id : parseInt(String(cell.id))
            if (!isNaN(cellId)) {
              completedCellIds.push(cellId)
            }
          }
        })
      }
      
      // 更新进度（通过 WebSocket 发送到后端）
      if (updateProgress) {
        await updateProgress(completedCellIds, undefined, progressPercentage)
      }
    }
  },
  { deep: true, immediate: false }
)

const updateLessonProgress = () => {
  const key = 'student_lesson_progress'
  const saved = localStorage.getItem(key)
  let progressData: Record<number, number> = {}
  
  if (saved) {
    try {
      progressData = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load progress data:', e)
    }
  }
  
  progressData[lessonId.value] = progress.value
  localStorage.setItem(key, JSON.stringify(progressData))
}

const stripHtmlTags = (html: string) =>
  html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()

const summarizeCell = (cell: any, index: number): string | null => {
  const orderLabel = `第${index + 1}单元`
  // 与后端 CellType 枚举一致：API 多为大写（如 BROWSER），统一成小写再查表
  const typeNorm = String(cell?.type ?? '').toLowerCase()
  const typeMap: Record<string, string> = {
    text: '文本',
    code: '代码',
    param: '参数',
    sim: '仿真',
    chart: '图表',
    contest: '竞赛',
    video: '视频',
    activity: '活动',
    flowchart: '流程图',
    browser: '浏览器',
    interactive: '交互式课件',
    reference_material: '参考素材',
  }
  const typeLabel = typeMap[typeNorm] || '单元'
  let detail = ''

  if (typeNorm === 'text' && cell.content?.html) {
    const plain = stripHtmlTags(cell.content.html)
    if (plain) {
      detail = plain.slice(0, 28)
      if (plain.length > 28) detail += '…'
    }
  } else if (typeNorm === 'activity' && cell.content?.title) {
    detail = cell.content.title
  } else if (typeNorm === 'video' && cell.content?.title) {
    detail = cell.content.title
  }

  const parts = [orderLabel, typeLabel]
  if (detail) {
    parts.push(`：${detail}`)
  }
  return parts.join('')
}

const handleNotesUpdate = (value: string) => {
  notes.value = value
  autoSaveNotes()
}

const appendNoteFromAssistant = (content: string) => {
  const cleaned = content.trim()
  if (!cleaned) return
  notes.value = notes.value ? `${notes.value.trim()}\n\n${cleaned}` : cleaned
  autoSaveNotes()
}

const loadNotes = () => {
  const key = `lesson_${lessonId.value}_notes`
  const saved = localStorage.getItem(key)
  if (saved) {
    notes.value = saved
  }
}

const saveNotes = () => {
  const key = `lesson_${lessonId.value}_notes`
  localStorage.setItem(key, notes.value)
  notesSaved.value = true
  notesSaving.value = false
  
  // 3秒后隐藏"已保存"提示
  setTimeout(() => {
    notesSaved.value = false
  }, 3000)
}

const autoSaveNotes = () => {
  notesSaved.value = false
  notesSaving.value = true
  
  // 清除之前的定时器
  if (notesAutoSaveTimer) {
    clearTimeout(notesAutoSaveTimer)
  }
  
  // 1秒后自动保存
  notesAutoSaveTimer = setTimeout(() => {
    saveNotes()
  }, 1000)
}

const handleReviewUpdated = () => {
  // 评论更新后，可以选择刷新课程数据以更新评分
  // 目前不需要特别处理，因为评分组件自己管理状态
  log.debug('Review updated')
}

// 问答相关方法
const loadQuestions = async () => {
  if (questionsLoading.value) return
  
  try {
    questionsLoading.value = true
    const response = await questionService.getLessonQuestions(lessonId.value, {
      sort: 'recent',
      page: questionsPage.value,
      page_size: 10
    })
    
    questions.value = response.items
    hasMoreQuestions.value = response.has_more
  } catch (err: any) {
    console.error('Failed to load questions:', err)
  } finally {
    questionsLoading.value = false
  }
}

const loadMoreQuestions = async () => {
  if (!hasMoreQuestions.value || questionsLoading.value) return
  
  questionsPage.value++
  try {
    questionsLoading.value = true
    const response = await questionService.getLessonQuestions(lessonId.value, {
      sort: 'recent',
      page: questionsPage.value,
      page_size: 10
    })
    
    questions.value = [...questions.value, ...response.items]
    hasMoreQuestions.value = response.has_more
  } catch (err: any) {
    console.error('Failed to load more questions:', err)
  } finally {
    questionsLoading.value = false
  }
}

const handleQuestionClick = (questionId: number) => {
  router.push(`/student/question/${questionId}`)
}

const handleQuestionSuccess = (_questionId: number) => {
  // 提问成功后重新加载问题列表
  questionsPage.value = 1
  loadQuestions()
  // 可选：跳转到问题详情页
  // router.push(`/student/question/${_questionId}`)
}

// 生命周期
onMounted(async () => {
  // 检测移动设备
  checkMobile()
  window.addEventListener('resize', checkMobile)
  
  // 恢复侧边栏显示状态（从localStorage，但手机端默认隐藏）
  const savedSidebarVisible = localStorage.getItem('student_sidebar_visible')
  if (isMobile.value) {
    // 手机端默认隐藏，优先显示主要授课内容
    sidebarVisible.value = false
  } else if (savedSidebarVisible !== null) {
    // 桌面端：恢复之前保存的状态
    sidebarVisible.value = savedSidebarVisible === 'true'
  } else {
    // 桌面端默认显示
    sidebarVisible.value = true
  }
  
  loadLesson()
  loadQuestions()
  // 初始化 display_cell_ids 监听器
  initDisplayCellIdsWatcher()
  
  // 监听浏览器全屏状态变化
  handleFullscreenChange()
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
})

onUnmounted(() => {
  // 组件卸载时保存笔记
  if (notes.value) {
    saveNotes()
  }
  
  // 清理定时器
  if (notesAutoSaveTimer) {
    clearTimeout(notesAutoSaveTimer)
  }
  
  // 清理 watch 监听器
  if (stopWatchDisplayCellIds) {
    stopWatchDisplayCellIds()
    stopWatchDisplayCellIds = null
  }
  
  // 移除窗口大小变化监听器
  window.removeEventListener('resize', checkMobile)
  
  // 移除全屏状态监听器
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
})
</script>

<style scoped>
/* 侧边栏滑动动画 */
.slide-sidebar-enter-active,
.slide-sidebar-leave-active {
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
}

.slide-sidebar-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-sidebar-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.slide-sidebar-enter-to,
.slide-sidebar-leave-from {
  transform: translateX(0);
  opacity: 1;
}

/* 移动端优化 */
@media (max-width: 768px) {
  /* 确保移动端侧边栏在最上层 */
  .slide-sidebar-enter-active,
  .slide-sidebar-leave-active {
    z-index: 40;
  }
}

/* 浮动按钮淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
}

.fade-enter-from {
  opacity: 0;
  transform: scale(0.8);
}

.fade-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
  transform: scale(1);
}

/* 🎓 学习科学优化：样式已移至 CellWrapper.vue 组件中 */

.teaching-image-frame {
  position: relative;
  height: calc(100dvh - 4.5rem);
  width: 100%;
  background: #000;
}

/* 单张图片铺满顶栏以下的区域，高度跟真实顶栏走，避免按视口估算后被 overflow 裁掉 */
.teaching-image-frame.is-fill {
  display: flex;
  flex: 1 1 0%;
  flex-direction: column;
  height: auto;
  min-height: 0;
}

.teaching-image-frame.is-fill :deep(.cell-container) {
  flex: 1 1 auto;
  min-height: 0;
  height: 100%;
}

.teaching-top-drawer {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 40;
  transform: translateY(-100%);
  transition: transform 0.2s ease;
}

.teaching-top-drawer.is-open {
  transform: translateY(0);
}

.teaching-top-drawer:not(.is-open) {
  pointer-events: none;
}

.teaching-header-handle {
  pointer-events: auto;
  position: absolute;
  left: 50%;
  top: 100%;
  z-index: 1;
  display: flex;
  height: 1.25rem;
  width: 3.5rem;
  transform: translateX(-50%);
  align-items: center;
  justify-content: center;
  border-radius: 0 0 0.5rem 0.5rem;
  background: rgba(255, 255, 255, 0.96);
  color: #64748b;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08), inset 0 0 0 1px #e2e8f0;
}

.teaching-header-handle:hover {
  color: #334155;
}
</style>
