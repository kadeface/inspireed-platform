/**
 * 学生相关类型定义
 */

/**
 * 学习进度记录
 */
export interface LearningProgress {
  lessonId: number
  progress: number  // 0-100
  completedCells: string[]
  lastStudied: string  // ISO date string
  studyTime: number  // minutes
}

/**
 * 学习笔记
 */
export interface LearningNote {
  lessonId: number
  content: string
  lastUpdated: string  // ISO date string
}

/**
 * 学习统计
 */
export interface LearningStats {
  totalLessons: number
  completedLessons: number
  inProgressLessons: number
  totalStudyTime: number  // hours
}

/**
 * 成就徽章
 */
export interface Badge {
  id: number
  name: string
  description: string
  icon: string
  earned: boolean
  earnedAt?: string  // ISO date string
}

/**
 * 学习记录
 */
export interface LearningRecord {
  lessonId: number
  lessonTitle: string
  progress: number
  lastStudied: string
  studyTime: number
}

/**
 * 笔记记录
 */
export interface NoteRecord {
  lessonId: number
  lessonTitle: string
  content: string
  lastUpdated: string
}

/**
 * 学生档案
 */
export interface StudentProfile {
  stats: LearningStats
  recentLessons: LearningRecord[]
  notes: NoteRecord[]
  badges: Badge[]
}

