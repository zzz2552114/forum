import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      globals: true,
      include: ['src/**/*.spec.ts', 'src/**/*.test.ts'],
      setupFiles: ['./vitest.setup.ts'],
      testTimeout: 20000,
      hookTimeout: 20000,
    },
  })
)
