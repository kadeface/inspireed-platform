/**
 * 增值评价系统API服务
 *
 * 提供所有评价系统相关的API调用封装
 */

import axios from 'axios';
import type {
  Semester,
  SemesterCreate,
  SemesterUpdate,
  Exam,
  ExamCreate,
  ExamUpdate,
  ExamSubject,
  Score,
  ExamScoreStatistics,
  DailyPerformanceScore,
  DailyPerformanceScoreCreate,
  ExamTotalScore,
  ExamTotalScoreCreate,
  ImportTask,
  ImportTaskCreate,
  ValueAddedEvaluation,
  ValueAddedEvaluationCreate,
  ValueAddedEvaluationSummary,
  PaginationParams,
} from '@/types/evaluation';

/**
 * 动态获取API基础URL
 * 与 api.ts 中的逻辑保持一致
 */
function getApiBaseUrl(): string {
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  
  // 如果环境变量中配置了API地址，优先使用
  if (import.meta.env.VITE_API_BASE_URL) {
    const envApiUrl = import.meta.env.VITE_API_BASE_URL
    // 如果环境变量已经包含完整路径，直接返回
    if (envApiUrl.startsWith('http://') || envApiUrl.startsWith('https://')) {
      return envApiUrl
    }
  }
  
  // Cloud Studio 环境
  if (hostname.includes('cloudstudio.club') || hostname.includes('coding.net')) {
    if (hostname.includes('--')) {
      const backendHostname = hostname.replace(/--\d+/, '--8000')
      return `https://${backendHostname}/api/v1`
    }
  }
  
  // 本地开发环境：前端端口5173 -> 后端端口8000
  const apiProtocol = protocol === 'https:' ? 'https:' : 'http:'
  return `${apiProtocol}//${hostname}:8000/api/v1`
}

const API_BASE_URL = getApiBaseUrl();

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // 如果是FormData，删除Content-Type让浏览器自动设置（包含boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理错误
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      // 401: 未授权，跳转登录
      if (status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(error);
      }

      // 403: 权限不足
      if (status === 403) {
        console.error('权限不足:', data?.detail || '无权访问此资源');
      }

      // 404: 资源不存在
      if (status === 404) {
        console.error('资源不存在:', data?.detail || '资源未找到');
      }

      // 422: 数据验证错误
      if (status === 422) {
        // Pydantic 验证错误通常是数组格式
        if (Array.isArray(data?.detail)) {
          const errors = data.detail.map((err: any) => {
            const field = err.loc?.join('.') || 'field';
            const msg = err.msg || 'validation error';
            return `${field}: ${msg}`;
          }).join('; ');
          console.error('数据验证失败:', errors);
          console.error('详细错误信息:', data.detail);
        } else {
          console.error('数据验证失败:', data?.detail || '数据格式不正确');
        }
      }

      return Promise.reject(error);
    }

    return Promise.reject(error);
  }
);

// ============================================================================
// 学期管理API
// ============================================================================

