import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Redireciona qualquer requisição que comece com /api
      '/api': {
        target: 'http://127.0.0.1:8000', // A URL do seu backend Django
        changeOrigin: true,
        secure: false,
      },
    },
  },
})