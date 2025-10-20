/**
 * 课程体系 API 服务
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
  ChapterUpdate
} from '@/types/curriculum'

export const curriculumService = {
  // ==================== Subject APIs ====================
  
  /**
   * 获取学科列表
   */
  async getSubjects(includeInactive = false): Promise<Subject[]> {
    return await api.get('/curriculum/subjects', {
      params: { include_inactive: includeInactive }
    })
  },

  /**
   * 启用/禁用学科
   */
  async toggleSubject(subjectId: number, isActive: boolean): Promise<Subject> {
    return await api.patch(`/curriculum/subjects/${subjectId}/toggle`, {
      is_active: isActive
    })
  },

  // ==================== Grade APIs ====================
  
  /**
   * 获取年级列表
   */
  async getGrades(includeInactive = false): Promise<Grade[]> {
    return await api.get('/curriculum/grades', {
      params: { include_inactive: includeInactive }
    })
  },

  /**
   * 启用/禁用年级
   */
  async toggleGrade(gradeId: number, isActive: boolean): Promise<Grade> {
    return await api.patch(`/curriculum/grades/${gradeId}/toggle`, {
      is_active: isActive
    })
  },

  // ==================== Course APIs ====================
  
  /**
   * 获取课程列表
   */
  async getCourses(params?: {
    subject_id?: number
    grade_id?: number
    include_inactive?: boolean
  }): Promise<Course[]> {
    return await api.get('/curriculum/courses', { params })
  },

  /**
   * 创建课程
   */
  async createCourse(data: CourseCreate): Promise<Course> {
    return await api.post('/curriculum/courses', data)
  },

  /**
   * 更新课程
   */
  async updateCourse(courseId: number, data: CourseUpdate): Promise<Course> {
    return await api.put(`/curriculum/courses/${courseId}`, data)
  },

  /**
   * 删除课程
   */
  async deleteCourse(courseId: number): Promise<void> {
    await api.delete(`/curriculum/courses/${courseId}`)
  },

  // ==================== Curriculum Tree API ====================
  
  /**
   * 获取完整的课程体系树形结构
   */
  async getCurriculumTree(includeInactive = false): Promise<CurriculumTree> {
    return await api.get('/curriculum/tree', {
      params: { include_inactive: includeInactive }
    })
  },

  // ==================== Helper Functions ====================
  
  /**
   * 根据学科ID和年级ID获取课程
   */
  async getCourseBySubjectAndGrade(
    subjectId: number,
    gradeId: number
  ): Promise<Course | null> {
    const courses = await this.getCourses({ subject_id: subjectId, grade_id: gradeId })
    return courses.length > 0 ? courses[0] : null
  },

  /**
   * 生成课程名称（学科名 + 年级名）
   */
  generateCourseName(subjectName: string, gradeName: string): string {
    return `${gradeName}${subjectName}`
  },

  // ==================== Chapter APIs ====================
  
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
  async batchImportChapters(courseId: number, file: File): Promise<{ message: string; chapters: Chapter[] }> {
    const formData = new FormData()
    formData.append('course_id', courseId.toString())
    formData.append('file', file)
    
    // 不要手动设置Content-Type，让浏览器自动设置multipart/form-data with boundary
    return await api.post('/chapters/batch-import', formData)
  },

  /**
   * 下载章节导入模板
   */
  async downloadChapterTemplate(): Promise<Blob> {
    return await api.downloadFile('/chapters/export-template')
  }
}

export default curriculumService