export const semesterApi = {
  /** 获取学期列表 */
  list: async (params?: PaginationParams & {
    year?: number;
    is_current?: boolean;
    region_id?: number;
  }): Promise<Semester[]> => {
    return apiClient.get('/semesters/', { params });
  },

  /** 获取当前学期 */
  getCurrent: async (): Promise<Semester> => {
    return apiClient.get('/semesters/current/');
  },

  /** 获取学期详情 */
  get: async (id: number): Promise<Semester> => {
    return apiClient.get(`/semesters/${id}`);
  },

  /** 创建学期 */
  create: async (data: SemesterCreate): Promise<Semester> => {
    return apiClient.post('/semesters/', data);
  },

  /** 更新学期 */
  update: async (id: number, data: SemesterUpdate): Promise<Semester> => {
    return apiClient.put(`/semesters/${id}`, data);
  },

  /** 删除学期 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/semesters/${id}`);
  },
};

// ============================================================================
// 考试管理API
// ============================================================================

export const examApi = {
  /** 获取考试列表 */
  list: async (params?: PaginationParams & {
    semester_id?: number;
    exam_type?: string;
    status?: string;
    grade_id?: number;
    region_id?: number;
    school_id?: number;
  }): Promise<Exam[]> => {
    return apiClient.get('/exams/', { params });
  },

  /** 获取考试详情 */
  get: async (id: number): Promise<Exam> => {
    return apiClient.get(`/exams/${id}`);
  },

  /** 创建考试 */
  create: async (data: ExamCreate): Promise<Exam> => {
    return apiClient.post('/exams/', data);
  },

  /** 更新考试 */
  update: async (id: number, data: ExamUpdate): Promise<Exam> => {
    return apiClient.put(`/exams/${id}`, data);
  },

  /** 删除考试 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/exams/${id}`);
  },

  /** 添加考试科目 */
  addSubject: async (examId: number, data: {
    subject_id: number;
    full_score: number;
    pass_line: number;
    excellent_line: number;
    good_line: number;
  }): Promise<ExamSubject> => {
    return apiClient.post(`/exams/${examId}/subjects`, data);
  },

  /** 获取考试科目 */
  getSubjects: async (examId: number): Promise<ExamSubject[]> => {
    return apiClient.get(`/exams/${examId}/subjects`);
  },

  /** 导入考生信息（考号映射） */
  importStudents: async (
    examId: number,
    file: File
  ): Promise<{
    total: number;
    success: number;
    failed: number;
    created: number;
    updated: number;
    skipped: number;
    errors: Array<{
      row: number;
      field?: string | null;
      message: string;
    }>;
  }> => {
    const formData = new FormData();
    formData.append('file', file);

    // 不需要手动设置 Content-Type，拦截器会自动处理 FormData
    return apiClient.post(`/exams/${examId}/students/import`, formData);
  },
};

// ============================================================================
// 成绩查询API
// ============================================================================

export const scoreApi = {
  /** 获取成绩列表 */
  list: async (params?: PaginationParams & {
    exam_id?: number;
    subject_id?: number;
    student_id?: number;
    min_score?: number;
    max_score?: number;
    grade_level?: string;
  }): Promise<Score[]> => {
    return apiClient.get('/scores/', { params });
  },

  /** 获取成绩详情 */
  get: async (id: number): Promise<Score> => {
    return apiClient.get(`/scores/${id}`);
  },

  /** 获取考试统计 */
  getStatistics: async (
    examId: number,
    subjectId?: number
  ): Promise<ExamScoreStatistics> => {
    const params = subjectId ? { subject_id: subjectId } : {};
    return apiClient.get(`/scores/exams/${examId}/statistics`, { params });
  },

  /** 获取学生考试成绩 */
  getStudentExamScores: async (
    studentId: number,
    semesterId?: number
  ): Promise<{
    student_id: number;
    exams: Array<any>;
  }> => {
    const params = semesterId ? { semester_id: semesterId } : {};
    return apiClient.get(`/scores/students/${studentId}/exams`, { params });
  },

  /** 获取班级考试成绩 */
  getClassroomExamScores: async (
    classroomId: number,
    examId: number,
    subjectId?: number
  ): Promise<{
    classroom_id: number;
    exam_id: number;
    subject_id?: number;
    total_count: number;
    scores: Array<any>;
  }> => {
    const params = subjectId ? { subject_id: subjectId } : {};
    return apiClient.get(`/scores/classrooms/${classroomId}/exams/${examId}`, { params });
  },
};

// ============================================================================
// 日常表现成绩API
// ============================================================================

export const dailyPerformanceApi = {
  /** 计算学生日常表现成绩 */
  calculate: async (data: DailyPerformanceScoreCreate): Promise<DailyPerformanceScore> => {
    return apiClient.post('/daily-performance/calculate', data);
  },

  /** 批量计算班级成绩 */
  batchCalculate: async (data: {
    classroom_id: number;
    period_name: string;
    start_date: string;
    end_date: string;
  }): Promise<{
    success_count: number;
    failed_count: number;
    results: DailyPerformanceScore[];
  }> => {
    return apiClient.post('/daily-performance/batch-calculate', data);
  },

  /** 获取日常表现成绩列表 */
  list: async (params?: PaginationParams & {
    student_id?: number;
    classroom_id?: number;
    semester_id?: number;
  }): Promise<DailyPerformanceScore[]> => {
    return apiClient.get('/daily-performance/', { params });
  },

  /** 获取成绩详情 */
  get: async (id: number): Promise<DailyPerformanceScore> => {
    return apiClient.get(`/daily-performance/${id}`);
  },

  /** 更新成绩 */
  update: async (id: number, data: Partial<DailyPerformanceScore>): Promise<DailyPerformanceScore> => {
    return apiClient.put(`/daily-performance/${id}`, data);
  },

  /** 删除成绩 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/daily-performance/${id}`);
  },

  /** 获取学生历史记录 */
  getStudentHistory: async (studentId: number): Promise<DailyPerformanceScore[]> => {
    return apiClient.get(`/daily-performance/students/${studentId}/history`);
  },

  /** 获取班级统计 */
  getClassroomStatistics: async (classroomId: number): Promise<{
    classroom_id: number;
    total_students: number;
    average_score: number;
    grade_distribution: Record<string, number>;
  }> => {
    return apiClient.get(`/daily-performance/classrooms/${classroomId}/statistics`);
  },
};

