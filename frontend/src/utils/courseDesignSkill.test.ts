import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  COURSE_DESIGN_PATCH_STORAGE_KEY,
  addCourseDesignPatch,
  buildCourseDesignQuestion,
  buildCourseDesignSkillManual,
  clearCourseDesignPatches,
  formatCourseDesignTabMarkdown,
  loadCourseDesignPatches,
  parseCourseDesignPackage,
  removeCourseDesignPatch,
} from './courseDesignSkill'

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
})
