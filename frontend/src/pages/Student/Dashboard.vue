<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 统一头部 -->
    <DashboardHeader
      title="学生工作台"
      subtitle="开始您的学习之旅"
      :user-name="userName"
      :region-name="regionName"
      :school-name="schoolName"
      :grade-name="gradeName"
      :classroom-name="classroomName"
      :show-profile-button="true"
      @profile="router.push('/student/profile')"
      @logout="handleLogout"
    />

    <!-- 主要内容区域 -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- 5E 学习活动循环横幅 -->
      <div class="mb-8 rounded-2xl bg-gradient-to-r from-[#4C6EF5] via-[#7B5CF7] to-[#E056FD] shadow-2xl overflow-hidden">
        <div class="p-8 md:p-10 text-white">
          <div class="flex flex-col gap-6">
            <div class="flex items-center gap-3">
              <span class="text-4xl">🔄</span>
              <div>
                <h2 class="text-3xl font-bold">5E 科学学习活动循环</h2>
                <p class="text-sm text-white/80 mt-1">
                  按照 5E 步骤推进课堂，逐步点亮探究、表达与反思能力。
                </p>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-5 gap-3 text-sm text-white/90">
              <div class="rounded-xl bg-white/10 px-3 py-4 flex flex-col items-center text-center">
                <span class="text-2xl mb-2">💡</span>
                <p class="font-semibold text-white">Engage</p>
                <p class="text-xs mt-1">激发问题</p>
              </div>
              <div class="rounded-xl bg-white/10 px-3 py-4 flex flex-col items-center text-center">
                <span class="text-2xl mb-2">🧪</span>
                <p class="font-semibold text-white">Explore</p>
                <p class="text-xs mt-1">动手探索</p>
              </div>
              <div class="rounded-xl bg-white/10 px-3 py-4 flex flex-col items-center text-center">
                <span class="text-2xl mb-2">🧠</span>
                <p class="font-semibold text-white">Explain</p>
                <p class="text-xs mt-1">表达理解</p>
              </div>
              <div class="rounded-xl bg-white/10 px-3 py-4 flex flex-col items-center text-center">
                <span class="text-2xl mb-2">🚀</span>
                <p class="font-semibold text-white">Elaborate</p>
                <p class="text-xs mt-1">拓展应用</p>
              </div>
              <div class="rounded-xl bg-white/10 px-3 py-4 flex flex-col items-center text-center">
                <span class="text-2xl mb-2">📊</span>
                <p class="font-semibold text-white">Evaluate</p>
                <p class="text-xs mt-1">自我检核</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 准备上课区域 -->
      <div v-if="pendingSessions.length > 0" class="mb-8 rounded-2xl bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-600 shadow-2xl overflow-hidden">
        <div class="p-6 md:p-8 text-white">
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
              <span class="text-3xl animate-pulse">⏳</span>
              <div>
                <h2 class="text-2xl font-bold">准备上课</h2>
                <p class="text-sm text-blue-100 mt-1">以下课程即将开始，请做好准备</p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm text-blue-100">待开始课堂</div>
              <div class="text-3xl font-bold">{{ pendingSessions.length }}</div>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="session in pendingSessions"
              :key="session.id"
              class="bg-white/10 backdrop-blur-sm rounded-xl p-4 hover:bg-white/20 transition-all cursor-pointer border border-white/20"
              @click="enterClassroom(session.lessonId)"
            >
              <div class="flex items-start justify-between mb-3">
                <h3 class="font-semibold text-white text-lg line-clamp-2 flex-1">{{ session.lessonTitle || '未命名课程' }}</h3>
              </div>
              <div class="space-y-2 text-sm text-blue-100">
                <div class="flex items-center gap-2">
                  <span>👨‍🏫</span>
                  <span>{{ session.teacherName || '未知教师' }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>🏫</span>
                  <span>{{ session.classroomName || '未知班级' }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>👥</span>
                  <span>{{ session.activeStudents || 0 }}/{{ session.totalStudents || 0 }} 人已加入</span>
                </div>
                <div class="flex items-center gap-2">
                  <span>⏰</span>
                  <span>{{ formatTimeAgo(session.createdAt) }}</span>
                </div>
              </div>
              <button
                class="w-full mt-4 px-4 py-2 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors flex items-center justify-center gap-2"
                @click.stop.prevent="enterClassroom(session.lessonId)"
              >
                <span>进入课堂</span>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <button
          @click="router.push('/student/favorites')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">❤️</div>
          <div class="text-sm font-medium text-gray-900">我的收藏</div>
        </button>
        <button
          @click="router.push('/student/learning-paths')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">🗺️</div>
          <div class="text-sm font-medium text-gray-900">学习路径</div>
        </button>
        <button
          @click="router.push('/student/profile')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">📊</div>
          <div class="text-sm font-medium text-gray-900">学习统计</div>
        </button>
        <button
          @click="showRecommended = !showRecommended"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow text-center"
        >
          <div class="text-3xl mb-2">⭐</div>
          <div class="text-sm font-medium text-gray-900">推荐课程</div>
        </button>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">可用课程</p>
              <p class="text-2xl font-semibold text-gray-900">{{ availableLessons.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">已完成</p>
              <p class="text-2xl font-semibold text-gray-900">{{ completedCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-500 rounded-md p-3">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">进行中</p>
              <p class="text-2xl font-semibold text-gray-900">{{ inProgressCount }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 推荐课程区域 -->
      <div v-if="showRecommended" class="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg shadow-lg p-6 mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-white flex items-center">
            <span class="mr-2">⭐</span>
            为你推荐
          </h2>
          <button @click="showRecommended = false" class="text-white hover:text-gray-200">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div v-if="loadingRecommended" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
        
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="lesson in recommendedLessons"
            :key="lesson.id"
            class="bg-white rounded-lg p-4 hover:shadow-xl transition-shadow cursor-pointer"
            @click="viewLesson(lesson.id)"
          >
            <h3 class="font-semibold text-gray-900 mb-2 line-clamp-1">{{ lesson.title }}</h3>
            <div class="flex items-center text-sm text-gray-600 mb-2">
              <span class="mr-2">⭐</span>
              <span>{{ lesson.average_rating?.toFixed(1) || '暂无评分' }}</span>
              <span class="mx-2">|</span>
              <span>{{ lesson.view_count || 0 }} 次学习</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                {{ getDifficultyText(lesson.difficulty_level) }}
              </span>
              <button class="text-blue-600 text-sm font-medium hover:text-blue-800">
                开始学习 →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 视图切换和筛选 -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-2xl font-bold text-gray-900">
            {{ viewMode === 'list' ? '课程列表' : '课程体系' }}
            <span v-if="selectedChapterName" class="text-sm font-normal text-green-600 ml-2">
              - {{ selectedChapterName }}
              <button 
                @click="clearChapterFilter"
                class="ml-1 text-xs hover:underline"
              >
                ✕ 清除
              </button>
            </span>
          </h2>
          <div class="inline-flex rounded-md shadow-sm" role="group">
            <button
              @click="viewMode = 'list'"
              :class="[
                'px-4 py-2 text-sm font-medium border transition-colors rounded-l-md',
                viewMode === 'list'
                  ? 'bg-green-600 text-white border-green-600 z-10'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
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
                'px-4 py-2 text-sm font-medium border transition-colors rounded-r-md',
                viewMode === 'tree'
                  ? 'bg-green-600 text-white border-green-600 z-10'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              ]"
              title="课程体系视图"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 高级筛选和搜索（仅列表视图显示） -->
      <div v-if="viewMode === 'list'" class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="flex flex-col gap-4">
          <!-- 第一行：搜索和基础筛选 -->
          <div class="flex flex-col md:flex-row gap-4">
            <div class="flex-1">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索课程名称..."
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <select
              v-model="filterStatus"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部状态</option>
              <option value="not_started">未开始</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
            </select>
            <select
              v-model="filterSubject"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部学科</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }}
              </option>
            </select>
          </div>
          
          <!-- 第二行：高级筛选 -->
          <div class="flex flex-col md:flex-row gap-4">
            <select
              v-model="filterDifficulty"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部难度</option>
              <option value="beginner">基础</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
            </select>
            <select
              v-model="filterRating"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">全部评分</option>
              <option value="4">4星以上</option>
              <option value="3">3星以上</option>
              <option value="2">2星以上</option>
            </select>
            <select
              v-model="sortBy"
              class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="default">默认排序</option>
              <option value="rating">评分最高</option>
              <option value="popular">最受欢迎</option>
              <option value="newest">最新发布</option>
            </select>
            <button
              @click="resetFilters"
              class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700"
            >
              重置筛选
            </button>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'">
        <!-- 课程列表 -->
        <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <p class="mt-4 text-gray-600">加载中...</p>
      </div>

        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p class="text-red-600">{{ error }}</p>
        <button
          @click="fetchData"
          class="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
        >
          重试
          </button>
        </div>

        <div v-else-if="filteredLessons.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
          <p class="mt-4 text-lg text-gray-600">暂无课程</p>
          <p class="mt-2 text-sm text-gray-500">请等待老师发布课程或调整筛选条件</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="lesson in filteredLessons"
          :key="lesson.id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition-shadow relative group"
        >
          <!-- 收藏按钮 -->
          <button
            @click.stop="toggleFavorite(lesson.id)"
            class="absolute top-4 right-4 z-10 p-2 bg-white rounded-full shadow-md hover:bg-red-50 transition-colors"
            :class="{ 'text-red-500': isFavorited(lesson.id), 'text-gray-400': !isFavorited(lesson.id) }"
          >
            <svg class="w-5 h-5" :fill="isFavorited(lesson.id) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
          </button>

          <!-- 课程封面 -->
          <div 
            class="h-40 bg-gradient-to-br from-blue-500 to-purple-600 rounded-t-lg flex items-center justify-center cursor-pointer"
            @click="viewLesson(lesson.id)"
          >
            <svg class="w-16 h-16 text-white opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>

          <!-- 课程信息 -->
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
              {{ lesson.title }}
            </h3>
            <p v-if="lesson.description" class="text-sm text-gray-600 mb-4 line-clamp-2">
              {{ lesson.description }}
            </p>

            <!-- 难度和评分 -->
            <div class="flex items-center gap-2 mb-3">
              <span v-if="lesson.difficulty_level" class="text-xs px-2 py-1 rounded" :class="getDifficultyClass(lesson.difficulty_level)">
                {{ getDifficultyText(lesson.difficulty_level) }}
              </span>
              <div class="flex items-center text-yellow-500">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span class="ml-1 text-sm text-gray-700">
                  {{ lesson.average_rating?.toFixed(1) || '0.0' }}
                </span>
                <span class="ml-1 text-xs text-gray-500">
                  ({{ lesson.review_count || 0 }})
                </span>
              </div>
            </div>

            <!-- 课程元信息 -->
            <div class="space-y-2 mb-4">
              <!-- 教师信息 -->
              <div v-if="lesson.creator_name" class="flex items-center text-xs text-gray-600">
                <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="font-medium text-gray-700">{{ lesson.creator_name }} 老师</span>
              </div>
              <div v-if="lesson.course" class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                </svg>
                {{ lesson.course.name }}
              </div>
              <div v-if="lesson.chapter" class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ lesson.chapter.name }}
              </div>
              <div class="flex items-center text-xs text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ lesson.estimated_duration || 45 }} 分钟
              </div>
            </div>

            <!-- 学习进度 -->
            <div class="mb-4">
              <div class="flex items-center justify-between text-xs text-gray-600 mb-1">
                <span>学习进度</span>
                <span>{{ getLessonProgress(lesson.id) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-500 h-2 rounded-full transition-all"
                  :style="{ width: `${getLessonProgress(lesson.id)}%` }"
                ></div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <button
              class="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              @click="viewLesson(lesson.id)"
            >
              {{ getLessonProgress(lesson.id) === 0 ? '开始学习' : '继续学习' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程体系视图 -->
      <div v-else-if="viewMode === 'tree'">
        <CurriculumTreeViewStudent
          @view-lessons="handleViewChapterLessons"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { lessonService } from '@/services/lesson'
import { curriculumService } from '@/services/curriculum'
import { favoriteService } from '@/services/favorite'
import classroomSessionService from '@/services/classroomSession'
import type { Lesson } from '@/types/lesson'
import type { Subject } from '@/types/curriculum'
import type { StudentPendingSession } from '@/types/classroomSession'
import DashboardHeader from '@/components/Common/DashboardHeader.vue'
import CurriculumTreeViewStudent from '@/components/Student/CurriculumTreeViewStudent.vue'

const router = useRouter()
const userStore = useUserStore()

// 状态
const loading = ref(false)
const error = ref<string | null>(null)
const availableLessons = ref<Lesson[]>([])
const subjects = ref<Subject[]>([])
const searchQuery = ref('')
const filterStatus = ref('')
const filterSubject = ref('')
const filterDifficulty = ref('')
const filterRating = ref('')
const sortBy = ref('default')
const showRecommended = ref(true)
const loadingRecommended = ref(false)
const recommendedLessons = ref<Lesson[]>([])
const favoritedLessonIds = ref<Set<number>>(new Set())
const viewMode = ref<'list' | 'tree'>('list') // 视图模式
const selectedChapterId = ref<number | null>(null) // 选中的章节ID
const selectedChapterName = ref<string>('') // 选中的章节名称

// 学习进度数据（从localStorage获取）
const progressData = ref<Record<number, number>>({})

// 准备上课相关状态
const pendingSessions = ref<StudentPendingSession[]>([])
const loadingPendingSessions = ref(false)
let pendingSessionsPollingInterval: ReturnType<typeof setInterval> | null = null
const PENDING_SESSIONS_POLLING_INTERVAL = 5000 // 5秒轮询一次

// 计算属性
const currentUser = computed(() => userStore.user)
const userName = computed(() => userStore.user?.full_name || userStore.user?.username || '学生')
const regionName = computed(() => userStore.user?.region_name || null)
const schoolName = computed(() => userStore.user?.school_name || null)
const gradeName = computed(() => userStore.user?.grade_name || null)
const classroomName = computed(() => userStore.user?.classroom_name || null)

const filteredLessons = computed(() => {
  let result = [...availableLessons.value]

  // 按章节过滤（优先级最高）
  if (selectedChapterId.value) {
    result = result.filter(lesson => lesson.chapter_id === selectedChapterId.value)
  }

  // 按搜索词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(lesson =>
      lesson.title.toLowerCase().includes(query) ||
      lesson.description?.toLowerCase().includes(query)
    )
  }

  // 按学科过滤
  if (filterSubject.value) {
    result = result.filter(lesson => lesson.course?.subject_id === Number(filterSubject.value))
  }

  // 按难度过滤
  if (filterDifficulty.value) {
    result = result.filter(lesson => lesson.difficulty_level === filterDifficulty.value)
  }

  // 按评分过滤
  if (filterRating.value) {
    const minRating = Number(filterRating.value)
    result = result.filter(lesson => (lesson.average_rating || 0) >= minRating)
  }

  // 按状态过滤
  if (filterStatus.value) {
    result = result.filter(lesson => {
      const progress = getLessonProgress(lesson.id)
      if (filterStatus.value === 'not_started') return progress === 0
      if (filterStatus.value === 'in_progress') return progress > 0 && progress < 100
      if (filterStatus.value === 'completed') return progress === 100
      return true
    })
  }

  // 排序
  if (sortBy.value === 'rating') {
    result.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0))
  } else if (sortBy.value === 'popular') {
    result.sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
  } else if (sortBy.value === 'newest') {
    result.sort((a, b) => new Date(b.published_at || b.created_at).getTime() - new Date(a.published_at || a.created_at).getTime())
  }

  return result
})

const completedCount = computed(() => {
  return availableLessons.value.filter(lesson => getLessonProgress(lesson.id) === 100).length
})

const inProgressCount = computed(() => {
  return availableLessons.value.filter(lesson => {
    const progress = getLessonProgress(lesson.id)
    return progress > 0 && progress < 100
  }).length
})

// 方法
const getLessonProgress = (lessonId: number): number => {
  return progressData.value[lessonId] || 0
}

const loadProgressData = () => {
  const saved = localStorage.getItem('student_lesson_progress')
  if (saved) {
    try {
      progressData.value = JSON.parse(saved)
    } catch (e) {
      console.error('Failed to load progress data:', e)
    }
  }
}

const fetchData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // 获取已发布的课程列表
    const response = await lessonService.fetchLessons({
      status: 'published',
      page: 1,
      page_size: 100
    })
    availableLessons.value = response.items

    // 获取学科列表
    subjects.value = await curriculumService.getSubjects()
    
    // 加载学习进度
    loadProgressData()
    
    // 加载收藏列表
    await loadFavorites()
    
    // 加载推荐课程
    await loadRecommendedLessons()
    
    // 加载待开始课堂
    await loadPendingSessions()
  } catch (e: any) {
    error.value = e.message || '加载数据失败'
    console.error('Failed to fetch data:', e)
  } finally {
    loading.value = false
  }
}

