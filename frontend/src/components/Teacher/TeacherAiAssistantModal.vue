<template>
  <Transition name="modal">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="handleClose"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-slate-900/60"></div>

        <div
          class="relative w-full max-w-5xl transform overflow-hidden rounded-2xl bg-white/95 backdrop-blur-sm shadow-2xl transition-all"
        >
          <!-- Header with Dashboard style -->
          <header class="relative overflow-hidden border-b border-gray-200 bg-white/80 backdrop-blur-md shadow-sm">
            <div class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-emerald-200/40 to-transparent"></div>
            <div class="absolute inset-y-0 left-0 w-48 bg-gradient-to-br from-emerald-50/60 via-transparent to-transparent pointer-events-none"></div>
            <div class="absolute -bottom-8 -right-8 h-32 w-32 rounded-full bg-emerald-100/40 blur-3xl pointer-events-none"></div>

            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <div class="flex flex-col gap-5">
                <div class="header-top flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  <!-- 左侧：标题和欢迎信息 -->
                  <div class="relative z-10">
                    <div class="flex items-center gap-3">
                      <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 shadow-lg shadow-violet-500/20">
                        <svg class="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>
                      <div>
                        <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent tracking-tight">AI 教学助理</h1>
                        <p class="text-sm text-gray-600 mt-1 font-medium">
                          基于当前教学数据，智能生成课堂洞察与行动建议。
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- 右侧：用户信息和操作 -->
                  <div class="relative z-10 flex items-center gap-4">
                    <!-- 用户信息 -->
                    <div class="flex flex-col items-end text-right">
                      <div class="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-800 bg-gray-100 rounded-full shadow-inner">
                        <svg class="h-4 w-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        <span>{{ userName }}</span>
                      </div>
                      <div
                        v-if="organizationInfo.length"
                        class="mt-2 flex flex-wrap justify-end gap-2 text-xs text-gray-500"
                      >
                        <span
                          v-for="(info, index) in organizationInfo"
                          :key="index"
                          class="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700 border border-emerald-100"
                        >
                          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 10-6 0 3 3 0 006 0z" />
                          </svg>
                          {{ info }}
                        </span>
                      </div>
                    </div>

                    <div class="h-10 w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent"></div>

                    <!-- 返回工作台按钮 -->
                    <button
                      @click="handleBackToDashboard"
                      class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl hover:bg-white hover:shadow-md transition-all"
                      title="返回教师工作台"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                      </svg>
                      返回工作台
                    </button>

                    <!-- 退出登录按钮 -->
                    <button
                      @click="handleLogout"
                      class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-rose-500 to-rose-600 rounded-xl shadow-lg shadow-rose-500/30 hover:shadow-xl hover:shadow-rose-500/40 hover:from-rose-600 hover:to-rose-700 transition-all transform hover:scale-105"
                    >
                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12H3m12 0l-4 4m4-4l-4-4m13 8v-8" />
                      </svg>
                      退出登录
                    </button>

                    <button
                      type="button"
                      @click="handleClose"
                      class="rounded-xl p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
                    >
                      <span class="sr-only">关闭</span>
                      <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path
                          fill-rule="evenodd"
                          d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10l-4.95-4.95A1 1 0 115.05 3.636L10 8.586z"
                          clip-rule="evenodd"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </header>

          <div class="grid gap-6 border-b border-gray-200 px-6 py-5 lg:grid-cols-[2fr,3fr]">
            <section class="space-y-4">
              <div class="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-4 shadow-lg">
                <span class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-500 to-teal-600"></span>
                <div class="flex items-center justify-between text-sm font-semibold text-gray-700">
                  <span>课堂概览</span>
                  <span
                    v-if="isLoading"
                    class="flex items-center gap-2 text-xs font-normal text-emerald-600"
                  >
                    <svg class="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      />
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 0 0-4 4H4z"
                      />
                    </svg>
                    同步数据...
                  </span>
                </div>

                <dl class="mt-3 grid grid-cols-3 gap-3 text-sm text-gray-700">
                  <div class="rounded-xl bg-emerald-50/50 px-3 py-2 shadow-sm border border-emerald-100/50">
                    <dt class="text-xs text-gray-600">草稿</dt>
                    <dd class="text-lg font-semibold text-emerald-700">
                      {{ lessonSummary?.draft ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-teal-50/50 px-3 py-2 shadow-sm border border-teal-100/50">
                    <dt class="text-xs text-gray-600">已发布</dt>
                    <dd class="text-lg font-semibold text-teal-700">
                      {{ lessonSummary?.published ?? 0 }}
                    </dd>
                  </div>
                  <div class="rounded-xl bg-cyan-50/50 px-3 py-2 shadow-sm border border-cyan-100/50">
                    <dt class="text-xs text-gray-600">待答问题</dt>
                    <dd class="text-lg font-semibold text-cyan-700">
                      {{ questionStats?.pending ?? 0 }}
                    </dd>
                  </div>
                </dl>

                <div
                  v-if="subjectGroupStats"
                  class="mt-3 grid grid-cols-2 gap-3 text-xs"
                >
                  <div class="rounded-xl bg-emerald-50/50 px-3 py-2 shadow-sm border border-emerald-100/50">
                    <p class="font-medium text-gray-600">我的教研组</p>
                    <p class="text-base font-semibold text-emerald-700">
                      {{ subjectGroupStats.my_groups }}
                    </p>
                  </div>
                  <div class="rounded-xl bg-teal-50/50 px-3 py-2 shadow-sm border border-teal-100/50">
                    <p class="font-medium text-gray-600">共享教案</p>
                    <p class="text-base font-semibold text-teal-700">
                      {{ subjectGroupStats.my_shared_lessons }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="space-y-3">
                <label class="text-sm font-semibold text-gray-900">助手关注主题</label>
                <div class="flex flex-wrap gap-2 text-xs font-medium">
                  <button
                    v-for="option in topicOptions"
                    :key="option.value"
                    type="button"
                    @click="selectedTopic = option.value"
                    :class="[
                      'rounded-full px-3 py-1 transition border',
                      selectedTopic === option.value
                        ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30'
                        : 'border-emerald-300 text-emerald-700 bg-white hover:bg-emerald-50',
                    ]"
                  >
                    {{ option.label }}
                  </button>
                </div>
              </div>

              <!-- 智能体选择 -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-semibold text-gray-900">智能体</label>
                  <button
                    type="button"
                    @click="showCreateAgentModal = true"
                    class="inline-flex items-center gap-1 rounded-full border border-violet-300 px-2.5 py-1 text-xs font-medium text-violet-700 transition hover:bg-violet-50 hover:border-violet-400"
                  >
                    <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    创建智能体
                  </button>
                </div>
                <div class="space-y-2">
                  <select
                    v-model="selectedAgentId"
                    class="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                  >
                    <option value="">默认智能体（无特殊提示词）</option>
                    <optgroup v-if="customAgents.length > 0" label="自定义智能体">
                      <option
                        v-for="agent in customAgents"
                        :key="agent.id"
                        :value="agent.id"
                      >
                        {{ agent.name }}
                      </option>
                    </optgroup>
                    <optgroup label="预设智能体">
                      <option
                        v-for="agent in presetAgents"
                        :key="agent.id"
                        :value="agent.id"
                      >
                        {{ agent.name }}
                      </option>
                    </optgroup>
                  </select>
                  <div
                    v-if="selectedAgent && selectedAgent.description"
                    class="rounded-lg border border-emerald-100 bg-emerald-50/50 px-3 py-2 text-xs text-emerald-700"
                  >
                    {{ selectedAgent.description }}
                  </div>
                  <div
                    v-if="selectedAgent && selectedAgent.isCustom"
                    class="flex items-center justify-end gap-2"
                  >
                    <button
                      type="button"
                      @click="handleEditAgent(selectedAgent)"
                      class="text-xs text-gray-600 hover:text-gray-900 transition"
                    >
                      编辑
                    </button>
                    <button
                      type="button"
                      @click="handleDeleteAgent(selectedAgent.id)"
                      class="text-xs text-red-600 hover:text-red-800 transition"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>

              <!-- 教案优化功能（仅在教案共创主题显示） -->
              <div v-if="selectedTopic === 'lesson_plan'" class="space-y-3">
                <div class="group relative overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/80 to-teal-50/60 p-4 shadow-sm">
                  <div class="flex items-center justify-between">
                    <div>
                      <h3 class="text-sm font-semibold text-gray-900">教案优化分析</h3>
                      <p class="mt-1 text-xs text-gray-600">
                        基于学习科学理论，全面分析教案并提供优化建议
                      </p>
                    </div>
                  </div>

                  <!-- 教案选择器 -->
                  <div v-if="availableLessons.length > 0" class="mt-3 space-y-2">
                    <label class="text-xs font-medium text-gray-700">选择要优化的教案</label>
                    <select
                      v-model="selectedLessonId"
                      class="w-full rounded-lg border border-emerald-200 bg-white px-3 py-2 text-xs text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
                    >
                      <option :value="null">请选择教案...</option>
                      <option
                        v-for="lesson in availableLessons"
                        :key="lesson.id"
                        :value="lesson.id"
                      >
                        {{ lesson.title }} ({{ lesson.status === 'draft' ? '草稿' : lesson.status === 'published' ? '已发布' : '已归档' }})
                      </option>
                    </select>
                  </div>
                  <div v-else class="mt-3 text-xs text-gray-500">
                    暂无可用教案
                  </div>

                  <!-- 优化按钮 -->
                  <button
                    type="button"
                    :disabled="!selectedLessonId || isOptimizing"
                    @click="handleOptimizeLesson"
                    class="mt-3 w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-violet-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-violet-500/40 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <svg
                      v-if="isOptimizing"
                      class="h-4 w-4 animate-spin"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      />
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                      />
                    </svg>
                    <svg
                      v-else
                      class="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                    <span>{{ isOptimizing ? '分析中...' : '一键优化分析' }}</span>
                  </button>
                </div>
              </div>

              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="text-sm font-semibold text-gray-900">智能推荐提问</label>
                  <button
                    type="button"
                    class="rounded-full border border-emerald-300 px-3 py-1 text-xs font-medium text-emerald-700 transition hover:bg-emerald-500 hover:text-white hover:border-emerald-500"
                    @click="refreshSuggestions"
                  >
                    换一批
                  </button>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="prompt in recommendedPrompts"
                    :key="prompt"
                    type="button"
                    class="rounded-xl border border-emerald-100 bg-emerald-50/50 px-3 py-1.5 text-left text-xs text-emerald-700 transition hover:border-emerald-300 hover:bg-emerald-100/70"
                    @click="applyPrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>

              <div class="space-y-2">
                <label class="text-sm font-semibold text-gray-900" for="assistant-question">
                  提问或描述需求
                </label>
                <textarea
                  id="assistant-question"
                  v-model="question"
                  rows="4"
                  class="w-full resize-none rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 bg-white/80 backdrop-blur-sm"
                  placeholder="例如：帮我总结目前课堂的亮点和下节课的优化建议。"
                ></textarea>
              </div>

              <div class="space-y-2">
                <!-- 显示当前使用的智能体 -->
                <div
                  v-if="selectedAgent"
                  class="rounded-lg border border-violet-200 bg-violet-50/50 px-3 py-2 text-xs"
                >
                  <div class="flex items-center gap-2">
                    <svg class="h-3.5 w-3.5 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <span class="font-medium text-violet-900">使用智能体：</span>
                    <span class="text-violet-700">{{ selectedAgent.name }}</span>
                    <span v-if="selectedAgent.description" class="text-violet-600">- {{ selectedAgent.description }}</span>
                  </div>
                </div>
                
                <div class="flex items-center justify-between gap-3">
                  <p class="text-xs text-gray-600">
                    <span v-if="selectedAgent">
                      将使用 <strong>{{ selectedAgent.name }}</strong> 的角色设定来生成回答。
                    </span>
                    <span v-else>
                      AI 会综合当前仪表盘数据，生成总结与下一步行动建议。
                    </span>
                  </p>
                  <button
                    type="button"
                    :disabled="!isReady || isSubmitting"
                    class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-emerald-500/40 enabled:focus:outline-none enabled:focus:ring-2 enabled:focus:ring-emerald-500/50 disabled:cursor-not-allowed disabled:opacity-60"
                    @click="handleSubmit"
                  >
                    <svg
                      v-if="isSubmitting"
                      class="h-4 w-4 animate-spin"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      />
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                      />
                    </svg>
                    <span>{{ isSubmitting ? '生成中...' : '生成建议' }}</span>
                  </button>
                </div>
              </div>

              <p v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50/80 backdrop-blur-sm px-3 py-2 text-xs text-red-700 shadow-sm">
                {{ errorMessage }}
              </p>
            </section>

            <section
              class="flex max-h-[70vh] flex-col gap-4 overflow-hidden rounded-2xl border border-gray-100 bg-gradient-to-br from-emerald-50/30 via-teal-50/20 to-cyan-50/30 p-5"
            >
              <div
                v-if="response"
                class="flex-1 overflow-y-auto rounded-2xl bg-white/90 backdrop-blur-sm p-5 text-sm text-gray-900 shadow-inner border border-gray-100"
              >
                <div class="flex items-center justify-between gap-3 border-b border-gray-200 pb-3">
                  <div class="flex items-center gap-3">
                    <h3 class="text-base font-semibold text-gray-900">助手回答</h3>
                    <div
                      v-if="selectedAgent"
                      class="inline-flex items-center gap-1 rounded-full bg-violet-100 px-2 py-0.5 text-xs text-violet-700"
                    >
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <span>{{ selectedAgent.name }}</span>
                    </div>
                  </div>
                  <div class="flex items-center gap-3 text-xs text-gray-600">
                    <span v-if="response.model_used">模型：{{ response.model_used }}</span>
                    <span v-if="response.response_time_ms">
                      {{ Math.round(response.response_time_ms) }} ms
                    </span>
                    <span v-if="response.confidence !== undefined">
                      置信度 {{ Math.round((response.confidence ?? 0) * 100) }}%
                    </span>
                  </div>
                </div>

                <div class="mt-3 text-sm leading-relaxed text-slate-800">
                  <MarkdownPreview :content="response.answer" />
                </div>

                <div v-if="response.insights.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">关键洞察</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="insight in response.insights"
                      :key="insight.title"
                      class="rounded-xl border border-emerald-200 bg-emerald-50/50 px-3 py-2 text-sm text-emerald-900"
                    >
                      <p class="font-semibold">{{ insight.title }}</p>
                      <p class="mt-1 text-xs text-emerald-700">{{ insight.detail }}</p>
                      <p v-if="insight.metric" class="mt-1 text-[11px] text-gray-600">
                        {{ insight.metric }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.suggested_actions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">建议行动</h4>
                  <ul class="space-y-2">
                    <li
                      v-for="action in response.suggested_actions"
                      :key="action.label"
                      class="rounded-xl border border-teal-200 bg-teal-50/50 px-3 py-2 text-sm text-teal-900"
                    >
                      <p class="font-semibold text-gray-900">{{ action.label }}</p>
                      <p v-if="action.description" class="mt-1 text-xs text-gray-700">
                        {{ action.description }}
                      </p>
                    </li>
                  </ul>
                </div>

                <div v-if="response.follow_up_questions.length" class="mt-4 space-y-3">
                  <h4 class="text-sm font-semibold text-gray-900">续问建议</h4>
                  <div class="flex flex-wrap gap-2">
                    <button
                      v-for="item in response.follow_up_questions"
                      :key="item"
                      type="button"
                      class="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-700 transition hover:border-emerald-400 hover:bg-emerald-50"
                      @click="applyPrompt(item)"
                    >
                      {{ item }}
                    </button>
                  </div>
                </div>

                <div
                  v-if="response.context_used?.length"
                  class="mt-4 border-t border-gray-200 pt-3 text-[11px] text-gray-600"
                >
                  <p>已引用的仪表盘数据：</p>
                  <ul class="mt-1 list-outside list-disc space-y-1 pl-4">
                    <li v-for="item in response.context_used" :key="item">
                      {{ item }}
                    </li>
                  </ul>
                </div>
              </div>

              <div
                v-else
                class="flex flex-1 flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white/70 backdrop-blur-sm text-center text-sm text-gray-600"
              >
                <div
                  class="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-r from-violet-500 via-purple-500 to-fuchsia-500 text-2xl text-white shadow-lg shadow-violet-500/30"
                >
                  🤖
                </div>
                <p class="font-semibold text-gray-900">等待您的问题</p>
                <p class="mt-1 text-xs text-gray-600">
                  <span v-if="selectedTopic === 'lesson_plan'">
                    选择教案并点击"一键优化分析"，或输入问题获取建议。
                  </span>
                  <span v-else>
                    选择主题并输入问题，AI 将结合最新数据给出建议。
                  </span>
                </p>
              </div>
            </section>
          </div>

          <footer
            class="flex items-center justify-between border-t border-gray-200 bg-gradient-to-r from-emerald-50/50 via-teal-50/30 to-cyan-50/30 px-6 py-4 text-xs text-gray-600"
          >
            <span>AI 输出仅供教学辅助，请结合课堂实际判断使用。</span>
            <button
              type="button"
              class="text-emerald-700 hover:text-emerald-800 font-medium transition-colors"
              @click="handleClose"
            >
              关闭
            </button>
          </footer>
        </div>
      </div>
    </div>
  </Transition>

  <!-- 创建/编辑智能体模态框 -->
  <Transition name="modal">
    <div
      v-if="showCreateAgentModal"
      class="fixed inset-0 z-[60] overflow-y-auto"
      @click.self="showCreateAgentModal = false"
    >
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-slate-900/60"></div>
        <div
          class="relative w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all"
        >
          <div class="px-6 py-5 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900">
                {{ editingAgent ? '编辑智能体' : '创建自定义智能体' }}
              </h3>
              <button
                type="button"
                @click="showCreateAgentModal = false"
                class="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition"
              >
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fill-rule="evenodd"
                    d="M10 8.586l4.95-4.95a1 1 0 111.414 1.414L11.414 10l4.95 4.95a1 1 0 01-1.414 1.414L10 11.414l-4.95 4.95a1 1 0 01-1.414-1.414L8.586 10l-4.95-4.95A1 1 0 115.05 3.636L10 8.586z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>

          <div class="px-6 py-5 space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                智能体名称 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="agentForm.name"
                type="text"
                placeholder="例如：课程设计专家、学习评估助手"
                class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                描述（可选）
              </label>
              <input
                v-model="agentForm.description"
                type="text"
                placeholder="简要描述这个智能体的用途"
                class="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                提示词 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="agentForm.prompt"
                rows="8"
                placeholder="输入自定义提示词，定义智能体的角色、能力和行为方式。例如：&#10;&#10;你是一位专注于STEM教育的课程设计专家，擅长基于建构主义学习理论设计探究式教学活动。你的回答应该：&#10;1. 结合5E教学模型（参与、探索、解释、深化、评价）&#10;2. 考虑不同学习风格的学生需求&#10;3. 提供可操作的具体建议&#10;4. 使用简洁、专业的语言"
                class="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 font-mono"
              ></textarea>
              <div class="mt-2 flex items-center justify-between">
                <p class="text-xs text-gray-500">
                  提示词将作为系统提示词，影响AI的回答风格和内容
                </p>
                <button
                  type="button"
                  @click="showPromptTemplates = !showPromptTemplates"
                  class="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  {{ showPromptTemplates ? '隐藏' : '显示' }}模板
                </button>
              </div>
              <div v-if="showPromptTemplates" class="mt-2 space-y-2">
                <div class="rounded-lg border border-emerald-100 bg-emerald-50/50 p-3 text-xs">
                  <p class="font-medium text-emerald-900 mb-2">提示词模板：</p>
                  <div class="space-y-2">
                    <button
                      type="button"
                      @click="applyPromptTemplate('curriculum')"
                      class="block w-full text-left text-emerald-700 hover:text-emerald-900 hover:bg-emerald-100 rounded px-2 py-1 transition"
                    >
                      📚 课程设计专家模板
                    </button>
                    <button
                      type="button"
                      @click="applyPromptTemplate('assessment')"
                      class="block w-full text-left text-emerald-700 hover:text-emerald-900 hover:bg-emerald-100 rounded px-2 py-1 transition"
                    >
                      📊 学习评估助手模板
                    </button>
                    <button
                      type="button"
                      @click="applyPromptTemplate('question')"
                      class="block w-full text-left text-emerald-700 hover:text-emerald-900 hover:bg-emerald-100 rounded px-2 py-1 transition"
                    >
                      ❓ 提问技巧教练模板
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                @click="showCreateAgentModal = false"
                class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                取消
              </button>
              <button
                type="button"
                @click="handleSaveAgent"
                :disabled="!agentForm.name.trim() || !agentForm.prompt.trim()"
                class="rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 transition enabled:hover:shadow-xl enabled:hover:shadow-emerald-500/40 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {{ editingAgent ? '保存' : '创建' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { PropType } from 'vue'
import { useUserStore } from '@/store/user'
import type { QuestionStats } from '@/types/question'
import type { SubjectGroupStatistics } from '@/types/subjectGroup'
import type { Lesson } from '@/types/lesson'
import type {
  TeacherAssistantContextPayload,
  TeacherAssistantResponse,
  TeacherAssistantTopic,
  CustomAgent,
  AgentOption,
} from '@/types/assistant'
import assistantService from '@/services/assistant'
import MarkdownPreview from '@/components/Common/MarkdownPreview.vue'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '教师')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)

const organizationInfo = computed(() => {
  const info: string[] = []
  if (regionName.value) {
    info.push(`区域：${regionName.value}`)
  }
  if (schoolName.value) {
    info.push(`学校：${schoolName.value}`)
  }
  if (gradeName.value) {
    info.push(`年级：${gradeName.value}`)
  }
  return info
})

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  lessonSummary: {
    type: Object as PropType<Record<string, number>>,
    default: () => ({ draft: 0, published: 0, archived: 0 }),
  },
  questionStats: {
    type: Object as PropType<QuestionStats | null>,
    default: null,
  },
  subjectGroupStats: {
    type: Object as PropType<SubjectGroupStatistics | null>,
    default: null,
  },
  latestLessons: {
    type: Array as PropType<Lesson[]>,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'close'])

