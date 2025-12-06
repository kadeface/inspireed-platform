<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="教师工作台"
      subtitle="管理您的教案和课程资源"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      @logout="handleLogout"
    />

    <!-- 主内容区 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="space-y-8">
        <!-- 问答统计卡片 -->
        <section>
          <div class="overview-grid">
            <!-- 问答总览卡片 -->
          <router-link
            to="/teacher/questions"
            class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
          >
            <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-cyan-500 to-blue-600"></span>
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-cyan-50/80 via-transparent to-transparent"></div>

            <div class="relative flex items-start justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-cyan-600">学生问答</p>
                <h3 class="mt-1 text-lg font-bold text-gray-900">互动反馈</h3>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-cyan-500 to-blue-600">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>

            <div v-if="questionStats" class="relative mt-4 flex items-baseline gap-2">
              <span class="text-3xl font-bold text-cyan-700">{{ questionStats.pending || 0 }}</span>
              <span class="text-sm text-gray-500">待回答</span>
            </div>
            <div v-else class="relative mt-4 text-sm text-gray-500">加载中...</div>

            <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
              {{ questionStats?.pending ? '有待处理互动，尽快回应学生的实时反馈。' : '课堂互动已及时闭环，随时查看评估总览。' }}
            </p>
            <p v-if="questionStats" class="relative mt-1 text-xs text-gray-500">
              总问题 {{ questionStats.total || 0 }} · 已解决 {{ questionStats.resolved || 0 }}
            </p>

            <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-cyan-600 hover:text-cyan-700 hover:bg-cyan-50 px-4 py-2 rounded-xl transition-all">
              查看总览
              <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </router-link>

          <!-- 学科教研组卡片 -->
          <router-link
            to="/teacher/subject-groups"
            class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
          >
            <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-emerald-50/80 via-transparent to-transparent"></div>

            <div class="relative flex items-start justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-emerald-600">学科教研组</p>
                <h3 class="mt-1 text-lg font-bold text-gray-900">协作共研</h3>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-emerald-500 to-teal-600">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>

            <div v-if="subjectGroupStats" class="relative mt-4 flex items-baseline gap-2">
              <span class="text-3xl font-bold text-emerald-700">{{ subjectGroupStats.my_groups || 0 }}</span>
              <span class="text-sm text-gray-500">我的教研组</span>
            </div>
            <div v-else class="relative mt-4 text-sm text-gray-500">加载中...</div>

            <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
              {{ subjectGroupStats?.my_groups ? '在教研组内沉淀成果，推动持续改进。' : '将优秀实践分享到教研组，形成共研。' }}
            </p>
            <p v-if="subjectGroupStats" class="relative mt-1 text-xs text-gray-500">
              全部 {{ subjectGroupStats.total_groups || 0 }} 个 · 共享教案 {{ subjectGroupStats.total_shared_lessons || 0 }} 篇
            </p>

            <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 px-4 py-2 rounded-xl transition-all">
              进入教研组
              <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </router-link>

          <!-- AI 教学助理卡片 -->
          <button
            type="button"
            @click="openAssistantModal"
            class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 text-left shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-violet-300"
          >
            <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-violet-500 to-purple-600"></span>
            <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-gradient-to-br from-violet-50/80 via-transparent to-transparent"></div>

            <div class="relative flex items-start justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-violet-600">AI 教学助理</p>
                <h3 class="mt-1 text-lg font-bold text-gray-900">智能建议</h3>
              </div>
              <div class="flex h-12 w-12 items-center justify-center rounded-xl shadow-lg bg-gradient-to-br from-violet-500 to-purple-600">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
            </div>

            <p class="relative mt-4 text-sm text-gray-600 leading-relaxed">
              基于课堂数据的智能建议，快速制定教学行动。
            </p>

            <ul class="relative mt-3 space-y-1.5">
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <span class="inline-flex h-1 w-1 rounded-full bg-violet-400"></span>
                <span>即时总结课堂表现</span>
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <span class="inline-flex h-1 w-1 rounded-full bg-violet-400"></span>
                <span>生成教学改进建议</span>
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <span class="inline-flex h-1 w-1 rounded-full bg-violet-400"></span>
                <span>一键草拟课堂答疑</span>
              </li>
            </ul>

            <div class="relative mt-4 inline-flex items-center gap-1 text-sm font-medium text-violet-600 hover:text-violet-700 hover:bg-violet-50 px-4 py-2 rounded-xl transition-all">
              使用助理
              <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>
          </div>
        </section>

      <!-- PDCA 教学质量管理循环 -->
      <section class="dashboard-section">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 class="text-2xl md:text-3xl font-bold text-gray-900 flex items-center gap-2">
              <span>🔄</span>
              <span>PDCA 教学质量管理循环</span>
            </h2>
            <p class="mt-2 text-sm text-gray-600">
              从教学设计到课堂实施、过程评估与循证改进，持续优化教学闭环。
            </p>
          </div>
          <div v-if="isPdcaLoading" class="flex items-center gap-2 text-sm text-emerald-600">
            <svg class="w-4 h-4 text-emerald-500 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            <span>数据刷新中...</span>
          </div>
        </div>

        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <div
            v-for="stage in pdcaStages"
            :key="stage.key"
            class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <span :class="['absolute inset-x-0 top-0 h-1.5', stage.accentBar]"></span>
            <div
              :class="['absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none', stage.hoverGradient]"
            ></div>

            <div class="relative flex items-start justify-between">
              <div>
                <p :class="['text-xs font-semibold uppercase tracking-wide', stage.labelClass]">
                  {{ stage.label }}
                </p>
                <h3 class="mt-1 text-lg font-bold text-gray-900">
                  {{ stage.title }}
                </h3>
              </div>
              <div :class="['flex h-12 w-12 items-center justify-center rounded-xl shadow-lg', stage.iconBg]">
                <span :class="['text-xl', stage.iconText]">{{ stage.icon }}</span>
              </div>
            </div>

            <div class="relative mt-4 flex items-baseline gap-2">
              <span :class="['text-3xl font-bold', stage.metricText]">
                {{ stage.value }}
              </span>
              <span class="text-sm text-gray-500">{{ stage.unit }}</span>
            </div>

            <p class="relative mt-3 text-sm text-gray-600 leading-relaxed">
              {{ stage.description }}
            </p>
            <p v-if="stage.secondary" class="relative mt-1 text-xs text-gray-500">
              {{ stage.secondary }}
            </p>

            <button
              v-if="stage.cta && stage.action"
              type="button"
              @click="stage.action()"
              :class="['relative mt-4 inline-flex items-center gap-1 text-sm font-medium px-4 py-2 rounded-xl transition-all', stage.buttonClass]"
            >
              {{ stage.cta }}
              <svg class="ml-1 h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </section>

        <!-- 页面标题、筛选与操作栏 -->
        <div class="mb-6">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div class="flex-1">
              <!-- 标签页切换 -->
              <div class="inline-flex rounded-xl shadow-sm bg-white/80 backdrop-blur-sm border border-gray-200 mb-4" role="tablist">
                <button
                  @click="lessonTab = 'my'"
                  :class="[
                    'px-5 py-2.5 text-sm font-medium transition-all rounded-l-xl',
                    lessonTab === 'my'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                      : 'bg-transparent text-gray-700 hover:bg-gray-50'
                  ]"
                  role="tab"
                  :aria-selected="lessonTab === 'my'"
                >
                  <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  我的教案
                </button>
                <button
                  @click="lessonTab = 'shared'"
                  :class="[
                    'px-5 py-2.5 text-sm font-medium transition-all rounded-r-xl',
                    lessonTab === 'shared'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                      : 'bg-transparent text-gray-700 hover:bg-gray-50'
                  ]"
                  role="tab"
                  :aria-selected="lessonTab === 'shared'"
                >
                  <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                  </svg>
                  共享教案
                </button>
              </div>
              
              <!-- 标题和统计 -->
              <div>
                <h2 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gray-900 via-emerald-700 to-teal-700 bg-clip-text text-transparent">
                  {{ lessonTab === 'my' ? '我的教案' : '共享教案' }}
                </h2>
                <p class="mt-2 text-sm text-gray-600">
                  <span v-if="lessonTab === 'my'">
                    共 {{ lessonStore.totalLessons }} 个教案
                  </span>
                  <span v-else>
                    共 {{ sharedLessonsTotal }} 个共享教案
                  </span>
                  <span v-if="selectedGrade" class="ml-2 text-emerald-600 font-medium">
                    - 已筛选: {{ selectedGradeName }}
                  </span>
                  <span v-if="selectedChapterId && selectedChapterName" class="ml-2 text-teal-600 font-medium">
                    - 章节: {{ selectedChapterName }}
                    <button 
                      @click="clearChapterFilter"
                      class="ml-1 text-xs hover:underline hover:text-teal-700 transition-colors"
                    >
                      ✕ 清除
                    </button>
                  </span>
                </p>
              </div>
            </div>
            <div class="flex flex-col sm:flex-row sm:items-center gap-3 w-full lg:w-auto">
              <CurriculumWithResources
                compact
                class="w-full sm:w-auto"
                @lesson-created="handleLessonCreated"
              />

              <div class="flex items-center gap-3">
              <!-- 视图切换按钮（仅在我的教案显示） -->
              <div v-if="lessonTab === 'my'" class="inline-flex rounded-xl shadow-sm bg-white/80 backdrop-blur-sm border border-gray-200" role="group">
                <button
                  @click="viewMode = 'list'"
                  :class="[
                    'px-4 py-2 text-sm font-medium transition-all',
                    'rounded-l-xl',
                    viewMode === 'list'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                      : 'bg-transparent text-gray-700 hover:bg-gray-50'
                  ]"
                  title="列表视图"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                  </svg>
                </button>
                <button
                  @click="viewMode = 'tree'"
                  :class="[
                    'px-4 py-2 text-sm font-medium transition-all',
                    'rounded-r-xl',
                    viewMode === 'tree'
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 z-10'
                      : 'bg-transparent text-gray-700 hover:bg-gray-50'
                  ]"
                  title="课程体系视图"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </button>
              </div>
 
              <!-- 创建教案按钮（仅在我的教案显示） -->
              <button
                v-if="lessonTab === 'my'"
                @click="showCreateModal = true"
                class="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm font-medium rounded-xl hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-all shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-105"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
                创建新教案
              </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 搜索和筛选栏（仅在列表视图显示） -->
        <div v-if="viewMode === 'list'" class="mb-6 flex flex-col sm:flex-row gap-4">
          <!-- 搜索框 -->
          <div class="flex-1">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索教案标题..."
                class="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl leading-5 bg-white/80 backdrop-blur-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition-all"
              />
            </div>
          </div>

          <!-- 状态筛选器 -->
          <div class="flex gap-2">
            <button
              v-for="filter in statusFilters"
              :key="filter.value || 'all'"
              @click="currentStatus = filter.value"
              :class="[
                'px-4 py-2.5 text-sm font-medium rounded-xl transition-all',
                currentStatus === filter.value
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                  : 'bg-white/80 backdrop-blur-sm text-gray-700 border border-gray-300 hover:bg-gray-50 hover:border-gray-400',
              ]"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- 章节筛选器 -->
          <div class="flex gap-2">
            <select
              v-model="selectedChapterId"
              @change="handleChapterSelected"
              class="px-3 py-2.5 text-sm border border-gray-300 rounded-xl bg-white/80 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all"
            >
              <option value="">所有章节</option>
              <option v-for="chapter in availableChapters" :key="chapter.id" :value="chapter.id">
                {{ chapter.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- 列表视图 -->
        <div v-if="viewMode === 'list'">
          <!-- 错误提示 -->
          <div
            v-if="lessonStore.error"
            class="mb-6 bg-red-50/80 backdrop-blur-sm border border-red-200 rounded-2xl p-4 shadow-lg"
          >
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ lessonStore.error }}</p>
              </div>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="(lessonTab === 'my' && lessonStore.isLoading) || (lessonTab === 'shared' && isLoadingSharedLessons)" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="i in 6"
            :key="i"
            class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg overflow-hidden animate-pulse"
          >
            <div class="h-40 bg-gradient-to-br from-gray-200 to-gray-300"></div>
            <div class="p-4">
              <div class="h-6 bg-gray-200 rounded-xl mb-2"></div>
              <div class="h-4 bg-gray-200 rounded-lg w-3/4 mb-4"></div>
              <div class="h-4 bg-gray-200 rounded-lg w-1/2"></div>
            </div>
            </div>
          </div>

          <!-- 空状态 -->
          <div
            v-else-if="!lessonStore.isLoading && lessonStore.lessons.length === 0"
            class="bg-white/80 backdrop-blur-sm rounded-2xl border border-gray-200 shadow-lg p-12 text-center"
          >
          <svg
            class="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 class="mt-2 text-sm font-medium text-gray-900">
            {{ lessonTab === 'my' ? '暂无教案' : '暂无共享教案' }}
          </h3>
          <p class="mt-1 text-sm text-gray-500">
            <span v-if="lessonTab === 'my'">
              {{ searchQuery || currentStatus ? '未找到符合条件的教案' : '开始创建您的第一个教案吧' }}
            </span>
            <span v-else>
              {{ searchQuery ? '未找到符合条件的共享教案' : '暂无教师共享的教案，快去分享您的优秀教案吧' }}
            </span>
          </p>
          <div class="mt-6">
            <button
              v-if="!searchQuery && !currentStatus"
              @click="showCreateModal = true"
              class="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-sm font-medium rounded-xl hover:from-emerald-600 hover:to-teal-600 shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-105 transition-all"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              创建新教案
              </button>
            </div>
          </div>

          <!-- 教案列表 -->
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            <!-- 我的教案列表 -->
            <template v-if="lessonTab === 'my'">
              <LessonCard
                v-for="lesson in lessonStore.lessons"
                :key="lesson.id"
                :lesson="lesson"
                @edit="handleEdit"
                @edit-published="handleEditPublished"
                @duplicate="handleDuplicate"
              @delete="handleDeleteClick"
              @publish="handlePublish"
              @unpublish="handleUnpublish"
              @view="handleView"
            />
            </template>
            
            <!-- 共享教案列表 -->
            <template v-else>
              <LessonCard
                v-for="lesson in sharedLessons"
                :key="lesson.id"
                :lesson="lesson"
                :readonly="true"
                @view="handleView"
                @duplicate="handleDuplicate"
              />
            </template>
          </div>

          <!-- 分页控件 -->
          <div
            v-if="(lessonTab === 'my' && !lessonStore.isLoading && lessonStore.lessons.length > 0 && lessonStore.totalLessons > lessonStore.pageSize) || (lessonTab === 'shared' && !isLoadingSharedLessons && sharedLessons.length > 0 && sharedLessonsTotal > lessonStore.pageSize)"
            class="mt-6 flex items-center justify-between border-t border-gray-200 bg-white/80 backdrop-blur-sm px-4 py-3 sm:px-6 rounded-2xl shadow-lg"
          >
          <div class="flex flex-1 justify-between sm:hidden">
            <button
              @click="handlePrevPage"
              :disabled="lessonStore.currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              上一页
            </button>
            <button
              @click="handleNextPage"
              :disabled="lessonStore.currentPage >= totalPages"
              class="relative ml-3 inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-300 rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              下一页
            </button>
          </div>
          <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第
                <span class="font-medium">{{ (lessonStore.currentPage - 1) * lessonStore.pageSize + 1 }}</span>
                到
                <span class="font-medium">{{ Math.min(lessonStore.currentPage * lessonStore.pageSize, lessonStore.totalLessons) }}</span>
                条，共
                <span class="font-medium">{{ lessonStore.totalLessons }}</span>
                条
              </p>
            </div>
            <div>
              <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  @click="handlePrevPage"
                  :disabled="lessonStore.currentPage === 1"
                  class="relative inline-flex items-center rounded-l-xl px-3 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <span class="sr-only">上一页</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z" clip-rule="evenodd" />
                  </svg>
                </button>
                <span class="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 bg-white/50">
                  {{ lessonStore.currentPage }} / {{ totalPages }}
                </span>
                <button
                  @click="handleNextPage"
                  :disabled="lessonStore.currentPage >= totalPages"
                  class="relative inline-flex items-center rounded-r-xl px-3 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <span class="sr-only">下一页</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
          </div>
        </div>

        <!-- 课程体系视图 -->
        <div v-else-if="viewMode === 'tree'">
          <CurriculumTreeView
            @create-lesson="handleCreateLessonFromChapter"
            @view-lessons="handleViewChapterLessons"
          />
        </div>
      </div>
    </main>

    <!-- 创建教案对话框 -->
    <CreateLessonModal
      v-model="showCreateModal"
      :initial-chapter-id="pendingChapterId"
      :initial-course-id="pendingCourseId"
      @create="handleCreate"
      @insert-material="handleInsertMaterial"
    />

    <ClassroomSelectorModal
      v-model="showPublishModal"
      :classrooms="availableClassrooms"
      :initial-selected-ids="selectedClassroomIds"
      :loading="isLoadingClassrooms"
      :error="publishModalError"
      @confirm="handlePublishConfirm"
      @cancel="handlePublishCancel"
    />

    <!-- 删除确认对话框 -->
    <ConfirmDialog
      v-model="showDeleteConfirm"
      title="确认删除"
      message="确定要删除这个教案吗？此操作无法撤销。"
      confirm-text="删除"
      cancel-text="取消"
      danger
      @confirm="handleDeleteConfirm"
    />

    <TeacherAiAssistantModal
      v-model="showAssistantModal"
      :lesson-summary="lessonStatusSummary"
      :question-stats="questionStats"
      :subject-group-stats="subjectGroupStats"
      :latest-lessons="lessonStore.lessons"
      :is-loading="isPdcaLoading || lessonStore.isLoading"
      @close="showAssistantModal = false"
    />

    <!-- Toast 提示 -->
    <Transition name="toast">
      <div
        v-if="toast.show"
        class="fixed bottom-4 right-4 z-50 max-w-sm"
      >
        <div
          :class="[
            'rounded-2xl shadow-xl p-4 backdrop-blur-sm',
            toast.type === 'success' ? 'bg-green-50/90 border border-green-200' : 'bg-red-50/90 border border-red-200',
          ]"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg
                v-if="toast.type === 'success'"
                class="h-5 w-5 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg
                v-else
                class="h-5 w-5 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <p
                :class="[
                  'text-sm font-medium',
                  toast.type === 'success' ? 'text-green-800' : 'text-red-800',
                ]"
              >
                {{ toast.message }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import { useUserStore } from '../../store/user'
import { useLessonStore } from '../../store/lesson'
import { LessonStatus } from '../../types/lesson'
import type { LessonCreate, LessonRelatedMaterial } from '../../types/lesson'
import LessonCard from '../../components/Lesson/LessonCard.vue'
import CreateLessonModal from '../../components/Lesson/CreateLessonModal.vue'
import ClassroomSelectorModal from '../../components/Lesson/ClassroomSelectorModal.vue'
import ConfirmDialog from '../../components/Common/ConfirmDialog.vue'
import CurriculumWithResources from '../../components/Curriculum/CurriculumWithResources.vue'
import CurriculumTreeView from '../../components/Curriculum/CurriculumTreeView.vue'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import TeacherAiAssistantModal from '@/components/Teacher/TeacherAiAssistantModal.vue'
import questionService from '@/services/question'
import { lessonService } from '@/services/lesson'
import curriculumService from '@/services/curriculum'
import { getSubjectGroupStatistics } from '@/services/subjectGroup'
import { authService } from '@/services/auth'
import type { QuestionStats } from '@/types/question'
import type { SubjectGroupStatistics } from '@/types/subjectGroup'

const router = useRouter()
const userStore = useUserStore()
const lessonStore = useLessonStore()

// 问答统计
const questionStats = ref<QuestionStats | null>(null)

// 学科教研组统计
const subjectGroupStats = ref<SubjectGroupStatistics | null>(null)

// 教案状态统计（用于 PDCA）
const lessonStatusSummary = ref({
  draft: 0,
  published: 0,
  archived: 0,
})

// PDCA 加载状态
const isPdcaLoading = ref(false)

// 用户名
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教师')
const regionName = computed(() => userStore.user?.region_name || '')
const schoolName = computed(() => userStore.user?.school_name || '')
const gradeName = computed(() => userStore.user?.grade_name || '')

// 本地状态
const showCreateModal = ref(false)
const showDeleteConfirm = ref(false)
const deleteTargetId = ref<number | null>(null)
const searchQuery = ref('')
const currentStatus = ref<LessonStatus | null>(null)
const selectedGrade = ref<number | null>(null)
const selectedGradeName = ref<string>('')
const selectedChapterId = ref<number | null>(null)
const selectedChapterName = ref<string>('')
const availableChapters = ref<any[]>([])
const viewMode = ref<'list' | 'tree'>('list') // 视图模式：列表视图或课程体系视图
const pendingChapterId = ref<number | null>(null) // 从课程体系视图创建教案时的章节ID
const pendingCourseId = ref<number | null>(null) // 从课程体系视图创建教案时的课程ID
const lessonTab = ref<'my' | 'shared'>('my') // 教案标签页：我的教案 / 共享教案
const sharedLessons = ref<any[]>([]) // 共享教案列表
const sharedLessonsTotal = ref(0) // 共享教案总数
const sharedLessonsPage = ref(1) // 共享教案当前页
const isLoadingSharedLessons = ref(false) // 加载共享教案状态
const showPublishModal = ref(false)
const publishError = ref<string | null>(null)
const publishTargetLessonId = ref<number | null>(null)
const selectedClassroomIds = ref<number[]>([])
const showAssistantModal = ref(false)

// Toast 提示
const toast = ref({
  show: false,
  type: 'success' as 'success' | 'error',
  message: '',
})

const availableClassrooms = computed(() => lessonStore.availableClassrooms)
const isLoadingClassrooms = computed(() => lessonStore.isLoadingClassrooms)
const classroomsError = computed(() => lessonStore.classroomsError)
const publishModalError = computed(
  () => publishError.value || classroomsError.value || null
)

// 状态筛选器
const statusFilters = [
  { label: '全部', value: null },
  { label: '草稿', value: LessonStatus.DRAFT },
  { label: '已发布', value: LessonStatus.PUBLISHED },
  { label: '已归档', value: LessonStatus.ARCHIVED },
]

function focusDraftLessons() {
  viewMode.value = 'list'
  if (currentStatus.value !== LessonStatus.DRAFT) {
    currentStatus.value = LessonStatus.DRAFT
  } else {
    loadLessons()
  }
}

function focusPublishedLessons() {
  viewMode.value = 'list'
  if (currentStatus.value !== LessonStatus.PUBLISHED) {
    currentStatus.value = LessonStatus.PUBLISHED
  } else {
    loadLessons()
  }
}

function openCreateLessonModal() {
  showCreateModal.value = true
}

function navigateToQuestions() {
  router.push('/teacher/questions')
}

function navigateToSubjectGroups() {
  router.push('/teacher/subject-groups')
}

function openAssistantModal() {
  showAssistantModal.value = true
}

const pdcaStages = computed(() => {
  const stageThemes: Record<
    string,
    {
      accentBar: string
      hoverGradient: string
      iconBg: string
      iconText: string
      metricText: string
      labelClass: string
      buttonClass: string
    }
  > = {
    plan: {
      accentBar: 'bg-gradient-to-r from-violet-500 to-purple-600',
      hoverGradient: 'bg-gradient-to-br from-violet-50/80 via-transparent to-transparent',
      iconBg: 'bg-gradient-to-br from-violet-500 to-purple-600',
      iconText: 'text-white',
      metricText: 'text-violet-700',
      labelClass: 'text-violet-600',
      buttonClass: 'text-violet-600 hover:text-violet-700 hover:bg-violet-50',
    },
    do: {
      accentBar: 'bg-gradient-to-r from-cyan-500 to-teal-600',
      hoverGradient: 'bg-gradient-to-br from-cyan-50/80 via-transparent to-transparent',
      iconBg: 'bg-gradient-to-br from-cyan-500 to-teal-600',
      iconText: 'text-white',
      metricText: 'text-cyan-700',
      labelClass: 'text-cyan-600',
      buttonClass: 'text-cyan-600 hover:text-cyan-700 hover:bg-cyan-50',
    },
    check: {
      accentBar: 'bg-gradient-to-r from-emerald-500 to-green-600',
      hoverGradient: 'bg-gradient-to-br from-emerald-50/80 via-transparent to-transparent',
      iconBg: 'bg-gradient-to-br from-emerald-500 to-green-600',
      iconText: 'text-white',
      metricText: 'text-emerald-700',
      labelClass: 'text-emerald-600',
      buttonClass: 'text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50',
    },
    act: {
      accentBar: 'bg-gradient-to-r from-amber-500 to-orange-600',
      hoverGradient: 'bg-gradient-to-br from-amber-50/80 via-transparent to-transparent',
      iconBg: 'bg-gradient-to-br from-amber-500 to-orange-600',
      iconText: 'text-white',
      metricText: 'text-amber-700',
      labelClass: 'text-amber-600',
      buttonClass: 'text-amber-600 hover:text-amber-700 hover:bg-amber-50',
    },
  }

  const draft = lessonStatusSummary.value.draft ?? 0
  const published = lessonStatusSummary.value.published ?? 0
  const archived = lessonStatusSummary.value.archived ?? 0
  const totalLessonsCount = draft + published + archived

  const totalQuestions = questionStats.value?.total ?? 0
  const resolvedQuestions = questionStats.value?.resolved ?? 0
  const pendingQuestions = questionStats.value?.pending ?? 0
  const resolutionRate =
    totalQuestions > 0 ? Math.round((resolvedQuestions / totalQuestions) * 100) : null

  const myGroups = subjectGroupStats.value?.my_groups ?? 0
  const mySharedLessons = subjectGroupStats.value?.my_shared_lessons ?? 0
  const platformSharedLessons = subjectGroupStats.value?.total_shared_lessons ?? 0

  return [
    {
      key: 'plan',
      label: 'Plan',
      title: '系统化设计',
      icon: '🧭',
      value: draft,
      unit: '草稿',
      description:
        draft > 0
          ? '完善教学目标、策略与活动链路。'
          : '创建新的教案，规划教学目标与策略。',
      secondary: archived ? `已归档 ${archived} 篇` : undefined,
      cta: draft > 0 ? '整理草稿' : '创建教案',
      action: draft > 0 ? focusDraftLessons : openCreateLessonModal,
      ...stageThemes.plan,
    },
    {
      key: 'do',
      label: 'Do',
      title: '结构化实施',
      icon: '🚀',
      value: published,
      unit: '发布',
      description:
        published > 0
          ? '已发布教案正在课堂落地实施。'
          : '发布教案，让教学设计进入课堂实践。',
      secondary: totalLessonsCount ? `累计教案 ${totalLessonsCount} 篇` : undefined,
      cta: published > 0 ? '查看已发布' : undefined,
      action: published > 0 ? focusPublishedLessons : undefined,
      ...stageThemes.do,
    },
    {
      key: 'check',
      label: 'Check',
      title: '过程性评估',
      icon: '✅',
      value: pendingQuestions,
      unit: '待答',
      description:
        pendingQuestions > 0
          ? '有待处理互动，尽快回应学生的实时反馈。'
          : '课堂互动已及时闭环，随时查看评估总览。',
      secondary:
        totalQuestions
          ? `已解决 ${resolvedQuestions} · 完成度 ${resolutionRate}%`
          : '等待课堂数据同步',
      cta: '查看总览',
      action: navigateToQuestions,
      ...stageThemes.check,
    },
    {
      key: 'act',
      label: 'Act',
      title: '循证改进',
      icon: '🔄',
      value: mySharedLessons,
      unit: '共享',
      description:
        mySharedLessons > 0
          ? '在教研组内沉淀成果，推动持续改进。'
          : '将优秀实践分享到教研组，形成共研。',
      secondary:
        myGroups > 0
          ? `所属教研组 ${myGroups} 个 · 平台共享 ${platformSharedLessons} 篇`
          : platformSharedLessons
          ? `平台累计共享 ${platformSharedLessons} 篇`
          : undefined,
      cta: '进入教研组',
      action: navigateToSubjectGroups,
      ...stageThemes.act,
    },
  ]
})

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(lessonStore.totalLessons / lessonStore.pageSize)
})

