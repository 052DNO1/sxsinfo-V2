import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  base: './',
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router'],
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [
        ElementPlusResolver({
          importStyle: 'css',
          locale: 'zh-cn',
        }),
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 5173,
    open: '/index.html',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
      }
    }
  },
  build: {
    outDir: 'dist/pc',
    assetsDir: 'assets',
    sourcemap: false,

    // ────────────────────────────────────────────────────────────────
    // target: 'esnext' —— 桌面端专属，与原 frontend/ 的配置不同，这是有意的
    //
    // 原因：Vite 的 vite:esbuild-transpile 插件（非 esnext 目标才会启用）
    // 会让 esbuild 把整段 chunk 写进 %TEMP%\esbuild-<hex> 再删除，
    // 而在 Windows 上这一步的删除会稳定地报 "Access is denied"，
    // 导致桌面端构建 100% 失败（同一份源码、同一套依赖在 frontend/ 下却能成功）。
    // 已实测：chrome120 / chrome100 / es2020 / es2022 全部失败，
    //         仅 esnext 成功（该目标下插件被跳过）。
    //
    // 为什么对桌面端可以接受：
    //   桌面端跑在 WebView2 里，是版本已知且持续的 Chromium 内核（本机 154），
    //   不存在需要兼容老旧浏览器的问题，本来就不需要降级。
    //
    // 影响范围：只改 desktop/frontend 这一份副本，Web 端部署行为完全不变。
    // 若将来要支持内核很旧的 WebView2，删掉这一行并同步排查上述删除问题。
    // ────────────────────────────────────────────────────────────────
    target: 'esnext',

    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      input: {
        main: fileURLToPath(new URL('./index.pc.html', import.meta.url))
      },
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'axios': ['axios'],
          'echarts': ['echarts', 'vue-echarts']
        }
      }
    }
  }
})