const question = ref('')
const selectedTopic = ref<TeacherAssistantTopic>('pdca')
const selectedLessonId = ref<number | null>(null)
const isSubmitting = ref(false)
const isOptimizing = ref(false)
const errorMessage = ref<string | null>(null)
const response = ref<TeacherAssistantResponse | null>(null)
const optimizationReport = ref<any>(null)
const suggestionOffset = ref(0)

// 智能体相关状态
const selectedAgentId = ref<string>('')
const showCreateAgentModal = ref(false)
const editingAgent = ref<CustomAgent | null>(null)
const showPromptTemplates = ref(false)
const agentForm = ref({
  name: '',
  description: '',
  prompt: '',
})

// 预设智能体
const presetAgents: AgentOption[] = [
  {
    id: 'curriculum_designer',
    name: '课程设计专家',
    description: '专注于各学科的教学设计，基于建构主义学习理论',
    prompt: `你是一位专业的教学助手，专门帮助教师设计各学科（语文、数学、科学、STEM等）的课程和教案。

你的核心职责是：
1. **理解教学需求**：仔细分析教师提出的教学设计问题，理解课程内容、学生特点和教学目标
2. **提供教学设计方案**：基于建构主义学习理论和学习科学原理，设计完整的教学方案
3. **应用教学模型**：结合5E教学模型（参与、探索、解释、深化、评价）或其他适合的教学模型
4. **考虑学生差异**：考虑不同学习风格（视觉型、听觉型、动觉型）和认知水平的学生需求
5. **提供具体建议**：给出可操作、可实施的具体教学步骤和活动设计

重要提醒：
- 你是一个**教学助手**，专注于帮助教师设计课程和教案
- 当教师提出教学设计问题时，你应该提供完整的教学方案，包括教学目标、活动设计、评价方式等
- 不要回答编程、技术实现等非教学相关的问题
- 使用简洁、专业、易懂的教学语言

请始终以教学设计的角度来回答教师的问题。`,
  },
  {
    id: 'assessment_specialist',
    name: '学习评估助手',
    description: '专注于形成性评价和元认知反思设计',
    prompt: '你是一位学习评估专家，擅长设计形成性评价和促进学生元认知反思的活动。你的回答应该：1. 基于布鲁姆分类法设计评价层次 2. 提供多元化的评价方式 3. 强调学生的自我监控和反思能力',
  },
  {
    id: 'question_coach',
    name: '提问技巧教练',
    description: '擅长苏格拉底式提问和引导学生思考',
    prompt: '你是一位提问技巧教练，擅长使用苏格拉底式提问法引导学生深入思考。你的回答应该：1. 提供澄清性、探索性、证据性等不同类型的问题 2. 帮助学生识别知识缺口 3. 促进元认知反思',
  },
]

