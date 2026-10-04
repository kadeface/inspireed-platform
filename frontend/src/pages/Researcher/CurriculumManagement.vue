<template>
  <div class="curriculum-management min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50 p-6">
    <div class="header mb-6">
      <div class="flex items-center gap-4 mb-2">
        <router-link
          to="/researcher"
          class="inline-flex h-9 items-center gap-1.5 rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>返回</span>
        </router-link>
      </div>
      <h1 class="text-3xl font-bold text-gray-900">课程体系管理</h1>
      <p class="text-gray-600 mt-2">教研员专属 - 管理学科、年级、课程和官方资源</p>
    </div>

    <!-- Statistics -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div class="text-sm text-slate-500">学科总数</div>
        <div class="text-2xl font-bold text-slate-900">{{ curriculumTree?.total_subjects || 0 }}</div>
      </div>
      <div class="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div class="text-sm text-slate-500">年级总数</div>
        <div class="text-2xl font-bold text-slate-900">{{ curriculumTree?.total_grades || 0 }}</div>
      </div>
      <div class="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div class="text-sm text-slate-500">课程总数</div>
        <div class="text-2xl font-bold text-slate-900">{{ curriculumTree?.total_courses || 0 }}</div>
      </div>
      <div class="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
        <div class="text-sm text-slate-500">教案总数</div>
        <div class="text-2xl font-bold text-emerald-700">{{ curriculumTree?.total_lessons || 0 }}</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">课程体系树</h2>
        <div class="flex gap-2">
          <label class="flex items-center">
            <input 
              v-model="includeInactive" 
              type="checkbox" 
              class="mr-2"
              @change="loadCurriculumTree"
            />
            <span class="text-sm">显示已禁用项</span>
          </label>
          <button
            @click="openUploadModal"
            class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-emerald-700 shadow-sm ring-1 ring-inset ring-emerald-200 transition-all hover:bg-emerald-50 hover:ring-emerald-300"
          >
            📤 上传资源
          </button>
          <button
            @click="openImportChaptersModal"
            class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!dataLoaded"
            :class="{ 'opacity-50 cursor-not-allowed': !dataLoaded }"
          >
            📥 导入章节
          </button>
          <button
            @click="openExportImportModal"
            class="inline-flex h-9 items-center rounded-xl bg-white px-3 text-sm font-medium text-slate-700 shadow-sm ring-1 ring-inset ring-slate-200 transition-all hover:bg-slate-50 hover:ring-slate-300"
          >
            📋 导出导入
          </button>
          <button
            @click="openCourseModal"
            class="inline-flex h-9 items-center rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 px-3 text-sm font-medium text-white shadow-lg shadow-emerald-500/30 transition-all hover:from-emerald-600 hover:to-teal-600 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!dataLoaded"
            :class="{ 'opacity-50 cursor-not-allowed': !dataLoaded }"
          >
            + 添加课程
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-500">加载中...</div>
      </div>

      <!-- Curriculum Tree -->
      <div v-else-if="curriculumTree" class="curriculum-tree">
        <div
          v-for="subject in curriculumTree.subjects"
          :key="subject.id"
          class="subject-node mb-4"
        >
          <div 
            class="subject-header flex cursor-pointer items-center justify-between rounded-xl bg-slate-50 p-3 hover:bg-slate-100"
            :class="{ 'opacity-50': !subject.is_active }"
            @click="toggleSubject(subject.id)"
          >
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ expandedSubjects.has(subject.id) ? '▼' : '▶' }}</span>
              <span class="font-semibold text-lg">{{ subject.name }}</span>
              <span class="text-sm text-gray-500">({{ subject.code }})</span>
              <span v-if="!subject.is_active" class="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">已禁用</span>
              <span class="text-sm text-gray-600">{{ subject.lesson_count }} 个教案</span>
              <button
                v-if="subject.lesson_count > 0"
                @click.stop="toggleSubjectLessons(subject.id)"
                class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                title="展开/收起教案"
              >
                {{ expandedSubjectLessons.has(subject.id) ? '▼' : '▶' }} 教案
              </button>
            </div>
            <div class="flex gap-2" @click.stop>
              <button
                @click="toggleSubjectStatus(subject)"
                class="px-3 py-1 text-sm rounded"
                :class="subject.is_active ? 'rounded-xl bg-red-50 text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-100' : 'rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-100'"
              >
                {{ subject.is_active ? '禁用' : '启用' }}
              </button>
            </div>
          </div>

          <!-- Subject Lessons -->
          <div v-if="expandedSubjectLessons.has(subject.id)" class="ml-8 mt-2">
            <SubjectGradeCourseLessonList
              :subject-id="subject.id"
              @view="handleViewLesson"
              @deleted="handleLessonDeleted"
            />
          </div>

          <!-- Grades -->
          <div v-if="expandedSubjects.has(subject.id)" class="grades-container ml-8 mt-2">
            <div
              v-for="grade in subject.grades"
              :key="grade.id"
              class="grade-node mb-3"
            >
              <div 
                class="grade-header flex cursor-pointer items-center justify-between rounded-xl bg-slate-50 p-2 hover:bg-slate-100"
                :class="{ 'opacity-50': !grade.is_active }"
                @click="toggleGrade(subject.id, grade.id)"
              >
                <div class="flex items-center gap-2">
                  <span>{{ expandedGrades.has(`${subject.id}-${grade.id}`) ? '▼' : '▶' }}</span>
                  <span class="font-medium">{{ grade.name }}</span>
                  <span v-if="!grade.is_active" class="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">已禁用</span>
                  <span class="text-sm text-gray-600">{{ grade.lesson_count }} 个教案</span>
                  <button
                    v-if="grade.lesson_count > 0"
                    @click.stop="toggleGradeLessons(subject.id, grade.id)"
                    class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                    title="展开/收起教案"
                  >
                    {{ expandedGradeLessons.has(`${subject.id}-${grade.id}`) ? '▼' : '▶' }} 教案
                  </button>
                </div>
                <div class="flex gap-2" @click.stop>
                  <button
                    @click="toggleGradeStatus(grade)"
                    class="px-2 py-1 text-sm rounded"
                    :class="grade.is_active ? 'rounded-xl bg-red-50 text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-100' : 'rounded-xl bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-100'"
                  >
                    {{ grade.is_active ? '禁用' : '启用' }}
                  </button>
                </div>
              </div>

              <!-- Grade Lessons -->
              <div v-if="expandedGradeLessons.has(`${subject.id}-${grade.id}`)" class="ml-6 mt-2">
                <SubjectGradeCourseLessonList
                  :subject-id="subject.id"
                  :grade-id="grade.id"
                  @view="handleViewLesson"
                  @deleted="handleLessonDeleted"
                />
              </div>

              <!-- Courses -->
              <div v-if="expandedGrades.has(`${subject.id}-${grade.id}`)" class="courses-container ml-6 mt-2">
                <div
                  v-for="course in grade.courses"
                  :key="course.id"
                  class="course-node mb-3"
                >
                  <!-- Course Header -->
                  <div 
                    class="flex cursor-pointer items-center justify-between rounded-xl bg-emerald-50/70 p-2 hover:bg-emerald-50"
                    :class="{ 'opacity-50': !course.is_active }"
                    @click="toggleCourse(course.id)"
                  >
                    <div class="flex items-center gap-2">
                      <span class="text-lg">{{ expandedCourses.has(course.id) ? '▼' : '▶' }}</span>
                      <span>📚</span>
                      <span class="font-medium">{{ course.name }}</span>
                      <span v-if="course.code" class="text-sm text-gray-500">({{ course.code }})</span>
                      <span v-if="!course.is_active" class="px-2 py-1 bg-red-100 text-red-600 text-xs rounded">已禁用</span>
                      <span class="text-sm text-gray-600">{{ course.lesson_count }} 个教案</span>
                      <button
                        v-if="course.lesson_count > 0"
                        @click.stop="toggleCourseLessons(course.id)"
                        class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                        title="展开/收起教案"
                      >
                        {{ expandedCourseLessons.has(course.id) ? '▼' : '▶' }} 教案
                      </button>
                      <span v-if="courseChapters.has(course.id)" class="text-sm text-slate-500">
                        {{ courseChapters.get(course.id)?.length || 0 }} 个章节
                      </span>
                    </div>
                    <div class="flex gap-2" @click.stop>
                      <button
                        v-if="course.code"
                        @click="openMergeModal(course)"
                        class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-sm font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                        title="合并相同代码的课程"
                      >
                        合并
                      </button>
                      <button
                        @click="editCourse(course, subject, grade)"
                        class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-sm font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-50"
                      >
                        编辑
                      </button>
                      <button
                        @click="deleteCourseConfirm(course)"
                        class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-sm font-medium text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-50"
                        :disabled="course.lesson_count > 0"
                        :class="{ 'opacity-50 cursor-not-allowed': course.lesson_count > 0 }"
                      >
                        删除
                      </button>
                    </div>
                  </div>

                  <!-- Course Lessons -->
                  <div v-if="expandedCourseLessons.has(course.id)" class="ml-8 mt-2">
                    <SubjectGradeCourseLessonList
                      :course-id="course.id"
                      @view="handleViewLesson"
                      @deleted="handleLessonDeleted"
                    />
                  </div>

                  <!-- Chapters -->
                  <div v-if="expandedCourses.has(course.id)" class="chapters-container ml-8 mt-2">
                    <!-- 添加章节按钮 -->
                    <div class="add-chapter-btn-container mb-2">
                      <button
                        @click="openAddChapterModal(course)"
                        class="add-chapter-btn inline-flex h-9 items-center gap-1 rounded-xl bg-white px-3 text-sm font-medium text-emerald-700 shadow-sm ring-1 ring-inset ring-emerald-200 transition-all hover:bg-emerald-50 hover:ring-emerald-300"
                      >
                        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                        添加章节
                      </button>
                    </div>
                    
                    <!-- Loading State -->
                    <div v-if="loadingChapters.has(course.id)" class="flex items-center gap-2 p-2 text-gray-500">
                      <div class="animate-spin h-4 w-4 rounded-full border-2 border-slate-200 border-t-emerald-500"></div>
                      <span class="text-sm">加载章节中...</span>
                    </div>
                    
                    <!-- Chapters List -->
                    <div v-else-if="courseChapters.has(course.id) && (courseChapters.get(course.id)?.length ?? 0) > 0" class="space-y-1">
                      <div
                        v-for="chapter in courseChapters.get(course.id)"
                        :key="chapter.id"
                        class="chapter-container"
                      >
                        <!-- 主章节 -->
                        <div class="chapter-node flex items-center justify-between gap-2 rounded-xl bg-white p-2 ring-1 ring-slate-200 hover:bg-slate-50">
                          <div class="flex items-center gap-2">
                            <button
                              @click.stop="toggleChapterLessons(chapter.id)"
                              class="text-slate-500 hover:text-slate-700"
                              title="展开/收起教案"
                            >
                              <span>{{ expandedLessons.has(chapter.id) ? '▼' : '▶' }}</span>
                            </button>
                            <button
                              @click.stop="toggleChapterResources(chapter.id)"
                              class="text-slate-500 hover:text-slate-700"
                              title="展开/收起资源"
                            >
                              <span>{{ expandedResources.has(chapter.id) ? '▼' : '▶' }}</span>
                            </button>
                            <span>📖</span>
                            <span class="font-medium">{{ chapter.name }}</span>
                            <span v-if="chapter.code" class="text-sm text-gray-500">({{ chapter.code }})</span>
                            <span v-if="chapter.description" class="text-sm text-gray-600">{{ chapter.description }}</span>
                            <span v-if="!chapter.is_active" class="px-1 py-0.5 bg-red-100 text-red-600 text-xs rounded">已禁用</span>
                            <span v-if="chapter.lesson_count !== undefined && chapter.lesson_count > 0" class="text-sm text-orange-600">
                              {{ chapter.lesson_count }} 个教案
                            </span>
                          </div>
                          <div class="flex gap-1" @click.stop>
                            <button
                              @click="associateLessonToChapter(chapter, course)"
                              class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                              title="关联教案"
                            >
                              📄 关联教案
                            </button>
                            <button
                              @click="uploadResourceToChapter(chapter)"
                              class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-50"
                              title="上传资源"
                            >
                              📎 上传
                            </button>
                            <button
                              @click="editChapter(chapter)"
                              class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-50"
                              title="编辑章节"
                            >
                              编辑
                            </button>
                            <button
                              @click="deleteChapterConfirm(chapter)"
                              class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-50"
                              title="删除章节"
                            >
                              删除
                            </button>
                          </div>
                        </div>
                        
                        <!-- 主章节教案列表 -->
                        <div v-if="expandedLessons.has(chapter.id)" class="ml-8 mt-1">
                          <ChapterLessonList
                            :chapter-id="chapter.id"
                            :can-unlink="true"
                            @refresh="handleChapterLessonRefresh(chapter.id)"
                            @view="handleViewLesson"
                          />
                        </div>
                        
                        <!-- 主章节资源列表 -->
                        <div v-if="expandedResources.has(chapter.id)" class="ml-8 mt-1" :data-chapter-id="chapter.id">
                          <ChapterResourceList
                            :chapter-id="chapter.id"
                            :can-delete="true"
                            @refresh="loadCurriculumTree"
                            @view="handleViewResource"
                          />
                        </div>
                        
                        <!-- 子章节 -->
                        <div v-if="chapter.children && chapter.children.length > 0" class="ml-6 mt-1 space-y-1">
                          <div
                            v-for="child in chapter.children"
                            :key="child.id"
                            class="chapter-container"
                          >
                            <div class="chapter-node flex items-center justify-between gap-2 rounded-xl bg-slate-50 p-2 ring-1 ring-slate-200 hover:bg-white">
                              <div class="flex items-center gap-2">
                                <button
                                  @click.stop="toggleChapterLessons(child.id)"
                                  class="text-gray-400 hover:text-gray-600"
                                  title="展开/收起教案"
                                >
                                  <span>{{ expandedLessons.has(child.id) ? '▼' : '▶' }}</span>
                                </button>
                                <button
                                  @click.stop="toggleChapterResources(child.id)"
                                  class="text-gray-400 hover:text-gray-600"
                                  title="展开/收起资源"
                                >
                                  <span>{{ expandedResources.has(child.id) ? '▼' : '▶' }}</span>
                                </button>
                                <span class="text-gray-400">└─</span>
                                <span class="text-slate-400">📄</span>
                                <span class="font-medium">{{ child.name }}</span>
                                <span v-if="child.code" class="text-sm text-gray-500">({{ child.code }})</span>
                                <span v-if="child.description" class="text-sm text-gray-600">{{ child.description }}</span>
                                <span v-if="!child.is_active" class="px-1 py-0.5 bg-red-100 text-red-600 text-xs rounded">已禁用</span>
                                <span v-if="child.lesson_count !== undefined && child.lesson_count > 0" class="text-sm text-orange-600">
                                  {{ child.lesson_count }} 个教案
                                </span>
                              </div>
                              <div class="flex gap-1" @click.stop>
                                <button
                                  @click="associateLessonToChapter(child, course)"
                                  class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-slate-700 ring-1 ring-inset ring-slate-200 hover:bg-slate-50"
                                  title="关联教案"
                                >
                                  📄 关联教案
                                </button>
                                <button
                                  @click="uploadResourceToChapter(child)"
                                  class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-50"
                                  title="上传资源"
                                >
                                  📎 上传
                                </button>
                                <button
                                  @click="editChapter(child)"
                                  class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-200 hover:bg-emerald-50"
                                  title="编辑章节"
                                >
                                  编辑
                                </button>
                                <button
                                  @click="deleteChapterConfirm(child)"
                                  class="inline-flex items-center rounded-xl bg-white px-2 py-1 text-xs font-medium text-red-600 ring-1 ring-inset ring-red-200 hover:bg-red-50"
                                  title="删除章节"
                                >
                                  删除
                                </button>
                              </div>
                            </div>
                            
                            <!-- 子章节教案列表 -->
                            <div v-if="expandedLessons.has(child.id)" class="ml-8 mt-1">
                              <ChapterLessonList
                                :chapter-id="child.id"
                                :can-unlink="true"
                                @refresh="handleChapterLessonRefresh(child.id)"
                                @view="handleViewLesson"
                              />
                            </div>
                            
                            <!-- 子章节资源列表 -->
                            <div v-if="expandedResources.has(child.id)" class="ml-8 mt-1" :data-chapter-id="child.id">
                              <ChapterResourceList
                                :chapter-id="child.id"
                                :can-delete="true"
                                @refresh="loadCurriculumTree"
                                @view="handleViewResource"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Empty State -->
                    <div v-else class="flex items-center gap-2 p-2 text-gray-500">
                      <span>📄</span>
                      <span class="text-sm">暂无章节</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 text-gray-500">
        暂无数据
      </div>
    </div>

    <!-- Course Form Modal -->
    <CourseFormModal
      v-if="showCourseModal"
      :course="editingCourse"
      :subjects="allSubjects"
      :grades="allGrades"
      @close="closeCourseModal"
      @save="handleSaveCourse"
    />

    <!-- Upload Resource Modal -->
    <UploadResourceModal
      v-model="showUploadModal"
      @success="handleUploadSuccess"
    />

    <!-- Import Chapters Modal -->
    <ImportChaptersModal
      :is-open="showImportChaptersModal"
      :courses="allCourses"
      @close="closeImportChaptersModal"
      @success="handleImportSuccess"
    />

    <!-- Course Export Import Modal -->
    <div v-if="showExportImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="mx-4 max-h-[90vh] w-full max-w-6xl overflow-y-auto rounded-2xl bg-white shadow-xl">
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">课程导出导入</h3>
            <button
              @click="closeExportImportModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <CourseExportImport />
        </div>
      </div>
    </div>

    <!-- Chapter Edit Modal -->
    <ChapterEditModal
      :is-open="showChapterEditModal"
      :chapter="editingChapter"
      :courses="allCourses"
      @close="closeChapterEditModal"
      @save="handleSaveChapter"
    />

    <!-- Chapter Resource Upload Modal -->
    <ChapterResourceUploadModal
      :is-open="showChapterResourceUploadModal"
      :chapter="uploadingToChapter"
      @close="closeChapterResourceUploadModal"
      @success="handleResourceUploadSuccess"
    />

    <!-- Associate Lesson Modal -->
    <AssociateLessonModal
      :is-open="showAssociateLessonModal"
      :chapter="associatingToChapter"
      :course-id="associatingToCourseId"
      @close="closeAssociateLessonModal"
      @success="handleAssociateLessonSuccess"
    />
    
    <CourseMergeModal
      :is-open="showMergeModal"
      :course-code="mergeCourseCode"
      :current-course-id="mergeCurrentCourseId"
      :service="researcherService"
      @close="closeMergeModal"
      @success="handleMergeSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import researcherService from '@/services/researcher'
