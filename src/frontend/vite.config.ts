import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../static',
    emptyOutDir: true,
    sourcemap: true
  },
  server: {
    proxy: {
      '/ask': 'http://127.0.0.1:50505',
      '/chat': 'http://127.0.0.1:50505',
      '/simple_conversation': 'http://127.0.0.1:50505',
      '/conversation': 'http://127.0.0.1:50505',
      '/frontend_settings': 'http://127.0.0.1:50505',
      '/history': 'http://127.0.0.1:50505',
      '/document': 'http://127.0.0.1:50505',
      '/simple_section_generate': 'http://127.0.0.1:50505',
      '/section': 'http://127.0.0.1:50505'
    }
  }
})
