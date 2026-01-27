/**
 * 字段命名转换工具
 * 后端使用 snake_case，前端使用 camelCase
 */

/**
 * 将对象的字段从 snake_case 转换为 camelCase
 */
export function snakeToCamel<T = any>(obj: any): T {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(snakeToCamel) as T
  }

  if (typeof obj !== 'object') {
    return obj
  }

  const result: any = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const camelKey = snakeToCamelString(key)
      result[camelKey] = snakeToCamel(obj[key])
    }
  }
  return result as T
}

/**
 * 将对象的字段从 camelCase 转换为 snake_case
 */
export function camelToSnake<T = any>(obj: any): T {
  if (obj === null || obj === undefined) {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(camelToSnake) as T
  }

  if (typeof obj !== 'object') {
    return obj
  }

  const result: any = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const snakeKey = camelToSnakeString(key)
      result[snakeKey] = camelToSnake(obj[key])
    }
  }
  return result as T
}

/**
 * 将字符串从 snake_case 转换为 camelCase
 */
function snakeToCamelString(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
}

/**
 * 将字符串从 camelCase 转换为 snake_case
 */
function camelToSnakeString(str: string): string {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase()
}