import type { CurriculumTree, Subject, Grade, Course, CourseCreate, CourseUpdate } from '@/types/curriculum'
import CourseFormModal from './CourseFormModal.vue'
import UploadResourceModal from '@/components/Admin/UploadResourceModal.vue'
import ImportChaptersModal from '@/components/Curriculum/ImportChaptersModal.vue'
import CourseExportImport from '@/components/Admin/CourseExportImport.vue'
import ChapterEditModal from '../../components/Curriculum/ChapterEditModal.vue'
import ChapterResourceUploadModal from '../../components/Curriculum/ChapterResourceUploadModal.vue'
import ChapterResourceList from '../../components/Curriculum/ChapterResourceList.vue'
import ChapterLessonList from '../../components/Curriculum/ChapterLessonList.vue'
import SubjectGradeCourseLessonList from '../../components/Curriculum/SubjectGradeCourseLessonList.vue'
import AssociateLessonModal from '../../components/Curriculum/AssociateLessonModal.vue'
import CourseMergeModal from '../../components/Curriculum/CourseMergeModal.vue'
import { useToast } from '@/composables/useToast'
import { getServerBaseUrl } from '@/utils/url'

const toast = useToast()
const loading = ref(false)
const includeInactive = ref(false)
const curriculumTree = ref<CurriculumTree | null>(null)
const allSubjects = ref<Subject[]>([])
const allGrades = ref<Grade[]>([])
const dataLoaded = ref(false)

