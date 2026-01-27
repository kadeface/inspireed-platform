<template>
  <div class="semester-performance">
    <div class="header">
      <h1>学期表现分析</h1>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 学期选择 -->
    <el-card class="filter-card">
      <el-form :model="queryForm" inline label-width="100px">
        <el-form-item label="选择学期">
          <el-select
            v-model="queryForm.semester_id"
            placeholder="选择学期"
            style="width: 300px;"
            @change="loadSemesterData"
          >
            <el-option
              v-for="semester in semesters"
              :key="semester.id"
              :label="semester.name"
              :value="semester.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="年级">
          <el-select
            v-model="queryForm.grade_id"
            placeholder="选择年级"
            style="width: 200px;"
            @change="loadSemesterData"
          >
            <el-option
              v-for="grade in grades"
              :key="grade.id"
              :label="grade.name"
              :value="grade.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="loadSemesterData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            导出报告
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据展示区域 -->
    <div v-if="semesterData" class="content-area">
      <!-- 基本统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="考试总数" :value="semesterData.total_exams || 0">
              <template #suffix>
                <span>场</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="参与学生" :value="semesterData.total_students || 0">
              <template #suffix>
                <span>人</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="平均分" :value="semesterData.avg_score || 0" :precision="2">
              <template #suffix>
                <span>分</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic title="合格率" :value="semesterData.pass_rate || 0" :precision="2">
              <template #suffix>
                <span>%</span>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <!-- 图表展示 -->
      <el-row :gutter="20">
        <!-- 考试趋势图 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>📈 考试成绩趋势</span>
              </div>
            </template>
            <div ref="trendChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 科目对比图 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>📊 科目平均分对比</span>
              </div>
            </template>
            <div ref="subjectChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <!-- 等级分布饼图 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>🍰 成绩等级分布</span>
              </div>
            </template>
            <div ref="gradePieChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <!-- 学校排名 -->
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="card-header">
                <span>🏆 学校排名（平均分）</span>
              </div>
            </template>
            <div ref="schoolRankChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细数据表格 -->
      <el-card class="table-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>📋 考试详细数据</span>
          </div>
        </template>

        <el-table :data="examDetails" stripe border>
          <el-table-column prop="exam_name" label="考试名称" width="200" />
          <el-table-column prop="exam_date" label="考试日期" width="120" />
          <el-table-column prop="subject_name" label="科目" width="100" />
          <el-table-column prop="total_students" label="参考人数" width="100" align="center" />
          <el-table-column label="平均分" width="100" align="center">
            <template #default="{ row }">
              <span class="score-value">{{ row.avg_score?.toFixed(2) || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="最高分" width="100" align="center">
            <template #default="{ row }">
              <span class="score-max">{{ row.max_score || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="最低分" width="100" align="center">
            <template #default="{ row }">
              <span class="score-min">{{ row.min_score || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="优秀率" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="success" size="small">{{ row.excellent_rate?.toFixed(1) || 0 }}%</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="良好率" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="" size="small">{{ row.good_rate?.toFixed(1) || 0 }}%</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="合格率" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning" size="small">{{ row.pass_rate?.toFixed(1) || 0 }}%</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty v-else description="请选择学期查看数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import * as echarts from 'echarts';
import { semesterApi } from '@/services/evaluation';
import { curriculumService } from '@/services/curriculum';
import type { Semester } from '@/types/evaluation';
import type { Grade } from '@/types/curriculum';

const router = useRouter();

// 响应式数据
const loading = ref(false);
const semesters = ref<Semester[]>([]);
const grades = ref<Grade[]>([]);
const semesterData = ref<any>(null);
const examDetails = ref<any[]>([]);

// 图表引用
const trendChartRef = ref<HTMLElement>();
const subjectChartRef = ref<HTMLElement>();
const gradePieChartRef = ref<HTMLElement>();
const schoolRankChartRef = ref<HTMLElement>();

let trendChart: echarts.ECharts | null = null;
let subjectChart: echarts.ECharts | null = null;
let gradePieChart: echarts.ECharts | null = null;
let schoolRankChart: echarts.ECharts | null = null;

// 查询表单
const queryForm = reactive({
  semester_id: undefined,
  grade_id: undefined,
});

// 返回
const goBack = () => {
  router.push('/district-admin/exams');
};

// 加载学期列表
const loadSemesters = async () => {
  try {
    semesters.value = await semesterApi.list();
    // 默认选择当前学期
    const current = semesters.value.find(s => s.is_current);
    if (current) {
      queryForm.semester_id = current.id;
      await loadSemesterData();
    }
  } catch (error: any) {
    ElMessage.error('加载学期列表失败');
  }
};

// 加载年级列表
const loadGrades = async () => {
  try {
    grades.value = await curriculumService.getGrades();
  } catch (error: any) {
    ElMessage.error('加载年级列表失败');
  }
};

// 加载学期数据
const loadSemesterData = async () => {
  if (!queryForm.semester_id) {
    ElMessage.warning('请选择学期');
    return;
  }

  loading.value = true;

  try {
    // TODO: 替换为实际的API调用
    // const data = await evaluationApi.getSemesterPerformance(queryForm.semester_id, queryForm.grade_id);

    // 模拟数据（实际应该从后端API获取）
    await new Promise(resolve => setTimeout(resolve, 1000));

    semesterData.value = {
      total_exams: 6,
      total_students: 1234,
      avg_score: 78.5,
      pass_rate: 85.3,
      excellent_rate: 35.2,
      good_rate: 45.6,
    };

    // 模拟考试详细数据
    examDetails.value = [
      {
        exam_name: '第一次月考',
        exam_date: '2024-03-15',
        subject_name: '数学',
        total_students: 1234,
        avg_score: 76.5,
        max_score: 100,
        min_score: 32,
        excellent_rate: 32.5,
        good_rate: 43.2,
        pass_rate: 83.5,
      },
      {
        exam_name: '期中考试',
        exam_date: '2024-04-20',
        subject_name: '数学',
        total_students: 1234,
        avg_score: 78.2,
        max_score: 100,
        min_score: 28,
        excellent_rate: 35.8,
        good_rate: 45.1,
        pass_rate: 86.2,
      },
      {
        exam_name: '第二次月考',
        exam_date: '2024-05-18',
        subject_name: '数学',
        total_students: 1234,
        avg_score: 79.5,
        max_score: 100,
        min_score: 35,
        excellent_rate: 38.2,
        good_rate: 46.5,
        pass_rate: 87.8,
      },
      {
        exam_name: '第一次月考',
        exam_date: '2024-03-16',
        subject_name: '语文',
        total_students: 1234,
        avg_score: 75.8,
        max_score: 98,
        min_score: 40,
        excellent_rate: 28.5,
        good_rate: 42.3,
        pass_rate: 82.1,
      },
      {
        exam_name: '期中考试',
        exam_date: '2024-04-21',
        subject_name: '语文',
        total_students: 1234,
        avg_score: 77.2,
        max_score: 99,
        min_rate: 38,
        excellent_rate: 31.2,
        good_rate: 44.5,
        pass_rate: 84.5,
      },
      {
        exam_name: '第二次月考',
        exam_date: '2024-05-19',
        subject_name: '语文',
        total_students: 1234,
        avg_score: 78.1,
        max_score: 100,
        min_score: 42,
        excellent_rate: 33.5,
        good_rate: 45.8,
        pass_rate: 85.2,
      },
    ];

    // 渲染图表
    await nextTick();
    renderAllCharts();

    ElMessage.success('数据加载成功');
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载数据失败');
  } finally {
    loading.value = false;
  }
};

// 渲染所有图表
const renderAllCharts = () => {
  renderTrendChart();
  renderSubjectChart();
  renderGradePieChart();
  renderSchoolRankChart();
};

// 渲染趋势图
const renderTrendChart = () => {
  if (!trendChartRef.value) return;

  if (trendChart) {
    trendChart.dispose();
  }

  trendChart = echarts.init(trendChartRef.value);

  // 按考试分组数据
  const mathExams = examDetails.value.filter(e => e.subject_name === '数学');
  const chineseExams = examDetails.value.filter(e => e.subject_name === '语文');

  const xAxis = mathExams.map(e => e.exam_name);
  const mathScores = mathExams.map(e => e.avg_score);
  const chineseScores = chineseExams.map(e => e.avg_score);

  const option = {
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['数学', '语文'],
      bottom: 10,
    },
    xAxis: {
      type: 'category',
      data: xAxis,
      axisLabel: {
        interval: 0,
        rotate: 30,
      },
    },
    yAxis: {
      type: 'value',
      name: '平均分',
      min: 0,
      max: 100,
    },
    series: [
      {
        name: '数学',
        type: 'line',
        data: mathScores,
        smooth: true,
        itemStyle: {
          color: '#409eff',
        },
      },
      {
        name: '语文',
        type: 'line',
        data: chineseScores,
        smooth: true,
        itemStyle: {
          color: '#67c23a',
        },
      },
    ],
  };

  trendChart.setOption(option);
};

// 渲染科目对比图
const renderSubjectChart = () => {
  if (!subjectChartRef.value) return;

  if (subjectChart) {
    subjectChart.dispose();
  }

  subjectChart = echarts.init(subjectChartRef.value);

  // 计算各科目平均分
  const subjectScores: Record<string, number[]> = {};
  examDetails.value.forEach(exam => {
    if (!subjectScores[exam.subject_name]) {
      subjectScores[exam.subject_name] = [];
    }
    subjectScores[exam.subject_name].push(exam.avg_score);
  });

  const subjects = Object.keys(subjectScores);
  const avgScores = subjects.map(s => {
    const scores = subjectScores[s];
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  });

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: subjects,
    },
    yAxis: {
      type: 'value',
      name: '平均分',
      min: 0,
      max: 100,
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
        data: avgScores,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' },
          ]),
        },
        barWidth: '50%',
      },
    ],
  };

  subjectChart.setOption(option);
};

