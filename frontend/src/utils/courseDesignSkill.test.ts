import { beforeEach, describe, expect, it, vi } from 'vitest'
import { CYCLE_REMAINDER_WIKI_SNAPSHOT } from '@/data/courseDesignWikiSnapshots'
import {
  COURSE_DESIGN_PATCH_STORAGE_KEY,
  COURSE_DESIGN_WIKI_SUGGESTION_STORAGE_KEY,
  addCourseDesignPatch,
  addWikiUpdateSuggestion,
  buildCourseDesignDraftQuestion,
  buildCourseDesignPackageQuestion,
  buildCourseDesignQuestion,
  buildCourseDesignSkillManual,
  clearCourseDesignPatches,
  createCourseDesignDraftFingerprint,
  formatCourseDesignTabMarkdown,
  loadCourseDesignPatches,
  loadWikiUpdateSuggestions,
  parseCourseDesignDraft,
  parseCourseDesignPackage,
  removeCourseDesignPatch,
  removeWikiUpdateSuggestion,
  runCourseDesignQualityChecks,
  validateCourseFeedback,
  type CourseDesignDraft,
  type CourseDesignPackage,
} from './courseDesignSkill'

const validDraft: CourseDesignDraft = {
  core_understanding: '用周期和余数定位第 n 项',
  inquiry_sequence: [
    { task: '圈出重复组', purpose: '发现周期', expected_evidence: '学生能指出起点' },
  ],
  key_misconceptions: [
    { symptom: '把总数当周期', cause: '未识别重复组', teacher_probe: '一组有几个？' },
    { symptom: '余数为0选第一位', cause: '误解余数含义', teacher_probe: '余数为0表示什么？' },
  ],
  assessment_evidence: ['能解释余数为0', '能指出周期长度'],
  time_budget: [
    { minutes: 10, activity: '导入' },
    { minutes: 30, activity: '探究' },
  ],
  wiki_alignment: [{ source_id: 'wiki-cycle-structure', use: '周期结构' }],
}

const validPackage: CourseDesignPackage = {
  core_understanding: '用周期和余数定位第 n 项',
  draft_fingerprint: 'abc123',
  source_notes: [{ source_id: 'wiki-cycle-structure', use: '周期结构' }],
  quality_evidence: {
    draft_evidence: '能解释余数为0',
    artifact_evidence: '学生口头解释商与余数',
  },
  teacher_lesson_plan: {
    objectives: ['理解周期与余数'],
    timeline: [
      { minutes: 10, activity: '导入' },
      { minutes: 30, activity: '探究' },
    ],
    misconceptions: [
      { symptom: '忽略周期起点', cause: '未圈重复组', teacher_probe: '起点在哪？' },
      { symptom: '余数为0错误', cause: '误解', teacher_probe: '余数为0表示什么？' },
    ],
    formative_check: '口答',
    body_markdown: '教案正文',
  },
  student_worksheet: { body_markdown: '学习单' },
  scaffold_cards: { below: '提示1', at: '提示2', above: '提示3' },
  observation_rubric: {
    items: [{ evidence: '能说出周期', looks_like: '学生圈出重复组' }],
  },
}

const fingerprint = 'abc123'

describe('courseDesignSkill patches', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('loads empty list when storage missing', () => {
    expect(loadCourseDesignPatches()).toEqual([])
  })

  it('appends a patch and persists it', () => {
    const patches = addCourseDesignPatch('去括号漏乘要写进提示卡', '解一元一次方程')
    expect(patches).toHaveLength(1)
    expect(patches[0].text).toContain('去括号')
    expect(patches[0].lesson_title).toBe('解一元一次方程')
    expect(JSON.parse(localStorage.getItem(COURSE_DESIGN_PATCH_STORAGE_KEY)!)).toHaveLength(1)
  })

  it('removes and clears patches', () => {
    const [a] = addCourseDesignPatch('规则A')
    addCourseDesignPatch('规则B')
    expect(removeCourseDesignPatch(a.id)).toHaveLength(1)
    expect(clearCourseDesignPatches()).toEqual([])
    expect(loadCourseDesignPatches()).toEqual([])
  })
})

