<template>
  <div class="teacher-control-panel" :class="{ 'panel-fullscreen': isPanelFullscreen }">
    <!-- 🎯 优化后的顶部控制栏（固定，始终可见） -->
    <div class="top-control-bar">
      <!-- 第一行：标题和操作按钮 -->
      <div class="top-control-row">
        <div class="top-control-left">
          <h2 class="panel-title">InspireEd 教师导播台</h2>
          <div v-if="lesson" class="lesson-info">
            <span class="lesson-title">{{ lesson.title }}</span>
          </div>
        </div>
        <div class="header-controls">
          <!-- 导播台全屏按钮 -->
          <button 
            @click="togglePanelFullscreen"
            class="btn btn-fullscreen"
            :title="isPanelFullscreen ? '退出全屏' : '全屏显示导播台'"
          >
            <svg v-if="!isPanelFullscreen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
            <span class="ml-1">{{ isPanelFullscreen ? '退出全屏' : '全屏' }}</span>
          </button>
        <!-- 没有会话时，显示"创建课堂"按钮 -->
        <button 
          v-if="!session"
          @click="handleCreateSession"
          :disabled="loading"
          class="btn btn-primary"
        >
          📚 创建课堂
        </button>
        
        <!-- PENDING 状态：等待学生登录 -->
        <template v-if="session && session.status === 'pending'">
          <button 
            @click="handleBeginClass"
            :disabled="loading || activeStudents.length === 0"
            class="btn btn-primary"
            :title="activeStudents.length === 0 ? '请等待学生加入课堂' : '开始上课'"
          >
            ▶️ 开始上课
          </button>
          <button 
            @click="handleCancelSession"
            :disabled="loading"
            class="btn btn-secondary"
          >
            ❌ 取消
          </button>
        </template>
        
        <!-- ACTIVE 状态：上课中 -->
        <template v-if="session && session.status === 'active'">
          <!-- 显示模式切换按钮 -->
          <div class="display-mode-controls">
            <button 
              @click="handleToggleDisplayMode"
              :disabled="loading"
              class="btn btn-display-mode"
              :class="{ 'active': currentDisplayMode === 'fullscreen' }"
              :title="currentDisplayMode === 'fullscreen' ? '当前：全屏模式' : '当前：窗口模式'"
            >
              <svg v-if="currentDisplayMode === 'window'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
              <span class="ml-1">{{ currentDisplayMode === 'fullscreen' ? '全屏' : '窗口' }}</span>
            </button>
          </div>
          <button 
            @click="handlePause"
            :disabled="loading"
            class="btn btn-secondary"
          >
            ⏸️ 暂停
          </button>
          <button 
            @click="handleEnd"
            :disabled="loading"
            class="btn btn-danger"
          >
            ⏹️ 结束
          </button>
        </template>
        
        <!-- PAUSED 状态：已暂停 -->
        <template v-if="session && session.status === 'paused'">
          <!-- 显示模式切换按钮 -->
          <div class="display-mode-controls">
            <button 
              @click="handleToggleDisplayMode"
              :disabled="loading"
              class="btn btn-display-mode"
              :class="{ 'active': currentDisplayMode === 'fullscreen' }"
              :title="currentDisplayMode === 'fullscreen' ? '当前：全屏模式' : '当前：窗口模式'"
            >
              <svg v-if="currentDisplayMode === 'window'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
              </svg>
              <span class="ml-1">{{ currentDisplayMode === 'fullscreen' ? '全屏' : '窗口' }}</span>
            </button>
          </div>
          <button 
            @click="handleResume"
            :disabled="loading"
            class="btn btn-primary"
          >
            ▶️ 继续
          </button>
          <button 
            @click="handleEnd"
            :disabled="loading"
            class="btn btn-danger"
          >
            ⏹️ 结束
          </button>
        </template>
        </div>
      </div>
      
      <!-- 第二行：关键指标（上课中时显示） - 首页风格卡片 -->
      <div v-if="session && session.status !== 'pending'" class="top-control-metrics">
        <!-- 课程时长卡片 -->
        <div 
          class="metric-card metric-card-time group"
          :class="{ 
            'metric-warning': remainingTime < 600, 
            'metric-danger': remainingTime < 300 
          }"
        >
          <span class="metric-accent-bar bg-gradient-to-r from-blue-500 to-cyan-500"></span>
          <div class="metric-card-content">
            <div class="metric-card-header">
              <div class="metric-header-text">
                <p class="metric-card-label">已用时</p>
                <h3 class="metric-card-title">课程时长</h3>
              </div>
              <div class="metric-icon-wrapper bg-gradient-to-br from-blue-100 to-cyan-100">
                <span class="metric-icon-text">⏱️</span>
              </div>
            </div>
            <div class="metric-card-value-group">
              <span class="metric-card-value" :class="{
                'text-blue-600': remainingTime >= 600,
                'text-orange-600': remainingTime < 600 && remainingTime >= 300,
                'text-red-600 animate-pulse': remainingTime < 300
              }">
                {{ formatDuration(displayDuration) }}
              </span>
            </div>
            <p class="metric-card-description" v-if="session.status === 'active'">
              剩余: {{ formatRemainingTime(remainingTime) }}
            </p>
          </div>
        </div>
        
        <!-- 在线学生数卡片 -->
        <div class="metric-card metric-card-student group">
          <span class="metric-accent-bar bg-gradient-to-r from-emerald-500 to-teal-500"></span>
          <div class="metric-card-content">
            <div class="metric-card-header">
              <div class="metric-header-text">
                <p class="metric-card-label">在线学生</p>
                <h3 class="metric-card-title">学生状态</h3>
              </div>
              <div class="metric-icon-wrapper bg-gradient-to-br from-emerald-100 to-teal-100">
                <span class="metric-icon-text">👥</span>
              </div>
            </div>
            <div class="metric-card-value-group">
              <span class="metric-card-value text-emerald-600">
                {{ activeStudents.length }}/{{ totalStudents }}
              </span>
            </div>
            <p class="metric-card-description">
              在线率: {{ totalStudents > 0 ? Math.round((activeStudents.length / totalStudents) * 100) : 0 }}%
            </p>
          </div>
        </div>
        
        <!-- 平均进度卡片 -->
        <div class="metric-card metric-card-progress group">
          <span class="metric-accent-bar bg-gradient-to-r from-purple-500 to-pink-500"></span>
          <div class="metric-card-content">
            <div class="metric-card-header">
              <div class="metric-header-text">
                <p class="metric-card-label">平均进度</p>
                <h3 class="metric-card-title">学习进度</h3>
              </div>
              <div class="metric-icon-wrapper bg-gradient-to-br from-purple-100 to-pink-100">
                <span class="metric-icon-text">📊</span>
              </div>
            </div>
            <div class="metric-card-value-group">
              <span class="metric-card-value text-purple-600">
                {{ Math.round(sessionStatistics?.average_progress || 0) }}%
              </span>
            </div>
            <p class="metric-card-description">
              参与度: {{ participationRate }}%
            </p>
          </div>
        </div>
        
        <!-- 当前模块卡片 -->
        <div class="metric-card metric-card-module group">
          <span class="metric-accent-bar bg-gradient-to-r from-amber-500 to-orange-500"></span>
          <div class="metric-card-content">
            <div class="metric-card-header">
              <div class="metric-header-text">
                <p class="metric-card-label">当前模块</p>
                <h3 class="metric-card-title">教学内容</h3>
              </div>
              <div class="metric-icon-wrapper bg-gradient-to-br from-amber-100 to-orange-100">
                <span class="metric-icon-text">🎯</span>
              </div>
            </div>
            <div class="metric-card-value-group">
              <span class="metric-card-value-small text-amber-600">
                {{ currentCell?.title || getCellTypeLabel(currentCell?.type) || '未选择' }}
              </span>
            </div>
            <p class="metric-card-description" v-if="lesson && lesson.content">
              模块 {{ getCurrentModuleIndex() + 1 }}/{{ lesson.content.length }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 主布局：左侧模块列表，右侧预览和监控 -->
    <div class="main-layout" :class="{ 'module-fullscreen-mode': modulePanelFullscreen }">
      <!-- 左侧：教学模块 -->
      <div class="panel teaching-modules" :class="{ 'module-panel-fullscreen': modulePanelFullscreen }">
        <div class="module-panel-header">
          <div class="module-header-left">
            <h3 class="panel-title">教学模块</h3>
            <div class="module-count" v-if="lesson && lesson.content">
              共 {{ lesson.content.length }} 个模块
            </div>
          </div>
          <div class="module-header-actions">
            <button 
              @click="toggleModulePanelFullscreen"
              class="module-action-btn"
              :title="modulePanelFullscreen ? '退出全屏' : '全屏显示模块'"
            >
              <svg v-if="modulePanelFullscreen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          </div>
        </div>
        <div class="module-list" v-if="lesson && lesson.content && lesson.content.length > 0">
          <!-- 隐藏所有内容选项 -->
          <div 
            class="module-item module-item-hidden"
            :class="{ 'module-item-active': !session?.current_cell_id || session.current_cell_id === 0 }"
            @click="handleHideAll"
            :title="'隐藏所有内容'"
          >
            <div class="module-item-icon">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
            </div>
            <div class="module-item-label">隐藏</div>
          </div>
          
          <!-- 课程模块列表 -->
          <div 
            v-for="(cell, index) in lesson.content" 
            :key="cell.id || index"
            class="module-item"
            :class="{
              'module-item-active': isModuleActive(cell, index),
              [`module-item-type-${cell.type}`]: true,
              'module-item-disabled': loading,
            }"
            :title="loading ? '切换中，请稍候...' : getModuleTooltip(cell, index)"
          >
            <!-- 复选框 -->
            <div class="module-item-checkbox" @click.stop="!loading && handleModuleCheckboxClick(cell, index, $event)">
              <input 
                type="checkbox" 
                :checked="isModuleActive(cell, index)"
                :disabled="loading"
                @change.stop="!loading && handleModuleCheckboxChange(cell, index, $event)"
                @click.stop
                class="checkbox-input"
              />
            </div>
            
            <!-- 模块序号 -->
            <div class="module-item-number">{{ index + 1 }}</div>
            
            <!-- 模块图标 -->
            <div class="module-item-icon" :class="`icon-${cell.type}`" @click="!loading && handleModuleItemClick(cell, index)">
              <CellTypeIcon :type="cell.type" />
            </div>
            
            <!-- 模块信息 -->
            <div class="module-item-content" @click="!loading && handleModuleItemClick(cell, index)">
              <div class="module-item-title">{{ cell.title || getCellTypeLabel(cell.type) || `模块 ${index + 1}` }}</div>
              <div class="module-item-subtitle">{{ getCellTypeLabel(cell.type) }}</div>
            </div>
            
            <!-- 活动状态标记 -->
            <div v-if="cell.type === 'activity' && isModuleActivityActive(cell, index)" class="module-item-activity-badge">
              🎯
            </div>
          </div>
        </div>
        <div v-else class="module-empty">
          <p>暂无课程模块</p>
        </div>
      </div>

      <!-- 右侧：学生视图预览 -->
      <div v-if="session && session.status !== 'pending' && displayCellOrders.length > 0" class="panel student-preview-panel">
        <h3 class="panel-title">👁️ 学生视图</h3>
        <div class="preview-content-compact">
          <div 
            v-for="(order, index) in displayCellOrders.slice(0, 3)" 
            :key="`preview-${order}-${index}`"
            class="preview-item-compact"
          >
            <div class="preview-item-header-compact">
              <span class="preview-item-number">#{{ order + 1 }}</span>
              <span class="preview-item-type-compact">{{ getCellTypeLabel(getCellByOrder(order)?.type || '') }}</span>
            </div>
            <div class="preview-item-title-compact">
              {{ getCellByOrder(order) ? (getCellByOrder(order)!.title || getCellTypeLabel(getCellByOrder(order)!.type)) : `模块 ${order + 1}` }}
            </div>
            <div class="preview-item-body-compact">
              <!-- 文本模块预览 -->
              <div v-if="getCellByOrder(order)?.type === 'text'" class="preview-text-compact">
                <div class="preview-text-snippet" v-html="getTextPreview(getCellByOrder(order)!, 60)"></div>
              </div>
              
              <!-- 视频模块预览 -->
              <div v-else-if="getCellByOrder(order)?.type === 'video'" class="preview-video-compact">
                <svg class="preview-icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span class="preview-icon-label">{{ (getCellByOrder(order) as any)?.content?.title || '视频' }}</span>
              </div>
              
              <!-- 代码模块预览 -->
              <div v-else-if="getCellByOrder(order)?.type === 'code'" class="preview-code-compact">
                <svg class="preview-icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span class="preview-icon-label">代码内容</span>
              </div>
              
              <!-- 活动模块预览 -->
              <div v-else-if="getCellByOrder(order)?.type === 'activity'" class="preview-activity-compact">
                <svg class="preview-icon-small" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <span class="preview-icon-label">{{ (getCellByOrder(order) as any)?.content?.title || '活动' }}</span>
              </div>
              
              <!-- 默认预览 -->
              <div v-else class="preview-default-compact">
                <div class="preview-icon-wrapper-small">
                  <CellTypeIcon :type="getCellByOrder(order)?.type || 'text'" />
                </div>
                <span class="preview-icon-label">{{ getCellTypeLabel(getCellByOrder(order)?.type || '') }}</span>
              </div>
            </div>
          </div>
          
          <!-- 如果超过3个模块，显示更多提示 -->
          <div v-if="displayCellOrders.length > 3" class="preview-item-compact preview-more-compact">
            <div class="preview-more-content-compact">
              <span class="preview-more-icon">+{{ displayCellOrders.length - 3 }}</span>
              <span class="preview-more-text-compact">更多模块</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 监控模块：合并课堂监控和实时数据 -->
      <div class="panel monitoring-module">
        <h3 class="panel-title">📊 课堂监控</h3>
        <div class="monitoring-module-content">
          <!-- 上半部分：学生监控 -->
          <div class="monitoring-students-section">
            <!-- 学生状态指示器网格 -->
            <div class="student-indicators">
              <div 
                v-for="(student, index) in displayStudents" 
                :key="student.id || index"
                class="indicator-item"
                :class="{ 'student-behind': (student.progressPercentage || student.progress_percentage || 0) < 50 }"
              >
                <div 
                  class="indicator-circle"
                  :class="getStudentStatusClass(student)"
                  :title="getStudentTooltip(student)"
                ></div>
                <div class="indicator-student-info">
                  <div class="indicator-student-name">{{ student.studentName || student.student_name || `学生 ${index + 1}` }}</div>
                  <div class="indicator-student-account">{{ getStudentAccount(student) }}</div>
                  <div class="indicator-student-progress">
                    <div class="indicator-progress-bar">
                      <div 
                        class="indicator-progress-fill" 
                        :style="{ width: `${Math.round(student.progressPercentage || student.progress_percentage || 0)}%` }"
                        :class="getStudentStatusClass(student)"
                      ></div>
                    </div>
                    <span class="indicator-progress-text">{{ Math.round(student.progressPercentage || student.progress_percentage || 0) }}%</span>
                  </div>
                </div>
              </div>
              <div 
                v-for="n in Math.max(0, 8 - displayStudents.length)"
                :key="`empty-${n}`"
                class="indicator-item"
              >
                <div class="indicator-circle indicator-empty"></div>
                <div class="indicator-student-info">
                  <div class="indicator-student-name indicator-empty-text">--</div>
                  <div class="indicator-student-account indicator-empty-text">--</div>
                </div>
              </div>
            </div>
            
            <!-- 进度落后学生区域（预警） -->
            <div v-if="studentsBehindCount > 0" class="students-behind-section">
              <div class="student-list-header">
                <span class="student-list-title">⚠️ 进度落后学生 ({{ studentsBehindCount }})</span>
              </div>
              <div class="student-list-content">
                <div 
                  v-for="(student, index) in activeStudents.filter(s => {
                    const progress = s.progressPercentage || s.progress_percentage || 0
                    return progress < 50
                  })" 
                  :key="student.id || `behind-${index}`"
                  class="student-list-item student-behind"
                  :class="getStudentStatusClass(student)"
                >
                  <div class="student-list-indicator"></div>
                  <div class="student-list-info">
                    <div class="student-list-name">{{ student.studentName || student.student_name || `学生 ${index + 1}` }}</div>
                    <div class="student-list-account">
                      {{ getStudentAccount(student) }}
                    </div>
                  </div>
                  <div class="student-progress-bar-container">
                    <div class="student-progress-bar">
                      <div 
                        class="student-progress-fill" 
                        :style="{ width: `${Math.round(student.progressPercentage || student.progress_percentage || 0)}%` }"
                        :class="getStudentStatusClass(student)"
                      ></div>
                    </div>
                    <div class="student-list-progress">
                      {{ Math.round(student.progressPercentage || student.progress_percentage || 0) }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 如果学生超过8个，显示更多学生列表 -->
            <div v-if="activeStudents.length > 8" class="student-list-extra">
              <div class="student-list-header">
                <span class="student-list-title">更多学生 ({{ activeStudents.length - 8 }})</span>
              </div>
              <div class="student-list-content">
                <div 
                  v-for="(student, index) in activeStudents.slice(8)" 
                  :key="student.id || `extra-${index}`"
                  class="student-list-item"
                  :class="getStudentStatusClass(student)"
                >
                  <div class="student-list-indicator"></div>
                  <div class="student-list-info">
                    <div class="student-list-name">{{ student.studentName || student.student_name || `学生 ${index + 9}` }}</div>
                    <div class="student-list-account">
                      {{ getStudentAccount(student) }}
                    </div>
                  </div>
                  <div class="student-progress-bar-container">
                    <div class="student-progress-bar">
                      <div 
                        class="student-progress-fill" 
                        :style="{ width: `${Math.round(student.progressPercentage || student.progress_percentage || 0)}%` }"
                        :class="getStudentStatusClass(student)"
                      ></div>
                    </div>
                    <div class="student-list-progress">
                      {{ Math.round(student.progressPercentage || student.progress_percentage || 0) }}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else-if="activeStudents.length === 0" class="student-list-empty">
              <p>暂无学生在线</p>
            </div>
          </div>
          
          <!-- 分隔线 -->
          <div class="monitoring-divider"></div>
          
          <!-- 下半部分：实时数据统计 -->
          <div class="monitoring-stats-section">
            <h4 class="stats-section-title">实时数据</h4>
            <div class="stats-grid-compact">
              <div class="stat-card-compact">
                <div class="stat-icon-compact">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div class="stat-content-compact">
                  <div class="stat-label-compact">互动次数</div>
                  <div class="stat-value-compact">{{ interactionCount }}次</div>
                </div>
              </div>
              
              <div class="stat-card-compact">
                <div class="stat-icon-compact stat-icon-red">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="stat-content-compact">
                  <div class="stat-label-compact">提问数量</div>
                  <div class="stat-value-compact">{{ questionCount }}个</div>
                </div>
              </div>
              
              <div class="stat-card-compact">
                <div class="stat-icon-compact stat-icon-green">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="stat-content-compact">
                  <div class="stat-label-compact">正确率</div>
                  <div class="stat-value-compact">{{ accuracyRate }}%</div>
                </div>
              </div>
              
              <div class="stat-card-compact">
                <div class="stat-icon-compact stat-icon-blue">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="stat-content-compact">
                  <div class="stat-label-compact">参与度</div>
                  <div class="stat-value-compact">{{ participationRate }}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 活动统计面板（当前 Cell 是 activity 类型时显示，放在三栏布局下方） -->
    <div v-if="session && currentCell && currentCell.type === 'activity' && currentActivityDbCell" class="activity-panel">
      <SubmissionStatistics
        :cell-id="currentActivityDbCell.id"
        :lesson-id="lesson?.id || lessonId"
        :session-id="session.id"
      />
      
      <!-- 学生提交详细列表 -->
      <div class="mt-4">
        <SubmissionList
          :cell-id="currentActivityDbCell.id"
          :activity="currentCell.content"
          :session-id="session.id"
          :lesson-id="lesson?.id || lessonId"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, h } from 'vue'
