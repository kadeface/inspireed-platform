<template>
  <div class="monitoring-report-detail">
    <div class="page-header flex items-center gap-4 mb-6">
      <el-button @click="router.back()" circle>
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <div>
        <h1 class="text-2xl font-bold text-gray-900">{{ report?.name }}</h1>
        <p class="text-gray-500 text-sm mt-1">
          {{ report?.academic_year }} · {{ report?.semester_type === 'up' ? '上学期' : '下学期' }}
          <el-tag :type="report?.report_type === 'primary' ? 'success' : 'primary'" size="small" class="ml-2">
            {{ report?.report_type === 'primary' ? '小学' : '初中' }}
          </el-tag>
        </p>
      </div>
    </div>

    <el-card v-loading="loading">
      <el-table :data="report?.school_rows ?? []" stripe border max-height="600">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="school_code" label="代码" width="90" />
        <el-table-column prop="school_name" label="学校名称" min-width="200" show-overflow-tooltip />

        <!-- 小学列 -->
        <template v-if="report?.report_type === 'primary'">
          <el-table-column label="六年级" align="center">
            <el-table-column prop="g6_score" label="得分" width="70" align="center" />
            <el-table-column prop="g6_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="五年级" align="center">
            <el-table-column prop="g5_score" label="得分" width="70" align="center" />
            <el-table-column prop="g5_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="四年级" align="center">
            <el-table-column prop="g4_score" label="得分" width="70" align="center" />
            <el-table-column prop="g4_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="3级合计" align="center">
            <el-table-column prop="g456_total_score" label="得分" width="80" align="center" />
            <el-table-column prop="g456_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="六年级增值" align="center">
            <el-table-column prop="g6_value_added_score" label="得分" width="80" align="center" />
            <el-table-column prop="g6_value_added_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="3级增值" align="center">
            <el-table-column prop="g456_value_added_score" label="得分" width="80" align="center" />
            <el-table-column prop="g456_value_added_rank" label="排名" width="70" align="center" />
          </el-table-column>
        </template>

        <!-- 初中列 -->
        <template v-else>
          <el-table-column label="九年级" align="center">
            <el-table-column prop="g9_score" label="得分" width="70" align="center" />
            <el-table-column prop="g9_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="八年级" align="center">
            <el-table-column prop="g8_score" label="得分" width="70" align="center" />
            <el-table-column prop="g8_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="七年级" align="center">
            <el-table-column prop="g7_score" label="得分" width="70" align="center" />
            <el-table-column prop="g7_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="3级合计" align="center">
            <el-table-column prop="g789_total_score" label="得分" width="80" align="center" />
            <el-table-column prop="g789_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="九年级增值" align="center">
            <el-table-column prop="g9_value_added_score" label="得分" width="80" align="center" />
            <el-table-column prop="g9_value_added_rank" label="排名" width="70" align="center" />
          </el-table-column>
          <el-table-column label="3级增值" align="center">
            <el-table-column prop="g789_value_added_score" label="得分" width="80" align="center" />
            <el-table-column prop="g789_value_added_rank" label="排名" width="70" align="center" />
          </el-table-column>
        </template>

        <el-table-column prop="remarks" label="备注" min-width="100" show-overflow-tooltip />
      </el-table>

      <el-empty v-if="!loading && (!report?.school_rows?.length)" description="暂无学校数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { monitoringReportApi } from '@/services/evaluation'
import type { MonitoringReportDetail } from '@/types/evaluation'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const report = ref<MonitoringReportDetail | null>(null)

const reportId = computed(() => Number(route.params.id))

async function loadDetail() {
  if (!reportId.value) return
  loading.value = true
  try {
    report.value = await monitoringReportApi.get(reportId.value)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '加载失败')
    router.back()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
.monitoring-report-detail {
  padding: 20px;
}
</style>