// 从 localStorage 加载自定义智能体
const loadCustomAgents = (): CustomAgent[] => {
  try {
    const stored = localStorage.getItem('teacher_custom_agents')
    if (stored) {
      const parsed = JSON.parse(stored)
      // 验证数据格式
      if (Array.isArray(parsed)) {
        return parsed.filter((agent) => 
          agent && 
          typeof agent.id === 'string' && 
          typeof agent.name === 'string' && 
          typeof agent.prompt === 'string'
        )
      }
    }
  } catch (error) {
    console.error('Failed to load custom agents:', error)
  }
  return []
}

// 保存自定义智能体到 localStorage
const saveCustomAgents = (agents: CustomAgent[]) => {
  try {
    const json = JSON.stringify(agents)
    localStorage.setItem('teacher_custom_agents', json)
    
    // 验证保存是否成功
    const verify = localStorage.getItem('teacher_custom_agents')
    if (verify === json) {
      console.log('✓ Custom agents saved successfully:', agents.length, 'agents')
    } else {
      console.error('✗ Custom agents save verification failed')
    }
  } catch (error) {
    console.error('Failed to save custom agents:', error)
    // 如果存储失败（可能是存储空间不足），尝试清理旧数据
    try {
      localStorage.removeItem('teacher_custom_agents')
      console.warn('Cleared corrupted custom agents data')
    } catch (clearError) {
      console.error('Failed to clear custom agents:', clearError)
    }
  }
}