import { useRoute } from 'vue-router'
import type { Lesson } from '../../types/lesson'
import type { Cell, ActivityCell } from '../../types/cell'
import classroomSessionService from '../../services/classroomSession'
import ClassroomSwitcher from './ClassroomSwitcher.vue'
import ClassroomControlBoard from './ClassroomControlBoard.vue'
import SubmissionStatistics from '../Activity/SubmissionStatistics.vue'
import SubmissionList from '../Activity/Teacher/SubmissionList.vue'
import { getCellId as getCellIdUtil, buildNavigateRequest, toNumericId, isUUID } from '../../utils/cellId'

// Cell类型图标组件
const CellTypeIcon = (props: { type: string }) => {
  const icons: Record<string, any> = {
    text: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 6h16M4 12h16M4 18h16' })
    ]),
    code: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4' })
    ]),
    activity: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
    ]),
    video: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' })
    ]),
    flowchart: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7' })
    ]),
    qa: () => h('svg', { class: 'w-5 h-5', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' })
    ]),
  }
  
  const IconComponent = icons[props.type] || icons.text
  return IconComponent()
}

interface Props {
  lessonId: number
  lesson?: Lesson
}

const props = defineProps<Props>()

const route = useRoute()
const session = ref<any>(null)
const loading = ref(false)
const activeStudents = ref<any[]>([])
const loadingStudents = ref(false)
const sessionStatistics = ref<any>(null)
const selectedCellIndex = ref(-1)  // -1表示隐藏所有内容
const sessionDuration = ref(0)
const durationInterval = ref<number | null>(null)
const dbCells = ref<Array<{ id: number; order: number; cell_type: string }>>([])  // 数据库中的 Cell 记录（用于 ID 匹配）
const modulePanelFullscreen = ref(false)  // 模块面板全屏状态
const isPanelFullscreen = ref(false)  // 整个导播台全屏状态

// 一节课的标准时长（40分钟 = 2400秒）
const LESSON_DURATION = 40 * 60

// 显示的课程时长（只有在 active 状态才显示实际时长）
const displayDuration = computed(() => {
  // 如果会话不存在或不是 active 状态，显示 0
  if (!session.value || session.value.status !== 'active') {
    return 0
  }
  return sessionDuration.value || 0
})

// 计算剩余时间
const remainingTime = computed(() => {
  if (sessionDuration.value === null || sessionDuration.value === undefined) return LESSON_DURATION
  const remaining = LESSON_DURATION - sessionDuration.value
  return remaining > 0 ? remaining : 0
})

// 计算属性
const statusTitle = computed(() => {
  if (!session.value) return '未创建会话'
  const statusMap: Record<string, string> = {
    pending: '准备中',
    active: '上课中',
    paused: '已暂停',
    ended: '已结束',
  }
  return statusMap[session.value.status] || '未知状态'
})

const statusClass = computed(() => {
  if (!session.value) return 'status-pending'
  return `status-${session.value.status}`
})

const totalStudents = computed(() => {
  return session.value?.total_students || 0
})

// 显示的学生列表（最多8个用于指示器）
const displayStudents = computed(() => {
  return activeStudents.value.slice(0, 8)
})

// 学生状态类
function getStudentStatusClass(student: any): string {
  const progress = student.progressPercentage || student.progress_percentage || 0
  if (progress >= 80) return 'indicator-green'
  if (progress >= 50) return 'indicator-yellow'
  return 'indicator-red'
}

// 获取学生提示信息
function getStudentTooltip(student: any): string {
  const name = student.studentName || student.student_name || '学生'
  const account = getStudentAccount(student)
  const progress = Math.round(student.progressPercentage || student.progress_percentage || 0)
  return `${name} (${account}) - 进度: ${progress}%`
}

// 获取学生登录账号
function getStudentAccount(student: any): string {
  // 尝试多种可能的字段名，但不包括姓名字段
  return student.username || 
         student.account || 
         student.loginAccount || 
         student.login_account ||
         student.userAccount ||
         student.user_account ||
         student.email ||
         student.user_id?.toString() ||
         student.id?.toString() ||
         '未知账号'
}

// 参与度（基于在线学生和总学生的比例，以及平均进度）
const participationRate = computed(() => {
  if (totalStudents.value === 0) return 0
  const onlineRatio = (activeStudents.value.length / totalStudents.value) * 100
  const avgProgress = sessionStatistics.value?.average_progress || 0
  // 综合在线率和平均进度
  return Math.round((onlineRatio * 0.6 + avgProgress * 0.4))
})

// 平均得分
const averageScore = computed(() => {
  if (sessionStatistics.value?.average_score !== undefined) {
    return Math.round(sessionStatistics.value.average_score)
  }
  // 如果没有得分数据，基于进度估算
  const avgProgress = sessionStatistics.value?.average_progress || 0
  return Math.round(avgProgress * 0.8) // 假设进度和得分有一定相关性
})

// 互动次数（基于活动模块的提交数）
const interactionCount = computed(() => {
  // 可以从sessionStatistics或其他数据源获取
  return sessionStatistics.value?.interaction_count || 12
})

// 提问数量
const questionCount = computed(() => {
  return sessionStatistics.value?.question_count || 8
})

// 正确率
const accuracyRate = computed(() => {
  if (sessionStatistics.value?.accuracy_rate !== undefined) {
    return Math.round(sessionStatistics.value.accuracy_rate)
  }
  // 如果没有数据，基于平均进度估算
  const avgProgress = sessionStatistics.value?.average_progress || 0
  return Math.round(avgProgress * 0.95) // 假设正确率略高于进度
})

// 进度条数据（示例数据，可以根据实际需求调整）
const progress1 = computed(() => {
  const avgProgress = sessionStatistics.value?.average_progress || 0
  return Math.min(100, Math.round(avgProgress * 0.9))
})

const progress2 = computed(() => {
  const participation = participationRate.value
  return Math.min(100, Math.round(participation * 0.85))
})

