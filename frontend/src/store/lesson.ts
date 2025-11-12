import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Lesson,
  LessonCreate,
  LessonClassroom,
  LessonRelatedMaterial
} from '../types/lesson'
import type { Cell } from '../types/cell'
import type { LessonListParams } from '../types/api'
import { lessonService } from '../services/lesson'

export const useLessonStore = defineStore('lesson', () => {
  const currentLesson = ref<Lesson | null>(null)
  const lessons = ref<Lesson[]>([])
  const isLoading = ref(false)
  const isSaving = ref(false)
  const isLoadingClassrooms = ref(false)
  const error = ref<string | null>(null)
  const classroomsError = ref<string | null>(null)
  const totalLessons = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  const availableClassrooms = ref<LessonClassroom[]>([])
  const pendingReferenceMaterials = ref<LessonRelatedMaterial[]>([])

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

  function updateCell(cellId: string | number, updates: Partial<Cell>) {
    if (currentLesson.value) {
      const index = currentLesson.value.content.findIndex(
        (c) => String(c.id) === String(cellId)
      )
      if (index !== -1) {
        currentLesson.value.content[index] = {
          ...currentLesson.value.content[index],
          ...updates,
        } as Cell
      }
    }
  }

  function deleteCell(cellId: string | number) {
    if (currentLesson.value) {
      currentLesson.value.content = currentLesson.value.content.filter(
        (c) => String(c.id) !== String(cellId)
      )
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

  function queueReferenceMaterial(material: LessonRelatedMaterial) {
    const exists = pendingReferenceMaterials.value.some((item) => item.id === material.id)
    if (!exists) {
      pendingReferenceMaterials.value.push(material)
    }
  }

  function removeQueuedReference(materialId: number) {
    pendingReferenceMaterials.value = pendingReferenceMaterials.value.filter(
      (item) => item.id !== materialId
    )
  }

  function consumeReferenceQueue() {
    const queue = [...pendingReferenceMaterials.value]
    pendingReferenceMaterials.value = []
    return queue
  }

  function clear() {
    currentLesson.value = null
    lessons.value = []
    error.value = null
    pendingReferenceMaterials.value = []
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
        })
      } else {
        // 创建新教案（理论上不会到这里，因为创建用 createNewLesson）
        savedLesson = await lessonService.createLesson({
          title: currentLesson.value.title,
          description: currentLesson.value.description,
          content: currentLesson.value.content,
          tags: currentLesson.value.tags,
          course_id: currentLesson.value.course_id,
          chapter_id: currentLesson.value.chapter_id,
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
  async function publishCurrentLesson(classroomIds: number[]) {
    if (!currentLesson.value?.id) {
      throw new Error('没有要发布的教案')
    }

    if (!classroomIds || classroomIds.length === 0) {
      throw new Error('请选择至少一个班级')
    }

    isSaving.value = true
    error.value = null

    try {
      const publishedLesson = await lessonService.publishLesson(
        currentLesson.value.id,
        classroomIds
      )
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

  /**
   * 获取教师可用的班级列表
   */
  async function loadAvailableClassrooms(force = false) {
    if (availableClassrooms.value.length > 0 && !force) {
      return
    }

    isLoadingClassrooms.value = true
    classroomsError.value = null

    try {
      availableClassrooms.value = await lessonService.fetchAvailableClassrooms()
    } catch (err: any) {
      const message = err.message || '获取班级列表失败'
      classroomsError.value = message
      throw err
    } finally {
      isLoadingClassrooms.value = false
    }
  }

  return {
    // 状态
    currentLesson,
    lessons,
    cells,
    isLoading,
    isSaving,
    isLoadingClassrooms,
    error,
    classroomsError,
    totalLessons,
    currentPage,
    pageSize,
    availableClassrooms,
    pendingReferenceMaterials,
    
    // 本地操作方法
    setCurrentLesson,
    setLessons,
    addCell,
    updateCell,
    deleteCell,
    reorderCells,
    queueReferenceMaterial,
    removeQueuedReference,
    consumeReferenceQueue,
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
    loadAvailableClassrooms,
  }
})