const customAgents = ref<CustomAgent[]>(loadCustomAgents())

// 所有可用的智能体（预设 + 自定义）
const allAgents = computed<AgentOption[]>(() => {
  const agents: AgentOption[] = [...presetAgents]
  customAgents.value.forEach((agent) => {
    agents.push({
      id: agent.id,
      name: agent.name,
      description: agent.description,
      prompt: agent.prompt,
      isCustom: true,
    })
  })
  return agents
})

// 当前选中的智能体
const selectedAgent = computed<AgentOption | null>(() => {
  if (!selectedAgentId.value) return null
  const agent = allAgents.value.find((a) => a.id === selectedAgentId.value) || null
  // 调试：如果找到智能体但prompt为空，记录警告
  if (agent && (!agent.prompt || !agent.prompt.trim())) {
    console.warn('⚠️ Found agent but prompt is empty:', {
      id: agent.id,
      name: agent.name,
      hasPrompt: !!agent.prompt,
      promptType: typeof agent.prompt,
      promptValue: agent.prompt
    })
  }
  return agent
})

const topicOptions: Array<{ label: string; value: TeacherAssistantTopic }> = [
  { label: '教学循环 (PDCA)', value: 'pdca' },
  { label: '教案共创', value: 'lesson_plan' },
  { label: '课堂问答辅导', value: 'qa' },
]