const progress3 = computed(() => {
  const accuracy = accuracyRate.value
  return Math.min(100, Math.round(accuracy * 0.95))
})


const currentCell = computed(() => {
  if (!props.lesson?.content || !session.value) {
    console.log('🔍 currentCell: 缺少必要数据', {
      hasLesson: !!props.lesson,
      hasContent: !!props.lesson?.content,
      hasSession: !!session.value,
    })
    return null
  }
  
  // 如果 selectedCellIndex 有效，优先使用它
  if (selectedCellIndex.value >= 0 && selectedCellIndex.value < props.lesson.content.length) {
    const cell = props.lesson.content[selectedCellIndex.value]
    console.log('✅ currentCell: 使用 selectedCellIndex', {
      selectedCellIndex: selectedCellIndex.value,
      cellType: cell?.type,
      cellTitle: cell?.title,
      cellOrder: cell?.order,
    })
    return cell
  }
  
  // 否则使用 current_cell_id 查找
  const currentId = session.value.current_cell_id
  if (!currentId || currentId === 0) {
    console.log('🔍 currentCell: current_cell_id 无效', {
      currentId,
      selectedCellIndex: selectedCellIndex.value,
    })
    return null
  }
  
  // 查找匹配的Cell
  const foundCell = props.lesson.content.find((cell, index) => {
    const cellId = getCellId(cell)
    // 尝试匹配数字ID
    if (typeof cellId === 'number' && cellId === currentId) return true
    // 尝试匹配字符串ID（转换为数字）
    if (typeof cellId === 'string') {
      const numId = parseInt(cellId)
      if (!isNaN(numId) && numId === currentId) return true
    }
    // 尝试通过索引匹配（如果currentId是顺序索引）
    if (index === currentId) return true
    // 尝试通过order匹配
    if (cell.order !== undefined && cell.order === currentId) return true
    return false
  })
  
  console.log('🔍 currentCell: 通过 current_cell_id 查找', {
    currentId,
    foundCell: foundCell ? { type: foundCell.type, title: foundCell.title } : null,
  })
  
  return foundCell || null
})

// 获取当前活动 Cell 的数据库 ID（用于查询提交数据）
// 计算 displayCellOrders（从 session.settings 中获取）
const displayCellOrders = computed(() => {
  if (!session.value?.settings) return []
  const settings = session.value.settings as any
  if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
    return settings.display_cell_orders
  }
  return []
})

const currentActivityDbCell = computed(() => {
  if (!currentCell.value || currentCell.value.type !== 'activity') {
    console.log('🔍 currentActivityDbCell: 不是活动模块', {
      hasCurrentCell: !!currentCell.value,
      cellType: currentCell.value?.type,
    })
    return null
  }
  
  if (!dbCells.value || dbCells.value.length === 0) {
    console.log('🔍 currentActivityDbCell: dbCells 为空', {
      dbCellsLength: dbCells.value?.length || 0,
    })
    return null
  }
  
  // 通过 order 查找对应的数据库 Cell
  const order = currentCell.value.order
  if (order === undefined) {
    console.log('🔍 currentActivityDbCell: currentCell.order 未定义', {
      currentCell: currentCell.value,
    })
    return null
  }
  
  // 尝试匹配 cell_type（可能是 'ACTIVITY' 或 'activity'）
  const matchedDbCell = dbCells.value.find(dbCell => {
    const cellTypeMatch = dbCell.cell_type === 'ACTIVITY' || 
                          dbCell.cell_type === 'activity' ||
                          dbCell.cell_type?.toUpperCase() === 'ACTIVITY'
    return dbCell.order === order && cellTypeMatch
  })
  
  console.log('🔍 currentActivityDbCell 查找结果:', {
    currentCellOrder: order,
    dbCells: dbCells.value.map(c => ({ id: c.id, order: c.order, type: c.cell_type })),
    matchedDbCell: matchedDbCell ? { id: matchedDbCell.id, order: matchedDbCell.order } : null,
  })
  
  return matchedDbCell || null
})


// 方法
// 使用工具函数获取 Cell ID（保留此函数名以兼容现有代码）
function getCellId(cell: Cell): number | string | null {
  return getCellIdUtil(cell)
}

function getCellTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    text: '文本',
    code: '代码',
    activity: '活动',
    video: '视频',
    flowchart: '流程图',
    qa: '问答',
  }
  return labels[type] || type
}

function getCellTypeEmoji(type: string): string {
  const emojis: Record<string, string> = {
    text: '📄',
    code: '💻',
    activity: '📝',
    video: '📹',
    flowchart: '📊',
    qa: '❓',
  }
  return emojis[type] || '📦'
}

// 判断模块是否激活
function isModuleActive(cell: Cell, index: number): boolean {
  if (!session.value) return false
  
  // 多选模式：优先使用 displayCellOrders
  if (displayCellOrders.value !== undefined && Array.isArray(displayCellOrders.value)) {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return displayCellOrders.value.includes(cellOrder)
  }
  
  // 单选模式：使用 current_cell_id 或 selectedCellIndex
  if (selectedCellIndex.value >= 0 && selectedCellIndex.value === index) {
    return true
  }
  
  const currentId = session.value.current_cell_id
  if (!currentId || currentId === 0) return false
  
  const cellId = getCellId(cell)
  if (typeof cellId === 'number' && cellId === currentId) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === currentId) return true
  }
  
  return false
}

// 判断活动模块是否激活
function isModuleActivityActive(cell: Cell, index: number): boolean {
  if (cell.type !== 'activity') return false
  if (!session.value?.current_activity_id) return false
  
  const cellId = getCellId(cell)
  if (typeof cellId === 'number' && cellId === session.value.current_activity_id) return true
  if (typeof cellId === 'string') {
    const numId = parseInt(cellId)
    if (!isNaN(numId) && numId === session.value.current_activity_id) return true
  }
  return false
}

// 处理模块项点击
function handleModuleItemClick(cell: Cell, index: number) {
  if (loading.value) return
  
  const cellId = getCellId(cell)
  const cellOrder = cell.order !== undefined ? cell.order : index
  
  // 使用 handleControlBoardNavigate 处理导航
  handleControlBoardNavigate(cellId, cellOrder, 'toggle', false)
}

// 处理复选框点击（防止事件冒泡）
function handleModuleCheckboxClick(cell: Cell, index: number, event: Event) {
  event.stopPropagation()
  console.log('🖱️ 复选框区域被点击:', { index, cellId: cell.id })
}

// 处理复选框变化
function handleModuleCheckboxChange(cell: Cell, index: number, event: Event) {
  console.log('🔘 复选框 change 事件触发:', { index, cellId: cell.id, loading: loading.value })
  
  if (loading.value) {
    console.warn('⏸️ 切换中，请稍候...')
    return
  }
  
  const target = event.target as HTMLInputElement
  const isChecked = target.checked
  const isCurrentlyActive = isModuleActive(cell, index)
  
  console.log('🔍 复选框状态检查:', {
    isChecked,
    isCurrentlyActive,
    displayCellOrders: displayCellOrders.value,
  })
  
  // 如果状态没有变化，不需要操作
  if (isChecked === isCurrentlyActive) {
    console.log('⏭️ 状态未变化，跳过操作')
    return
  }
  
  // 确定操作类型：如果勾选则添加，否则移除
  const action: 'add' | 'remove' = isChecked ? 'add' : 'remove'
  
  console.log('☑️ 复选框状态变化:', {
    index,
    cellId: cell.id,
    isChecked,
    action,
    cellType: cell.type,
    cellOrder: cell.order,
  })
  
  const cellId = getCellId(cell)
  const cellOrder = cell.order !== undefined ? cell.order : index
  
  console.log('📤 准备发送导航事件:', {
    cellId,
    cellOrder,
    action,
    multiSelect: true,
    cellIdType: typeof cellId,
    isUUID: cellId && typeof cellId === 'string' ? isUUID(cellId) : false,
  })
  
  // 发送导航事件（多选模式）
  if (cellId && typeof cellId === 'string' && isUUID(cellId)) {
    console.log('✅ 使用 cellOrder (UUID):', cellOrder)
    handleControlBoardNavigate(null, cellOrder, action, true)
  } else {
    const numericId = toNumericId(cellId)
    if (numericId) {
      console.log('✅ 使用 numericId:', numericId)
      handleControlBoardNavigate(numericId, null, action, true)
    } else {
      console.log('✅ 使用 cellOrder (fallback):', cellOrder)
      handleControlBoardNavigate(null, cellOrder, action, true)
    }
  }
  
  console.log('✅ 导航事件已发送 (emit 调用完成)')
}

// 获取模块提示信息
function getModuleTooltip(cell: Cell, index: number): string {
  const typeLabel = getCellTypeLabel(cell.type)
  const title = cell.title || `模块 ${index + 1}`
  const isActiveCell = isModuleActive(cell, index)
  const status = isActiveCell ? ' (已选中)' : ''
  return `${index + 1}. ${title} - ${typeLabel}${status}`
}

// 获取当前模块索引
function getCurrentModuleIndex(): number {
  if (!props.lesson?.content || !currentCell.value) return -1
  return props.lesson.content.findIndex(cell => {
    const cellId = getCellId(cell)
    const currentId = session.value?.current_cell_id
    if (!currentId) return false
    return cellId === currentId || (typeof cellId === 'string' && parseInt(cellId) === currentId)
  })
}

// 计算进度落后学生数量（进度 < 50%）
const studentsBehindCount = computed(() => {
  return activeStudents.value.filter(s => {
    const progress = s.progressPercentage || s.progress_percentage || 0
    return progress < 50
  }).length
})

// 是否有预警（用于高亮预警栏）
const hasAlerts = computed(() => {
  return studentsBehindCount.value > 0 || questionCount.value > 0 || hasLowSubmissionRate.value
})

// 是否有低提交率（活动模块）
const hasLowSubmissionRate = computed(() => {
  if (!currentCell.value || currentCell.value.type !== 'activity') return false
  if (!sessionStatistics.value) return false
  // 假设如果提交率低于 50% 且总学生数 > 5，则显示预警
  // 这里需要根据实际的提交统计数据来判断
  return false // TODO: 根据实际数据实现
})

// 滚动到落后学生区域
function scrollToStudentsBehind() {
  // 实现滚动逻辑，可以给落后学生添加特殊标记
  const element = document.querySelector('.students-behind-section')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}

// 滚动到提问区域
function scrollToQuestions() {
  // TODO: 实现滚动到提问列表的逻辑
  console.log('滚动到提问列表')
}

// 根据 order 获取 Cell
function getCellByOrder(order: number): Cell | null {
  if (!props.lesson?.content) return null
  return props.lesson.content.find((cell, index) => {
    const cellOrder = cell.order !== undefined ? cell.order : index
    return cellOrder === order
  }) || null
}

// 获取文本预览（去除HTML标签，截取前N字符）
function getTextPreview(cell: Cell, maxLength: number = 100): string {
  if (cell.type !== 'text') return ''
  const content = (cell as any).content
  if (!content?.html) return '文本内容'
  
  // 去除HTML标签
  const text = content.html.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
  return text.slice(0, maxLength) + (text.length > maxLength ? '...' : '')
}

// 获取代码预览（截取前50行）
function getCodePreview(cell: Cell): string {
  if (cell.type !== 'code') return ''
  const content = (cell as any).content
  if (!content?.code) return '// 代码内容'
  
  const lines = content.code.split('\n')
  return lines.slice(0, 10).join('\n') + (lines.length > 10 ? '\n...' : '')
}

// 切换模块面板全屏
function toggleModulePanelFullscreen() {
  modulePanelFullscreen.value = !modulePanelFullscreen.value
}

// 切换整个导播台全屏
async function togglePanelFullscreen() {
  if (!isPanelFullscreen.value) {
    // 进入全屏
    try {
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
      isPanelFullscreen.value = true
    } catch (error: any) {
      console.error('进入全屏失败:', error)
      // 如果浏览器全屏失败，使用CSS全屏模式
      isPanelFullscreen.value = true
    }
  } else {
    // 退出全屏
    try {
      if (document.exitFullscreen) {
        await document.exitFullscreen()
      } else if ((document as any).webkitExitFullscreen) {
        await (document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        await (document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        await (document as any).msExitFullscreen()
      }
      isPanelFullscreen.value = false
    } catch (error: any) {
      console.error('退出全屏失败:', error)
      isPanelFullscreen.value = false
    }
  }
}

// 监听浏览器全屏状态变化
function handleFullscreenChange() {
  const isCurrentlyFullscreen = !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).mozFullScreenElement ||
    (document as any).msFullscreenElement
  )
  
  if (!isCurrentlyFullscreen && isPanelFullscreen.value) {
    isPanelFullscreen.value = false
  }
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  // 显示为"15分钟"格式
  return `${minutes}分钟`
}

