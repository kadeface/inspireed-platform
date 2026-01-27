<template>
  <div class="district-admin-dashboard p-6 bg-gray-50 min-h-screen">
    <!-- 页面头部 -->
    <div class="page-header flex justify-between items-center mb-8 text-left">
      <div class="flex items-center gap-4">
        <el-button @click="router.back()" circle>
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">考试管理看板</h1>
          <p class="text-gray-600 mt-2">智能闭环考务系统：从标准设定到成绩分析的全流程管理</p>
        </div>
      </div>
      <div class="current-semester flex items-center gap-4">
        <el-badge :value="runningTasks.length" :hidden="runningTasks.length === 0" class="mr-4">
          <el-popover placement="bottom" :width="300" trigger="click">
            <template #reference
              ><el-button circle
                ><el-icon :class="{ 'animate-spin': runningTasks.length > 0 }"
                  ><Refresh v-if="runningTasks.length > 0" /><Bell v-else /></el-icon></el-button
            ></template>
            <div class="task-center text-sm text-left">
              <h4 class="font-bold mb-2 border-b pb-2">后台任务中心</h4>
              <div v-if="runningTasks.length === 0" class="text-center py-4 text-gray-400">
                暂无运行任务
              </div>
              <div v-else class="space-y-4">
                <div v-for="task in runningTasks" :key="task.id" class="task-item">
                  <div class="flex justify-between text-xs mb-1">
                    <span>{{ task.name }}</span
                    ><span>{{ task.progress }}%</span>
                  </div>
                  <el-progress :percentage="task.progress" :stroke-width="3" :show-text="false" />
                </div>
              </div>
            </div>
          </el-popover>
        </el-badge>
        <el-tag v-if="currentSemester" type="success" size="large" effect="dark">{{
          currentSemester.name
        }}</el-tag>
      </div>
    </div>

    <!-- 核心功能卡片 -->
    <el-row :gutter="20" class="mb-10 text-left">
      <el-col :xs="24" :sm="12" :md="6">
        <el-dropdown trigger="click" style="width: 100%" @command="handleConfigCommand">
          <AdminFunctionCard
            title="基础配置"
            description="管理学期时间线与科目标准"
            icon="Setting"
            icon-color="#409eff"
            is-business
          />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="semester"
                ><el-icon><Calendar /></el-icon> 学期时间线管理</el-dropdown-item
              >
              <el-dropdown-item command="subject"
                ><el-icon><Reading /></el-icon> 各年级科目标准</el-dropdown-item
              >
              <el-dropdown-item command="school-profile"
                ><el-icon><OfficeBuilding /></el-icon> 学校基础资料配置</el-dropdown-item
              >
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6"
        ><AdminFunctionCard
          title="校级考试"
          description="一键组织校内考、月考与模考"
          icon="UserFilled"
          icon-color="#67c23a"
          icon-bg-color="#f0f9eb"
          is-business
          @click="startSchoolWorkflow"
      /></el-col>
      <el-col :xs="24" :sm="12" :md="6"
        ><AdminFunctionCard
          title="全区统考"
          description="多校联考创建与全域考务协同"
          icon="OfficeBuilding"
          icon-color="#a855f7"
          icon-bg-color="#f5f3ff"
          is-business
          @click="startDistrictWorkflow"
      /></el-col>
      <el-col :xs="24" :sm="12" :md="6"
        ><AdminFunctionCard
          title="数据中心"
          description="成绩批量导入与评价分析报告"
          icon="DataLine"
          icon-color="#f56c6c"
          @click="openEvaluationDialog"
      /></el-col>
    </el-row>

    <!-- 流程引导 (优化绑定学校显示) -->
    <el-card class="workflow-section mb-10 text-left" shadow="hover">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <el-icon color="#409eff"><Operation /></el-icon>
            <h2 class="text-xl font-bold text-gray-800">
              {{ activeWorkflowTab === 'school' ? '校级考试组织流程' : '全区统考组织流程' }}
            </h2>
            <div
              v-if="activeWorkflowTab === 'school' && configuredSchoolName"
              class="flex items-center gap-1 ml-4 px-3 py-1 bg-green-50 text-green-700 rounded-full border border-green-200"
            >
              <el-icon size="14"><CircleCheckFilled /></el-icon>
              <span class="text-xs font-bold">{{ configuredSchoolName }}</span>
            </div>
          </div>
          <el-radio-group v-model="activeWorkflowTab" size="small">
            <el-radio-button value="school">学校模式</el-radio-button>
            <el-radio-button value="district">区县模式</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div class="py-4 text-center">
        <el-steps
          :active="activeWorkflowTab === 'school' ? schoolWorkflowStep : districtWorkflowStep"
          align-center
          class="interactive-steps"
        >
          <el-step
            v-for="(step, idx) in activeWorkflowTab === 'school' ? schoolSteps : districtSteps"
            :key="idx"
            :title="step.title"
            :description="step.desc"
            class="cursor-pointer"
            @click="step.action()"
            ><template #icon
              ><el-icon><component :is="step.icon" /></el-icon></template
          ></el-step>
        </el-steps>
      </div>
      <div class="workflow-footer bg-blue-50 p-4 rounded-lg mt-4 flex items-center justify-between">
        <div class="flex items-center gap-2 text-blue-700">
          <el-icon><InfoFilled /></el-icon
          ><span class="text-sm font-medium"
            >当前操作：{{
              (activeWorkflowTab === 'school' ? schoolSteps : districtSteps)[
                activeWorkflowTab === 'school' ? schoolWorkflowStep : districtWorkflowStep
              ]?.title
            }}</span
          >
        </div>
        <el-button
          type="primary"
          @click="
            (activeWorkflowTab === 'school' ? schoolSteps : districtSteps)[
              activeWorkflowTab === 'school' ? schoolWorkflowStep : districtWorkflowStep
            ]?.action()
          "
          >立即去处理</el-button
        >
      </div>
    </el-card>

    <!-- 列表 -->
    <el-card shadow="hover" class="text-left">
      <template #header
        ><div class="flex justify-between items-center">
          <h3 class="text-lg font-bold">考试档案列表</h3>
          <el-input
            v-model="searchQuery"
            placeholder="搜索考试..."
            size="small"
            style="width: 240px"
            ><template #prefix
              ><el-icon><Search /></el-icon></template
          ></el-input></div
      ></template>
      <el-table :data="filteredExams" v-loading="loading" stripe border>
        <el-table-column
          prop="name"
          label="考试名称"
          min-width="150"
          show-overflow-tooltip
          align="center"
          class-name="exam-name-column"
        />
        <el-table-column label="考试类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ getExamTypeName(row.exam_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="exam_date" label="日期" width="110" align="center">
          <template #default="{ row }">
            {{ row.exam_date ? row.exam_date.split('T')[0] : '' }}
          </template>
        </el-table-column>
        <el-table-column label="进度" width="150" align="center">
          <template #default="{ row }">
            <el-progress
              :percentage="getExamProgress(row)"
              :status="getExamProgressStatus(row)"
              :stroke-width="6"
              :show-text="false"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewExamDetail(row)"
              >详情</el-button
            >
            <el-button link type="success" size="small" @click="viewExamRooms(row)"
              >座位表</el-button
            >
            <el-button link type="primary" size="small" @click="importStudentsForExam(row)"
              >考生</el-button
            >
            <el-button link type="primary" size="small" @click="importScoresForExam(row)"
              >成绩</el-button
            >
            <el-button link type="danger" size="small" @click="deleteExam(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗集 -->
    <el-dialog
      v-model="schoolProfileDialogVisible"
      title="学校基础资料配置"
      width="800px"
      @open="openSchoolProfileDialog"
    >
      <div class="p-6 text-left">
        <el-form :model="schoolProfileForm" label-width="120px" label-position="left">
          <div class="mb-4 font-bold border-b pb-2 text-blue-600">本校基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12"
              ><el-form-item label="学校全称" required
                ><el-autocomplete
                  v-model="schoolProfileForm.name"
                  :fetch-suggestions="querySearchSchools"
                  @select="handleSchoolSelect"
                  style="width: 100%" /></el-form-item
            ></el-col>
            <el-col :span="12"
              ><el-form-item label="学校代码"
                ><el-input v-model="schoolProfileForm.code" disabled /></el-form-item
            ></el-col>
          </el-row>
          <el-form-item label="详细地址"
            ><el-input v-model="schoolProfileForm.address" type="textarea" :rows="2"
          /></el-form-item>
        </el-form>
      </div>
      <template #footer
        ><el-button @click="schoolProfileDialogVisible = false">取消</el-button
        ><el-button type="primary" @click="saveSchoolProfile" :loading="savingConfig"
          >保存并绑定主体</el-button
        ></template
      >
    </el-dialog>

    <el-dialog
      v-model="schoolQuickExamDialogVisible"
      :title="activeWorkflowTab === 'school' ? '校级考试组织' : '全区统考组织'"
      width="1000px"
    >
      <el-steps :active="schoolExamStep" align-center class="mb-8"
        ><el-step title="范围确认" /><el-step title="科目标准" /><el-step
          title="考务设置" /><el-step title="完成"
      /></el-steps>

      <div v-show="schoolExamStep === 0" class="px-10 py-4 text-left">
        <el-form :model="schoolExamForm" label-position="top">
          <el-form-item label="考试名称" required
            ><el-input v-model="schoolExamForm.name" placeholder="请输入本次考试完整名称"
          /></el-form-item>
          <el-row :gutter="20">
            <el-col :span="8"
              ><el-form-item label="考试类型" required>
                <el-select v-model="schoolExamForm.exam_type" style="width: 100%">
                  <el-option label="月考" value="monthly" />
                  <el-option label="期中考试" value="midterm" />
                  <el-option label="期末考试" value="final" />
                  <el-option label="模拟考试" value="mock" />
                  <el-option label="单元测试" value="unit" />
                  <el-option label="区县统考" value="district_unified" />
                </el-select> </el-form-item
            ></el-col>
            <el-col :span="8"
              ><el-form-item label="对应学期" required
                ><el-select v-model="schoolExamForm.semester_id" style="width: 100%"
                  ><el-option
                    v-for="s in semesters"
                    :key="s.id"
                    :label="s.name"
                    :value="s.id" /></el-select></el-form-item
            ></el-col>
            <el-col :span="8">
              <!-- 校级考试：学校选择 -->
              <template v-if="activeWorkflowTab === 'school'">
                <el-form-item label="组织主体" v-if="configuredSchoolId">
                  <div
                    class="mt-1 flex items-center gap-2 text-gray-800 font-bold bg-gray-50 p-2 rounded border border-dashed border-green-300"
                  >
                    <el-icon color="#67c23a"><OfficeBuilding /></el-icon>
                    {{ configuredSchoolName }}
                  </div>
                </el-form-item>
                <el-form-item label="目标学校" v-else required>
                  <el-select
                    v-model="schoolExamForm.target_school_id"
                    @change="onSchoolChange"
                    style="width: 100%"
                    filterable
                    placeholder="搜索学校"
                    ><el-option v-for="s in schools" :key="s.id" :label="s.name" :value="s.id"
                  /></el-select>
                </el-form-item>
              </template>
              <!-- 全区统考：区县选择 -->
              <template v-else>
                <el-form-item label="所属区县" required>
                  <el-select
                    v-model="schoolExamForm.region_id"
                    @change="onDistrictRegionChange"
                    style="width: 100%"
                    placeholder="选择区县"
                  >
                    <el-option v-for="r in regions" :key="r.id" :label="r.name" :value="r.id" />
                  </el-select>
                </el-form-item>
              </template>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="参与年级" required>
                <el-select
                  v-model="schoolExamForm.grade_id"
                  @change="
                    activeWorkflowTab === 'school'
                      ? onGradeChange(schoolExamForm.grade_id)
                      : onDistrictGradeChange(schoolExamForm.grade_id)
                  "
                  style="width: 100%"
                  :placeholder="activeWorkflowTab === 'school' ? '请先选择学校' : '选择年级'"
                >
                  <el-option
                    v-for="g in activeWorkflowTab === 'school' ? availableGrades : grades"
                    :key="g.id"
                    :label="g.name"
                    :value="g.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12" v-if="activeWorkflowTab === 'district'">
              <el-form-item label="参与学校" required>
                <div class="flex gap-2">
                  <el-select
                    v-model="schoolExamForm.school_ids"
                    multiple
                    collapse-tags
                    style="flex: 1"
                    placeholder="请先选择区县和年级"
                  >
                    <el-option
                      v-for="s in filteredSchoolsForDistrict"
                      :key="s.id"
                      :label="s.name"
                      :value="s.id"
                    />
                  </el-select>
                  <el-button
                    @click="toggleAllDistrictSchools"
                    :disabled="filteredSchoolsForDistrict.length === 0"
                  >
                    {{ isAllDistrictSchoolsSelected ? '取消全选' : '全选' }}
                  </el-button>
                </div>
                <div class="text-xs text-gray-500 mt-1" v-if="schoolExamForm.grade_id">
                  已显示 {{ filteredSchoolsForDistrict.length }} 所{{
                    grades.find((g) => g.id === schoolExamForm.grade_id)?.name
                  }}学校
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="参与班级" v-if="activeWorkflowTab === 'school'" required>
            <div class="flex gap-2">
              <el-select
                v-model="schoolExamForm.class_ids"
                multiple
                collapse-tags
                style="flex: 1"
                placeholder="请先选择学校和年级"
              >
                <el-option
                  v-for="c in filteredClassrooms"
                  :key="c.id"
                  :label="c.name"
                  :value="c.id"
                />
              </el-select>
              <el-button @click="toggleAllClasses" :disabled="filteredClassrooms.length === 0">
                {{ isAllClassesSelected ? '取消全选' : '全选' }}
              </el-button>
            </div>
            <div class="text-xs text-gray-500 mt-1" v-if="schoolExamForm.grade_id">
              已显示 {{ filteredClassrooms.length }} 个{{
                grades.find((g) => g.id === schoolExamForm.grade_id)?.name
              }}班级
            </div>
          </el-form-item>
        </el-form>
      </div>

      <div v-show="schoolExamStep === 1" class="px-10 py-4 text-left">
        <div class="flex justify-between items-center mb-4">
          <div>
            <span class="text-gray-700">已配置的学科标准</span>
            <div class="text-xs text-gray-500 mt-1" v-if="schoolExamForm.grade_id">
              {{ availableSubjects.length }} 个学科 ·
              {{ grades.find((g) => g.id === schoolExamForm.grade_id)?.name }}
            </div>
          </div>
          <div class="flex gap-2">
            <el-button size="small" @click="openSubjectConfigDialog">
              <el-icon class="mr-1"><Setting /></el-icon>
              配置学科标准
            </el-button>
            <el-checkbox
              :model-value="isAllSelected"
              :indeterminate="isIndeterminate"
              @change="handleSelectAllChange"
              >全选所有学科</el-checkbox
            >
          </div>
        </div>
        <el-alert
          v-if="availableSubjects.length === 0 && !subjectLoading"
          type="warning"
          :closable="false"
          class="mb-4"
        >
          <template #title>
            该年级尚未配置学科标准，请先点击右上角「配置学科标准」按钮进行配置
          </template>
        </el-alert>
        <el-table :data="availableSubjects" border size="small" v-loading="subjectLoading">
          <el-table-column width="50" align="center"
            ><template #default="{ row }"
              ><el-checkbox
                :model-value="isSubjectSelected(row)"
                @change="(v) => toggleSubject(row, v)" /></template
          ></el-table-column>
          <el-table-column prop="name" label="学科" /><el-table-column label="设定满分"
            ><template #default="{ row }"
              ><el-input-number
                v-model="row.max_score"
                size="small"
                :min="0"
                :max="200" /></template
          ></el-table-column>
        </el-table>
      </div>

      <div v-show="schoolExamStep === 2" class="px-10 py-4 text-left">
        <el-form label-width="120px"
          ><el-form-item label="考场容量"
            ><el-input-number v-model="roomConfig.capacity" :min="10" :max="60" /></el-form-item
        ></el-form>
      </div>
      <div v-show="schoolExamStep === 3" class="px-10 py-4">
        <el-result icon="success" title="档案组织完毕" sub-title="请确认以下信息无误后生成考试档案">
          <template #extra>
            <div class="text-left bg-gray-50 p-6 rounded-lg max-w-2xl mx-auto">
              <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span class="text-gray-600">考试名称：</span
                  ><span class="font-semibold">{{ schoolExamForm.name }}</span>
                </div>
                <div>
                  <span class="text-gray-600">考试类型：</span
                  ><span class="font-semibold">{{
                    getExamTypeName(schoolExamForm.exam_type)
                  }}</span>
                </div>
                <div>
                  <span class="text-gray-600">所属学期：</span
                  ><span class="font-semibold">{{
                    semesters.find((s) => s.id === schoolExamForm.semester_id)?.name
                  }}</span>
                </div>
                <div>
                  <span class="text-gray-600">参与年级：</span
                  ><span class="font-semibold">{{
                    grades.find((g) => g.id === schoolExamForm.grade_id)?.name
                  }}</span>
                </div>

                <!-- 校级考试：显示班级 -->
                <div v-if="activeWorkflowTab === 'school'" class="col-span-2">
                  <span class="text-gray-600">参与班级：</span>
                  <el-tag
                    v-for="classId in schoolExamForm.class_ids"
                    :key="classId"
                    size="small"
                    class="ml-1"
                    >{{ availableClassrooms.find((c) => c.id === classId)?.name }}</el-tag
                  >
                  <span
                    v-if="schoolExamForm.class_ids.length === 0"
                    class="text-red-500 font-semibold ml-2"
                    >未选择班级</span
                  >
                </div>

                <!-- 全区统考：显示区县和学校 -->
                <template v-if="activeWorkflowTab === 'district'">
                  <div class="col-span-2">
                    <span class="text-gray-600">所属区县：</span>
                    <span class="font-semibold">{{
                      regions.find((r) => r.id === schoolExamForm.region_id)?.name
                    }}</span>
                  </div>
                  <div class="col-span-2">
                    <span class="text-gray-600">参与学校：</span>
                    <el-tag
                      v-for="schoolId in schoolExamForm.school_ids"
                      :key="schoolId"
                      size="small"
                      type="warning"
                      class="ml-1"
                      >{{ schools.find((s) => s.id === schoolId)?.name }}</el-tag
                    >
                    <span
                      v-if="schoolExamForm.school_ids.length === 0"
                      class="text-red-500 font-semibold ml-2"
                      >未选择学校</span
                    >
                  </div>
                </template>

                <div class="col-span-2">
                  <span class="text-gray-600">考试科目：</span>
                  <el-tag
                    v-for="subject in schoolExamForm.subjects"
                    :key="subject.id"
                    size="small"
                    type="success"
                    class="ml-1"
                    >{{ subject.name }} ({{ subject.max_score }}分)</el-tag
                  >
                  <span
                    v-if="schoolExamForm.subjects.length === 0"
                    class="text-red-500 font-semibold ml-2"
                    >未选择科目</span
                  >
                </div>
                <div>
                  <span class="text-gray-600">考场容量：</span
                  ><span class="font-semibold">{{ roomConfig.capacity }}人/考场</span>
                </div>
              </div>

              <!-- 校级考试警告 -->
              <el-alert
                v-if="activeWorkflowTab === 'school' && schoolExamForm.class_ids.length === 0"
                type="error"
                :closable="false"
                class="mt-4"
              >
                <template #title>
                  <strong>警告：</strong>尚未选择参与班级，请返回上一步选择班级后再生成考试档案
                </template>
              </el-alert>

              <!-- 全区统考警告 -->
              <el-alert
                v-if="activeWorkflowTab === 'district' && schoolExamForm.school_ids.length === 0"
                type="error"
                :closable="false"
                class="mt-4"
              >
                <template #title>
                  <strong>警告：</strong>尚未选择参与学校，请返回上一步选择学校后再生成考试档案
                </template>
              </el-alert>
            </div>
          </template>
        </el-result>
      </div>
      <template #footer>
        <!-- 第0步：只显示"下一步" -->
        <el-button v-if="schoolExamStep === 0" type="primary" @click="handleNextStep"
          >下一步</el-button
        >

        <!-- 第1步：显示"上一步"和"下一步" -->
        <template v-if="schoolExamStep === 1">
          <el-button @click="schoolExamStep--">上一步</el-button>
          <el-button
            type="primary"
            @click="handleNextStep"
            :disabled="schoolExamForm.subjects.length === 0"
          >
            下一步
          </el-button>
        </template>

        <!-- 第2步：显示"上一步"和"生成档案" -->
        <template v-if="schoolExamStep === 2">
          <el-button @click="schoolExamStep--">上一步</el-button>
          <el-button type="primary" @click="handleNextStep">生成档案</el-button>
        </template>

        <!-- 第3步：显示"生成考试档案"和"取消" -->
        <template v-if="schoolExamStep === 3">
          <el-button @click="schoolExamStep--">返回修改</el-button>
          <el-button
            type="success"
            @click="createExam"
            :loading="creatingExam"
            :disabled="activeWorkflowTab === 'school' && schoolExamForm.class_ids.length === 0"
          >
            生成考试档案
          </el-button>
        </template>
      </template>
    </el-dialog>

    <!-- 学期管理对话框 -->
    <el-dialog v-model="semesterDialogVisible" title="学期管理" width="900px">
      <div class="p-4">
        <el-form :model="semesterForm" label-width="120px" class="mb-4">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学年">
                <el-input v-model="semesterForm.year" placeholder="2024-2025" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="学期">
                <el-select v-model="semesterForm.semester_type" style="width: 100%">
                  <el-option label="上学期" value="up" />
                  <el-option label="下学期" value="down" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开始日期">
                <el-date-picker
                  v-model="semesterForm.start_date"
                  type="date"
                  placeholder="选择开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="结束日期">
                <el-date-picker
                  v-model="semesterForm.end_date"
                  type="date"
                  placeholder="选择结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <el-button type="primary" @click="handleCreateSemester">创建学期</el-button>
        <el-divider />
        <el-table :data="semesters" border>
          <el-table-column prop="name" label="学期名称" />
          <el-table-column prop="year" label="学年" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button v-if="row.is_current" type="success" size="small" disabled
                >当前学期</el-button
              >
              <el-button v-else type="primary" size="small" @click="handleSetCurrentSemester(row)"
                >设为当前</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 年级科目标准配置对话框 -->
    <el-dialog
      v-model="subjectConfigDialogVisible"
      title="年级科目标准配置"
      width="1200px"
      @open="initSubjectConfig"
      @closed="refreshSubjects"
    >
      <div class="config-dialog-content">
        <!-- 年级选择标签页 -->
        <el-tabs v-model="selectedGradeTab" type="card" @tab-change="selectGrade">
          <el-tab-pane
            v-for="grade in grades"
            :key="grade.id"
            :label="grade.name"
            :name="String(grade.id)"
          >
            <div class="grade-config-content">
              <!-- 统计信息 -->
              <div class="mb-4 p-3 bg-blue-50 rounded">
                <span class="text-sm text-gray-700">
                  已配置 <strong>{{ currentGradeSubjectConfigs.length }}</strong> 个学科
                </span>
              </div>

              <!-- 操作按钮 -->
              <div class="mb-4 flex justify-between items-center">
                <h3 class="text-lg font-semibold">科目列表</h3>
                <el-button type="primary" size="small" @click="openAddSubjectStandardModal">
                  <el-icon class="mr-1"><Plus /></el-icon>
                  添加科目标准
                </el-button>
              </div>

              <!-- Loading -->
              <div v-if="subjectLoading" class="text-center py-8 text-gray-500">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span class="ml-2">加载中...</span>
              </div>

              <!-- Empty State -->
              <div
                v-else-if="currentGradeSubjectConfigs.length === 0"
                class="text-center py-12 bg-gray-50 rounded"
              >
                <div class="text-4xl mb-2">📋</div>
                <p class="text-gray-600 mb-4">该年级暂未配置科目标准</p>
                <el-button type="primary" @click="openAddSubjectStandardModal">立即配置</el-button>
              </div>

              <!-- Subject List -->
              <el-table v-else :data="currentGradeSubjectConfigs" border stripe>
                <el-table-column prop="subject_name" label="学科" width="120" />
                <el-table-column prop="subject_code" label="代码" width="100" />
                <el-table-column prop="full_score" label="满分" width="80" />
                <el-table-column prop="pass_line" label="及格线" width="80" />
                <el-table-column prop="excellent_line" label="优秀线" width="80" />
                <el-table-column prop="good_line" label="良好线" width="80" />
                <el-table-column
                  prop="description"
                  label="说明"
                  min-width="150"
                  show-overflow-tooltip
                />
                <el-table-column label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                      {{ row.is_active ? '启用' : '禁用' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="180" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="editSubjectStandard(row)"
                      >编辑</el-button
                    >
                    <el-button
                      link
                      type="warning"
                      size="small"
                      @click="handleDeleteSubjectConfig(row)"
                      >删除</el-button
                    >
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <!-- 添加/编辑科目标准对话框 -->
    <el-dialog
      v-model="subjectStandardFormVisible"
      :title="editingConfigId ? '编辑标准' : '新增标准'"
      width="500px"
      append-to-body
    >
      <el-form :model="subjectStandardForm" label-width="100px">
        <el-form-item label="学科" required>
          <el-select
            v-model="subjectStandardForm.subject_id"
            filterable
            style="width: 100%"
            :disabled="!!editingConfigId"
          >
            <el-option
              v-for="s in allSubjects"
              :key="s.id"
              :label="`${s.name} (${s.code})`"
              :value="s.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="满分" required>
          <el-input-number
            v-model="subjectStandardForm.full_score"
            :min="1"
            :max="200"
            style="width: 100%"
            @change="autoFillLines"
          />
        </el-form-item>
        <el-form-item label="及格线">
          <el-input-number
            v-model="subjectStandardForm.pass_line"
            :min="0"
            :max="subjectStandardForm.full_score"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="优秀线">
          <el-input-number
            v-model="subjectStandardForm.excellent_line"
            :min="0"
            :max="subjectStandardForm.full_score"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="良好线">
          <el-input-number
            v-model="subjectStandardForm.good_line"
            :min="0"
            :max="subjectStandardForm.full_score"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="subjectStandardForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subjectStandardFormVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSubjectStandard" :loading="savingConfig"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ArrowLeft,
  Setting,
  Edit,
  DataLine,
  Operation,
  InfoFilled,
  Search,
  Plus,
  Calendar,
  Document,
  Upload,
  TrendCharts,
  OfficeBuilding,
  UserFilled,
  Bell,
  Refresh,
  Reading,
  CircleCheckFilled,
  Loading,
} from '@element-plus/icons-vue'
import AdminFunctionCard from '@/components/Admin/AdminFunctionCard.vue'
import { useSemesterStore } from '@/store/semester'
import { evaluationService } from '@/services/evaluation'
import { curriculumService } from '@/services/curriculum'
import { adminService } from '@/services/admin'
import examSubjectsService from '@/services/examSubjects'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const semesterStore = useSemesterStore()
const currentSemester = computed(() => semesterStore.currentSemester)
const loading = ref(false)
const subjectLoading = ref(false)
const savingConfig = ref(false)
const creatingExam = ref(false)
const searchQuery = ref('')
const exams = ref<any[]>([])
const semesters = ref<any[]>([])
const grades = ref<any[]>([])
const schools = ref<any[]>([])
const allSubjects = ref<any[]>([])
const regions = ref<any[]>([])
const currentGradeSubjectConfigs = ref<any[]>([])
const runningTasks = ref<any[]>([])
const activeWorkflowTab = ref('school')
const schoolExamStep = ref(0)
const schoolWorkflowStep = ref(0)
const districtWorkflowStep = ref(0)
const semesterDialogVisible = ref(false)
const subjectConfigDialogVisible = ref(false)
const schoolProfileDialogVisible = ref(false)
const schoolQuickExamDialogVisible = ref(false)
const subjectStandardFormVisible = ref(false)

// 响应式声明
const roomConfig = reactive({ capacity: 30, codeRule: 'student_no' })
const editingConfigId = ref<number | null>(null)
const configuredSchoolId = ref<number | null>(null)
const configuredSchoolName = ref<string>('')
const availableClassrooms = ref<any[]>([])
const availableSubjects = ref<any[]>([])
const availableGrades = ref<any[]>([])
const selectedGradeTab = ref<string>('')

const schoolProfileForm = reactive({ id: null as any, name: '', code: '', address: '' })
const schoolExamForm = reactive({
  name: '',
  exam_type: 'monthly',
  target_school_id: null as any,
  grade_id: null as any,
  semester_id: null as any,
  class_ids: [],
  school_ids: [],
  region_id: null as any,
  subjects: [] as any[],
})
const subjectStandardForm = reactive({
  subject_id: null as any,
  full_score: 100,
  pass_line: 60,
  excellent_line: 85,
  good_line: 75,
  description: '',
})
const semesterForm = reactive({ year: `${new Date().getFullYear()}-${new Date().getFullYear() + 1}`, semester_type: 'up', name: '', start_date: '', end_date: '' })

// 逻辑方法
const handleConfigCommand = (c: string) => {
  if (c === 'semester') semesterDialogVisible.value = true
  else if (c === 'subject') subjectConfigDialogVisible.value = true
  else if (c === 'school-profile') schoolProfileDialogVisible.value = true
}
// 打开学科标准配置对话框（从考试组织流程中）
const openSubjectConfigDialog = () => {
  subjectConfigDialogVisible.value = true
  // 设置当前选中的年级标签
  if (schoolExamForm.grade_id) {
    selectedGradeTab.value = String(schoolExamForm.grade_id)
  }
}
// 监听学科标准对话框关闭，刷新学科列表
const refreshSubjects = () => {
  if (schoolExamForm.grade_id) {
    onGradeChange(schoolExamForm.grade_id)
  }
}
// 打开学校资料对话框时，初始化表单数据
const openSchoolProfileDialog = () => {
  if (configuredSchoolId.value && configuredSchoolName.value) {
    // 如果已经绑定过学校，从 schools 列表中找到完整的学校信息
    const school = schools.value.find((s) => s.id === configuredSchoolId.value)
    if (school) {
      Object.assign(schoolProfileForm, {
        id: school.id,
        name: school.name,
        code: school.code || '',
        address: school.address || '',
      })
    } else {
      // 如果找不到学校，至少填充已有的信息
      Object.assign(schoolProfileForm, {
        id: configuredSchoolId.value,
        name: configuredSchoolName.value,
        code: '',
        address: '',
      })
    }
  } else {
    // 清空表单
    Object.assign(schoolProfileForm, {
      id: null,
      name: '',
      code: '',
      address: '',
    })
  }
}
const saveSchoolProfile = async () => {
  if (!schoolProfileForm.id) return ElMessage.warning('请选择学校')
  configuredSchoolId.value = schoolProfileForm.id
  configuredSchoolName.value = schoolProfileForm.name
  localStorage.setItem('admin_bound_school_id', String(schoolProfileForm.id))
  localStorage.setItem('admin_bound_school_name', schoolProfileForm.name)
  ElMessage.success('学校主体绑定成功')
  schoolProfileDialogVisible.value = false
}
const querySearchSchools = (q: string, cb: any) => {
  const res = q ? schools.value.filter((s) => s.name.includes(q)) : schools.value
  cb(res.map((s) => ({ ...s, value: s.name })))
}
const handleSchoolSelect = (i: any) => {
  Object.assign(schoolProfileForm, {
    id: i.id,
    name: i.name,
    code: i.code || '',
    address: i.address || '',
  })
}

const startSchoolWorkflow = () => {
  activeWorkflowTab.value = 'school'
  schoolExamStep.value = 0
  schoolWorkflowStep.value = 0
  if (configuredSchoolId.value) {
    schoolExamForm.target_school_id = configuredSchoolId.value
    onSchoolChange(configuredSchoolId.value)
  }
  schoolQuickExamDialogVisible.value = true
}
const startDistrictWorkflow = () => {
  activeWorkflowTab.value = 'district'
  schoolExamStep.value = 0
  districtWorkflowStep.value = 0
  schoolQuickExamDialogVisible.value = true
}
const openEvaluationDialog = () => {
  router.push('/district-admin/data-center')
}
const onSchoolChange = async (id: number) => {
  schoolExamForm.class_ids = []
  schoolExamForm.grade_id = null // 清空年级选择
  if (!id) {
    availableClassrooms.value = []
    availableGrades.value = []
    return
  }
  const res = await adminService.getClassrooms({ school_id: id, size: 1000 })
  availableClassrooms.value = res.classrooms || []

  // 从班级列表中提取该校实际开设的年级（去重）
  const schoolGradeIds = Array.from(new Set(availableClassrooms.value.map((c) => c.grade_id)))
  availableGrades.value = grades.value.filter((g) => schoolGradeIds.includes(g.id))
}

// 根据选择的年级过滤班级列表
const filteredClassrooms = computed(() => {
  if (!schoolExamForm.grade_id) {
    return availableClassrooms.value
  }
  return availableClassrooms.value.filter((c) => c.grade_id === schoolExamForm.grade_id)
})

// 根据选择的区县和年级过滤学校列表（全区统考用）
const filteredSchoolsForDistrict = computed(() => {
  let result = schools.value

  // 先按区县筛选
  if (schoolExamForm.region_id) {
    result = result.filter((s) => s.region_id === schoolExamForm.region_id)
  }

  // 再按年级筛选（查找该校是否有该年级的班级）
  if (schoolExamForm.grade_id && availableClassrooms.value.length > 0) {
    const schoolIdsWithGrade = Array.from(
      new Set(
        availableClassrooms.value
          .filter((c) => c.grade_id === schoolExamForm.grade_id)
          .map((c) => c.school_id)
      )
    )
    result = result.filter((s) => schoolIdsWithGrade.includes(s.id))
  }

  return result
})

// 全区统考：是否全选了所有学校
const isAllDistrictSchoolsSelected = computed(() => {
  return (
    filteredSchoolsForDistrict.value.length > 0 &&
    schoolExamForm.school_ids.length === filteredSchoolsForDistrict.value.length
  )
})

// 全区统考：区县变化时的处理
const onDistrictRegionChange = async (regionId: number) => {
  // 清空已选学校和年级
  schoolExamForm.school_ids = []
  schoolExamForm.grade_id = null

  if (!regionId) {
    availableClassrooms.value = []
    return
  }

  // 加载该区县所有学校的班级信息
  try {
    const regionSchools = schools.value.filter((s) => s.region_id === regionId)
    const classroomPromises = regionSchools.map((school) =>
      adminService.getClassrooms({ school_id: school.id, size: 1000 })
    )
    const results = await Promise.all(classroomPromises)

    // 合并所有班级
    availableClassrooms.value = results.flatMap((res) => res.classrooms || [])
  } catch (error) {
    console.error('加载区县班级失败:', error)
    availableClassrooms.value = []
  }
}

// 全区统考：年级变化时的处理
const onDistrictGradeChange = async (gradeId: number) => {
  // 切换年级时清空已选学校和科目
  schoolExamForm.school_ids = []
  schoolExamForm.subjects = []
  subjectLoading.value = true

  try {
    // 只获取该年级已配置的学科标准
    const res = await examSubjectsService.getGradeSubjects(gradeId)

    if (res.subjects && res.subjects.length > 0) {
      // 获取所有学科信息（用于显示学科名称）
      const allSubjects = await curriculumService.getSubjects()

      // 只显示该年级已配置的学科
      availableSubjects.value = res.subjects.map((std: any) => {
        const subject = allSubjects.find((s) => s.id === std.subject_id)
        return {
          id: std.subject_id,
          name: subject?.name || '未知学科',
          max_score: std.full_score || 100,
          is_standard: true,
        }
      })
    } else {
      // 该年级没有配置任何学科标准
      availableSubjects.value = []
    }
  } catch (error) {
    console.error('获取年级学科标准失败:', error)
    availableSubjects.value = []
  } finally {
    subjectLoading.value = false
  }
}

// 全区统考：全选/取消全选学校
const toggleAllDistrictSchools = () => {
  if (isAllDistrictSchoolsSelected.value) {
    schoolExamForm.school_ids = []
  } else {
    schoolExamForm.school_ids = filteredSchoolsForDistrict.value.map((s) => s.id)
  }
}

const onGradeChange = async (v: number) => {
  // 切换年级时清空已选班级和科目
  schoolExamForm.class_ids = []
  schoolExamForm.subjects = []
  subjectLoading.value = true

  try {
    // 只获取该年级已配置的学科标准
    const res = await examSubjectsService.getGradeSubjects(v)

    if (res.subjects && res.subjects.length > 0) {
      // 获取所有学科信息（用于显示学科名称）
      const allSubjects = await curriculumService.getSubjects()

      // 只显示该年级已配置的学科
      availableSubjects.value = res.subjects.map((std: any) => {
        const subject = allSubjects.find((s) => s.id === std.subject_id)
        return {
          id: std.subject_id,
          name: subject?.name || '未知学科',
          max_score: std.full_score || 100,
          is_standard: true,
        }
      })
    } else {
      // 该年级没有配置任何学科标准
      availableSubjects.value = []
    }
  } catch (error) {
    console.error('获取年级学科标准失败:', error)
    availableSubjects.value = []
  } finally {
    subjectLoading.value = false
  }
}

const handleNextStep = () => {
  if (schoolExamStep.value === 0) {
    // 验证必填项
    if (!schoolExamForm.name) {
      return ElMessage.warning('请输入考试名称')
    }

    if (activeWorkflowTab.value === 'school') {
      // 校级考试验证
      if (!schoolExamForm.target_school_id) {
        return ElMessage.warning('请选择目标学校')
      }
      if (schoolExamForm.class_ids.length === 0) {
        return ElMessage.warning('请选择至少一个参与班级')
      }
    } else {
      // 全区统考验证
      if (!schoolExamForm.region_id) {
        return ElMessage.warning('请选择所属区县')
      }
      if (!schoolExamForm.grade_id) {
        return ElMessage.warning('请选择参与年级')
      }
      if (schoolExamForm.school_ids.length === 0) {
        return ElMessage.warning('请选择至少一个参与学校')
      }
    }
    schoolExamStep.value++
  } else if (schoolExamStep.value === 1) {
    // 验证是否选择了学科
    if (schoolExamForm.subjects.length === 0) {
      return ElMessage.warning('请至少选择一个考试科目')
    }
    schoolExamStep.value++
  } else {
    schoolExamStep.value++
  }
}
// 班级全选相关
const isAllClassesSelected = computed(
  () =>
    filteredClassrooms.value.length > 0 &&
    schoolExamForm.class_ids.length === filteredClassrooms.value.length
)
const toggleAllClasses = () => {
  if (isAllClassesSelected.value) {
    schoolExamForm.class_ids = []
  } else {
    schoolExamForm.class_ids = filteredClassrooms.value.map((c) => c.id)
  }
}
const isAllSelected = computed(
  () =>
    availableSubjects.value.length > 0 &&
    schoolExamForm.subjects.length === availableSubjects.value.length
)
const isIndeterminate = computed(
  () =>
    schoolExamForm.subjects.length > 0 &&
    schoolExamForm.subjects.length < availableSubjects.value.length
)
const handleSelectAllChange = (v: boolean) =>
  (schoolExamForm.subjects = v ? [...availableSubjects.value] : [])
const isSubjectSelected = (r: any) => schoolExamForm.subjects.some((s) => s.id === r.id)
const toggleSubject = (r: any, v: boolean) => {
  if (v) schoolExamForm.subjects.push(r)
  else schoolExamForm.subjects = schoolExamForm.subjects.filter((s) => s.id !== r.id)
}

const initSubjectConfig = () => {
  if (grades.value.length > 0 && !selectedGradeTab.value) {
    selectedGradeTab.value = String(grades.value[0].id)
    selectGrade(grades.value[0].id)
  }
}
const selectGrade = async (id: number) => {
  selectedGradeTab.value = String(id)
  subjectLoading.value = true
  try {
    const res = await examSubjectsService.getGradeSubjects(id)
    currentGradeSubjectConfigs.value = res.subjects || []
  } finally {
    subjectLoading.value = false
  }
}
const openAddSubjectStandardModal = () => {
  editingConfigId.value = null
  Object.assign(subjectStandardForm, {
    subject_id: null,
    full_score: 100,
    pass_line: 60,
    excellent_line: 85,
    good_line: 75,
    description: '',
  })
  subjectStandardFormVisible.value = true
}
const editSubjectStandard = (row: any) => {
  editingConfigId.value = row.id
  Object.assign(subjectStandardForm, {
    subject_id: row.subject_id,
    full_score: row.full_score,
    pass_line: row.pass_line,
    excellent_line: row.excellent_line,
    good_line: row.good_line || 75,
    description: row.description || '',
  })
  subjectStandardFormVisible.value = true
}
const autoFillLines = (v: number) => {
  subjectStandardForm.pass_line = Math.round(v * 0.6)
  subjectStandardForm.excellent_line = Math.round(v * 0.85)
  subjectStandardForm.good_line = Math.round(v * 0.75)
}
const saveSubjectStandard = async () => {
  try {
    const p = { ...subjectStandardForm, grade_id: Number(selectedGradeTab.value) }
    if (editingConfigId.value)
      await examSubjectsService.updateGradeSubjectConfig(editingConfigId.value, p as any)
    else await examSubjectsService.createGradeSubjectConfig(p as any)
    ElMessage.success('成功')
    subjectStandardFormVisible.value = false
    selectGrade(Number(selectedGradeTab.value))
  } catch (e) {
    ElMessage.error('失败')
  }
}
const handleDeleteSubjectConfig = (row: any) =>
  ElMessageBox.confirm('移除？').then(async () => {
    await examSubjectsService.deleteGradeSubjectConfig(row.id)
    selectGrade(Number(selectedGradeTab.value))
  })

const loadData = async () => {
  loading.value = true
  try {
    const [e, s, g, sch, r, sub] = await Promise.all([
      evaluationService.exam.list(),
      evaluationService.semester.list(),
      curriculumService.getGrades(),
      adminService.getSchools({ size: 1000 }),
      adminService.getRegions({ size: 100 }),
      curriculumService.getSubjects(),
    ])
    exams.value = e
    semesters.value = s
    grades.value = g
    schools.value = sch.schools || []
    regions.value = r.regions || []
    allSubjects.value = sub
    if (currentSemester.value) schoolExamForm.semester_id = currentSemester.value.id
    const savedId = localStorage.getItem('admin_bound_school_id')
    const savedName = localStorage.getItem('admin_bound_school_name')
    if (savedId) {
      configuredSchoolId.value = Number(savedId)
      configuredSchoolName.value = savedName || ''
    }
  } finally {
    loading.value = false
  }
}

const getExamProgress = (r: any) => (r.has_students ? 50 : 0) + (r.has_scores ? 50 : 0)
const getExamProgressStatus = (r: any) => (getExamProgress(r) === 100 ? 'success' : 'warning')
const deleteExam = (r: any) =>
  ElMessageBox.confirm(`删除 ${r.name}?`).then(async () => {
    await evaluationService.exam.delete(r.id)
    loadData()
  })
const filteredExams = computed(() =>
  searchQuery.value ? exams.value.filter((e) => e.name.includes(searchQuery.value)) : exams.value
)
const handleCreateSemester = async () => {
  if (!semesterForm.year) return
  if (!semesterForm.start_date || !semesterForm.end_date) {
    ElMessage.error('请选择开始日期和结束日期')
    return
  }
  await evaluationService.semester.create({
    ...semesterForm,
    name: `${semesterForm.year}学年${semesterForm.semester_type === 'up' ? '上学期' : '下学期'}`,
    start_date: semesterForm.start_date + 'T00:00:00',
    end_date: semesterForm.end_date + 'T00:00:00',
  } as any)
  loadData()
}
const handleSetCurrentSemester = async (r: any) => {
  await evaluationService.semester.update(r.id, { is_current: true })
  await semesterStore.fetchCurrentSemester()
  loadData()
}
// 查看考试详情
const viewExamDetail = (exam: any) => {
  router.push(`/district-admin/exam-list`)
}

// 查看座位表（考场管理）
const viewExamRooms = (exam: any) => {
  router.push(`/district-admin/exam-list/${exam.id}/rooms`)
}

const importStudentsForExam = (exam: any) => {
  router.push({
    path: '/district-admin/student-import',
    query: { examId: exam.id, examName: exam.name },
  })
}

const importScoresForExam = (exam: any) => {
  router.push({
    path: '/district-admin/score-import',
    query: { examId: exam.id, examName: exam.name },
  })
}

const viewReport = (r: any) => ElMessage.info('分析报告功能开发中')
const closeSchoolQuickExamDialog = () => {
  schoolQuickExamDialogVisible.value = false
  schoolExamStep.value = 0
}

// 获取考试类型名称
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    monthly: '月考',
    midterm: '期中考试',
    final: '期末考试',
    mock: '模拟考试',
    unit: '单元测试',
    district_unified: '区县统考',
  }
  return typeMap[type] || type
}