// 加载教案列表
async function loadLessons() {
  try {
    await lessonStore.loadLessons({
      page: lessonStore.currentPage,
      page_size: lessonStore.pageSize,
      status: currentStatus.value || undefined,
      search: searchQuery.value || undefined,
      grade_id: selectedGrade.value || undefined,
      chapter_id: selectedChapterId.value || undefined,
    })
  } catch (error: any) {
    showToast('error', error.message || '加载教案列表失败')
  }
}

// 加载共享教案列表
async function loadSharedLessons() {
  isLoadingSharedLessons.value = true
  try {
    // TODO: 调用实际的共享教案API
    // 这里先使用模拟数据，后续需要根据实际API调整
    const response = await lessonService.fetchLessons({
      page: sharedLessonsPage.value,
      page_size: lessonStore.pageSize,
      search: searchQuery.value || undefined,
      // 注意：LessonListParams 类型中暂不支持 shared 参数
      // 如需支持共享教案筛选，需要在 types/api.ts 中扩展 LessonListParams 接口
    })
    sharedLessons.value = response.items
    sharedLessonsTotal.value = response.total
  } catch (error: any) {
    showToast('error', error.message || '加载共享教案列表失败')
    sharedLessons.value = []
    sharedLessonsTotal.value = 0
  } finally {
    isLoadingSharedLessons.value = false
  }
}