function formatRemainingTime(seconds: number): string {
  if (seconds <= 0) return '0:00'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 会话操作
// 创建课堂会话（保持 PENDING 状态，等待学生加入）
async function handleCreateSession() {
  loading.value = true
  try {
    // 首先需要创建会话，这里需要classroom_id
    // 暂时从路由或props中获取，或者提示用户选择班级
    const classroomId = route.params.classroomId as string || '1'
    
    try {
      console.log('🚀 Creating session...')
      // 创建会话（状态为 PENDING）
      const newSession = await classroomSessionService.createSession(props.lessonId, {
        classroom_id: parseInt(classroomId),
      })
      
      console.log('✅ Session created, received:', newSession)
      
      // 检查响应
      if (!newSession || !newSession.id) {
        console.error('❌ Invalid session response:', newSession)
        throw new Error('创建会话失败：服务器返回的数据格式不正确')
      }
      
      // 保持 PENDING 状态，不立即开始
      session.value = newSession
      console.log('✅ Session created in PENDING state, waiting for students...')
      
      // 加载学生列表（开始轮询）
      loadParticipants()
      
      // 设置定时刷新学生列表（每3秒）
      const refreshInterval = setInterval(() => {
        if (session.value && session.value.status === 'pending') {
          loadParticipants()
        } else {
          clearInterval(refreshInterval)
        }
      }, 3000)
      
      // 组件卸载时清除定时器
      onUnmounted(() => {
        clearInterval(refreshInterval)
      })
    } catch (createError: any) {
      // 如果创建失败，检查是否是因为已有活跃会话
      const errorDetail = createError.response?.data?.detail || createError.message || ''
      
      if (errorDetail.includes('已有活跃的课堂会话') || createError.response?.status === 400) {
        // 尝试查找并加载现有会话
        console.log('检测到已有活跃会话，尝试加载...')
        
        // 首先尝试从错误信息中提取会话ID
        const sessionIdMatch = errorDetail.match(/ID:\s*(\d+)/)
        let activeSessions: any[] = []
        
        if (sessionIdMatch) {
          // 如果错误信息中包含会话ID，直接使用它
          const sessionId = parseInt(sessionIdMatch[1])
          console.log(`从错误信息中提取到会话ID: ${sessionId}`)
          try {
            const existingSession = await classroomSessionService.getSession(sessionId)
            if (existingSession) {
              activeSessions = [existingSession]
              console.log(`成功通过ID获取会话:`, existingSession)
            }
          } catch (getError: any) {
            console.error('通过ID获取会话失败:', getError)
            // 如果通过ID获取失败，尝试查询列表
          }
        }
        
        // 如果通过ID获取失败或没有提取到ID，尝试查询列表
        if (activeSessions.length === 0) {
          try {
            const allSessions = await classroomSessionService.listSessions(props.lessonId)
            console.log(`📋 查询到 ${allSessions.length} 个会话`)
            // 过滤活跃会话，并且如果知道classroomId，也按classroomId过滤
            activeSessions = allSessions.filter(s => {
              const isActive = s.status === 'active' || s.status === 'paused' || s.status === 'pending'
              if (!isActive) return false
              // 尝试匹配 classroomId（如果有的话）
              const sessionClassroomId = s.classroomId || (s as any).classroom_id
              const targetClassroomId = parseInt(classroomId)
              if (sessionClassroomId && targetClassroomId) {
                return sessionClassroomId === targetClassroomId
              }
              // 如果没有 classroomId，匹配所有活跃会话
              return true
            })
            console.log(`✅ 通过列表查询找到 ${activeSessions.length} 个活跃会话（classroom_id=${classroomId}）`)
          } catch (e: any) {
            console.error('查询会话列表失败:', e)
            const listErrorDetail = e.response?.data?.detail || e.message || ''
            console.error('查询失败详情:', listErrorDetail)
            // 如果列表查询也失败，尝试再次从错误信息中提取ID
            if (!sessionIdMatch) {
              const fallbackIdMatch = listErrorDetail.match(/ID:\s*(\d+)/) || errorDetail.match(/ID:\s*(\d+)/)
              if (fallbackIdMatch) {
                const fallbackSessionId = parseInt(fallbackIdMatch[1])
                try {
                  const existingSession = await classroomSessionService.getSession(fallbackSessionId)
                  if (existingSession) {
                    activeSessions = [existingSession]
                    console.log(`通过备用方法获取会话成功`)
                  }
                } catch (fallbackError: any) {
                  console.error('备用方法也失败:', fallbackError)
                  // 检查是否是权限问题
                  if (fallbackError.response?.status === 403) {
                    console.warn('⚠️ 无权限访问该会话，可能是会话不属于当前用户')
                  } else if (fallbackError.response?.status === 404) {
                    console.warn('⚠️ 会话不存在，可能已被删除')
                  }
                }
              }
            }
          }
        }
        
        if (activeSessions.length > 0) {
          // 找到现有会话，直接使用
          const existingSession = activeSessions[0]
          session.value = existingSession
          
          // 如果会话是pending状态，不自动开始，保持等待状态
          // 让教师手动点击"开始上课"按钮
          
          // 注意：不在这里自动启动计时器
          // 只有在用户点击"开始上课"或"继续"按钮时才启动计时器
          loadParticipants()
          loadStatistics()
          
          // 如果会话是 pending 状态，设置定时刷新学生列表
          if (session.value.status === 'pending') {
            const refreshInterval = setInterval(() => {
              if (session.value && session.value.status === 'pending') {
                loadParticipants()
              } else {
                clearInterval(refreshInterval)
              }
            }, 3000)
            
            onUnmounted(() => {
              clearInterval(refreshInterval)
            })
          }
          
          // 提示用户已加载现有会话
          const statusText = {
            'active': '进行中',
            'paused': '已暂停',
            'pending': '等待学生加入'
          }[existingSession.status] || '未知'
          console.log(`✅ 已自动加载现有会话 (ID: ${existingSession.id}, 状态: ${statusText})`)
          
          // 如果会话是暂停状态，提示用户
          if (existingSession.status === 'paused') {
            // 不显示alert，让用户看到界面状态即可
            console.log('💡 会话当前处于暂停状态，可以点击"继续"按钮恢复')
          }
          
          return // 成功加载，退出函数
        } else {
          // 没有找到活跃会话
          console.warn('⚠️ 虽然检测到已有活跃会话，但无法加载会话详情')
          console.warn('原始错误:', createError.response?.data || createError.message)
          
          // 尝试最后一次：直接从错误信息中提取ID
          const finalIdMatch = errorDetail.match(/ID:\s*(\d+)/)
          if (finalIdMatch) {
            const finalSessionId = parseInt(finalIdMatch[1])
            console.log(`🔄 最后尝试：直接使用会话ID ${finalSessionId}`)
            try {
              const finalSession = await classroomSessionService.getSession(finalSessionId)
              if (finalSession) {
                session.value = finalSession
                
                // 如果会话是pending状态，不自动开始，保持等待状态
                
          // 注意：不在这里自动启动计时器
          // 只有在用户点击"开始上课"或"继续"按钮时才启动计时器
          loadParticipants()
          loadStatistics()
                
                // 如果会话是 pending 状态，设置定时刷新学生列表
                if (session.value.status === 'pending') {
                  const refreshInterval = setInterval(() => {
                    if (session.value && session.value.status === 'pending') {
                      loadParticipants()
                    } else {
                      clearInterval(refreshInterval)
                    }
                  }, 3000)
                  
                  onUnmounted(() => {
                    clearInterval(refreshInterval)
                  })
                }
                
                console.log(`✅ 成功！已加载会话 ID: ${finalSessionId}`)
                return
              }
            } catch (finalError: any) {
              console.error('❌ 最后尝试也失败:', finalError)
              console.error('❌ 错误详情:', {
                message: finalError.message,
                response: finalError.response,
                status: finalError.response?.status,
                data: finalError.response?.data,
              })
              // 检查具体错误类型
              if (finalError.response?.status === 403) {
                console.error('⚠️ 无权限访问该会话，可能是会话不属于当前用户')
                throw new Error('无权限访问该会话。会话可能属于其他教师，请确保您是该会话的创建者。')
              } else if (finalError.response?.status === 404) {
                console.error('⚠️ 会话不存在，可能已被删除')
                throw new Error('会话不存在，可能已被删除。请刷新页面重试。')
              } else if (finalError.response?.status === 400) {
                // 400 错误可能包含详细信息
                const errorDetail = finalError.response?.data?.detail || finalError.message || '无法加载会话'
                console.error('⚠️ 请求错误 (400):', errorDetail)
                throw new Error(`无法加载现有会话：${errorDetail}`)
              } else {
                // 其他错误，抛出更友好的错误信息
                const finalErrorMessage = finalError.response?.data?.detail || finalError.message || '无法加载会话'
                console.error('⚠️ 未知错误:', finalErrorMessage)
                throw new Error(`无法加载现有会话：${finalErrorMessage}`)
              }
            }
          }
          
          // 如果所有方法都失败，抛出更友好的错误信息
          const friendlyError = new Error(
            '无法加载现有活跃会话。请尝试刷新页面，或联系管理员检查会话状态。'
          )
          throw friendlyError
        }
      } else {
        // 其他错误，直接抛出
        throw createError
      }
    }
  } catch (error: any) {
    console.error('Failed to create session:', error)
    // 提取更友好的错误信息
    let errorMessage = error.message || error.response?.data?.detail || '创建课堂失败'
    
    // 如果是已知的错误类型，显示更友好的提示
    if (errorMessage.includes('无权限')) {
      errorMessage = '无法访问该会话。请确保您是该会话的创建者。'
    } else if (errorMessage.includes('不存在')) {
      errorMessage = '会话不存在，请刷新页面重试。'
    } else if (errorMessage.includes('已有活跃的课堂会话')) {
      // 这种情况应该已经被处理了，但如果仍然出现，说明加载失败
      errorMessage = '检测到已有活跃会话，但无法自动加载。请刷新页面重试。'
    }
    
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 开始上课（将 PENDING 状态变为 ACTIVE）
async function handleBeginClass() {
  if (!session.value || session.value.status !== 'pending') return
  
  loading.value = true
  try {
    console.log('🎬 Starting session with id:', session.value.id)
    session.value = await classroomSessionService.startSession(session.value.id)
    console.log('✅ Session started successfully:', session.value)
    
    // 检查开始会话的响应
    if (!session.value) {
      throw new Error('开始会话失败：服务器返回的数据格式不正确')
    }
    
    // 开始计时（新会话从0开始）
    // 注意：计时器会通过 watch 监听 session.status 变化自动启动
    // 这里确保状态正确即可，watch 会自动处理计时器启动
    if (session.value.status === 'active') {
      sessionDuration.value = 0  // 新会话从0开始
      // watch 会自动启动计时器，但为了确保立即启动，这里也调用一次
      if (!durationInterval.value) {
        startDurationTimer()
      }
    }
    
    // 加载统计信息
    loadStatistics()
    
    // 设置定时刷新学生列表和统计（每5秒）
    const refreshInterval = setInterval(() => {
      if (session.value && (session.value.status === 'active' || session.value.status === 'paused')) {
        loadParticipants()
        loadStatistics()
      } else {
        clearInterval(refreshInterval)
      }
    }, 5000)
    
    // 组件卸载时清除定时器
    onUnmounted(() => {
      clearInterval(refreshInterval)
    })
  } catch (error: any) {
    console.error('Failed to start session:', error)
    const errorMessage = error.message || error.response?.data?.detail || '开始上课失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 取消课堂（删除 PENDING 状态的会话）
async function handleCancelSession() {
  if (!session.value || session.value.status !== 'pending') return
  if (!confirm('确定要取消课堂吗？这将删除当前会话。')) return
  
  loading.value = true
  try {
    // 注意：这里可能需要一个删除会话的API，如果没有，可以结束会话
    // 暂时先提示用户
    alert('取消课堂功能需要后端支持删除会话API')
    // TODO: 实现删除会话的逻辑
    // await classroomSessionService.deleteSession(session.value.id)
    // session.value = null
  } catch (error: any) {
    console.error('Failed to cancel session:', error)
    alert('取消课堂失败')
  } finally {
    loading.value = false
  }
}

async function handlePause() {
  if (!session.value) return
  loading.value = true
  try {
    session.value = await classroomSessionService.pauseSession(session.value.id)
    stopDurationTimer()
  } catch (error: any) {
    console.error('Failed to pause session:', error)
    alert('暂停失败')
  } finally {
    loading.value = false
  }
}

async function handleResume() {
  if (!session.value) return
  loading.value = true
  try {
    session.value = await classroomSessionService.resumeSession(session.value.id)
    startDurationTimer()
  } catch (error: any) {
    console.error('Failed to resume session:', error)
    alert('继续失败')
  } finally {
    loading.value = false
  }
}

// 计算当前显示模式
const currentDisplayMode = computed(() => {
  if (!session.value?.settings) return 'window'
  const settings = session.value.settings as any
  return settings.display_mode || 'window'
})

// 切换显示模式
async function handleToggleDisplayMode() {
  if (!session.value) return
  
  const newMode = currentDisplayMode.value === 'fullscreen' ? 'window' : 'fullscreen'
  
  loading.value = true
  try {
    session.value = await classroomSessionService.updateDisplayMode(session.value.id, newMode)
    console.log(`✅ 显示模式已切换为: ${newMode}`)
  } catch (error: any) {
    console.error('❌ 切换显示模式失败:', error)
    alert('切换显示模式失败')
  } finally {
    loading.value = false
  }
}

async function handleEnd() {
  if (!session.value) return
  if (!confirm('确定要结束课程吗？')) return
  
  loading.value = true
  try {
    session.value = await classroomSessionService.endSession(session.value.id)
    stopDurationTimer()
  } catch (error: any) {
    console.error('Failed to end session:', error)
    alert('结束课程失败')
  } finally {
    loading.value = false
  }
}

// 隐藏所有内容（通过导播台的"隐藏"节点调用）
async function handleHideAll() {
  if (!session.value) return
  
  loading.value = true
  try {
    // 🆕 使用 displayCellOrders: [] 来隐藏所有内容
    session.value = await classroomSessionService.navigateToCell(session.value.id, {
      displayCellOrders: [],
      action: 'set',
    })
    selectedCellIndex.value = -1
  } catch (error: any) {
    console.error('Failed to hide content:', error)
    const errorMessage = error.response?.data?.detail || error.message || '隐藏内容失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}


// 活动控制
async function handleStartActivity() {
  if (!session.value || !currentCell.value) return
  
  // 使用session中的current_cell_id，这是当前显示的Cell
  const currentCellId = session.value.current_cell_id
  if (!currentCellId) {
    alert('无法开始活动：当前没有显示任何Cell')
    return
  }
  
  loading.value = true
  try {
    session.value = await classroomSessionService.startActivity(session.value.id, {
      cellId: currentCellId,
    })
  } catch (error: any) {
    console.error('Failed to start activity:', error)
    const errorMessage = error.response?.data?.detail || error.message || '开始活动失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

async function handleEndActivity() {
  if (!session.value) return
  
  loading.value = true
  try {
    session.value = await classroomSessionService.endActivity(session.value.id)
  } catch (error: any) {
    console.error('Failed to end activity:', error)
    alert('结束活动失败')
  } finally {
    loading.value = false
  }
}

// 导播台导航处理
async function handleControlBoardNavigate(
  cellId: number | string | null, 
  cellOrder: number | null,
  action: 'toggle' | 'add' | 'remove' = 'toggle',
  multiSelect: boolean = false
) {
  console.log('📬 收到导播台导航事件:', { cellId, cellOrder, action, multiSelect })
  
  if (!session.value) {
    console.warn('⚠️ 无法导航：会话不存在')
    return
  }
  
  console.log('🎯 导播台导航请求:', { 
    cellId, 
    cellOrder, 
    cellIdType: typeof cellId, 
    action, 
    multiSelect,
    sessionId: session.value.id,
  })
  
  loading.value = true
  try {
    // 🆕 新方式：使用 display_cell_orders（推荐）
    // 获取当前选中的 orders（从 settings 中获取，如果有的话）
    let displayOrders: number[] = []
    const currentSettings = session.value.settings as any
    if (currentSettings?.display_cell_orders) {
      displayOrders = [...currentSettings.display_cell_orders]
    } else if (currentSettings?.display_cell_ids && props.lesson?.content) {
      // 向后兼容：如果只有 display_cell_ids，转换成 orders
      displayOrders = currentSettings.display_cell_ids
        .map((id: number) => {
          const cell = props.lesson!.content.find((c: any) => getCellId(c) === id)
          return cell ? (cell.order !== undefined ? cell.order : props.lesson!.content.indexOf(cell)) : -1
        })
        .filter((order: number) => order >= 0)
    }
    
    // 如果是隐藏所有（cellId === 0、"0" 或 null）且不是多选模式
    const isHideAll = (cellId === 0 || cellId === "0" || cellId === null) && cellOrder === null && !multiSelect
    if (isHideAll) {
      displayOrders = []
    } else if (cellOrder !== null) {
      // 根据 action 更新 displayOrders
      if (action === 'add') {
        if (!displayOrders.includes(cellOrder)) {
          displayOrders.push(cellOrder)
        }
      } else if (action === 'remove') {
        displayOrders = displayOrders.filter(o => o !== cellOrder)
      } else if (action === 'toggle') {
        if (displayOrders.includes(cellOrder)) {
          displayOrders = displayOrders.filter(o => o !== cellOrder)
        } else {
          displayOrders = multiSelect ? [...displayOrders, cellOrder] : [cellOrder]
        }
      }
    }
    
    // 发送新方式的请求
    const requestData = {
      displayCellOrders: displayOrders,
      action,
    }
    console.log('📤 发送导航请求（新方式）:', requestData)
    const updatedSession = await classroomSessionService.navigateToCell(session.value.id, requestData)
    
    // 确保更新后的会话状态正确（不要丢失状态）
    if (updatedSession) {
      session.value = {
        ...session.value,
        ...updatedSession,
        status: session.value.status, // 保持原有状态，导航不应该改变会话状态
        id: session.value.id,
      }
      
      // 使用 display_cell_orders
      const updatedSettings = updatedSession.settings as any
      if (updatedSettings?.display_cell_orders) {
        const orders = updatedSettings.display_cell_orders
        console.log('✅ 使用 display_cell_orders:', orders)
      }
      console.log('✅ 更新显示 Cell 列表, settings:', updatedSession.settings)
    }
    
    // 导航后立即刷新学生列表
    loadParticipants()
    
    // 🆕 如果点击的是活动模块，确保数据库记录存在
    if (cellOrder !== null && props.lesson?.content) {
      const clickedCell = props.lesson.content.find((cell, idx) => {
        const cellOrderValue = cell.order !== undefined ? cell.order : idx
        return cellOrderValue === cellOrder
      })
      
      if (clickedCell && clickedCell.type === 'activity') {
        console.log('🎯 点击了活动模块，确保数据库记录存在...')
        const createdCellId = await ensureActivityCellExists(clickedCell, cellOrder)
        // 重新加载 dbCells 以获取最新数据
        await loadDbCells()
        
        // 🆕 如果创建成功，等待一小段时间让数据库记录生效
        if (createdCellId) {
          console.log('✅ 活动模块数据库记录已创建，等待生效...')
          await new Promise(resolve => setTimeout(resolve, 500))
          // 再次加载确保获取到最新数据
          await loadDbCells()
        }
      }
    }
    
    // 🆕 如果 dbCells 为空，重新加载（可能活动模块刚创建）
    if (dbCells.value.length === 0) {
      console.log('🔄 dbCells 为空，重新加载...')
      await loadDbCells()
    }
    
    // 更新selectedCellIndex
    if (cellId === 0) {
      selectedCellIndex.value = -1
    } else if (cellOrder !== null && cellOrder !== undefined && props.lesson?.content) {
      // 🆕 通过 cellOrder 查找对应的数组索引（而不是直接使用 cellOrder）
      const index = props.lesson.content.findIndex((cell, idx) => {
        const cellOrderValue = cell.order !== undefined ? cell.order : idx
        return cellOrderValue === cellOrder
      })
      if (index >= 0) {
        selectedCellIndex.value = index
        console.log('✅ 通过 cellOrder 找到索引:', index, 'cellOrder:', cellOrder)
      } else {
        // 如果找不到，尝试使用 cellOrder 作为索引（向后兼容）
        selectedCellIndex.value = cellOrder < props.lesson.content.length ? cellOrder : -1
        console.log('⚠️ 未找到匹配的 cell，使用 cellOrder 作为索引:', cellOrder)
      }
    } else if (cellId && props.lesson?.content) {
      // 通过 cellId 查找索引
      const index = props.lesson.content.findIndex((cell) => {
        const id = getCellId(cell)
        if (typeof id === 'number' && id === cellId) return true
        if (typeof id === 'string') {
          const numId = parseInt(id, 10)
          if (!isNaN(numId) && numId === cellId) return true
        }
        return false
      })
      if (index >= 0) {
        selectedCellIndex.value = index
        console.log('✅ 通过 cellId 找到索引:', index)
      } else {
        console.warn('⚠️ 未找到匹配的 cell，使用 cellOrder 作为 fallback')
        // 如果找不到，尝试使用返回的 currentCellId 对应的索引
        if (updatedSession?.currentCellId) {
          const currentId = updatedSession.currentCellId
          const foundIndex = props.lesson.content.findIndex((cell) => {
            const id = getCellId(cell)
            return id === currentId || (typeof id === 'string' && String(id) === String(currentId))
          })
          if (foundIndex >= 0) {
            selectedCellIndex.value = foundIndex
          }
        }
      }
    }
  } catch (error: any) {
    console.error('Failed to navigate from control board:', error)
    const errorMessage = error.response?.data?.detail || error.message || '切换内容失败'
    alert(errorMessage)
  } finally {
    loading.value = false
  }
}

// 加载数据
async function loadParticipants() {
  if (!session.value) {
    console.warn('⚠️ 无法加载学生列表：会话不存在')
    return
  }
  
  console.log('🔄 开始加载在线学生列表，会话ID:', session.value.id)
  loadingStudents.value = true
  try {
    // 获取所有在线学生（is_active=true）
    const participants = await classroomSessionService.getParticipants(session.value.id, true)
    
    // 确保是数组且只包含在线学生
    const activeParticipants = Array.isArray(participants) 
      ? participants.filter(p => p.isActive !== false)
      : []
    
    activeStudents.value = activeParticipants
    console.log(`👥 加载在线学生完成: ${activeStudents.value.length} 人`, activeStudents.value.map(s => ({
      id: s.id,
      name: s.studentName || s.student_name,
      isActive: s.isActive || s.is_active,
    })))
    
    // 更新会话统计中的在线学生数
    if (session.value) {
      session.value.activeStudents = activeStudents.value.length
      console.log('📊 更新会话统计，在线学生数:', session.value.activeStudents)
    }
  } catch (error: any) {
    console.error('❌ 加载学生列表失败:', error)
    console.error('❌ 错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data,
    })
    activeStudents.value = []
  } finally {
    loadingStudents.value = false
  }
}

async function loadStatistics() {
  if (!session.value) return
  
  try {
    sessionStatistics.value = await classroomSessionService.getStatistics(session.value.id)
  } catch (error) {
    console.error('Failed to load statistics:', error)
  }
}

// 定时器
function startDurationTimer() {
  if (durationInterval.value) return
  
  // 如果还没有开始计时（值为0或未定义），从0开始
  // 如果已经有值（比如暂停后继续），保持当前值继续计时
  if (sessionDuration.value === 0 || sessionDuration.value === null || sessionDuration.value === undefined) {
    sessionDuration.value = 0
  }
  
  // 每秒递增，直到达到课程时长
  durationInterval.value = setInterval(() => {
    sessionDuration.value = Math.min(sessionDuration.value + 1, LESSON_DURATION)
  }, 1000)
}

function stopDurationTimer() {
  if (durationInterval.value) {
    clearInterval(durationInterval.value)
    durationInterval.value = null
  }
}

// 监听session状态变化，自动启动/停止计时器
watch(() => session.value?.status, (status, oldStatus) => {
  if (status === 'active') {
    // 当状态变为 active 时，启动计时器
    console.log('⏱️ 会话状态变为 active，启动计时器')
    if (!durationInterval.value) {
      // 如果计时器还没有启动
      // 只有在从 pending 状态变为 active（新开始）时，才重置为0
      // 如果是从 paused 恢复（继续），保持当前时长继续计时
      if (oldStatus === 'pending' || sessionDuration.value === 0) {
        sessionDuration.value = 0
      }
      startDurationTimer()
    }
  } else if (status === 'paused') {
    // 当状态变为 paused 时，停止计时器（但保持当前时长）
    console.log('⏸️ 会话状态变为 paused，停止计时器')
    stopDurationTimer()
  } else if (status === 'ended') {
    // 当状态变为 ended 时，停止计时器
    console.log('⏹️ 会话状态变为 ended，停止计时器')
    stopDurationTimer()
  } else {
    // 其他状态（如 pending），停止计时器
    stopDurationTimer()
  }
}, { immediate: true })

// 监听session变化，更新selectedCellIndex和displayCellIds
watch(() => session.value, (newSession) => {
  if (!props.lesson?.content || !newSession) return
  
  // 使用 display_cell_orders
  const settings = newSession.settings as any
  if (settings?.display_cell_orders && Array.isArray(settings.display_cell_orders)) {
    const orders = settings.display_cell_orders
    console.log('✅ watch: 使用 display_cell_orders:', orders)
    
    // 如果有选中的 orders，使用第一个的索引
    if (orders.length > 0) {
      selectedCellIndex.value = orders[0]
      return
    }
  }
  
  // 单选模式：更新 selectedCellIndex
  const cellId = newSession.current_cell_id
  if (!cellId || cellId === 0) {
    selectedCellIndex.value = -1
    return
  }
  
  // 查找匹配的Cell
  const index = props.lesson.content.findIndex(cell => {
    const id = getCellId(cell)
    // 尝试匹配数字ID
    if (typeof id === 'number' && id === cellId) return true
    // 尝试匹配字符串ID（转换为数字）
    if (typeof id === 'string') {
      const numId = parseInt(id)
      if (!isNaN(numId) && numId === cellId) return true
    }
    return false
  })
  
  if (index >= 0) {
    selectedCellIndex.value = index
  } else {
    // 如果没找到，设置为-1（隐藏状态）
    selectedCellIndex.value = -1
  }
}, { immediate: true, deep: true })

// 加载数据库中的 Cell 记录
async function loadDbCells() {
  try {
    const { api } = await import('../../services/api')
    const response = await api.get(`/cells/lesson/${props.lessonId}`)
    dbCells.value = Array.isArray(response) ? response : ([] as any)
    console.log('📦 加载数据库 Cell 记录:', dbCells.value.length, '个', dbCells.value)
  } catch (error: any) {
    console.warn('⚠️ 加载数据库 Cell 记录失败:', error)
    dbCells.value = []
  }
}

// 🆕 确保活动模块的数据库记录存在
async function ensureActivityCellExists(cell: Cell, order: number): Promise<number | null> {
  // 如果 dbCells 中已经有匹配的记录，直接返回
  const existing = dbCells.value.find(dbCell => 
    dbCell.order === order && 
    (dbCell.cell_type === 'ACTIVITY' || dbCell.cell_type === 'activity' || dbCell.cell_type?.toUpperCase() === 'ACTIVITY')
  )
  if (existing) {
    console.log('✅ 活动模块数据库记录已存在:', existing.id)
    return existing.id
  }
  
  // 尝试创建数据库记录
  try {
    console.log('📤 创建活动模块数据库记录...', {
      lessonId: props.lessonId,
      order,
      title: cell.title,
      type: cell.type,
    })
    
    const { api } = await import('../../services/api')
    // ActivityCell 有可选的 config 属性
    const activityCell = cell as ActivityCell
    const cellCreateData = {
      lesson_id: props.lessonId,
      cell_type: 'ACTIVITY',  // 后端使用大写枚举值
      title: cell.title || '',
      content: cell.content || {},
      config: activityCell.config || {},
      order: order,
      editable: cell.editable ?? false,
    }
    
    console.log('📤 发送创建 Cell 请求:', cellCreateData)
    const createResponse = await api.post<{ id: number | string }>('/cells', cellCreateData)
    const newCell = createResponse
    console.log('📥 创建 Cell 响应:', newCell)
    
    if (newCell && newCell.id) {
      const cellId = typeof newCell.id === 'number' ? newCell.id : parseInt(newCell.id, 10)
      if (!isNaN(cellId)) {
        console.log('✅ 成功创建活动模块数据库记录:', cellId)
        
        // 添加到 dbCells 数组
        dbCells.value.push({
          id: cellId,
          order: order,
          cell_type: 'ACTIVITY',
        })
        
        return cellId
      }
    }
  } catch (error: any) {
    console.error('❌ 创建活动模块数据库记录失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
    })
  }
  
  return null
}

// 初始化
onMounted(async () => {
  // 监听浏览器全屏状态变化
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
  // 加载数据库 Cell 记录（用于 ID 匹配）
  await loadDbCells()
  
  // 检查是否有现有的活跃会话
  try {
    // 查询所有会话，然后过滤出活跃的
    const allSessions = await classroomSessionService.listSessions(props.lessonId)
    const activeSessions = allSessions.filter(s => 
      s.status === 'active' || s.status === 'paused' || s.status === 'pending'
    )
    
    console.log('🔍 检查现有会话:', { total: allSessions.length, active: activeSessions.length })
    
    // 添加空值检查
    if (activeSessions && Array.isArray(activeSessions) && activeSessions.length > 0) {
      session.value = activeSessions[0]
      console.log('✅ 加载现有会话:', session.value)
      
      // 注意：只有在用户点击"开始上课"后才会启动计时器
      // 这里不自动启动，因为可能是之前已经开始的会话，需要从服务器获取已用时长
      // 如果会话是 active 状态，可以考虑从服务器获取已用时长，但暂时不自动启动计时器
      // 让用户通过"开始上课"按钮明确控制
      
      // 加载学生列表和统计
      loadParticipants()
      loadStatistics()
      
      // 设置定时刷新学生列表（每5秒）
      const refreshInterval = setInterval(() => {
        if (session.value && (session.value.status === 'active' || session.value.status === 'paused')) {
          loadParticipants()
          loadStatistics()
        } else {
          clearInterval(refreshInterval)
        }
      }, 5000)
      
      // 如果会话是 pending 状态，也设置定时刷新
      if (session.value.status === 'pending') {
        const pendingRefreshInterval = setInterval(() => {
          if (session.value && session.value.status === 'pending') {
            loadParticipants()
          } else {
            clearInterval(pendingRefreshInterval)
          }
        }, 3000)
        
        onUnmounted(() => {
          clearInterval(pendingRefreshInterval)
        })
      }
      
      // 组件卸载时清除定时器
      onUnmounted(() => {
        clearInterval(refreshInterval)
      })
    } else {
      console.log('ℹ️ 没有找到现有会话')
    }
  } catch (error: any) {
    console.error('❌ 加载现有会话失败:', error)
    // 如果是404或其他错误，不显示错误提示（可能是正常的，没有现有会话）
    if (error.response?.status !== 404) {
      console.warn('加载现有会话时出错，但可以继续创建新会话')
    }
  }
})

onUnmounted(() => {
  stopDurationTimer()
  
  // 移除全屏状态监听器
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
})
</script>

<style scoped>
/* 活动统计面板样式 */
.activity-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.teacher-control-panel {
  @apply bg-white rounded-lg border border-gray-200;
  min-height: auto;
  position: relative;
  width: 100%;
}

/* 导播台全屏模式 */
.teacher-control-panel.panel-fullscreen {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  border-radius: 0 !important;
  border: none !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow-y: auto;
}

.teacher-control-panel.panel-fullscreen .top-control-bar {
  position: sticky;
  top: 0;
  z-index: 100;
}

.teacher-control-panel.panel-fullscreen .main-layout {
  padding: 24px;
  min-height: calc(100vh - 280px);
  height: auto;
}

.teacher-control-panel.panel-fullscreen .teaching-modules {
  height: calc(100vh - 320px) !important;
  min-height: 700px !important;
  max-height: calc(100vh - 320px) !important;
}

.teacher-control-panel.panel-fullscreen .monitoring-module {
  height: calc(100vh - 320px);
  min-height: 600px;
  max-height: calc(100vh - 320px);
  overflow-y: auto;
}

/* 🎯 优化后的顶部控制栏 */
.top-control-bar {
  @apply bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm;
}

.top-control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
}

.top-control-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.lesson-info {
  @apply text-sm text-gray-600;
}

.lesson-title {
  @apply font-medium text-gray-800;
}

/* 关键指标行 - 首页风格卡片 */
.top-control-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px 24px;
  @apply bg-gray-50 border-t border-gray-200;
  overflow-x: auto;
}

@media (max-width: 1400px) {
  .top-control-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .top-control-metrics {
    grid-template-columns: 1fr;
  }
}

/* 指标卡片 - 首页风格 */
.metric-card {
  position: relative;
  overflow: hidden;
  @apply rounded-2xl border border-gray-100 bg-white/80 backdrop-blur-sm p-6 shadow-lg;
  transition: all 0.3s ease;
  transform: translateY(0);
}

.metric-card:hover {
  @apply shadow-2xl;
  transform: translateY(-4px);
}

.metric-accent-bar {
  position: absolute;
  inset-x: 0;
  top: 0;
  height: 4px;
}

.metric-card-content {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.metric-header-text {
  flex: 1;
  min-width: 0;
}

.metric-card-label {
  @apply text-xs font-semibold uppercase tracking-wide text-gray-500;
  margin-bottom: 4px;
}

.metric-card-title {
  @apply text-base font-bold text-gray-900;
  line-height: 1.3;
}

.metric-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.metric-icon-text {
  font-size: 24px;
  line-height: 1;
}

.metric-card-value-group {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 4px;
}

.metric-card-value {
  @apply text-3xl font-bold;
  line-height: 1;
}

.metric-card-value-small {
  @apply text-xl font-bold;
  line-height: 1.3;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-card-description {
  @apply text-sm text-gray-600;
  margin-top: 4px;
  line-height: 1.4;
}

/* 警告和危险状态 */
.metric-card.metric-warning .metric-accent-bar {
  @apply bg-gradient-to-r from-orange-500 to-amber-500;
}

.metric-card.metric-danger .metric-accent-bar {
  @apply bg-gradient-to-r from-red-500 to-rose-500;
}

.metric-card.metric-warning {
  @apply border-orange-200 bg-orange-50/50;
}

.metric-card.metric-danger {
  @apply border-red-200 bg-red-50/50;
}

/* 📺 学生预览面板样式 */
.student-preview-panel {
  /* 样式已在上面定义 */
}

/* 预览内容样式已在上面定义 */

.preview-item-compact {
  @apply bg-gray-50 border border-gray-200 rounded-lg p-2.5;
  transition: all 0.2s ease;
  flex-shrink: 0;
  min-height: 90px;
}

.preview-item-compact:hover {
  @apply border-gray-300 shadow-sm;
  transform: translateY(-1px);
}

.preview-item-header-compact {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  gap: 8px;
}

.preview-item-number {
  @apply text-xs font-bold text-gray-500 bg-gray-200 px-2 py-0.5 rounded;
}

.preview-item-type-compact {
  @apply text-xs text-gray-600 bg-white px-2 py-0.5 rounded border border-gray-300;
}

.preview-item-title-compact {
  @apply text-xs font-semibold text-gray-900 mb-1.5;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.preview-item-body-compact {
  @apply text-xs text-gray-600;
  min-height: 40px;
  max-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 文本预览（紧凑版） */
.preview-text-compact {
  width: 100%;
}

.preview-text-snippet {
  @apply text-xs text-gray-600;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.preview-text-snippet :deep(p) {
  margin: 0;
  display: inline;
}

/* 图标预览（紧凑版） */
.preview-video-compact,
.preview-code-compact,
.preview-activity-compact,
.preview-default-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px 0;
}

.preview-icon-small {
  width: 32px;
  height: 32px;
  @apply text-gray-400;
}

.preview-icon-wrapper-small {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  @apply text-gray-400;
}

.preview-icon-label {
  @apply text-xs text-gray-500;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* 更多模块提示（紧凑版） */
.preview-more-compact {
  @apply bg-gradient-to-br from-gray-100 to-gray-200 border-dashed border-2 border-gray-300;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80px;
}

.preview-more-content-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  @apply text-gray-500;
}

.preview-more-icon {
  @apply text-xl font-bold;
}

.preview-more-text-compact {
  @apply text-xs;
}

/* 实时数据部分样式已合并到监控模块中 */

.preview-item {
  @apply bg-gray-50 border border-gray-200 rounded-xl p-4;
  transition: all 0.2s ease;
  min-height: 180px;
  display: flex;
  flex-direction: column;
}

.preview-item:hover {
  @apply border-gray-300 shadow-md;
  transform: translateY(-2px);
}

.preview-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 8px;
}

.preview-item-badge {
  @apply text-sm font-semibold text-gray-900;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-item-type {
  @apply text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded;
  flex-shrink: 0;
}

.preview-item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 文本预览 */
.preview-text-content {
  flex: 1;
  @apply bg-white rounded-lg p-3 border border-gray-200;
  max-height: 120px;
  overflow-y: auto;
}

.preview-text-html {
  @apply text-sm text-gray-700;
  line-height: 1.6;
}

.preview-text-html :deep(p) {
  margin: 0 0 8px 0;
}

.preview-text-html :deep(p:last-child) {
  margin-bottom: 0;
}

/* 视频预览 */
.preview-video-content {
  flex: 1;
  @apply bg-gray-900 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-video-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-white;
}

.preview-video-icon {
  width: 48px;
  height: 48px;
}

.preview-video-title {
  @apply text-sm font-medium;
  text-align: center;
  padding: 0 12px;
}

/* 代码预览 */
.preview-code-content {
  flex: 1;
  @apply bg-gray-900 rounded-lg p-3;
  max-height: 120px;
  overflow-y: auto;
}

.preview-code-snippet {
  @apply text-xs text-green-400 font-mono;
  line-height: 1.5;
}

.preview-code-snippet code {
  @apply text-green-400;
}

/* 活动预览 */
.preview-activity-content {
  flex: 1;
  @apply bg-purple-50 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-activity-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-purple-700;
}

.preview-activity-icon {
  width: 40px;
  height: 40px;
}

/* 流程图预览 */
.preview-flowchart-content {
  flex: 1;
  @apply bg-indigo-50 rounded-lg flex items-center justify-center;
  min-height: 120px;
}

.preview-flowchart-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  @apply text-indigo-700;
}

.preview-flowchart-icon {
  width: 40px;
  height: 40px;
}

/* 默认预览 */
.preview-default-content {
  flex: 1;
  @apply bg-gray-100 rounded-lg flex flex-col items-center justify-center gap-3;
  min-height: 120px;
}

.preview-default-icon {
  @apply text-gray-400;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-default-text {
  @apply text-sm text-gray-600;
}

/* 更多模块提示 */
.preview-item-more {
  @apply bg-gradient-to-br from-gray-100 to-gray-200 border-dashed border-2 border-gray-300;
  justify-content: center;
  align-items: center;
}

.preview-more-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  @apply text-gray-500;
}

.preview-more-text {
  @apply text-2xl font-bold;
}

.preview-more-label {
  @apply text-xs;
}

/* ⚠️ 预警提示栏 */
.alert-bar {
  padding: 12px 24px;
  @apply border-b border-gray-200;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.3s ease;
}

.alert-bar.has-alerts {
  @apply bg-yellow-50 border-yellow-200;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.alert-warning {
  @apply bg-orange-50 text-orange-800 border border-orange-200;
}

.alert-info {
  @apply bg-blue-50 text-blue-800 border border-blue-200;
}

.alert-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.alert-action {
  margin-left: auto;
  padding: 4px 12px;
  @apply bg-white border border-current rounded-md text-sm font-medium;
  cursor: pointer;
  transition: all 0.2s ease;
}

.alert-action:hover {
  @apply bg-opacity-80;
}

/* 顶部标题栏（保留兼容性） */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 24px;
  @apply bg-white border border-gray-200 rounded-lg;
}

.panel-title {
  font-size: 24px;
  font-weight: bold;
  @apply text-gray-900;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
}

/* 主布局 - 三栏：左侧模块列表，中间预览，右侧监控模块 */
.main-layout {
  display: grid;
  grid-template-columns: 2fr 1.5fr 2fr;
  gap: 20px;
  margin-bottom: 24px;
  padding: 24px;
  position: relative;
  align-items: start;
  min-height: calc(100vh - 350px);
}

/* 学生预览面板 */
.student-preview-panel {
  height: calc(100vh - 320px);
  min-height: 500px;
  max-height: calc(100vh - 320px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.student-preview-panel .panel-title {
  flex-shrink: 0;
}

.preview-content-compact {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

/* 监控模块：合并的课堂监控和实时数据 */
.monitoring-module {
  height: calc(100vh - 320px);
  min-height: 500px;
  max-height: calc(100vh - 320px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.monitoring-module .panel-title {
  flex-shrink: 0;
}

.monitoring-module-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
  min-height: 0;
}

.monitoring-module-content::-webkit-scrollbar {
  width: 6px;
}

.monitoring-module-content::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 3px;
}

.monitoring-module-content::-webkit-scrollbar-thumb {
  @apply bg-gray-300;
  border-radius: 3px;
}

.monitoring-module-content::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}

.monitoring-students-section {
  flex: 1 1 auto;
  min-height: 0;
  max-height: calc(100% - 200px);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
}

.monitoring-students-section::-webkit-scrollbar {
  width: 6px;
}

.monitoring-students-section::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 3px;
}

.monitoring-students-section::-webkit-scrollbar-thumb {
  @apply bg-gray-300;
  border-radius: 3px;
}

.monitoring-students-section::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}

.monitoring-divider {
  height: 1px;
  @apply bg-gray-200;
  margin: 12px 0 8px 0;
  flex-shrink: 0;
}

.monitoring-stats-section {
  flex: 0 0 auto;
  min-height: 180px;
  padding-top: 12px;
  background: white;
}

.stats-section-title {
  @apply text-sm font-semibold text-gray-700 mb-3;
}

.stats-grid-compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card-compact {
  @apply bg-gray-50 border border-gray-200 rounded-lg p-3;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}

.stat-card-compact:hover {
  @apply bg-gray-100 border-gray-300 shadow-sm;
}

.stat-icon-compact {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  @apply bg-white border border-gray-200 rounded-lg;
  flex-shrink: 0;
  @apply text-gray-600;
}

.stat-icon-red {
  @apply text-red-600;
}

.stat-icon-green {
  @apply text-green-600;
}

.stat-icon-blue {
  @apply text-blue-600;
}

.stat-content-compact {
  flex: 1;
  min-width: 0;
}

.stat-label-compact {
  @apply text-xs text-gray-600 mb-1;
}

.stat-value-compact {
  @apply text-base font-bold text-gray-900;
}

/* 模块面板全屏模式时的布局 */
.main-layout.module-fullscreen-mode {
  grid-template-columns: 1fr 0fr 0fr !important;
}

.main-layout.module-fullscreen-mode .student-preview-panel,
.main-layout.module-fullscreen-mode .monitoring-module {
  display: none;
}

/* 模块面板全屏模式 */
/* 模块面板全屏模式 */
.main-layout.module-fullscreen-mode {
  grid-template-columns: 1fr 0fr 0fr !important;
  transition: grid-template-columns 0.3s ease;
}

/* 全屏模式下监控模块隐藏已在上面的规则中处理 */

.main-layout.module-fullscreen-mode .teaching-modules {
  height: calc(100vh - 280px) !important;
  min-height: 700px !important;
  max-height: calc(100vh - 280px) !important;
}

/* 通用面板样式 */
.panel {
  @apply bg-white rounded-lg border border-gray-200 p-6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.panel h3.panel-title {
  font-size: 18px;
  font-weight: 600;
  @apply text-gray-900;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  @apply border-b border-gray-200;
}

/* 左侧：教学模块 */
.teaching-modules {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 320px);
  min-height: 500px;
  max-height: calc(100vh - 320px);
  overflow: hidden;
}

.module-panel-fullscreen {
  height: calc(100vh - 48px) !important;
  min-height: auto !important;
  max-height: calc(100vh - 48px) !important;
}

.module-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  @apply border-b border-gray-200;
  flex-shrink: 0;
}

.module-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.module-header-actions {
  display: flex;
  gap: 8px;
}

.module-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  @apply bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.module-action-btn:hover {
  @apply bg-gray-200;
  transform: scale(1.05);
}

.module-count {
  font-size: 12px;
  @apply text-gray-600;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 8px;
  flex: 1;
  min-height: 0;
}

.module-list::-webkit-scrollbar {
  width: 6px;
}

.module-list::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb {
  @apply bg-gray-300;
  border-radius: 3px;
}

.module-list::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}

.module-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  padding-right: 60px; /* 为复选框预留空间 */
  @apply bg-white border-2 border-gray-200 rounded-xl;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 80px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0;
}

/* 全屏模式下模块项可以更大 */
.module-panel-fullscreen .module-item {
  min-height: 100px;
  padding: 20px;
  gap: 16px;
}

.module-panel-fullscreen .module-item-icon {
  width: 48px;
  height: 48px;
}

.module-panel-fullscreen .module-item-title {
  font-size: 16px;
}

.module-panel-fullscreen .module-item-subtitle {
  font-size: 14px;
}

.module-item:hover:not(.module-item-disabled) {
  @apply border-gray-300 shadow-lg;
  transform: translateX(4px);
}

.module-item-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 不同类型模块的颜色主题 */
.module-item-type-video {
  @apply border-blue-200 bg-blue-50;
}

.module-item-type-video:hover:not(.module-item-disabled) {
  @apply border-blue-300 bg-blue-100;
}

.module-item-type-text {
  @apply border-gray-200 bg-gray-50;
}

.module-item-type-text:hover:not(.module-item-disabled) {
  @apply border-gray-300 bg-gray-100;
}

.module-item-type-activity {
  @apply border-purple-200 bg-purple-50;
}

.module-item-type-activity:hover:not(.module-item-disabled) {
  @apply border-purple-300 bg-purple-100;
}

.module-item-type-code {
  @apply border-green-200 bg-green-50;
}

.module-item-type-code:hover:not(.module-item-disabled) {
  @apply border-green-300 bg-green-100;
}

.module-item-type-flowchart {
  @apply border-indigo-200 bg-indigo-50;
}

.module-item-type-flowchart:hover:not(.module-item-disabled) {
  @apply border-indigo-300 bg-indigo-100;
}

.module-item-type-qa {
  @apply border-yellow-200 bg-yellow-50;
}

.module-item-type-qa:hover:not(.module-item-disabled) {
  @apply border-yellow-300 bg-yellow-100;
}

/* 激活状态 */
.module-item-active {
  @apply shadow-xl ring-4 ring-offset-2;
  transform: translateX(4px) scale(1.02);
  z-index: 10;
}

.module-item-type-video.module-item-active {
  @apply bg-blue-500 border-blue-600 ring-blue-300;
}

.module-item-type-text.module-item-active {
  @apply bg-gray-600 border-gray-700 ring-gray-300;
}

.module-item-type-activity.module-item-active {
  @apply bg-purple-500 border-purple-600 ring-purple-300;
}

.module-item-type-code.module-item-active {
  @apply bg-green-500 border-green-600 ring-green-300;
}

.module-item-type-flowchart.module-item-active {
  @apply bg-indigo-500 border-indigo-600 ring-indigo-300;
}

.module-item-type-qa.module-item-active {
  @apply bg-yellow-500 border-yellow-600 ring-yellow-300;
}

/* 激活状态下的 hover 效果 - 保持深色背景以确保白色文字可见 */
.module-item-type-video.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-blue-600 border-blue-700 ring-blue-400;
}

.module-item-type-text.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-gray-700 border-gray-800 ring-gray-400;
}

.module-item-type-activity.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-purple-600 border-purple-700 ring-purple-400;
}

.module-item-type-code.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-green-600 border-green-700 ring-green-400;
}

.module-item-type-flowchart.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-indigo-600 border-indigo-700 ring-indigo-400;
}

