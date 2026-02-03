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
import { createLogger } from '../utils/logger'

const logger = createLogger('LESSON')
import { lessonService } from '../services/lesson'
import { isContentWithSections, sectionsToContent, sectionsToFlatCells, normalizeContentToSections } from '../utils/lessonContent'

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

  const cells = computed(() => {
    const c = currentLesson.value?.content
    if (!c) return []
    if (Array.isArray(c)) return c
    if (c && typeof c === 'object' && 'sections' in c && Array.isArray((c as any).sections)) {
      return (c as any).sections.flatMap((s: any) => s.cells || [])
    }
    return []
  })

  function setCurrentLesson(lesson: Lesson) {
    currentLesson.value = lesson
  }

  function setLessons(lessonList: Lesson[]) {
    lessons.value = lessonList
  }

  function addCell(cell: Cell) {
    if (!currentLesson.value) return
    const content = currentLesson.value.content
    if (Array.isArray(content)) {
      content.push(cell)
      return
    }
    if (isContentWithSections(content)) {
      const sections = content.sections || []
      const teaching = sections.find((s) => s.order === 1)
      if (teaching) {
        teaching.cells = teaching.cells || []
        cell.order = teaching.cells.length
        teaching.cells.push(cell)
      } else {
        const sec = {
          id: 'sec-default-1',
          name: '教学过程',
          type: 'default' as const,
          order: 1,
          is_collapsed: false,
          cells: [{ ...cell, order: 0 }],
        }
        sections.push(sec)
        sections.sort((a, b) => a.order - b.order)
      }
      currentLesson.value.content = sectionsToContent(sections)
    }
  }

  function updateCell(cellId: string | number, updates: Partial<Cell>) {
    if (!currentLesson.value) return
    const content = currentLesson.value.content
    if (Array.isArray(content)) {
      const index = content.findIndex((c) => String(c.id) === String(cellId))
      if (index !== -1) {
        content[index] = { ...content[index], ...updates } as Cell
      }
      return
    }
    if (isContentWithSections(content)) {
      const sections = content.sections || []
      for (const sec of sections) {
        const cells = sec.cells || []
        const idx = cells.findIndex((c) => String(c.id) === String(cellId))
        if (idx !== -1) {
          cells[idx] = { ...cells[idx], ...updates } as Cell
          currentLesson.value.content = sectionsToContent(sections)
          return
        }
      }
    }
  }

  function deleteCell(cellId: string | number) {
    if (!currentLesson.value) return
    const content = currentLesson.value.content
    if (Array.isArray(content)) {
      currentLesson.value.content = content.filter(
        (c) => String(c.id) !== String(cellId)
      )
      return
    }
    if (isContentWithSections(content)) {
      const sections = content.sections || []
      for (const sec of sections) {
        const before = (sec.cells || []).length
        sec.cells = (sec.cells || []).filter(
          (c) => String(c.id) !== String(cellId)
        )
        if (sec.cells.length !== before) {
          currentLesson.value.content = sectionsToContent(sections)
          return
        }
      }
    }
  }

  function reorderCells(fromIndex: number, toIndex: number) {
    if (!currentLesson.value) return
    const content = currentLesson.value.content
    if (!Array.isArray(content)) return // sections format: reorder not supported
    const cells = content
    const [removed] = cells.splice(fromIndex, 1)
    cells.splice(toIndex, 0, removed)
    cells.forEach((cell, index) => {
      cell.order = index
    })
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
        creator_only: params?.creator_only,
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

      // 调试日志：记录加载的数据（仅在开发环境）
      // 处理 content 可能是数组或对象（sections）的情况
      const contentCells = Array.isArray(lesson.content)
        ? lesson.content
        : isContentWithSections(lesson.content)
          ? sectionsToFlatCells(normalizeContentToSections(lesson.content))
          : []
      
      logger.debug('加载教案:', {
        lessonId: lesson.id,
        title: lesson.title,
        contentLength: contentCells.length,
        contentType: Array.isArray(lesson.content) ? 'array' : isContentWithSections(lesson.content) ? 'sections' : 'unknown',
        contentDetails: contentCells.map((cell: any, idx: number) => ({
          index: idx,
          id: cell?.id,
          type: cell?.type,
          order: cell?.order,
          hasContent: !!cell?.content,
        })),
        contentPreview: contentCells.slice(0, 2),
        version: lesson.version,
        updatedAt: lesson.updated_at,
      })

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
  // 保存锁，防止并发保存
  let isSavingInProgress = false
  
  async function saveCurrentLesson() {
    if (!currentLesson.value) {
      throw new Error('没有要保存的教案')
    }

    // 如果正在保存，等待当前保存完成
    if (isSavingInProgress) {
      console.warn('⚠️ 检测到并发保存请求，等待当前保存完成...')
      // 等待最多5秒
      let waitCount = 0
      while (isSavingInProgress && waitCount < 50) {
        await new Promise(resolve => setTimeout(resolve, 100))
        waitCount++
      }
      if (isSavingInProgress) {
        throw new Error('保存操作超时，请稍后重试')
      }
    }

    isSavingInProgress = true
    isSaving.value = true
    error.value = null

    try {
      let savedLesson: Lesson

      if (currentLesson.value.id) {
        // 更新现有教案；content 支持旧格式 Cell[] 或新格式 { sections: [...] }
        const content = currentLesson.value.content !== undefined && currentLesson.value.content !== null
          ? currentLesson.value.content
          : []

        const updateData = {
          title: currentLesson.value.title,
          description: currentLesson.value.description,
          content,
          tags: currentLesson.value.tags || [],
          cover_image_url: currentLesson.value.cover_image_url,
        }

        // 验证数据完整性
        if (!updateData.title) {
          throw new Error('教案标题不能为空')
        }

        const contentCells = Array.isArray(content)
          ? content
          : (content as any)?.sections?.flatMap((s: any) => s.cells || []) || []

        if (contentCells.length === 0 && !(content as any)?.sections?.length) {
          console.warn('⚠️ 警告：保存的教案 content 为空')
        }

        const beforeSaveCount = contentCells.length
        const beforeSaveIds = contentCells.map((c: any) => c?.id).filter(Boolean)
        
        savedLesson = await lessonService.updateLesson(currentLesson.value.id, updateData)
        
        // 保存后的 content 可能是 Array 或 { sections }
        const savedCells = Array.isArray(savedLesson.content)
          ? savedLesson.content
          : (savedLesson.content as any)?.sections?.flatMap((s: any) => s.cells || []) || []
        const afterSaveCount = savedCells.length
        const afterSaveIds = savedCells.map((c: any) => c?.id).filter(Boolean)

        // 检查保存前后数量是否一致
        if (beforeSaveCount !== afterSaveCount) {
          console.error('❌ 警告：保存前后 cell 数量不一致！', {
            beforeSave: beforeSaveCount,
            afterSave: afterSaveCount,
            beforeIds: beforeSaveIds,
            afterIds: afterSaveIds,
            missingIds: beforeSaveIds.filter(id => !afterSaveIds.includes(id)),
          })
        }
      } else {
        // 创建新教案（理论上不会到这里，因为创建用 createNewLesson）
        // LessonCreate.content 只接受 Cell[]，需要转换 sections 格式
        const contentForCreate = Array.isArray(currentLesson.value.content)
          ? currentLesson.value.content
          : isContentWithSections(currentLesson.value.content)
          ? sectionsToFlatCells(currentLesson.value.content.sections || [])
          : []
        
        savedLesson = await lessonService.createLesson({
          title: currentLesson.value.title,
          description: currentLesson.value.description,
          content: contentForCreate,
          tags: currentLesson.value.tags,
          course_id: currentLesson.value.course_id,
          chapter_id: currentLesson.value.chapter_id,
        })
      }

      const wasPublished = currentLesson.value.status === 'published'
      const oldVersion = currentLesson.value.version || 1
      
      const localCells = Array.isArray(currentLesson.value.content)
        ? currentLesson.value.content
        : (currentLesson.value.content as any)?.sections?.flatMap((s: any) => s.cells || []) || []
      const localContentLength = localCells.length
      const savedContentLength = Array.isArray(savedLesson.content)
        ? (savedLesson.content?.length || 0)
        : ((savedLesson.content as any)?.sections?.flatMap((s: any) => s.cells || [])?.length || 0)
      
      // 检查服务器返回数据的完整性
      // 注意：不要直接覆盖 savedLesson.content，这会触发 watch 并导致死循环
      // 只在数据严重不一致时（差异超过1）记录错误，但信任服务器返回的数据
      if (localContentLength !== savedContentLength) {
        const diff = Math.abs(localContentLength - savedContentLength)
        if (diff > 1) {
          // 数据严重不一致，记录错误
          console.error('❌ 严重错误：服务器返回的数据数量与本地不一致', {
            localLength: localContentLength,
            savedLength: savedContentLength,
            diff: diff
          })
        } else {
          // 差异较小（≤1），可能是正常的并发或时序问题，记录警告但继续
          console.warn('⚠️ 服务器返回的数据数量与本地有微小差异', {
            localLength: localContentLength,
            savedLength: savedContentLength,
            diff: diff
          })
        }
        // 关键：始终使用服务器返回的数据作为真实来源，避免客户端覆盖导致的状态不一致
        // 如果确实有数据丢失，应该在后端解决，而不是在前端"修复"
      }
      
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
      isSavingInProgress = false
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
  async function publishCurrentLesson(classroomIds: number[] = []) {
    if (!currentLesson.value?.id) {
      throw new Error('没有要发布的教案')
    }

    isSaving.value = true
    error.value = null

    try {
      // 先保存当前教案内容，确保最新的单元（包括活动单元）已经写入后端
      const lessonToUpdate = currentLesson.value
      await lessonService.updateLesson(lessonToUpdate.id, {
        title: lessonToUpdate.title,
        description: lessonToUpdate.description,
        content: lessonToUpdate.content,
        tags: lessonToUpdate.tags,
      })

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