// 创建考试
const createExam = async () => {
  // 验证必填项
  if (!schoolExamForm.name || !schoolExamForm.grade_id || !schoolExamForm.semester_id) {
    return ElMessage.error('缺少必填信息')
  }

  if (!schoolExamForm.exam_type) {
    return ElMessage.error('请选择考试类型')
  }

  if (schoolExamForm.subjects.length === 0) {
    return ElMessage.error('请至少选择一个考试科目')
  }

  // 根据考试级别验证特定字段
  if (activeWorkflowTab.value === 'school') {
    if (!schoolExamForm.target_school_id) {
      return ElMessage.error('请选择目标学校')
    }
    if (schoolExamForm.class_ids.length === 0) {
      return ElMessage.error('请选择至少一个参与班级')
    }
  } else {
    // 全区统考
    if (!schoolExamForm.region_id) {
      return ElMessage.error('请选择所属区县')
    }
    if (schoolExamForm.school_ids.length === 0) {
      return ElMessage.error('请选择至少一个参与学校')
    }
  }

  creatingExam.value = true
  try {
    // 构建考试数据
    const now = new Date()
    const examData: any = {
      name: schoolExamForm.name,
      exam_type: schoolExamForm.exam_type, // 考试性质：monthly、midterm、final等
      exam_level: activeWorkflowTab.value === 'school' ? 'school' : 'district', // 考试级别
      semester_id: schoolExamForm.semester_id,
      grade_id: schoolExamForm.grade_id,
      // 使用不带时区的datetime格式，匹配数据库的 TIMESTAMP WITHOUT TIME ZONE
      exam_date: now.toISOString().replace('Z', ''), // 2024-01-19T12:15:27.150 (移除Z)
      status: 'draft',
    }

    // 如果是校级考试，添加学校和班级信息
    if (activeWorkflowTab.value === 'school') {
      examData.school_id = schoolExamForm.target_school_id
      examData.class_ids = schoolExamForm.class_ids
    } else {
      // 如果是全区统考，添加区县和学校列表
      examData.region_id = schoolExamForm.region_id
      examData.school_ids = schoolExamForm.school_ids
    }

    // 添加考试科目
    examData.subjects = schoolExamForm.subjects.map((s: any) => ({
      subject_id: s.id,
      full_score: s.max_score,
    }))

    // 添加考场配置
    examData.room_config = {
      capacity: roomConfig.capacity,
    }

    console.log('创建考试数据：', examData)

    // 调用API创建考试
    await evaluationService.exam.create(examData)

    ElMessage.success('考试档案创建成功！')

    // 关闭对话框
    closeSchoolQuickExamDialog()

    // 刷新考试列表
    await loadData()
  } catch (error: any) {
    console.error('创建考试失败:', error)
    ElMessage.error(error?.response?.data?.detail || error?.message || '创建考试失败，请重试')
  } finally {
    creatingExam.value = false
  }
}

