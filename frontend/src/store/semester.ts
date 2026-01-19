import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { evaluationService } from '../services/evaluation'
import type { Semester } from '../types/evaluation'

export const useSemesterStore = defineStore('semester', () => {
  const currentSemester = ref<Semester | null>(null)
  const allSemesters = ref<Semester[]>([])
  const loading = ref(false)
  const initialized = ref(false)

  const isSet = computed(() => !!currentSemester.value)

  async function fetchSemesters() {
    loading.value = true
    try {
      const data = await evaluationService.semester.list()
      allSemesters.value = data
      
      // 优先查找设置为当前的学期
      const current = data.find(s => s.is_current)
      if (current) {
        currentSemester.value = current
      } else if (data.length > 0) {
        // 如果没有明确设置当前的，选择时间最晚的一个作为默认（或者不选）
        // 这里暂时选择第一个
        // currentSemester.value = data[0]
      }
      initialized.value = true
    } catch (error) {
      console.error('Failed to fetch semesters:', error)
    } finally {
      loading.value = false
    }
  }

  async function fetchCurrentSemester() {
    loading.value = true
    try {
      const data = await evaluationService.semester.getCurrent()
      currentSemester.value = data
      initialized.value = true
    } catch (error) {
      console.error('Failed to fetch current semester:', error)
      // 如果获取当前失败，尝试加载列表
      if (!initialized.value) {
        await fetchSemesters()
      }
    } finally {
      loading.value = false
    }
  }

  function setCurrentSemester(semester: Semester) {
    currentSemester.value = semester
  }

  return {
    currentSemester,
    allSemesters,
    loading,
    initialized,
    isSet,
    fetchSemesters,
    fetchCurrentSemester,
    setCurrentSemester
  }
})
