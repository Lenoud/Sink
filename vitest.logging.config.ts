import { defineConfig } from 'vitest/config'

// 这些纯逻辑检查无需远端 Workers AI 或生产凭据。
export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/unit/markdown.spec.ts', 'tests/unit/link-store.spec.ts'],
  },
})