.module-item-type-qa.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-yellow-600 border-yellow-700 ring-yellow-400;
}

.module-item-hidden {
  @apply bg-orange-50 border-orange-200;
}

.module-item-hidden:hover:not(.module-item-disabled) {
  @apply bg-orange-100 border-orange-300;
}

.module-item-hidden.module-item-active {
  @apply bg-orange-500 border-orange-600 ring-orange-300;
}

.module-item-hidden.module-item-active:hover:not(.module-item-disabled) {
  @apply bg-orange-600 border-orange-700 ring-orange-400;
}

.module-item-number {
  @apply absolute -top-3 -left-3 w-7 h-7 rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
  @apply bg-white border-2 border-gray-300 text-gray-700;
  @apply shadow-md;
  z-index: 2;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.module-item-type-video .module-item-number {
  @apply border-blue-400 text-blue-600;
}

.module-item-type-activity .module-item-number {
  @apply border-purple-400 text-purple-600;
}

.module-item-type-code .module-item-number {
  @apply border-green-400 text-green-600;
}

.module-item-type-flowchart .module-item-number {
  @apply border-indigo-400 text-indigo-600;
}

.module-item-type-qa .module-item-number {
  @apply border-yellow-400 text-yellow-600;
}

.module-item-active .module-item-number {
  @apply bg-white scale-110 shadow-lg;
}

.module-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  @apply bg-white border border-gray-200 rounded-lg;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.module-item-active .module-item-icon {
  @apply bg-white scale-110;
  border-color: transparent;
}

.icon-text {
  @apply text-gray-600;
}

.icon-video {
  @apply text-blue-600;
}

.icon-activity {
  @apply text-purple-600;
}

.icon-code {
  @apply text-green-600;
}

.icon-flowchart {
  @apply text-indigo-600;
}

.icon-qa {
  @apply text-yellow-600;
}

.module-item-active .module-item-icon {
  @apply text-white;
}

.module-item-content {
  flex: 1;
  min-width: 0;
  padding-right: 8px; /* 额外预留一点空间 */
  overflow: hidden; /* 确保文字不会溢出 */
}

.module-item-title {
  font-size: 14px;
  font-weight: 600;
  @apply text-gray-800;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  transition: all 0.3s ease;
  max-width: 100%; /* 确保不超过容器 */
}

.module-item-subtitle {
  font-size: 12px;
  @apply text-gray-500;
  transition: all 0.3s ease;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%; /* 确保不超过容器 */
}

.module-item-active .module-item-title,
.module-item-active .module-item-subtitle {
  @apply text-white font-semibold;
}


.module-item-activity-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  padding: 4px 8px;
  @apply bg-purple-500 text-white rounded-full;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
  animation: pulse-badge 2s infinite;
}