// ============================================================================
// 高中总分评价API
// ============================================================================

export const totalScoreApi = {
  /** 创建总分评价 */
  create: async (data: ExamTotalScoreCreate): Promise<ExamTotalScore> => {
    return apiClient.post('/total-scores/', data);
  },

  /** 批量创建 */
  batchCreate: async (data: {
    exam_id: number;
    scores: Array<{
      student_id: number;
      total_score: number;
      student_type: string;
    }>;
  }): Promise<{
    success_count: number;
    failed_count: number;
    results: ExamTotalScore[];
  }> => {
    return apiClient.post('/total-scores/batch', data);
  },

  /** 获取总分列表 */
  list: async (params?: PaginationParams & {
    exam_id?: number;
    student_id?: number;
    student_type?: string;
  }): Promise<ExamTotalScore[]> => {
    return apiClient.get('/total-scores/', { params });
  },

  /** 获取详情 */
  get: async (id: number): Promise<ExamTotalScore> => {
    return apiClient.get(`/total-scores/${id}`);
  },

  /** 更新 */
  update: async (id: number, data: Partial<ExamTotalScore>): Promise<ExamTotalScore> => {
    return apiClient.put(`/total-scores/${id}`, data);
  },

  /** 删除 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/total-scores/${id}`);
  },

  /** 获取考试统计 */
  getExamStatistics: async (examId: number): Promise<{
    exam_id: number;
    total_count: number;
    average_score: number;
    score_distribution: Record<string, number>;
    reach_statistics: Record<string, number>;
  }> => {
    return apiClient.get(`/total-scores/exams/${examId}/statistics`);
  },

  /** 获取学生历史 */
  getStudentHistory: async (studentId: number): Promise<ExamTotalScore[]> => {
    return apiClient.get(`/total-scores/students/${studentId}/history`);
  },

  /** 获取考试排名 */
  getExamRanking: async (examId: number, params?: {
    student_type?: string;
    top_n?: number;
  }): Promise<{
    exam_id: number;
    ranking: Array<{
      rank: number;
      student_id: number;
      student_name: string;
      total_score: number;
      student_type: string;
    }>;
  }> => {
    return apiClient.get(`/total-scores/exams/${examId}/ranking`, { params });
  },
};

// ============================================================================
// 导入任务API
// ============================================================================

export const importTaskApi = {
  /** 创建导入任务 */
  create: async (
    taskName: string,
    examId: number,
    file: File,
    autoProcess: boolean = true
  ): Promise<ImportTask> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('task_name', taskName);
    formData.append('exam_id', examId.toString());
    formData.append('auto_process', autoProcess.toString());

    // 不需要手动设置 Content-Type，拦截器会自动处理 FormData
    return apiClient.post('/import-tasks/', formData);
  },

  /** 获取任务详情 */
  get: async (id: number): Promise<ImportTask> => {
    return apiClient.get(`/import-tasks/${id}`);
  },

  /** 获取任务列表 */
  list: async (params?: PaginationParams & {
    exam_id?: number;
    status?: string;
  }): Promise<ImportTask[]> => {
    return apiClient.get('/import-tasks/', { params });
  },

  /** 取消任务 */
  cancel: async (id: number): Promise<{ message: string; task_id: number }> => {
    return apiClient.post(`/import-tasks/${id}/cancel`);
  },

  /** 重试失败任务 */
  retry: async (id: number): Promise<ImportTask> => {
    return apiClient.post(`/import-tasks/${id}/retry`);
  },

  /** 删除任务 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/import-tasks/${id}`);
  },

  /** 获取错误详情 */
  getErrors: async (id: number): Promise<{
    task_id: number;
    error_message: string;
    errors: Array<{
      row: number;
      exam_number: string;
      error: string;
    }>;
  }> => {
    return apiClient.get(`/import-tasks/${id}/errors`);
  },
};