// 监听标签页切换
watch(lessonTab, (newTab) => {
  if (newTab === 'my') {
    loadLessons()
  } else {
    loadSharedLessons()
  }
}, { immediate: false })

// 加载问答统计
async function loadQuestionStats() {
  try {
    questionStats.value = await questionService.getQuestionStats()
  } catch (error: any) {
    console.error('Failed to load question stats:', error)
    // 不显示错误，静默失败
  }
}

// 加载学科教研组统计
async function loadSubjectGroupStats() {
  try {
    subjectGroupStats.value = await getSubjectGroupStatistics()
  } catch (error: any) {
    console.error('Failed to load subject group stats:', error)
    // 不显示错误，静默失败
  }
}

// 加载教案状态统计
async function loadLessonStatusStats() {
  try {
    const [draftResponse, publishedResponse, archivedResponse] = await Promise.all([
      lessonService.fetchLessons({ status: LessonStatus.DRAFT, page_size: 1 }),
      lessonService.fetchLessons({ status: LessonStatus.PUBLISHED, page_size: 1 }),
      lessonService.fetchLessons({ status: LessonStatus.ARCHIVED, page_size: 1 }),
    ])

    lessonStatusSummary.value = {
      draft: draftResponse.total ?? 0,
      published: publishedResponse.total ?? 0,
      archived: archivedResponse.total ?? 0,
    }
  } catch (error: any) {
    console.error('Failed to load lesson status summary:', error)
  }
}

