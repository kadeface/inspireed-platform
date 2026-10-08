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

export interface CourseDesignSourceNote {
  source_id: string
  use: string
}

export interface CourseDesignQualityEvidence {
  draft_evidence: string
  artifact_evidence: string
}

export interface CourseDesignQualityCheck {
  id:
    | 'draft_match'
    | 'timeline_40_minutes'
    | 'artifact_completeness'
    | 'misconception_coverage'
    | 'evidence_alignment'
    | 'source_traceability'
    | 'scope_boundary'
  status: 'pass' | 'fail'
  message: string
}

export interface CourseDesignDraft {
  core_understanding: string
  inquiry_sequence: Array<{ task: string; purpose: string; expected_evidence: string }>
  key_misconceptions: CourseDesignMisconception[]
  assessment_evidence: string[]
  time_budget: Array<{ minutes: number; activity: string }>
  wiki_alignment: Array<{ source_id: string; use: string }>
}

export type ParseCourseDesignDraftResult =
  | { ok: true; draft: CourseDesignDraft }
  | { ok: false; raw: string }

export interface CourseDesignPackage {
  core_understanding: string
  draft_fingerprint?: string
  source_notes?: CourseDesignSourceNote[]
  quality_evidence?: CourseDesignQualityEvidence
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

const DRAFT_SKILL_MANUAL = `你是中国中小学「课程设计 Skill」草案生成器。

只输出课程草案 JSON（可包在 \`\`\`json 围栏中），字段必须包含：
core_understanding,
inquiry_sequence[{task,purpose,expected_evidence}],
key_misconceptions[{symptom,cause,teacher_probe}],
assessment_evidence[],
time_budget[{minutes,activity}]（分钟合计必须为输入课时）,
wiki_alignment[{source_id,use}]（只引用教学上下文中存在的 source_id）

不要生成四件套；使用简体中文。`

const PACKAGE_SKILL_MANUAL = `你是中国中小学「课程设计 Skill」四件套生成器。

基于已确认的课程草案与同一 Wiki 教学上下文，只输出四件套 JSON（可包在 \`\`\`json 围栏中），字段必须包含：
core_understanding,
draft_fingerprint（与输入一致）,
source_notes[{source_id,use}],
quality_evidence{draft_evidence,artifact_evidence},
teacher_lesson_plan{objectives,timeline,misconceptions[{symptom,cause,teacher_probe}],formative_check,body_markdown},
student_worksheet{body_markdown},
scaffold_cards{below,at,above},
observation_rubric{items[{evidence,looks_like}]}

四件套必须对齐草案核心理解、任务链与评价证据；使用简体中文。`

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

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

export function buildCourseDesignDraftQuestion(input: CourseDesignInput): string {
  const notes = input.student_notes?.trim()
  let q = `请生成课程草案：${input.grade}${input.subject}《${input.topic_title}》，${input.duration_minutes}分钟。`
  if (notes) q += `学情：${notes}`
  if (q.length > 400) q = q.slice(0, 400)
  return q
}

export function buildCourseDesignPackageQuestion(draftFingerprint: string): string {
  let q = `请基于已确认草案生成四件套，草案指纹：${draftFingerprint}。`
  if (q.length > 400) q = q.slice(0, 400)
  return q
}

export function buildCourseDesignDraftManual(patches: CourseDesignSkillPatch[]): string {
  return buildSkillManualWithPatches(DRAFT_SKILL_MANUAL, patches)
}

export function buildCourseDesignPackageManual(
  draft: CourseDesignDraft,
  draftFingerprint: string,
  patches: CourseDesignSkillPatch[]
): string {
  const base = buildSkillManualWithPatches(PACKAGE_SKILL_MANUAL, patches)
  return `${base}\n\n已确认草案（指纹 ${draftFingerprint}）：\n${JSON.stringify(draft)}`
}

function buildSkillManualWithPatches(base: string, patches: CourseDesignSkillPatch[]): string {
  if (!patches.length) return base
  const rules = patches
    .map((p, i) => `${i + 1}. ${p.text}${p.lesson_title ? `（课题：${p.lesson_title}）` : ''}`)
    .join('\n')
  return `${base}\n\n教师个人规则（必须遵守，优先于默认示例）：\n${rules}`
}

function stableHash(input: string): string {
  let hash = 2166136261
  for (let i = 0; i < input.length; i++) {
    hash ^= input.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return (hash >>> 0).toString(16).padStart(8, '0')
}

export function createCourseDesignDraftFingerprint(
  draft: CourseDesignDraft,
  snapshotIdentity: string,
  studentNotes: string,
  patches: CourseDesignSkillPatch[]
): string {
  const payload = JSON.stringify({
    draft,
    snapshotIdentity,
    studentNotes,
    patches: patches.map((p) => ({ id: p.id, text: p.text })),
  })
  return stableHash(payload)
}

function isDraft(value: unknown): value is CourseDesignDraft {
  if (!value || typeof value !== 'object') return false
  const v = value as Record<string, unknown>
  if (typeof v.core_understanding !== 'string') return false
  if (!Array.isArray(v.inquiry_sequence) || v.inquiry_sequence.length === 0) return false
  if (!Array.isArray(v.key_misconceptions)) return false
  if (!isStringArray(v.assessment_evidence) || v.assessment_evidence.length === 0) return false
  if (!Array.isArray(v.time_budget) || v.time_budget.length === 0) return false
  if (!Array.isArray(v.wiki_alignment)) return false
  return true
}

export function parseCourseDesignDraft(answer: string): ParseCourseDesignDraftResult {
  try {
    const parsed = extractJsonObject(answer)
    if (!isDraft(parsed)) return { ok: false, raw: answer }
    return { ok: true, draft: parsed }
  } catch {
    return { ok: false, raw: answer }
  }
}

export const COURSE_DESIGN_WIKI_SUGGESTION_STORAGE_KEY = 'teacher_wiki_suggestions_course_design'
export const COURSE_DESIGN_MAX_WIKI_SUGGESTIONS = 20
export const COURSE_DESIGN_MAX_WIKI_SUGGESTION_CHARS = 16000

export interface CourseFeedbackInput {
  observed_evidence: string
  student_difficulties: string
  effective_scaffolds: string
  teacher_reflection?: string
}

export interface WikiUpdateSuggestion {
  id: string
  created_at: string
  status: 'pending_review'
  snapshot_id: string
  snapshot_version: string
  lesson_title: string
  evidence_summary: string
  suggested_change: string
  quality_check_summary: string
}

function readWikiSuggestionStorage(): WikiUpdateSuggestion[] {
  try {
    const raw = localStorage.getItem(COURSE_DESIGN_WIKI_SUGGESTION_STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function writeWikiSuggestionStorage(suggestions: WikiUpdateSuggestion[]): void {
  localStorage.setItem(COURSE_DESIGN_WIKI_SUGGESTION_STORAGE_KEY, JSON.stringify(suggestions))
}

function trimWikiSuggestions(suggestions: WikiUpdateSuggestion[]): WikiUpdateSuggestion[] {
  let next = suggestions.slice(-COURSE_DESIGN_MAX_WIKI_SUGGESTIONS)
  let total = next.reduce((sum, item) => sum + item.suggested_change.length + item.evidence_summary.length, 0)
  while (total > COURSE_DESIGN_MAX_WIKI_SUGGESTION_CHARS && next.length > 1) {
    const removed = next.shift()
    total -= (removed?.suggested_change.length ?? 0) + (removed?.evidence_summary.length ?? 0)
  }
  return next
}

export function validateCourseFeedback(input: CourseFeedbackInput): { ok: true } | { ok: false } {
  if (!input.observed_evidence.trim() || !input.student_difficulties.trim()) {
    return { ok: false }
  }
  return { ok: true }
}

export function loadWikiUpdateSuggestions(): WikiUpdateSuggestion[] {
  return readWikiSuggestionStorage()
}

export function removeWikiUpdateSuggestion(id: string): WikiUpdateSuggestion[] {
  const next = readWikiSuggestionStorage().filter((item) => item.id !== id)
  writeWikiSuggestionStorage(next)
  return next
}

export function addWikiUpdateSuggestion(
  feedback: CourseFeedbackInput,
  snapshot: { snapshot_id: string; version: string; title: string },
  qualityChecks: CourseDesignQualityCheck[]
): WikiUpdateSuggestion[] {
  const qualitySummary = qualityChecks.map((item) => `${item.id}:${item.status}`).join('; ')
  const suggestion: WikiUpdateSuggestion = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    created_at: new Date().toISOString(),
    status: 'pending_review',
    snapshot_id: snapshot.snapshot_id,
    snapshot_version: snapshot.version,
    lesson_title: snapshot.title,
    evidence_summary: feedback.observed_evidence.trim(),
    suggested_change: [
      `观察到的困难：${feedback.student_difficulties.trim()}`,
      `支架效果：${feedback.effective_scaffolds.trim()}`,
      feedback.teacher_reflection?.trim() ? `教师反思：${feedback.teacher_reflection.trim()}` : '',
      '建议 Wiki 核查或补充相关原子页与课包 query。',
    ]
      .filter(Boolean)
      .join('\n'),
    quality_check_summary: qualitySummary,
  }
  const next = trimWikiSuggestions([...readWikiSuggestionStorage(), suggestion])
  writeWikiSuggestionStorage(next)
  return next
}

export function runCourseDesignQualityChecks(
  pkg: CourseDesignPackage,
  draft: CourseDesignDraft,
  fingerprint: string,
  snapshot: { duration_minutes: number; sources: Array<{ id: string }>; assessment_evidence?: string[] }
): CourseDesignQualityCheck[] {
  const checks: CourseDesignQualityCheck[] = []
  const structuredText = JSON.stringify(pkg)

  checks.push({
    id: 'draft_match',
    status: pkg.draft_fingerprint === fingerprint ? 'pass' : 'fail',
    message:
      pkg.draft_fingerprint === fingerprint
        ? '四件套草案指纹与当前确认一致'
        : '四件套草案指纹不匹配',
  })

  const timelineTotal = (pkg.teacher_lesson_plan.timeline ?? []).reduce(
    (sum, item) => sum + (Number(item.minutes) || 0),
    0
  )
  checks.push({
    id: 'timeline_40_minutes',
    status:
      timelineTotal === snapshot.duration_minutes &&
      (pkg.teacher_lesson_plan.timeline ?? []).every((item) => item.minutes > 0)
        ? 'pass'
        : 'fail',
    message: `教案时间合计 ${timelineTotal} 分钟`,
  })

  const complete =
    !!pkg.core_understanding &&
    !!pkg.student_worksheet.body_markdown?.trim() &&
    !!pkg.scaffold_cards.below?.trim() &&
    !!pkg.scaffold_cards.at?.trim() &&
    !!pkg.scaffold_cards.above?.trim() &&
    (pkg.observation_rubric.items ?? []).length > 0 &&
    (pkg.teacher_lesson_plan.objectives ?? []).length > 0
  checks.push({
    id: 'artifact_completeness',
    status: complete ? 'pass' : 'fail',
    message: complete ? '四件套必填字段完整' : '四件套存在空字段',
  })

  const miscText = JSON.stringify(pkg.teacher_lesson_plan.misconceptions ?? [])
  const hasRemainderZero =
    miscText.includes('余数为0') ||
    miscText.includes('余数為0') ||
    miscText.includes('余数 0')
  const hasPeriodMisconception =
    miscText.includes('周期') || miscText.includes('重复')
  checks.push({
    id: 'misconception_coverage',
    status: hasRemainderZero && hasPeriodMisconception ? 'pass' : 'fail',
    message: '需覆盖余数为0与周期识别相关误解',
  })

  const rubricText = JSON.stringify(pkg.observation_rubric.items ?? [])
  const evidenceAligned =
    rubricText.length > 0 &&
    !!pkg.quality_evidence?.draft_evidence?.trim() &&
    !!pkg.quality_evidence?.artifact_evidence?.trim()
  checks.push({
    id: 'evidence_alignment',
    status: evidenceAligned ? 'pass' : 'fail',
    message: evidenceAligned ? '观察表与质量证据对齐' : '观察表或质量证据不足',
  })

  const sourceIds = new Set(snapshot.sources.map((item) => item.id))
  const notes = pkg.source_notes ?? []
  const traceable =
    notes.length > 0 && notes.every((note) => sourceIds.has(note.source_id))
  checks.push({
    id: 'source_traceability',
    status: traceable ? 'pass' : 'fail',
    message: traceable ? '来源映射有效' : '来源映射缺失或引用不存在',
  })

  const outOfScope = /机器人|编程|同余/.test(structuredText)
  checks.push({
    id: 'scope_boundary',
    status: outOfScope ? 'fail' : 'pass',
    message: outOfScope ? '结构化结果出现越界关键词' : '未声明机器人/编程/同余为课堂内容',
  })

  return checks
}

function isPackage(value: unknown): value is CourseDesignPackage {
  if (!value || typeof value !== 'object') return false
  const v = value as Record<string, unknown>
  if (typeof v.core_understanding !== 'string') return false

  const plan = v.teacher_lesson_plan
  if (!plan || typeof plan !== 'object') return false
  const p = plan as Record<string, unknown>
  if (!isStringArray(p.objectives)) return false
  if (!Array.isArray(p.timeline)) return false
  if (!Array.isArray(p.misconceptions)) return false
  if (typeof p.formative_check !== 'string') return false
  if (typeof p.body_markdown !== 'string') return false

  const worksheet = v.student_worksheet
  if (!worksheet || typeof worksheet !== 'object') return false
  if (typeof (worksheet as Record<string, unknown>).body_markdown !== 'string') return false

  const cards = v.scaffold_cards
  if (!cards || typeof cards !== 'object') return false
  const c = cards as Record<string, unknown>
  if (typeof c.below !== 'string' || typeof c.at !== 'string' || typeof c.above !== 'string') {
    return false
  }

  const rubric = v.observation_rubric
  if (!rubric || typeof rubric !== 'object') return false
  if (!Array.isArray((rubric as Record<string, unknown>).items)) return false

  if (v.draft_fingerprint !== undefined && typeof v.draft_fingerprint !== 'string') return false
  if (v.source_notes !== undefined && !Array.isArray(v.source_notes)) return false
  if (v.quality_evidence !== undefined) {
    const qe = v.quality_evidence as Record<string, unknown>
    if (typeof qe.draft_evidence !== 'string' || typeof qe.artifact_evidence !== 'string') {
      return false
    }
  }

  return true
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
    const timeline = (plan.timeline ?? [])
      .map((t) => `- ${t.minutes}分钟：${t.activity}`)
      .join('\n')
    const misc = (plan.misconceptions ?? [])
      .map(
        (m) =>
          `| ${m.symptom} | ${m.cause} | ${m.teacher_probe} |`
      )
      .join('\n')
    return [
      `## 核心理解\n${pkg.core_understanding}`,
      `## 目标\n${(plan.objectives ?? []).map((o) => `- ${o}`).join('\n')}`,
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
  const items = (pkg.observation_rubric.items ?? [])
    .map((i) => `- **证据**：${i.evidence}\n  - 看起来像：${i.looks_like}`)
    .join('\n')
  return `## 课堂观察（对齐：${pkg.core_understanding}）\n${items}`
}
