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
  },

  /**
   * 获取精选科创课程列表（公开）
   * @param category 课程分类：人工智能、无人机、轮式机器人、开源硬件、虚拟仿真、3D打印等
   * @param limit 返回数量限制，默认20
   */
  async getFeaturedCourses(category?: string, limit: number = 20): Promise<Course[]> {
    const params: any = { limit }
    if (category) {
      params.category = category
    }
    return await api.get('/public/curriculum/featured-courses', { params })
  }
}

export default publicCurriculumService