/* 复选框样式 */
.module-item-checkbox {
  @apply absolute bottom-3 right-3 z-10;
  @apply bg-white rounded-lg shadow-md p-1.5;
  transition: all 0.3s ease;
  min-width: 32px;
  min-height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  /* 确保复选框不会遮挡内容 */
  pointer-events: auto;
}

.module-item-checkbox:hover {
  @apply shadow-lg scale-110;
  @apply bg-gray-50;
}

.checkbox-input {
  @apply w-6 h-6 cursor-pointer;
  @apply border-2 border-gray-400 rounded;
  @apply focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.module-item-type-video .checkbox-input:checked {
  accent-color: #3b82f6;
}

.module-item-type-activity .checkbox-input:checked {
  accent-color: #a855f7;
}

.module-item-type-code .checkbox-input:checked {
  accent-color: #22c55e;
}

.module-item-type-flowchart .checkbox-input:checked {
  accent-color: #6366f1;
}

.module-item-type-qa .checkbox-input:checked {
  accent-color: #eab308;
}

.checkbox-input:disabled {
  @apply cursor-not-allowed opacity-50;
}

@keyframes pulse-badge {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.module-empty {
  text-align: center;
  padding: 40px 20px;
  @apply text-gray-500;
}

/* 中间：课堂监控 */
/* 监控模块样式已在上面定义 */

.monitoring-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.student-indicators {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  @apply bg-gray-50 border border-gray-200 rounded-lg;
  transition: all 0.2s ease;
}

.indicator-item:hover {
  @apply bg-gray-100 border-gray-300;
}

.indicator-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  @apply border-2 border-gray-300;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.indicator-student-info {
  flex: 1;
  min-width: 0;
}

.indicator-student-name {
  @apply text-sm font-medium text-gray-900;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.indicator-student-account {
  @apply text-xs text-gray-500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.indicator-student-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  width: 100%;
}

.indicator-progress-bar {
  flex: 1;
  height: 4px;
  @apply bg-gray-200 rounded-full overflow-hidden;
}

.indicator-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.indicator-progress-fill.indicator-green {
  @apply bg-green-500;
}

.indicator-progress-fill.indicator-yellow {
  @apply bg-yellow-500;
}

.indicator-progress-fill.indicator-red {
  @apply bg-red-500;
}

.indicator-progress-text {
  @apply text-xs text-gray-600 font-medium;
  min-width: 35px;
  text-align: right;
}

.indicator-empty-text {
  @apply text-gray-400;
}

.indicator-item.student-behind {
  @apply bg-orange-50 border-orange-200;
}

.indicator-green {
  @apply bg-green-500 border-green-600;
}

.indicator-yellow {
  @apply bg-yellow-500 border-yellow-600;
}

.indicator-red {
  @apply bg-red-500 border-red-600;
}

.indicator-empty {
  @apply bg-gray-200 border-gray-300;
  opacity: 0.5;
}

/* 学生列表样式 */
.student-list-extra {
  margin-top: 16px;
  margin-bottom: 16px;
  @apply border-t border-gray-200 pt-4;
}

.student-list-header {
  margin-bottom: 12px;
}

.student-list-title {
  @apply text-sm font-semibold text-gray-700;
}

.student-list-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 4px;
}

.student-list-content::-webkit-scrollbar {
  width: 4px;
}

.student-list-content::-webkit-scrollbar-track {
  @apply bg-gray-100;
  border-radius: 2px;
}

.student-list-content::-webkit-scrollbar-thumb {
  @apply bg-gray-300;
  border-radius: 2px;
}

.student-list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  @apply bg-gray-50 border border-gray-200 rounded-lg;
  transition: all 0.2s ease;
}

.student-list-item:hover {
  @apply bg-gray-100 border-gray-300;
}

.student-list-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.student-list-item.indicator-green .student-list-indicator {
  @apply bg-green-500;
}

.student-list-item.indicator-yellow .student-list-indicator {
  @apply bg-yellow-500;
}

.student-list-item.indicator-red .student-list-indicator {
  @apply bg-red-500;
}

.student-list-info {
  flex: 1;
  min-width: 0;
}

.student-list-name {
  @apply text-sm font-medium text-gray-900;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list-account {
  @apply text-xs text-gray-500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list-progress {
  @apply text-xs font-semibold text-gray-600;
  flex-shrink: 0;
  min-width: 40px;
  text-align: right;
}

.student-progress-bar-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 120px;
}

.student-progress-bar {
  flex: 1;
  height: 6px;
  @apply bg-gray-200 rounded-full overflow-hidden;
}

.student-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 4px;
}

.student-progress-fill.indicator-green {
  @apply bg-green-500;
}

.student-progress-fill.indicator-yellow {
  @apply bg-yellow-500;
}

.student-progress-fill.indicator-red {
  @apply bg-red-500;
}

.student-list-item.student-behind {
  @apply bg-orange-50 border-orange-300;
}

.students-behind-section {
  margin-top: 16px;
  margin-bottom: 16px;
  @apply border-t border-orange-200 pt-4;
}

.students-behind-section .student-list-header {
  @apply mb-3;
}

.students-behind-section .student-list-title {
  @apply text-orange-700 font-semibold;
}

.student-list-empty {
  margin-top: 16px;
  margin-bottom: 16px;
  text-align: center;
  padding: 20px;
  @apply text-gray-500 text-sm;
  @apply border-t border-gray-200 pt-4;
}

.monitoring-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  @apply border-t border-gray-200 pt-4;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  @apply border-b border-gray-200;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  @apply text-gray-600;
  font-size: 14px;
}