// 渲染等级分布饼图
const renderGradePieChart = () => {
  if (!gradePieChartRef.value) return;

  if (gradePieChart) {
    gradePieChart.dispose();
  }

  gradePieChart = echarts.init(gradePieChartRef.value);

  // 计算平均等级率
  const avgExcellent = examDetails.value.reduce((sum, e) => sum + e.excellent_rate, 0) / examDetails.value.length;
  const avgGood = examDetails.value.reduce((sum, e) => sum + e.good_rate, 0) / examDetails.value.length;
  const avgPass = examDetails.value.reduce((sum, e) => sum + e.pass_rate, 0) / examDetails.value.length;
  const avgFail = 100 - avgPass;

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}% ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: ['优秀', '良好', '合格', '不合格'],
    },
    series: [
      {
        name: '成绩等级',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: true,
          formatter: '{b}: {c}%',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
          },
        },
        data: [
          { value: avgExcellent.toFixed(1), name: '优秀', itemStyle: { color: '#67c23a' } },
          { value: avgGood.toFixed(1), name: '良好', itemStyle: { color: '#409eff' } },
          { value: (avgPass - avgExcellent - avgGood).toFixed(1), name: '合格', itemStyle: { color: '#e6a23c' } },
          { value: avgFail.toFixed(1), name: '不合格', itemStyle: { color: '#f56c6c' } },
        ],
      },
    ],
  };

  gradePieChart.setOption(option);
};

