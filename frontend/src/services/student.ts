/**
 * 学生学习服务
 * 处理学生学习进度、笔记等本地数据管理
 */

import type {
  LearningProgress,
  LearningNote,
  LearningStats,
  LearningRecord,
  NoteRecord,
  Badge
} from '@/types/student'
import type { Lesson } from '@/types/lesson'

class StudentService {
  private readonly PROGRESS_KEY = 'student_lesson_progress'
  private readonly NOTES_PREFIX = 'lesson_'
  private readonly NOTES_SUFFIX = '_notes'
  private readonly COMPLETED_CELLS_SUFFIX = '_completed_cells'

  /**
   * 获取所有课程的学习进度
   */
  getAllProgress(): Record<number, number> {
    const saved = localStorage.getItem(this.PROGRESS_KEY)
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch (e) {
        console.error('Failed to load progress data:', e)
      }
    }
    return {}
  }

  /**
   * 获取特定课程的学习进度
   */
  getLessonProgress(lessonId: number): number {
    const allProgress = this.getAllProgress()
    return allProgress[lessonId] || 0
  }

  /**
   * 更新课程学习进度
   */
  updateLessonProgress(lessonId: number, progress: number): void {
    const allProgress = this.getAllProgress()
    allProgress[lessonId] = progress
    localStorage.setItem(this.PROGRESS_KEY, JSON.stringify(allProgress))
  }

  /**
   * 获取已完成的Cell列表
   */
  getCompletedCells(lessonId: number): string[] {
    const key = `${this.NOTES_PREFIX}${lessonId}${this.COMPLETED_CELLS_SUFFIX}`
    const saved = localStorage.getItem(key)
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch (e) {
        console.error('Failed to load completed cells:', e)
      }
    }
    return []
  }

  /**
   * 标记Cell为已完成
   */
  markCellAsCompleted(lessonId: number, cellId: string): void {
    const completedCells = new Set(this.getCompletedCells(lessonId))
    completedCells.add(cellId)
    const key = `${this.NOTES_PREFIX}${lessonId}${this.COMPLETED_CELLS_SUFFIX}`
    localStorage.setItem(key, JSON.stringify(Array.from(completedCells)))
  }

  /**
   * 批量标记多个Cell为已完成
   */
  markCellsAsCompleted(lessonId: number, cellIds: string[]): void {
    const completedCells = new Set(this.getCompletedCells(lessonId))
    cellIds.forEach(id => completedCells.add(id))
    const key = `${this.NOTES_PREFIX}${lessonId}${this.COMPLETED_CELLS_SUFFIX}`
    localStorage.setItem(key, JSON.stringify(Array.from(completedCells)))
  }

  /**
   * 获取课程笔记
   */
  getLessonNotes(lessonId: number): string {
    const key = `${this.NOTES_PREFIX}${lessonId}${this.NOTES_SUFFIX}`
    return localStorage.getItem(key) || ''
  }

  /**
   * 保存课程笔记
   */
  saveLessonNotes(lessonId: number, notes: string): void {
    const key = `${this.NOTES_PREFIX}${lessonId}${this.NOTES_SUFFIX}`
    localStorage.setItem(key, notes)
  }

  /**
   * 获取所有有笔记的课程
   */
  getAllNotes(lessons: Lesson[]): NoteRecord[] {
    const notes: NoteRecord[] = []
    
    for (const lesson of lessons) {
      const content = this.getLessonNotes(lesson.id)
      if (content && content.trim()) {
        notes.push({
          lessonId: lesson.id,
          lessonTitle: lesson.title,
          content,
          lastUpdated: new Date().toISOString() // TODO: 实际应保存笔记更新时间
        })
      }
    }
    
    return notes
  }

  /**
   * 计算学习统计数据
   */
  calculateStats(): LearningStats {
    const progressData = this.getAllProgress()
    const totalLessons = Object.keys(progressData).length
    const completedLessons = Object.values(progressData).filter(p => p === 100).length
    const inProgressLessons = Object.values(progressData).filter(p => p > 0 && p < 100).length
    
    // 简单估算学习时长（每个课程平均45分钟）
    const totalStudyTime = Math.round((totalLessons * 45) / 60)
    
    return {
      totalLessons,
      completedLessons,
      inProgressLessons,
      totalStudyTime
    }
  }

  /**
   * 获取最近学习记录
   */
  getRecentLessons(lessons: Lesson[], limit: number = 5): LearningRecord[] {
    const progressData = this.getAllProgress()
    const records: LearningRecord[] = []
    
    for (const [lessonIdStr, progress] of Object.entries(progressData)) {
      const lessonId = Number(lessonIdStr)
      const lesson = lessons.find(l => l.id === lessonId)
      if (lesson) {
        records.push({
          lessonId,
          lessonTitle: lesson.title,
          progress,
          lastStudied: new Date().toISOString(), // TODO: 实际应从localStorage读取最后学习时间
          studyTime: 0 // TODO: 实际应从localStorage读取学习时长
        })
      }
    }
    
    // 按学习时间排序，最近的在前
    return records.slice(0, limit)
  }

  /**
   * 计算成就徽章
   */
  calculateBadges(stats: LearningStats, notesCount: number): Badge[] {
    return [
      {
        id: 1,
        name: '初学者',
        description: '完成第一个课程',
        icon: '🎓',
        earned: stats.totalLessons >= 1,
        earnedAt: stats.totalLessons >= 1 ? new Date().toISOString() : undefined
      },
      {
        id: 2,
        name: '勤奋学习',
        description: '学习5个课程',
        icon: '📚',
        earned: stats.totalLessons >= 5,
        earnedAt: stats.totalLessons >= 5 ? new Date().toISOString() : undefined
      },
      {
        id: 3,
        name: '完成大师',
        description: '完成3个课程',
        icon: '🏆',
        earned: stats.completedLessons >= 3,
        earnedAt: stats.completedLessons >= 3 ? new Date().toISOString() : undefined
      },
      {
        id: 4,
        name: '笔记达人',
        description: '记录3篇笔记',
        icon: '📝',
        earned: notesCount >= 3,
        earnedAt: notesCount >= 3 ? new Date().toISOString() : undefined
      },
      {
        id: 5,
        name: '学习之星',
        description: '完成10个课程',
        icon: '⭐',
        earned: stats.completedLessons >= 10,
        earnedAt: stats.completedLessons >= 10 ? new Date().toISOString() : undefined
      },
      {
        id: 6,
        name: '坚持不懈',
        description: '学习时长超过10小时',
        icon: '💪',
        earned: stats.totalStudyTime >= 10,
        earnedAt: stats.totalStudyTime >= 10 ? new Date().toISOString() : undefined
      }
    ]
  }

  /**
   * 清除特定课程的学习数据
   */
  clearLessonData(lessonId: number): void {
    // 清除进度
    const allProgress = this.getAllProgress()
    delete allProgress[lessonId]
    localStorage.setItem(this.PROGRESS_KEY, JSON.stringify(allProgress))
    
    // 清除笔记
    const notesKey = `${this.NOTES_PREFIX}${lessonId}${this.NOTES_SUFFIX}`
    localStorage.removeItem(notesKey)
    
    // 清除已完成的Cell
    const cellsKey = `${this.NOTES_PREFIX}${lessonId}${this.COMPLETED_CELLS_SUFFIX}`
    localStorage.removeItem(cellsKey)
  }

  /**
   * 清除所有学习数据
   */
  clearAllData(): void {
    // 清除进度
    localStorage.removeItem(this.PROGRESS_KEY)
    
    // 清除所有笔记和已完成的Cell（需要遍历所有localStorage键）
    const keysToRemove: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && (key.includes(this.NOTES_PREFIX))) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(key => localStorage.removeItem(key))
  }

  /**
   * 导出学习数据（用于备份）
   */
  exportData(): string {
    const data = {
      progress: this.getAllProgress(),
      notes: {} as Record<number, string>,
      completedCells: {} as Record<number, string[]>,
      exportDate: new Date().toISOString()
    }
    
    // 导出所有笔记和已完成的Cell
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.includes(this.NOTES_PREFIX)) {
        const value = localStorage.getItem(key)
        if (value) {
          // 提取lesson ID
          const match = key.match(/lesson_(\d+)_/)
          if (match) {
            const lessonId = Number(match[1])
            if (key.includes(this.NOTES_SUFFIX)) {
              data.notes[lessonId] = value
            } else if (key.includes(this.COMPLETED_CELLS_SUFFIX)) {
              try {
                data.completedCells[lessonId] = JSON.parse(value)
              } catch (e) {
                console.error('Failed to parse completed cells:', e)
              }
            }
          }
        }
      }
    }
    
    return JSON.stringify(data, null, 2)
  }

  /**
   * 导入学习数据（用于恢复）
   */
  importData(jsonData: string): boolean {
    try {
      const data = JSON.parse(jsonData)
      
      // 导入进度
      if (data.progress) {
        localStorage.setItem(this.PROGRESS_KEY, JSON.stringify(data.progress))
      }
      
      // 导入笔记
      if (data.notes) {
        for (const [lessonId, content] of Object.entries(data.notes)) {
          const key = `${this.NOTES_PREFIX}${lessonId}${this.NOTES_SUFFIX}`
          localStorage.setItem(key, content as string)
        }
      }
      
      // 导入已完成的Cell
      if (data.completedCells) {
        for (const [lessonId, cells] of Object.entries(data.completedCells)) {
          const key = `${this.NOTES_PREFIX}${lessonId}${this.COMPLETED_CELLS_SUFFIX}`
          localStorage.setItem(key, JSON.stringify(cells))
        }
      }
      
      return true
    } catch (e) {
      console.error('Failed to import data:', e)
      return false
    }
  }
}

// 导出单例实例
export const studentService = new StudentService()