.stat-value {
  @apply text-gray-900;
  font-size: 18px;
  font-weight: 600;
}

/* 实时数据样式已合并到监控模块中 */

.data-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  @apply bg-white border border-gray-200 rounded-lg;
  @apply text-gray-600;
  flex-shrink: 0;
}

.data-icon-red {
  @apply text-red-600;
}

.data-icon-green {
  @apply text-green-600;
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.data-label {
  @apply text-gray-600;
  font-size: 12px;
}

.data-value {
  @apply text-gray-900;
  font-size: 18px;
  font-weight: 600;
}

.progress-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.progress-item {
  height: 8px;
  @apply bg-gray-200;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-purple {
  background: linear-gradient(90deg, #a855f7 0%, #9333ea 100%);
}

.progress-lavender {
  background: linear-gradient(90deg, #c084fc 0%, #a855f7 100%);
}

.progress-green {
  background: linear-gradient(90deg, #22c55e 0%, #16a34a 100%);
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700;
}

.btn-secondary:hover:not(:disabled) {
  @apply bg-gray-200;
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

/* 活动统计面板样式 */
.activity-panel {
  margin-top: 24px;
  @apply bg-white rounded-lg border border-gray-200 p-6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .panel {
    padding: 20px;
  }
  
  .teaching-modules {
    height: auto;
    min-height: 400px;
    max-height: 600px;
  }
}

@media (max-width: 768px) {
  .panel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .header-controls {
    width: 100%;
    flex-wrap: wrap;
  }
  
  .module-buttons {
    gap: 12px;
  }
  
  .module-btn {
    padding: 16px;
  }
  
  .student-indicators {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }
  
  .indicator-circle {
    width: 40px;
    height: 40px;
  }
}

.session-status-bar {
  @apply rounded-lg p-5 border-2 shadow-sm;
}

.session-status-bar.status-active {
  @apply bg-green-50 border-green-300;
}

.session-status-bar.status-paused {
  @apply bg-yellow-50 border-yellow-300;
}

.session-status-bar.status-pending {
  @apply bg-gray-50 border-gray-300;
}

.status-content {
  @apply flex items-center gap-5;
}

.status-indicator {
  @apply flex items-center justify-center w-12 h-12 rounded-full;
}

.pulse-dot {
  @apply w-4 h-4 bg-green-600 rounded-full animate-pulse;
}

.status-text {
  @apply flex-1 flex flex-col gap-1.5;
}

.status-title {
  @apply text-lg font-semibold text-gray-900 leading-tight;
}

.duration {
  @apply flex items-center gap-2 text-sm;
}

.duration-label {
  @apply text-gray-600;
}

.duration-value {
  @apply font-mono font-semibold text-gray-900 text-base;
}

.duration-value.duration-warning {
  @apply text-orange-600;
}

.duration-value.duration-danger {
  @apply text-red-600 animate-pulse;
}

.control-actions {
  @apply flex gap-3;
}

.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}

.btn-secondary {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.btn-danger {
  @apply bg-red-600 text-white hover:bg-red-700;
}

.btn-display-mode {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300;
  @apply flex items-center justify-center gap-1;
}

.btn-display-mode.active {
  @apply bg-blue-100 text-blue-700 border-blue-400;
}

.btn-fullscreen {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300;
  @apply flex items-center justify-center gap-1;
}

.btn-fullscreen:hover {
  @apply bg-gray-200;
}

.display-mode-controls {
  @apply flex items-center;
}

.btn-lg {
  @apply px-6 py-3 text-lg;
}

.btn-sm {
  @apply px-3 py-1 text-sm;
}

.students-panel,
.content-control {
  @apply border border-gray-200 rounded-lg p-4;
}

.panel-header {
  @apply flex items-center justify-between mb-4 pb-2 border-b border-gray-200;
}

.panel-header h4 {
  @apply text-lg font-semibold text-gray-900;
}

.panel-stats {
  @apply flex items-center gap-3;
}

.stat-badge {
  @apply flex items-center gap-1.5 px-2.5 py-1 bg-gray-100 rounded-md text-sm;
}

.stat-label {
  @apply text-gray-600;
}

.stat-value {
  @apply font-semibold text-gray-900;
}

.loading-state {
  @apply flex flex-col items-center justify-center py-8;
}

.spinner {
  @apply w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-2;
}

.students-grid {
  @apply grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3;
}

.student-card {
  @apply flex items-center gap-3 p-3 border border-gray-200 rounded-lg bg-white hover:shadow-md transition-shadow;
}

.student-card.at-current-cell {
  @apply border-blue-400 bg-blue-50;
}

.student-avatar {
  @apply w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-semibold;
}

.student-info {
  @apply flex-1 min-w-0;
}

.student-name {
  @apply text-sm font-medium text-gray-900 truncate;
}

.student-progress {
  @apply flex items-center gap-2 mt-1;
}

.progress-bar-mini {
  @apply flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden;
}

.progress-fill {
  @apply h-full bg-blue-500 transition-all duration-300;
}

.progress-text {
  @apply text-xs text-gray-600 whitespace-nowrap;
}

.sync-indicator {
  @apply text-green-600 font-bold;
}

.empty-students {
  @apply text-center py-8 text-gray-500;
}

.waiting-students-panel {
  @apply bg-blue-50 border-2 border-blue-200 rounded-lg p-6 space-y-4;
}

.waiting-header {
  @apply flex items-start gap-4;
}

.waiting-icon {
  @apply text-4xl;
}

.waiting-content {
  @apply flex-1;
}

.waiting-title {
  @apply text-xl font-bold text-gray-900 mb-1;
}

.waiting-subtitle {
  @apply text-sm text-gray-600;
}

.waiting-stats {
  @apply flex items-center gap-6 pt-4 border-t border-blue-200;
}

.stat-item {
  @apply flex items-center gap-2;
}

.stat-label {
  @apply text-sm text-gray-600;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}

.stat-value.highlight {
  @apply text-blue-600 text-2xl;
}

.content-control {
  @apply space-y-4;
}

.control-board-preview {
  @apply bg-white rounded-lg border border-gray-200 p-6;
}

.control-board-preview .board-header {
  @apply flex items-center justify-between mb-6 pb-4 border-b border-gray-200;
}

.control-board-preview .board-title {
  @apply text-lg font-semibold text-gray-900;
}

.control-board-preview .board-stats {
  @apply flex items-center gap-4 text-sm text-gray-600;
}

.control-board-preview .stat-item {
  @apply px-2 py-1 bg-gray-100 rounded;
}

.control-board-preview .control-chain {
  @apply flex items-center;
  overflow-x: auto;
  padding: 1rem 0;
}

.control-board-preview .chain-node {
  @apply flex flex-col items-center justify-center relative;
  @apply min-w-[80px] w-[80px] p-3 rounded-lg;
  @apply bg-gray-50 border-2 border-gray-200;
  flex-shrink: 0;
}

.chain-node-preview {
  @apply opacity-60 cursor-default;
  pointer-events: none;
}

.control-board-preview .node-number {
  @apply absolute -top-2 -left-2 w-6 h-6 bg-gray-600 text-white rounded-full;
  @apply flex items-center justify-center text-xs font-bold;
}

.control-board-preview .node-icon {
  @apply w-10 h-10 flex items-center justify-center;
  @apply text-gray-600 mb-2;
}

.control-board-preview .node-label {
  @apply text-xs text-center text-gray-700 font-medium;
  @apply line-clamp-2;
  max-width: 100%;
}

.control-board-preview .chain-connector {
  @apply flex-shrink-0;
  width: 2rem;
  height: 2px;
  background: linear-gradient(to right, #e5e7eb, #9ca3af);
  margin: 0 0.5rem;
}

.current-cell-info {
  @apply mt-4 p-3 bg-gray-50 rounded-lg;
}

.cell-header {
  @apply flex items-center gap-2 mb-2;
}

.cell-type-badge {
  @apply px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded;
}

.cell-title {
  @apply text-sm font-medium text-gray-900;
}

.activity-control {
  @apply mt-3;
}

/* 响应式布局 */
@media (max-width: 1600px) {
  .main-layout {
    grid-template-columns: 1.8fr 1.3fr 1.8fr;
  }
}

@media (max-width: 1400px) {
  .main-layout {
    grid-template-columns: 1.5fr 1.2fr 1.5fr;
  }
  
  .stats-grid-compact {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .student-preview-panel,
  .monitoring-module {
    height: auto;
    max-height: 600px;
  }
  
  .monitoring-module-content {
    max-height: 500px;
  }
}

@media (max-width: 768px) {
  .top-control-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .student-indicators {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-grid-compact {
    grid-template-columns: 1fr;
  }
}

</style>

