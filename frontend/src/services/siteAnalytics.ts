import api from './api'

export interface SiteVisitorStats {
  total_visits: number
  today_visits: number
}

const VISIT_STORAGE_PREFIX = 'inspireed_visit_recorded_'

function todayKey(): string {
  return new Date().toISOString().slice(0, 10)
}

function visitStorageKey(): string {
  return `${VISIT_STORAGE_PREFIX}${todayKey()}`
}

export function hasRecordedVisitToday(): boolean {
  try {
    return sessionStorage.getItem(visitStorageKey()) === '1'
  } catch {
    return false
  }
}

export function markVisitRecordedToday(): void {
  try {
    sessionStorage.setItem(visitStorageKey(), '1')
  } catch {
    /* ignore */
  }
}

export async function fetchVisitorStats(): Promise<SiteVisitorStats> {
  return api.get<SiteVisitorStats>('/public/site/visitors/stats')
}

export async function recordVisitor(): Promise<SiteVisitorStats> {
  return api.post<SiteVisitorStats>('/public/site/visitors/record')
}

export async function loadAndTrackVisitorStats(): Promise<SiteVisitorStats> {
  if (!hasRecordedVisitToday()) {
    const stats = await recordVisitor()
    markVisitRecordedToday()
    return stats
  }
  return fetchVisitorStats()
}