const expandedSubjects = ref(new Set<number>())
const expandedGrades = ref(new Set<string>())
const expandedCourses = ref(new Set<number>())
const expandedResources = ref(new Set<number>())
const expandedLessons = ref(new Set<number>())
const expandedSubjectLessons = ref(new Set<number>())
const expandedGradeLessons = ref(new Set<string>())
const expandedCourseLessons = ref(new Set<number>())
const courseChapters = ref<Map<number, any[]>>(new Map())
const loadingChapters = ref(new Set<number>())

const showCourseModal = ref(false)
const editingCourse = ref<{
  course?: Course
  subject?: Subject
  grade?: Grade
} | null>(null)

const showUploadModal = ref(false)
const showImportChaptersModal = ref(false)
const showExportImportModal = ref(false)
const showChapterEditModal = ref(false)
const editingChapter = ref<any>(null)
const showChapterResourceUploadModal = ref(false)
const uploadingToChapter = ref<any>(null)
const showAssociateLessonModal = ref(false)
const associatingToChapter = ref<any>(null)
const associatingToCourseId = ref<number>(0)
const showMergeModal = ref(false)
const mergeCourseCode = ref('')
const mergeCurrentCourseId = ref<number | undefined>(undefined)

// 计算所有课程的扁平列表（附带学科/年级名称，便于下拉展示与搜索）
const allCourses = computed(() => {
  if (!curriculumTree.value || !curriculumTree.value.subjects) return []
  const courses: any[] = []
  curriculumTree.value.subjects.forEach(subject => {
    if (subject.grades) {
      subject.grades.forEach(grade => {
        if (grade.courses) {
          grade.courses.forEach(course => {
            // 增强课程对象，附加学科/年级名称，供选择器展示和过滤
            courses.push({
              ...course,
              subject_name: subject.name,
              grade_name: grade.name
            })
          })
        }
      })
    }
  })
  return courses
})