// 渲染学校排名图
const renderSchoolRankChart = () => {
  if (!schoolRankChartRef.value) return;

  if (schoolRankChart) {
    schoolRankChart.dispose();
  }

  schoolRankChart = echarts.init(schoolRankChartRef.value);

  // 模拟学校排名数据
  const schoolNames = ['第一中学', '第二中学', '第三中学', '第四中学', '第五中学'];
  const avgScores = [82.5, 79.3, 76.8, 74.2, 71.5];

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: '平均分',
      max: 100,
    },
    yAxis: {
      type: 'category',
      data: schoolNames,
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
        data: avgScores,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: '#ffd666' },
            { offset: 0.5, color: '#ffa39e' },
            { offset: 1, color: '#ff7875' },
          ]),
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}分',
        },
      },
    ],
  };

  schoolRankChart.setOption(option);
};

// 导出报告
const exportReport = () => {
  if (!semesterData.value) {
    ElMessage.warning('请先选择学期并加载数据');
    return;
  }

  ElMessage.info('导出功能开发中...');
  // TODO: 实现导出功能（Excel/PDF）
};

// 组件挂载
onMounted(() => {
  loadGrades();
  loadSemesters();
});
</script>

<style scoped>
.semester-performance {
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

.content-area {
  width: 100%;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.chart-card,
.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 16px;
  font-weight: 600;
}

.chart-container {
  height: 350px;
  width: 100%;
}

.score-value {
  color: #409eff;
  font-weight: 600;
}

.score-max {
  color: #67c23a;
  font-weight: 600;
}

.score-min {
  color: #f56c6c;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .semester-performance {
    padding: 10px;
  }

  .stats-row .el-col {
    margin-bottom: 10px;
  }

  .chart-container {
    height: 300px;
  }
}
</style>
