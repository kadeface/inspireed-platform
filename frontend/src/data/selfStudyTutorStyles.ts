export type SelfStudyTutorStyle = 'default' | 'socratic' | 'feynman' | 'confucius'

export interface SelfStudyTutorStyleOption {
  id: SelfStudyTutorStyle
  name: string
  icon: string
  description: string
}

export const SELF_STUDY_TUTOR_STYLES: SelfStudyTutorStyleOption[] = [
  {
    id: 'default',
    name: '默认教练',
    icon: '🎯',
    description: '耐心引导，帮你讲清楚对错',
  },
  {
    id: 'socratic',
    name: '苏格拉底',
    icon: '❓',
    description: '用一连串问题带你自己想明白',
  },
  {
    id: 'feynman',
    name: '费曼',
    icon: '🗣️',
    description: '逼你用大白话把每一步讲出来',
  },
  {
    id: 'confucius',
    name: '孔子',
    icon: '📖',
    description: '温和启发，用类比帮你回到题意',
  },
]

export function getTutorStyleLabel(style: SelfStudyTutorStyle | string | null | undefined): string {
  const match = SELF_STUDY_TUTOR_STYLES.find((item) => item.id === style)
  return match?.name ?? '默认教练'
}