onMounted(() => {
  loadCurriculumTree()
  loadSubjectsAndGrades()
})

async function loadCurriculumTree() {
  loading.value = true
  try {
    curriculumTree.value = await researcherService.getCurriculumTree(includeInactive.value)
  } catch (error) {
    console.error('Failed to load curriculum tree:', error)
    toast.error('加载课程体系失败')
  } finally {
    loading.value = false
  }
}

function toggleChapterResources(chapterId: number) {
  if (expandedResources.value.has(chapterId)) {
    expandedResources.value.delete(chapterId)
  } else {
    expandedResources.value.add(chapterId)
  }
}

function toggleChapterLessons(chapterId: number) {
  if (expandedLessons.value.has(chapterId)) {
    expandedLessons.value.delete(chapterId)
  } else {
    expandedLessons.value.add(chapterId)
  }
}

function toggleSubjectLessons(subjectId: number) {
  if (expandedSubjectLessons.value.has(subjectId)) {
    expandedSubjectLessons.value.delete(subjectId)
  } else {
    expandedSubjectLessons.value.add(subjectId)
  }
}

function toggleGradeLessons(subjectId: number, gradeId: number) {
  const key = `${subjectId}-${gradeId}`
  if (expandedGradeLessons.value.has(key)) {
    expandedGradeLessons.value.delete(key)
  } else {
    expandedGradeLessons.value.add(key)
  }
}