const normalizedContext = computed<TeacherAssistantContextPayload>(() => {
  const payload: TeacherAssistantContextPayload = {}

  if (props.lessonSummary) {
    const totalValue = Object.values(props.lessonSummary).reduce(
      (sum, value) => sum + (Number.isFinite(value) ? value : 0),
      0
    )
    if (totalValue > 0) {
      payload.lesson_summary = props.lessonSummary
    }
  }

  if (props.questionStats && (props.questionStats.total ?? 0) > 0) {
    payload.question_stats = props.questionStats
  }

  if (
    props.subjectGroupStats &&
    (props.subjectGroupStats.total_groups ?? 0) > 0
  ) {
    payload.subject_group_stats = props.subjectGroupStats
  }

  if (props.latestLessons.length > 0) {
    payload.recent_lessons = props.latestLessons.slice(0, 3).map((lesson) => ({
      id: lesson.id,
      title: lesson.title,
      status: lesson.status,
      updated_at: lesson.updated_at,
    }))
  }

  return payload
})

const recommendedPrompts = computed(() => {
  const promptsByTopic: Record<TeacherAssistantTopic, string[]> = {
    pdca: [
      '结合当前教案状态，帮我安排下一周的课堂重点和改进行动。',
      '根据待答问题和发布教案情况，提出课堂循环中的薄弱环节。',
      '请总结目前课堂执行的亮点，并给出循证改进建议。',
    ],
    lesson_plan: [
      '根据最近发布的教案，帮我提炼一次共研分享提纲。',
      '为当前草稿教案生成一个课堂导入活动。',
      '请为最近的教案提出一个面向教研组的优化建议。',
    ],
    qa: [
      '帮我整理学生提问的主要关注点，并给出统一答复框架。',
      '请为待答问题生成一份高质量回答草稿。',
      '结合问答数据，为家校沟通准备一段反馈说明。',
    ],
  }

  const basePrompts = promptsByTopic[selectedTopic.value] ?? []

  // 根据数据追加定制推荐
  const customPrompts: string[] = []
  const stats = props.questionStats
  if (stats && stats.pending > 0) {
    customPrompts.push(`针对当前 ${stats.pending} 个待答问题，生成优先处理建议。`)
  }

  if (
    props.lessonSummary &&
    (props.lessonSummary.draft ?? 0) > (props.lessonSummary.published ?? 0)
  ) {
    customPrompts.push('草稿教案较多，请帮我规划一份整理与发布的时间表。')
  }

  if (
    props.subjectGroupStats &&
    props.subjectGroupStats.my_shared_lessons === 0 &&
    selectedTopic.value === 'lesson_plan'
  ) {
    customPrompts.push('我还未在教研组共享教案，请给出一个分享流程与内容要点。')
  }

  const suggestions = [...basePrompts, ...customPrompts]
  if (suggestions.length <= 3) {
    return suggestions
  }

  const start = suggestionOffset.value % suggestions.length
  return suggestions.slice(start, start + 3)
})

