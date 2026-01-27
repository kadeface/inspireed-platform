import api from './api'
import type {
  Course,
  CourseWithChapters,
  Subject
} from '@/types/curriculum'

export const publicCurriculumService = {
  /**
   * 获取全部启用学科（公开）
   */
  async getSubjects(): Promise<Subject[]> {
    return await api.get('/public/curriculum/subjects')
  },

  /**
   * 根据学科代码获取课程列表（公开）
   */
  async getCoursesBySubject(subjectCode: string, params?: { grade_id?: number }): Promise<Course[]> {
    return await api.get(`/public/curriculum/subjects/${subjectCode}/courses`, {
      params
    })
  },

  /**
   * 获取课程详情及章节树（公开）
   */
  async getCourseWithChapters(courseId: number): Promise<CourseWithChapters> {
    return await api.get(`/public/curriculum/courses/${courseId}/with-chapters`)
  }
}

export default publicCurriculumService