function toggleCourseLessons(courseId: number) {
  if (expandedCourseLessons.value.has(courseId)) {
    expandedCourseLessons.value.delete(courseId)
  } else {
    expandedCourseLessons.value.add(courseId)
  }
}

async function loadSubjectsAndGrades() {
  try {
    const [subjects, grades] = await Promise.all([
      researcherService.getSubjects(true),
      researcherService.getGrades(true)
    ])
    
    // Check if data is valid
    if (!Array.isArray(subjects) || !Array.isArray(grades)) {
      throw new Error(`Invalid data format: subjects is ${typeof subjects}, grades is ${typeof grades}`)
    }
    
    allSubjects.value = subjects
    allGrades.value = grades
    dataLoaded.value = true
  } catch (error) {
    console.error('Failed to load subjects and grades:', error)
    dataLoaded.value = false
  }
}

function toggleSubject(subjectId: number) {
  if (expandedSubjects.value.has(subjectId)) {
    expandedSubjects.value.delete(subjectId)
  } else {
    expandedSubjects.value.add(subjectId)
  }
}

function toggleGrade(subjectId: number, gradeId: number) {
  const key = `${subjectId}-${gradeId}`
  if (expandedGrades.value.has(key)) {
    expandedGrades.value.delete(key)
  } else {
    expandedGrades.value.add(key)
  }
}