const loadRecommendedLessons = async () => {
  loadingRecommended.value = true
  try {
    const response = await lessonService.fetchRecommendedLessons(6)
    recommendedLessons.value = response.items
  } catch (e) {
    console.error('Failed to load recommended lessons:', e)
  } finally {
    loadingRecommended.value = false
  }
}

const loadFavorites = async () => {
  try {
    const favorites = await favoriteService.getMyFavorites()
    favoritedLessonIds.value = new Set(favorites.map(f => f.lesson_id))
  } catch (e) {
    console.error('Failed to load favorites:', e)
  }
}

const isFavorited = (lessonId: number): boolean => {
  return favoritedLessonIds.value.has(lessonId)
}

const toggleFavorite = async (lessonId: number) => {
  try {
    const isFav = await favoriteService.toggleFavorite(lessonId)
    if (isFav) {
      favoritedLessonIds.value.add(lessonId)
    } else {
      favoritedLessonIds.value.delete(lessonId)
    }
  } catch (e: any) {
    alert(e.message || '操作失败')
  }
}

const getDifficultyText = (level: string | undefined): string => {
  const map: Record<string, string> = {
    'beginner': '基础',
    'intermediate': '中级',
    'advanced': '高级'
  }
  return map[level || ''] || '基础'
}

const getDifficultyClass = (level: string | undefined): string => {
  const map: Record<string, string> = {
    'beginner': 'bg-green-100 text-green-700',
    'intermediate': 'bg-yellow-100 text-yellow-700',
    'advanced': 'bg-red-100 text-red-700'
  }
  return map[level || ''] || 'bg-gray-100 text-gray-700'
}

