/**
 * 教学活动（Activity）类型定义
 * 统一管理：测验、问卷、作业、评价量表
 */

// ========== 活动类型 ==========
export type ActivityType = 'quiz' | 'survey' | 'assignment' | 'rubric' | 'mixed'

// ========== 课程阶段 ==========
export type CoursePhase = 'pre-class' | 'in-class' | 'post-class'

// ========== 提交状态 ==========
export type ActivitySubmissionStatus = 'draft' | 'submitted' | 'graded' | 'returned'

// ========== 互评状态 ==========
export type PeerReviewStatus = 'pending' | 'in_progress' | 'completed'

// ========== 活动项类型 ==========
export type ActivityItemType =
  | 'single-choice'      // 单选题
  | 'multiple-choice'    // 多选题
  | 'true-false'         // 判断题
  | 'short-answer'       // 简答题
  | 'long-answer'        // 论述题
  | 'file-upload'        // 文件上传
  | 'code-submission'    // 代码提交
  | 'scale'              // 量表评分（1-5分）
  | 'rubric-item'        // 评价标准项

// ========== 反馈显示时机 ==========
export type FeedbackTiming = 'immediate' | 'after_deadline' | 'manual'

// ========== 结果可见性 ==========
export type ResultVisibility = 'teacher_only' | 'all_students' | 'after_submission'

// ========== 活动时间配置 ==========
export interface ActivityTiming {
  phase: CoursePhase
  startTime?: string  // ISO 8601 格式
  deadline?: string
  duration?: number  // 时长限制（分钟）
  allowLateSubmission?: boolean
  lateSubmissionPenalty?: number  // 迟交扣分比例 (0-1)
}

// ========== 评分配置 ==========
export interface ActivityGrading {
  enabled: boolean
  totalPoints: number
  passingScore?: number
  autoGrade?: boolean
  rubric?: RubricConfig
  showScoreToStudent?: boolean
}

// ========== 提交配置 ==========
export interface ActivitySubmissionConfig {
  allowMultiple?: boolean  // 允许多次提交
  showFeedback?: FeedbackTiming
  anonymous?: boolean  // 匿名提交（问卷）
  requireAttachment?: boolean
  allowedFileTypes?: string[]
  maxFileSize?: number  // MB
}

// ========== 显示配置 ==========
export interface ActivityDisplay {
  shuffle?: boolean  // 随机打乱题目顺序
  showProgress?: boolean
  showResults?: boolean  // 显示统计结果
  resultVisibility?: ResultVisibility
}

// ========== 评分标准（Rubric）配置 ==========
export interface RubricConfig {
  type: 'holistic' | 'analytic'  // 整体式/分析式
  allowSelfEvaluation?: boolean
  allowPeerEvaluation?: boolean
}

// ========== 活动项基础接口 ==========
export interface ActivityItemBase {
  id: string
  order: number
  type: ActivityItemType
  question: string  // 问题/任务描述
  required: boolean
  points?: number  // 该题分值
}

// ========== 选择题选项 ==========
export interface ChoiceOption {
  id: string
  text: string
  isCorrect?: boolean  // 问卷中可选，测验中必填
}

// ========== 单选题 ==========
export interface SingleChoiceItem extends ActivityItemBase {
  type: 'single-choice'
  config: {
    options: ChoiceOption[]
    correctAnswer?: string  // 正确答案ID
    explanation?: string  // 答案解析
  }
}

// ========== 多选题 ==========
export interface MultipleChoiceItem extends ActivityItemBase {
  type: 'multiple-choice'
  config: {
    options: ChoiceOption[]
    correctAnswers?: string[]  // 正确答案ID列表
    explanation?: string
  }
}

// ========== 判断题 ==========
export interface TrueFalseItem extends ActivityItemBase {
  type: 'true-false'
  config: {
    correctAnswer?: boolean
    explanation?: string
  }
}

// ========== 简答题 ==========
export interface ShortAnswerItem extends ActivityItemBase {
  type: 'short-answer'
  config: {
    minLength?: number
    maxLength?: number
    placeholder?: string
    validation?: 'none' | 'email' | 'url' | 'number'
  }
}

