<template>
  <div class="district-admin-dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1>考试管理</h1>
        <p class="subtitle">区县考试管理员工作台</p>
      </div>
      <div class="current-semester">
        <el-tag v-if="currentSemester" type="success" size="large">
          {{ currentSemester.name }}
        </el-tag>
        <el-tag v-else type="info" size="large">未设置当前学期</el-tag>
      </div>
    </div>

    <!-- 快速入口 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
      <!-- 快速创建考试 -->
      <div class="quick-action-card" @click="openQuickExamDialog">
        <el-card shadow="hover">
          <div class="card-content">
            <div class="card-icon">
              <el-icon :size="48" color="#409EFF"><Document /></el-icon>
            </div>
            <div class="card-info">
              <h3>快速创建考试</h3>
              <p class="description">3步完成考试创建，自动获取学生信息</p>
              <div class="steps">
                <span class="step">1.选择</span>
                <span class="arrow">→</span>
                <span class="step">2.设置</span>
                <span class="arrow">→</span>
                <span class="step">3.完成</span>
              </div>
            </div>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>

      <!-- 批量导入 -->
      <div class="quick-action-card" @click="openBatchImportDialog">
        <el-card shadow="hover">
          <div class="card-content">
            <div class="card-icon">
              <el-icon :size="48" color="#67C23A"><Upload /></el-icon>
            </div>
            <div class="card-info">
              <h3>批量导入成绩</h3>
              <p class="description">支持Excel批量导入多个学校成绩</p>
              <div class="feature-tags">
                <el-tag size="small" type="success">高效</el-tag>
                <el-tag size="small" type="info">模板化</el-tag>
              </div>
            </div>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>

      <!-- 考试模板 -->
      <div class="quick-action-card" @click="openExamTemplateDialog">
        <el-card shadow="hover">
          <div class="card-content">
            <div class="card-icon">
              <el-icon :size="48" color="#E6A23C"><CopyDocument /></el-icon>
            </div>
            <div class="card-info">
              <h3>使用考试模板</h3>
              <p class="description">从历史考试快速创建新考试</p>
              <div class="stats">
                <span class="stat-item">{{ examTemplates }} 个模板</span>
              </div>
            </div>
          </div>
          <div class="card-arrow">
            <el-icon><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 考试工作流指南 -->
    <el-card class="workflow-guide-section" shadow="never">
      <template #header>
        <div class="workflow-header">
          <h2>📋 考试组织流程</h2>
          <p class="workflow-subtitle">根据您的角色选择合适的流程</p>
        </div>
      </template>

      <!-- 流程选项卡 -->
      <el-tabs v-model="activeWorkflowTab" type="border-card">
        <!-- 区县管理员流程 -->
        <el-tab-pane label="区县管理员" name="district">
          <div class="workflow-content">
            <div class="workflow-steps">
              <el-steps :active="districtWorkflowStep" finish-status="success" align-center>
                <el-step title="创建考试" description="设置考试基本信息和参与学校" />
                <el-step title="分配考号" description="为考生分配考号（可选）" />
                <el-step title="导入成绩" description="批量导入各学校考试成绩" />
                <el-step title="生成报告" description="自动生成评价报告" />
              </el-steps>
            </div>
            <div class="workflow-description">
              <h4>📝 操作说明</h4>
              <ul class="instruction-list">
                <li><strong>创建考试：</strong>设置考试名称、类型、日期、参与学校</li>
                <li><strong>分配考号：</strong>系统自动或手动为考生分配考号（可选）</li>
                <li><strong>导入成绩：</strong>下载Excel模板，填写成绩后批量导入</li>
                <li><strong>生成报告：</strong>系统自动生成增值评价报告和对比分析</li>
              </ul>
            </div>
            <div class="workflow-actions">
              <el-button type="primary" size="large" @click="startDistrictWorkflow">
                <el-icon><Plus /></el-icon>
                <span style="margin-left: 8px;">开始创建考试</span>
              </el-button>
            </div>
          </div>
        </el-tab-pane>

        <!-- 学校管理员流程 -->
        <el-tab-pane label="学校管理员" name="school">
          <div class="workflow-content">
            <div class="workflow-steps">
              <el-steps :active="schoolWorkflowStep" finish-status="success" align-center>
                <el-step title="选择班级" description="选择参与考试的年级和班级" />
                <el-step title="设置科目" description="设置考试科目和分值" />
                <el-step title="确认学生" description="系统自动获取班级学生名单" />
                <el-step title="录入成绩" description="在线录入或导入成绩" />
              </el-steps>
            </div>
            <div class="workflow-description">
              <h4>📝 操作说明</h4>
              <ul class="instruction-list">
                <li><strong>选择班级：</strong>选择参与考试的年级和班级，可多选</li>
                <li><strong>设置科目：</strong>设置考试科目、满分值、考试时长</li>
                <li><strong>确认学生：</strong>系统自动获取选定班级的学生信息</li>
                <li><strong>录入成绩：</strong>在线录入、Excel导入、或批量上传</li>
              </ul>
            </div>
            <div class="workflow-actions">
              <el-button type="primary" size="large" @click="startSchoolWorkflow">
                <el-icon><Plus /></el-icon>
                <span style="margin-left: 8px;">开始组织考试</span>
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 考试列表和状态 -->
    <el-card class="exam-list-section" shadow="never" style="margin-top: 20px;">
      <template #header>
        <div class="section-header">
          <h3>📊 考试列表</h3>
          <el-button size="small" @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="exams" v-loading="loading" stripe>
        <el-table-column prop="name" label="考试名称" width="200" />
        <el-table-column prop="exam_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ getExamTypeName(row.exam_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_level" label="级别" width="90">
          <template #default="{ row }">
            <el-tag :type="getExamLevelType(row.exam_level)" size="small">
              {{ getExamLevelName(row.exam_level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="考试日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusName(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数据准备进度" width="200">
          <template #default="{ row }">
            <div class="progress-info">
              <el-progress
                :percentage="getExamProgress(row)"
                :status="getExamProgressStatus(row)"
                :stroke-width="8"
                :show-text="false"
              />
              <div class="progress-steps">
                <el-tag
                  :type="row.hasStudents ? 'success' : 'info'"
                  size="small"
                  style="margin-right: 8px;"
                >
                  {{ row.hasStudents ? '✓' : '○' }} 考生信息
                </el-tag>
                <el-tag
                  :type="row.hasScores ? 'success' : 'info'"
                  size="small"
                >
                  {{ row.hasScores ? '✓' : '○' }} 成绩数据
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="importStudentsForExam(row)">
              <el-icon><User /></el-icon>
              导入考生
            </el-button>
            <el-button size="small" link @click="importScoresForExam(row)">
              <el-icon><Upload /></el-icon>
              导入成绩
            </el-button>
            <el-button size="small" link type="danger" @click="deleteExam(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 其他功能区域 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 学期管理 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openSemesterDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#409eff">
              <component :is="'Calendar'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学期管理</h3>
            <p>创建和管理学期</p>
            <div class="card-stats">
              <span>{{ semesters.length }} 个学期</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 评价报告 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openEvaluationDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'DataAnalysis'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>评价报告</h3>
            <p>生成增值评价报告</p>
            <div class="card-stats">
              <span>{{ evaluations.length }} 个评价</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 学期表现 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="openPerformanceDialog">
          <div class="card-icon">
            <el-icon :size="40" color="#909399">
              <component :is="'TrendCharts'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>学期表现</h3>
            <p>查看学期统计</p>
            <div class="card-stats">
              <span>数据分析</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 导入任务 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="function-card" shadow="hover" @click="viewImportTasks">
          <div class="card-icon">
            <el-icon :size="40" color="#e6a23c">
              <component :is="'List'" />
            </el-icon>
          </div>
          <div class="card-content">
            <h3>导入任务</h3>
            <p>查看导入历史</p>
            <div class="card-stats">
              <span>{{ importTasks.length }} 个任务</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学期管理对话框 -->
    <el-dialog
      v-model="semesterDialogVisible"
      title="学期管理"
      width="900px"
      @close="resetSemesterForm"
    >
      <!-- 快速创建学期表单 -->
      <div class="quick-create-section">
        <h4>快速创建学期</h4>
        <el-form :model="semesterForm" :rules="semesterRules" ref="semesterFormRef" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学年" prop="year">
                <el-input
                  v-model="semesterForm.year"
                  placeholder="请输入学年，格式：2023-2024"
                  maxlength="9"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学期类型" prop="semester_type">
                <el-radio-group v-model="semesterForm.semester_type">
                  <el-radio value="up">上学期</el-radio>
                  <el-radio value="down">下学期</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期" prop="start_date">
                <el-date-picker
                  v-model="semesterForm.start_date"
                  type="date"
                  placeholder="开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期" prop="end_date">
                <el-date-picker
                  v-model="semesterForm.end_date"
                  type="date"
                  placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="学期名称" prop="name">
            <el-input v-model="semesterForm.name" placeholder="自动生成或手动输入">
              <template #append>
                <el-button @click="generateSemesterName">自动生成</el-button>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="createSemester" :loading="semesterSubmitting">
              创建学期
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 学期列表 -->
      <div class="semester-list-section">
        <h4>学期列表</h4>
        <el-table :data="semesters" max-height="300" size="small">
          <el-table-column prop="name" label="名称" width="180" />
          <el-table-column prop="year" label="学年" width="80" />
          <el-table-column prop="semester_type" label="类型" width="80">
            <template #default="{ row }">
              {{ row.semester_type === 'up' ? '上' : '下' }}
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始" width="110" />
          <el-table-column prop="end_date" label="结束" width="110" />
          <el-table-column prop="is_current" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_current ? 'success' : 'info'" size="small">
                {{ row.is_current ? '当前' : '非当前' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button
                v-if="!row.is_current"
                size="small"
                type="success"
                link
                @click.stop="setCurrentSemester(row)"
              >
                设为当前
              </el-button>
              <el-button size="small" link @click.stop="deleteSemester(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 考试管理对话框 -->
    <el-dialog
      v-model="examDialogVisible"
      title="考试管理"
      width="1000px"
      @close="resetExamForm"
    >
      <!-- 快速创建考试表单 -->
      <div class="quick-create-section">
        <h4>快速创建考试</h4>
        <el-form :model="examForm" :rules="examRules" ref="examFormRef" label-width="100px">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="考试名称" prop="name">
                <el-input v-model="examForm.name" placeholder="请输入考试名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="考试类型" prop="exam_type">
                <el-select v-model="examForm.exam_type" placeholder="选择类型" style="width: 100%;">
                  <el-option label="期中考试" value="midterm" />
                  <el-option label="期末考试" value="final" />
                  <el-option label="月考" value="monthly" />
                  <el-option label="模考" value="mock" />
                  <el-option label="统考" value="unified" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="学期" prop="semester_id">
                <el-select v-model="examForm.semester_id" placeholder="选择学期" style="width: 100%;">
                  <el-option
                    v-for="semester in semesters"
                    :key="semester.id"
                    :label="semester.name"
                    :value="semester.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="年级" prop="grade_id">
                <el-select v-model="examForm.grade_id" placeholder="选择年级" clearable style="width: 100%;">
                  <el-option
                    v-for="grade in grades"
                    :key="grade.id"
                    :label="grade.name"
                    :value="grade.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="考试日期" prop="exam_date">
                <el-date-picker
                  v-model="examForm.exam_date"
                  type="date"
                  placeholder="选择日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item>
            <el-button type="primary" @click="createExam" :loading="examSubmitting">
              创建考试
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-divider />

      <!-- 考试列表 -->
      <div class="exam-list-section">
        <h4>考试列表</h4>
        <el-table :data="exams" max-height="300" size="small">
          <el-table-column prop="name" label="考试名称" width="180" />
          <el-table-column prop="exam_type" label="类型" width="90">
            <template #default="{ row }">
              <el-tag size="small">{{ getExamTypeName(row.exam_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="exam_level" label="级别" width="80">
            <template #default="{ row }">
              <el-tag :type="getExamLevelType(row.exam_level)" size="small">
                {{ getExamLevelName(row.exam_level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">
                {{ getStatusName(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="exam_date" label="日期" width="110" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" link @click.stop="deleteExam(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 导入考生信息对话框 -->
    <el-dialog
      v-model="studentImportDialogVisible"
      title="导入考生信息"
      width="600px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="考生信息导入功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>批量导入考生基本资料</li>
          <li>Excel模板下载</li>
          <li>数据验证和错误提示</li>
          <li>导入进度显示</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 导入成绩对话框 -->
    <el-dialog
      v-model="scoreImportDialogVisible"
      title="导入成绩"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="成绩导入功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>Excel成绩单上传</li>
          <li>自动关联考试和科目</li>
          <li>数据验证和查重</li>
          <li>实时导入进度</li>
          <li>错误报告下载</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 评价报告对话框 -->
    <el-dialog
      v-model="evaluationDialogVisible"
      title="评价报告"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="评价报告功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>基线考试与结束考试对比</li>
          <li>增值评价自动计算</li>
          <li>多维度数据分析</li>
          <li>可视化图表展示</li>
          <li>报告导出</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 学期表现对话框 -->
    <el-dialog
      v-model="performanceDialogVisible"
      title="学期表现"
      width="700px"
    >
      <el-alert
        title="功能开发中"
        type="info"
        description="学期表现功能正在开发中，敬请期待。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <p>此功能将支持：</p>
        <ul>
          <li>学期整体表现统计</li>
          <li>各学科成绩分析</li>
          <li>进步趋势展示</li>
          <li>优秀率/合格率对比</li>
          <li>数据可视化图表</li>
        </ul>
      </div>
    </el-dialog>

    <!-- 学校端快速创建考试对话框 -->
    <el-dialog
      v-model="schoolQuickExamDialogVisible"
      title="快速组织考试"
      width="900px"
      @close="closeSchoolQuickExamDialog"
    >
      <!-- 步骤条 -->
      <el-steps :active="schoolExamStep" align-center style="margin-bottom: 30px;">
        <el-step title="选择班级" description="选择参与考试的班级" />
        <el-step title="设置科目" description="设置考试科目和分值" />
        <el-step title="确认学生" description="系统自动获取学生名单" />
        <el-step title="完成" description="创建成功" />
      </el-steps>

      <!-- 步骤1: 选择班级（区县管理员） -->
      <div v-show="schoolExamStep === 0 && isDistrictAdmin" class="step-content">
        <h4>🏛️ 区县管理员 - 创建统考</h4>
        <el-form :model="schoolExamForm" label-width="100px">
          <el-form-item label="考试名称">
            <el-input v-model="schoolExamForm.name" placeholder="例如：2024年春季期末统考" />
          </el-form-item>
          <el-form-item label="考试级别">
            <el-select v-model="schoolExamForm.exam_level" placeholder="选择考试级别" style="width: 100%;">
              <el-option label="校级考试" value="school">
                <span>校级考试</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">本校考试，使用班级选择</span>
              </el-option>
              <el-option label="区县统考" value="district">
                <span>区县统考</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">区县统一考试，选择区县和学校</span>
              </el-option>
              <el-option label="市级考试" value="city">
                <span>市级考试</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">市级统一考试，需导入市级考号</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="schoolExamForm.exam_level === 'district' || schoolExamForm.exam_level === 'city'"
            label="选择区县"
          >
            <el-select
              v-model="schoolExamForm.region_id"
              placeholder="请选择区县"
              style="width: 100%;"
              filterable
              @change="onRegionChange"
            >
              <el-option
                v-for="region in availableRegions"
                :key="region.id"
                :label="region.name"
                :value="region.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="schoolExamForm.exam_level === 'district' || schoolExamForm.exam_level === 'city'"
            label="选择学段"
          >
            <el-select
              v-model="schoolExamForm.study_level"
              placeholder="请先选择区县"
              style="width: 100%;"
              :disabled="!schoolExamForm.region_id"
              @change="onStudyLevelChange"
            >
              <el-option
                v-for="studyLevel in availableStudyLevels"
                :key="studyLevel"
                :label="studyLevel"
                :value="studyLevel"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="schoolExamForm.exam_level === 'district' || schoolExamForm.exam_level === 'city'"
            label="选择年级"
          >
            <el-select
              v-model="schoolExamForm.grade_id"
              placeholder="请先选择学段"
              style="width: 100%;"
              :disabled="!schoolExamForm.study_level"
              @change="onGradeChange"
            >
              <el-option
                v-for="grade in filteredGrades"
                :key="grade.id"
                :label="grade.name"
                :value="grade.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="schoolExamForm.exam_level === 'district' || schoolExamForm.exam_level === 'city'"
            label="选择学校"
          >
            <el-select
              v-model="schoolExamForm.school_ids"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="请先选择年级，可多选学校"
              style="width: 100%;"
              :disabled="!schoolExamForm.grade_id"
              @change="onSchoolsChange"
            >
              <el-option
                v-if="filteredSchools.length > 0"
                label="全选"
                :value="'all'"
                @click="selectAllSchools"
              />
              <el-option
                v-for="school in filteredSchools"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              />
            </el-select>
            <div v-if="schoolExamForm.grade_id && filteredSchools.length > 0" style="margin-top: 8px;">
              <el-link type="primary" @click="selectAllSchools" style="font-size: 13px;">
                全选{{ filteredSchools.length }}所学校
              </el-link>
              <el-divider direction="vertical" />
              <el-link type="info" @click="schoolExamForm.school_ids = []" style="font-size: 13px;">
                清空选择
              </el-link>
            </div>
          </el-form-item>
          <el-form-item label="选择学期">
            <el-select
              v-model="schoolExamForm.semester_id"
              placeholder="请选择学期"
              style="width: 100%;"
            >
              <el-option
                v-for="semester in semesters"
                :key="semester.id"
                :label="semester.name"
                :value="semester.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker
              v-model="schoolExamForm.exam_date"
              type="date"
              placeholder="选择考试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
        <div class="step-info">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              <span v-if="schoolExamForm.school_ids.length > 0">
                已选择 <strong>{{ schoolExamForm.school_ids.length }}</strong> 所学校参与统考
              </span>
              <span v-else>请按顺序选择：区县 → 学校（可多选）→ 年级</span>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤1: 选择班级（学校管理员） -->
      <div v-show="schoolExamStep === 0 && isSchoolAdmin" class="step-content">
        <h4>🏫 学校管理员 - 组织考试</h4>
        <el-form :model="schoolExamForm" label-width="120px">
          <el-form-item label="考试名称">
            <el-input v-model="schoolExamForm.name" placeholder="例如：2024年春季期末考试" />
          </el-form-item>
          <el-form-item label="考试级别">
            <el-select v-model="schoolExamForm.exam_level" placeholder="选择考试级别" style="width: 100%;">
              <el-option label="校级考试" value="school">
                <span>校级考试</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">本校考试，使用班级选择</span>
              </el-option>
              <el-option label="区县统考" value="district">
                <span>区县统考</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">区县统一考试，选择区县和学校</span>
              </el-option>
              <el-option label="市级考试" value="city">
                <span>市级考试</span>
                <span style="font-size: 12px; color: #999; margin-left: 8px;">市级统一考试，需导入市级考号</span>
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="所属学校">
            <el-input :value="currentUser?.school_name" disabled style="width: 100%;" />
            <div style="margin-top: 8px;">
              <el-checkbox v-model="schoolExamForm.isJointExam" @change="onJointExamChange">
                联考模式（邀请其他学校参与）
              </el-checkbox>
            </div>
          </el-form-item>
          <el-form-item v-if="schoolExamForm.isJointExam" label="参与学校">
            <el-select
              v-model="schoolExamForm.additional_school_ids"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="选择参与联考的其他学校"
              style="width: 100%;"
            >
              <el-option
                v-for="school in availableSchools.filter(s => s.id !== currentUser?.school_id)"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              />
            </el-select>
            <div style="margin-top: 8px; color: #909399; font-size: 13px;">
              <el-icon><InfoFilled /></el-icon>
              已自动包含本校：{{ currentUser?.school_name }}
            </div>
          </el-form-item>
          <el-form-item label="选择年级">
            <el-select
              v-model="schoolExamForm.grade_id"
              placeholder="请选择年级"
              style="width: 100%;"
              @change="onGradeChange"
            >
              <el-option
                v-for="grade in availableGrades"
                :key="grade.id"
                :label="grade.name"
                :value="grade.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="schoolExamForm.exam_level === 'school'"
            label="选择班级"
          >
            <el-select
              v-model="schoolExamForm.class_ids"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="请先选择年级"
              style="width: 100%;"
              :disabled="!schoolExamForm.grade_id"
            >
              <el-option
                v-if="availableClassrooms.length > 0"
                label="全选"
                :value="'all'"
                @click="selectAllClasses"
              />
              <el-option
                v-for="classroom in availableClassrooms"
                :key="classroom.id"
                :label="classroom.name"
                :value="classroom.id"
              />
            </el-select>
            <div v-if="schoolExamForm.grade_id && availableClassrooms.length > 0" style="margin-top: 8px;">
              <el-link type="primary" @click="selectAllClasses" style="font-size: 13px;">
                全选{{ availableClassrooms.length }}个班级
              </el-link>
              <el-divider direction="vertical" />
              <el-link type="info" @click="schoolExamForm.class_ids = []" style="font-size: 13px;">
                清空选择
              </el-link>
            </div>
          </el-form-item>
          <el-form-item label="选择学期">
            <el-select
              v-model="schoolExamForm.semester_id"
              placeholder="请选择学期"
              style="width: 100%;"
            >
              <el-option
                v-for="semester in semesters"
                :key="semester.id"
                :label="semester.name"
                :value="semester.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker
              v-model="schoolExamForm.exam_date"
              type="date"
              placeholder="选择考试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
        <div class="step-info">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              <span v-if="schoolExamForm.class_ids.length > 0">
                已选择 <strong>{{ schoolExamForm.class_ids.length }}</strong> 个班级，
                预计约 <strong>{{ estimatedStudentCount }}</strong> 名学生参与
              </span>
              <span v-else>请按顺序选择：年级 → 班级</span>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤1: 通用管理员（无角色特定限制） -->
      <div v-show="schoolExamStep === 0 && !isDistrictAdmin && !isSchoolAdmin" class="step-content">
        <h4>📚 选择参与考试的班级</h4>
        <el-form :model="schoolExamForm" label-width="100px">
          <el-form-item label="考试名称">
            <el-input v-model="schoolExamForm.name" placeholder="例如：2024年春季期末考试" />
          </el-form-item>
          <el-form-item label="选择学校">
            <el-select
              v-model="schoolExamForm.school_id"
              placeholder="请先选择学校"
              style="width: 100%;"
              filterable
              @change="onSchoolChange"
            >
              <el-option
                v-for="school in availableSchools"
                :key="school.id"
                :label="school.name"
                :value="school.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="选择年级">
            <el-select
              v-model="schoolExamForm.grade_id"
              placeholder="请先选择学校"
              style="width: 100%;"
              :disabled="!schoolExamForm.school_id"
              @change="onGradeChange"
            >
              <el-option
                v-for="grade in availableGrades"
                :key="grade.id"
                :label="grade.name"
                :value="grade.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="选择班级">
            <el-select
              v-model="schoolExamForm.class_ids"
              multiple
              collapse-tags
              collapse-tags-tooltip
              placeholder="请先选择学校和年级"
              style="width: 100%;"
              :disabled="!schoolExamForm.grade_id"
            >
              <el-option
                v-if="availableClassrooms.length > 0"
                label="全选"
                :value="'all'"
                @click="selectAllClasses"
              />
              <el-option
                v-for="classroom in availableClassrooms"
                :key="classroom.id"
                :label="classroom.name"
                :value="classroom.id"
              />
            </el-select>
            <div v-if="schoolExamForm.grade_id && availableClassrooms.length > 0" style="margin-top: 8px;">
              <el-link type="primary" @click="selectAllClasses" style="font-size: 13px;">
                全选{{ availableClassrooms.length }}个班级
              </el-link>
              <el-divider direction="vertical" />
              <el-link type="info" @click="schoolExamForm.class_ids = []" style="font-size: 13px;">
                清空选择
              </el-link>
            </div>
          </el-form-item>
          <el-form-item label="选择学期">
            <el-select
              v-model="schoolExamForm.semester_id"
              placeholder="请选择学期"
              style="width: 100%;"
            >
              <el-option
                v-for="semester in semesters"
                :key="semester.id"
                :label="semester.name"
                :value="semester.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="考试日期">
            <el-date-picker
              v-model="schoolExamForm.exam_date"
              type="date"
              placeholder="选择考试日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>
        <div class="step-info">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              <span v-if="schoolExamForm.class_ids.length > 0">
                已选择 <strong>{{ schoolExamForm.class_ids.length }}</strong> 个班级，
                预计约 <strong>{{ estimatedStudentCount }}</strong> 名学生参与
              </span>
              <span v-else>请按顺序选择：学校 → 年级 → 班级</span>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤2: 设置科目 -->
      <div v-show="schoolExamStep === 1" class="step-content">
        <h4>📝 选择考试科目</h4>
        <p style="color: #909399; margin-bottom: 16px;">
          请勾选本次考试的科目，并设置满分值
        </p>

        <el-table :data="availableSubjects" border stripe style="width: 100%;">
          <el-table-column width="60" align="center">
            <template #header>
              <el-checkbox
                v-model="selectAllSubjects"
                :indeterminate="isIndeterminateSubjects"
                @change="handleSelectAllSubjects"
              >
                全选
              </el-checkbox>
            </template>
            <template #default="{ row }">
              <el-checkbox
                v-model="row.selected"
                @change="updateSelectedSubjects"
              />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="科目名称" width="150" />
          <el-table-column prop="code" label="科目代码" width="120" />
          <el-table-column label="满分值" width="200">
            <template #default="{ row }">
              <el-input-number
                v-model="row.max_score"
                :min="1"
                :max="200"
                :disabled="!row.selected"
                placeholder="满分"
                style="width: 100%;"
                @change="updateTotalMaxScore"
              />
            </template>
          </el-table-column>
          <el-table-column prop="description" label="说明" show-overflow-tooltip />
        </el-table>

        <div class="step-info" style="margin-top: 20px;">
          <el-alert
            type="success"
            :closable="false"
            show-icon
          >
            <template #title>
              已选择 <strong>{{ selectedSubjectsCount }}</strong> 个科目，
              总分 <strong>{{ totalMaxScore }}</strong> 分
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤3: 考场安排 -->
      <div v-show="schoolExamStep === 2" class="step-content">
        <h4>🏫 考场安排</h4>

        <!-- 考场信息概览 -->
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 20px;"
        >
          <template #title>
            参考学生：<strong>{{ estimatedStudentCount }}</strong> 名
            预计考场数：<strong>{{ estimatedRoomsCount }}</strong> 个
          </template>
        </el-alert>

        <!-- 编排规则 -->
        <el-form :model="roomArrangementForm" label-width="140px" style="margin-bottom: 20px;">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="每个考场人数">
                <el-input-number
                  v-model="roomArrangementForm.capacityPerRoom"
                  :min="10"
                  :max="100"
                  :step="5"
                  @change="updateCanGoNext"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="编排方式">
                <el-radio-group v-model="roomArrangementForm.arrangementType">
                  <el-radio value="by_class">按班级</el-radio>
                  <el-radio value="mixed">混排</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="座位排列">
                <el-radio-group v-model="roomArrangementForm.seatPattern">
                  <el-radio value="s_shape">S型</el-radio>
                  <el-radio value="sequential">顺序</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="考场位置">
                <el-checkbox v-model="roomArrangementForm.useExistingRooms">
                  使用现有教室作为考场
                </el-checkbox>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <!-- 操作按钮 -->
        <div style="margin-bottom: 20px;">
          <el-button
            type="primary"
            size="large"
            @click="autoAssignExamRooms"
            :loading="arrangingRooms"
            :icon="MagicStick"
          >
            自动编排考场
          </el-button>
          <el-button
            v-if="examRooms.length > 0"
            @click="autoAssignProctors"
            :loading="assigningProctors"
          >
            分配监考教师
          </el-button>
          <el-button
            v-if="examRooms.length > 0"
            type="danger"
            @click="clearAllExamRooms"
          >
            清空考场
          </el-button>
        </div>

        <!-- 考场列表 -->
        <div v-if="examRooms.length > 0">
          <h5 style="margin-bottom: 10px;">考场列表</h5>
          <el-table :data="examRooms" border stripe>
            <el-table-column prop="name" label="考场" width="120" />
            <el-table-column label="容量" width="80">
              <template #default="{ row }">
                {{ row.seat_count }}/{{ row.capacity }}
              </template>
            </el-table-column>
            <el-table-column label="监考教师" width="200">
              <template #default="{ row }">
                {{ getProctorNames(row) }}
              </template>
            </el-table-column>
            <el-table-column label="考号范围" width="180">
              <template #default="{ row }">
                {{ row.exam_number_start }} - {{ row.exam_number_end }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="320">
              <template #default="{ row }">
                <el-button size="small" @click="viewRoomDetail(row)">详情</el-button>
                <el-button size="small" type="primary" @click="exportSeatingChart(row)">座位表</el-button>
                <el-button size="small" type="success" @click="exportExamTickets(row)">准考证</el-button>
                <el-button size="small" type="warning" @click="exportProctorHandbook(row)">监考手册</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 步骤4: 确认学生 -->
      <div v-show="schoolExamStep === 3" class="step-content">
        <h4>👥 确认学生名单</h4>
        <p style="color: #909399; margin-bottom: 16px;">
          系统已自动从选定班级获取学生名单，共 <strong>{{ confirmedStudents.length }}</strong> 名学生
        </p>

        <el-table :data="confirmedStudents" max-height="300" stripe border>
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="classroom" label="班级" width="150" />
          <el-table-column prop="student_code" label="学号" />
        </el-table>

        <div class="step-actions" style="margin-top: 20px;">
          <el-alert
            type="info"
            :closable="false"
            show-icon
          >
            <template #title>
              学生名单已自动获取，确认无误后点击"完成"创建考试
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 步骤4: 完成 -->
      <div v-show="schoolExamStep === 4" class="step-content">
        <el-result
          icon="success"
          title="考试创建成功！"
          sub-title="现在可以开始录入成绩了"
        >
          <template #extra>
            <el-space>
              <el-button type="primary" @click="goToScoreEntry">
                立即录入成绩
              </el-button>
              <el-button @click="closeSchoolQuickExamDialog">
                返回首页
              </el-button>
            </el-space>
          </template>
        </el-result>
      </div>

      <!-- 对话框底部按钮 -->
      <template #footer v-if="schoolExamStep < 4">
        <span class="dialog-footer">
          <el-button @click="prevStep" :disabled="schoolExamStep === 0">上一步</el-button>
          <el-button type="primary" @click="nextStep" :disabled="!canGoNext">
            {{ schoolExamStep === 3 ? '完成' : '下一步' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import {
  Document,
  ArrowRight,
  Upload,
  CopyDocument,
  Plus,
  User,
  Delete,
  Refresh,
  Calendar,
  DataAnalysis,
  TrendCharts,
  List,
  InfoFilled,
  MagicStick,
  Download
} from '@element-plus/icons-vue';
import { semesterApi, examApi } from '@/services/evaluation';
import { curriculumService } from '@/services/curriculum';
import { adminService } from '@/services/admin';  // 导入adminService
import { examRoomService } from '@/services/examRoom';  // 导入examRoomService
import { useUserStore } from '@/store/user';  // 导入userStore
import type { Semester, Exam, ExamRoom } from '@/types/evaluation';
import type { Grade } from '@/types/curriculum';

// 获取当前用户信息
const userStore = useUserStore();
const currentUser = computed(() => userStore.user);
const currentUserRole = computed(() => currentUser.value?.role?.toLowerCase());
const isDistrictAdmin = computed(() => currentUserRole.value === 'district_admin');
const isSchoolAdmin = computed(() => currentUserRole.value === 'school_admin');

// 扩展 Exam 类型以包含数据准备状态
interface ExamWithStatus extends Exam {
  hasStudents?: boolean;
  hasScores?: boolean;
}

const router = useRouter();

// 响应式数据
const loading = ref(false);
const semesters = ref<Semester[]>([]);
const exams = ref<ExamWithStatus[]>([]);
const grades = ref<Grade[]>([]);
const currentSemester = ref<Semester | null>(null);
const importTasks = ref([]);
const evaluations = ref([]);

// 工作流程相关
const activeWorkflowTab = ref('district');
const districtWorkflowStep = ref(0);
const schoolWorkflowStep = ref(0);

// 快速入口相关
const examTemplates = ref(5); // 考试模板数量
const quickExamDialogVisible = ref(false);
const batchImportDialogVisible = ref(false);
const examTemplateDialogVisible = ref(false);

// 学校端快速创建考试相关
const schoolQuickExamDialogVisible = ref(false);
const schoolExamStep = ref(0);
const availableSchools = ref<any[]>([]);
const availableRegions = ref<any[]>([]);
const availableGrades = ref<any[]>([]);
const availableClassrooms = ref<any[]>([]);
const confirmedStudents = ref<any[]>([]);

// 考场安排相关
const examRooms = ref<ExamRoom[]>([]);
const createdExamId = ref<number | null>(null);
const arrangingRooms = ref(false);
const assigningProctors = ref(false);

// 考场编排配置
const roomArrangementForm = reactive({
  capacityPerRoom: 30,
  arrangementType: 'by_class' as 'by_class' | 'mixed',
  seatPattern: 's_shape' as 'sequential' | 's_shape',
  useExistingRooms: true
});

// 计算属性：动态获取当前区县的学段（学校类型）列表
const availableStudyLevels = computed(() => {
  let schools = availableSchools.value;

  // 先根据区县过滤
  if (schoolExamForm.region_id) {
    schools = schools.filter(s => s.region_id === schoolExamForm.region_id);
  }

  // 提取学校类型（去重、排序）
  const studyLevels = [...new Set(schools.map(s => s.school_type))].filter(Boolean);

  // 按照常见顺序排序（小学、初中、高中）
  const order = { '小学': 1, '初中': 2, '高中': 3 };
  studyLevels.sort((a, b) => {
    const orderA = order[a as keyof typeof order] || 999;
    const orderB = order[b as keyof typeof order] || 999;
    return orderA - orderB;
  });

  return studyLevels;
});

// 计算属性：根据选择的区县过滤学校
const filteredSchools = computed(() => {
  let result = availableSchools.value;

  // 先根据区县过滤
  if (schoolExamForm.region_id) {
    result = result.filter(s => s.region_id === schoolExamForm.region_id);
  }

  // 再根据学段过滤（只显示该学段的学校）
  if (schoolExamForm.study_level) {
    result = result.filter(s => s.school_type === schoolExamForm.study_level);
  }

  return result;
});

// 计算属性：根据选择的学段过滤年级（使用 Grade 的 level 字段）
const filteredGrades = computed(() => {
  if (!schoolExamForm.study_level) {
    return [];
  }

  // 根据学段使用 level 字段过滤
  return availableGrades.value.filter(grade => {
    const level = grade.level;

    if (schoolExamForm.study_level === '小学') {
      // 小学：1-6年级
      return level >= 1 && level <= 6;
    } else if (schoolExamForm.study_level === '初中') {
      // 初中：7-9年级
      return level >= 7 && level <= 9;
    } else if (schoolExamForm.study_level === '高中') {
      // 高中：10-12年级
      return level >= 10 && level <= 12;
    }

    return false;
  });
});

// 学校端考试表单
interface Subject {
  name: string;
  max_score: number;
}

const schoolExamForm = reactive({
  name: '',
  exam_type: '',
  // 考试级别：school（校级）/ district（区级）/ city（市级）
  exam_level: 'school',
  // 区县管理员字段（用于 district/city 级别）
  region_id: undefined as number | undefined,
  study_level: undefined as string | undefined,  // 学段：小学/初中/高中
  grade_id: undefined as number | undefined,  // 年级
  school_ids: [] as number[],  // 多选学校
  // 学校管理员字段（用于 school 级别）
  isJointExam: false,
  additional_school_ids: [] as number[],  // 联考时额外的学校
  // 通用字段
  school_id: undefined as number | undefined,
  class_ids: [] as number[],
  semester_id: undefined as number | undefined,  // 学期ID
  exam_date: '',
  subjects: [
    { name: '语文', max_score: 150 },
    { name: '数学', max_score: 150 },
    { name: '英语', max_score: 150 },
  ] as Subject[],
});

// 对话框显示状态
const semesterDialogVisible = ref(false);
const examDialogVisible = ref(false);
const studentImportDialogVisible = ref(false);
const scoreImportDialogVisible = ref(false);
const evaluationDialogVisible = ref(false);
const performanceDialogVisible = ref(false);

// 学期表单
const semesterForm = reactive({
  year: `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`,
  semester_type: 'up', // 'up' 表示上学期, 'down' 表示下学期
  name: '',
  start_date: '',
  end_date: '',
});

const semesterRules = {
  year: [
    { required: true, message: '请输入学年', trigger: 'blur' },
    {
      pattern: /^\d{4}-\d{4}$/,
      message: '学年格式不正确，应为：2023-2024',
      trigger: 'blur'
    }
  ],
  semester_type: [{ required: true, message: '请选择学期类型', trigger: 'change' }],
  name: [{ required: true, message: '请输入学期名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
};

const semesterFormRef = ref<FormInstance>();
const semesterSubmitting = ref(false);

// 考试表单
const examForm = reactive({
  name: '',
  exam_type: '',
  grade_id: undefined,
  semester_id: undefined,
  exam_date: '',
  description: '',
});

const examRules = {
  name: [{ required: true, message: '请输入考试名称', trigger: 'blur' }],
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  semester_id: [{ required: true, message: '请选择学期', trigger: 'change' }],
  exam_date: [{ required: true, message: '请选择考试日期', trigger: 'change' }],
};

const examFormRef = ref<FormInstance>();
const examSubmitting = ref(false);

// 加载数据
const loadData = async () => {
  loading.value = true;
  try {
    semesters.value = await semesterApi.list();
    const examsList = await examApi.list({ skip: 0, limit: 100 });

    // 为每个考试添加数据准备状态（这里需要调用API获取实际状态）
    // 暂时使用模拟数据，实际应该从后端获取
    exams.value = examsList.map((exam: Exam) => ({
      ...exam,
      hasStudents: false, // TODO: 从API获取是否有考生映射
      hasScores: false, // TODO: 从API获取是否有成绩数据
    })) as ExamWithStatus[];

    // 加载年级数据
    grades.value = await curriculumService.getGrades();
    availableGrades.value = grades.value;  // 同时赋值给 availableGrades

    // 查找当前学期
    currentSemester.value = semesters.value.find(s => s.is_current) || null;
  } catch (error: any) {
    console.error('加载数据失败:', error);
    ElMessage.error(error.response?.data?.detail || '加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 生成学期名称
const generateSemesterName = () => {
  const semesterText = semesterForm.semester_type === 'up' ? '上学期' : '下学期';
  semesterForm.name = `${semesterForm.year}学年${semesterText}`;
};

// 监听学期表单变化
watch(
  () => [semesterForm.year, semesterForm.semester_type],
  () => {
    generateSemesterName();
  }
);

// 监听学校端考试表单变化
watch(
  () => schoolExamForm.class_ids,
  () => {
    updateEstimatedStudentCount();
  },
  { deep: true }
);

watch(
  () => schoolExamForm.subjects,
  () => {
    updateTotalMaxScore();
  },
  { deep: true }
);

watch(
  () => [
    schoolExamForm.name,
    schoolExamForm.school_id,
    schoolExamForm.school_ids,
    schoolExamForm.region_id,
    schoolExamForm.grade_id,
    schoolExamForm.class_ids,
    schoolExamForm.semester_id,
    schoolExamForm.exam_date
  ],
  () => {
    updateCanGoNext();
  },
  { deep: true }
);

// ==================== 快速入口方法 ====================

// 快速创建考试 - 直接打开学校端快速创建考试对话框
const openQuickExamDialog = async () => {
  schoolQuickExamDialogVisible.value = true;
  resetSchoolExamForm();
  // 加载学校数据
  await loadSchools();

  // 如果是学校管理员，自动加载当前学校的年级
  if (isSchoolAdmin.value && currentUser.value?.school_id) {
    const school = availableSchools.value.find(s => s.id === currentUser.value.school_id);
    if (school) {
      await loadGradesBySchoolType(school);
      schoolExamForm.school_id = currentUser.value.school_id;
      ElMessage.success(`已自动加载${currentUser.value.school_name}的年级数据`);
    }
  }

  ElMessage.info(isDistrictAdmin.value ? '开始创建统考...' : '开始快速创建考试...');
};

// 批量导入成绩 - 跳转到成绩导入页面
const openBatchImportDialog = () => {
  router.push('/district-admin/score-import');
};

// 使用考试模板 - 显示提示信息
const openExamTemplateDialog = () => {
  ElMessage.info('考试模板功能开发中，敬请期待...');
  // TODO: 未来实现从历史考试创建新考试
};

// 开始区县管理员工作流
const startDistrictWorkflow = async () => {
  activeWorkflowTab.value = 'district';
  districtWorkflowStep.value = 0;
  // 区县管理员也可以使用快速创建考试功能
  schoolQuickExamDialogVisible.value = true;
  resetSchoolExamForm();
  // 加载学校数据
  await loadSchools();
  ElMessage.info('开始创建考试...');
};

// 开始学校管理员工作流
const startSchoolWorkflow = async () => {
  activeWorkflowTab.value = 'school';
  schoolWorkflowStep.value = 0;
  schoolQuickExamDialogVisible.value = true;
  resetSchoolExamForm();
  // 加载学校数据
  await loadSchools();

  // 如果是学校管理员，自动加载当前学校的年级
  if (isSchoolAdmin.value && currentUser.value?.school_id) {
    const school = availableSchools.value.find(s => s.id === currentUser.value.school_id);
    if (school) {
      await loadGradesBySchoolType(school);
      schoolExamForm.school_id = currentUser.value.school_id;
      ElMessage.success(`已自动加载${currentUser.value.school_name}的年级数据`);
    }
  }
};

// ==================== 学校端快速创建考试方法 ====================

// 计算属性：预估学生数量
const estimatedStudentCount = ref(0);

// 计算属性：科目总分
const totalMaxScore = ref(450);

// 计算属性：是否可以进入下一步
const canGoNext = ref(false);

// 可选科目列表（从系统动态获取）
const availableSubjects = ref<any[]>([]);

// 科目全选相关
const selectAllSubjects = ref(false);
const isIndeterminateSubjects = ref(false);

// 计算属性：已选科目数量
const selectedSubjectsCount = computed(() => {
  return availableSubjects.value.filter(s => s.selected).length;
});

// 计算属性：预计考场数量
const estimatedRoomsCount = computed(() => {
  const students = estimatedStudentCount.value || 0;
  const capacity = roomArrangementForm.capacityPerRoom;
  return Math.ceil(students / capacity);
});

// 加载学校列表和区域列表
const loadSchools = async () => {
  try {
    // 并行加载学校和区域数据
    const [schoolsResponse, regionsResponse] = await Promise.all([
      adminService.getSchools({
        page: 1,
        size: 1000,
        search: ''
      }),
      // TODO: 需要添加获取区域的API
      // adminService.getRegions()
    ]);

    availableSchools.value = schoolsResponse.schools;

    // 提取唯一的区域列表（从学校数据中获取）
    const regionMap = new Map();
    availableSchools.value.forEach(school => {
      if (school.region_id && school.region) {
        regionMap.set(school.region_id, {
          id: school.region_id,
          name: school.region.name
        });
      }
    });
    availableRegions.value = Array.from(regionMap.values());

    if (availableSchools.value.length === 0) {
      ElMessage.warning('暂无学校数据，请先创建学校');
    } else {
      console.log(`已加载 ${availableSchools.value.length} 所学校`);
      if (isDistrictAdmin.value) {
        console.log(`已加载 ${availableRegions.value.length} 个区域`);
      }
    }
  } catch (error: any) {
    console.error('加载学校失败:', error);
    ElMessage.error(error.response?.data?.detail || '加载学校失败');
  }
};

// 学校变化时加载对应的年级
const onSchoolChange = async (schoolId: number | undefined) => {
  // 清空已选择的年级和班级
  schoolExamForm.grade_id = undefined;
  schoolExamForm.class_ids = [];
  availableGrades.value = [];
  availableClassrooms.value = [];

  if (!schoolId) {
    return;
  }

  try {
    // 使用curriculumService获取所有年级，然后根据学校类型过滤
    const allGrades = await curriculumService.getGrades();

    // 获取学校信息
    const school = availableSchools.value.find(s => s.id === schoolId);

    if (school) {
      // 根据学校类型过滤年级
      let filteredGrades = [];

      if (school.school_type === '小学') {
        filteredGrades = allGrades.filter(g =>
          g.name.includes('一年级') || g.name.includes('二年级') ||
          g.name.includes('三年级') || g.name.includes('四年级') ||
          g.name.includes('五年级') || g.name.includes('六年级')
        );
      } else if (school.school_type === '初中') {
        filteredGrades = allGrades.filter(g =>
          g.name.includes('七年级') || g.name.includes('八年级') || g.name.includes('九年级')
        );
      } else if (school.school_type === '高中') {
        filteredGrades = allGrades.filter(g =>
          g.name.includes('高一') || g.name.includes('高二') || g.name.includes('高三')
        );
      } else {
        // 完全中学或其他类型，返回所有年级
        filteredGrades = allGrades;
      }

      availableGrades.value = filteredGrades;

      if (filteredGrades.length > 0) {
        ElMessage.success(`${school.name} - 已加载${filteredGrades.length}个年级`);
      } else {
        ElMessage.warning(`${school.name} - 暂无对应年级数据`);
      }
    }
  } catch (error) {
    console.error('加载年级失败:', error);
    ElMessage.error('加载年级失败');
  }
};

// 年级变化时加载对应的班级
const onGradeChange = async (gradeId: number | undefined) => {
  // 清空已选择的班级
  schoolExamForm.class_ids = [];
  availableClassrooms.value = [];

  if (!gradeId) {
    return;
  }

  // 区县管理员：选择年级后，自动加载所有选中学校的该年级班级
  if (isDistrictAdmin.value && schoolExamForm.school_ids.length > 0) {
    try {
      // 获取第一个选中学校的年级信息（用于显示）
      const firstSchool = availableSchools.value.find(s => s.id === schoolExamForm.school_ids[0]);

      // 加载所有选中学校的该年级班级
      const allClassrooms = [];
      for (const schoolId of schoolExamForm.school_ids) {
        const response = await adminService.getClassrooms({
          school_id: schoolId,
          grade_id: gradeId,
          page: 1,
          size: 100
        });
        allClassrooms.push(...response.classrooms);
      }

      availableClassrooms.value = allClassrooms;

      if (allClassrooms.length > 0) {
        const grade = availableGrades.value.find(g => g.id === gradeId);
        ElMessage.success(`已加载${schoolExamForm.school_ids.length}所学校的${grade?.name}班级，共${allClassrooms.length}个班级`);
      } else {
        ElMessage.warning('所选学校该年级暂无班级数据');
      }
    } catch (error: any) {
      console.error('加载班级失败:', error);
      ElMessage.error(error.response?.data?.detail || '加载班级失败');
    }
  }
  // 学校管理员：使用当前学校的ID
  else if (isSchoolAdmin.value && currentUser.value?.school_id) {
    schoolExamForm.school_id = currentUser.value.school_id;

    try {
      const response = await adminService.getClassrooms({
        school_id: schoolExamForm.school_id,
        grade_id: gradeId,
        page: 1,
        size: 100
      });

      availableClassrooms.value = response.classrooms;

      if (availableClassrooms.value.length > 0) {
        const grade = availableGrades.value.find(g => g.id === gradeId);
        ElMessage.success(`${currentUser.value.school_name} ${grade?.name} - 已加载${availableClassrooms.value.length}个班级`);
      } else {
        ElMessage.warning('该年级暂无班级数据');
      }
    } catch (error: any) {
      console.error('加载班级失败:', error);
      ElMessage.error(error.response?.data?.detail || '加载班级失败');
    }
  }
  // 通用管理员：使用选中的单个学校ID
  else if (schoolExamForm.school_id) {
    try {
      const response = await adminService.getClassrooms({
        school_id: schoolExamForm.school_id,
        grade_id: gradeId,
        page: 1,
        size: 100
      });

      availableClassrooms.value = response.classrooms;

      if (availableClassrooms.value.length > 0) {
        const grade = availableGrades.value.find(g => g.id === gradeId);
        const school = availableSchools.value.find(s => s.id === schoolExamForm.school_id);
        ElMessage.success(`${school?.name} ${grade?.name} - 已加载${availableClassrooms.value.length}个班级`);
      } else {
        ElMessage.warning('该年级暂无班级数据');
      }
    } catch (error: any) {
      console.error('加载班级失败:', error);
      ElMessage.error(error.response?.data?.detail || '加载班级失败');
    }
  }
};

// 区县管理员：区县变化时的处理
const onRegionChange = (regionId: number | undefined) => {
  // 清空已选择的学段、年级和学校
  schoolExamForm.study_level = undefined;
  schoolExamForm.school_ids = [];
  schoolExamForm.grade_id = undefined;
  schoolExamForm.class_ids = [];
  availableClassrooms.value = [];

  if (regionId) {
    const region = availableRegions.value.find(r => r.id === regionId);
    const schoolCount = filteredSchools.value.length;
    ElMessage.success(`${region?.name} - 共有${schoolCount}所学校`);
  }
};

// 区县管理员：学段变化时的处理
const onStudyLevelChange = (studyLevel: string | undefined) => {
  // 清空已选择的年级和学校
  schoolExamForm.grade_id = undefined;
  schoolExamForm.school_ids = [];
  schoolExamForm.class_ids = [];
  availableClassrooms.value = [];

  if (studyLevel) {
    // 根据学段过滤年级
    const gradeCount = filteredGrades.value.length;
    const schoolCount = filteredSchools.value.length;
    ElMessage.success(`${studyLevel} - 共${schoolCount}所学校，${gradeCount}个年级`);
  }
};

// 区县管理员：学校列表变化时的处理
const onSchoolsChange = () => {
  // 清空已选择的班级
  schoolExamForm.class_ids = [];
  availableClassrooms.value = [];

  // 注意：年级已经通过学段选择了，这里不需要再加载年级
};

// 学校管理员：联考模式变化
const onJointExamChange = (isJoint: boolean) => {
  if (!isJoint) {
    schoolExamForm.additional_school_ids = [];
  }
};

// 区县管理员：全选学校
const selectAllSchools = () => {
  schoolExamForm.school_ids = filteredSchools.value.map(s => s.id);
  onSchoolsChange();
};

// 根据学校类型加载年级（辅助函数）
const loadGradesBySchoolType = async (school: any) => {
  try {
    const allGrades = await curriculumService.getGrades();

    let filteredGrades = [];

    if (school.school_type === '小学') {
      filteredGrades = allGrades.filter(g =>
        g.name.includes('一年级') || g.name.includes('二年级') ||
        g.name.includes('三年级') || g.name.includes('四年级') ||
        g.name.includes('五年级') || g.name.includes('六年级')
      );
    } else if (school.school_type === '初中') {
      filteredGrades = allGrades.filter(g =>
        g.name.includes('七年级') || g.name.includes('八年级') || g.name.includes('九年级')
      );
    } else if (school.school_type === '高中') {
      filteredGrades = allGrades.filter(g =>
        g.name.includes('高一') || g.name.includes('高二') || g.name.includes('高三')
      );
    } else {
      // 完全中学或其他类型，返回所有年级
      filteredGrades = allGrades;
    }

    availableGrades.value = filteredGrades;

    if (filteredGrades.length > 0) {
      ElMessage.success(`${school.name} - 已加载${filteredGrades.length}个年级`);
    } else {
      ElMessage.warning(`${school.name} - 暂无对应年级数据`);
    }
  } catch (error) {
    console.error('加载年级失败:', error);
    ElMessage.error('加载年级失败');
  }
};

// 加载科目列表（从系统动态获取）
const loadSubjects = async () => {
  try {
    const subjects = await curriculumService.getSubjects(true);

    // 为每个科目添加selected和max_score字段
    availableSubjects.value = subjects.map(subject => ({
      ...subject,
      selected: false,
      max_score: 100  // 默认满分值
    }));

    // 预选常用科目（语文、数学、英语）
    const commonSubjects = ['语文', '数学', '英语'];
    availableSubjects.value.forEach(subject => {
      if (commonSubjects.includes(subject.name)) {
        subject.selected = true;
        subject.max_score = 150;  // 主科默认150分
      }
    });

    updateSelectedSubjects();

    ElMessage.success(`已加载${subjects.length}个科目`);
  } catch (error: any) {
    console.error('加载科目失败:', error);
    ElMessage.error(error.response?.data?.detail || '加载科目失败');
  }
};

// 处理全选科目
const handleSelectAllSubjects = (checked: boolean) => {
  availableSubjects.value.forEach(subject => {
    subject.selected = checked;
    if (checked && !subject.max_score) {
      subject.max_score = 100;
    }
  });
  updateSelectedSubjects();
};

// 更新选中科目列表
const updateSelectedSubjects = () => {
  const selected = availableSubjects.value.filter(s => s.selected);
  const allSelected = availableSubjects.value.length > 0 &&
    selected.length === availableSubjects.value.length;

  selectAllSubjects.value = allSelected;
  isIndeterminateSubjects.value = selected.length > 0 && !allSelected;

  // 更新表单中的科目列表
  schoolExamForm.subjects = selected.map(s => ({
    name: s.name,
    max_score: s.max_score || 100
  }));

  updateTotalMaxScore();
  updateCanGoNext();
};

// 全选班级
const selectAllClasses = () => {
  schoolExamForm.class_ids = availableClassrooms.value.map(c => c.id);
  updateEstimatedStudentCount();
};

// 更新预估学生数量
const updateEstimatedStudentCount = () => {
  estimatedStudentCount.value = schoolExamForm.class_ids.length * 45;
  updateCanGoNext();
};

// 更新科目总分
const updateTotalMaxScore = () => {
  totalMaxScore.value = availableSubjects.value
    .filter(s => s.selected)
    .reduce((sum, subject) => sum + (subject.max_score || 0), 0);
  updateCanGoNext();
};

// 更新是否可以进入下一步
const updateCanGoNext = () => {
  if (schoolExamStep.value === 0) {
    // 区县管理员验证
    if (isDistrictAdmin.value) {
      canGoNext.value =
        schoolExamForm.name.trim() !== '' &&
        schoolExamForm.region_id !== undefined &&
        schoolExamForm.school_ids.length > 0 &&
        schoolExamForm.grade_id !== undefined &&
        schoolExamForm.semester_id !== undefined &&
        schoolExamForm.exam_date !== '';
    }
    // 学校管理员验证
    else if (isSchoolAdmin.value) {
      canGoNext.value =
        schoolExamForm.name.trim() !== '' &&
        schoolExamForm.grade_id !== undefined &&
        schoolExamForm.class_ids.length > 0 &&
        schoolExamForm.semester_id !== undefined &&
        schoolExamForm.exam_date !== '';
    }
    // 通用管理员验证
    else {
      canGoNext.value =
        schoolExamForm.name.trim() !== '' &&
        schoolExamForm.school_id !== undefined &&
        schoolExamForm.grade_id !== undefined &&
        schoolExamForm.class_ids.length > 0 &&
        schoolExamForm.semester_id !== undefined &&
        schoolExamForm.exam_date !== '';
    }
  } else if (schoolExamStep.value === 1) {
    // 验证是否选择了至少一个科目
    canGoNext.value = selectedSubjectsCount.value > 0;
  } else if (schoolExamStep.value === 2) {
    // 考场安排步骤：必须有已分配的考场
    canGoNext.value = examRooms.value.length > 0;
  } else if (schoolExamStep.value === 3) {
    // 预览确认步骤：学生数量大于0
    canGoNext.value = confirmedStudents.value.length > 0;
  }
};

// 上一步
const prevStep = () => {
  if (schoolExamStep.value > 0) {
    schoolExamStep.value--;
    updateCanGoNext();
  }
};

// 下一步
const nextStep = async () => {
  if (!canGoNext.value) return;

  if (schoolExamStep.value === 0) {
    // 从步骤1进入步骤2：加载科目
    schoolExamStep.value = 1;
    await loadSubjects();
    updateCanGoNext();
  } else if (schoolExamStep.value === 1) {
    // 从步骤2进入步骤3：创建考试（为考场安排准备）
    await createSchoolExamForRooms();
    schoolExamStep.value = 2;
    updateCanGoNext();
  } else if (schoolExamStep.value === 2) {
    // 从步骤3进入步骤4：加载学生名单
    schoolExamStep.value = 3;
    await loadConfirmedStudents();
    updateCanGoNext();
  } else if (schoolExamStep.value === 3) {
    // 从步骤4进入步骤5：完成
    await finalizeSchoolExam();
  }
};

// 加载确认的学生名单
const loadConfirmedStudents = async () => {
  try {
    // TODO: 后端需要添加按班级批量获取学生的API
    // 暂时使用 getUsers API 获取所有学生，然后在前端过滤

    // 获取所有学生
    const response = await adminService.getUsers({
      role: 'student',
      page: 1,
      size: 1000  // 足够大的数量
    });

    // 过滤出选定班级的学生
    const selectedClassIds = schoolExamForm.class_ids;
    confirmedStudents.value = response.users
      .filter(user => selectedClassIds.includes(user.classroom_id!))
      .map(user => ({
        id: user.id,
        name: user.full_name || user.username,
        classroom: user.classroom_name || '未分配班级',
        student_code: user.student_id_number || user.username,
        classroom_id: user.classroom_id,
        school_id: user.school_id
      }));

    if (confirmedStudents.value.length > 0) {
      ElMessage.success(`已加载 ${confirmedStudents.value.length} 名学生`);
    } else {
      ElMessage.warning('选定班级暂无学生数据');
    }
  } catch (error: any) {
    console.error('加载学生名单失败:', error);
    ElMessage.error(error.response?.data?.detail || '加载学生名单失败');
  }
};

// 创建学校考试
// 创建考试（为考场安排准备）- 不显示成功消息
const createSchoolExamForRooms = async () => {
  try {
    // 构建考试日期时间（使用中午12点，格式：YYYY-MM-DD HH:mm:ss）
    const examDate = new Date(schoolExamForm.exam_date);
    const year = examDate.getFullYear();
    const month = String(examDate.getMonth() + 1).padStart(2, '0');
    const day = String(examDate.getDate()).padStart(2, '0');
    const examDateTime = `${year}-${month}-${day} 12:00:00`;

    // 构建请求数据
    const requestData: any = {
      name: schoolExamForm.name,
      exam_type: schoolExamForm.exam_type || 'final',  // 考试类型
      exam_level: schoolExamForm.exam_level,  // 考试级别：school/district/city
      semester_id: schoolExamForm.semester_id!,
      grade_id: schoolExamForm.grade_id!,
      exam_date: examDateTime,  // 格式：YYYY-MM-DD HH:mm:ss
    };

    // 根据考试级别和用户角色添加不同的字段
    if (schoolExamForm.exam_level === 'school') {
      // 校级考试：使用 school_id 和 class_ids
      requestData.school_id = isSchoolAdmin.value ? currentUser.value?.school_id : schoolExamForm.school_id;
      if (schoolExamForm.class_ids.length > 0) {
        requestData.class_ids = schoolExamForm.class_ids;
      }
    } else if (schoolExamForm.exam_level === 'district' || schoolExamForm.exam_level === 'city') {
      // 区级/市级考试：使用 region_id 和 school_ids
      requestData.region_id = schoolExamForm.region_id;
      if (schoolExamForm.school_ids.length > 0) {
        requestData.school_ids = schoolExamForm.school_ids;
      }
      // study_level 仅用于前端过滤，不发送到后端
    }

    console.log('创建考试请求:', requestData);

    // 调用API创建考试
    const response = await examApi.create(requestData);

    // 保存考试ID用于后续考场安排
    createdExamId.value = response.id;

    console.log('考试创建成功，ID:', createdExamId.value);
  } catch (error: any) {
    console.error('创建考试失败:', error);
    console.error('错误详情:', error.response?.data);

    // 显示详细错误信息
    const detail = error.response?.data?.detail || '创建考试失败';
    ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    throw error;
  }
};

// 自动分配考场
const autoAssignExamRooms = async () => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在，请先创建考试');
    return;
  }

  arrangingRooms.value = true;
  try {
    const requestData = {
      capacity_per_room: roomArrangementForm.capacityPerRoom,
      arrangement_type: roomArrangementForm.arrangementType,
      seat_pattern: roomArrangementForm.seatPattern,
      use_existing_rooms: roomArrangementForm.useExistingRooms
    };

    console.log('编排考场请求:', requestData);
    console.log('考试ID:', createdExamId.value);

    const rooms = await examRoomService.autoAssignRooms(
      createdExamId.value,
      requestData
    );
    examRooms.value = rooms;
    ElMessage.success(`成功创建 ${rooms.length} 个考场`);
    updateCanGoNext();
  } catch (error: any) {
    console.error('编排考场失败:', error);
    console.error('错误详情:', error.response?.data);

    // 显示详细错误信息
    const detail = error.response?.data?.detail || '编排考场失败';
    ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  } finally {
    arrangingRooms.value = false;
  }
};

// 自动分配监考教师
const autoAssignProctors = async () => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在，请先创建考试');
    return;
  }

  if (examRooms.value.length === 0) {
    ElMessage.warning('请先编排考场');
    return;
  }

  assigningProctors.value = true;
  try {
    const result = await examRoomService.autoAssignProctors(
      createdExamId.value,
      {
        auto_assign: true,
        avoid_own_class: true,
        same_school_only: true
      }
    );
    ElMessage.success(result.message);
    // 刷新考场数据以显示监考教师
    await loadExamRooms();
  } catch (error: any) {
    console.error('分配监考失败:', error);
    ElMessage.error(error.response?.data?.detail || '分配监考失败');
  } finally {
    assigningProctors.value = false;
  }
};

// 清空所有考场
const clearAllExamRooms = async () => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在，请先创建考试');
    return;
  }

  try {
    await ElMessageBox.confirm(
      '确定要清空所有考场编排吗？此操作将删除所有考场、学生分配和监考分配，且不可恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    await examRoomService.clearAllRooms(createdExamId.value);
    ElMessage.success('已清空所有考场');
    // 清空本地数据
    examRooms.value = [];
    // 刷新数据
    await loadExamRooms();
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('清空考场失败:', error);
      ElMessage.error(error.response?.data?.detail || '清空考场失败');
    }
  }
};

// 加载考场列表
const loadExamRooms = async () => {
  if (!createdExamId.value) return;

  try {
    const rooms = await examRoomService.getExamRooms(createdExamId.value);
    examRooms.value = rooms;
  } catch (error: any) {
    console.error('加载考场失败:', error);
  }
};

// 获取监考教师姓名
const getProctorNames = (room: ExamRoom) => {
  if (!room.proctors || room.proctors.length === 0) {
    return '未分配';
  }
  return room.proctors
    .map(p => {
      const type = p.proctor_type === 'primary' ? '(主)' : '(副)';
      // TODO: 从user数据获取姓名，暂时返回占位符
      return `${type}`;
    })
    .join('、');
};

// 完成考试创建
const finalizeSchoolExam = async () => {
  try {
    schoolExamStep.value = 4;
    ElMessage.success('考试创建成功！');
  } catch (error: any) {
    console.error('完成考试创建失败:', error);
    ElMessage.error('操作失败');
  }
};

// 查看考场详情
const viewRoomDetail = async (room: ExamRoom) => {
  ElMessage.info(`查看 ${room.name} 详情`);
  // TODO: 实现考场详情对话框
  // 可以显示该考场的所有学生及其座位号
};

// 导出座位表
const exportSeatingChart = async (room: ExamRoom) => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在');
    return;
  }

  try {
    ElMessage.info(`正在导出 ${room.name} 座位表...`);
    await examRoomService.exportSeatingChart(createdExamId.value, room.id);
    ElMessage.success('座位表导出成功');
  } catch (error: any) {
    console.error('导出座位表失败:', error);
    ElMessage.error(error.response?.data?.detail || '导出座位表失败');
  }
};

// 导出准考证
const exportExamTickets = async (room: ExamRoom) => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在');
    return;
  }

  try {
    ElMessage.info(`正在导出 ${room.name} 准考证...`);
    await examRoomService.exportExamTickets(createdExamId.value, room.id);
    ElMessage.success('准考证导出成功');
  } catch (error: any) {
    console.error('导出准考证失败:', error);
    ElMessage.error(error.response?.data?.detail || '导出准考证失败');
  }
};

// 导出监考手册
const exportProctorHandbook = async (room: ExamRoom) => {
  if (!createdExamId.value) {
    ElMessage.error('考试ID不存在');
    return;
  }

  try {
    ElMessage.info(`正在导出 ${room.name} 监考手册...`);
    await examRoomService.exportProctorHandbook(createdExamId.value, room.id);
    ElMessage.success('监考手册导出成功');
  } catch (error: any) {
    console.error('导出监考手册失败:', error);
    ElMessage.error(error.response?.data?.detail || '导出监考手册失败');
  }
};

const createSchoolExam = async () => {
  try {
    // TODO: 调用API创建考试
    // await examApi.create({
    //   name: schoolExamForm.name,
    //   class_ids: schoolExamForm.class_ids,
    //   exam_date: schoolExamForm.exam_date,
    //   subjects: schoolExamForm.subjects,
    //   student_ids: confirmedStudents.value.map(s => s.id),
    // });

    // 模拟创建成功
    await new Promise(resolve => setTimeout(resolve, 1000));

    schoolExamStep.value = 3;
    ElMessage.success('考试创建成功！');
  } catch (error: any) {
    console.error('创建考试失败:', error);
    ElMessage.error(error.response?.data?.detail || '创建考试失败');
  }
};

// 跳转到成绩录入页面
const goToScoreEntry = () => {
  // TODO: 跳转到成绩录入页面，并传递考试ID
  ElMessage.info('跳转到成绩录入页面...');
  // router.push({
  //   path: '/district-admin/score-entry',
  //   query: { exam_id: createdExamId }
  // });
};

// 关闭学校端快速创建考试对话框
const closeSchoolQuickExamDialog = () => {
  schoolQuickExamDialogVisible.value = false;
  resetSchoolExamForm();
};

// 重置学校端考试表单
const resetSchoolExamForm = () => {
  schoolExamStep.value = 0;
  schoolExamForm.name = '';
  schoolExamForm.exam_type = '';
  schoolExamForm.exam_level = 'school';  // 重置为默认值
  // 重置区县管理员字段
  schoolExamForm.region_id = undefined;
  schoolExamForm.study_level = undefined;
  schoolExamForm.school_ids = [];
  // 重置学校管理员字段
  schoolExamForm.isJointExam = false;
  schoolExamForm.additional_school_ids = [];
  // 重置通用字段
  schoolExamForm.school_id = undefined;
  schoolExamForm.grade_id = undefined;
  schoolExamForm.class_ids = [];
  schoolExamForm.semester_id = undefined;
  schoolExamForm.exam_date = '';
  schoolExamForm.subjects = [
    { name: '语文', max_score: 150 },
    { name: '数学', max_score: 150 },
    { name: '英语', max_score: 150 },
  ];
  availableSchools.value = [];
  availableRegions.value = [];
  // 注意：availableGrades 是全局数据，不应在重置表单时清空
  // availableGrades.value = [];  // ← 移除这行
  availableClassrooms.value = [];
  availableSubjects.value = [];
  confirmedStudents.value = [];
  estimatedStudentCount.value = 0;
  totalMaxScore.value = 450;
  selectAllSubjects.value = false;
  isIndeterminateSubjects.value = false;
  canGoNext.value = false;

  // 重置考场安排相关状态
  examRooms.value = [];
  createdExamId.value = null;
  arrangingRooms.value = false;
  assigningProctors.value = false;
  roomArrangementForm.capacityPerRoom = 30;
  roomArrangementForm.arrangementType = 'by_class';
  roomArrangementForm.seatPattern = 's_shape';
  roomArrangementForm.useExistingRooms = true;
};

// ==================== 原有方法 ====================

// 打开对话框方法
const openSemesterDialog = () => {
  router.push('/district-admin/semesters');
};

const openExamDialog = () => {
  router.push('/district-admin/exam-management');
};

const openStudentImportDialog = () => {
  router.push('/district-admin/student-import');
};

const openScoreImportDialog = () => {
  router.push('/district-admin/score-import');
};

const openEvaluationDialog = () => {
  router.push('/district-admin/evaluation-report');
};

const openPerformanceDialog = () => {
  router.push('/district-admin/semester-performance');
};

const viewImportTasks = () => {
  router.push('/district-admin/score-import');
};

// 为指定考试导入考生信息
const importStudentsForExam = (exam: Exam) => {
  router.push({
    path: '/district-admin/student-import',
    query: { exam_id: exam.id.toString() }
  });
};

// 为指定考试导入成绩
const importScoresForExam = (exam: Exam) => {
  router.push({
    path: '/district-admin/score-import',
    query: { exam_id: exam.id.toString() }
  });
};

// 计算考试数据准备进度
const getExamProgress = (exam: ExamWithStatus): number => {
  let progress = 0;
  if (exam.hasStudents) progress += 50;
  if (exam.hasScores) progress += 50;
  return progress;
};

// 获取进度状态
const getExamProgressStatus = (exam: ExamWithStatus): string => {
  if (exam.hasStudents && exam.hasScores) return 'success';
  if (exam.hasStudents || exam.hasScores) return 'warning';
  return '';
};

// 学期操作
const createSemester = async () => {
  const valid = await semesterFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  semesterSubmitting.value = true;
  try {
    await semesterApi.create({
      year: semesterForm.year,
      semester_type: semesterForm.semester_type,
      name: semesterForm.name,
      start_date: semesterForm.start_date + 'T00:00:00', // 转换为完整的 datetime 格式
      end_date: semesterForm.end_date + 'T00:00:00', // 转换为完整的 datetime 格式
      is_current: false,
    });
    ElMessage.success('创建成功');
    resetSemesterForm();
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败');
  } finally {
    semesterSubmitting.value = false;
  }
};

const setCurrentSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要将"${semester.name}"设为当前学期吗？`,
      '确认设置',
      { type: 'info' }
    );
    await semesterApi.update(semester.id, { is_current: true });
    ElMessage.success('设置成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '设置失败');
    }
  }
};

const deleteSemester = async (semester: Semester) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学期"${semester.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    );
    await semesterApi.delete(semester.id);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

const resetSemesterForm = () => {
  const currentYear = new Date().getFullYear();
  semesterForm.year = `${currentYear}-${currentYear + 1}`;
  semesterForm.semester_type = 'up'; // 'up' 表示上学期
  semesterForm.name = '';
  semesterForm.start_date = '';
  semesterForm.end_date = '';
  generateSemesterName();
  semesterFormRef.value?.resetFields();
};

// 考试操作
const createExam = async () => {
  const valid = await examFormRef.value?.validate().catch(() => false);
  if (!valid) return;

  examSubmitting.value = true;
  try {
    await examApi.create({
      name: examForm.name,
      exam_type: examForm.exam_type as any,
      grade_id: examForm.grade_id,
      semester_id: examForm.semester_id!,
      exam_date: examForm.exam_date,
      description: examForm.description,
    });
    ElMessage.success('创建成功');
    resetExamForm();
    await loadData();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败');
  } finally {
    examSubmitting.value = false;
  }
};

const deleteExam = async (exam: Exam) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除考试"${exam.name}"吗？`,
      '确认删除',
      { type: 'warning' }
    );
    await examApi.delete(exam.id);
    ElMessage.success('删除成功');
    await loadData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败');
    }
  }
};

const resetExamForm = () => {
  examForm.name = '';
  examForm.exam_type = '';
  examForm.grade_id = undefined;
  examForm.semester_id = undefined;
  examForm.exam_date = '';
  examForm.description = '';
  examFormRef.value?.resetFields();
};

// 辅助函数
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    midterm: '期中',
    final: '期末',
    monthly: '月考',
    mock: '模考',
    unified: '统考',
  };
  return typeMap[type] || type;
};

const getStatusName = (status: string) => {
  const statusMap: Record<string, string> = {
    draft: '草稿',
    scheduled: '已安排',
    in_progress: '进行中',
    completed: '已完成',
  };
  return statusMap[status] || status;
};

const getStatusType = (status: string) => {
  const typeMap: Record<string, any> = {
    draft: 'info',
    scheduled: '',
    in_progress: 'warning',
    completed: 'success',
  };
  return typeMap[status] || '';
};

const getExamLevelName = (level: string) => {
  const levelMap: Record<string, string> = {
    school: '校级',
    district: '区级',
    city: '市级',
  };
  return levelMap[level] || level;
};

const getExamLevelType = (level: string) => {
  const typeMap: Record<string, any> = {
    school: 'info',
    district: 'warning',
    city: 'danger',
  };
  return typeMap[level] || 'info';
};

// 组件挂载
onMounted(() => {
  loadData();
  generateSemesterName();
});
</script>

<style scoped>
.district-admin-dashboard {
  padding: 20px;
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.subtitle {
  margin: 8px 0 0 0;
  font-size: 14px;
  color: #909399;
}

.current-semester {
  flex-shrink: 0;
}

.cards-container {
  margin-bottom: 20px;
}

.function-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.function-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.function-card :deep(.el-card__body) {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: #f5f7fa;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-content h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.card-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #909399;
}

.card-stats {
  font-size: 13px;
  color: #67c23a;
  font-weight: 500;
}

.card-arrow {
  flex-shrink: 0;
  color: #c0c4cc;
  transition: color 0.3s;
}

.function-card:hover .card-arrow {
  color: #409eff;
}

/* 工作流区域样式 */
.workflow-section {
  margin-bottom: 20px;
}

.workflow-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.workflow-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.workflow-subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.workflow-steps {
  padding: 20px 0;
}

.workflow-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-steps {
  display: flex;
  align-items: center;
}

.quick-create-section {
  margin-bottom: 20px;
}

.quick-create-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.semester-list-section h4,
.exam-list-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 学校端快速创建考试对话框样式 */
.step-content {
  min-height: 300px;
}

.step-content h4 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.step-info {
  margin-top: 20px;
}

.step-actions {
  margin-top: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 工作流区域样式优化 */
.workflow-content {
  padding: 20px 0;
}

.workflow-description {
  margin: 30px 0;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.workflow-description h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.instruction-list {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.instruction-list li {
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.instruction-list li strong {
  color: #303133;
  font-weight: 600;
}

.workflow-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.workflow-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #909399;
}

/* 快速入口卡片样式 */
.quick-action-card {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-action-card:hover {
  transform: translateY(-4px);
}

.quick-action-card:hover :deep(.el-card) {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.quick-action-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
}

.quick-action-card .card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.quick-action-card .card-content h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.quick-action-card .card-content .description {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.quick-action-card .steps {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.quick-action-card .step {
  padding: 4px 12px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  font-weight: 500;
}

.quick-action-card .arrow {
  color: #c0c4cc;
  font-size: 14px;
}

.quick-action-card .feature-tags {
  display: flex;
  gap: 8px;
}

.quick-action-card .stats {
  display: flex;
  gap: 12px;
}

.quick-action-card .stat-item {
  font-size: 13px;
  color: #67c23a;
  font-weight: 500;
}

.quick-action-card .card-arrow {
  color: #c0c4cc;
  transition: color 0.3s;
}

.quick-action-card:hover .card-arrow {
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .function-card :deep(.el-card__body) {
    padding: 16px;
  }

  .card-icon {
    width: 48px;
    height: 48px;
  }

  .quick-action-card :deep(.el-card__body) {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
