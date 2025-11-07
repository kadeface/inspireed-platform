import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Lesson, LessonCreate } from '../types/lesson'
import type { Cell } from '../types/cell'
import type { LessonListParams } from '../types/api'
import { lessonService } from '../services/lesson'

export const useLessonStore = defineStore('lesson', () => {
  const currentLesson = ref<Lesson | null>(null)
  const lessons = ref<Lesson[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const error = ref<string | null>(null)
  const totalLessons = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  const cells = computed(() => currentLesson.value?.content || [])

  function setCurrentLesson(lesson: Lesson) {
    currentLesson.value = lesson
  }

  function setLessons(lessonList: Lesson[]) {
    lessons.value = lessonList
  }

  function addCell(cell: Cell) {
    if (currentLesson.value) {
      currentLesson.value.content.push(cell)
    }
  }

  function updateCell(cellId: string, updates: Partial<Cell>) {
    if (currentLesson.value) {
      const index = currentLesson.value.content.findIndex((c) => c.id === cellId)
      if (index !== -1) {
        currentLesson.value.content[index] = {
          ...currentLesson.value.content[index],
          ...updates,
        }
      }
    }
  }

  function deleteCell(cellId: string) {
    if (currentLesson.value) {
      currentLesson.value.content = currentLesson.value.content.filter((c) => c.id !== cellId)
    }
  }

  function reorderCells(fromIndex: number, toIndex: number) {
    if (currentLesson.value) {
      const cells = currentLesson.value.content
      const [removed] = cells.splice(fromIndex, 1)
      cells.splice(toIndex, 0, removed)
      
      // 更新order字段
      cells.forEach((cell, index) => {
        cell.order = index
      })
    }
  }

  function clear() {
    currentLesson.value = null
    lessons.value = []
    error.value = null
  }

  // ========== 异步操作方法 ==========

  /**
   * 加载教案列表
   */
  async function loadLessons(params?: LessonListParams) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await lessonService.fetchLessons({
        page: params?.page || currentPage.value,
        page_size: params?.page_size || pageSize.value,
        status: params?.status,
        search: params?.search,
        chapter_id: params?.chapter_id,
        grade_id: params?.grade_id,
        course_id: params?.course_id,
      })
      
      lessons.value = response.items
      totalLessons.value = response.total
      currentPage.value = response.page
      pageSize.value = response.page_size
      
      return response
    } catch (err: any) {
      error.value = err.message || '加载教案列表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 加载单个教案详情
   */
  async function loadLesson(id: number) {
    isLoading.value = true
    error.value = null
    
    try {
      const lesson = await lessonService.fetchLessonById(id)
      currentLesson.value = lesson
      return lesson
    } catch (err: any) {
      error.value = err.message || '加载教案详情失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 保存当前教案（自动判断创建或更新）
   */
  async function saveCurrentLesson() {
    if (!currentLesson.value) {
      throw new Error('没有要保存的教案')
    }

    isSaving.value = true
    error.value = null

    try {
      let savedLesson: Lesson

      if (currentLesson.value.id) {
        // 更新现有教案
        savedLesson = await lessonService.updateLesson(currentLesson.value.id, {
          title: currentLesson.value.title,
          description: currentLesson.value.description,
          content: currentLesson.value.content,
          tags: currentLesson.value.tags,
          status: currentLesson.value.status,
        })
      } else {
        // 创建新教案（理论上不会到这里，因为创建用 createNewLesson）
        savedLesson = await lessonService.createLesson({
          title: currentLesson.value.title,
          description: currentLesson.value.description,
          content: currentLesson.value.content,
          tags: currentLesson.value.tags,
        })
      }

      const wasPublished = currentLesson.value.status === 'published'
      const oldVersion = currentLesson.value.version || 1
      
      currentLesson.value = savedLesson

      // 更新列表中的教案
      const index = lessons.value.findIndex((l) => l.id === savedLesson.id)
      if (index !== -1) {
        lessons.value[index] = savedLesson
      }

      // 如果教案已发布且版本号增加，说明内容已更新，学生可以看到最新版本
      if (wasPublished && savedLesson.status === 'published' && savedLesson.version > oldVersion) {
        // 版本已更新，后端会自动更新 published_at 时间戳
        // 学生端会通过版本号检测到更新
      }

      return savedLesson
    } catch (err: any) {
      error.value = err.message || '保存教案失败'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 创建新教案
   */
  async function createNewLesson(template: LessonCreate) {
    isSaving.value = true
    error.value = null

    try {
      const newLesson = await lessonService.createLesson(template)
      currentLesson.value = newLesson
      
      // 将新教案添加到列表开头
      lessons.value.unshift(newLesson)
      totalLessons.value += 1

      return newLesson
    } catch (err: any) {
      error.value = err.message || '创建教案失败'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 发布当前教案
   */
  async function publishCurrentLesson() {
    if (!currentLesson.value?.id) {
      throw new Error('没有要发布的教案')
    }

    isSaving.value = true
    error.value = null

    try {
      const publishedLesson = await lessonService.publishLesson(currentLesson.value.id)
      currentLesson.value = publishedLesson

      // 更新列表中的教案
      const index = lessons.value.findIndex((l) => l.id === publishedLesson.id)
      if (index !== -1) {
        lessons.value[index] = publishedLesson
      }

      return publishedLesson
    } catch (err: any) {
      error.value = err.message || '发布教案失败'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 取消发布当前教案（切换回草稿状态）
   */
  async function unpublishCurrentLesson() {
    if (!currentLesson.value?.id) {
      throw new Error('没有要取消发布的教案')
    }

    isSaving.value = true
    error.value = null

    try {
      const unpublishedLesson = await lessonService.unpublishLesson(currentLesson.value.id)
      currentLesson.value = unpublishedLesson

      // 更新列表中的教案
      const index = lessons.value.findIndex((l) => l.id === unpublishedLesson.id)
      if (index !== -1) {
        lessons.value[index] = unpublishedLesson
      }

      return unpublishedLesson
    } catch (err: any) {
      error.value = err.message || '取消发布教案失败'
      throw err
    } finally {
      isSaving.value = false
    }
  }

  /**
   * 删除指定教案
   */
  async function deleteLessonById(id: number) {
    isLoading.value = true
    error.value = null

    try {
      await lessonService.deleteLesson(id)
      
      // 从列表中移除
      lessons.value = lessons.value.filter((l) => l.id !== id)
      totalLessons.value -= 1

      // 如果删除的是当前教案，清空
      if (currentLesson.value?.id === id) {
        currentLesson.value = null
      }
    } catch (err: any) {
      error.value = err.message || '删除教案失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 复制指定教案
   */
  async function duplicateLessonById(id: number) {
    isLoading.value = true
    error.value = null

    try {
      const duplicatedLesson = await lessonService.duplicateLesson(id)
      
      // 将复制的教案添加到列表开头
      lessons.value.unshift(duplicatedLesson)
      totalLessons.value += 1

      return duplicatedLesson
    } catch (err: any) {
      error.value = err.message || '复制教案失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // 状态
    currentLesson,
    lessons,
    cells,
    isLoading,
    isSaving,
    error,
    totalLessons,
    currentPage,
    pageSize,
    
    // 本地操作方法
    setCurrentLesson,
    setLessons,
    addCell,
    updateCell,
    deleteCell,
    reorderCells,
    clear,
    unpublishCurrentLesson,
    
    // 异步操作方法
    loadLessons,
    loadLesson,
    saveCurrentLesson,
    createNewLesson,
    publishCurrentLesson,
    deleteLessonById,
    duplicateLessonById,
  }
})

