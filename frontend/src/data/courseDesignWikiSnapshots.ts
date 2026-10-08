export interface CourseDesignWikiRetrieveRef {
  bundle_id: string
  query_id: string
  chunk_id: string
  score: number
}

export interface CourseDesignWikiSource {
  id: string
  label: string
  wiki_path: string
  summary: string
  retrieve_ref?: CourseDesignWikiRetrieveRef
}

export interface CourseDesignWikiSnapshot {
  snapshot_id: string
  version: string
  captured_at: string
  bundle_ref: string
  title: string
  grade: string
  subject: string
  duration_minutes: number
  core_ideas: string[]
  learning_progression: string[]
  misconceptions: string[]
  task_principles: string[]
  evidence_principles: string[]
  scope_boundaries: string[]
  sources: CourseDesignWikiSource[]
}

export const CYCLE_REMAINDER_WIKI_SNAPSHOT: Readonly<CourseDesignWikiSnapshot> = {
  snapshot_id: 'math-thinking-g3-cycle-remainder-v1',
  version: '1.0.0',
  captured_at: '2026-07-21',
  bundle_ref: '2026-07-21T103000Z',
  title: '周期与余数',
  grade: '三年级',
  subject: '数学',
  duration_minutes: 40,
  core_ideas: [
    '先确定重复的一组及周期起点，再用完整周期数和余数定位。',
    '余数表示落在下一周期中的位置；余数为0表示落在上一完整周期的末位。',
  ],
  learning_progression: ['发现重复', '确定周期', '用除法定位', '解释余数', '迁移到新情境'],
  misconceptions: [
    '把总项数当作周期长度',
    '忽略周期起点',
    '余数为0时错误地选第一位',
    '只套除法算式而不能解释余数',
  ],
  task_principles: ['先画或圈出重复组', '再用除法压缩枚举过程', '最后要求解释和迁移'],
  evidence_principles: ['能指出周期起点和长度', '能解释商与余数各表示什么', '能单独解释余数为0'],
  scope_boundaries: ['纯数学思维课，不引入机器人或编程活动', '不使用超出三年级理解范围的同余术语'],
  sources: [
    {
      id: 'wiki-cycle-structure',
      label: '周期结构',
      wiki_path: 'wiki/concepts/周期结构.md',
      summary: '识别重复单位、起点和周期长度。',
      retrieve_ref: {
        bundle_id: '2026-07-21T103000Z',
        query_id: 'q-core-ideas',
        chunk_id: 'chunk-002',
        score: 0.87,
      },
    },
    {
      id: 'wiki-remainder-position',
      label: '余数定位',
      wiki_path: 'wiki/concepts/余数定位.md',
      summary: '用余数表示下一周期位置，并单独处理余数为0。',
      retrieve_ref: {
        bundle_id: '2026-07-21T103000Z',
        query_id: 'q-core-ideas',
        chunk_id: 'chunk-001',
        score: 0.82,
      },
    },
    {
      id: 'wiki-evidence-progression',
      label: '学习证据',
      wiki_path: 'wiki/concepts/学习证据.md',
      summary: '从图示枚举过渡到算式解释与迁移。',
      retrieve_ref: {
        bundle_id: '2026-07-21T103000Z',
        query_id: 'q-evidence',
        chunk_id: 'chunk-003',
        score: 0.75,
      },
    },
  ],
}

export function serializeWikiSnapshotContext(snapshot: CourseDesignWikiSnapshot): string {
  return JSON.stringify(snapshot)
}
