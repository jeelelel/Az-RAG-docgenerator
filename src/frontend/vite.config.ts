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
      '/ask': 'http://127.0.0.1:8000',
      '/chat': 'http://127.0.0.1:8000',
      '/simple_conversation': 'http://127.0.0.1:8000',
      '/conversation': 'http://127.0.0.1:8000',
      '/frontend_settings': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/document': 'http://127.0.0.1:8000',
      '/simple_section_generate': 'http://127.0.0.1:8000',
      '/section': 'http://127.0.0.1:8000'
    }
  }
})
