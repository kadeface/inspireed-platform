import { readFileSync } from 'node:fs'
import { join } from 'node:path'

export interface RetrieveBundleHit {
  vault_path: string
  chunk_id: string
  score: number
  excerpt: string
  page_title: string
  page_type: string
  filtered?: boolean
}

export interface RetrieveBundleQuery {
  query_id: string
  query_text: string
  top_k: number
  hits: RetrieveBundleHit[]
}

export interface RetrieveBundleDedupedPage {
  vault_path: string
  page_title: string
  page_type: string
  hit_count: number
  best_score: number
  sections_used: string[]
}

export interface RetrieveBundleReview {
  status: 'pending' | 'approved' | 'rejected'
  reviewer: string | null
  reviewed_at: string | null
  notes: string | null
}

export interface RetrieveBundle {
  bundle_version: string
  package_id: string
  retrieved_at: string
  vault_commit?: string
  retrieve_skill_version?: string
  queries: RetrieveBundleQuery[]
  deduped_pages: RetrieveBundleDedupedPage[]
  review: RetrieveBundleReview
}

export interface PackageMeta {
  title: string
  grade: string
  subject: string
  duration_minutes: number
  scope_boundaries: string[]
}

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

export interface DraftCourseDesignWikiSnapshot {
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

export type StructureWikiSnapshotResult =
  | { ok: true; snapshot: DraftCourseDesignWikiSnapshot }
  | { ok: false; error: string }

const SECTION_FIELD_MAP: Record<string, keyof Pick<
  DraftCourseDesignWikiSnapshot,
  'core_ideas' | 'learning_progression' | 'misconceptions' | 'task_principles' | 'evidence_principles' | 'scope_boundaries'
>> = {
  核心理解: 'core_ideas',
  学习进阶: 'learning_progression',
  常见误解: 'misconceptions',
  任务原则: 'task_principles',
  课堂证据: 'evidence_principles',
  边界说明: 'scope_boundaries',
}

function sourceIdFromVaultPath(vaultPath: string): string {
  const stem = vaultPath.replace(/^wiki\//, '').replace(/\.md$/, '').replace(/\//g, '-')
  return `wiki-${stem}`
}

function parseMarkdownSections(markdown: string): Record<string, string[]> {
  const sections: Record<string, string[]> = {}
  const lines = markdown.split('\n')
  let current: string | null = null

  for (const line of lines) {
    const heading = line.match(/^##\s+(.+?)\s*$/)
    if (heading) {
      current = heading[1]!.trim()
      sections[current] = []
      continue
    }
    if (current && line.trim()) {
      sections[current]!.push(line.trim())
    }
  }

  return sections
}

function splitListItems(text: string): string[] {
  return text
    .split(/[；;。→\n]/)
    .map((part) => part.trim())
    .filter((part) => part.length > 0)
}

function appendUnique(target: string[], items: string[], limit: number): void {
  for (const item of items) {
    if (target.length >= limit) break
    if (!target.includes(item)) target.push(item)
  }
}

function findBestHit(
  bundle: RetrieveBundle,
  vaultPath: string,
): { hit: RetrieveBundleHit; query_id: string } | null {
  let best: { hit: RetrieveBundleHit; query_id: string } | null = null

  for (const query of bundle.queries) {
    for (const hit of query.hits) {
      if (hit.filtered || hit.vault_path !== vaultPath) continue
      if (!best || hit.score > best.hit.score) {
        best = { hit, query_id: query.query_id }
      }
    }
  }

  return best
}

export function structureWikiSnapshotFromBundle(
  bundle: RetrieveBundle,
  options: { bundleId: string; vaultRoot: string; packageMeta: PackageMeta },
): StructureWikiSnapshotResult {
  if (bundle.review.status !== 'approved') {
    return { ok: false, error: 'bundle review status must be approved' }
  }

  const snapshot: DraftCourseDesignWikiSnapshot = {
    snapshot_id: `${bundle.package_id}-v1`,
    version: '1.0.0',
    captured_at: bundle.retrieved_at.slice(0, 10),
    bundle_ref: options.bundleId,
    title: options.packageMeta.title,
    grade: options.packageMeta.grade,
    subject: options.packageMeta.subject,
    duration_minutes: options.packageMeta.duration_minutes,
    core_ideas: [],
    learning_progression: [],
    misconceptions: [],
    task_principles: [],
    evidence_principles: [],
    scope_boundaries: [...options.packageMeta.scope_boundaries],
    sources: [],
  }

  for (const page of bundle.deduped_pages) {
    const filePath = join(options.vaultRoot, page.vault_path)
    let markdown = ''
    try {
      markdown = readFileSync(filePath, 'utf8')
    } catch {
      return { ok: false, error: `missing vault page: ${page.vault_path}` }
    }

    const sections = parseMarkdownSections(markdown)
    for (const [sectionTitle, field] of Object.entries(SECTION_FIELD_MAP)) {
      const body = (sections[sectionTitle] ?? []).join(' ')
      if (!body) continue
      const limit = field === 'core_ideas' ? 5 : field === 'misconceptions' ? 6 : 8
      appendUnique(snapshot[field], splitListItems(body), limit)
    }

    const bestHit = findBestHit(bundle, page.vault_path)
    const summarySource =
      (sections['核心理解'] ?? []).join(' ') || bestHit?.hit.excerpt || page.page_title

    snapshot.sources.push({
      id: sourceIdFromVaultPath(page.vault_path),
      label: page.page_title,
      wiki_path: page.vault_path,
      summary: summarySource.slice(0, 120),
      retrieve_ref: bestHit
        ? {
            bundle_id: options.bundleId,
            query_id: bestHit.query_id,
            chunk_id: bestHit.hit.chunk_id,
            score: bestHit.hit.score,
          }
        : undefined,
    })
  }

  if (snapshot.sources.length === 0) {
    return { ok: false, error: 'bundle has no deduped pages' }
  }

  return { ok: true, snapshot }
}