const schoolSteps = [
  {
    title: '范围确认',
    desc: '学校及班级',
    icon: 'UserFilled',
    action: () => {
      schoolWorkflowStep.value = 0
      activeWorkflowTab.value = 'school'
      schoolExamStep.value = 0
      schoolQuickExamDialogVisible.value = true
    },
  },
  {
    title: '设置标准',
    desc: '分值及标准',
    icon: 'Setting',
    action: () => {
      schoolWorkflowStep.value = 1
      activeWorkflowTab.value = 'school'
      schoolExamStep.value = 1
      schoolQuickExamDialogVisible.value = true
    },
  },
  {
    title: '成绩录入',
    desc: '数据补录',
    icon: 'Edit',
    action: () => {
      schoolWorkflowStep.value = 2
      activeWorkflowTab.value = 'school'
      schoolExamStep.value = 2
      schoolQuickExamDialogVisible.value = true
    },
  },
  {
    title: '教学反馈',
    desc: '进步分析',
    icon: 'DataLine',
    action: () => {
      schoolWorkflowStep.value = 3
      activeWorkflowTab.value = 'school'
      schoolExamStep.value = 3
      schoolQuickExamDialogVisible.value = true
    },
  },
]

const districtSteps = [
  {
    title: '创建考试',
    desc: '联考范围',
    icon: 'Plus',
    action: () => {
      districtWorkflowStep.value = 0
      activeWorkflowTab.value = 'district'
      schoolExamStep.value = 0
      schoolQuickExamDialogVisible.value = true
    },
  },
  {
    title: '考场安排',
    desc: '全区分配',
    icon: 'OfficeBuilding',
    action: () => {
      districtWorkflowStep.value = 1
      activeWorkflowTab.value = 'district'
      schoolExamStep.value = 2
      schoolQuickExamDialogVisible.value = true
    },
  },
  {
    title: '成绩导入',
    desc: '批量汇总',
    icon: 'Upload',
    action: () => ElMessage.info('成绩导入功能开发中'),
  },
  {
    title: '分析对比',
    desc: '全区表现',
    icon: 'TrendCharts',
    action: () => ElMessage.info('数据分析功能开发中'),
  },
]

onMounted(() => {
  loadData()
  semesterStore.fetchCurrentSemester()
})
</script>

<style scoped>
.stat-mini-card :deep(.el-card__body) {
  padding: 16px;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.task-center {
  max-height: 400px;
  overflow-y: auto;
}

/* 考试名称列靠左显示 */
:deep(.exam-name-column .cell) {
  text-align: left !important;
}

/* 考试名称列表头也靠左 */
:deep(.exam-name-column .el-table__cell-wrapper) {
  justify-content: flex-start !important;
}

/* 其他列的表头和内容居中 */
:deep(.el-table th.el-table__cell:not(.exam-name-column)) {
  text-align: center !important;
}

:deep(.el-table td.el-table__cell:not(.exam-name-column)) {
  text-align: center !important;
}
</style>
