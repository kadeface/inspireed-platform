/**
 * 合并进前端 .eslintrc.cjs / eslint.config 的命名检查片段。
 *
 * 用法（.eslintrc.cjs）：
 *   const naming = require('./docs/templates/naming-scaffold/eslint.naming.snippet.cjs')
 *   module.exports = { ...existing, overrides: [ ...(existing.overrides||[]), ...naming.overrides ] }
 *
 * 依赖：@typescript-eslint/eslint-plugin（Vue 模板项目通常已有 @vue/eslint-config-typescript）
 *
 * 范围：只约束 types / services 中的「数据字段」；组件局部变量仍用 camelCase（默认 TS 规则）。
 */
module.exports = {
  overrides: [
    {
      files: ['**/types/**/*.{ts,tsx}', '**/services/**/*.{ts,tsx}'],
      parser: '@typescript-eslint/parser',
      plugins: ['@typescript-eslint'],
      rules: {
        '@typescript-eslint/naming-convention': [
          'error',
          {
            selector: 'typeProperty',
            format: ['snake_case'],
            leadingUnderscore: 'allow',
            // 常见例外：HTTP 头、第三方 id、单字母
            filter: {
              regex: '^(Authorization|Content-Type|id|_.*)$',
              match: false,
            },
          },
          {
            selector: 'enumMember',
            format: ['UPPER_CASE', 'snake_case'],
          },
          {
            selector: 'typeLike',
            format: ['PascalCase'],
          },
        ],
      },
    },
  ],
}