async function toggleCourse(courseId: number) {
  if (expandedCourses.value.has(courseId)) {
    expandedCourses.value.delete(courseId)
  } else {
    expandedCourses.value.add(courseId)
    
    // 如果还没有加载章节，则加载
    if (!courseChapters.value.has(courseId)) {
      await loadCourseChapters(courseId)
    }
  }
}

async function loadCourseChapters(courseId: number) {
  try {
    loadingChapters.value.add(courseId)
    const chapters = await researcherService.getCourseChapters(courseId, true)
    courseChapters.value.set(courseId, chapters)
  } catch (error: any) {
    console.error('Failed to load chapters:', error)
    // 设置空数组以避免重复加载
    courseChapters.value.set(courseId, [])
  } finally {
    loadingChapters.value.delete(courseId)
  }
}

async function toggleSubjectStatus(subject: any) {
  try {
    await researcherService.toggleSubject(subject.id, !subject.is_active)
    await loadCurriculumTree()
    toast.success(subject.is_active ? '学科已禁用' : '学科已启用')
  } catch (error: any) {
    console.error('Failed to toggle subject:', error)
    toast.error(error.response?.data?.detail || '操作失败')
  }
}

async function toggleGradeStatus(grade: any) {
  try {
    await researcherService.toggleGrade(grade.id, !grade.is_active)
    await loadCurriculumTree()
    toast.success(grade.is_active ? '年级已禁用' : '年级已启用')
  } catch (error: any) {
    console.error('Failed to toggle grade:', error)
    toast.error(error.response?.data?.detail || '操作失败')
  }
}

