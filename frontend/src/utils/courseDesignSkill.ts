export const COURSE_DESIGN_PATCH_STORAGE_KEY = 'teacher_skill_patches_course_design'
export const COURSE_DESIGN_MAX_PATCHES = 20
export const COURSE_DESIGN_MAX_PATCH_CHARS = 8000

export type CourseDesignTabId =
  | 'teacher_lesson_plan'
  | 'student_worksheet'
  | 'scaffold_cards'
  | 'observation_rubric'

export interface CourseDesignInput {
  grade: string
  subject: string
  topic_title: string
  duration_minutes: number
  student_notes?: string
}

export interface CourseDesignSkillPatch {
  id: string
  text: string
  created_at: string
  lesson_title?: string
}

export interface CourseDesignMisconception {
  symptom: string
  cause: string
  teacher_probe: string
}

export interface CourseDesignPackage {
  core_understanding: string
  teacher_lesson_plan: {
    objectives: string[]
    timeline: Array<{ minutes: number; activity: string }>
    misconceptions: CourseDesignMisconception[]
    formative_check: string
    body_markdown: string
  }
  student_worksheet: { body_markdown: string }
  scaffold_cards: { below: string; at: string; above: string }
  observation_rubric: {
    items: Array<{ evidence: string; looks_like: string }>
  }
}

export type ParseCourseDesignResult =
  | { ok: true; package: CourseDesignPackage }
  | { ok: false; raw: string }

const BASE_SKILL_MANUAL = `你是中国中小学「课程设计 Skill」执行器，不是临时聊天助手。

工作步骤：
1. 阅读年级、学科、课题、课时与学情。
2. 用一句话写出本节课「核心理解」（不是知识点清单）。
3. 预判 2–4 个具体易错：表现、原因、教师追问。
4. 围绕同一核心理解与同一套易错，同步生成四件套。
5. 自检：目标是否可一句话陈述；易错是否可观察；提示是否不直接给最终答案；观察表是否对齐同一证据。

四类判断力（必须体现在输出中）：
- 内容判断：真正要教会什么
- 学习判断：学生会在哪里卡住
- 支架判断：先问什么、再提示什么
- 评价判断：看到什么证据才算理解

一致性规则：教师教案、学生学习单、分层提示卡、课堂观察表必须共享同一核心理解与同一套易错；禁止各写各的空话；观察表禁止只写「是否认真听讲」。

学科备注：按输入学科调整术语；默认 45 分钟中国课堂节奏；使用简体中文。

输出要求：只输出一个 JSON 对象（可包在 \`\`\`json 围栏中），字段必须包含：
core_understanding,
teacher_lesson_plan{objectives,timeline,misconceptions[{symptom,cause,teacher_probe}],formative_check,body_markdown},
student_worksheet{body_markdown},
scaffold_cards{below,at,above},
observation_rubric{items[{evidence,looks_like}]}
`

function readStorage(): CourseDesignSkillPatch[] {
  try {
    const raw = localStorage.getItem(COURSE_DESIGN_PATCH_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed.filter(
      (p) => p && typeof p.id === 'string' && typeof p.text === 'string'
    )
  } catch {
    return []
  }
}

function writeStorage(patches: CourseDesignSkillPatch[]): void {
  localStorage.setItem(COURSE_DESIGN_PATCH_STORAGE_KEY, JSON.stringify(patches))
}

function trimPatches(patches: CourseDesignSkillPatch[]): CourseDesignSkillPatch[] {
  let next = patches.slice(-COURSE_DESIGN_MAX_PATCHES)
  let total = next.reduce((sum, p) => sum + p.text.length, 0)
  while (total > COURSE_DESIGN_MAX_PATCH_CHARS && next.length > 1) {
    const removed = next.shift()
    total -= removed?.text.length ?? 0
  }
  return next
}

export function loadCourseDesignPatches(): CourseDesignSkillPatch[] {
  return readStorage()
}

export function addCourseDesignPatch(
  text: string,
  lessonTitle?: string
): CourseDesignSkillPatch[] {
  const trimmed = text.trim()
  if (!trimmed) return readStorage()
  const patch: CourseDesignSkillPatch = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    text: trimmed,
    created_at: new Date().toISOString(),
    ...(lessonTitle?.trim() ? { lesson_title: lessonTitle.trim() } : {}),
  }
  const next = trimPatches([...readStorage(), patch])
  writeStorage(next)
  return next
}