const resetFilters = () => {
  searchQuery.value = ''
  filterStatus.value = ''
  filterSubject.value = ''
  filterDifficulty.value = ''
  filterRating.value = ''
  sortBy.value = 'default'
}

const viewLesson = (lessonId: number) => {
  router.push(`/student/lesson/${lessonId}`)
}

// 加载待开始课堂列表
const loadPendingSessions = async () => {
  // 只允许学生访问
  if (currentUser.value?.role !== 'student') {
    return
  }
  
  loadingPendingSessions.value = true
  try {
    const sessions = await classroomSessionService.getStudentPendingSessions()
    pendingSessions.value = sessions
    console.log('📋 Loaded pending sessions:', sessions.length)
  } catch (e: any) {
    console.error('Failed to load pending sessions:', e)
    // 如果是权限错误或其他错误,不显示错误提示
    if (e.response?.status !== 403) {
      console.warn('⚠️ Could not load pending sessions:', e.message)
    }
  } finally {
    loadingPendingSessions.value = false
  }
}

// 格式化时间（显示多久前）
const formatTimeAgo = (dateString: string): string => {
  if (!dateString) {
    return '未知时间'
  }
  
  // 处理后端返回的UTC时间字符串（可能没有时区信息）
  let utcString = dateString.trim()
  
  // 检查是否已有时区信息（Z或+/-时区偏移）
  const hasTimezone = utcString.endsWith('Z') || /[+-]\d{2}:?\d{2}$/.test(utcString)
  
  if (!hasTimezone) {
    // 如果没有时区信息，假设它是UTC时间并添加Z后缀
    // 处理格式：YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS
    if (utcString.includes(' ')) {
      // 空格格式转换为ISO格式
      utcString = utcString.replace(' ', 'T') + 'Z'
    } else if (utcString.includes('T')) {
      // 已经是ISO格式，只需添加Z
      utcString = utcString + 'Z'
    } else {
      // 其他格式，尝试解析后再处理
      utcString = utcString + 'Z'
    }
  }
  
  // 解析为UTC时间
  let date: Date
  try {
    date = new Date(utcString)
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString, '->', utcString)
      return '未知时间'
    }
  } catch (e) {
    console.error('Error parsing date:', dateString, e)
    return '未知时间'
  }
  
  const now = new Date()
  
  // 计算时间差（毫秒）
  const diffMs = now.getTime() - date.getTime()
  
  // 如果时间差为负（未来时间），可能解析有误，返回"刚刚"
  if (diffMs < 0) {
    // 检查是否是因为时区问题导致的时间差异（小于24小时，可能是时区问题）
    if (Math.abs(diffMs) < 24 * 60 * 60 * 1000) {
      return '刚刚'
    }
    // 否则返回"未知时间"
    return '未知时间'
  }
  
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) {
    return '刚刚'
  } else if (diffMins < 60) {
    return `${diffMins}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    // 显示具体日期（转换为本地时间显示）
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

// 进入课堂
const enterClassroom = (lessonId: number) => {
  // 跳转到课程页面，会自动加入会话
  router.push(`/student/lesson/${lessonId}`)
}

// 开始轮询待开始课堂列表
const startPendingSessionsPolling = () => {
  // 只允许学生轮询
  if (currentUser.value?.role !== 'student') {
    return
  }
  
  // 如果已经有轮询,先清除
  if (pendingSessionsPollingInterval) {
    clearInterval(pendingSessionsPollingInterval)
  }
  
  // 立即加载一次
  loadPendingSessions()
  
  // 设置定时轮询
  pendingSessionsPollingInterval = setInterval(() => {
    loadPendingSessions()
  }, PENDING_SESSIONS_POLLING_INTERVAL)
}

// 停止轮询
const stopPendingSessionsPolling = () => {
  if (pendingSessionsPollingInterval) {
    clearInterval(pendingSessionsPollingInterval)
    pendingSessionsPollingInterval = null
  }
}

// 查看章节的课程列表
async function handleViewChapterLessons(chapterId: number) {
  // 切换到列表视图并筛选指定章节的课程
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
  
  // 重新筛选课程列表
  fetchData()
}

// 清除章节筛选
function clearChapterFilter() {
  selectedChapterId.value = null
  selectedChapterName.value = ''
  fetchData()
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

// 生命周期
onMounted(() => {
  fetchData()
  // 开始轮询待开始课堂列表
  startPendingSessionsPolling()
})

onUnmounted(() => {
  // 停止轮询
  stopPendingSessionsPolling()
})
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