// 刷新 PDCA 相关数据
async function refreshPdcaOverview() {
  isPdcaLoading.value = true
  try {
    await Promise.all([loadLessonStatusStats(), loadQuestionStats(), loadSubjectGroupStats()])
  } finally {
    isPdcaLoading.value = false
  }
}

// 处理年级选择
function handleGradeSelected(gradeId: number | null) {
  selectedGrade.value = gradeId
  selectedGradeName.value = gradeId ? getGradeName(gradeId) : ''
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
}

// 处理章节选择
function handleChapterSelected() {
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
}

// MVP: 处理教案创建成功
function handleLessonCreated(lessonId: number) {
  console.log('Lesson created:', lessonId)
  // 刷新教案列表
  loadLessons()
  refreshPdcaOverview()
  showToast('success', '教案创建成功')
}

// 获取年级名称（这里需要根据实际数据结构调整）
function getGradeName(gradeId: number): string {
  // 这里应该根据实际的年级数据来获取名称
  // 暂时返回一个简单的映射
  const gradeNames: Record<number, string> = {
    1: '一年级', 2: '二年级', 3: '三年级', 4: '四年级', 5: '五年级', 6: '六年级',
    7: '七年级', 8: '八年级', 9: '九年级',
    10: '高一', 11: '高二', 12: '高三'
  }
  return gradeNames[gradeId] || `年级${gradeId}`
}

