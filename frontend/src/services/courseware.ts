/**
 * 课件交互数据 API Service
 */
import axios from 'axios'

const BASE = '/api/v1/courseware'

export interface CoursewareInteraction {
  courseware_id: string
  courseware_title: string
  platform: string
  student_id: string
  total_questions: number
  correct_count: number
  score: number
  total_time_ms: number
  answers: Array<{
    questionIndex: number
    chosen: number
    correct: number
    isCorrect: boolean
    timeMs: number
  }>
  lesson_id?: number
  cell_id?: number
  teacher_id?: number
}

export interface DashboardOverview {
  total_interactions: number
  total_coursewares: number
  total_students: number
  avg_score: number
  avg_time_ms: number
}

export interface DailyTrend {
  date: string
  count: number
  avg_score: number
}

export interface TopCourseware {
  id: string
  title: string
  count: number
  avg_score: number
}

export interface DashboardData {
  overview: DashboardOverview
  daily_trend: DailyTrend[]
  top_coursewares: TopCourseware[]
}

export interface CoursewareSummary {
  courseware_id: string
  courseware_title: string
  platform: string
  total_sessions: number
  avg_score: number
  avg_time_ms: number
  student_count: number
  last_used: string | null
}

export interface StudentAnalytics {
  student_id: string
  total_interactions: number
  avg_score: number
  total_time_ms: number
  coursewares_used: number
  recent_scores: Array<{
    score: number
    courseware: string
    time: string | null
  }>
}

export const coursewareService = {
  /** 上报交互数据 */
  async reportInteraction(data: Partial<CoursewareInteraction>) {
    const res = await axios.post(`${BASE}/interactions`, data)
    return res.data
  },

  /** 获取看板概览 */
  async getDashboardOverview(days = 30): Promise<DashboardData> {
    const res = await axios.get(`${BASE}/dashboard/overview`, { params: { days } })
    return res.data
  },

  /** 获取课件分析 */
  async getCoursewareAnalytics(coursewareId: string, days = 30): Promise<CoursewareSummary> {
    const res = await axios.get(`${BASE}/analytics/courseware/${coursewareId}`, { params: { days } })
    return res.data
  },

  /** 获取学生分析 */
  async getStudentAnalytics(studentId: string, days = 30): Promise<StudentAnalytics> {
    const res = await axios.get(`${BASE}/analytics/student/${studentId}`, { params: { days } })
    return res.data
  },
}
