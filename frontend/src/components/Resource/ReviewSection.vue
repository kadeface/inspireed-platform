<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">课程评价</h2>

    <!-- 评分统计 -->
    <div v-if="stats" class="bg-gray-50 rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- 平均评分 -->
        <div class="text-center">
          <div class="text-5xl font-bold text-gray-900">{{ stats.average_rating.toFixed(1) }}</div>
          <div class="flex items-center justify-center my-2">
            <div v-for="n in 5" :key="n" class="text-yellow-400">
              <svg class="w-6 h-6" :fill="n <= Math.round(stats.average_rating) ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
              </svg>
            </div>
          </div>
          <p class="text-sm text-gray-600">{{ stats.review_count }} 条评价</p>
        </div>

        <!-- 评分分布 -->
        <div class="space-y-2">
          <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="flex items-center">
            <span class="text-sm text-gray-600 w-8">{{ star }}星</span>
            <div class="flex-1 mx-2 bg-gray-200 rounded-full h-2">
              <div
                class="bg-yellow-400 h-2 rounded-full"
                :style="{ width: `${getStarPercentage(star)}%` }"
              ></div>
            </div>
            <span class="text-sm text-gray-600 w-8 text-right">{{ stats.rating_distribution[star] || 0 }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 我的评价 -->
    <div v-if="!myReview" class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
      <h3 class="font-semibold text-gray-900 mb-4">写下你的评价</h3>
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">评分</label>
        <div class="flex items-center gap-2">
          <button
            v-for="n in 5"
            :key="n"
            @click="newRating = n"
            class="text-3xl"
            :class="n <= newRating ? 'text-yellow-400' : 'text-gray-300'"
          >
            ⭐
          </button>
          <span class="ml-2 text-sm text-gray-600">{{ getRatingText(newRating) }}</span>
        </div>
      </div>
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">评论</label>
        <textarea
          v-model="newComment"
          rows="4"
          placeholder="分享你的学习体验..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        ></textarea>
      </div>
      <button
        @click="submitReview"
        :disabled="newRating === 0 || submitting"
        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {{ submitting ? '提交中...' : '提交评价' }}
      </button>
    </div>

    <!-- 编辑我的评价 -->
    <div v-else class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
      <div class="flex items-start justify-between mb-4">
        <h3 class="font-semibold text-gray-900">我的评价</h3>
        <div class="flex gap-2">
          <button
            v-if="!editing"
            @click="startEdit"
            class="text-blue-600 hover:text-blue-800 text-sm"
          >
            编辑
          </button>
          <button
            v-if="!editing"
            @click="deleteMyReview"
            class="text-red-600 hover:text-red-800 text-sm"
          >
            删除
          </button>
        </div>
      </div>

      <div v-if="!editing">
        <div class="flex items-center mb-2">
          <div class="flex">
            <span v-for="n in 5" :key="n" class="text-yellow-400">
              {{ n <= myReview.rating ? '⭐' : '☆' }}
            </span>
          </div>
          <span class="ml-2 text-sm text-gray-600">{{ getRatingText(myReview.rating) }}</span>
        </div>
        <p class="text-gray-700 whitespace-pre-wrap">{{ myReview.comment || '无评论内容' }}</p>
        <p class="text-xs text-gray-500 mt-2">
          {{ new Date(myReview.created_at).toLocaleString('zh-CN') }}
        </p>
      </div>

      <div v-else>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">评分</label>
          <div class="flex items-center gap-2">
            <button
              v-for="n in 5"
              :key="n"
              @click="editRating = n"
              class="text-3xl"
              :class="n <= editRating ? 'text-yellow-400' : 'text-gray-300'"
            >
              ⭐
            </button>
            <span class="ml-2 text-sm text-gray-600">{{ getRatingText(editRating) }}</span>
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">评论</label>
          <textarea
            v-model="editComment"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          ></textarea>
        </div>
        <div class="flex gap-2">
          <button
            @click="updateReview"
            :disabled="submitting"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
          >
            {{ submitting ? '保存中...' : '保存' }}
          </button>
          <button
            @click="cancelEdit"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
          >
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 其他评价列表 -->
    <div class="space-y-4">
      <h3 class="font-semibold text-gray-900 mb-4">全部评价 ({{ reviews.length }})</h3>
      
      <div v-if="loadingReviews" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <div v-else-if="reviews.length === 0" class="text-center py-8 text-gray-500">
        暂无评价，成为第一个评价的人吧！
      </div>

      <div v-else v-for="review in reviews" :key="review.id" class="border-b border-gray-200 pb-4">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0 w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
            <span class="text-sm font-medium text-gray-700">{{ review.user_name[0] }}</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="font-medium text-gray-900">{{ review.user_name }}</span>
              <span class="text-xs text-gray-500">
                {{ new Date(review.created_at).toLocaleDateString('zh-CN') }}
              </span>
            </div>
            <div class="flex items-center mb-2">
              <span v-for="n in 5" :key="n" class="text-yellow-400 text-sm">
                {{ n <= review.rating ? '⭐' : '☆' }}
              </span>
            </div>
            <p class="text-gray-700 text-sm whitespace-pre-wrap">{{ review.comment || '用户未留下评论' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reviewService } from '@/services/review'
import type { Review, ReviewWithUser, LessonRatingStats } from '@/services/review'

const props = defineProps<{
  lessonId: number
}>()

const emit = defineEmits<{
  (e: 'updated'): void
}>()

const stats = ref<LessonRatingStats | null>(null)
const myReview = ref<Review | null>(null)
const reviews = ref<ReviewWithUser[]>([])
const loadingReviews = ref(false)
const submitting = ref(false)
const editing = ref(false)

const newRating = ref(0)
const newComment = ref('')
const editRating = ref(0)
const editComment = ref('')

const loadData = async () => {
  loadingReviews.value = true
  try {
    // 加载评分统计
    stats.value = await reviewService.getLessonRatingStats(props.lessonId)
    
    // 加载我的评论
    myReview.value = await reviewService.getMyReview(props.lessonId)
    
    // 加载所有评论
    const allReviews = await reviewService.getLessonReviews(props.lessonId)
    // 过滤掉我的评论
    reviews.value = myReview.value 
      ? allReviews.filter(r => r.id !== myReview.value!.id)
      : allReviews
  } catch (e) {
    console.error('Failed to load reviews:', e)
  } finally {
    loadingReviews.value = false
  }
}

const getStarPercentage = (star: number): number => {
  if (!stats.value || stats.value.review_count === 0) return 0
  return ((stats.value.rating_distribution[star] || 0) / stats.value.review_count) * 100
}

const getRatingText = (rating: number): string => {
  const texts = ['', '很差', '一般', '还行', '不错', '非常好']
  return texts[rating] || ''
}

const submitReview = async () => {
  if (newRating.value === 0) {
    alert('请选择评分')
    return
  }

  submitting.value = true
  try {
    await reviewService.createReview({
      lesson_id: props.lessonId,
      rating: newRating.value,
      comment: newComment.value.trim() || undefined
    })
    
    newRating.value = 0
    newComment.value = ''
    
    await loadData()
    emit('updated')
  } catch (e: any) {
    alert(e.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const startEdit = () => {
  if (myReview.value) {
    editRating.value = myReview.value.rating
    editComment.value = myReview.value.comment || ''
    editing.value = true
  }
}

const cancelEdit = () => {
  editing.value = false
  editRating.value = 0
  editComment.value = ''
}

const updateReview = async () => {
  if (!myReview.value) return

  submitting.value = true
  try {
    await reviewService.updateReview(myReview.value.id, {
      rating: editRating.value,
      comment: editComment.value.trim() || undefined
    })
    
    editing.value = false
    await loadData()
    emit('updated')
  } catch (e: any) {
    alert(e.message || '更新失败')
  } finally {
    submitting.value = false
  }
}

const deleteMyReview = async () => {
  if (!myReview.value) return
  
  if (!confirm('确定要删除你的评价吗？')) return

  try {
    await reviewService.deleteReview(myReview.value.id)
    await loadData()
    emit('updated')
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