// 搜索防抖
const debouncedSearch = useDebounceFn(() => {
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
}, 300)

// 创建教案
async function handleCreate(lessonData: LessonCreate) {
  try {
    const newLesson = await lessonStore.createNewLesson(lessonData)
    showCreateModal.value = false
    // 清除pending状态
    pendingChapterId.value = null
    pendingCourseId.value = null
    showToast('success', '教案创建成功')
    refreshPdcaOverview()
    
    // 跳转到编辑页面
    router.push(`/teacher/lesson/${newLesson.id}`)
  } catch (error: any) {
    showToast('error', error.message || '创建教案失败')
  }
}

function handleInsertMaterial(material: LessonRelatedMaterial) {
  lessonStore.queueReferenceMaterial(material)
}

// 编辑教案
function handleEdit(lessonId: number) {
  router.push(`/teacher/lesson/${lessonId}`)
}

// 编辑已发布教案（先取消发布再跳转）
async function handleEditPublished(lessonId: number) {
  try {
    // 先取消发布
    await lessonStore.loadLesson(lessonId)
    const wasPublished = lessonStore.currentLesson?.status === 'published'
    await lessonStore.unpublishCurrentLesson()
    
    // 标记这个教案曾经是已发布的
    if (wasPublished) {
      sessionStorage.setItem(`lesson_${lessonId}_was_published`, 'true')
    }
    
    // 刷新列表
    loadLessons()
    refreshPdcaOverview()
    
    // 跳转到编辑页面
    router.push(`/teacher/lesson/${lessonId}`)
  } catch (error: any) {
    showToast('error', error.message || '取消发布失败')
  }
}

