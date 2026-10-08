import { describe, expect, it } from 'vitest'
import { CYCLE_REMAINDER_WIKI_SNAPSHOT } from './courseDesignWikiSnapshots'

describe('cycle remainder wiki snapshot', () => {
  it('is the fixed 40-minute grade-three experiment', () => {
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.grade).toBe('三年级')
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.subject).toBe('数学')
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.title).toBe('周期与余数')
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.duration_minutes).toBe(40)
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.bundle_ref).toBeTruthy()
  })

  it('has unique, traceable sources with real vault paths', () => {
    const ids = CYCLE_REMAINDER_WIKI_SNAPSHOT.sources.map((item) => item.id)
    expect(new Set(ids).size).toBe(ids.length)
    expect(ids.length).toBeGreaterThan(0)
    for (const source of CYCLE_REMAINDER_WIKI_SNAPSHOT.sources) {
      expect(source.wiki_path.startsWith('wiki/')).toBe(true)
      expect(source.summary.length).toBeGreaterThan(0)
    }
    expect(CYCLE_REMAINDER_WIKI_SNAPSHOT.scope_boundaries.join('')).toContain('机器人')
  })

  it('includes retrieve_ref on sources when structured from bundle', () => {
    const withRef = CYCLE_REMAINDER_WIKI_SNAPSHOT.sources.filter((s) => s.retrieve_ref)
    expect(withRef.length).toBeGreaterThan(0)
    expect(withRef[0]?.retrieve_ref?.query_id).toBeTruthy()
  })
})