describe('courseDesignSkill builders', () => {
  it('builds a question under 400 chars', () => {
    const q = buildCourseDesignQuestion({
      grade: '七年级',
      subject: '数学',
      topic_title: '解一元一次方程',
      duration_minutes: 45,
      student_notes: '部分学生移项机械变号',
    })
    expect(q.length).toBeGreaterThanOrEqual(3)
    expect(q.length).toBeLessThanOrEqual(400)
    expect(q).toContain('解一元一次方程')
  })

  it('includes personal rules in the skill manual', () => {
    const manual = buildCourseDesignSkillManual([
      {
        id: '1',
        text: '观察表不要写是否认真听讲',
        created_at: '2026-07-20T00:00:00.000Z',
      },
    ])
    expect(manual).toContain('教师个人规则')
    expect(manual).toContain('观察表不要写是否认真听讲')
    expect(manual).toContain('核心理解')
  })
})

describe('courseDesignSkill parse', () => {
  it('parses fenced JSON', () => {
    const raw = `\`\`\`json
{
  "core_understanding": "移项要用等式性质解释",
  "teacher_lesson_plan": {
    "objectives": ["能用等式性质解释移项"],
    "timeline": [{"minutes": 10, "activity": "导入"}],
    "misconceptions": [
      {"symptom": "只在一边减", "cause": "未理解等式性质", "teacher_probe": "另一边发生了什么？"}
    ],
    "formative_check": "口答一步移项依据",
    "body_markdown": "## 教案\\n内容"
  },
  "student_worksheet": { "body_markdown": "## 学习单" },
  "scaffold_cards": { "below": "线索1", "at": "线索2", "above": "线索3" },
  "observation_rubric": {
    "items": [{ "evidence": "能说出两边相同运算", "looks_like": "学生口头复述" }]
  }
}
\`\`\``
    const result = parseCourseDesignPackage(raw)
    expect(result.ok).toBe(true)
    if (result.ok) {
      expect(result.package.core_understanding).toContain('等式性质')
      const md = formatCourseDesignTabMarkdown(result.package, 'teacher_lesson_plan')
      expect(md).toContain('教案')
    }
  })

  it('returns raw on invalid JSON', () => {
    const result = parseCourseDesignPackage('不是JSON')
    expect(result.ok).toBe(false)
    if (!result.ok) expect(result.raw).toBe('不是JSON')
  })

  it('rejects JSON with empty teacher_lesson_plan object', () => {
    const raw = JSON.stringify({
      core_understanding: '核心理解',
      teacher_lesson_plan: {},
      student_worksheet: { body_markdown: '学习单' },
      scaffold_cards: { below: 'a', at: 'b', above: 'c' },
      observation_rubric: { items: [] },
    })
    const result = parseCourseDesignPackage(raw)
    expect(result.ok).toBe(false)
  })
})

describe('courseDesignSkill draft', () => {
  it('parses a complete course design draft', () => {
    const result = parseCourseDesignDraft(JSON.stringify(validDraft))
    expect(result.ok).toBe(true)
  })

  it('rejects a draft whose time budget is incomplete', () => {
    const result = parseCourseDesignDraft(JSON.stringify({ ...validDraft, time_budget: [] }))
    expect(result.ok).toBe(false)
  })

  it('changes the fingerprint when generation inputs change', () => {
    const a = createCourseDesignDraftFingerprint(validDraft, 'snapshot@1.0.0', '学情A', [])
    const b = createCourseDesignDraftFingerprint(validDraft, 'snapshot@1.0.0', '学情B', [])
    expect(a).not.toBe(b)
  })

  it('builds separate draft and package questions under 400 chars', () => {
    const fixedInput = {
      grade: '三年级',
      subject: '数学',
      topic_title: '周期与余数',
      duration_minutes: 40,
    }
    expect(buildCourseDesignDraftQuestion(fixedInput).length).toBeLessThanOrEqual(400)
    expect(buildCourseDesignPackageQuestion('draft-fingerprint').length).toBeLessThanOrEqual(400)
  })
})

