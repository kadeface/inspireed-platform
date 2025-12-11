/**
 * 教研员 API 服务
 * 课程体系管理功能（从管理员端迁移而来）
 */
import api from './api'
import type {
  Subject,
  Grade,
  Course,
  CourseCreate,
  CourseUpdate,
  CurriculumTree,
  Chapter,
  ChapterCreate,
  ChapterUpdate,
  CourseWithChapters,
  CourseMergeRequest,
  CourseMergeResponse
} from '@/types/curriculum'

export const researcherService = {
  // ==================== Subject APIs ====================
  
  /**
   * 获取学科列表（教研员）
   */
  async getSubjects(includeInactive = false): Promise<Subject[]> {
    return await api.get('/researcher/curriculum/subjects', {
      params: { include_inactive: includeInactive }
    })
  },

  /**
   * 启用/禁用学科（教研员）
   */
  async toggleSubject(subjectId: number, isActive: boolean): Promise<Subject> {
    return await api.patch(`/researcher/curriculum/subjects/${subjectId}/toggle`, {
      is_active: isActive
    })
  },

  // ==================== Grade APIs ====================
  
  /**
   * 获取年级列表（教研员）
   */
  async getGrades(includeInactive = false): Promise<Grade[]> {
    return await api.get('/researcher/curriculum/grades', {
      params: { include_inactive: includeInactive }
    })
  },

  /**
   * 启用/禁用年级（教研员）
   */
  async toggleGrade(gradeId: number, isActive: boolean): Promise<Grade> {
    return await api.patch(`/researcher/curriculum/grades/${gradeId}/toggle`, {
      is_active: isActive
    })
  },

  // ==================== Course APIs ====================
  
  /**
   * 获取课程列表（教研员）
   */
  async getCourses(params?: {
    subject_id?: number
    grade_id?: number
    include_inactive?: boolean
  }): Promise<Course[]> {
    return await api.get('/researcher/curriculum/courses', { params })
  },

  /**
   * 创建课程（教研员）
   */
  async createCourse(data: CourseCreate): Promise<Course> {
    return await api.post('/researcher/curriculum/courses', data)
  },

  /**
   * 更新课程（教研员）
   */
  async updateCourse(courseId: number, data: CourseUpdate): Promise<Course> {
    return await api.put(`/researcher/curriculum/courses/${courseId}`, data)
  },

  /**
   * 删除课程（教研员）
   */
  async deleteCourse(courseId: number): Promise<void> {
    await api.delete(`/researcher/curriculum/courses/${courseId}`)
  },

  // ==================== Curriculum Tree API ====================
  
  /**
   * 获取完整的课程体系树形结构（教研员）
   */
  async getCurriculumTree(includeInactive = false): Promise<CurriculumTree> {
    return await api.get('/researcher/curriculum/tree', {
      params: { include_inactive: includeInactive }
    })
  },

  /**
   * 获取课程详情及其章节（包含统计数据）
   */
  async getCourseWithChapters(courseId: number): Promise<CourseWithChapters> {
    return await api.get(`/researcher/curriculum/courses/${courseId}/with-chapters`)
  },

  /**
   * 根据课程代码查找所有具有相同代码的课程
   */
  async getCoursesByCode(courseCode: string): Promise<Course[]> {
    return await api.get(`/researcher/curriculum/courses/by-code/${courseCode}`)
  },

  /**
   * 合并课程
   */
  async mergeCourses(mergeRequest: CourseMergeRequest): Promise<CourseMergeResponse> {
    return await api.post('/researcher/curriculum/courses/merge', mergeRequest)
  },

  // ==================== Helper Functions ====================
  
  /**
   * 根据学科ID和年级ID获取课程
   */
  async getCourseBySubjectAndGrade(
    subjectId: number,
    gradeId: number
  ): Promise<Course[]> {
    return await this.getCourses({ subject_id: subjectId, grade_id: gradeId })
  },

  /**
   * 生成课程名称（学科名 + 年级名）
   */
  generateCourseName(subjectName: string, gradeName: string): string {
    return `${gradeName}${subjectName}`
  },

  /**
   * 生成课程代码（grade{level}-{subjectCode}）
   */
  generateCourseCode(subjectCode: string, gradeLevel: number): string {
    return `grade${gradeLevel}-${subjectCode}`
  },

  // ==================== Chapter APIs (复用通用章节接口) ====================
  
  /**
   * 获取课程的章节列表（树形结构）
   */
  async getCourseChapters(courseId: number, includeChildren = true): Promise<Chapter[]> {
    return await api.get(`/chapters/courses/${courseId}/chapters`, {
      params: { include_children: includeChildren }
    })
  },

  /**
   * 获取章节详情
   */
  async getChapter(chapterId: number): Promise<Chapter> {
    return await api.get(`/chapters/${chapterId}`)
  },

  /**
   * 创建章节
   */
  async createChapter(data: ChapterCreate): Promise<Chapter> {
    return await api.post('/chapters', data)
  },

  /**
   * 更新章节
   */
  async updateChapter(chapterId: number, data: ChapterUpdate): Promise<Chapter> {
    return await api.put(`/chapters/${chapterId}`, data)
  },

  /**
   * 删除章节
   */
  async deleteChapter(chapterId: number): Promise<void> {
    await api.delete(`/chapters/${chapterId}`)
  },

  /**
   * 批量导入章节
   */
  async batchImportChapters(
    courseId: number,
    file: File,
    overwriteExisting = false
  ): Promise<{ message: string; chapters: Chapter[] }> {
    const formData = new FormData()
    formData.append('course_id', courseId.toString())
    formData.append('file', file)
    formData.append('overwrite_existing', overwriteExisting ? 'true' : 'false')
    
    return await api.post('/chapters/batch-import', formData)
  },

  /**
   * 下载章节导入模板
   */
  async downloadChapterTemplate(): Promise<Blob> {
    return await api.downloadFile('/chapters/export-template')
  }
}

export default researcherService

