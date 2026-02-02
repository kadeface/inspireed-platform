import { describe, it, expect } from 'vitest'

describe('Vitest 配置验证', () => {
  it('应该能运行基础测试', () => {
    expect(1 + 1).toBe(2)
  })

  it('应该支持异步测试', async () => {
    const result = await Promise.resolve(42)
    expect(result).toBe(42)
  })
})
