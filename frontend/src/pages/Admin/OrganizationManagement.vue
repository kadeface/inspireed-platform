<template>
  <div class="organization-management p-6">
    <!-- 面包屑导航 -->
    <div class="mb-4">
      <router-link 
        to="/admin" 
        class="text-blue-600 hover:text-blue-800 flex items-center gap-2"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回管理员首页
      </router-link>
    </div>
    
    <div class="header mb-6">
      <h1 class="text-3xl font-bold text-gray-900">组织架构管理</h1>
      <p class="text-gray-600 mt-2">管理区域、学校和班级成员信息</p>
    </div>

    <!-- 标签页切换 -->
    <div class="bg-white rounded-lg shadow mb-6">
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button
            @click="activeTab = 'regions'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'regions'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            区域管理
          </button>
          <button
            @click="activeTab = 'schools'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'schools'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            学校管理
          </button>
          <button
            @click="activeTab = 'classrooms'"
            :class="[
              'px-6 py-3 text-sm font-medium border-b-2',
              activeTab === 'classrooms'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            班级成员管理
            <span class="ml-1 text-xs text-gray-400">(添加教师/学生到班级)</span>
          </button>
        </nav>
      </div>
    </div>

    <!-- 区域管理 -->
    <div v-if="activeTab === 'regions'" class="space-y-6">
      <!-- 操作栏 -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center">
          <div class="flex gap-4">
            <button
              @click="openCreateRegionModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + 创建区域
            </button>
            <button
              @click="loadRegions"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              🔄 刷新
            </button>
          </div>
          <div class="flex gap-2">
            <select v-model="regionLevelFilter" @change="loadRegions" class="px-3 py-2 border rounded-lg">
              <option value="">所有级别</option>
              <option value="1">省级</option>
              <option value="2">市级</option>
              <option value="3">区级</option>
            </select>
            <input
              v-model="regionSearchQuery"
              @input="searchRegions"
              type="text"
              placeholder="搜索区域..."
              class="px-3 py-2 border rounded-lg w-64"
            />
          </div>
        </div>
      </div>

      <!-- 区域列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">区域名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">级别</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">创建时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="region in regions" :key="region.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ region.name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ region.code }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="getRegionLevelClass(region.level)">
                  {{ getRegionLevelName(region.level) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="region.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ region.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(region.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button @click="editRegion(region)" class="text-blue-600 hover:text-blue-900">
                    编辑
                  </button>
                  <button @click="deleteRegion(region)" class="text-red-600 hover:text-red-900">
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
          显示 {{ (regionPage - 1) * regionPageSize + 1 }} - {{ Math.min(regionPage * regionPageSize, regionTotal) }} 条，共 {{ regionTotal }} 条
        </div>
        <div class="flex gap-2">
          <button
            @click="prevRegionPage"
            :disabled="regionPage === 1"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-2">{{ regionPage }} / {{ regionTotalPages }}</span>
          <button
            @click="nextRegionPage"
            :disabled="regionPage === regionTotalPages"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 学校管理 -->
    <div v-if="activeTab === 'schools'" class="space-y-6">
      <!-- 操作栏 -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center">
          <div class="flex gap-4">
            <button
              @click="openCreateSchoolModal"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + 创建学校
            </button>
            <button
              @click="openSchoolImportDialog"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              📥 批量导入学校
            </button>
            <button
              @click="openDistrictClassroomImportDialog"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              📥 批量导入班级
            </button>
            <button
              @click="loadSchools"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              🔄 刷新
            </button>
          </div>
          <div class="flex gap-2">
            <select v-model="schoolTypeFilter" @change="loadSchools" class="px-3 py-2 border rounded-lg">
              <option value="">所有类型</option>
              <option value="小学">小学</option>
              <option value="初中">初中</option>
              <option value="高中">高中</option>
              <option value="大学">大学</option>
            </select>
            <input
              v-model="schoolSearchQuery"
              @input="searchSchools"
              type="text"
              placeholder="搜索学校..."
              class="px-3 py-2 border rounded-lg w-64"
            />
          </div>
        </div>
      </div>

      <!-- 学校列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">编码</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">校长</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="school in schools" :key="school.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ school.name }}</div>
                <div class="text-sm text-gray-500">{{ school.address }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ school.code }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                  {{ school.school_type }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ school.principal || '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full"
                      :class="school.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                  {{ school.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button @click="editSchool(school)" class="text-blue-600 hover:text-blue-900">
                    编辑
                  </button>
                  <button @click="openClassroomManager(school)" class="text-indigo-600 hover:text-indigo-900">
                    班级管理
                  </button>
                  <button @click="deleteSchool(school)" class="text-red-600 hover:text-red-900">
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
          显示 {{ (schoolPage - 1) * schoolPageSize + 1 }} - {{ Math.min(schoolPage * schoolPageSize, schoolTotal) }} 条，共 {{ schoolTotal }} 条
        </div>
        <div class="flex gap-2">
          <button
            @click="prevSchoolPage"
            :disabled="schoolPage === 1"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            上一页
          </button>
          <span class="px-3 py-2">{{ schoolPage }} / {{ schoolTotalPages }}</span>
          <button
            @click="nextSchoolPage"
            :disabled="schoolPage === schoolTotalPages"
            class="px-3 py-2 border rounded-lg disabled:opacity-50"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 学校批量导入对话框 -->
    <el-dialog
      v-model="showSchoolImportDialog"
      title="批量导入学校"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="school-import-content">
        <!-- 步骤指示 -->
        <el-steps :active="importStep" finish-status="success" style="margin-bottom: 20px;">
          <el-step title="下载模板" />
          <el-step title="上传文件" />
          <el-step title="导入结果" />
        </el-steps>

        <!-- 步骤1: 下载模板 -->
        <div v-if="importStep === 0" class="import-step">
          <el-alert
            title="导入说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <ul style="margin: 8px 0 0 0; padding-left: 20px;">
              <li>请先下载Excel模板，按照模板格式填写学校信息</li>
              <li>必需字段：区域名称、学校名称</li>
              <li>可选字段：学校代码、学校类型、地址、联系电话、邮箱、校长</li>
              <li>支持格式：.xlsx, .xls</li>
            </ul>
          </el-alert>

          <div class="template-fields">
            <h4>模板字段说明</h4>
            <el-table :data="templateFields" border size="small" style="margin-top: 10px;">
              <el-table-column prop="field" label="字段名" width="120" />
              <el-table-column prop="required" label="是否必填" width="100" />
              <el-table-column prop="description" label="说明" />
              <el-table-column prop="example" label="示例" width="150" />
            </el-table>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button type="primary" @click="downloadSchoolTemplate">
              <el-icon><Download /></el-icon>
              <span style="margin-left: 8px;">下载Excel模板</span>
            </el-button>
            <el-button @click="importStep = 1">
              已有模板，下一步
              <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 上传文件 -->
        <div v-if="importStep === 1" class="import-step">
          <el-form :model="importForm" label-width="120px">
            <el-form-item label="自动创建区域">
              <el-switch
                v-model="importForm.autoCreateRegion"
                active-text="是"
                inactive-text="否"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果区域不存在，是否自动创建
              </span>
            </el-form-item>
          </el-form>

          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 xlsx/xls 文件，且不超过 10MB
              </div>
            </template>
          </el-upload>

          <div v-if="selectedFile" class="file-info" style="margin-top: 20px;">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">{{ selectedFile.name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(selectedFile.size) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button @click="importStep = 0">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              @click="startSchoolImport"
              :loading="importing"
              :disabled="!selectedFile"
            >
              <el-icon><Upload /></el-icon>
              <span style="margin-left: 8px;">开始导入</span>
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 导入结果 -->
        <div v-if="importStep === 2" class="import-step">
          <el-alert
            :title="importResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
            :type="importResult.success > 0 ? 'success' : 'error'"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <div v-if="importResult.total > 0">
            <h4>📊 导入统计</h4>
            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="总记录数" :value="importResult.total" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成功" :value="importResult.success">
                  <template #suffix>
                    <span style="color: #67c23a;">✓</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="失败" :value="importResult.failed">
                  <template #suffix>
                    <span style="color: #f56c6c;">✗</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="创建学校" :value="importResult.created_schools" />
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="创建区域" :value="importResult.created_regions" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="更新学校" :value="importResult.updated_schools" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="跳过" :value="importResult.skipped_schools" />
              </el-col>
            </el-row>

            <div v-if="importResult.errors && importResult.errors.length > 0" style="margin-top: 20px;">
              <h4>⚠️ 错误详情</h4>
              <el-table :data="importResult.errors" max-height="300" size="small" style="margin-top: 10px;">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="message" label="错误信息" />
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="importStep < 2" @click="showSchoolImportDialog = false">取消</el-button>
        <el-button
          v-if="importStep === 2"
          type="primary"
          @click="closeSchoolImportDialog"
        >
          完成
        </el-button>
      </template>
    </el-dialog>

    <!-- 班级批量导入对话框（学校端） -->
    <el-dialog
      v-model="showClassroomImportDialog"
      title="批量导入班级"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="classroom-import-content">
        <!-- 步骤指示 -->
        <el-steps :active="classroomImportStep" finish-status="success" style="margin-bottom: 20px;">
          <el-step title="下载模板" />
          <el-step title="上传文件" />
          <el-step title="导入结果" />
        </el-steps>

        <!-- 步骤1: 下载模板 -->
        <div v-if="classroomImportStep === 0" class="import-step">
          <el-alert
            title="导入说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <ul style="margin: 8px 0 0 0; padding-left: 20px;">
              <li>请先下载Excel模板，按照模板格式填写班级信息</li>
              <li>必需字段：年级级别、班级编号</li>
              <li>可选字段：年级名称、班级名称、入学年份、班级容量、班级描述</li>
              <li>支持格式：.xlsx, .xls</li>
              <li><strong>注意：</strong>班主任信息不在导入模板中，请在班级创建后通过"班级成员管理"功能添加</li>
            </ul>
          </el-alert>

          <div v-if="classroomSchool" class="school-info" style="margin-bottom: 20px; padding: 12px; background: #f5f7fa; border-radius: 4px;">
            <strong>当前学校：</strong>{{ classroomSchool.name }}
          </div>

          <div class="template-fields">
            <h4>模板字段说明</h4>
            <el-table :data="classroomTemplateFields" border size="small" style="margin-top: 10px;">
              <el-table-column prop="field" label="字段名" width="120" />
              <el-table-column prop="required" label="是否必填" width="100" />
              <el-table-column prop="description" label="说明" />
              <el-table-column prop="example" label="示例" width="150" />
            </el-table>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button type="primary" @click="downloadClassroomTemplate">
              <el-icon><Download /></el-icon>
              <span style="margin-left: 8px;">下载Excel模板</span>
            </el-button>
            <el-button @click="classroomImportStep = 1">
              已有模板，下一步
              <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 上传文件 -->
        <div v-if="classroomImportStep === 1" class="import-step">
          <el-form :model="classroomImportForm" label-width="140px">
            <el-form-item label="统一设置入学年份">
              <el-input-number
                v-model="classroomImportForm.enrollmentYear"
                :min="1900"
                :max="2100"
                placeholder="留空则使用Excel中的值"
                style="width: 200px;"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果设置，将覆盖Excel中的所有入学年份
              </span>
            </el-form-item>
            <el-form-item label="统一设置班级容量">
              <el-input-number
                v-model="classroomImportForm.capacity"
                :min="1"
                :max="200"
                placeholder="留空则使用Excel中的值"
                style="width: 200px;"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果设置，将覆盖Excel中的所有班级容量
              </span>
            </el-form-item>
            <el-form-item label="更新已存在班级">
              <el-switch
                v-model="classroomImportForm.updateExisting"
                active-text="是"
                inactive-text="否"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果班级已存在，是否更新
              </span>
            </el-form-item>
          </el-form>

          <el-upload
            ref="classroomUploadRef"
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleClassroomFileChange"
            :on-exceed="handleClassroomExceed"
            accept=".xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 xlsx/xls 文件，且不超过 10MB
              </div>
            </template>
          </el-upload>

          <div v-if="selectedClassroomFile" class="file-info" style="margin-top: 20px;">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">{{ selectedClassroomFile.name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(selectedClassroomFile.size) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button @click="classroomImportStep = 0">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              @click="startClassroomImport"
              :loading="classroomImporting"
              :disabled="!selectedClassroomFile"
            >
              <el-icon><Upload /></el-icon>
              <span style="margin-left: 8px;">开始导入</span>
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 导入结果 -->
        <div v-if="classroomImportStep === 2" class="import-step">
          <el-alert
            :title="classroomImportResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
            :type="classroomImportResult.success > 0 ? 'success' : 'error'"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <div v-if="classroomImportResult.total > 0">
            <h4>📊 导入统计</h4>
            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="总记录数" :value="classroomImportResult.total" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成功" :value="classroomImportResult.success">
                  <template #suffix>
                    <span style="color: #67c23a;">✓</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="失败" :value="classroomImportResult.failed">
                  <template #suffix>
                    <span style="color: #f56c6c;">✗</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="创建" :value="classroomImportResult.created" />
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="更新" :value="classroomImportResult.updated" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="跳过" :value="classroomImportResult.skipped" />
              </el-col>
            </el-row>

            <div v-if="classroomImportResult.errors && classroomImportResult.errors.length > 0" style="margin-top: 20px;">
              <h4>⚠️ 错误详情</h4>
              <el-table :data="classroomImportResult.errors" max-height="300" size="small" style="margin-top: 10px;">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="message" label="错误信息" />
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="classroomImportStep < 2" @click="showClassroomImportDialog = false">取消</el-button>
        <el-button
          v-if="classroomImportStep === 2"
          type="primary"
          @click="closeClassroomImportDialog"
        >
          完成
        </el-button>
      </template>
    </el-dialog>

    <!-- 县区管理端班级批量导入对话框 -->
    <el-dialog
      v-model="showDistrictClassroomImportDialog"
      title="批量导入班级（支持多个学校）"
      width="800px"
      :close-on-click-modal="false"
    >
      <div class="classroom-import-content">
        <!-- 步骤指示 -->
        <el-steps :active="districtClassroomImportStep" finish-status="success" style="margin-bottom: 20px;">
          <el-step title="下载模板" />
          <el-step title="上传文件" />
          <el-step title="导入结果" />
        </el-steps>

        <!-- 步骤1: 下载模板 -->
        <div v-if="districtClassroomImportStep === 0" class="import-step">
          <el-alert
            title="导入说明"
            type="info"
            :closable="false"
            style="margin-bottom: 20px;"
          >
            <ul style="margin: 8px 0 0 0; padding-left: 20px;">
              <li>请先下载Excel模板，按照模板格式填写班级信息</li>
              <li>必需字段：学校名称、年级级别、班级编号</li>
              <li>可选字段：学校代码、年级名称、班级名称、入学年份、班级容量、班级描述</li>
              <li>支持格式：.xlsx, .xls</li>
              <li><strong>注意：</strong>可以一次导入多个学校的班级，Excel中需要包含学校信息</li>
              <li><strong>注意：</strong>班主任信息不在导入模板中，请在班级创建后通过"班级成员管理"功能添加</li>
            </ul>
          </el-alert>

          <div class="template-fields">
            <h4>模板字段说明</h4>
            <el-table :data="districtClassroomTemplateFields" border size="small" style="margin-top: 10px;">
              <el-table-column prop="field" label="字段名" width="120" />
              <el-table-column prop="required" label="是否必填" width="100" />
              <el-table-column prop="description" label="说明" />
              <el-table-column prop="example" label="示例" width="150" />
            </el-table>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button type="primary" @click="downloadDistrictClassroomTemplate">
              <el-icon><Download /></el-icon>
              <span style="margin-left: 8px;">下载Excel模板</span>
            </el-button>
            <el-button @click="districtClassroomImportStep = 1">
              已有模板，下一步
              <el-icon style="margin-left: 8px;"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 上传文件 -->
        <div v-if="districtClassroomImportStep === 1" class="import-step">
          <el-form :model="districtClassroomImportForm" label-width="140px">
            <el-form-item label="统一设置入学年份">
              <el-input-number
                v-model="districtClassroomImportForm.enrollmentYear"
                :min="1900"
                :max="2100"
                placeholder="留空则使用Excel中的值"
                style="width: 200px;"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果设置，将覆盖Excel中的所有入学年份
              </span>
            </el-form-item>
            <el-form-item label="统一设置班级容量">
              <el-input-number
                v-model="districtClassroomImportForm.capacity"
                :min="1"
                :max="200"
                placeholder="留空则使用Excel中的值"
                style="width: 200px;"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果设置，将覆盖Excel中的所有班级容量
              </span>
            </el-form-item>
            <el-form-item label="更新已存在班级">
              <el-switch
                v-model="districtClassroomImportForm.updateExisting"
                active-text="是"
                inactive-text="否"
              />
              <span style="margin-left: 10px; color: #909399; font-size: 12px;">
                如果班级已存在，是否更新
              </span>
            </el-form-item>
          </el-form>

          <el-upload
            ref="districtClassroomUploadRef"
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleDistrictClassroomFileChange"
            :on-exceed="handleDistrictClassroomExceed"
            accept=".xlsx,.xls"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 xlsx/xls 文件，且不超过 10MB
              </div>
            </template>
          </el-upload>

          <div v-if="selectedDistrictClassroomFile" class="file-info" style="margin-top: 20px;">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">{{ selectedDistrictClassroomFile.name }}</el-descriptions-item>
              <el-descriptions-item label="文件大小">{{ formatFileSize(selectedDistrictClassroomFile.size) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="step-actions" style="margin-top: 20px; text-align: center;">
            <el-button @click="districtClassroomImportStep = 0">
              <el-icon><ArrowLeft /></el-icon>
              上一步
            </el-button>
            <el-button
              type="primary"
              @click="startDistrictClassroomImport"
              :loading="districtClassroomImporting"
              :disabled="!selectedDistrictClassroomFile"
            >
              <el-icon><Upload /></el-icon>
              <span style="margin-left: 8px;">开始导入</span>
            </el-button>
          </div>
        </div>

        <!-- 步骤3: 导入结果 -->
        <div v-if="districtClassroomImportStep === 2" class="import-step">
          <el-alert
            :title="districtClassroomImportResult.success > 0 ? '✅ 导入完成' : '❌ 导入失败'"
            :type="districtClassroomImportResult.success > 0 ? 'success' : 'error'"
            :closable="false"
            style="margin-bottom: 20px;"
          />

          <div v-if="districtClassroomImportResult.total > 0">
            <h4>📊 导入统计</h4>
            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="总记录数" :value="districtClassroomImportResult.total" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="成功" :value="districtClassroomImportResult.success">
                  <template #suffix>
                    <span style="color: #67c23a;">✓</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="失败" :value="districtClassroomImportResult.failed">
                  <template #suffix>
                    <span style="color: #f56c6c;">✗</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="创建" :value="districtClassroomImportResult.created" />
              </el-col>
            </el-row>

            <el-row :gutter="20" style="margin-top: 10px;">
              <el-col :span="6">
                <el-statistic title="更新" :value="districtClassroomImportResult.updated" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="跳过" :value="districtClassroomImportResult.skipped" />
              </el-col>
            </el-row>

            <div v-if="districtClassroomImportResult.errors && districtClassroomImportResult.errors.length > 0" style="margin-top: 20px;">
              <h4>⚠️ 错误详情</h4>
              <el-table :data="districtClassroomImportResult.errors" max-height="300" size="small" style="margin-top: 10px;">
                <el-table-column prop="row" label="行号" width="80" />
                <el-table-column prop="field" label="字段" width="120" />
                <el-table-column prop="message" label="错误信息" />
              </el-table>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="districtClassroomImportStep < 2" @click="showDistrictClassroomImportDialog = false">取消</el-button>
        <el-button
          v-if="districtClassroomImportStep === 2"
          type="primary"
          @click="closeDistrictClassroomImportDialog"
        >
          完成
        </el-button>
      </template>
    </el-dialog>

    <!-- 班级成员管理 -->
    <div v-if="activeTab === 'classrooms'" class="space-y-6">
      <!-- 功能说明 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p class="text-sm text-blue-800">
          💡 <strong>功能说明：</strong>此页面专门用于管理所有班级的成员（添加教师、学生到班级）。班级信息的创建、编辑和删除请在"学校管理"标签页中的"班级管理"功能中操作。
        </p>
      </div>
      <!-- 操作栏 -->
      <div class="bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center">
          <div class="flex gap-4">
            <button
              @click="loadAllClassrooms"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              🔄 刷新
            </button>
          </div>
          <div class="flex gap-2">
            <select
              v-model="allClassroomRegionFilter"
              @change="handleRegionFilterChange"
              class="px-3 py-2 border rounded-lg"
            >
              <option value="">所有县区</option>
              <option v-for="region in allRegions" :key="region.id" :value="region.id">
                {{ region.name }}
              </option>
            </select>
            <select
              v-model="allClassroomSchoolFilter"
              @change="loadAllClassrooms"
              class="px-3 py-2 border rounded-lg"
            >
              <option value="">所有学校</option>
              <option v-for="school in filteredSchoolsForClassroom" :key="school.id" :value="school.id">
                {{ school.name }}
              </option>
            </select>
            <select
              v-model="allClassroomGradeFilter"
              @change="handleGradeFilterChange"
              class="px-3 py-2 border rounded-lg"
            >
              <option value="">所有年级</option>
              <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                {{ grade.name }}
              </option>
            </select>
            <input
              v-model="allClassroomSearchQuery"
              @keyup.enter="loadAllClassrooms"
              type="text"
              placeholder="搜索学校或班级名称..."
              class="px-3 py-2 border rounded-lg w-64"
            />
          </div>
        </div>
      </div>

      <!-- 班级列表 -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div v-if="allClassroomsLoading" class="p-6 text-center text-gray-500">
          加载中...
        </div>
        <div v-else-if="allClassrooms.length === 0" class="p-6 text-center text-gray-500">
          暂无班级
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">班级名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学校</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">年级</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="classroom in allClassrooms" :key="classroom.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ classroom.name }}</div>
                <div class="text-xs text-gray-500">编码：{{ classroom.code || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getSchoolNameById(classroom.school_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ getGradeName(classroom.grade_id) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="classroom.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                >
                  {{ classroom.is_active ? '激活' : '未激活' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="openMemberManager(classroom)"
                  class="text-indigo-600 hover:text-indigo-900 font-medium"
                >
                  成员管理
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 区域编辑模态框 -->
    <div v-if="showRegionModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingRegion ? '编辑区域' : '创建区域' }}
        </h3>
        <form @submit.prevent="saveRegion">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">区域名称</label>
              <input
                v-model="regionForm.name"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">区域编码</label>
              <input
                v-model="regionForm.code"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">级别</label>
              <select v-model="regionForm.level" class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option :value="1">省级</option>
                <option :value="2">市级</option>
                <option :value="3">区级</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">描述</label>
              <textarea
                v-model="regionForm.description"
                rows="3"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              ></textarea>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="regionForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活状态</span>
              </label>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeRegionModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingRegion ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 学校编辑模态框 -->
    <div v-if="showSchoolModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingSchool ? '编辑学校' : '创建学校' }}
        </h3>
        <form @submit.prevent="saveSchool">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">学校名称</label>
              <input
                v-model="schoolForm.name"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">学校编码</label>
              <input
                v-model="schoolForm.code"
                type="text"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">学校类型</label>
              <select v-model="schoolForm.school_type" class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="小学">小学</option>
                <option value="初中">初中</option>
                <option value="高中">高中</option>
                <option value="大学">大学</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">所属区域</label>
              <select v-model="schoolForm.region_id" required class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2">
                <option value="">请选择区域</option>
                <option v-for="region in allRegions" :key="region.id" :value="region.id">
                  {{ region.name }}
                </option>
              </select>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700">学校地址</label>
              <input
                v-model="schoolForm.address"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">联系电话</label>
              <input
                v-model="schoolForm.phone"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">邮箱</label>
              <input
                v-model="schoolForm.email"
                type="email"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">校长姓名</label>
              <input
                v-model="schoolForm.principal"
                type="text"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              />
            </div>
            <div>
              <label class="flex items-center mt-6">
                <input v-model="schoolForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活状态</span>
              </label>
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700">描述</label>
              <textarea
                v-model="schoolForm.description"
                rows="3"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              ></textarea>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeSchoolModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingSchool ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 班级管理抽屉 -->
    <div v-if="showClassroomManager" class="fixed inset-0 bg-gray-800 bg-opacity-40 flex justify-end z-50">
      <div class="w-full max-w-4xl h-full bg-white shadow-xl flex flex-col">
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">
              {{ classroomSchool?.name }} - 班级信息管理
            </h3>
            <p class="text-sm text-gray-500 mt-1">
              管理该学校的班级信息（创建、编辑、删除班级）。如需管理班级成员（添加教师、学生），请切换到"班级成员管理"标签页。
            </p>
          </div>
          <button @click="closeClassroomManager" class="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <div class="px-6 py-4 border-b flex flex-wrap gap-3 items-center">
          <button
            @click="openCreateClassroomModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            :disabled="!classroomSchool"
          >
            + 新增班级
          </button>
          <button
            @click="openClassroomImportDialog"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            :disabled="!classroomSchool"
          >
            📥 批量导入
          </button>
          <button
            @click="loadClassrooms"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            🔄 刷新
          </button>
          <select
            v-model="classroomGradeFilter"
            @change="handleClassroomFilterChange"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="">全部年级</option>
            <option v-for="grade in grades" :key="grade.id" :value="grade.id">
              {{ grade.name }}
            </option>
          </select>
          <input
            v-model="classroomSearchQuery"
            @keyup.enter="handleClassroomFilterChange"
            type="text"
            placeholder="搜索班级名称或编码..."
            class="px-3 py-2 border rounded-lg flex-1 min-w-[200px]"
          />
        </div>

        <div class="flex-1 overflow-y-auto">
          <div v-if="classroomLoading" class="p-6 text-center text-gray-500">
            班级数据加载中...
          </div>
          <div v-else class="p-6">
            <div v-if="classrooms.length === 0" class="text-center text-gray-500 py-12 border-2 border-dashed rounded-lg">
              暂无班级，请点击上方“新增班级”创建。
            </div>
            <div v-else class="bg-white rounded-lg shadow overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      班级名称
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      年级
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      入学年份
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      状态
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="classroom in classrooms" :key="classroom.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="text-sm font-medium text-gray-900">{{ classroom.name }}</div>
                      <div class="text-xs text-gray-500">
                        编码：{{ classroom.code || '—' }}
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ getGradeName(classroom.grade_id) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ classroom.enrollment_year || '—' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                        :class="classroom.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                      >
                        {{ classroom.is_active ? '激活' : '未激活' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div class="flex gap-2">
                        <button @click="editClassroom(classroom)" class="text-blue-600 hover:text-blue-900">
                          编辑
                        </button>
                        <button @click="deleteClassroom(classroom)" class="text-red-600 hover:text-red-900">
                          删除
                        </button>
                      </div>
                      <div class="mt-1">
                        <button @click="openMemberManager(classroom)" class="text-xs text-indigo-600 hover:text-indigo-900">
                          管理成员 →
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t flex justify-between items-center">
          <div class="text-sm text-gray-600">
            显示 {{ (classroomPage - 1) * classroomPageSize + (classrooms.length ? 1 : 0) }} -
            {{ Math.min(classroomPage * classroomPageSize, classroomTotal) }} 条，共 {{ classroomTotal }} 条
          </div>
          <div class="flex gap-2">
            <button
              @click="prevClassroomPage"
              :disabled="classroomPage === 1"
              class="px-3 py-2 border rounded-lg disabled:opacity-50"
            >
              上一页
            </button>
            <span class="px-3 py-2 text-sm text-gray-600">{{ classroomPage }} / {{ classroomTotalPages || 1 }}</span>
            <button
              @click="nextClassroomPage"
              :disabled="classroomPage === classroomTotalPages || classroomTotalPages === 0"
              class="px-3 py-2 border rounded-lg disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 成员管理模态框 -->
    <div v-if="showMemberManager" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div class="px-6 py-4 border-b flex items-center justify-between">
          <div>
            <h3 class="text-xl font-semibold text-gray-900">
              {{ selectedClassroom?.name }} - 成员管理
            </h3>
            <p class="text-sm text-gray-500 mt-1">管理班级成员，添加、编辑和移除成员</p>
          </div>
          <button @click="closeMemberManager" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="px-6 py-4 border-b">
          <div class="flex items-center justify-between mb-3">
            <div class="flex gap-2">
              <button
                @click="openAddMemberModal"
                class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                + 添加成员
              </button>
            </div>
            <button
              @click="loadMembers"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              🔄 刷新
            </button>
          </div>
          <div class="text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-2">
            💡 <strong>提示：</strong>添加学生成员时，建议填写<strong>学号</strong>和<strong>座号</strong>，便于后续的考勤管理和座位管理。未填写的信息显示为"未填写"，可以通过"编辑"按钮补充。
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="membersLoading" class="text-center text-gray-500 py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            加载中...
          </div>
          <div v-else-if="members.length === 0" class="text-center text-gray-500 py-12 border-2 border-dashed rounded-lg">
            暂无成员，请点击"添加成员"按钮添加
          </div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">姓名</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户名/邮箱</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">学号</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">座号</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">职务</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="member in members" :key="member.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <div class="font-medium text-gray-900">{{ member.userFullName || member.userName || '未设置' }}</div>
                    <div class="text-xs text-gray-500">ID: {{ member.userId }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>{{ member.userUsername || '—' }}</div>
                    <div class="text-xs text-gray-400">{{ member.userEmail || '' }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getRoleBadgeClass(member.roleInClass)">
                      {{ getRoleName(member.roleInClass) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span v-if="member.studentNo" class="text-gray-900 font-medium">{{ member.studentNo }}</span>
                    <span v-else class="text-gray-400 italic">未填写</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm">
                    <span v-if="member.seatNo !== null && member.seatNo !== undefined" class="text-gray-900 font-medium">{{ member.seatNo }}</span>
                    <span v-else class="text-gray-400 italic">未填写</span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ member.cadreTitle || '—' }}</td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                      :class="member.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    >
                      {{ member.isActive ? '活跃' : '非活跃' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div class="flex gap-2">
                      <button @click="editMember(member)" class="text-blue-600 hover:text-blue-900">
                        编辑
                      </button>
                      <button @click="removeMember(member)" class="text-red-600 hover:text-red-900">
                        移除
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑成员模态框 -->
    <div v-if="showMemberModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="px-6 py-4 border-b flex items-center justify-between flex-shrink-0">
          <h3 class="text-lg font-semibold text-gray-900">
            {{ editingMember ? '编辑成员' : '添加成员' }}
          </h3>
          <button @click="closeMemberModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto">
          <form @submit.prevent="saveMember" class="p-6 space-y-4">
          <!-- 添加模式切换 -->
          <div v-if="!editingMember" class="mb-4">
            <div class="flex gap-2">
              <button
                type="button"
                @click="batchAddMode = false"
                :class="[
                  'flex-1 px-4 py-2 rounded-lg border transition-colors',
                  !batchAddMode
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                ]"
              >
                单个添加
              </button>
              <button
                type="button"
                @click="batchAddMode = true; loadSourceClassroomStudents()"
                :class="[
                  'flex-1 px-4 py-2 rounded-lg border transition-colors',
                  batchAddMode
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                ]"
              >
                批量添加（从班级选择）
              </button>
            </div>
          </div>

          <!-- 批量添加模式 -->
          <div v-if="!editingMember && batchAddMode" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                选择来源班级 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="sourceClassroomFilter"
                @change="loadSourceClassroomStudents"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">请选择班级</option>
                <option v-for="classroom in allClassrooms" :key="classroom.id" :value="classroom.id">
                  {{ classroom.name }} ({{ classroom.code || `ID: ${classroom.id}` }})
                </option>
              </select>
              <p class="text-xs text-gray-500 mt-1">
                💡 提示：选择一个班级后，将显示该班级的所有学生，可以选择多个学生批量添加到当前班级
              </p>
            </div>

            <div v-if="sourceStudentsLoading" class="text-center text-gray-500 py-4 text-sm">
              加载中...
            </div>
            <div v-else-if="sourceClassroomFilter && sourceClassroomStudents.length > 0" class="border border-gray-300 rounded-lg">
              <div class="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                <span class="text-sm font-medium text-gray-700">
                  学生列表（{{ sourceClassroomStudents.length }} 人）
                </span>
                <button
                  type="button"
                  @click="toggleSelectAllStudents"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  {{ selectedStudentIds.size === sourceClassroomStudents.length ? '取消全选' : '全选' }}
                </button>
              </div>
              <div class="max-h-64 overflow-y-auto">
                <div
                  v-for="student in sourceClassroomStudents"
                  :key="student.userId"
                  @click="toggleStudentSelection(student.userId)"
                  class="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 flex items-center gap-3"
                  :class="{ 'bg-blue-50': selectedStudentIds.has(student.userId) }"
                >
                  <input
                    type="checkbox"
                    :checked="selectedStudentIds.has(student.userId)"
                    @click.stop="toggleStudentSelection(student.userId)"
                    class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div class="flex-1">
                    <div class="font-medium text-gray-900">{{ student.userFullName || student.userName || '未设置' }}</div>
                    <div class="text-xs text-gray-500">
                      ID: {{ student.userId }} | {{ student.userUsername || '' }}
                      <span v-if="student.studentNo" class="ml-2 text-blue-600">学号: {{ student.studentNo }}</span>
                      <span v-if="student.seatNo !== null && student.seatNo !== undefined" class="ml-2">座号: {{ student.seatNo }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="selectedStudentIds.size > 0" class="bg-blue-50 px-4 py-2 border-t border-gray-200">
                <span class="text-sm text-blue-700 font-medium">已选择 {{ selectedStudentIds.size }} 个学生</span>
              </div>
            </div>
            <div v-else-if="sourceClassroomFilter && !sourceStudentsLoading" class="text-center text-gray-500 py-4 text-sm border border-gray-200 rounded-lg">
              该班级暂无学生
            </div>
          </div>

          <!-- 单个添加模式 -->
          <div v-if="!editingMember && !batchAddMode">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              选择用户 <span class="text-red-500">*</span>
            </label>
            <div class="space-y-2">
              <div class="flex gap-2">
                <input
                  v-model="userSearchQuery"
                  @input="searchUsersForMember"
                  type="text"
                  placeholder="搜索用户名、姓名或邮箱..."
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <select
                  v-model="userRoleFilter"
                  @change="onUserRoleFilterChange"
                  class="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">所有角色</option>
                  <option value="teacher">教师</option>
                  <option value="student">学生</option>
                </select>
              </div>
              <div v-if="userSearchLoading" class="text-center text-gray-500 py-2 text-sm">
                搜索中...
              </div>
              <div
                v-else-if="searchedUsers.length > 0"
                class="max-h-48 overflow-y-auto border border-gray-300 rounded-lg"
              >
                <div
                  v-for="user in searchedUsers"
                  :key="user.id"
                  @click="selectUserForMember(user)"
                  class="px-3 py-2 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                  :class="{ 'bg-blue-100': memberForm.userId === user.id }"
                >
                  <div class="font-medium text-gray-900">{{ user.full_name || user.username }}</div>
                  <div class="text-xs text-gray-500">
                    ID: {{ user.id }} | {{ user.username }} | {{ user.email }}
                    <span v-if="user.classroom_name" class="text-blue-600">(当前班级: {{ user.classroom_name }})</span>
                  </div>
                </div>
              </div>
              <div v-else-if="userSearchQuery && !userSearchLoading" class="text-center text-gray-500 py-2 text-sm border border-gray-200 rounded-lg">
                未找到用户，请尝试其他搜索关键词
              </div>
              <div v-if="selectedUserInfo" class="p-2 bg-blue-50 border border-blue-200 rounded-lg">
                <div class="text-sm font-medium text-blue-900">已选择：{{ selectedUserInfo.full_name || selectedUserInfo.username }}</div>
                <div class="text-xs text-blue-700">ID: {{ selectedUserInfo.id }} | {{ selectedUserInfo.email }}</div>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              提示：搜索用户并点击选择，或直接在下方输入用户ID
            </p>
          </div>
          <div v-if="!editingMember && !batchAddMode">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              或直接输入用户ID <span class="text-red-500">*</span>
            </label>
            <input
              v-model.number="memberForm.userId"
              type="number"
              required
              placeholder="请输入用户ID"
              @input="onUserIdInput"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div v-else>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              用户ID
            </label>
            <input
              :value="memberForm.userId"
              type="number"
              disabled
              class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
            />
            <p class="text-xs text-gray-500 mt-1">编辑模式下无法更改用户</p>
          </div>

          <div v-if="!batchAddMode">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              角色 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="memberForm.roleInClass"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="RoleInClass.HEAD_TEACHER_PRIMARY">正班主任</option>
              <option :value="RoleInClass.HEAD_TEACHER_DEPUTY">副班主任</option>
              <option :value="RoleInClass.SUBJECT_TEACHER">任课教师</option>
              <option :value="RoleInClass.CADRE">班干部</option>
              <option :value="RoleInClass.STUDENT">学生</option>
            </select>
          </div>

          <div v-if="!batchAddMode && memberForm.roleInClass === RoleInClass.STUDENT">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              学号
              <span class="text-gray-500 text-xs font-normal ml-1">(建议填写，便于管理)</span>
            </label>
            <input
              v-model="memberForm.studentNo"
              type="text"
              placeholder="请输入学号，如：2024001"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">
              💡 提示：学号用于标识学生身份，建议填写完整的学号信息
            </p>
          </div>

          <div v-if="memberForm.roleInClass === RoleInClass.STUDENT">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              座号
              <span class="text-gray-500 text-xs font-normal ml-1">(建议填写)</span>
            </label>
            <input
              v-model.number="memberForm.seatNo"
              type="number"
              placeholder="请输入座号，如：1"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">
              💡 提示：座号用于课堂座位管理和考勤记录
            </p>
          </div>

          <div v-if="!batchAddMode && memberForm.roleInClass === RoleInClass.CADRE">
            <label class="block text-sm font-medium text-gray-700 mb-2">职务名称</label>
            <input
              v-model="memberForm.cadreTitle"
              type="text"
              placeholder="请输入职务名称（如：班长、学习委员等）"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div v-if="!batchAddMode">
            <label class="flex items-center">
              <input
                v-model="memberForm.isPrimaryClass"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="ml-2 text-sm text-gray-700">设为主班级/默认进入班级</span>
            </label>
            <div class="mt-2 text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded-lg p-2">
              💡 <strong>主班级说明：</strong>
              <ul class="list-disc list-inside mt-1 space-y-0.5">
                <li>当一个学生同时属于多个班级时，标记为"主班级"的班级会作为默认班级使用</li>
                <li>系统在查询学生统计信息、显示班级信息时会优先使用主班级的数据</li>
                <li>如果学生只属于一个班级，建议勾选此项</li>
                <li>如果学生属于多个班级，建议将最重要的班级（如主修班）标记为主班级</li>
              </ul>
            </div>
          </div>

          <div v-if="memberError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {{ memberError }}
          </div>
          </form>
        </div>

        <div class="px-6 py-4 border-t flex justify-end gap-3 flex-shrink-0 bg-white">
          <button
            type="button"
            @click="closeMemberModal"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
          >
            取消
          </button>
          <button
            type="button"
            @click="batchAddMode ? batchAddMembers() : saveMember()"
            :disabled="memberSaving || (batchAddMode && selectedStudentIds.size === 0)"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ memberSaving ? '保存中...' : (batchAddMode ? `批量添加 (${selectedStudentIds.size})` : '保存') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 班级编辑模态框 -->
    <div v-if="showClassroomModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-lg">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingClassroom ? '编辑班级' : '创建班级' }}
        </h3>
        <form @submit.prevent="saveClassroom">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">班级名称</label>
              <input
                v-model="classroomForm.name"
                type="text"
                required
                placeholder="01 或 10"
                @input="classroomNameError = ''"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
                :class="{ 'border-red-500': classroomNameError }"
              />
              <p class="mt-1 text-xs text-gray-500">
                格式说明：1-9班请使用 01-09 格式（例如：01 表示1班）；10班及以上使用正常数字格式（例如：10 表示10班，11 表示11班）
              </p>
              <p v-if="classroomNameError" class="mt-1 text-xs text-red-600">
                {{ classroomNameError }}
              </p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">所属年级</label>
              <select
                v-model="classroomForm.grade_id"
                required
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              >
                <option value="">请选择年级</option>
                <option v-for="grade in grades" :key="grade.id" :value="grade.id">
                  {{ grade.name }} (ID: {{ grade.id }})
                </option>
              </select>
              <p class="mt-1 text-xs text-gray-500">
                💡 提示：年级名称后括号内显示的是年级ID，导入用户时可使用此ID
              </p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">入学年份</label>
                <input
                  v-model="classroomForm.enrollment_year"
                  type="number"
                  min="1990"
                  max="2099"
                  class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">班级编码</label>
                <input
                  v-model="classroomForm.code"
                  type="text"
                  class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-100 text-gray-600"
                  disabled
                />
                <p class="mt-1 text-xs text-gray-500">
                  自动生成，格式为“入学年份 + 班级名称”，例如 2025 + 01 = 202501
                </p>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">描述</label>
              <textarea
                v-model="classroomForm.description"
                rows="3"
                class="mt-1 block w-full border border-gray-300 rounded-lg px-3 py-2"
              ></textarea>
            </div>
            <div>
              <label class="flex items-center">
                <input v-model="classroomForm.is_active" type="checkbox" class="mr-2" />
                <span class="text-sm text-gray-700">激活状态</span>
              </label>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button
              type="button"
              @click="closeClassroomModal"
              class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {{ editingClassroom ? '更新' : '创建' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import adminService, { type Region, type School, type Classroom, type User, type SchoolImportResponse, type ClassroomImportResponse } from '@/services/admin'
import curriculumService from '@/services/curriculum'
import { classroomAssistantService } from '@/services/classroomAssistant'
import type { Grade } from '@/types/curriculum'
import type {
  ClassroomMembership,
  ClassroomMembershipCreate,
  ClassroomMembershipUpdate,
} from '@/types/classroomAssistant'
import { RoleInClass } from '@/types/classroomAssistant'
import { Download, UploadFilled, Upload, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import type { UploadFile, UploadProps } from 'element-plus'
import * as XLSX from 'xlsx'

const toast = useToast()

// 标签页状态
const activeTab = ref<'regions' | 'schools' | 'classrooms'>('regions')

// 区域管理状态
const regions = ref<Region[]>([])
const regionPage = ref(1)
const regionPageSize = ref(10)
const regionTotal = ref(0)
const regionLevelFilter = ref('')
const regionSearchQuery = ref('')
const showRegionModal = ref(false)
const editingRegion = ref<Region | null>(null)
const regionForm = ref({
  name: '',
  code: '',
  level: 1,
  description: '',
  is_active: true
})

// 学校管理状态
const schools = ref<School[]>([])
const schoolPage = ref(1)
const schoolPageSize = ref(10)
const schoolTotal = ref(0)
const schoolTypeFilter = ref('')
const schoolSearchQuery = ref('')
const showSchoolModal = ref(false)
const editingSchool = ref<School | null>(null)
const allRegions = ref<Region[]>([])
const schoolForm = ref({
  name: '',
  code: '',
  region_id: '',
  school_type: '小学',
  address: '',
  phone: '',
  email: '',
  principal: '',
  description: '',
  is_active: true
})

// 学校批量导入状态
const showSchoolImportDialog = ref(false)
const importStep = ref(0)
const selectedFile = ref<File | null>(null)
const uploadRef = ref()
const importing = ref(false)
const importForm = ref({
  autoCreateRegion: true
})
const importResult = ref<SchoolImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created_regions: 0,
  created_schools: 0,
  updated_schools: 0,
  skipped_schools: 0,
  errors: []
})
const templateFields = [
  { field: '区域名称', required: '✅ 必填', description: '市或区名称，如：北京市、朝阳区', example: '北京市' },
  { field: '学校名称', required: '✅ 必填', description: '学校全称', example: '北京市第一中学' },
  { field: '学校代码', required: '⭕ 选填', description: '学校代码，用于精确匹配', example: '10001' },
  { field: '学校类型', required: '⭕ 选填', description: '小学/初中/高中/大学', example: '高中' },
  { field: '地址', required: '⭕ 选填', description: '学校地址', example: '北京市XX区XX路' },
  { field: '联系电话', required: '⭕ 选填', description: '联系电话', example: '010-12345678' },
  { field: '邮箱', required: '⭕ 选填', description: '邮箱地址', example: 'school@example.com' },
  { field: '校长', required: '⭕ 选填', description: '校长姓名', example: '张校长' },
]

// 班级管理状态
const showClassroomManager = ref(false)
const classroomSchool = ref<School | null>(null)
const classrooms = ref<Classroom[]>([])
const classroomLoading = ref(false)
const classroomPage = ref(1)
const classroomPageSize = ref(50)
const classroomTotal = ref(0)
const grades = ref<Grade[]>([])
const classroomSearchQuery = ref('')
const classroomGradeFilter = ref<number | ''>('')
const showClassroomModal = ref(false)
const editingClassroom = ref<Classroom | null>(null)
const classroomForm = ref({
  name: '',
  grade_id: '',
  enrollment_year: new Date().getFullYear().toString(),
  code: '',
  description: '',
  is_active: true,
})
const classroomNameError = ref('')

// 所有班级列表状态（用于班级成员管理标签页）
const allClassrooms = ref<Classroom[]>([])
const allClassroomsLoading = ref(false)
const allClassroomSearchQuery = ref('')
const allClassroomRegionFilter = ref<number | ''>('')
const allClassroomSchoolFilter = ref<number | ''>('')
const allClassroomGradeFilter = ref<number | ''>('')

// 计算属性：根据县区和年级筛选过滤学校列表
const filteredSchoolsForClassroom = computed(() => {
  let filtered = schools.value

  // 根据县区筛选
  if (allClassroomRegionFilter.value) {
    filtered = filtered.filter(school => school.region_id === Number(allClassroomRegionFilter.value))
  }

  // 根据年级筛选：只显示该年级下有班级的学校
  if (allClassroomGradeFilter.value) {
    // 从已加载的班级列表中提取该年级下的学校ID
    const schoolIdsInGrade = new Set(
      allClassrooms.value
        .filter(c => c.grade_id === Number(allClassroomGradeFilter.value))
        .map(c => c.school_id)
    )
    // 只保留这些学校
    filtered = filtered.filter(school => schoolIdsInGrade.has(school.id))
  }

  return filtered
})

// 班级批量导入状态
const showClassroomImportDialog = ref(false)
const classroomImportStep = ref(0)
const selectedClassroomFile = ref<File | null>(null)
const classroomUploadRef = ref()
const classroomImporting = ref(false)
const classroomImportForm = ref({
  enrollmentYear: undefined as number | undefined,
  capacity: undefined as number | undefined,
  updateExisting: false
})
const classroomImportResult = ref<ClassroomImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: []
})
const classroomTemplateFields = [
  { field: '年级级别', required: '✅ 必填', description: '年级级别1-12（如：7表示七年级，10表示高一）', example: '7' },
  { field: '年级名称', required: '⭕ 选填', description: '年级名称（如不填写，将根据年级级别自动获取）', example: '七年级' },
  { field: '班级编号', required: '✅ 必填', description: '班级编码（唯一标识，如：701表示7年级1班）', example: '701' },
  { field: '班级名称', required: '⭕ 选填', description: '班级名称（如不填写，将根据班级编号和年级名称自动生成）', example: '七年级1班' },
  { field: '入学年份', required: '⭕ 选填', description: '入学年份/届别（可在导入界面统一设置）', example: '2024' },
  { field: '班级容量', required: '⭕ 选填', description: '计划人数（可在导入界面统一设置）', example: '45' },
  { field: '班级描述', required: '⭕ 选填', description: '班级描述信息', example: '重点班' },
]

// 县区管理端班级批量导入状态
const showDistrictClassroomImportDialog = ref(false)
const districtClassroomImportStep = ref(0)
const selectedDistrictClassroomFile = ref<File | null>(null)
const districtClassroomUploadRef = ref()
const districtClassroomImporting = ref(false)
const districtClassroomImportForm = ref({
  enrollmentYear: undefined as number | undefined,
  capacity: undefined as number | undefined,
  updateExisting: false
})
const districtClassroomImportResult = ref<ClassroomImportResponse>({
  total: 0,
  success: 0,
  failed: 0,
  created: 0,
  updated: 0,
  skipped: 0,
  errors: []
})
const districtClassroomTemplateFields = [
  { field: '学校名称', required: '✅ 必填', description: '学校全称（用于匹配学校）', example: '开平市第一中学' },
  { field: '学校代码', required: '⭕ 选填', description: '学校代码（用于精确匹配，优先于学校名称）', example: '10001' },
  { field: '年级级别', required: '✅ 必填', description: '年级级别1-12（如：7表示七年级，10表示高一）', example: '7' },
  { field: '年级名称', required: '⭕ 选填', description: '年级名称（如不填写，将根据年级级别自动获取）', example: '七年级' },
  { field: '班级编号', required: '✅ 必填', description: '班级编码（唯一标识，如：701表示7年级1班）', example: '701' },
  { field: '班级名称', required: '⭕ 选填', description: '班级名称（如不填写，将根据班级编号和年级名称自动生成）', example: '七年级1班' },
  { field: '入学年份', required: '⭕ 选填', description: '入学年份/届别（可在导入界面统一设置）', example: '2024' },
  { field: '班级容量', required: '⭕ 选填', description: '计划人数（可在导入界面统一设置）', example: '45' },
  { field: '班级描述', required: '⭕ 选填', description: '班级描述信息', example: '重点班' },
]

// 成员管理状态
const showMemberManager = ref(false)
const selectedClassroom = ref<Classroom | null>(null)
const members = ref<ClassroomMembership[]>([])
const membersLoading = ref(false)
const showMemberModal = ref(false)
const editingMember = ref<ClassroomMembership | null>(null)
const memberSaving = ref(false)
const memberError = ref('')
const memberForm = ref<ClassroomMembershipCreate & { userId: number }>({
  classroomId: 0,
  userId: 0,
  roleInClass: RoleInClass.STUDENT,
  studentNo: null,
  seatNo: null,
  cadreTitle: null,
  isPrimaryClass: false,
})

// 用户搜索状态（用于添加成员）
const userSearchQuery = ref('')
const userRoleFilter = ref<string>('')
const searchedUsers = ref<User[]>([])
const userSearchLoading = ref(false)
const selectedUserInfo = ref<User | null>(null)

// 批量添加成员状态
const batchAddMode = ref(false) // true: 批量模式, false: 单个模式
const sourceClassroomFilter = ref<number | ''>('') // 筛选来源班级
const sourceClassroomStudents = ref<ClassroomMembership[]>([])
const sourceStudentsLoading = ref(false)
const selectedStudentIds = ref<Set<number>>(new Set()) // 选中的学生ID集合

// 计算属性
const regionTotalPages = computed(() => Math.ceil(regionTotal.value / regionPageSize.value))
const schoolTotalPages = computed(() => Math.ceil(schoolTotal.value / schoolPageSize.value))
const classroomTotalPages = computed(() => Math.ceil(classroomTotal.value / classroomPageSize.value))

// 区域管理方法
function getRegionLevelName(level: number): string {
  const levelMap = { 1: '省级', 2: '市级', 3: '区级' }
  return levelMap[level] || '未知'
}

function getRegionLevelClass(level: number): string {
  const classMap = {
    1: 'bg-red-100 text-red-800',
    2: 'bg-blue-100 text-blue-800',
    3: 'bg-green-100 text-green-800'
  }
  return classMap[level] || 'bg-gray-100 text-gray-800'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

async function loadRegions() {
  try {
    const response = await adminService.getRegions({
      page: regionPage.value,
      size: regionPageSize.value,
      level: regionLevelFilter.value ? parseInt(regionLevelFilter.value) : undefined,
      search: regionSearchQuery.value || undefined
    })
    regions.value = response.regions
    regionTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load regions:', error)
    toast.error(error.response?.data?.detail || '加载区域列表失败')
  }
}

async function loadAllRegions() {
  try {
    const response = await adminService.getRegions({ size: 100 })
    allRegions.value = response.regions
  } catch (error: any) {
    console.error('Failed to load all regions:', error)
  }
}

async function loadGradesList() {
  try {
    grades.value = await curriculumService.getGrades()
  } catch (error: any) {
    console.error('Failed to load grades:', error)
    toast.error(error.response?.data?.detail || '加载年级列表失败')
  }
}

function searchRegions() {
  regionPage.value = 1
  loadRegions()
}

function openCreateRegionModal() {
  editingRegion.value = null
  regionForm.value = {
    name: '',
    code: '',
    level: 1,
    description: '',
    is_active: true
  }
  showRegionModal.value = true
}

function editRegion(region: Region) {
  editingRegion.value = region
  regionForm.value = {
    name: region.name,
    code: region.code,
    level: region.level,
    description: region.description || '',
    is_active: region.is_active
  }
  showRegionModal.value = true
}

function closeRegionModal() {
  showRegionModal.value = false
  editingRegion.value = null
}

async function saveRegion() {
  try {
    if (editingRegion.value) {
      await adminService.updateRegion(editingRegion.value.id, regionForm.value)
      toast.success('区域更新成功')
    } else {
      await adminService.createRegion(regionForm.value)
      toast.success('区域创建成功')
    }
    closeRegionModal()
    loadRegions()
  } catch (error: any) {
    console.error('Failed to save region:', error)
    toast.error(error.response?.data?.detail || '保存区域失败')
  }
}

async function deleteRegion(region: Region) {
  if (!confirm(`确定要删除区域 ${region.name} 吗？`)) {
    return
  }
  
  try {
    await adminService.deleteRegion(region.id)
    toast.success('区域删除成功')
    loadRegions()
  } catch (error: any) {
    console.error('Failed to delete region:', error)
    toast.error(error.response?.data?.detail || '删除区域失败')
  }
}

function prevRegionPage() {
  if (regionPage.value > 1) {
    regionPage.value--
    loadRegions()
  }
}

function nextRegionPage() {
  if (regionPage.value < regionTotalPages.value) {
    regionPage.value++
    loadRegions()
  }
}

// 学校管理方法
async function loadSchools() {
  try {
    const response = await adminService.getSchools({
      page: schoolPage.value,
      size: schoolPageSize.value,
      school_type: schoolTypeFilter.value || undefined,
      search: schoolSearchQuery.value || undefined
    })
    schools.value = response.schools
    schoolTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load schools:', error)
    toast.error(error.response?.data?.detail || '加载学校列表失败')
  }
}

function searchSchools() {
  schoolPage.value = 1
  loadSchools()
}

async function openCreateSchoolModal() {
  editingSchool.value = null
  schoolForm.value = {
    name: '',
    code: '',
    region_id: '',
    school_type: '小学',
    address: '',
    phone: '',
    email: '',
    principal: '',
    description: '',
    is_active: true
  }
  // 加载所有区域供选择
  await loadAllRegions()
  showSchoolModal.value = true
}

async function editSchool(school: School) {
  editingSchool.value = school
  schoolForm.value = {
    name: school.name,
    code: school.code,
    region_id: school.region_id.toString(),
    school_type: school.school_type,
    address: school.address || '',
    phone: school.phone || '',
    email: school.email || '',
    principal: school.principal || '',
    description: school.description || '',
    is_active: school.is_active
  }
  // 加载所有区域供选择
  await loadAllRegions()
  showSchoolModal.value = true
}

function closeSchoolModal() {
  showSchoolModal.value = false
  editingSchool.value = null
}

async function saveSchool() {
  try {
    const formData = {
      ...schoolForm.value,
      region_id: parseInt(schoolForm.value.region_id)
    }
    
    if (editingSchool.value) {
      await adminService.updateSchool(editingSchool.value.id, formData)
      toast.success('学校更新成功')
    } else {
      await adminService.createSchool(formData)
      toast.success('学校创建成功')
    }
    closeSchoolModal()
    loadSchools()
  } catch (error: any) {
    console.error('Failed to save school:', error)
    toast.error(error.response?.data?.detail || '保存学校失败')
  }
}

async function deleteSchool(school: School) {
  if (!confirm(`确定要删除学校 ${school.name} 吗？`)) {
    return
  }
  
  try {
    await adminService.deleteSchool(school.id)
    toast.success('学校删除成功')
    loadSchools()
  } catch (error: any) {
    console.error('Failed to delete school:', error)
    toast.error(error.response?.data?.detail || '删除学校失败')
  }
}

// 学校批量导入方法
function openSchoolImportDialog() {
  showSchoolImportDialog.value = true
  importStep.value = 0
  selectedFile.value = null
  importForm.value = { autoCreateRegion: true }
  importResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created_regions: 0,
    created_schools: 0,
    updated_schools: 0,
    skipped_schools: 0,
    errors: []
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

function closeSchoolImportDialog() {
  showSchoolImportDialog.value = false
  importStep.value = 0
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  // 刷新学校列表
  loadSchools()
}

function downloadSchoolTemplate() {
  // 创建CSV模板数据
  const template = [
    ['区域名称*', '学校名称*', '学校代码', '学校类型', '地址', '联系电话', '邮箱', '校长'],
    ['开平市', '开平市第一中学', '10001', '高中', '开平市XX区XX路', '010-12345678', 'school1@example.com', '张校长'],
    ['开平市', '开平市第二小学', '10002', '小学', '开平市XX区XX街', '010-87654321', 'school2@example.com', '李校长'],
    ['', '', '', '', '', '', '', ''],
  ]

  // 创建CSV内容
  const csvContent = template.map(row => row.join(',')).join('\n')

  // 创建Blob并下载
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', '学校信息导入模板.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  toast.success('模板下载成功')
}

const handleFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedFile.value = uploadFile.raw || null
}

const handleExceed: UploadProps['onExceed'] = () => {
  toast.warning('只能上传一个文件')
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

async function startSchoolImport() {
  if (!selectedFile.value) {
    toast.warning('请先选择文件')
    return
  }

  importing.value = true

  try {
    const result = await adminService.importSchools(
      selectedFile.value,
      importForm.value.autoCreateRegion
    )

    importResult.value = result
    importStep.value = 2

    if (result.success > 0) {
      toast.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      toast.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    toast.error(error.response?.data?.detail || '导入失败')
    importResult.value = {
      total: 0,
      success: 0,
      failed: 1,
      created_regions: 0,
      created_schools: 0,
      updated_schools: 0,
      skipped_schools: 0,
      errors: [{
        row: 0,
        field: null,
        message: error.response?.data?.detail || '导入失败'
      }]
    }
    importStep.value = 2
  } finally {
    importing.value = false
  }
}

function prevSchoolPage() {
  if (schoolPage.value > 1) {
    schoolPage.value--
    loadSchools()
  }
}

function nextSchoolPage() {
  if (schoolPage.value < schoolTotalPages.value) {
    schoolPage.value++
    loadSchools()
  }
}

function getGradeName(gradeId?: number | null): string {
  if (!gradeId) return '—'
  const grade = grades.value.find(g => g.id === gradeId)
  return grade ? grade.name : `年级 #${gradeId}`
}

function getSchoolNameById(schoolId: number): string {
  const school = schools.value.find((s) => s.id === schoolId)
  return school?.name || `学校${schoolId}`
}

// 处理县区筛选变化
function handleRegionFilterChange() {
  // 清空学校筛选，因为县区改变了
  allClassroomSchoolFilter.value = ''
  // 重新加载班级列表
  loadAllClassrooms()
}

// 处理年级筛选变化
function handleGradeFilterChange() {
  // 清空学校筛选，因为年级改变了
  allClassroomSchoolFilter.value = ''
  // 重新加载班级列表（加载后会更新学校列表）
  loadAllClassrooms()
}

async function loadAllClassrooms() {
  try {
    allClassroomsLoading.value = true
    // 先加载所有区域，以便显示区域名称和筛选
    if (allRegions.value.length === 0) {
      await loadAllRegions()
    }
    // 先加载所有学校，以便显示学校名称和筛选
    // 注意：这里需要加载所有学校，因为过滤是在前端通过computed属性完成的
    if (schools.value.length === 0) {
      const allSchoolsResponse = await adminService.getSchools({ page: 1, size: 1000 })
      schools.value = allSchoolsResponse.schools
    }
    // 加载所有年级，以便显示年级名称和筛选
    if (grades.value.length === 0) {
      await loadGradesList()
    }
    // 加载所有班级（后端限制最大size为100，如果需要更多需要分页）
    const response = await adminService.getClassrooms({
      page: 1,
      size: 100, // 后端API限制最大值为100
      region_id: allClassroomRegionFilter.value ? Number(allClassroomRegionFilter.value) : undefined,
      school_id: allClassroomSchoolFilter.value ? Number(allClassroomSchoolFilter.value) : undefined,
      grade_id: allClassroomGradeFilter.value ? Number(allClassroomGradeFilter.value) : undefined,
      search: allClassroomSearchQuery.value || undefined,
    })
    allClassrooms.value = response.classrooms
    // 确保学校列表包含所有需要的学校
    const schoolIds = [...new Set(response.classrooms.map(c => c.school_id))]
    const missingSchoolIds = schoolIds.filter(id => !schools.value.find(s => s.id === id))
    if (missingSchoolIds.length > 0) {
      // 如果列表中的学校不在当前学校列表中，需要加载所有学校
      const allSchoolsResponse = await adminService.getSchools({ page: 1, size: 1000 })
      schools.value = allSchoolsResponse.schools
    }
  } catch (error: any) {
    console.error('Failed to load all classrooms:', error)
    toast.error(error.response?.data?.detail || '加载班级列表失败')
  } finally {
    allClassroomsLoading.value = false
  }
}

async function openClassroomManager(school: School) {
  classroomSchool.value = school
  classroomPage.value = 1
  classroomSearchQuery.value = ''
  classroomGradeFilter.value = ''
  await Promise.all([loadGradesList(), loadClassrooms()])
  showClassroomManager.value = true
}

function closeClassroomManager() {
  showClassroomManager.value = false
  classroomSchool.value = null
  classrooms.value = []
}

async function loadClassrooms() {
  if (!classroomSchool.value) return
  try {
    classroomLoading.value = true
    const response = await adminService.getClassrooms({
      page: classroomPage.value,
      size: classroomPageSize.value,
      school_id: classroomSchool.value.id,
      grade_id: classroomGradeFilter.value ? Number(classroomGradeFilter.value) : undefined,
      search: classroomSearchQuery.value || undefined,
      is_active: undefined,
    })
    classrooms.value = response.classrooms
    classroomTotal.value = response.total
  } catch (error: any) {
    console.error('Failed to load classrooms:', error)
    toast.error(error.response?.data?.detail || '加载班级列表失败')
  } finally {
    classroomLoading.value = false
  }
}

function handleClassroomFilterChange() {
  classroomPage.value = 1
  loadClassrooms()
}

function prevClassroomPage() {
  if (classroomPage.value > 1) {
    classroomPage.value--
    loadClassrooms()
  }
}

function nextClassroomPage() {
  if (classroomPage.value < classroomTotalPages.value) {
    classroomPage.value++
    loadClassrooms()
  }
}

function openCreateClassroomModal() {
  if (!classroomSchool.value) return
  editingClassroom.value = null
  classroomForm.value = {
    name: '',
    grade_id: '',
    enrollment_year: new Date().getFullYear().toString(),
    code: '',
    description: '',
    is_active: true,
  }
  classroomNameError.value = ''
  showClassroomModal.value = true
}

function editClassroom(classroom: Classroom) {
  editingClassroom.value = classroom
  classroomForm.value = {
    name: classroom.name,
    grade_id: classroom.grade_id ? classroom.grade_id.toString() : '',
    enrollment_year: classroom.enrollment_year ? classroom.enrollment_year.toString() : '',
    code: classroom.code || '',
    description: classroom.description || '',
    is_active: classroom.is_active,
  }
  classroomNameError.value = ''
  showClassroomModal.value = true
}

// 成员管理方法
function getRoleName(role: RoleInClass): string {
  const roleMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: '正班主任',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: '副班主任',
    [RoleInClass.SUBJECT_TEACHER]: '任课教师',
    [RoleInClass.CADRE]: '班干部',
    [RoleInClass.STUDENT]: '学生',
  }
  return roleMap[role] || role
}

function getRoleBadgeClass(role: RoleInClass): string {
  const classMap: Record<RoleInClass, string> = {
    [RoleInClass.HEAD_TEACHER_PRIMARY]: 'bg-purple-100 text-purple-800',
    [RoleInClass.HEAD_TEACHER_DEPUTY]: 'bg-indigo-100 text-indigo-800',
    [RoleInClass.SUBJECT_TEACHER]: 'bg-blue-100 text-blue-800',
    [RoleInClass.CADRE]: 'bg-yellow-100 text-yellow-800',
    [RoleInClass.STUDENT]: 'bg-green-100 text-green-800',
  }
  return classMap[role] || 'bg-gray-100 text-gray-800'
}

async function openMemberManager(classroom: Classroom) {
  selectedClassroom.value = classroom
  showMemberManager.value = true
  await loadMembers()
}

function closeMemberManager() {
  showMemberManager.value = false
  selectedClassroom.value = null
  members.value = []
}

async function loadMembers() {
  if (!selectedClassroom.value) return
  
  try {
    membersLoading.value = true
    members.value = await classroomAssistantService.getClassroomMembers(selectedClassroom.value.id)
  } catch (error: any) {
    console.error('加载成员列表失败:', error)
    toast.error(error.response?.data?.detail || '加载成员列表失败')
  } finally {
    membersLoading.value = false
  }
}

function openAddMemberModal() {
  if (!selectedClassroom.value) return
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
  memberForm.value = {
    classroomId: selectedClassroom.value.id,
    userId: 0,
    roleInClass: RoleInClass.STUDENT,
    studentNo: null,
    seatNo: null,
    cadreTitle: null,
    isPrimaryClass: false,
  }
  showMemberModal.value = true
}

async function searchUsersForMember() {
  if (!userSearchQuery.value && !userRoleFilter.value) {
    searchedUsers.value = []
    return
  }
  
  try {
    userSearchLoading.value = true
    const response = await adminService.getUsers({
      page: 1,
      size: 20,
      role: userRoleFilter.value || undefined,
      search: userSearchQuery.value || undefined,
    })
    searchedUsers.value = response.users
  } catch (error: any) {
    console.error('搜索用户失败:', error)
    toast.error(error.response?.data?.detail || '搜索用户失败')
  } finally {
    userSearchLoading.value = false
  }
}

function onUserRoleFilterChange() {
  // 当用户选择角色筛选时，自动设置对应的角色
  if (userRoleFilter.value === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (userRoleFilter.value === 'teacher') {
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
  // 执行搜索
  searchUsersForMember()
}

function selectUserForMember(user: User) {
  memberForm.value.userId = user.id
  selectedUserInfo.value = user
  // 根据用户的系统角色自动设置班级角色
  autoSetRoleFromUser(user)
}

function autoSetRoleFromUser(user: User) {
  // 根据用户的系统角色自动设置班级角色
  if (user.role === 'student') {
    memberForm.value.roleInClass = RoleInClass.STUDENT
  } else if (user.role === 'teacher' || user.role === 'admin' || user.role === 'researcher') {
    // 如果选择的是教师、管理员或研究员，默认设置为任课教师
    // 管理员可以根据需要后续手动调整为正班主任或副班主任
    memberForm.value.roleInClass = RoleInClass.SUBJECT_TEACHER
  }
}

async function onUserIdInput() {
  const userId = memberForm.value.userId
  
  // 如果输入的用户ID与已选用户不同，清除已选用户信息
  if (selectedUserInfo.value && selectedUserInfo.value.id !== userId) {
    selectedUserInfo.value = null
  }
  
  // 如果输入了有效的用户ID（大于0），尝试获取用户信息并自动设置角色
  if (userId && userId > 0 && !selectedUserInfo.value) {
    try {
      const user = await adminService.getUser(userId)
      selectedUserInfo.value = user
      // 自动设置角色
      autoSetRoleFromUser(user)
    } catch (error: any) {
      // 用户不存在或无法获取，忽略错误（用户可能还在输入）
      console.debug('获取用户信息失败:', error)
    }
  }
}

function editMember(member: ClassroomMembership) {
  editingMember.value = member
  memberError.value = ''
  memberForm.value = {
    classroomId: member.classroomId,
    userId: member.userId,
    roleInClass: member.roleInClass,
    studentNo: member.studentNo || null,
    seatNo: member.seatNo || null,
    cadreTitle: member.cadreTitle || null,
    isPrimaryClass: member.isPrimaryClass,
  }
  showMemberModal.value = true
}

function closeMemberModal() {
  showMemberModal.value = false
  editingMember.value = null
  memberError.value = ''
  userSearchQuery.value = ''
  userRoleFilter.value = ''
  searchedUsers.value = []
  selectedUserInfo.value = null
  batchAddMode.value = false
  sourceClassroomFilter.value = ''
  sourceClassroomStudents.value = []
  selectedStudentIds.value = new Set()
}

async function saveMember() {
  if (!selectedClassroom.value) return
  
  try {
    memberSaving.value = true
    memberError.value = ''
    
    if (editingMember.value) {
      // 更新成员
      const updateData: ClassroomMembershipUpdate = {
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.updateClassroomMember(
        selectedClassroom.value.id,
        editingMember.value.userId,
        updateData
      )
      toast.success('成员信息更新成功')
    } else {
      // 添加成员
      const createData: ClassroomMembershipCreate = {
        classroomId: selectedClassroom.value.id,
        userId: memberForm.value.userId,
        roleInClass: memberForm.value.roleInClass,
        studentNo: memberForm.value.studentNo || null,
        seatNo: memberForm.value.seatNo || null,
        cadreTitle: memberForm.value.cadreTitle || null,
        isPrimaryClass: memberForm.value.isPrimaryClass,
      }
      await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
      toast.success('成员添加成功')
    }
    
    closeMemberModal()
    await loadMembers()
  } catch (error: any) {
    console.error('保存成员失败:', error)
    memberError.value = error.response?.data?.detail || error.message || '保存失败，请重试'
  } finally {
    memberSaving.value = false
  }
}

// 加载来源班级的学生列表
async function loadSourceClassroomStudents() {
  if (!sourceClassroomFilter.value) {
    sourceClassroomStudents.value = []
    selectedStudentIds.value = new Set()
    return
  }
  
  try {
    sourceStudentsLoading.value = true
    const sourceMembers = await classroomAssistantService.getClassroomMembers(Number(sourceClassroomFilter.value))
    // 只显示学生角色
    let students = sourceMembers.filter(m => m.roleInClass === RoleInClass.STUDENT)
    
    // 排除已经是当前班级成员的学生
    if (selectedClassroom.value) {
      try {
        const currentMembers = await classroomAssistantService.getClassroomMembers(selectedClassroom.value.id)
        const currentMemberUserIds = new Set(currentMembers.filter(m => m.isActive).map(m => m.userId))
        students = students.filter(s => !currentMemberUserIds.has(s.userId))
      } catch (error) {
        // 如果获取当前班级成员失败，忽略错误，继续显示所有学生
        console.warn('获取当前班级成员失败:', error)
      }
    }
    
    sourceClassroomStudents.value = students
    selectedStudentIds.value = new Set()
  } catch (error: any) {
    console.error('加载班级学生失败:', error)
    toast.error(error.response?.data?.detail || '加载班级学生失败')
    sourceClassroomStudents.value = []
  } finally {
    sourceStudentsLoading.value = false
  }
}

// 切换学生选择状态
function toggleStudentSelection(userId: number) {
  if (selectedStudentIds.value.has(userId)) {
    selectedStudentIds.value.delete(userId)
  } else {
    selectedStudentIds.value.add(userId)
  }
}

// 全选/取消全选
function toggleSelectAllStudents() {
  if (selectedStudentIds.value.size === sourceClassroomStudents.value.length) {
    selectedStudentIds.value = new Set()
  } else {
    selectedStudentIds.value = new Set(sourceClassroomStudents.value.map(s => s.userId))
  }
}

// 批量添加成员
async function batchAddMembers() {
  if (!selectedClassroom.value || selectedStudentIds.value.size === 0) return
  
  try {
    memberSaving.value = true
    memberError.value = ''
    
    const errors: string[] = []
    let successCount = 0
    
    // 逐个添加选中的学生
    for (const userId of selectedStudentIds.value) {
      try {
        const student = sourceClassroomStudents.value.find(s => s.userId === userId)
        if (!student) continue
        
        const createData: ClassroomMembershipCreate = {
          classroomId: selectedClassroom.value.id,
          userId: userId,
          roleInClass: RoleInClass.STUDENT,
          studentNo: student.studentNo || null,
          seatNo: student.seatNo || null,
          cadreTitle: null,
          isPrimaryClass: false,
        }
        
        await classroomAssistantService.addClassroomMember(selectedClassroom.value.id, createData)
        successCount++
      } catch (error: any) {
        const studentName = sourceClassroomStudents.value.find(s => s.userId === userId)?.userFullName || `ID: ${userId}`
        const errorMsg = error.response?.data?.detail || '添加失败'
        errors.push(`${studentName}: ${errorMsg}`)
        console.error(`添加成员失败 (userId: ${userId}):`, error)
      }
    }
    
    if (successCount > 0) {
      toast.success(`成功添加 ${successCount} 个成员${errors.length > 0 ? `，${errors.length} 个失败` : ''}`)
    }
    
    if (errors.length > 0 && successCount === 0) {
      memberError.value = errors.join('\n')
      toast.error('批量添加失败')
    }
    
    if (successCount > 0) {
      closeMemberModal()
      await loadMembers()
    }
  } catch (error: any) {
    console.error('批量添加成员失败:', error)
    memberError.value = error.response?.data?.detail || '批量添加失败'
    toast.error(error.response?.data?.detail || '批量添加失败')
  } finally {
    memberSaving.value = false
  }
}

async function removeMember(member: ClassroomMembership) {
  if (!selectedClassroom.value) return
  if (!confirm(`确定要移除用户ID ${member.userId} 吗？`)) {
    return
  }
  
  try {
    await classroomAssistantService.removeClassroomMember(selectedClassroom.value.id, member.userId)
    toast.success('成员移除成功')
    await loadMembers()
  } catch (error: any) {
    console.error('移除成员失败:', error)
    toast.error(error.response?.data?.detail || error.message || '移除失败，请重试')
  }
}

function closeClassroomModal() {
  showClassroomModal.value = false
  editingClassroom.value = null
  classroomNameError.value = ''
}

async function saveClassroom() {
  if (!classroomSchool.value) {
    toast.error('请先选择学校')
    return
  }
  
  // 验证班级名称格式
  const name = classroomForm.value.name.trim()
  // 允许：01-09（两位数格式）或 10 及以上的数字
  // 正则说明：0[1-9] 匹配 01-09，[1-9]\d+ 匹配 10 及以上的数字（不以0开头）
  const namePattern = /^(0[1-9]|[1-9]\d+)$/
  if (!namePattern.test(name)) {
    classroomNameError.value = '班级名称格式错误：1-9班请输入 01-09（例如：01 表示1班），10班及以上请输入正常数字（例如：10 表示10班）'
    return
  }
  classroomNameError.value = ''
  
  try {
    const enrollmentYearNumber = classroomForm.value.enrollment_year
      ? Number(classroomForm.value.enrollment_year)
      : undefined
    const payload: any = {
      name: classroomForm.value.name.trim(),
      grade_id: classroomForm.value.grade_id ? Number(classroomForm.value.grade_id) : undefined,
      school_id: classroomSchool.value.id,
      is_active: classroomForm.value.is_active,
      description: classroomForm.value.description || undefined,
      enrollment_year: enrollmentYearNumber,
    }

    const generatedCode =
      enrollmentYearNumber && classroomForm.value.name
        ? `${enrollmentYearNumber}${classroomForm.value.name.replace(/\s+/g, '')}`
        : undefined

    if (!payload.grade_id) {
      toast.error('请选择年级')
      return
    }

    payload.code = generatedCode
    classroomForm.value.code = generatedCode || ''

    if (editingClassroom.value) {
      await adminService.updateClassroom(editingClassroom.value.id, payload)
      toast.success('班级更新成功')
    } else {
      await adminService.createClassroom(payload)
      toast.success('班级创建成功')
    }
    closeClassroomModal()
    loadClassrooms()
  } catch (error: any) {
    console.error('Failed to save classroom:', error)
    toast.error(error.response?.data?.detail || '保存班级失败')
  }
}

async function deleteClassroom(classroom: Classroom) {
  if (!confirm(`确定要删除班级 ${classroom.name} 吗？`)) {
    return
  }
  try {
    await adminService.deleteClassroom(classroom.id)
    toast.success('班级删除成功')
    loadClassrooms()
  } catch (error: any) {
    console.error('Failed to delete classroom:', error)
    toast.error(error.response?.data?.detail || '删除班级失败')
  }
}

// 班级批量导入方法
function openClassroomImportDialog() {
  if (!classroomSchool.value) {
    toast.warning('请先选择学校')
    return
  }
  showClassroomImportDialog.value = true
  classroomImportStep.value = 0
  selectedClassroomFile.value = null
  classroomImportForm.value = {
    enrollmentYear: undefined,
    capacity: undefined,
    updateExisting: false
  }
  classroomImportResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: []
  }
  if (classroomUploadRef.value) {
    classroomUploadRef.value.clearFiles()
  }
}

function closeClassroomImportDialog() {
  showClassroomImportDialog.value = false
  classroomImportStep.value = 0
  selectedClassroomFile.value = null
  if (classroomUploadRef.value) {
    classroomUploadRef.value.clearFiles()
  }
  // 刷新班级列表
  loadClassrooms()
}

function downloadClassroomTemplate() {
  // 创建Excel模板数据（学校端简化版，不包含学校字段）
  const template = [
    ['年级级别*', '年级名称', '班级编号*', '班级名称', '入学年份', '班级容量', '班级描述'],
    [7, '七年级', '701', '七年级1班', 2024, 45, '重点班'],
    [7, '七年级', '702', '七年级2班', 2024, 45, '普通班'],
    [8, '八年级', '801', '八年级1班', 2023, 48, ''],
  ]

  // 使用xlsx库生成Excel文件
  const ws = XLSX.utils.aoa_to_sheet(template)

  // 设置列宽
  const colWidths = [
    { wch: 12 }, // 年级级别
    { wch: 12 }, // 年级名称
    { wch: 12 }, // 班级编号
    { wch: 15 }, // 班级名称
    { wch: 12 }, // 入学年份
    { wch: 12 }, // 班级容量
    { wch: 15 }, // 班级描述
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '班级信息')
  XLSX.writeFile(wb, '班级信息导入模板.xlsx')
  toast.success('模板下载成功')
}

const handleClassroomFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedClassroomFile.value = uploadFile.raw || null
}

const handleClassroomExceed: UploadProps['onExceed'] = () => {
  toast.warning('只能上传一个文件')
}

async function startClassroomImport() {
  if (!selectedClassroomFile.value) {
    toast.warning('请先选择文件')
    return
  }

  if (!classroomSchool.value) {
    toast.error('缺少学校信息')
    return
  }

  classroomImporting.value = true

  try {
    const result = await adminService.importClassrooms(
      selectedClassroomFile.value,
      classroomSchool.value.id,
      undefined, // region_id（学校端不需要）
      classroomImportForm.value.updateExisting,
      classroomImportForm.value.enrollmentYear,
      classroomImportForm.value.capacity
    )

    classroomImportResult.value = result
    classroomImportStep.value = 2

    if (result.success > 0) {
      toast.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      toast.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    toast.error(error.response?.data?.detail || '导入失败')
    classroomImportResult.value = {
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
      }]
    }
    classroomImportStep.value = 2
  } finally {
    classroomImporting.value = false
  }
}

// 县区管理端班级批量导入方法
function openDistrictClassroomImportDialog() {
  showDistrictClassroomImportDialog.value = true
  districtClassroomImportStep.value = 0
  selectedDistrictClassroomFile.value = null
  districtClassroomImportForm.value = {
    enrollmentYear: undefined,
    capacity: undefined,
    updateExisting: false
  }
  districtClassroomImportResult.value = {
    total: 0,
    success: 0,
    failed: 0,
    created: 0,
    updated: 0,
    skipped: 0,
    errors: []
  }
  if (districtClassroomUploadRef.value) {
    districtClassroomUploadRef.value.clearFiles()
  }
}

function closeDistrictClassroomImportDialog() {
  showDistrictClassroomImportDialog.value = false
  districtClassroomImportStep.value = 0
  selectedDistrictClassroomFile.value = null
  if (districtClassroomUploadRef.value) {
    districtClassroomUploadRef.value.clearFiles()
  }
  // 刷新学校列表（可能需要刷新班级数据）
  loadSchools()
}

function downloadDistrictClassroomTemplate() {
  // 创建Excel模板数据（县区端完整版，包含学校字段）
  const template = [
    ['学校名称*', '学校代码', '年级级别*', '年级名称', '班级编号*', '班级名称', '入学年份', '班级容量', '班级描述'],
    ['开平市第一中学', '10001', 7, '七年级', '701', '七年级1班', 2024, 45, '重点班'],
    ['开平市第一中学', '10001', 7, '七年级', '702', '七年级2班', 2024, 45, '普通班'],
    ['开平市第二中学', '10002', 7, '七年级', '701', '七年级1班', 2024, 50, ''],
  ]

  // 使用xlsx库生成Excel文件
  const ws = XLSX.utils.aoa_to_sheet(template)

  // 设置列宽
  const colWidths = [
    { wch: 20 }, // 学校名称
    { wch: 12 }, // 学校代码
    { wch: 12 }, // 年级级别
    { wch: 12 }, // 年级名称
    { wch: 12 }, // 班级编号
    { wch: 15 }, // 班级名称
    { wch: 12 }, // 入学年份
    { wch: 12 }, // 班级容量
    { wch: 15 }, // 班级描述
  ]
  ws['!cols'] = colWidths

  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '班级信息')
  XLSX.writeFile(wb, '班级信息导入模板（县区端）.xlsx')
  toast.success('模板下载成功')
}

const handleDistrictClassroomFileChange: UploadProps['onChange'] = (uploadFile) => {
  selectedDistrictClassroomFile.value = uploadFile.raw || null
}

const handleDistrictClassroomExceed: UploadProps['onExceed'] = () => {
  toast.warning('只能上传一个文件')
}

async function startDistrictClassroomImport() {
  if (!selectedDistrictClassroomFile.value) {
    toast.warning('请先选择文件')
    return
  }

  districtClassroomImporting.value = true

  try {
    const result = await adminService.importClassrooms(
      selectedDistrictClassroomFile.value,
      undefined, // school_id（县区端不需要，从Excel中读取）
      undefined, // region_id（可选，如果需要可以添加）
      districtClassroomImportForm.value.updateExisting,
      districtClassroomImportForm.value.enrollmentYear,
      districtClassroomImportForm.value.capacity
    )

    districtClassroomImportResult.value = result
    districtClassroomImportStep.value = 2

    if (result.success > 0) {
      toast.success(`导入完成！成功 ${result.success} 条，失败 ${result.failed} 条`)
    } else {
      toast.error(`导入失败：${result.errors.length > 0 ? result.errors[0].message : '未知错误'}`)
    }
  } catch (error: any) {
    console.error('导入失败:', error)
    toast.error(error.response?.data?.detail || '导入失败')
    districtClassroomImportResult.value = {
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
      }]
    }
    districtClassroomImportStep.value = 2
  } finally {
    districtClassroomImporting.value = false
  }
}

// 监听标签页切换，切换到班级成员管理时自动加载
watch(activeTab, (newTab) => {
  if (newTab === 'classrooms' && allClassrooms.value.length === 0) {
    loadAllClassrooms()
  }
})

onMounted(() => {
  loadRegions()
  loadSchools()
  loadAllRegions()
  loadGradesList()
  // 如果默认是班级成员管理标签页，加载数据
  if (activeTab.value === 'classrooms') {
    loadAllClassrooms()
  }
})
</script>