// 查看教案
function handleView(lessonId: number) {
  router.push(`/teacher/lesson/${lessonId}`)
}

// 复制教案
async function handleDuplicate(lessonId: number) {
  try {
    await lessonStore.duplicateLessonById(lessonId)
    showToast('success', '教案复制成功')
    loadLessons() // 刷新列表
    refreshPdcaOverview()
  } catch (error: any) {
    showToast('error', error.message || '复制教案失败')
  }
}

// 删除教案 - 显示确认对话框
function handleDeleteClick(lessonId: number) {
  deleteTargetId.value = lessonId
  showDeleteConfirm.value = true
}

// 确认删除
async function handleDeleteConfirm() {
  if (deleteTargetId.value === null) return
  
  try {
    await lessonStore.deleteLessonById(deleteTargetId.value)
    showToast('success', '教案删除成功')
    
    // 如果当前页没有数据了，回到上一页
    if (lessonStore.lessons.length === 0 && lessonStore.currentPage > 1) {
      lessonStore.currentPage -= 1
    }
    loadLessons()
    refreshPdcaOverview()
  } catch (error: any) {
    showToast('error', error.message || '删除教案失败')
  } finally {
    deleteTargetId.value = null
  }
}

// 取消发布教案（切换回草稿）
async function handleUnpublish(lessonId: number) {
  try {
    // 加载教案并取消发布
    await lessonStore.loadLesson(lessonId)
    const wasPublished = lessonStore.currentLesson?.status === 'published'
    await lessonStore.unpublishCurrentLesson()
    showToast('success', '教案已切换为草稿状态')
    
    // 标记这个教案曾经是已发布的
    if (wasPublished) {
      sessionStorage.setItem(`lesson_${lessonId}_was_published`, 'true')
    }
    
    loadLessons() // 刷新列表
    refreshPdcaOverview()
  } catch (error: any) {
    showToast('error', error.message || '取消发布失败')
  }
}

