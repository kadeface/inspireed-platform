<template>
  <div class="evaluation-report">
    <div class="header">
      <h1>评价报告</h1>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 查询条件 -->
    <el-card class="filter-card">
      <el-form :model="queryForm" inline label-width="100px">
        <el-form-item label="基线考试">
          <el-select
            v-model="queryForm.baseline_exam_id"
            placeholder="选择基线考试"
            style="width: 200px;"
            @change="loadBaselineSubjects"
          >
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="`${exam.name} (${exam.exam_date.split('T')[0]})`"
              :value="exam.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="结束考试">
          <el-select
            v-model="queryForm.endline_exam_id"
            placeholder="选择结束考试"
            style="width: 200px;"
            @change="loadEndlineSubjects"
          >
            <el-option
              v-for="exam in exams"
              :key="exam.id"
              :label="`${exam.name} (${exam.exam_date.split('T')[0]})`"
              :value="exam.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="科目">
          <el-select
            v-model="queryForm.subject_id"
            placeholder="选择科目"
            style="width: 150px;"
          >
            <el-option
              v-for="subject in commonSubjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="评价范围">
          <el-select
            v-model="queryForm.scope_type"
            placeholder="选择范围"
            style="width: 120px;"
          >
            <el-option label="全区" value="region" />
            <el-option label="学校" value="school" />
            <el-option label="班级" value="classroom" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generateReport" :loading="generating">
            <el-icon><DataAnalysis /></el-icon>
            生成报告
          </el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 评价结果 -->
    <div v-if="reportData" class="report-content">
      <!-- 基本信息 -->
      <el-card class="summary-card" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>📊 评价概要</span>
          </div>
        </template>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="评价名称">{{ reportData.name }}</el-descriptions-item>
          <el-descriptions-item label="基线考试">
            {{ reportData.baseline_exam?.name }}
            <span style="color: #909399; font-size: 12px;">({{ reportData.baseline_exam?.date }})</span>
          </el-descriptions-item>
          <el-descriptions-item label="结束考试">
            {{ reportData.endline_exam?.name }}
            <span style="color: #909399; font-size: 12px;">({{ reportData.endline_exam?.date }})</span>
          </el-descriptions-item>
          <el-descriptions-item label="评价科目">{{ reportData.subject?.name }}</el-descriptions-item>
          <el-descriptions-item label="评价范围">
            <el-tag size="small">{{ getScopeTypeName(reportData.scope_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(reportData.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 指标对比表格 -->
      <el-card class="metrics-card" style="margin-bottom: 20px;">
        <template #header>
          <span>📈 增值指标对比</span>
        </template>

        <el-table :data="reportData.metrics" stripe border>
          <el-table-column prop="metric_name" label="指标" width="120" />
          <el-table-column label="基线值" width="120" align="center">
            <template #default="{ row }">
              <span class="baseline-value">{{ row.baseline_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="结束值" width="120" align="center">
            <template #default="{ row }">
              <span class="endline-value">{{ row.endline_rate }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="增值" width="120" align="center">
            <template #default="{ row }">
              <span :class="getValueClass(row.value_added)">
                {{ row.value_added > 0 ? '+' : '' }}{{ row.value_added }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column label="提升" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getImprovementType(row.improvement)" size="small">
                {{ row.improvement }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 20px; padding: 15px; background: #f5f7fa; border-radius: 4px;">
          <h4 style="margin: 0 0 10px 0;">💡 说明</h4>
          <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #606266;">
            <li><strong>增值</strong>：结束值减去基线值的差值（百分点）</li>
            <li><strong>正向增值</strong>：增值 > 0，表示进步</li>
            <li><strong>负向增值</strong>：增值 < 0，表示退步</li>
            <li><strong>显著提升</strong>：增值 ≥ 5个百分点</li>
            <li><strong>显著下降</strong>：增值 ≤ -5个百分点</li>
          </ul>
        </div>
      </el-card>

      <!-- 可视化图表 -->
      <el-card class="chart-card">
        <template #header>
          <span>📊 可视化图表</span>
        </template>

        <div class="chart-container">
          <div ref="barChartRef" style="height: 400px;"></div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="请选择条件并生成报告" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { examApi, evaluationApi } from '@/services/evaluation';
import type { Exam, Subject } from '@/types/evaluation';
import type { ValueAddedEvaluationSummary } from '@/types/evaluation';

const router = useRouter();

// 响应式数据
const exams = ref<Exam[]>([]);
const baselineSubjects = ref<Subject[]>([]);
const endlineSubjects = ref<Subject[]>([]);
const commonSubjects = ref<Subject[]>([]);
const reportData = ref<ValueAddedEvaluationSummary | null>(null);
const generating = ref(false);

// 图表引用
const barChartRef = ref<HTMLElement>();
let barChart: echarts.ECharts | null = null;

// 查询表单
const queryForm = reactive({
  baseline_exam_id: undefined,
  endline_exam_id: undefined,
  subject_id: undefined,
  scope_type: 'region',
  scope_id: undefined,
});

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};

// 加载考试列表
const loadExams = async () => {
  try {
    const completedExams = await examApi.list({
      status: 'completed',
    });
    // 按日期排序，最近的在前
    exams.value = completedExams.sort((a, b) =>
      new Date(b.exam_date).getTime() - new Date(a.exam_date).getTime()
    );
  } catch (error: any) {
    ElMessage.error('加载考试列表失败');
  }
};

// 加载基线考试科目
const loadBaselineSubjects = async () => {
  if (!queryForm.baseline_exam_id) {
    baselineSubjects.value = [];
    return;
  }

  try {
    const exam = await examApi.get(queryForm.baseline_exam_id);
    baselineSubjects.value = exam.subjects || [];
    updateCommonSubjects();
  } catch (error: any) {
    console.error('加载基线考试科目失败:', error);
  }
};

// 加载结束考试科目
const loadEndlineSubjects = async () => {
  if (!queryForm.endline_exam_id) {
    endlineSubjects.value = [];
    return;
  }

  try {
    const exam = await examApi.get(queryForm.endline_exam_id);
    endlineSubjects.value = exam.subjects || [];
    updateCommonSubjects();
  } catch (error: any) {
    console.error('加载结束考试科目失败:', error);
  }
};

// 更新共同科目
const updateCommonSubjects = () => {
  const baselineIds = new Set(baselineSubjects.value.map(s => s.id));
  const endlineIds = new Set(endlineSubjects.value.map(s => s.id));

  // 找出两个考试都有的科目
  commonSubjects.value = baselineSubjects.value.filter(s => endlineIds.has(s.id));

  // 如果没有共同科目，显示基线考试的科目
  if (commonSubjects.value.length === 0) {
    commonSubjects.value = baselineSubjects.value;
  }

  // 重置科目选择
  queryForm.subject_id = undefined;
};

// 生成报告
const generateReport = async () => {
  // 验证表单
  if (!queryForm.baseline_exam_id) {
    ElMessage.warning('请选择基线考试');
    return;
  }
  if (!queryForm.endline_exam_id) {
    ElMessage.warning('请选择结束考试');
    return;
  }
  if (queryForm.baseline_exam_id === queryForm.endline_exam_id) {
    ElMessage.warning('基线考试和结束考试不能相同');
    return;
  }
  if (!queryForm.subject_id) {
    ElMessage.warning('请选择科目');
    return;
  }

  generating.value = true;

  try {
    // 调用后端API计算增值评价
    const result = await evaluationApi.batchCreate(
      `${queryForm.baseline_exam_id}_${queryForm.endline_exam_id}评价`,
      queryForm.baseline_exam_id,
      queryForm.endline_exam_id,
      queryForm.subject_id,
      1, // region_id
      queryForm.scope_type,
      [] // classroom_ids (空表示全部)
    );

    // 获取评价汇总
    reportData.value = await evaluationApi.getSummary(result.evaluation_ids[0]);

    // 渲染图表
    await nextTick();
    renderChart();

    ElMessage.success('报告生成成功');
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '生成报告失败');
  } finally {
    generating.value = false;
  }
};

// 重置查询
const resetQuery = () => {
  queryForm.baseline_exam_id = undefined;
  queryForm.endline_exam_id = undefined;
  queryForm.subject_id = undefined;
  queryForm.scope_type = 'region';
  queryForm.scope_id = undefined;
  baselineSubjects.value = [];
  endlineSubjects.value = [];
  commonSubjects.value = [];
  reportData.value = null;
};

// 渲染图表
const renderChart = () => {
  if (!barChartRef.value || !reportData.value) return;

  // 销毁旧图表
  if (barChart) {
    barChart.dispose();
  }

  // 创建新图表
  barChart = echarts.init(barChartRef.value);

  const metrics = reportData.value.metrics;
  const categories = metrics.map(m => m.metric_name);
  const baselineData = metrics.map(m => m.baseline_rate);
  const endlineData = metrics.map(m => m.endline_rate);
  const valueAddedData = metrics.map(m => m.value_added);

  const option = {
    title: {
      text: '增值评价对比',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: {
      data: ['基线值', '结束值', '增值'],
      bottom: 10,
    },
    xAxis: {
      type: 'category',
      data: categories,
    },
    yAxis: {
      type: 'value',
      name: '百分比(%)',
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        name: '基线值',
        type: 'bar',
        data: baselineData,
        itemStyle: {
          color: '#909399',
        },
      },
      {
        name: '结束值',
        type: 'bar',
        data: endlineData,
        itemStyle: {
          color: '#409eff',
        },
      },
      {
        name: '增值',
        type: 'line',
        data: valueAddedData,
        itemStyle: {
          color: '#67c23a',
        },
        lineStyle: {
          width: 3,
        },
      },
    ],
  };

  barChart.setOption(option);
};

// 获取范围类型名称
const getScopeTypeName = (scopeType: string) => {
  const typeMap: Record<string, string> = {
    region: '全区',
    school: '学校',
    classroom: '班级',
  };
  return typeMap[scopeType] || scopeType;
};

// 获取增值值的样式类
const getValueClass = (value: number) => {
  if (value > 0) return 'value-positive';
  if (value < 0) return 'value-negative';
  return 'value-neutral';
};

// 获取提升类型
const getImprovementType = (improvement: string) => {
  const typeMap: Record<string, any> = {
    '显著提升': 'success',
    '提升': '',
    '持平': 'info',
    '下降': 'warning',
    '显著下降': 'danger',
  };
  return typeMap[improvement] || '';
};

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return '-';
  const date = new Date(time);
  return date.toLocaleString('zh-CN');
};

// 组件挂载
onMounted(() => {
  loadExams();
});
</script>

<style scoped>
.evaluation-report {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.filter-card {
  margin-bottom: 20px;
}

.summary-card,
.metrics-card,
.chart-card {
  margin-bottom: 20px;
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.baseline-value {
  color: #909399;
  font-weight: 600;
}

.endline-value {
  color: #409eff;
  font-weight: 600;
}

.value-positive {
  color: #67c23a;
  font-weight: 600;
}

.value-negative {
  color: #f56c6c;
  font-weight: 600;
}

.value-neutral {
  color: #909399;
  font-weight: 600;
}

.chart-container {
  width: 100%;
}

/* 响应式 */
@media (max-width: 768px) {
  .evaluation-report {
    padding: 10px;
  }

  .el-form--inline .el-form-item {
    display: block;
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>
