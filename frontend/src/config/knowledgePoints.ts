/**
 * 小学奥数知识点分类体系配置
 */

export interface KnowledgePointCategory {
  name: string
  subcategories: string[]
}

export const MathOlympiadCategories: Record<string, KnowledgePointCategory> = {
  CALCULATION: {
    name: '计算类',
    subcategories: ['速算技巧', '巧算方法', '数论基础', '分数运算', '小数运算', '整数运算']
  },
  GEOMETRY: {
    name: '几何类',
    subcategories: ['图形认知', '面积周长', '立体图形', '角度测量', '对称图形', '图形变换']
  },
  APPLICATION: {
    name: '应用题类',
    subcategories: ['行程问题', '工程问题', '浓度问题', '利润问题', '年龄问题', '植树问题']
  },
  LOGIC: {
    name: '逻辑推理类',
    subcategories: ['排列组合', '逻辑推理', '数独游戏', '找规律', '逻辑判断', '推理题']
  },
  NUMBER_THEORY: {
    name: '数论类',
    subcategories: ['整除性质', '最大公约数', '最小公倍数', '质数与合数', '数的奇偶性', '余数问题']
  },
  ALGEBRA: {
    name: '代数类',
    subcategories: ['方程求解', '不等式', '函数初步', '数列初步', '代数式', '因式分解']
  }
}

/**
 * 获取所有知识点分类
 */
export function getAllCategories(): KnowledgePointCategory[] {
  return Object.values(MathOlympiadCategories)
}

/**
 * 根据分类名称获取子分类
 */
export function getSubcategories(categoryName: string): string[] {
  const category = Object.values(MathOlympiadCategories).find(
    cat => cat.name === categoryName
  )
  return category?.subcategories || []
}

/**
 * 格式化知识点分类字符串（用于存储）
 * 格式：大类/小类，如：计算类/速算技巧
 */
export function formatKnowledgePointCategory(
  category: string,
  subcategory: string
): string {
  return `${category}/${subcategory}`
}

/**
 * 解析知识点分类字符串
 */
export function parseKnowledgePointCategory(
  categoryStr: string
): { category: string; subcategory: string } | null {
  if (!categoryStr || !categoryStr.includes('/')) {
    return null
  }
  const [category, subcategory] = categoryStr.split('/')
  return { category: category.trim(), subcategory: subcategory.trim() }
}

/**
 * 获取所有可能的分类值（用于筛选）
 */
export function getAllCategoryValues(): string[] {
  const values: string[] = []
  Object.values(MathOlympiadCategories).forEach(cat => {
    cat.subcategories.forEach(sub => {
      values.push(formatKnowledgePointCategory(cat.name, sub))
    })
  })
  return values
}