function editCourse(course: any, subject: any, grade: any) {
  editingCourse.value = { course, subject, grade }
  showCourseModal.value = true
}

function openCourseModal() {
  if (!dataLoaded.value) {
    toast.warning('数据加载中，请稍候...')
    return
  }
  showCourseModal.value = true
}

function closeCourseModal() {
  showCourseModal.value = false
  editingCourse.value = null
}

async function handleSaveCourse(data: CourseCreate | CourseUpdate) {
  try {
    if (editingCourse.value?.course) {
      // Update existing course
      await researcherService.updateCourse(editingCourse.value.course.id, data as CourseUpdate)
      toast.success('课程更新成功')
    } else {
      // Create new course
      await researcherService.createCourse(data as CourseCreate)
      toast.success('课程创建成功')
    }
    await loadCurriculumTree()
    closeCourseModal()
  } catch (error: any) {
    console.error('Failed to save course:', error)
    toast.error(error.response?.data?.detail || '保存失败')
  }
}

async function deleteCourseConfirm(course: any) {
  if (course.lesson_count > 0) {
    toast.warning('该课程下有教案，无法删除')
    return
  }
  
  if (!confirm(`确定要删除课程"${course.name}"吗？此操作不可撤销。`)) {
    return
  }
  
  try {
    await researcherService.deleteCourse(course.id)
    toast.success('课程删除成功')
    await loadCurriculumTree()
  } catch (error: any) {
    console.error('Failed to delete course:', error)
    toast.error(error.response?.data?.detail || '删除失败')
  }
}

function openUploadModal() {
  showUploadModal.value = true
}

function handleUploadSuccess(resourceId: number) {
  console.log('Resource uploaded successfully:', resourceId)
  toast.success('资源上传成功！')
  // 可以选择刷新课程树以显示新资源
  loadCurriculumTree()
}

function openImportChaptersModal() {
  if (!dataLoaded.value) {
    toast.warning('数据加载中，请稍候...')
    return
  }
  showImportChaptersModal.value = true
}

function closeImportChaptersModal() {
  showImportChaptersModal.value = false
}

function openExportImportModal() {
  showExportImportModal.value = true
}

function closeExportImportModal() {
  showExportImportModal.value = false
}

function handleImportSuccess() {
  console.log('Chapters imported successfully')
  toast.success('章节导入成功！')
  loadCurriculumTree()
  
  // 清空已缓存的章节数据，强制重新加载
  courseChapters.value.clear()
}

// 处理资源查看
function handleViewResource(resource: any) {
  if (!resource.file_url) {
    toast.error('资源文件不存在')
    return
  }
  
  // 构建完整的查看URL
  const baseURL = getServerBaseUrl()
  const viewUrl = `${baseURL}${resource.file_url}`
  
  // 在新窗口中打开文件
  window.open(viewUrl, '_blank')
  
  toast.success('正在打开文件...')
}

// 章节编辑相关方法
function openAddChapterModal(course: any) {
  // 创建一个新章节对象，预填课程ID
  editingChapter.value = {
    course_id: course.id,
    name: '',
    code: '',
    description: '',
    parent_id: null,
    display_order: 0,
    is_active: true
  }
  showChapterEditModal.value = true
}

function editChapter(chapter: any) {
  console.log('editChapter called with:', chapter)
  editingChapter.value = chapter
  showChapterEditModal.value = true
  console.log('Modal should be open:', showChapterEditModal.value)
}

function closeChapterEditModal() {
  showChapterEditModal.value = false
  editingChapter.value = null
}

async function handleSaveChapter(data: any) {
  try {
    const courseId = data.course_id || editingChapter.value?.course_id
    
    if (editingChapter.value?.id) {
      // 更新现有章节
      await researcherService.updateChapter(editingChapter.value.id, data)
      toast.success('章节更新成功！')
    } else {
      // 创建新章节
      await researcherService.createChapter(data)
      toast.success('章节创建成功！')
    }
    
    // 重新加载相关课程的章节
    if (courseId) {
      courseChapters.value.delete(courseId)
      await loadCourseChapters(courseId)
    }
    
    closeChapterEditModal()
  } catch (error: any) {
    console.error('Failed to save chapter:', error)
    toast.error(error.response?.data?.detail || '保存失败')
  }
}