export function removeCourseDesignPatch(id: string): CourseDesignSkillPatch[] {
  const next = readStorage().filter((p) => p.id !== id)
  writeStorage(next)
  return next
}

export function clearCourseDesignPatches(): CourseDesignSkillPatch[] {
  writeStorage([])
  return []
}

export function buildCourseDesignSkillManual(
  patches: CourseDesignSkillPatch[]
): string {
  if (!patches.length) return BASE_SKILL_MANUAL
  const rules = patches
    .map((p, i) => `${i + 1}. ${p.text}${p.lesson_title ? `（课题：${p.lesson_title}）` : ''}`)
    .join('\n')
  return `${BASE_SKILL_MANUAL}\n\n教师个人规则（必须遵守，优先于默认示例）：\n${rules}`
}

export function buildCourseDesignQuestion(input: CourseDesignInput): string {
  const notes = input.student_notes?.trim()
  let q = `请按课程设计Skill生成四件套：${input.grade}${input.subject}《${input.topic_title}》，${input.duration_minutes}分钟。`
  if (notes) q += `学情：${notes}`
  if (q.length > 400) q = q.slice(0, 400)
  return q
}

function extractJsonObject(answer: string): unknown {
  const fenced = answer.match(/```(?:json)?\s*([\s\S]*?)```/i)
  const candidate = (fenced?.[1] ?? answer).trim()
  return JSON.parse(candidate)
}

function isPackage(value: unknown): value is CourseDesignPackage {
  if (!value || typeof value !== 'object') return false
  const v = value as Record<string, unknown>
  return (
    typeof v.core_understanding === 'string' &&
    typeof v.teacher_lesson_plan === 'object' &&
    v.teacher_lesson_plan !== null &&
    typeof v.student_worksheet === 'object' &&
    v.student_worksheet !== null &&
    typeof v.scaffold_cards === 'object' &&
    v.scaffold_cards !== null &&
    typeof v.observation_rubric === 'object' &&
    v.observation_rubric !== null
  )
}

export function parseCourseDesignPackage(answer: string): ParseCourseDesignResult {
  try {
    const parsed = extractJsonObject(answer)
    if (!isPackage(parsed)) return { ok: false, raw: answer }
    return { ok: true, package: parsed }
  } catch {
    return { ok: false, raw: answer }
  }
}

export function formatCourseDesignTabMarkdown(
  pkg: CourseDesignPackage,
  tab: CourseDesignTabId
): string {
  if (tab === 'teacher_lesson_plan') {
    const plan = pkg.teacher_lesson_plan
    const timeline = plan.timeline
      .map((t) => `- ${t.minutes}分钟：${t.activity}`)
      .join('\n')
    const misc = plan.misconceptions
      .map(
        (m) =>
          `| ${m.symptom} | ${m.cause} | ${m.teacher_probe} |`
      )
      .join('\n')
    return [
      `## 核心理解\n${pkg.core_understanding}`,
      `## 目标\n${plan.objectives.map((o) => `- ${o}`).join('\n')}`,
      `## 流程\n${timeline}`,
      `## 易错×原因×追问\n| 表现 | 原因 | 追问 |\n|---|---|---|\n${misc}`,
      `## 当堂检测\n${plan.formative_check}`,
      plan.body_markdown,
    ].join('\n\n')
  }
  if (tab === 'student_worksheet') {
    return pkg.student_worksheet.body_markdown?.trim() || '_（空）_'
  }
  if (tab === 'scaffold_cards') {
    return [
      `## 低于当前水平\n${pkg.scaffold_cards.below}`,
      `## 达到当前水平\n${pkg.scaffold_cards.at}`,
      `## 高于当前水平\n${pkg.scaffold_cards.above}`,
    ].join('\n\n')
  }
  const items = pkg.observation_rubric.items
    .map((i) => `- **证据**：${i.evidence}\n  - 看起来像：${i.looks_like}`)
    .join('\n')
  return `## 课堂观察（对齐：${pkg.core_understanding}）\n${items}`
}