// 发布教案
async function handlePublish(lessonId: number) {
  publishError.value = null
  publishTargetLessonId.value = lessonId

  try {
    if (lessonStore.currentLesson?.id !== lessonId) {
      await lessonStore.loadLesson(lessonId)
    }

    await lessonStore.loadAvailableClassrooms()

    const existingIds = lessonStore.currentLesson?.classroom_ids ?? []
    selectedClassroomIds.value = [...existingIds]

    if (
      selectedClassroomIds.value.length === 0 &&
      availableClassrooms.value.length === 1
    ) {
      selectedClassroomIds.value = [availableClassrooms.value[0].id]
    }

    showPublishModal.value = true
  } catch (error: any) {
    publishTargetLessonId.value = null
    showToast('error', error.message || '加载班级信息失败')
  }
}

async function handlePublishConfirm(classroomIds: number[]) {
  if (classroomIds.length === 0) {
    publishError.value = '请选择至少一个班级'
    return
  }

  publishError.value = null

  try {
    if (publishTargetLessonId.value && lessonStore.currentLesson?.id !== publishTargetLessonId.value) {
      await lessonStore.loadLesson(publishTargetLessonId.value)
    }

    await lessonStore.publishCurrentLesson(classroomIds)
    selectedClassroomIds.value = [...classroomIds]
    showPublishModal.value = false
    publishTargetLessonId.value = null
    showToast('success', '教案发布成功')
    loadLessons()
    refreshPdcaOverview()
  } catch (error: any) {
    publishError.value = error.message || '发布教案失败'
  }
}