// ========== 论述题 ==========
export interface LongAnswerItem extends ActivityItemBase {
  type: 'long-answer'
  config: {
    minLength?: number
    maxLength?: number
    placeholder?: string
  }
}

// ========== 文件上传 ==========
export interface FileUploadItem extends ActivityItemBase {
  type: 'file-upload'
  config: {
    acceptedTypes: string[]  // ['pdf', 'docx', 'zip']
    maxSize: number  // MB
    multiple: boolean
  }
}

// ========== 代码提交 ==========
export interface CodeTestCase {
  input: string
  expectedOutput: string
}

export interface CodeSubmissionItem extends ActivityItemBase {
  type: 'code-submission'
  config: {
    language: 'python' | 'javascript' | 'java' | 'cpp'
    template?: string  // 代码模板
    testCases?: CodeTestCase[]
    autoTest?: boolean  // 自动测试
  }
}

// ========== 量表评分 ==========
export interface ScaleItem extends ActivityItemBase {
  type: 'scale'
  config: {
    min: number  // 例如：1
    max: number  // 例如：5
    minLabel?: string  // "非常不同意"
    maxLabel?: string  // "非常同意"
    step?: number  // 步长
  }
}

// ========== 评价标准项 ==========
export interface RubricLevel {
  level: number
  name: string  // 优秀、良好、及格、不及格
  description: string
  points: number
}

export interface RubricItem extends ActivityItemBase {
  type: 'rubric-item'
  config: {
    criterion: string  // 评价维度名称
    weight?: number  // 权重百分比
    levels: RubricLevel[]
  }
}

// ========== 活动项联合类型 ==========
export type ActivityItem =
  | SingleChoiceItem
  | MultipleChoiceItem
  | TrueFalseItem
  | ShortAnswerItem
  | LongAnswerItem
  | FileUploadItem
  | CodeSubmissionItem
  | ScaleItem
  | RubricItem

// ========== Activity Cell 内容结构 ==========
export interface ActivityCellContent {
  title: string
  description?: string
  activityType: ActivityType
  timing: ActivityTiming
  items: ActivityItem[]
  grading: ActivityGrading
  submission: ActivitySubmissionConfig
  display: ActivityDisplay
}

// ========== 学生答案格式 ==========
export interface SingleChoiceAnswer {
  answer: string  // 选项ID
  correct?: boolean
  score?: number
}

export interface MultipleChoiceAnswer {
  answer: string[]  // 选项ID列表
  correct?: boolean
  score?: number
}

export interface TextAnswer {
  text: string
  score?: number
}

export interface FileAnswer {
  files: string[]  // 文件URL列表
  score?: number
}

export interface CodeAnswer {
  code: string
  testResults?: Array<{
    input: string
    expectedOutput: string
    actualOutput: string
    passed: boolean
  }>
  score?: number
}

export interface ScaleAnswer {
  value: number
  score?: number
}

export interface RubricAnswer {
  level: number
  score: number
  comment?: string
}

export type ItemAnswer =
  | SingleChoiceAnswer
  | MultipleChoiceAnswer
  | TextAnswer
  | FileAnswer
  | CodeAnswer
  | ScaleAnswer
  | RubricAnswer

// ========== 活动提交数据 ==========
export interface ActivitySubmission {
  id: number
  cellId: number
  lessonId: number
  studentId: number
  responses: Record<string, ItemAnswer>  // key: item_id, value: 答案
  score?: number
  maxScore?: number
  autoGraded: boolean
  status: ActivitySubmissionStatus
  teacherFeedback?: string
  gradedBy?: number
  startedAt?: string
  submittedAt?: string
  gradedAt?: string
  submissionCount: number
  timeSpent?: number  // 秒
  isLate: boolean
  version: number
  synced: boolean
  createdAt: string
  updatedAt: string
}

// ========== 互评数据 ==========
export interface PeerReview {
  id: number
  submissionId: number
  reviewerId: number
  lessonId: number
  cellId: number
  reviewData: Record<string, any>
  score?: number
  maxScore?: number
  comment?: string
  status: PeerReviewStatus
  isAnonymous: boolean
  assignedAt: string
  completedAt?: string
  createdAt: string
  updatedAt: string
}