describe('courseDesignSkill quality checks', () => {
  it('passes all checks for an aligned 40-minute package', () => {
    const pkg = { ...validPackage, draft_fingerprint: fingerprint }
    const result = runCourseDesignQualityChecks(
      pkg,
      validDraft,
      fingerprint,
      CYCLE_REMAINDER_WIKI_SNAPSHOT,
    )
    expect(result.every((item) => item.status === 'pass')).toBe(true)
  })

  it.each([
    ['draft_match', { draft_fingerprint: 'wrong' }],
    [
      'timeline_40_minutes',
      {
        teacher_lesson_plan: {
          ...validPackage.teacher_lesson_plan,
          timeline: [{ minutes: 39, activity: '活动' }],
        },
      },
    ],
    ['source_traceability', { source_notes: [{ source_id: 'missing', use: '不存在' }] }],
  ] as const)('fails %s for invalid package', (checkId, patch) => {
    const result = runCourseDesignQualityChecks(
      { ...validPackage, draft_fingerprint: fingerprint, ...patch },
      validDraft,
      fingerprint,
      CYCLE_REMAINDER_WIKI_SNAPSHOT,
    )
    expect(result.find((item) => item.id === checkId)?.status).toBe('fail')
  })

  it('fails scope_boundary when robot content appears', () => {
    const result = runCourseDesignQualityChecks(
      {
        ...validPackage,
        draft_fingerprint: fingerprint,
        teacher_lesson_plan: {
          ...validPackage.teacher_lesson_plan,
          body_markdown: '本课使用机器人编程',
        },
      },
      validDraft,
      fingerprint,
      CYCLE_REMAINDER_WIKI_SNAPSHOT,
    )
    expect(result.find((item) => item.id === 'scope_boundary')?.status).toBe('fail')
  })
})

describe('courseDesignSkill wiki suggestions', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('requires observed evidence and student difficulties', () => {
    expect(
      validateCourseFeedback({
        observed_evidence: '',
        student_difficulties: '',
        effective_scaffolds: '',
        teacher_reflection: '',
      }).ok,
    ).toBe(false)
  })

  it('creates a pending suggestion without changing skill patches', () => {
    const before = loadCourseDesignPatches()
    addCourseDesignPatch('保留规则')
    const patchesBefore = loadCourseDesignPatches()
    const suggestions = addWikiUpdateSuggestion(
      {
        observed_evidence: '学生能圈周期',
        student_difficulties: '余数为0仍错',
        effective_scaffolds: '追问有效',
      },
      CYCLE_REMAINDER_WIKI_SNAPSHOT,
      runCourseDesignQualityChecks(
        { ...validPackage, draft_fingerprint: fingerprint },
        validDraft,
        fingerprint,
        CYCLE_REMAINDER_WIKI_SNAPSHOT,
      ),
    )
    expect(suggestions[0].status).toBe('pending_review')
    expect(suggestions[0].snapshot_version).toBe('1.0.0')
    expect(loadCourseDesignPatches()).toEqual(patchesBefore)
    expect(before).toEqual([])
    localStorage.removeItem(COURSE_DESIGN_PATCH_STORAGE_KEY)
  })

  it('removes a suggestion', () => {
    const [item] = addWikiUpdateSuggestion(
      {
        observed_evidence: '证据',
        student_difficulties: '困难',
        effective_scaffolds: '支架',
      },
      CYCLE_REMAINDER_WIKI_SNAPSHOT,
      [],
    )
    const next = removeWikiUpdateSuggestion(item.id)
    expect(next).toHaveLength(0)
    expect(JSON.parse(localStorage.getItem(COURSE_DESIGN_WIKI_SUGGESTION_STORAGE_KEY)!)).toEqual([])
  })
})
