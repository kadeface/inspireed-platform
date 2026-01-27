export interface SubjectTheme {
  emoji: string
  headerFrom: string
  headerTo: string
  badgeFrom: string
  badgeTo: string
  accentText: string
  cardFrom: string
  cardTo: string
  focusRing: string
}

export const subjectThemes: Record<string, SubjectTheme> = {
  computer: {
    emoji: '🤖',
    headerFrom: 'from-orange-500',
    headerTo: 'to-orange-600',
    badgeFrom: 'from-orange-500',
    badgeTo: 'to-orange-600',
    accentText: 'text-orange-100',
    cardFrom: 'from-orange-500',
    cardTo: 'to-orange-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-orange-200'
  },
  math: {
    emoji: '📐',
    headerFrom: 'from-emerald-500',
    headerTo: 'to-emerald-600',
    badgeFrom: 'from-emerald-500',
    badgeTo: 'to-emerald-600',
    accentText: 'text-emerald-100',
    cardFrom: 'from-emerald-500',
    cardTo: 'to-emerald-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-emerald-200'
  },
  physics: {
    emoji: '⚛️',
    headerFrom: 'from-sky-500',
    headerTo: 'to-sky-600',
    badgeFrom: 'from-sky-500',
    badgeTo: 'to-sky-600',
    accentText: 'text-sky-100',
    cardFrom: 'from-sky-500',
    cardTo: 'to-sky-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-sky-200'
  },
  chemistry: {
    emoji: '🧪',
    headerFrom: 'from-purple-500',
    headerTo: 'to-purple-600',
    badgeFrom: 'from-purple-500',
    badgeTo: 'to-purple-600',
    accentText: 'text-purple-100',
    cardFrom: 'from-purple-500',
    cardTo: 'to-purple-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-purple-200'
  },
  biology: {
    emoji: '🧬',
    headerFrom: 'from-pink-500',
    headerTo: 'to-pink-600',
    badgeFrom: 'from-pink-500',
    badgeTo: 'to-pink-600',
    accentText: 'text-pink-100',
    cardFrom: 'from-pink-500',
    cardTo: 'to-pink-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-pink-200'
  },
  earth: {
    emoji: '🌍',
    headerFrom: 'from-amber-500',
    headerTo: 'to-amber-600',
    badgeFrom: 'from-amber-500',
    badgeTo: 'to-amber-600',
    accentText: 'text-amber-100',
    cardFrom: 'from-amber-500',
    cardTo: 'to-amber-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-amber-200'
  },
  science: {
    emoji: '🔬',
    headerFrom: 'from-cyan-500',
    headerTo: 'to-cyan-600',
    badgeFrom: 'from-cyan-500',
    badgeTo: 'to-cyan-600',
    accentText: 'text-cyan-100',
    cardFrom: 'from-cyan-500',
    cardTo: 'to-cyan-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-cyan-200'
  },
  psychology: {
    emoji: '🧠',
    headerFrom: 'from-indigo-500',
    headerTo: 'to-indigo-600',
    badgeFrom: 'from-indigo-500',
    badgeTo: 'to-indigo-600',
    accentText: 'text-indigo-100',
    cardFrom: 'from-indigo-500',
    cardTo: 'to-indigo-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-indigo-200'
  },
  music: {
    emoji: '🎵',
    headerFrom: 'from-rose-500',
    headerTo: 'to-rose-600',
    badgeFrom: 'from-rose-500',
    badgeTo: 'to-rose-600',
    accentText: 'text-rose-100',
    cardFrom: 'from-rose-500',
    cardTo: 'to-rose-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-rose-200'
  },
  art: {
    emoji: '🎨',
    headerFrom: 'from-violet-500',
    headerTo: 'to-violet-600',
    badgeFrom: 'from-violet-500',
    badgeTo: 'to-violet-600',
    accentText: 'text-violet-100',
    cardFrom: 'from-violet-500',
    cardTo: 'to-violet-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-violet-200'
  },
  comprehensive: {
    emoji: '🌟',
    headerFrom: 'from-yellow-500',
    headerTo: 'to-yellow-600',
    badgeFrom: 'from-yellow-500',
    badgeTo: 'to-yellow-600',
    accentText: 'text-yellow-100',
    cardFrom: 'from-yellow-500',
    cardTo: 'to-yellow-600',
    focusRing: 'focus-visible:ring-4 focus-visible:ring-yellow-200'
  }
}

export const defaultSubjectTheme: SubjectTheme = {
  emoji: '📚',
  headerFrom: 'from-slate-600',
  headerTo: 'to-slate-700',
  badgeFrom: 'from-slate-500',
  badgeTo: 'to-slate-600',
  accentText: 'text-slate-100',
  cardFrom: 'from-slate-600',
  cardTo: 'to-slate-700',
  focusRing: 'focus-visible:ring-4 focus-visible:ring-slate-200'
}

export const subjectIntros: Record<string, string> = {
  computer: '从智能农业到物联网实训，系统掌握未来核心数字能力。',
  math: '以真实问题驱动的数学建模与推理实践。',
  physics: '通过实验与仿真探究自然规律，理解能量与运动。',
  chemistry: '兼具实验安全与数据分析的化学探究课程。',
  biology: '从生命现象出发，走向跨学科的综合研究。',
  earth: '聚焦地球系统与环境变迁，培养可持续发展的视角。',
  science: '探索自然世界的奥秘，培养科学思维与实践能力。',
  psychology: '了解人类心理与行为，促进自我认知与成长。',
  music: '感受音乐之美，培养艺术素养与审美能力。',
  art: '激发创造力，培养艺术表现与审美鉴赏能力。',
  comprehensive: '跨学科综合实践，培养全面发展的核心素养。'
}

export const defaultCourseDescription =
  '面向真实场景的综合实践课程，帮助学生构建系统化知识体系。'