// ========== 活动统计数据 ==========
export interface ActivityStatistics {
  id: number
  cellId: number
  lessonId: number
  totalStudents: number
  draftCount: number
  submittedCount: number
  gradedCount: number
  averageScore?: number
  highestScore?: number
  lowestScore?: number
  medianScore?: number
  averageTimeSpent?: number  // 秒
  itemStatistics?: Record<string, any>
  peerReviewCount: number
  avgPeerReviewScore?: number
  updatedAt: string
}

// ========== 创建活动提交请求 ==========
export interface CreateActivitySubmissionRequest {
  cellId: number
  lessonId: number
  responses?: Record<string, ItemAnswer>
  startedAt?: string
}

// ========== 更新活动提交请求 ==========
export interface UpdateActivitySubmissionRequest {
  responses?: Record<string, ItemAnswer>
  status?: ActivitySubmissionStatus
  timeSpent?: number
}

// ========== 提交活动请求 ==========
export interface SubmitActivityRequest {
  responses: Record<string, ItemAnswer>
  timeSpent?: number
}

// ========== 评分请求 ==========
export interface GradeActivityRequest {
  score: number
  teacherFeedback?: string
  itemScores?: Record<string, number>  // 每题的分数
}

// ========== 创建互评请求 ==========
export interface CreatePeerReviewRequest {
  submissionId: number
  reviewData: Record<string, any>
  score?: number
  comment?: string
}

// ========== 活动模板 ==========
export interface ActivityTemplate {
  id: string
  name: string
  description: string
  icon: string
  activityType: ActivityType
  template: Partial<ActivityCellContent>
}

// ========== 预设活动模板 ==========
export const ACTIVITY_TEMPLATES: ActivityTemplate[] = [
  {
    id: 'blank',
    name: '空白活动',
    description: '从零开始创建',
    icon: '📋',
    activityType: 'mixed',
    template: {
      items: [],
      timing: {
        phase: 'in-class',
      },
      grading: {
        enabled: false,
        totalPoints: 0,
      },
      submission: {},
      display: {},
    },
  },
  {
    id: 'quick-quiz',
    name: '快速测验',
    description: '课堂小测验',
    icon: '✅',
    activityType: 'quiz',
    template: {
      timing: {
        phase: 'in-class',
        duration: 15,
      },
      grading: {
        enabled: true,
        autoGrade: true,
        totalPoints: 100,
        showScoreToStudent: true,
      },
      submission: {
        allowMultiple: false,
        showFeedback: 'immediate',
      },
      display: {
        showProgress: true,
      },
    },
  },
  {
    id: 'pre-class-survey',
    name: '课前调查',
    description: '了解学生背景',
    icon: '📊',
    activityType: 'survey',
    template: {
      timing: {
        phase: 'pre-class',
      },
      grading: {
        enabled: false,
        totalPoints: 0,
      },
      submission: {
        anonymous: true,
      },
      display: {
        showResults: true,
        resultVisibility: 'all_students',
      },
    },
  },
  {
    id: 'homework',
    name: '课后作业',
    description: '巩固练习',
    icon: '📝',
    activityType: 'assignment',
    template: {
      timing: {
        phase: 'post-class',
        allowLateSubmission: true,
        lateSubmissionPenalty: 0.1,
      },
      grading: {
        enabled: true,
        totalPoints: 100,
        autoGrade: false,
      },
      submission: {
        allowMultiple: true,
        showFeedback: 'manual',
      },
    },
  },
  {
    id: 'peer-review-assignment',
    name: '互评作业',
    description: '学生互相评价',
    icon: '🤝',
    activityType: 'assignment',
    template: {
      timing: {
        phase: 'post-class',
      },
      grading: {
        enabled: true,
        totalPoints: 100,
        rubric: {
          type: 'analytic',
          allowPeerEvaluation: true,
        },
      },
      submission: {
        showFeedback: 'after_deadline',
      },
    },
  },
]

