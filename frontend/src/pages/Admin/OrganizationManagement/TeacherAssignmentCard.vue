<template>
  <div class="space-y-6">
    <!-- 功能说明 -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <p class="text-sm text-blue-800">
        💡 <strong>功能说明：</strong>管理教师在各学校、年级、班级、学科的教学任务分配，支持班主任和学科教师两种任务类型。
      </p>
    </div>

    <!-- 筛选和操作栏 -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex flex-wrap items-center gap-4 mb-4">
        <!-- 筛选器 -->
        <!-- 县区 -->
        <select
          v-model="assignmentFilters.region_id"
          @change="handleAssignmentRegionChange"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有县区</option>
          <option v-for="region in allRegions" :key="region.id" :value="region.id">
            {{ region.name }}
          </option>
        </select>
        <!-- 学期 -->
        <select
          v-model="assignmentFilters.semester_id"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学期</option>
          <option v-for="semester in semesters" :key="semester.id" :value="semester.id">
            {{ semester.name }}
          </option>
        </select>
        <!-- 年级 -->
        <select
          v-model="assignmentFilters.grade_id"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有年级</option>
          <option v-for="grade in grades" :key="grade.id" :value="grade.id">
            {{ grade.name }}
          </option>
        </select>
        <!-- 科目 -->
        <select
          v-model="assignmentFilters.subject_id"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学科</option>
          <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
            {{ subject.name }}
          </option>
        </select>
        <!-- 学校 -->
        <select
          v-model="assignmentFilters.school_id"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有学校</option>
          <option v-for="school in filteredAssignmentSchools" :key="school.id" :value="school.id">
            {{ school.name }}
          </option>
        </select>
        <!-- 教师名字 -->
        <select
          v-model="assignmentFilters.teacher_id"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">所有教师</option>
          <option v-for="teacher in teachers" :key="teacher.id" :value="teacher.id">
            {{ teacher.full_name || teacher.username }}
          </option>
        </select>
        <!-- 状态 -->
        <select
          v-model="assignmentFilters.is_active"
          @change="loadTeacherAssignments"
          class="px-3 py-2 border rounded-lg"
        >
          <option :value="undefined">全部状态</option>
          <option :value="true">激活</option>
          <option :value="false">停用</option>
        </select>
        <button
          @click="loadTeacherAssignments"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          🔄 刷新
        </button>
        <button
          @click="openCreateAssignmentDialog"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + 添加教学任务
        </button>
        <button
          @click="openAssignmentImportDialog"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          📥 批量导入
        </button>
      </div>
    </div>

    <!-- 教学任务列表 -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
      <div v-if="assignmentLoading" class="p-6 text-center text-gray-500">加载中...</div>
      <div v-else-if="teacherAssignments.length === 0" class="p-6 text-center text-gray-500">暂无教学任务</div>
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">教师</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">年级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">班级</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学科</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学期/学年</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">任务类型</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="assignment in teacherAssignments" :key="assignment.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
              {{ assignment.teacher?.full_name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ assignment.school?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ assignment.grade?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ assignment.classroom?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ assignment.subject?.name || '未知' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
              {{ assignment.semester?.name || '未知' }} ({{ assignment.academic_year }})
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  assignment.assignment_type === 'head_teacher'
                    ? 'bg-purple-100 text-purple-800'
                    : 'bg-blue-100 text-blue-800'
                ]"
              >
                {{ getAssignmentTypeName(assignment.assignment_type) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  assignment.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                ]"
              >
                {{ assignment.is_active ? '激活' : '非激活' }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex gap-2">
                <button
                  @click="editTeacherAssignment(assignment)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  编辑
                </button>
                <button
                  @click="deleteTeacherAssignment(assignment)"
                  class="text-red-600 hover:text-red-900"
                >
                  删除
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="flex justify-between items-center">
      <div class="text-sm text-gray-700">
        显示 {{ (assignmentPage - 1) * assignmentSize + (teacherAssignments.length ? 1 : 0) }} -
        {{ Math.min(assignmentPage * assignmentSize, assignmentTotal) }} 条，共 {{ assignmentTotal }} 条
      </div>
      <div class="flex gap-2">
        <button
          @click="assignmentPage--; loadTeacherAssignments()"
          :disabled="assignmentPage === 1"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          上一页
        </button>
        <span class="px-3 py-2 text-sm text-gray-600">
          {{ assignmentPage }} / {{ assignmentTotalPages || 1 }}
        </span>
        <button
          @click="assignmentPage++; loadTeacherAssignments()"
          :disabled="assignmentPage === assignmentTotalPages || assignmentTotalPages === 0"
          class="px-3 py-2 border rounded-lg disabled:opacity-50"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 添加/编辑教学任务对话框 -->
    <el-dialog
      v-model="showAssignmentDialog"
      :title="editingAssignment ? '编辑教学任务' : '添加教学任务'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="assignmentForm" label-width="120px">
        <el-form-item label="教师*" required>
          <el-select
            v-model="assignmentForm.teacher_id"
            placeholder="请选择教师"
            filterable
            class="w-full"
          >
            <el-option
              v-for="teacher in teachers"
              :key="teacher.id"
              :label="teacher.full_name || teacher.username"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学校*" required>
          <el-select
            v-model="assignmentForm.school_id"
            @change="handleAssignmentSchoolChange"
            placeholder="请选择学校"
            filterable
            class="w-full"
          >
            <el-option
              v-for="school in schools"
              :key="school.id"
              :label="school.name"
              :value="school.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="年级*" required>
          <el-select
            v-model="assignmentForm.grade_id"
            @change="handleAssignmentGradeChange"
            placeholder="请选择年级"
            class="w-full"
          >
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="班级*" required>
          <el-select
            v-model="assignmentForm.classroom_id"
            placeholder="请选择班级"
            :disabled="!assignmentForm.school_id || !assignmentForm.grade_id"
            filterable
            class="w-full"
          >
            <el-option
              v-for="classroom in filteredAssignmentClassrooms"
              :key="classroom.id"
              :label="classroom.name"
              :value="classroom.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学科*" required>
          <el-select
            v-model="assignmentForm.subject_id"
            placeholder="请选择学科"
            filterable
            class="w-full"
          >
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学期*" required>
          <el-select
            v-model="assignmentForm.semester_id"
            placeholder="请选择学期"
            class="w-full"
          >
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="学年*" required>
          <el-input
            v-model="assignmentForm.academic_year"
            placeholder="如：2023-2024"
            maxlength="20"
          />
        </el-form-item>
        <el-form-item label="任务类型*" required>
          <el-select
            v-model="assignmentForm.assignment_type"
            placeholder="请选择任务类型"
            class="w-full"
          >
            <el-option label="班主任" value="head_teacher" />
            <el-option label="学科教师" value="subject_teacher" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="assignmentForm.is_active"
            active-text="激活"
            inactive-text="停用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignmentDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTeacherAssignment" :loading="assignmentSaving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量导入教学任务对话框 -->
    <el-dialog
      v-model="showAssignmentImportDialog"
      title="批量导入教师教学任务"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-steps :active="assignmentImportStep" finish-status="success" align-center class="mb-6">
        <el-step title="下载模板" />
        <el-step title="填写数据" />
        <el-step title="上传文件" />
        <el-step title="导入结果" />
      </el-steps>

      <!-- 步骤1: 下载模板 -->
      <div v-if="assignmentImportStep === 0" class="space-y-4">
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-800 mb-2">
            <strong>使用说明：</strong>
          </p>
          <ul class="text-sm text-blue-700 list-disc list-inside space-y-1">
            <li>如果您已有模板，可以直接点击"下一步"；如果没有，请先下载Excel模板</li>
            <li>必填字段：教师姓名、学校名称、年级级别、班级编码、学科名称、学期编号、学年、任务类型</li>
            <li>年级级别：填写数字（如7表示七年级，8表示八年级）</li>
            <li>班级编码：填写班级编码（如701表示七年级1班，前1-2位是年级，后2位是班级序号）</li>
            <li>学期编号：填写1（上学期）或2（下学期）</li>
            <li>任务类型：填写职务名称（如"班主任"、"学科教师"、"校长"、"教研室主任"等），支持自定义职务类型</li>
            <li>是否激活：填写"是"或"否"（默认为"是"）</li>
            <li>如果任务已存在，可以选择"更新已存在的任务"来覆盖</li>
            <li>💡 提示：可在"职务类型管理"标签页中查看和创建自定义职务类型</li>
            <li>💡 <strong>重要提示</strong>：如果系统中没有对应的学期或教师，请在上传文件步骤中勾选"自动创建"选项</li>
          </ul>
        </div>
        <div class="flex justify-center gap-4">
          <el-button type="primary" @click="downloadAssignmentTemplate" :icon="Download">
            下载导入模板
          </el-button>
          <el-button @click="assignmentImportStep = 1">
            下一步
          </el-button>
        </div>
      </div>

      <!-- 步骤2: 填写数据说明 -->
      <div v-if="assignmentImportStep === 1" class="space-y-4">
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p class="text-sm text-yellow-800">
            <strong>填写提示：</strong>
          </p>
          <ul class="text-sm text-yellow-700 list-disc list-inside space-y-1 mt-2">
            <li>年级级别：填写1-12的数字（1-6为小学，7-9为初中，10-12为高中）</li>
            <li>班级编码：格式为"年级级别+班级序号"，如701（7年级1班）、1001（10年级1班）</li>
            <li>学期编号：填写1（上学期）或2（下学期）</li>
            <li>学年格式：如 2024-2025</li>
            <li>任务类型：填写系统中已存在的职务名称（支持自定义职务，如"校长"、"教研室主任"等）</li>
            <li>填写完成后，请保存Excel文件</li>
            <li><strong>💡 重要提示</strong>：如果教师或学期在系统中不存在，请在上传文件步骤中勾选相应的"自动创建"选项</li>
          </ul>
        </div>
        
        <!-- 可用职务类型列表 -->
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
          <p class="text-sm text-green-800 font-semibold mb-2">
            📋 当前可用的职务类型：
          </p>
          <div v-if="availablePositionTypes.length > 0" class="flex flex-wrap gap-2">
            <span
              v-for="pt in availablePositionTypes"
              :key="pt.id"
              class="px-3 py-1 text-xs font-medium rounded-full"
              :class="pt.is_system ? 'bg-purple-100 text-purple-800' : 'bg-blue-100 text-blue-800'"
            >
              {{ pt.name }}
              <span v-if="pt.is_system" class="ml-1 text-purple-600">(系统)</span>
            </span>
          </div>
          <p v-else class="text-sm text-green-700">正在加载职务类型列表...</p>
          <p class="text-xs text-green-600 mt-2">
            💡 如需添加新的职务类型，请前往"职务类型管理"标签页
          </p>
        </div>
        
        <div class="flex justify-center gap-4">
          <el-button @click="assignmentImportStep = 0">上一步</el-button>
          <el-button type="primary" @click="assignmentImportStep = 2">下一步：上传文件</el-button>
        </div>
      </div>

      <!-- 步骤3: 上传文件 -->
      <div v-if="assignmentImportStep === 2" class="space-y-4">
        <div class="flex flex-col gap-3 mb-4">
          <label class="flex items-center">
            <input
              v-model="assignmentImportForm.updateExisting"
              type="checkbox"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">更新已存在的任务</span>
          </label>
          <label class="flex items-center">
            <input
              v-model="assignmentImportForm.autoCreateTeachers"
              type="checkbox"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">如果教师不存在，自动创建</span>
          </label>
          <div v-if="assignmentImportForm.autoCreateTeachers" class="ml-6 text-xs text-blue-600">
            💡 提示：自动创建的教师账号信息将在导入结果中显示，可导出Excel分发给教师
          </div>
          <label class="flex items-center">
            <input
              v-model="assignmentImportForm.autoCreateSemesters"
              type="checkbox"
              class="mr-2"
            />
            <span class="text-sm text-gray-700">如果学期不存在，自动创建</span>
          </label>
          <div v-if="assignmentImportForm.autoCreateSemesters" class="ml-6 text-xs text-blue-600">
            💡 提示：学期编号1对应上学期（up），2对应下学期（down）。系统会根据学年自动计算学期日期
          </div>
        </div>
        <el-upload
          ref="assignmentImportUploadRef"
          :auto-upload="false"
          :on-change="handleAssignmentFileChange"
          :on-exceed="handleAssignmentExceed"
          :limit="1"
          accept=".xlsx,.xls"
          drag
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传Excel文件（.xlsx, .xls），且不超过10MB
            </div>
          </template>
        </el-upload>
        <div v-if="selectedAssignmentFile" class="mt-4 p-3 bg-gray-50 rounded-lg">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-700">{{ selectedAssignmentFile.name }}</p>
              <p class="text-xs text-gray-500">{{ formatFileSize(selectedAssignmentFile.size) }}</p>
            </div>
            <el-button
              type="danger"
              size="small"
              @click="selectedAssignmentFile = null; assignmentImportUploadRef?.clearFiles()"
            >
              移除
            </el-button>
          </div>
        </div>
        <div class="flex justify-center gap-4">
          <el-button @click="assignmentImportStep = 1">上一步</el-button>
          <el-button
            type="primary"
            @click="startAssignmentImport"
            :loading="assignmentImporting"
            :disabled="!selectedAssignmentFile"
          >
            {{ assignmentImporting ? '导入中...' : '开始导入' }}
          </el-button>
        </div>
      </div>

      <!-- 步骤4: 导入结果 -->
      <div v-if="assignmentImportStep === 3" class="space-y-4">
        <div
          :class="[
            'p-4 rounded-lg',
            assignmentImportResult.success > 0
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          ]"
        >
          <p class="text-sm font-medium mb-2">
            {{ assignmentImportResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败' }}
          </p>
          <div class="text-sm space-y-1">
            <p>总记录数：{{ assignmentImportResult.total }}</p>
            <p>成功：{{ assignmentImportResult.success }} 条</p>
            <p>失败：{{ assignmentImportResult.failed }} 条</p>
            <p v-if="assignmentImportResult.created > 0">创建：{{ assignmentImportResult.created }} 条</p>
            <p v-if="assignmentImportResult.updated > 0">更新：{{ assignmentImportResult.updated }} 条</p>
            <p v-if="assignmentImportResult.skipped > 0">跳过：{{ assignmentImportResult.skipped }} 条</p>
          </div>
        </div>

        <!-- 新创建的教师列表 -->
        <div v-if="assignmentImportResult.created_teachers && assignmentImportResult.created_teachers.length > 0" class="mt-4">
          <div class="flex items-center justify-between mb-2">
            <p class="text-sm font-medium text-blue-700">
              ✅ 新创建的教师账号（共 {{ assignmentImportResult.created_teachers.length }} 个）
            </p>
            <el-button
              type="primary"
              size="small"
              @click="exportCreatedTeachers"
            >
              导出账号信息
            </el-button>
          </div>
          <div class="max-h-60 overflow-y-auto border rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-blue-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">教师姓名</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">用户名</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">邮箱</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">初始密码</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">学校</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(teacher, index) in assignmentImportResult.created_teachers" :key="index">
                  <td class="px-4 py-2 text-sm text-gray-900">{{ teacher.teacher_name }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700 font-mono">{{ teacher.username }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700 font-mono">{{ teacher.email }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700 font-mono">{{ teacher.password }}</td>
                  <td class="px-4 py-2 text-sm text-gray-600">{{ teacher.school_name }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="mt-2 text-xs text-blue-600">
            💡 提示：请导出账号信息Excel文件，分发给新创建的教师。首次登录需要修改密码。
          </p>
        </div>

        <!-- 新创建的学期列表 -->
        <div v-if="assignmentImportResult.created_semesters && assignmentImportResult.created_semesters.length > 0" class="mt-4">
          <p class="text-sm font-medium text-green-700 mb-2">
            ✅ 新创建的学期（共 {{ assignmentImportResult.created_semesters.length }} 个）
          </p>
          <div class="max-h-60 overflow-y-auto border rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-green-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">学期名称</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">学年</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">学期类型</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">开始日期</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-700">结束日期</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(semester, index) in assignmentImportResult.created_semesters" :key="index">
                  <td class="px-4 py-2 text-sm text-gray-900">{{ semester.semester_name }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700">{{ semester.academic_year }}</td>
                  <td class="px-4 py-2 text-sm text-gray-700">
                    <span class="px-2 py-1 text-xs rounded-full"
                          :class="semester.semester_type === 'up' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'">
                      {{ semester.semester_type === 'up' ? '上学期' : '下学期' }}
                    </span>
                  </td>
                  <td class="px-4 py-2 text-sm text-gray-600">{{ semester.start_date ? new Date(semester.start_date).toLocaleDateString('zh-CN') : '—' }}</td>
                  <td class="px-4 py-2 text-sm text-gray-600">{{ semester.end_date ? new Date(semester.end_date).toLocaleDateString('zh-CN') : '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="assignmentImportResult.errors.length > 0" class="mt-4">
          <p class="text-sm font-medium text-gray-700 mb-2">错误详情：</p>
          <div class="max-h-60 overflow-y-auto border rounded-lg">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">行号</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">字段</th>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">错误信息</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(error, index) in assignmentImportResult.errors" :key="index">
                  <td class="px-4 py-2 text-sm text-gray-900">{{ error.row }}</td>
                  <td class="px-4 py-2 text-sm text-gray-500">{{ error.field || '—' }}</td>
                  <td class="px-4 py-2 text-sm text-red-600">{{ error.message }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="flex justify-center gap-4 mt-4">
          <el-button @click="closeAssignmentImportDialog">关闭</el-button>
          <el-button
            v-if="assignmentImportResult.success > 0"
            type="primary"
            @click="closeAssignmentImportDialog(); loadTeacherAssignments()"
          >
            查看结果
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import type { UploadProps } from 'element-plus'
import * as XLSX from 'xlsx'
import adminService, { type Region, type School, type Classroom, type User } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import teacherApi from '@/services/teacher'
import { semesterApi } from '@/services/evaluation'
import { teacherPositionApi } from '@/services/teacher_position'
import type {
  TeacherPositionTypeResponse as TeacherPositionType,
} from '@/types/teacher_position'
import type { Grade, Subject } from '@/types/curriculum'
import type {
  TeacherTeachingAssignment,
  TeacherTeachingAssignmentCreate,
  TeacherTeachingAssignmentUpdate,
  TeacherAssignmentImportResponse,
} from '@/types/teacher'
import { TeachingAssignmentType } from '@/types/teacher'
import type { Semester } from '@/types/evaluation'

// 教师教学任务管理状态
const teacherAssignments = ref<TeacherTeachingAssignment[]>([])
const teachers = ref<User[]>([])
const subjects = ref<Subject[]>([])
const semesters = ref<Semester[]>([])
const schools = ref<School[]>([])
const allRegions = ref<Region[]>([])
const grades = ref<Grade[]>([])
const allClassrooms = ref<Classroom[]>([])

const assignmentPage = ref(1)
const assignmentSize = ref(10)
const assignmentTotal = ref(0)
const assignmentLoading = ref(false)
const assignmentFilters = ref({
  region_id: undefined as number | undefined,
  semester_id: undefined as number | undefined,
  grade_id: undefined as number | undefined,
  subject_id: undefined as number | undefined,
  school_id: undefined as number | undefined,
  teacher_id: undefined as number | undefined,
  classroom_id: undefined as number | undefined,
  is_active: undefined as boolean | undefined,
})
const assignmentTotalPages = computed(() => Math.ceil(assignmentTotal.value / assignmentSize.value))

// 教师教学任务对话框状态
const showAssignmentDialog = ref(false)
const editingAssignment = ref<TeacherTeachingAssignment | null>(null)
const assignmentSaving = ref(false)
const assignmentForm = ref<TeacherTeachingAssignmentCreate>({
  teacher_id: 0,
  school_id: 0,
  grade_id: 0,
  classroom_id: 0,
  subject_id: 0,
  semester_id: 0,
  academic_year: '',
  assignment_type: TeachingAssignmentType.SUBJECT_TEACHER,
  is_active: true,
})

// 批量导入教学任务状态
const showAssignmentImportDialog = ref(false)
const assignmentImportStep = ref(0)
const selectedAssignmentFile = ref<File | null>(null)
const assignmentImportUploadRef = ref<any>(null)
const assignmentImporting = ref(false)
const assignmentImportForm = ref({
  updateExisting: false,
  autoCreateTeachers: false,
  autoCreateSemesters: false,
})

const assignmentImportResult = ref<TeacherAssignmentImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: [],
  created_teachers: [],
  created_semesters: [],
})
const availablePositionTypes = ref<TeacherPositionType[]>([])

// 计算属性：过滤后的学校列表（用于教学任务筛选）
const filteredAssignmentSchools = computed(() => {
  if (!assignmentFilters.value.region_id) {
    return schools.value
  }
  return schools.value.filter(
    (s) => s.region_id === assignmentFilters.value.region_id
  )
})

// 计算属性：过滤后的班级列表（用于教学任务表单）
const filteredAssignmentClassrooms = computed(() => {
  if (!assignmentForm.value.school_id || !assignmentForm.value.grade_id) {
    return []
  }
  return allClassrooms.value.filter(
    (c) => c.school_id === assignmentForm.value.school_id && c.grade_id === assignmentForm.value.grade_id
  )
})

// 方法
function getAssignmentTypeName(type: string): string {
  return type === 'head_teacher' ? '班主任' : '学科教师'
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 1000 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
  }
}

async function loadSchools() {
  try {
    const response = await adminService.getSchools({ size: 1000 })
    schools.value = response.schools
  } catch (error: any) {
    console.error('Failed to load schools:', error)
  }
}

async function loadGrades() {
  try {
    grades.value = await curriculumService.getGrades(true)
  } catch (error: any) {
    console.error('Failed to load grades:', error)
  }
}

async function loadAllClassrooms() {
  try {
    const response = await adminService.getClassrooms({ size: 100 })
    allClassrooms.value = response.classrooms
  } catch (error: any) {
    console.error('Failed to load all classrooms:', error)
  }
}

async function loadTeachers() {
  try {
    const response = await adminService.getUsers({ role: 'teacher', size: 1000 })
    teachers.value = response.users
  } catch (error: any) {
    console.error('Failed to load teachers:', error)
  }
}

async function loadSubjects() {
  try {
    subjects.value = await curriculumService.getSubjects(true)
  } catch (error: any) {
    console.error('Failed to load subjects:', error)
  }
}

async function loadSemesters() {
  try {
    semesters.value = await semesterApi.list({ limit: 100 })
  } catch (error: any) {
    console.error('Failed to load semesters:', error)
  }
}

function handleAssignmentRegionChange() {
  // 当县区改变时，清空学校筛选，因为学校列表会根据县区过滤
  assignmentFilters.value.school_id = undefined
  loadTeacherAssignments()
}

async function loadTeacherAssignments() {
  assignmentLoading.value = true
  try {
    const response = await teacherApi.getAssignments({
      ...assignmentFilters.value,
      page: assignmentPage.value,
      size: assignmentSize.value,
    })
    teacherAssignments.value = response.assignments
    assignmentTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load assignments:', error)
    ElMessage.error(error.response?.data?.detail || '加载教学任务列表失败')
  } finally {
    assignmentLoading.value = false
  }
}

function openCreateAssignmentDialog() {
  editingAssignment.value = null
  assignmentForm.value = {
    teacher_id: 0,
    school_id: 0,
    grade_id: 0,
    classroom_id: 0,
    subject_id: 0,
    semester_id: 0,
    academic_year: '',
    assignment_type: TeachingAssignmentType.SUBJECT_TEACHER,
    is_active: true,
  }
  showAssignmentDialog.value = true
}

function editTeacherAssignment(assignment: TeacherTeachingAssignment) {
  editingAssignment.value = assignment
  assignmentForm.value = {
    teacher_id: assignment.teacher_id,
    school_id: assignment.school_id,
    grade_id: assignment.grade_id,
    classroom_id: assignment.classroom_id,
    subject_id: assignment.subject_id,
    semester_id: assignment.semester_id,
    academic_year: assignment.academic_year,
    assignment_type: assignment.assignment_type,
    is_active: assignment.is_active,
  }
  showAssignmentDialog.value = true
}

function handleAssignmentSchoolChange() {
  assignmentForm.value.grade_id = 0
  assignmentForm.value.classroom_id = 0
}

function handleAssignmentGradeChange() {
  assignmentForm.value.classroom_id = 0
}

async function saveTeacherAssignment() {
  if (!assignmentForm.value.teacher_id || !assignmentForm.value.school_id || !assignmentForm.value.grade_id ||
      !assignmentForm.value.classroom_id || !assignmentForm.value.subject_id || !assignmentForm.value.semester_id ||
      !assignmentForm.value.academic_year || !assignmentForm.value.assignment_type) {
    ElMessage.warning('请填写所有必填字段')
    return
  }

  assignmentSaving.value = true
  try {
    if (editingAssignment.value) {
      // 更新
      const updateData: TeacherTeachingAssignmentUpdate = {
        teacher_id: assignmentForm.value.teacher_id,
        school_id: assignmentForm.value.school_id,
        grade_id: assignmentForm.value.grade_id,
        classroom_id: assignmentForm.value.classroom_id,
        subject_id: assignmentForm.value.subject_id,
        semester_id: assignmentForm.value.semester_id,
        academic_year: assignmentForm.value.academic_year,
        assignment_type: assignmentForm.value.assignment_type,
        is_active: assignmentForm.value.is_active,
      }
      await teacherApi.updateAssignment(editingAssignment.value.id, updateData)
      ElMessage.success('教学任务更新成功')
    } else {
      // 创建
      await teacherApi.createAssignment(assignmentForm.value as TeacherTeachingAssignmentCreate)
      ElMessage.success('教学任务创建成功')
    }
    showAssignmentDialog.value = false
    editingAssignment.value = null
    loadTeacherAssignments()
  } catch (error: any) {
    console.error('Failed to save assignment:', error)
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    assignmentSaving.value = false
  }
}

async function deleteTeacherAssignment(assignment: TeacherTeachingAssignment) {
  try {
    await ElMessageBox.confirm(
      `确定要删除该教学任务吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await teacherApi.deleteAssignment(assignment.id)
    ElMessage.success('删除成功')
    loadTeacherAssignments()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Failed to delete assignment:', error)
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 批量导入教学任务方法
async function loadAvailablePositionTypes() {
  try {
    const response = await teacherPositionApi.getPositionTypes({ is_active: true })
    availablePositionTypes.value = response.position_types
  } catch (error: any) {
    console.error('Failed to load available position types:', error)
    // 不显示错误，静默失败
  }
}

function openAssignmentImportDialog() {
  showAssignmentImportDialog.value = true
  assignmentImportStep.value = 0
  selectedAssignmentFile.value = null
  assignmentImportForm.value = {
    updateExisting: false,
    autoCreateTeachers: false,
    autoCreateSemesters: false,
  }
  assignmentImportResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: [],
    created_teachers: [],
    created_semesters: [],
  }
  if (assignmentImportUploadRef.value) {
    assignmentImportUploadRef.value.clearFiles()
  }
  // 加载可用职务类型列表
  loadAvailablePositionTypes()
}

function closeAssignmentImportDialog() {
  showAssignmentImportDialog.value = false
  assignmentImportStep.value = 0
  selectedAssignmentFile.value = null
  if (assignmentImportUploadRef.value) {
    assignmentImportUploadRef.value.clearFiles()
  }
  // 刷新教学任务列表
  loadTeacherAssignments()
}

function downloadAssignmentTemplate() {
  // 创建Excel模板数据（使用简化格式）
  const template = [
    ['教师姓名*', '学校名称*', '年级级别*', '班级编码*', '学科名称*', '学期编号*', '学年*', '任务类型*', '是否激活'],
    ['张老师', '开平市第一中学', 7, '701', '语文', 1, '2024-2025', '学科教师', '是'],
    ['李老师', '开平市第一中学', 7, '701', '数学', 1, '2024-2025', '学科教师', '是'],
    ['王老师', '开平市第一中学', 7, '701', '英语', 1, '2024-2025', '班主任', '是'],
  ]

  // 使用xlsx库生成Excel文件
  const ws = XLSX.utils.aoa_to_sheet(template)

  // 设置列宽
  const colWidths = [
    { wch: 15 }, // 教师姓名
    { wch: 20 }, // 学校名称
    { wch: 12 }, // 年级级别
    { wch: 12 }, // 班级编码
    { wch: 12 }, // 学科名称
    { wch: 12 }, // 学期编号
    { wch: 12 }, // 学年
    { wch: 12 }, // 任务类型
    { wch: 12 }, // 是否激活
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '教师教学任务')
  XLSX.writeFile(wb, '教师教学任务导入模板.xlsx')
  ElMessage.success('模板下载成功')
}

function exportCreatedTeachers() {
  if (!assignmentImportResult.value.created_teachers || assignmentImportResult.value.created_teachers.length === 0) {
    ElMessage.warning('没有可导出的教师账号信息')
    return
  }

  // 创建Excel数据
  const headers = ['教师姓名', '用户名', '邮箱', '初始密码', '学校名称', '学校编码', '年级名称', '班级编码', '班级名称', 'Excel行号']
  const data = [
    headers,
    ...assignmentImportResult.value.created_teachers.map(teacher => [
      teacher.teacher_name,
      teacher.username,
      teacher.email,
      teacher.password,
      teacher.school_name,
      teacher.school_code,
      teacher.grade_name || '',
      teacher.classroom_code || '',
      teacher.classroom_name || '',
      teacher.row_number,
    ])
  ]

  // 使用xlsx库生成Excel文件
  const ws = XLSX.utils.aoa_to_sheet(data)

  // 设置列宽
  const colWidths = [
    { wch: 12 }, // 教师姓名
    { wch: 25 }, // 用户名
    { wch: 30 }, // 邮箱
    { wch: 15 }, // 初始密码
    { wch: 20 }, // 学校名称
    { wch: 15 }, // 学校编码
    { wch: 12 }, // 年级名称
    { wch: 12 }, // 班级编码
    { wch: 15 }, // 班级名称
    { wch: 10 }, // Excel行号
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '新创建教师账号')
  XLSX.writeFile(wb, `新创建教师账号_${new Date().toISOString().split('T')[0]}.xlsx`)
  ElMessage.success('账号信息导出成功')
}

const handleAssignmentFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedAssignmentFile.value = uploadFile.raw || null
}

const handleAssignmentExceed: UploadProps['onExceed'] = () => {
  ElMessage.warning('只能上传一个文件')
}

async function startAssignmentImport() {
  if (!selectedAssignmentFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  assignmentImporting.value = true

  try {
    const result = await teacherApi.importAssignments(
      selectedAssignmentFile.value,
      assignmentImportForm.value.updateExisting,
      assignmentImportForm.value.autoCreateTeachers,
      assignmentImportForm.value.autoCreateSemesters
    )

    assignmentImportResult.value = result
    assignmentImportStep.value = 3

    if (result.success > 0) {
      ElMessage.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      ElMessage.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.detail || '导入失败')
    assignmentImportResult.value = {
      total: 0,
      success: 0,
      failed: 1,
      created: 0,
      updated: 0,
      skipped: 0,
      errors: [{
        row: 0,
        field: null,
        message: error.response?.data?.detail || '导入失败'
      }],
      created_teachers: [],
      created_semesters: [],
    }
    assignmentImportStep.value = 3
  } finally {
    assignmentImporting.value = false
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([
    loadAllRegions(),
    loadSchools(),
    loadGrades(),
    loadAllClassrooms(),
    loadTeachers(),
    loadSubjects(),
    loadSemesters(),
    loadTeacherAssignments(),
  ])
})
</script>

<style scoped>
.space-y-6 > * + * {
  margin-top: 1.5rem;
}
</style>