const isReady = computed(() => question.value.trim().length >= 4)

const availableLessons = computed(() => {
  return props.latestLessons.filter((lesson) => 
    lesson.status === 'draft' || lesson.status === 'published'
  )
})

function handleClose() {
  emit('update:modelValue', false)
  emit('close')
}

// 返回工作台
function handleBackToDashboard() {
  handleClose()
  router.push('/teacher')
}

// 退出登录
function handleLogout() {
  userStore.logout()
  router.push('/login')
}

function applyPrompt(prompt: string) {
  question.value = prompt
}

function refreshSuggestions() {
  suggestionOffset.value += 1
}

// 智能体相关函数
function handleSaveAgent() {
  if (!agentForm.value.name.trim() || !agentForm.value.prompt.trim()) {
    return
  }

  const now = new Date().toISOString()

  if (editingAgent.value) {
    // 更新现有智能体
    const index = customAgents.value.findIndex((a) => a.id === editingAgent.value!.id)
    if (index !== -1) {
      // 使用新数组确保响应式更新
      const updated = [...customAgents.value]
      updated[index] = {
        ...updated[index],
        name: agentForm.value.name.trim(),
        description: agentForm.value.description.trim(),
        prompt: agentForm.value.prompt.trim(),
        updated_at: now,
      }
      customAgents.value = updated
      saveCustomAgents(customAgents.value)
      console.log('Agent updated:', updated[index].name)
    }
  } else {
    // 创建新智能体
    const description = agentForm.value.description.trim()
    const newAgent: CustomAgent = {
      id: `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: agentForm.value.name.trim(),
      description: description || undefined,
      prompt: agentForm.value.prompt.trim(),
      created_at: now,
      updated_at: now,
    }
    // 使用新数组确保响应式更新
    customAgents.value = [...customAgents.value, newAgent]
    saveCustomAgents(customAgents.value)
    selectedAgentId.value = newAgent.id
    console.log('Agent created:', newAgent.name, 'Total agents:', customAgents.value.length)
  }

  // 重置表单并关闭模态框
  agentForm.value = { name: '', description: '', prompt: '' }
  editingAgent.value = null
  showCreateAgentModal.value = false
}

function handleEditAgent(agent: AgentOption) {
  if (!agent.isCustom) return

  const customAgent = customAgents.value.find((a) => a.id === agent.id)
  if (customAgent) {
    editingAgent.value = customAgent
    agentForm.value = {
      name: customAgent.name,
      description: customAgent.description || '',
      prompt: customAgent.prompt,
    }
    showCreateAgentModal.value = true
  }
}

function handleDeleteAgent(agentId: string) {
  if (confirm('确定要删除这个智能体吗？')) {
    // 使用新数组确保响应式更新
    customAgents.value = customAgents.value.filter((a) => a.id !== agentId)
    saveCustomAgents(customAgents.value)
    if (selectedAgentId.value === agentId) {
      selectedAgentId.value = ''
    }
    console.log('Agent deleted. Remaining agents:', customAgents.value.length)
  }
}

// 提示词模板
const promptTemplates = {
  curriculum: `你是一位专业的教学助手，专门帮助教师设计各学科（语文、数学、科学、STEM等）的课程和教案。

你的核心职责是：
1. **理解教学需求**：仔细分析教师提出的教学设计问题，理解课程内容、学生特点和教学目标
2. **提供教学设计方案**：基于建构主义学习理论和学习科学原理，设计完整的教学方案
3. **应用教学模型**：结合5E教学模型（参与、探索、解释、深化、评价）或其他适合的教学模型
4. **考虑学生差异**：考虑不同学习风格（视觉型、听觉型、动觉型）和认知水平的学生需求
5. **提供具体建议**：给出可操作、可实施的具体教学步骤和活动设计

重要提醒：
- 你是一个**教学助手**，专注于帮助教师设计课程和教案
- 当教师提出教学设计问题时，你应该提供完整的教学方案，包括教学目标、活动设计、评价方式等
- 不要回答编程、技术实现等非教学相关的问题
- 使用简洁、专业、易懂的教学语言

请始终以教学设计的角度来回答教师的问题。`,
  assessment: `你是一位学习评估专家，擅长设计形成性评价和促进学生元认知反思的活动。

你的回答应该：
1. 基于布鲁姆分类法设计多层次的评价方式
2. 提供多元化的评价方法（自评、互评、师评）
3. 强调形成性评价和过程性反馈
4. 设计促进学生自我监控和反思的问题
5. 结合最近发展区理论提供脚手架支持

使用清晰、结构化的方式呈现评价方案。`,
  question: `你是一位提问技巧教练，擅长使用苏格拉底式提问法引导学生深入思考。

你的回答应该：
1. 提供不同类型的提问（澄清性、探索性、证据性、视角性、影响性）
2. 帮助学生识别知识缺口和认知盲点
3. 促进元认知反思和自我监控
4. 设计问题序列，引导学生逐步深入思考
5. 结合费曼学习法，鼓励学生用自己的话解释概念

使用启发式、引导性的语言，避免直接给出答案。`,
}

function applyPromptTemplate(templateKey: keyof typeof promptTemplates) {
  agentForm.value.prompt = promptTemplates[templateKey]
  showPromptTemplates.value = false
}

async function handleSubmit() {
  if (!isReady.value || isSubmitting.value) {
    return
  }

  errorMessage.value = null
  isSubmitting.value = true
  optimizationReport.value = null

  try {
    // 构建上下文：如果有选中的智能体，将提示词添加到 context 中
    const contextWithAgent = { ...normalizedContext.value }
    
    // 调试信息：检查智能体选择状态
    console.log('=== Agent Selection Debug ===')
    console.log('selectedAgentId.value:', selectedAgentId.value)
    console.log('selectedAgent.value:', selectedAgent.value)
    console.log('allAgents.value:', allAgents.value.map(a => ({ id: a.id, name: a.name, hasPrompt: !!a.prompt })))
    
    // 将智能体的提示词通过 agent_prompt 字段传递
    if (selectedAgent.value) {
      console.log('=== Agent Found ===')
      console.log('Agent name:', selectedAgent.value.name)
      console.log('Agent ID:', selectedAgent.value.id)
      console.log('Agent prompt exists:', !!selectedAgent.value.prompt)
      console.log('Agent prompt type:', typeof selectedAgent.value.prompt)
      
      if (selectedAgent.value.prompt && selectedAgent.value.prompt.trim()) {
        contextWithAgent.agent_prompt = selectedAgent.value.prompt.trim()
        console.log('✅ Agent prompt set, length:', contextWithAgent.agent_prompt.length)
        console.log('Prompt preview:', contextWithAgent.agent_prompt.substring(0, 200))
      } else {
        console.warn('⚠️ Agent selected but prompt is empty or undefined')
        console.warn('Agent prompt value:', selectedAgent.value.prompt)
      }
      console.log('Question:', question.value.trim())
    } else {
      console.log('=== Using Default Assistant ===')
      console.log('No agent selected or agent not found')
      console.log('selectedAgentId:', selectedAgentId.value)
      console.log('Available agents count:', allAgents.value.length)
      if (selectedAgentId.value) {
        console.warn('⚠️ selectedAgentId is set but agent not found in allAgents')
        console.warn('Looking for ID:', selectedAgentId.value)
        const found = allAgents.value.find(a => a.id === selectedAgentId.value)
        console.warn('Found agent:', found)
      }
    }

    console.log('=== Request Payload ===')
    console.log('Question:', question.value.trim())
    console.log('Topic:', selectedTopic.value)
    console.log('Has agent_prompt:', !!contextWithAgent.agent_prompt)
    console.log('Agent prompt value:', contextWithAgent.agent_prompt ? contextWithAgent.agent_prompt.substring(0, 100) + '...' : null)
    console.log('Context keys:', Object.keys(contextWithAgent))

    const assistantResponse = await assistantService.askTeacherAssistant({
      question: question.value.trim(),
      topic: selectedTopic.value,
      context: contextWithAgent,
      lesson_id: selectedLessonId.value || undefined,
    })

    console.log('✅ AI Response received:', {
      model: assistantResponse.model_used,
      confidence: assistantResponse.confidence,
      answerLength: assistantResponse.answer?.length,
      hasInsights: assistantResponse.insights?.length > 0,
      hasActions: assistantResponse.suggested_actions?.length > 0,
    })
    
    // 打印完整的回答内容，便于调试
    console.log('📝 AI Answer Content:', assistantResponse.answer)
    console.log('📝 AI Answer Preview (first 500 chars):', assistantResponse.answer?.substring(0, 500))
    
    // 检查回答内容是否符合预期
    if (selectedAgent.value && selectedAgent.value.prompt) {
      const isProgrammingAnswer = assistantResponse.answer?.includes('编程') || 
                                   assistantResponse.answer?.includes('代码') ||
                                   assistantResponse.answer?.includes('def ') ||
                                   assistantResponse.answer?.includes('function')
      const isTeachingAnswer = assistantResponse.answer?.includes('教学') ||
                               assistantResponse.answer?.includes('教案') ||
                               assistantResponse.answer?.includes('设计') ||
                               assistantResponse.answer?.includes('目标')
      
      if (isProgrammingAnswer && !isTeachingAnswer) {
        console.warn('⚠️ 警告：选择了课程设计专家，但回答似乎是编程相关的内容')
        console.warn('   这可能说明智能体的提示词没有生效')
      } else {
        console.log('✅ 回答内容符合预期（教学设计相关）')
      }
    }

    response.value = assistantResponse
  } catch (error: any) {
    // 详细的错误日志
    console.error('❌ AI Assistant Error:', {
      error,
      errorType: error?.constructor?.name,
      errorMessage: error?.message,
      errorResponse: error?.response,
      errorResponseData: error?.response?.data,
      errorResponseStatus: error?.response?.status,
      errorStack: error?.stack,
    })
    
    // 构建详细的错误消息
    let detailedError = '请求 AI 助手失败，请稍后重试。'
    
    if (error?.response?.data?.detail) {
      detailedError = `服务器错误: ${error.response.data.detail}`
    } else if (error?.response?.status) {
      detailedError = `请求失败 (状态码: ${error.response.status})`
      if (error.response.status === 500) {
        detailedError += ' - 服务器内部错误，请检查后端日志'
      } else if (error.response.status === 401) {
        detailedError += ' - 未授权，请重新登录'
      } else if (error.response.status === 403) {
        detailedError += ' - 权限不足'
      }
    } else if (error?.message) {
      detailedError = error.message
    } else if (error?.toString) {
      detailedError = error.toString()
    }
    
    errorMessage.value = detailedError
    
    // 如果是网络错误，提供更多信息
    if (!error?.response) {
      console.error('⚠️  可能是网络连接问题或后端服务未启动')
      console.error('   请检查：')
      console.error('   1. 后端服务是否运行在 http://localhost:8000')
      console.error('   2. 网络连接是否正常')
      console.error('   3. 查看后端日志: tail -f logs/backend.log')
    }
  } finally {
    isSubmitting.value = false
  }
}

async function handleOptimizeLesson() {
  if (!selectedLessonId.value || isOptimizing.value) {
    return
  }

  errorMessage.value = null
  isOptimizing.value = true
  response.value = null

  try {
    // 构建优化分析的问题
    const selectedLesson = props.latestLessons.find(l => l.id === selectedLessonId.value)
    const optimizationQuestion = `请对教案《${selectedLesson?.title || '当前教案'}》进行全面优化分析，包括：
1. 教学目标设计（是否明确、是否基于布鲁姆分类法）
2. 活动设计（是否符合5E模型、是否有认知层次）
3. 学生参与度（是否有主动输出、是否有互动）
4. 评价设计（是否有形成性评价、是否有元认知反思）
5. 学习科学理论应用（是否应用了相关理论）

请提供结构化的分析报告，包括：
- 总体评分（0-100分）
- 各维度评分和详细分析
- 优势、待改进点、具体优化建议
- 基于学习科学理论的详细优化方案`

    // 构建上下文，包含智能体提示词（如果选择了智能体）
    const contextWithAgent = {
      ...normalizedContext.value,
      lesson_outline: selectedLesson ? `教案标题：${selectedLesson.title}\n状态：${selectedLesson.status}` : undefined,
    }
    
    // 将智能体的提示词通过 agent_prompt 字段传递
    if (selectedAgent.value && selectedAgent.value.prompt) {
      contextWithAgent.agent_prompt = selectedAgent.value.prompt
      console.log('Using agent for lesson optimization:', selectedAgent.value.name)
    }

    const assistantResponse = await assistantService.askTeacherAssistant({
      question: optimizationQuestion,
      topic: 'lesson_plan',
      context: contextWithAgent,
      lesson_id: selectedLessonId.value,
    })

    // 解析优化报告（从 AI 回答中提取结构化信息）
    optimizationReport.value = parseOptimizationReport(assistantResponse.answer, assistantResponse)
  } catch (error: any) {
    errorMessage.value = error.message || '教案优化分析失败，请稍后重试。'
  } finally {
    isOptimizing.value = false
  }
}

function parseOptimizationReport(answer: string, response: TeacherAssistantResponse): any {
  // 尝试从回答中提取结构化信息
  // 如果 AI 返回的是结构化 JSON，直接解析
  // 否则从文本中提取关键信息
  
  try {
    // 尝试解析 JSON（如果 AI 返回了结构化数据）
    const jsonMatch = answer.match(/```json\s*([\s\S]*?)\s*```/) || answer.match(/\{[\s\S]*\}/)
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[1] || jsonMatch[0])
      if (parsed.overall_score !== undefined) {
        return parsed
      }
    }
  } catch {
    // 如果不是 JSON，继续文本解析
  }

  // 从文本中提取信息，构建结构化报告
  const report: any = {
    overall_score: 75, // 默认分数，实际应该从 AI 回答中提取
    dimensions: [
      {
        name: '教学目标设计',
        score: 70,
        strengths: [],
        issues: [],
        suggestions: [],
      },
      {
        name: '活动设计',
        score: 75,
        strengths: [],
        issues: [],
        suggestions: [],
      },
      {
        name: '学生参与度',
        score: 70,
        strengths: [],
        issues: [],
        suggestions: [],
      },
      {
        name: '评价设计',
        score: 65,
        strengths: [],
        issues: [],
        suggestions: [],
      },
      {
        name: '学习科学理论应用',
        score: 70,
        strengths: [],
        issues: [],
        suggestions: [],
      },
    ],
    detailed_suggestions: answer,
  }

  // 从 AI 回答中提取评分信息（简单模式匹配）
  const scoreMatch = answer.match(/(?:总体评分|总分|综合评分)[：:]\s*(\d+)/i)
  if (scoreMatch) {
    report.overall_score = parseInt(scoreMatch[1], 10)
  }

  return report
}

function copyOptimizationReport() {
  if (!optimizationReport.value) return
  
  const reportText = `教案优化分析报告

总体评分：${optimizationReport.value.overall_score} / 100

${optimizationReport.value.dimensions?.map((d: any) => `
${d.name}：${d.score} / 100
${d.strengths?.length ? `优势：${d.strengths.join('；')}` : ''}
${d.issues?.length ? `待改进：${d.issues.join('；')}` : ''}
${d.suggestions?.length ? `建议：${d.suggestions.join('；')}` : ''}
`).join('\n')}

详细方案：
${optimizationReport.value.detailed_suggestions || ''}
`

  navigator.clipboard
    .writeText(reportText)
    .then(() => {
      // 可以添加 toast 提示
      console.log('报告已复制到剪贴板')
    })
    .catch(() => {
      console.error('复制失败')
    })
}

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      question.value = ''
      errorMessage.value = null
      response.value = null
      optimizationReport.value = null
      selectedLessonId.value = null
      suggestionOffset.value = 0
      // 重新加载自定义智能体（可能在其他地方被修改）
      const loaded = loadCustomAgents()
      customAgents.value = loaded
      console.log('Modal opened. Loaded agents:', loaded.length)
    }
  }
)

// 监听创建模态框打开，重新加载数据（以防在其他标签页被修改）
watch(showCreateAgentModal, (isOpen) => {
  if (isOpen) {
    // 打开时重新加载，确保数据是最新的
    const loaded = loadCustomAgents()
    customAgents.value = loaded
    console.log('Create agent modal opened. Loaded agents:', loaded.length)
  } else {
    // 关闭时重置表单
    agentForm.value = { name: '', description: '', prompt: '' }
    editingAgent.value = null
  }
})

watch(
  () => selectedTopic.value,
  () => {
    // 切换主题时清除优化报告
    optimizationReport.value = null
    selectedLessonId.value = null
  }
)
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: scale(0.98);
}

.header-top {
  display: flex;
}
</style>

