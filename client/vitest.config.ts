import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['src/**/*.{test,spec}.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/**/*.d.ts',
        'src/main.ts',
        'src/vite-env.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
    setupFiles: ['./src/test/setup.ts'],
    alias: {
      '@': resolve(__dirname, './src'),
      '@shared': resolve(__dirname, '../shared/types'),
    },
  },
})