function handlePublishCancel() {
  publishError.value = null
  publishTargetLessonId.value = null
}

// 上一页
function handlePrevPage() {
  if (lessonStore.currentPage > 1) {
    lessonStore.currentPage -= 1
    loadLessons()
  }
}

// 下一页
function handleNextPage() {
  if (lessonStore.currentPage < totalPages.value) {
    lessonStore.currentPage += 1
    loadLessons()
  }
}

// 从课程体系视图创建教案
function handleCreateLessonFromChapter(chapterId: number, courseId: number) {
  pendingChapterId.value = chapterId
  pendingCourseId.value = courseId
  showCreateModal.value = true
}

// 查看章节的教案列表
async function handleViewChapterLessons(chapterId: number) {
  // 切换到列表视图并筛选指定章节的教案
  viewMode.value = 'list'
  selectedChapterId.value = chapterId
  
  // 获取章节名称用于显示
  try {
    const chapter = await curriculumService.getChapter(chapterId)
    selectedChapterName.value = chapter.name
  } catch (error) {
    console.error('Failed to load chapter name:', error)
    selectedChapterName.value = `章节 #${chapterId}`
  }
  
  loadLessons()
}

// 清除章节筛选
function clearChapterFilter() {
  selectedChapterId.value = null
  selectedChapterName.value = ''
  loadLessons()
}

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

// 显示 Toast
function showToast(type: 'success' | 'error', message: string) {
  toast.value = { show: true, type, message }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 监听搜索查询变化
watch(searchQuery, () => {
  debouncedSearch()
})

// 监听状态筛选变化
watch(currentStatus, () => {
  lessonStore.currentPage = 1 // 重置到第一页
  loadLessons()
})

// 加载可用章节列表
async function loadAvailableChapters() {
  try {
    // 这里应该从lessonStore中获取所有教案的章节信息
    // 或者调用专门的API获取章节列表
    // 暂时使用空数组，后续可以根据实际需求实现
    availableChapters.value = []
  } catch (error) {
    console.error('Failed to load chapters:', error)
    availableChapters.value = []
  }
}

// 页面加载时获取数据
onMounted(() => {
  const initialize = async () => {
    if (!userStore.user) {
      try {
        const currentUser = await authService.getCurrentUser()
        userStore.setUser(currentUser)
      } catch (error) {
        console.error('Failed to load current user info:', error)
      }
    }

    loadLessons()
    loadAvailableChapters()
    refreshPdcaOverview()
  }

  initialize()
})
</script>

<style scoped>
.dashboard-section {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 2rem;
}

.overview-grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(1rem);
}
</style>