// ============================================================================
// 增值评价API
// ============================================================================

export const evaluationApi = {
  /** 创建评价 */
  create: async (data: ValueAddedEvaluationCreate): Promise<ValueAddedEvaluation> => {
    return apiClient.post('/evaluations/', data);
  },

  /** 批量创建班级评价 */
  batchCreate: async (
    name: string,
    baselineExamId: number,
    endlineExamId: number,
    subjectId: number,
    schoolId: number,
    classroomIds?: number[]
  ): Promise<{
    message: string;
    evaluation_ids: number[];
  }> => {
    const params: any = {
      name,
      baseline_exam_id: baselineExamId,
      endline_exam_id: endlineExamId,
      subject_id: subjectId,
      school_id: schoolId,
    };

    if (classroomIds) {
      params.classroom_ids = classroomIds.join(',');
    }

    return apiClient.post('/evaluations/batch', null, { params });
  },

  /** 获取评价汇总 */
  getSummary: async (id: number): Promise<ValueAddedEvaluationSummary> => {
    return apiClient.get(`/evaluations/${id}`);
  },

  /** 获取评价列表 */
  list: async (params?: PaginationParams & {
    scope_type?: string;
    subject_id?: number;
    baseline_exam_id?: number;
    endline_exam_id?: number;
  }): Promise<ValueAddedEvaluation[]> => {
    return apiClient.get('/evaluations/', { params });
  },

  /** 计算率指标 */
  calculateMetrics: async (
    examId: number,
    subjectId: number,
    scopeType: string,
    scopeId?: number
  ): Promise<{
    total_count: number;
    valid_count: number;
    excellent_count: number;
    excellent_rate: number;
    good_count: number;
    good_rate: number;
    pass_count: number;
    pass_rate: number;
    low_count: number;
    low_rate: number;
    average_score: number;
  }> => {
    const params: any = {
      exam_id: examId,
      subject_id: subjectId,
      scope_type: scopeType,
    };

    if (scopeId !== undefined) {
      params.scope_id = scopeId;
    }

    return apiClient.get('/evaluations/metrics/calculate', { params });
  },

  /** 删除评价 */
  delete: async (id: number): Promise<void> => {
    return apiClient.delete(`/evaluations/${id}`);
  },
};

// ============================================================================
// 质量监测报告 API
// ============================================================================

export const monitoringReportApi = {
  /** 导入 Excel */
  import: async (
    file: File,
    data: {
      report_type: 'primary' | 'junior_high';
      name: string;
      academic_year: string;
      semester_type: 'up' | 'down';
      region_id?: number;
    }
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('report_type', data.report_type);
    formData.append('name', data.name);
    formData.append('academic_year', data.academic_year);
    formData.append('semester_type', data.semester_type);
    if (data.region_id != null) {
      formData.append('region_id', String(data.region_id));
    }
    return apiClient.post('/monitoring-reports/import', formData);
  },

  /** 列表 */
  list: async (params?: {
    academic_year?: string;
    semester_type?: string;
    report_type?: string;
    skip?: number;
    limit?: number;
  }) => {
    return apiClient.get('/monitoring-reports/', { params });
  },

  /** 详情 */
  get: async (id: number) => {
    return apiClient.get(`/monitoring-reports/${id}`);
  },

  /** 删除 */
  delete: async (id: number) => {
    return apiClient.delete(`/monitoring-reports/${id}`);
  },
};

// ============================================================================
// 导出所有API
// ============================================================================

export const evaluationService = {
  semester: semesterApi,
  exam: examApi,
  score: scoreApi,
  dailyPerformance: dailyPerformanceApi,
  totalScore: totalScoreApi,
  importTask: importTaskApi,
  evaluation: evaluationApi,
  monitoringReport: monitoringReportApi,
};

export default evaluationService;