async function deleteChapterConfirm(chapter: any) {
  if (!confirm(`确定要删除章节"${chapter.name}"吗？此操作不可撤销。`)) {
    return
  }
  
  try {
    await researcherService.deleteChapter(chapter.id)
    toast.success('章节删除成功！')
    
    // 重新加载相关课程的章节
    if (chapter.course_id) {
      courseChapters.value.delete(chapter.course_id)
      await loadCourseChapters(chapter.course_id)
    }
  } catch (error: any) {
    console.error('Failed to delete chapter:', error)
    toast.error(error.response?.data?.detail || '删除失败')
  }
}

// 章节资源上传相关方法
function uploadResourceToChapter(chapter: any) {
  uploadingToChapter.value = chapter
  showChapterResourceUploadModal.value = true
}

function closeChapterResourceUploadModal() {
  showChapterResourceUploadModal.value = false
  uploadingToChapter.value = null
}

function handleResourceUploadSuccess(resourceId: number) {
  console.log('Resource uploaded successfully:', resourceId)
  toast.success('资源上传成功！')
  closeChapterResourceUploadModal()
}

// 关联教案相关方法
function associateLessonToChapter(chapter: any, course: any) {
  associatingToChapter.value = chapter
  associatingToCourseId.value = course.id
  showAssociateLessonModal.value = true
}

function closeAssociateLessonModal() {
  showAssociateLessonModal.value = false
  associatingToChapter.value = null
  associatingToCourseId.value = 0
}

function handleAssociateLessonSuccess() {
  console.log('Lessons associated successfully')
  // 重新加载相关课程的章节（以更新教案数量）
  if (associatingToChapter.value?.course_id) {
    courseChapters.value.delete(associatingToChapter.value.course_id)
    loadCourseChapters(associatingToChapter.value.course_id)
  }
  closeAssociateLessonModal()
}

function handleChapterLessonRefresh(chapterId: number) {
  // 重新加载相关课程的章节（以更新教案数量）
  const chapter = findChapterById(chapterId)
  if (chapter?.course_id) {
    courseChapters.value.delete(chapter.course_id)
    loadCourseChapters(chapter.course_id)
  }
}

// 课程合并相关方法
function openMergeModal(course: any) {
  if (!course.code) {
    toast.warning('该课程没有课程代码，无法合并')
    return
  }
  mergeCourseCode.value = course.code
  mergeCurrentCourseId.value = course.id
  showMergeModal.value = true
}

function closeMergeModal() {
  showMergeModal.value = false
  mergeCourseCode.value = ''
  mergeCurrentCourseId.value = undefined
}

async function handleMergeSuccess() {
  console.log('Courses merged successfully')
  // 重新加载课程树
  await loadCurriculumTree()
  closeMergeModal()
}

function findChapterById(chapterId: number): any {
  for (const chapters of courseChapters.value.values()) {
    const found = findChapterInTree(chapters, chapterId)
    if (found) return found
  }
  return null
}

function findChapterInTree(chapters: any[], chapterId: number): any {
  for (const chapter of chapters) {
    if (chapter.id === chapterId) return chapter
    if (chapter.children) {
      const found = findChapterInTree(chapter.children, chapterId)
      if (found) return found
    }
  }
  return null
}

// 查看教案
function handleViewLesson(lesson: any) {
  // 在新窗口中打开教案编辑页面
  // 使用教研员专用的教案查看路由
  const lessonUrl = `/researcher/lesson/${lesson.id}`
  window.open(lessonUrl, '_blank')
}

// 处理教案删除事件
async function handleLessonDeleted(lessonId: number) {
  // 重新加载课程树以更新教案数量
  await loadCurriculumTree()
}

</script>

<style scoped>
.curriculum-tree {
  max-height: 600px;
  overflow-y: auto;
}

.bg-purple-25 {
  background-color: rgb(250 245 255);
}

.hover\:bg-purple-75:hover {
  background-color: rgb(243 232 255);
}

.add-chapter-btn-container {
  display: flex;
  justify-content: flex-start;
  padding-left: 0.5rem;
}

.add-chapter-btn {
  transition: all 0.2s;
}

.add-chapter-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>

